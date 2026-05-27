from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os, tempfile

# Register Thai-compatible font (falls back to Helvetica if unavailable)
FONT_NAME = "Helvetica"
try:
    font_path = os.path.join(os.path.dirname(__file__), "..", "static", "fonts", "THSarabunNew.ttf")
    font_bold = os.path.join(os.path.dirname(__file__), "..", "static", "fonts", "THSarabunNew Bold.ttf")
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont("THSarabun", font_path))
        if os.path.exists(font_bold):
            pdfmetrics.registerFont(TTFont("THSarabun-Bold", font_bold))
        FONT_NAME = "THSarabun"
except Exception:
    pass

RISK_COLORS = {
    "ต่ำ": colors.HexColor("#28a745"),
    "ปานกลาง": colors.HexColor("#ffc107"),
    "สูง": colors.HexColor("#dc3545"),
}


def _style(name="Normal", size=11, bold=False, color=colors.black, align="LEFT"):
    font = (FONT_NAME + "-Bold") if bold and FONT_NAME == "THSarabun" else FONT_NAME
    return ParagraphStyle(
        name,
        fontName=font,
        fontSize=size,
        textColor=color,
        alignment={"LEFT": 0, "CENTER": 1, "RIGHT": 2}.get(align, 0),
        leading=size * 1.4,
    )


