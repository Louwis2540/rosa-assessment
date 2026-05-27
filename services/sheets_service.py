import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from config import settings
import json, os

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SHEET_HEADERS = [
    "ID","วันที่","ชื่อ-สกุล","เพศ","อายุ","น้ำหนัก(kg)","ส่วนสูง(cm)",
    "รอบเอว(นิ้ว)","โรคประจำตัว","ประเภทงาน","แผนก","อายุงาน(ปี)","อายุงาน(เดือน)",
    "ชม.คอม/วัน",
    "คะแนนความสูงเบาะ","คะแนนความลึกเบาะ","คะแนนแขนพัก","คะแนนพนักพิง",
    "คะแนนรวมA(เบาะ)","คะแนนรวมA(แขน/หลัง)","คะแนนตารางA","Duration_A","คะแนนSection_A",
    "คะแนนหน้าจอ","คะแนนโทรศัพท์","monitor_axis","phone_axis","Duration_B","คะแนนSection_B",
    "คะแนนเมาส์","คะแนนคีย์บอร์ด","mouse_axis","keyboard_axis","Duration_C","คะแนนSection_C",
    "คะแนนSection_D","ROSA_Final","ระดับความเสี่ยง","PDF_URL",
]


def _get_creds():
    val = settings.google_credentials_json
    if not val:
        return None
    if val.strip().startswith("{"):
        return Credentials.from_service_account_info(json.loads(val), scopes=SCOPES)
    if os.path.exists(val):
        return Credentials.from_service_account_file(val, scopes=SCOPES)
    return None


def _get_client():
    creds = _get_creds()
    if creds is None:
        return None
    return gspread.authorize(creds)


def _get_or_create_sheet(gc):
    sh = gc.open_by_key(settings.google_sheet_id)
    try:
        ws = sh.worksheet("ผลการประเมิน")
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet("ผลการประเมิน", rows=5000, cols=len(SHEET_HEADERS))
        ws.append_row(SHEET_HEADERS)
    return ws


def save_assessment(result: dict, pdf_url: str = "") -> str:
    gc = _get_client()
    if gc is None:
        return ""
    ws = _get_or_create_sheet(gc)
    p = result["personal"]
    row_id = datetime.now().strftime("%Y%m%d%H%M%S")
    row = [
        row_id,
        datetime.now().strftime("%d/%m/%Y %H:%M"),
        p.get("name",""),
        p.get("gender",""),
        p.get("age",""),
        p.get("weight",""),
        p.get("height",""),
        p.get("waist",""),
        ", ".join(p.get("diseases", [])) + (" / " + p.get("diseases_other","") if p.get("diseases_other") else ""),
        p.get("job_type",""),
        p.get("department",""),
        p.get("work_years",""),
        p.get("work_months",""),
        p.get("computer_hours",""),
        result.get("chair_height_score",""),
        result.get("pan_depth_score",""),
        result.get("armrest_score",""),
        result.get("back_support_score",""),
        result.get("seat_pan_combined",""),
        result.get("armrest_back_combined",""),
        result.get("table_a_score",""),
        result.get("chair_duration",""),
        result.get("section_a_score",""),
        result.get("monitor_score",""),
        result.get("phone_score",""),
        result.get("monitor_axis",""),
        result.get("phone_axis",""),
        result.get("section_b_duration",""),
        result.get("section_b_score",""),
        result.get("mouse_score",""),
        result.get("keyboard_score",""),
        result.get("mouse_axis",""),
        result.get("keyboard_axis",""),
        result.get("section_c_duration",""),
        result.get("section_c_score",""),
        result.get("section_d_score",""),
        result.get("rosa_final_score",""),
        result.get("risk_level",""),
        pdf_url,
    ]
    ws.append_row(row)
    return row_id


def get_all_assessments() -> list:
    gc = _get_client()
    if gc is None:
        return []
    ws = _get_or_create_sheet(gc)
    records = ws.get_all_records()
    return records
