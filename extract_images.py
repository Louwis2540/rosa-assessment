"""
Extract individual option images from the ROSA worksheet PDF.
Usage: python extract_images.py "ROSA worksheet.pdf"
"""
import sys, os
import fitz
from PIL import Image

# All coords in pixels at zoom=3 (px = PDF_pt * 3)
# Page is landscape 792x612 pts → 2376x1836 px
#
# Section A (Chair) : x=0..1188 px, 5 cols of ~188px each
# Section B/C (Mon/Tel/Mouse/KB): x=1188..2376 px
#
# Col boundaries Section A (px): 0, 188, 375, 563, 750, 940
# Col boundaries Section B (px relative to 1188): 0,170,340,510,680,850,1020
# → absolute: 1188,1358,1528,1698,1868,2038,2208

A_COLS = [0, 188, 375, 563, 750, 940]          # Section A column edges
B_OFF  = 1188                                    # Section B start x
B_COLS = [0, 170, 340, 510, 680, 850, 1020]     # Section B relative col edges

# Image-only y ranges (skip sub-section headers)
Y_CHAIR   = (195, 335)   # Chair Height
Y_PAN     = (465, 660)   # Pan Depth
Y_ARM     = (830, 1055)  # Armrests
Y_BACK    = (1180, 1400) # Back Support
Y_MON     = (195, 335)   # Monitor  (same row as chair)
Y_TEL     = (545, 665)   # Telephone
Y_MOUSE   = (915, 1055)  # Mouse
Y_KEY     = (1235, 1395) # Keyboard

def bc(i):
    """Section B absolute column: left edge of column i."""
    return B_OFF + B_COLS[i]

CROPS = {
    # ── Section A : Chair ──────────────────────────────────────────
    "chair_height_good":    (*Y_CHAIR, A_COLS[0], A_COLS[1]),   # knees 90°  (1)
    "chair_height_low":     (*Y_CHAIR, A_COLS[1], A_COLS[2]),   # too low   (2)
    "chair_height_high":    (*Y_CHAIR, A_COLS[2], A_COLS[3]),   # too high  (2)
    "chair_height_nofeet":  (*Y_CHAIR, A_COLS[3], A_COLS[4]),   # no feet   (3)
    "chair_under_desk":     (*Y_CHAIR, A_COLS[4], A_COLS[5]),   # under desk(+1)

    "pan_depth_good":       (*Y_PAN,   A_COLS[0], A_COLS[1]),   # ~3 inches (1)
    "pan_depth_long":       (*Y_PAN,   A_COLS[1], A_COLS[2]),   # too long  (2)
    "pan_depth_short":      (*Y_PAN,   A_COLS[2], A_COLS[3]),   # too short (2)

    "armrest_good":         (*Y_ARM,   A_COLS[0], A_COLS[1]),   # elbows in line   (1)
    "armrest_high":         (*Y_ARM,   A_COLS[1], A_COLS[2]),   # too high/low     (2)
    "armrest_hard":         (*Y_ARM,   A_COLS[2], A_COLS[3]),   # hard/damaged(+1)
    "armrest_wide":         (*Y_ARM,   A_COLS[3], A_COLS[4]),   # too wide  (+1)

    "back_good":            (*Y_BACK,  A_COLS[0], A_COLS[1]),   # adequate  (1)
    "back_no_lumbar":       (*Y_BACK,  A_COLS[1], A_COLS[2]),   # no lumbar (2)
    "back_angled":          (*Y_BACK,  A_COLS[2], A_COLS[3]),   # angled    (2)
    "back_none":            (*Y_BACK,  A_COLS[3], A_COLS[4]),   # no support(2)
    "back_surface_high":    (*Y_BACK,  A_COLS[4], A_COLS[5]),   # desk too high(+1)

    # ── Section B : Monitor & Telephone ────────────────────────────
    "monitor_good":         (*Y_MON,   bc(0), bc(1)),   # arm's length / eye level (1)
    "monitor_low":          (*Y_MON,   bc(1), bc(2)),   # too low                  (2)
    "monitor_high":         (*Y_MON,   bc(2), bc(3)),   # too high                 (3)
    "monitor_neck_twist":   (*Y_MON,   bc(3), bc(4)),   # neck twist >30°         (+1)
    "monitor_glare":        (*Y_MON,   bc(4), bc(5)),   # glare                   (+1)
    "monitor_no_holder":    (*Y_MON,   bc(5), bc(6)),   # no doc holder           (+1)

    # Telephone: unequal columns (headset small, reaching wide, shoulder medium)
    "phone_good":           (*Y_TEL,   bc(0),       bc(0)+220),  # headset / one hand (1)
    "phone_far":            (*Y_TEL,   bc(0)+220,   bc(0)+620),  # too far reach      (2)
    "phone_neck":           (*Y_TEL,   bc(0)+620,   bc(0)+920),  # neck & shoulder   (+2)

    # ── Section C : Mouse & Keyboard ───────────────────────────────
    "mouse_good":           (*Y_MOUSE, bc(0), bc(1)),   # in line with shoulder (1)
    "mouse_reach":          (*Y_MOUSE, bc(1), bc(2)),   # reaching              (2)
    "mouse_diff_surfaces":  (*Y_MOUSE, bc(2), bc(3)),   # diff surfaces        (+2)
    "mouse_pinch":          (*Y_MOUSE, bc(3), bc(4)),   # pinch grip           (+1)
    "mouse_palmrest":       (*Y_MOUSE, bc(4), bc(5)),   # palmrest in front    (+1)

    "keyboard_good":        (*Y_KEY,   bc(0), bc(1)),   # wrists straight (1)
    "keyboard_extended":    (*Y_KEY,   bc(1), bc(2)),   # wrists extended (2)
    "keyboard_deviation":   (*Y_KEY,   bc(2), bc(3)),   # deviation      (+1)
    "keyboard_too_high":    (*Y_KEY,   bc(3), bc(4)),   # too high       (+1)
    "keyboard_overhead":    (*Y_KEY,   bc(4), bc(5)),   # overhead reach (+1)
}


def extract(pdf_path: str, out_dir: str, zoom: float = 3.0):
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    page = doc[0]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    full_path = os.path.join(out_dir, "page_1_full.png")
    pix.save(full_path)
    print(f"Full page: {pix.width}x{pix.height}px -> {full_path}")

    img = Image.open(full_path)
    W, H = img.size

    for name, (y0, y1, x0, x1) in CROPS.items():
        # clamp to image bounds
        x0c, x1c = max(0, x0), min(W, x1)
        y0c, y1c = max(0, y0), min(H, y1)
        cropped = img.crop((x0c, y0c, x1c, y1c))
        out = os.path.join(out_dir, f"{name}.png")
        cropped.save(out)
        print(f"  {name}.png  ({cropped.width}x{cropped.height}px)")

    doc.close()
    print(f"\nDone - {len(CROPS)} images in {out_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python extract_images.py "ROSA worksheet.pdf"')
        sys.exit(1)
    extract(sys.argv[1],
            os.path.join(os.path.dirname(__file__), "static", "images", "rosa"))