def generate_pdf(result: dict) -> str:
    p = result["personal"]
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()

    doc = SimpleDocTemplate(
        tmp.name,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    story = []

    # Header
    story.append(Paragraph("รายงานผลการประเมินความเสี่ยงด้วยวิธีการ ROSA", _style(size=16, bold=True, align="CENTER")))
    story.append(Paragraph("Rapid Office Strain Assessment", _style(size=12, color=colors.grey, align="CENTER")))
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a73e8")))
    story.append(Spacer(1, 0.4*cm))

    # Personal info table
    story.append(Paragraph("ข้อมูลผู้รับการประเมิน", _style(size=13, bold=True)))
    story.append(Spacer(1, 0.2*cm))

    diseases = ", ".join(p.get("diseases", []))
    if p.get("diseases_other"):
        diseases += f" / {p['diseases_other']}"

    personal_data = [
        ["ชื่อ-สกุล", p.get("name",""), "วันที่ประเมิน", datetime.now().strftime("%d/%m/%Y")],
        ["เพศ", p.get("gender",""), "อายุ", f"{p.get('age','')} ปี"],
        ["น้ำหนัก", f"{p.get('weight','')} kg", "ส่วนสูง", f"{p.get('height','')} cm"],
        ["รอบเอว", f"{p.get('waist','')} นิ้ว", "BMI", f"{_bmi(p):.1f}"],
        ["ประเภทงาน", p.get("job_type",""), "แผนก", p.get("department","")],
        ["อายุงาน", f"{p.get('work_years',0)} ปี {p.get('work_months',0)} เดือน",
         "ชม.คอมพิวเตอร์/วัน", f"{p.get('computer_hours','')} ชั่วโมง"],
        ["โรคประจำตัว", diseases or "-", "", ""],
    ]

    pt = Table(personal_data, colWidths=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
    pt.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), FONT_NAME),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("FONTNAME", (0,0), (0,-1), FONT_NAME),
        ("FONTNAME", (2,0), (2,-1), FONT_NAME),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#e8f0fe")),
        ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#e8f0fe")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("SPAN", (1,6), (3,6)),
    ]))
    story.append(pt)
    story.append(Spacer(1, 0.5*cm))

    # ROSA Score summary
    final = result.get("rosa_final_score", 0)
    risk = result.get("risk_level", "")
    risk_color = RISK_COLORS.get(risk, colors.grey)

    story.append(Paragraph("ผลการประเมิน ROSA", _style(size=13, bold=True)))
    story.append(Spacer(1, 0.2*cm))

    score_data = [
        ["คะแนน Section A (เก้าอี้)", str(result.get("section_a_score",""))],
        ["คะแนน Section B (หน้าจอ + โทรศัพท์)", str(result.get("section_b_score",""))],
        ["คะแนน Section C (เมาส์ + คีย์บอร์ด)", str(result.get("section_c_score",""))],
        ["คะแนน Section D (รวม B+C)", str(result.get("section_d_score",""))],
        ["ROSA Final Score", str(final)],
        ["ระดับความเสี่ยง", risk],
    ]

    st = Table(score_data, colWidths=[9*cm, 8*cm])
    st.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), FONT_NAME),
        ("FONTSIZE", (0,0), (-1,-1), 11),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#f8f9fa")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("BACKGROUND", (0,4), (-1,4), colors.HexColor("#1a73e8")),
        ("TEXTCOLOR", (0,4), (-1,4), colors.white),
        ("FONTSIZE", (0,4), (-1,4), 14),
        ("BACKGROUND", (0,5), (-1,5), risk_color),
        ("TEXTCOLOR", (0,5), (-1,5), colors.white),
        ("FONTSIZE", (0,5), (-1,5), 12),
    ]))
    story.append(st)
    story.append(Spacer(1, 0.4*cm))

    # Risk interpretation
    story.append(Paragraph("การแปลผลและข้อแนะนำ", _style(size=13, bold=True)))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(f"• {result.get('risk_description','')}", _style(size=11)))
    story.append(Paragraph(f"• {result.get('risk_action','')}", _style(size=11)))
    story.append(Spacer(1, 0.5*cm))

    # Score breakdown
    story.append(Paragraph("รายละเอียดคะแนนแต่ละส่วน", _style(size=13, bold=True)))
    story.append(Spacer(1, 0.2*cm))

    detail_data = [
        ["ส่วน A – เก้าอี้", "", "", ""],
        ["  ความสูงของเบาะ", str(result.get("chair_height_score","")),
         "  ความลึกของเบาะ", str(result.get("pan_depth_score",""))],
        ["  แขนพัก", str(result.get("armrest_score","")),
         "  พนักพิง", str(result.get("back_support_score",""))],
        ["  รวมเบาะ (แกนแถว)", str(result.get("seat_pan_combined","")),
         "  รวมแขน/หลัง (แกนคอลัมน์)", str(result.get("armrest_back_combined",""))],
        ["  คะแนนตาราง A", str(result.get("table_a_score","")),
         "  Duration เก้าอี้", str(result.get("chair_duration",""))],
        ["ส่วน B – หน้าจอ/โทรศัพท์", "", "", ""],
        ["  หน้าจอ (area)", str(result.get("monitor_score","")),
         "  โทรศัพท์ (area)", str(result.get("phone_score",""))],
        ["  หน้าจอ (แกน)", str(result.get("monitor_axis","")),
         "  โทรศัพท์ (แกน)", str(result.get("phone_axis",""))],
        ["ส่วน C – เมาส์/คีย์บอร์ด", "", "", ""],
        ["  เมาส์ (area)", str(result.get("mouse_score","")),
         "  คีย์บอร์ด (area)", str(result.get("keyboard_score",""))],
        ["  เมาส์ (แกน)", str(result.get("mouse_axis","")),
         "  คีย์บอร์ด (แกน)", str(result.get("keyboard_axis",""))],
    ]

    dt = Table(detail_data, colWidths=[5.5*cm, 3*cm, 5.5*cm, 3*cm])
    dt.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), FONT_NAME),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a73e8")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("BACKGROUND", (0,5), (-1,5), colors.HexColor("#34a853")),
        ("TEXTCOLOR", (0,5), (-1,5), colors.white),
        ("BACKGROUND", (0,8), (-1,8), colors.HexColor("#ea4335")),
        ("TEXTCOLOR", (0,8), (-1,8), colors.white),
        ("SPAN", (0,0), (-1,0)),
        ("SPAN", (0,5), (-1,5)),
        ("SPAN", (0,8), (-1,8)),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(dt)
    story.append(Spacer(1, 1*cm))

    # Footer
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "ROSA – Rapid Office Strain Assessment | Developed by Michael Sonne, MHK, CK.",
        _style(size=8, color=colors.grey, align="CENTER"),
    ))
    story.append(Paragraph(
        f"พิมพ์เมื่อ: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        _style(size=8, color=colors.grey, align="CENTER"),
    ))

    doc.build(story)
    return tmp.name


def _bmi(p: dict) -> float:
    h = p.get("height", 0)
    w = p.get("weight", 0)
    if h and w:
        return w / ((h / 100) ** 2)
    return 0.0
