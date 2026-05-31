from fastapi import FastAPI, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
from pathlib import Path
import json, os, tempfile, io, traceback

CROPS_CONFIG = Path("config/crops.json")
FULL_PAGE    = Path("static/images/rosa/page_1_full.png")
ROSA_IMG_DIR = Path("static/images/rosa")

def _load_crops():
    if CROPS_CONFIG.exists():
        return json.loads(CROPS_CONFIG.read_text("utf-8"))
    return {}

def _save_crops(data: dict):
    CROPS_CONFIG.parent.mkdir(exist_ok=True)
    CROPS_CONFIG.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")

from config import settings
from services.rosa_scorer import calculate_rosa
from services.sheets_service import save_assessment, get_all_assessments
from services.drive_service import upload_pdf
from services.pdf_service import generate_pdf

app = FastAPI(title=settings.app_title, version=settings.app_version)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def _resp(request, name, ctx=None):
    context = {"request": request, "title": settings.app_title}
    if ctx:
        context.update(ctx)
    return templates.TemplateResponse(request=request, name=name, context=context)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return _resp(request, "home.html")


@app.get("/assess", response_class=HTMLResponse)
async def assess_form(request: Request):
    return _resp(request, "home.html")


@app.post("/submit", response_class=JSONResponse)
async def submit_assessment(request: Request):
    data = await request.json()
    personal = data.get("personal", {})
    chair = data.get("chair", {})
    monitor_phone = data.get("monitor_phone", {})
    mouse_keyboard = data.get("mouse_keyboard", {})

    scorer_input = {**chair, **monitor_phone, **mouse_keyboard}
    scores = calculate_rosa(scorer_input)

    result = {
        "personal": personal,
        **scores,
        "timestamp": datetime.now().isoformat(),
    }

    # Generate PDF
    pdf_path = ""
    pdf_url = ""
    try:
        pdf_path = generate_pdf(result)
        name_safe = personal.get("name", "unknown").replace(" ", "_")
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"ROSA_{name_safe}_{date_str}.pdf"
        pdf_url = upload_pdf(pdf_path, filename)
    except Exception as e:
        print(f"PDF/Drive error: {e}")
    finally:
        if pdf_path and os.path.exists(pdf_path):
            pass  # keep temp file for download

    # Save to Google Sheets
    row_id = ""
    try:
        row_id = save_assessment(result, pdf_url)
    except Exception as e:
        print(f"Sheets error: {e}\n{traceback.format_exc()}")

    result["row_id"] = row_id
    result["pdf_url"] = pdf_url
    result["pdf_local"] = pdf_path

    return JSONResponse(content=result)


@app.get("/result", response_class=HTMLResponse)
async def result_page(request: Request):
    return _resp(request, "home.html")


@app.get("/download-pdf")
async def download_pdf(path: str):
    if not path or not os.path.exists(path):
        raise HTTPException(404, "PDF not found")
    return FileResponse(path, media_type="application/pdf", filename="ROSA_result.pdf")


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, pw: str = ""):
    return _resp(request, "home.html")

@app.get("/api/dashboard")
async def api_dashboard(pw: str = ""):
    if pw != settings.admin_password:
        raise HTTPException(403, "Unauthorized")
    records = []
    try:
        records = get_all_assessments()
    except Exception as e:
        print(f"Dashboard fetch error: {e}\n{traceback.format_exc()}")
    return JSONResponse(content=records)

@app.get("/api/crops")
async def api_crops(pw: str = ""):
    if pw != settings.admin_password:
        raise HTTPException(403, "Unauthorized")
    return JSONResponse(content={"crops": _load_crops(), "has_pdf": FULL_PAGE.exists()})


@app.get("/api/image-version")
async def api_image_version():
    max_mtime = 0
    for f in ROSA_IMG_DIR.glob("*.png"):
        mtime = f.stat().st_mtime
        if mtime > max_mtime:
            max_mtime = mtime
    return JSONResponse({"v": int(max_mtime)})


@app.get("/health")
async def health():
    return {"status": "ok", "version": settings.app_version}


# ── Admin: Image Manager ─────────────────────────────────────────────────────

@app.get("/admin/images", response_class=HTMLResponse)
async def admin_images_page(request: Request, pw: str = ""):
    return _resp(request, "home.html")


@app.post("/admin/images/recrop")
async def admin_recrop(request: Request):
    body = await request.json()
    if body.get("pw") != settings.admin_password:
        raise HTTPException(403, "Unauthorized")
    name = body["name"]
    x0, y0, x1, y1 = int(body["x0"]), int(body["y0"]), int(body["x1"]), int(body["y1"])
    if not FULL_PAGE.exists():
        raise HTTPException(400, "Full page image missing — run extract_images.py first")
    from PIL import Image as _PIL
    img = _PIL.open(FULL_PAGE)
    W, H = img.size
    x0, x1 = max(0, x0), min(W, x1)
    y0, y1 = max(0, y0), min(H, y1)
    if x1 <= x0 or y1 <= y0:
        raise HTTPException(400, "Invalid crop region")
    img.crop((x0, y0, x1, y1)).save(ROSA_IMG_DIR / f"{name}.png")
    crops = _load_crops()
    if name in crops:
        crops[name].update({"x0": x0, "y0": y0, "x1": x1, "y1": y1})
        _save_crops(crops)
    ts = int(datetime.now().timestamp())
    return JSONResponse({"ok": True, "src": f"/static/images/rosa/{name}.png?t={ts}"})


@app.post("/admin/images/upload")
async def admin_upload_image(pw: str = Form(...), name: str = Form(...),
                              file: UploadFile = File(...)):
    if pw != settings.admin_password:
        raise HTTPException(403, "Unauthorized")
    if file.content_type not in {"image/png", "image/jpeg", "image/webp"}:
        raise HTTPException(400, "Only PNG/JPEG/WebP")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 5 MB)")
    from PIL import Image as _PIL
    img = _PIL.open(io.BytesIO(content)).convert("RGB")
    img.save(ROSA_IMG_DIR / f"{name}.png", "PNG")
    ts = int(datetime.now().timestamp())
    return JSONResponse({"ok": True, "src": f"/static/images/rosa/{name}.png?t={ts}"})
