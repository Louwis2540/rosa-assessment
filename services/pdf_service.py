from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os, tempfile

# ── Font ──────────────────────────────────────────────────────────────────────
FONT_REG  = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
try:
    _base = os.path.join(os.path.dirname(__file__), "..", "static", "fonts")
    _r = os.path.join(_base, "THSarabunNew.ttf")
    _b = os.path.join(_base, "THSarabunNew Bold.ttf")
    if os.path.exists(_r):
        pdfmetrics.registerFont(TTFont("THSarabun", _r))
        FONT_REG = "THSarabun"
    if os.path.exists(_b):
        pdfmetrics.registerFont(TTFont("THSarabun-Bold", _b))
        FONT_BOLD = "THSarabun-Bold"
except Exception:
    pass

# ── Palette ───────────────────────────────────────────────────────────────────
C_NAVY   = colors.HexColor("#1a3a5c")
C_BLUE   = colors.HexColor("#1565c0")
C_LBLUE  = colors.HexColor("#dce8f8")
C_GREEN  = colors.HexColor("#1b5e20")
C_LGREEN = colors.HexColor("#e8f5e9")
C_ORANGE = colors.HexColor("#bf360c")
C_LORANGE= colors.HexColor("#fff3e0")
C_RED    = colors.HexColor("#b71c1c")
C_LRED   = colors.HexColor("#ffebee")
C_LGREY  = colors.HexColor("#f5f7fa")
C_MGREY  = colors.HexColor("#cfd8dc")
C_DGREY  = colors.HexColor("#546e7a")
C_WHITE  = colors.white
C_BLACK  = colors.HexColor("#212121")

RISK_BG   = {"ต่ำ": C_LGREEN,  "ปานกลาง": C_LORANGE, "สูง": C_LRED}
RISK_FG   = {"ต่ำ": C_GREEN,   "ปานกลาง": C_ORANGE,  "สูง": C_RED}
RISK_LABEL= {"ต่ำ": "ความเสี่ยงต่ำ", "ปานกลาง": "ความเสี่ยงปานกลาง", "สูง": "ความเสี่ยงสูง"}
RISK_EMOJI= {"ต่ำ": "●", "ปานกลาง": "●", "สูง": "●"}

SCORE_ACTION = {
    "ต่ำ": (
        "สถานีงานอยู่ในเกณฑ์ที่ยอมรับได้ในปัจจุบัน",
        "ไม่จำเป็นต้องดำเนินการแก้ไขในทันที ควรติดตามและประเมินซ้ำเป็นระยะ",
    ),
    "ปานกลาง": (
        "สถานีงานมีปัจจัยเสี่ยงที่อาจส่งผลต่อสุขภาพกล้ามเนื้อและกระดูก",
        "ควรวางแผนปรับปรุงสถานีงานในระยะอันใกล้ และติดตามอาการผิดปกติ",
    ),
    "สูง": (
        "สถานีงานมีความเสี่ยงสูง จำเป็นต้องได้รับการแก้ไขโดยเร่งด่วน",
        "ต้องดำเนินการปรับปรุงสถานีงานทันที และพิจารณาส่งพบแพทย์อาชีวเวชศาสตร์",
    ),
}

# ── Helpers ───────────────────────────────────────────────────────────────────
PW = 17 * cm  # page usable width (A4 – 2cm×2)

def _s(size=11, bold=False, color=None, align=TA_LEFT):
    return ParagraphStyle(
        f"_{size}{'B' if bold else ''}_{id(color)}",
        fontName=FONT_BOLD if bold else FONT_REG,
        fontSize=size, textColor=color or C_BLACK,
        alignment=align, leading=size * 1.4,
    )

def _p(text, **kw):
    return Paragraph(str(text), _s(**kw))

def _score_bar_color(score):
    if score <= 4: return C_GREEN
    if score == 5: return C_ORANGE
    return C_RED

def _score_chip(score):
    clr = _score_bar_color(score)
    t = Table([[_p(str(score), size=11, bold=True, color=C_WHITE, align=TA_CENTER)]],
              colWidths=[1.2*cm], rowHeights=[0.6*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), clr),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 0),
    ]))
    return t

def _section_bar(text):
    t = Table([[_p(f"  {text}", size=12, bold=True, color=C_WHITE)]],
              colWidths=[PW])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), C_NAVY),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 0),
    ]))
    return t

def _label_val_table(rows, col_w=None):
    """2-col or 4-col label/value table with standard style."""
    n_cols = len(rows[0])
    if col_w is None:
        col_w = [3.5*cm, 5*cm] * (n_cols // 2)
    t = Table(rows, colWidths=col_w)
    cmd = [
        ("FONTNAME",      (0,0), (-1,-1), FONT_REG),
        ("FONTSIZE",      (0,0), (-1,-1), 10.5),
        ("GRID",          (0,0), (-1,-1), 0.4, C_MGREY),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",  (0,0), (-1,-1), 6),
    ]
    # Shade label columns
    for col in range(0, n_cols, 2):
        cmd.append(("BACKGROUND", (col,0), (col,-1), C_LBLUE))
        cmd.append(("FONTNAME",   (col,0), (col,-1), FONT_BOLD))
    t.setStyle(TableStyle(cmd))
    return t


# ── Main generator ────────────────────────────────────────────────────────────
def generate_pdf(result: dict) -> str:
    p   = result["personal"]
    now = datetime.now()
    row_id   = result.get("row_id") or now.strftime("%Y%m%d%H%M%S")
    risk     = result.get("risk_level", "")
    final_sc = result.get("rosa_final_score", "-")
    desc, action = SCORE_ACTION.get(risk, ("", ""))

    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.close()

    doc = SimpleDocTemplate(
        tmp.name, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm,   bottomMargin=2*cm,
        title="รายงานผลการประเมิน ROSA",
    )
    story = []

    # ═══════════════════════════════════════════════════════
    # 1. DOCUMENT HEADER
    # ═══════════════════════════════════════════════════════
    hdr = Table([
        [
            _p("กรมควบคุมโรค กระทรวงสาธารณสุข\nสำนักงานป้องกันควบคุมโรคที่ 7 จังหวัดขอนแก่น",
               size=12, bold=True, color=C_WHITE),
            _p(f"เลขที่รายงาน: {row_id}\nวันที่พิมพ์: {now.strftime('%d/%m/%Y  %H:%M น.')}",
               size=10, color=C_WHITE, align=TA_RIGHT),
        ]
    ], colWidths=[10*cm, 7*cm])
    hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), C_NAVY),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (0,-1),  8),
        ("RIGHTPADDING",  (-1,0), (-1,-1), 8),
    ]))
    story.append(hdr)
    story.append(Spacer(1, 0.3*cm))

    # Title
    story.append(_p("รายงานผลการประเมินความเสี่ยงทางการยศาสตร์",
                    size=17, bold=True, color=C_NAVY, align=TA_CENTER))
    story.append(_p("Rapid Office Strain Assessment (ROSA)",
                    size=12, color=C_DGREY, align=TA_CENTER))
    story.append(Spacer(1, 0.15*cm))
    story.append(HRFlowable(width="100%", thickness=2.5, color=C_NAVY, spaceAfter=0.3*cm))

    # ═══════════════════════════════════════════════════════
    # 2. PERSONAL INFORMATION
    # ═══════════════════════════════════════════════════════
    story.append(_section_bar("1. ข้อมูลผู้รับการประเมิน"))
    story.append(Spacer(1, 0.2*cm))

    diseases = ", ".join(p.get("diseases", []))
    if p.get("diseases_other"):
        diseases += (" / " if diseases else "") + p["diseases_other"]

    bmi_val = _bmi(p)
    bmi_cat = (
        "น้ำหนักต่ำกว่าเกณฑ์" if bmi_val < 18.5 else
        "น้ำหนักปกติ" if bmi_val < 23 else
        "น้ำหนักเกิน" if bmi_val < 25 else
        "อ้วน"
    ) if bmi_val > 0 else "-"

    pi_rows = [
        ["ชื่อ – สกุล", p.get("name","–"),         "วันที่ประเมิน", now.strftime("%d/%m/%Y")],
        ["เพศ",          p.get("gender","–"),        "อายุ",          f"{p.get('age','–')} ปี"],
        ["น้ำหนัก",      f"{p.get('weight','–')} kg","ส่วนสูง",       f"{p.get('height','–')} cm"],
        ["รอบเอว",       f"{p.get('waist','–')} นิ้ว","BMI",          f"{bmi_val:.1f}  ({bmi_cat})" if bmi_val else "–"],
        ["ประเภทงาน",    p.get("job_type","–"),      "แผนก / หน่วยงาน", p.get("department","–")],
        ["อายุงาน",  f"{p.get('work_years',0)} ปี {p.get('work_months',0)} เดือน",
         "ชม.คอมพิวเตอร์/วัน", f"{p.get('computer_hours','–')} ชั่วโมง"],
    ]
    if diseases:
        pi_rows.append(["โรคประจำตัว", diseases, "", ""])

    pi_tbl = _label_val_table(pi_rows, col_w=[3.5*cm, 5*cm, 3.5*cm, 5*cm])
    if diseases:
        pi_tbl.setStyle(TableStyle([
            ("SPAN",    (1,-1), (3,-1)),
            ("FONTNAME",(0,0),(-1,-1), FONT_REG),
        ]))
    story.append(pi_tbl)
    story.append(Spacer(1, 0.4*cm))

    # ═══════════════════════════════════════════════════════
    # 3. ROSA RESULT SUMMARY
    # ═══════════════════════════════════════════════════════
    story.append(_section_bar("2. สรุปผลการประเมิน ROSA"))
    story.append(Spacer(1, 0.2*cm))

    risk_bg = RISK_BG.get(risk, C_LGREY)
    risk_fg = RISK_FG.get(risk, C_DGREY)

    # Big score + risk box (left) | Section scores (right)
    score_box = Table([
        [_p("ROSA Final Score", size=11, bold=True, color=risk_fg, align=TA_CENTER)],
        [_p(str(final_sc),      size=48, bold=True, color=risk_fg, align=TA_CENTER)],
        [_p(RISK_LABEL.get(risk,""), size=14, bold=True, color=risk_fg, align=TA_CENTER)],
    ], colWidths=[6*cm])
    score_box.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), risk_bg),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("BOX",           (0,0), (-1,-1), 1.5, risk_fg),
    ]))

    sec_scores = [
        ["ส่วน", "คะแนน", "ความหมาย"],
        ["A  เก้าอี้",                str(result.get("section_a_score","–")), "Chair"],
        ["B  หน้าจอ + โทรศัพท์",     str(result.get("section_b_score","–")), "Monitor/Phone"],
        ["C  เมาส์ + คีย์บอร์ด",      str(result.get("section_c_score","–")), "Mouse/Keyboard"],
        ["D  รวม B+C",                str(result.get("section_d_score","–")), "Peripherals"],
    ]
    sec_tbl = Table(sec_scores, colWidths=[5.5*cm, 2*cm, 3.5*cm])
    sec_cmd = [
        ("FONTNAME",      (0,0), (-1,-1), FONT_REG),
        ("FONTSIZE",      (0,0), (-1,-1), 10.5),
        ("BACKGROUND",    (0,0), (-1,0),  C_NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0),  C_WHITE),
        ("FONTNAME",      (0,0), (-1,0),  FONT_BOLD),
        ("ALIGN",         (1,0), (1,-1),  "CENTER"),
        ("GRID",          (0,0), (-1,-1), 0.4, C_MGREY),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ]
    # Color score cells by value
    for i, row in enumerate(sec_scores[1:], start=1):
        try:
            sc = int(row[1])
            clr = _score_bar_color(sc)
            sec_cmd.append(("TEXTCOLOR",   (1,i), (1,i), clr))
            sec_cmd.append(("FONTNAME",    (1,i), (1,i), FONT_BOLD))
            sec_cmd.append(("FONTSIZE",    (1,i), (1,i), 13))
            sec_cmd.append(("BACKGROUND",  (0,i), (-1,i), C_LGREY if i % 2 == 0 else C_WHITE))
        except (ValueError, TypeError):
            pass
    sec_tbl.setStyle(TableStyle(sec_cmd))

    summary_tbl = Table([[score_box, sec_tbl]], colWidths=[6.5*cm, 10.5*cm])
    summary_tbl.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING",   (1,0), (1,0),   8),
        ("TOPPADDING",    (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    story.append(summary_tbl)
    story.append(Spacer(1, 0.35*cm))

    # Interpretation box
    interp = Table([
        [_p("ความหมายของผล", size=11, bold=True, color=risk_fg)],
        [_p(desc,   size=11, color=C_BLACK)],
        [_p(f"คำแนะนำ: {action}", size=11, bold=True, color=risk_fg)],
    ], colWidths=[PW])
    interp.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), risk_bg),
        ("BOX",           (0,0), (-1,-1), 1, risk_fg),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story.append(interp)
    story.append(Spacer(1, 0.4*cm))

    # ═══════════════════════════════════════════════════════
    # 4. DETAILED SECTION SCORES
    # ═══════════════════════════════════════════════════════
    story.append(_section_bar("3. ผลคะแนนรายส่วน"))
    story.append(Spacer(1, 0.2*cm))

    # ─── Section A ───────────────────────────────────────
    a_data = [
        ["รายการ",                    "คะแนนย่อย",  "รายการ",                      "คะแนนย่อย"],
        ["ความสูงเบาะ",               result.get("chair_height_score","–"),
         "ความลึกเบาะ",               result.get("pan_depth_score","–")],
        ["แขนพัก",                    result.get("armrest_score","–"),
         "พนักพิง",                   result.get("back_support_score","–")],
        ["รวมเบาะ (แกนแถว)",          result.get("seat_pan_combined","–"),
         "รวมแขน/หลัง (แกนคอลัมน์)", result.get("armrest_back_combined","–")],
        ["คะแนนตาราง A",              result.get("table_a_score","–"),
         "Duration ที่ใช้เก้าอี้",   result.get("chair_duration","–")],
    ]
    a_final_sc = result.get("section_a_score", "-")

    def _detail_block(title, data, section_score, col_w=None):
        if col_w is None:
            col_w = [4.5*cm, 2*cm, 4.5*cm, 2*cm]  # adjusted to fit section header
        # Section sub-header
        sub_hdr = Table([
            [_p(title, size=11, bold=True, color=C_NAVY),
             _p(f"คะแนนส่วน = {section_score}", size=11, bold=True,
                color=_score_bar_color(int(section_score)) if str(section_score).isdigit() else C_DGREY,
                align=TA_RIGHT)]
        ], colWidths=[10*cm, 7*cm])
        sub_hdr.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), C_LBLUE),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING",   (0,0), (0,0),   8),
            ("RIGHTPADDING",  (-1,0), (-1,-1), 8),
            ("BOX",           (0,0), (-1,-1), 0.5, C_MGREY),
        ]))

        tbl = Table(data, colWidths=col_w)
        cmd = [
            ("FONTNAME",      (0,0), (-1,-1), FONT_REG),
            ("FONTSIZE",      (0,0), (-1,-1), 10),
            ("BACKGROUND",    (0,0), (-1,0),  C_NAVY),
            ("TEXTCOLOR",     (0,0), (-1,0),  C_WHITE),
            ("FONTNAME",      (0,0), (-1,0),  FONT_BOLD),
            ("ALIGN",         (1,0), (1,-1),  "CENTER"),
            ("ALIGN",         (3,0), (3,-1),  "CENTER"),
            ("GRID",          (0,0), (-1,-1), 0.4, C_MGREY),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
            ("BACKGROUND",    (0,1), (-1,1),  C_LGREY),
            ("BACKGROUND",    (0,3), (-1,3),  C_LGREY),
        ]
        tbl.setStyle(TableStyle(cmd))
        return KeepTogether([sub_hdr, tbl, Spacer(1, 0.3*cm)])

    story.append(_detail_block(
        "ส่วน A – เก้าอี้ (Chair)", a_data, a_final_sc
    ))

    # ─── Section B ───────────────────────────────────────
    b_data = [
        ["รายการ",             "คะแนนย่อย", "รายการ",         "คะแนนย่อย"],
        ["หน้าจอคอมพิวเตอร์",  result.get("monitor_score","–"),
         "โทรศัพท์",           result.get("phone_score","–")],
        ["หน้าจอ (คะแนนแกน)", result.get("monitor_axis","–"),
         "โทรศัพท์ (คะแนนแกน)", result.get("phone_axis","–")],
        ["Duration B",         result.get("section_b_duration","–"), "", ""],
    ]
    story.append(_detail_block(
        "ส่วน B – หน้าจอ + โทรศัพท์ (Monitor/Phone)", b_data,
        result.get("section_b_score","-")
    ))

    # ─── Section C ───────────────────────────────────────
    c_data = [
        ["รายการ",            "คะแนนย่อย", "รายการ",              "คะแนนย่อย"],
        ["เมาส์",             result.get("mouse_score","–"),
         "คีย์บอร์ด",         result.get("keyboard_score","–")],
        ["เมาส์ (คะแนนแกน)", result.get("mouse_axis","–"),
         "คีย์บอร์ด (คะแนนแกน)", result.get("keyboard_axis","–")],
        ["Duration C",        result.get("section_c_duration","–"), "", ""],
    ]
    story.append(_detail_block(
        "ส่วน C – เมาส์ + คีย์บอร์ด (Mouse/Keyboard)", c_data,
        result.get("section_c_score","-")
    ))

    # ─── Section D ───────────────────────────────────────
    d_data = [
        ["Section B", "Section C", "Section D (B × C)", "ROSA Final Score"],
        [str(result.get("section_b_score","–")),
         str(result.get("section_c_score","–")),
         str(result.get("section_d_score","–")),
         str(final_sc)],
    ]
    d_tbl = Table(d_data, colWidths=[4.25*cm]*4)
    d_cmd = [
        ("FONTNAME",      (0,0), (-1,-1), FONT_REG),
        ("FONTSIZE",      (0,0), (-1,-1), 10.5),
        ("BACKGROUND",    (0,0), (-1,0),  C_NAVY),
        ("TEXTCOLOR",     (0,0), (-1,0),  C_WHITE),
        ("FONTNAME",      (0,0), (-1,0),  FONT_BOLD),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("GRID",          (0,0), (-1,-1), 0.4, C_MGREY),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("BACKGROUND",    (3,1), (3,1),   RISK_BG.get(risk, C_LGREY)),
        ("TEXTCOLOR",     (3,1), (3,1),   RISK_FG.get(risk, C_DGREY)),
        ("FONTNAME",      (3,1), (3,1),   FONT_BOLD),
        ("FONTSIZE",      (3,1), (3,1),   14),
    ]
    d_tbl.setStyle(TableStyle(d_cmd))

    d_sub_hdr = Table(
        [[_p("ส่วน D – คะแนน Final (Section D = max(A, D_table))", size=11, bold=True, color=C_NAVY)]],
        colWidths=[PW]
    )
    d_sub_hdr.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), C_LBLUE),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("BOX",           (0,0), (-1,-1), 0.5, C_MGREY),
    ]))
    story.append(KeepTogether([d_sub_hdr, d_tbl, Spacer(1, 0.4*cm)]))

    # ═══════════════════════════════════════════════════════
    # 5. RECOMMENDATIONS
    # ═══════════════════════════════════════════════════════
    story.append(_section_bar("4. สรุปและข้อเสนอแนะ"))
    story.append(Spacer(1, 0.2*cm))

    rec_rows = [
        [_p("ผลการประเมิน", size=11, bold=True, color=C_NAVY),
         _p(RISK_LABEL.get(risk,""), size=11, bold=True,
            color=RISK_FG.get(risk, C_DGREY))],
        [_p("ROSA Final Score", size=11, bold=True, color=C_NAVY),
         _p(str(final_sc), size=11)],
        [_p("สรุปผล", size=11, bold=True, color=C_NAVY),
         _p(desc, size=11)],
        [_p("คำแนะนำ", size=11, bold=True, color=C_NAVY),
         _p(action, size=11)],
    ]
    rec_tbl = Table(rec_rows, colWidths=[4*cm, 13*cm])
    rec_tbl.setStyle(TableStyle([
        ("FONTNAME",      (0,0), (-1,-1), FONT_REG),
        ("FONTSIZE",      (0,0), (-1,-1), 10.5),
        ("GRID",          (0,0), (-1,-1), 0.4, C_MGREY),
        ("BACKGROUND",    (0,0), (-1,-1), C_WHITE),
        ("BACKGROUND",    (0,0), (0,-1),  C_LBLUE),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("BACKGROUND",    (0,2), (-1,3),  C_LGREY),
    ]))
    story.append(rec_tbl)
    story.append(Spacer(1, 0.6*cm))

    # ═══════════════════════════════════════════════════════
    # 6. SIGNATURE BLOCK
    # ═══════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=0.6, color=C_MGREY, spaceAfter=0.3*cm))
    sig_rows = [[
        _p("ผู้รับการประเมิน\n\n\nลงชื่อ ____________________\n"
           f"({p.get('name','……………………………')})\n"
           f"วันที่ {now.strftime('%d/%m/%Y')}",
           size=10.5, align=TA_CENTER),
        _p("เจ้าหน้าที่ผู้ประเมิน\n\n\nลงชื่อ ____________________\n"
           "(……………………………………)\n"
           "ตำแหน่ง ……………………………",
           size=10.5, align=TA_CENTER),
        _p("ผู้อนุมัติ\n\n\nลงชื่อ ____________________\n"
           "(……………………………………)\n"
           "ตำแหน่ง ……………………………",
           size=10.5, align=TA_CENTER),
    ]]
    sig_tbl = Table(sig_rows, colWidths=[PW/3]*3)
    sig_tbl.setStyle(TableStyle([
        ("FONTNAME",   (0,0), (-1,-1), FONT_REG),
        ("VALIGN",     (0,0), (-1,-1), "TOP"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("LINEBEFORE", (1,0), (1,-1), 0.5, C_MGREY),
        ("LINEBEFORE", (2,0), (2,-1), 0.5, C_MGREY),
    ]))
    story.append(sig_tbl)
    story.append(Spacer(1, 0.3*cm))

    # ═══════════════════════════════════════════════════════
    # 7. FOOTER
    # ═══════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_NAVY))
    story.append(Spacer(1, 0.1*cm))
    story.append(_p(
        "ระบบประเมินความเสี่ยง ROSA  |  "
        "กรมควบคุมโรค กระทรวงสาธารณสุข  |  "
        "อ้างอิง: Sonne, M. et al. (2012) Rapid Office Strain Assessment (ROSA)",
        size=8, color=C_DGREY, align=TA_CENTER,
    ))

    doc.build(story)
    return tmp.name


def _bmi(p: dict) -> float:
    h = p.get("height", 0)
    w = p.get("weight", 0)
    try:
        h, w = float(h), float(w)
        return w / ((h / 100) ** 2) if h else 0.0
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0
