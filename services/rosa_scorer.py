# ROSA scoring tables and calculation logic
# Based on the Rapid Office Strain Assessment by Michael Sonne, MHK, CK.

# Table A: seat_pan (height+depth) x armrest_back → Chair section score
TABLE_A = {
    (2,2):2,(2,3):2,(2,4):3,(2,5):4,(2,6):5,(2,7):6,(2,8):7,(2,9):8,
    (3,2):2,(3,3):2,(3,4):3,(3,5):4,(3,6):5,(3,7):6,(3,8):7,(3,9):8,
    (4,2):3,(4,3):3,(4,4):3,(4,5):4,(4,6):5,(4,7):6,(4,8):7,(4,9):8,
    (5,2):4,(5,3):4,(5,4):4,(5,5):4,(5,6):5,(5,7):6,(5,8):7,(5,9):8,
    (6,2):5,(6,3):5,(6,4):5,(6,5):5,(6,6):6,(6,7):7,(6,8):8,(6,9):9,
    (7,2):6,(7,3):6,(7,4):6,(7,5):7,(7,6):7,(7,7):8,(7,8):8,(7,9):9,
    (8,2):7,(8,3):7,(8,4):7,(8,5):8,(8,6):8,(8,7):9,(8,8):9,(8,9):9,
}

# Table B: phone x monitor → Section B score
TABLE_B = {
    (0,0):1,(0,1):1,(0,2):1,(0,3):2,(0,4):3,(0,5):4,(0,6):5,(0,7):6,
    (1,0):1,(1,1):1,(1,2):2,(1,3):2,(1,4):3,(1,5):4,(1,6):5,(1,7):6,
    (2,0):1,(2,1):2,(2,2):2,(2,3):3,(2,4):3,(2,5):4,(2,6):6,(2,7):7,
    (3,0):2,(3,1):2,(3,2):3,(3,3):3,(3,4):4,(3,5):5,(3,6):6,(3,7):8,
    (4,0):3,(4,1):3,(4,2):4,(4,3):4,(4,4):5,(4,5):6,(4,6):7,(4,7):8,
    (5,0):4,(5,1):4,(5,2):5,(5,3):5,(5,4):6,(5,5):7,(5,6):8,(5,7):9,
    (6,0):5,(6,1):5,(6,2):6,(6,3):7,(6,4):8,(6,5):8,(6,6):9,(6,7):9,
}

# Table C: mouse x keyboard → Section C score
TABLE_C = {
    (0,0):1,(0,1):1,(0,2):1,(0,3):2,(0,4):3,(0,5):4,(0,6):5,(0,7):6,
    (1,0):1,(1,1):1,(1,2):2,(1,3):3,(1,4):4,(1,5):5,(1,6):6,(1,7):7,
    (2,0):1,(2,1):2,(2,2):2,(2,3):3,(2,4):4,(2,5):5,(2,6):6,(2,7):7,
    (3,0):2,(3,1):3,(3,2):3,(3,3):3,(3,4):5,(3,5):6,(3,6):7,(3,7):8,
    (4,0):3,(4,1):4,(4,2):4,(4,3):5,(4,4):5,(4,5):6,(4,6):7,(4,7):8,
    (5,0):4,(5,1):5,(5,2):5,(5,3):6,(5,4):6,(5,5):7,(5,6):8,(5,7):9,
    (6,0):5,(6,1):6,(6,2):6,(6,3):7,(6,4):7,(6,5):8,(6,6):8,(6,7):9,
    (7,0):6,(7,1):7,(7,2):7,(7,3):8,(7,4):8,(7,5):9,(7,6):9,(7,7):9,
}

# Table D: section_b x section_c → Monitor+Peripherals score
TABLE_D = {
    (1,1):1,(1,2):2,(1,3):3,(1,4):4,(1,5):5,(1,6):6,(1,7):7,(1,8):8,(1,9):9,
    (2,1):2,(2,2):2,(2,3):3,(2,4):4,(2,5):5,(2,6):6,(2,7):7,(2,8):8,(2,9):9,
    (3,1):3,(3,2):3,(3,3):3,(3,4):4,(3,5):5,(3,6):6,(3,7):7,(3,8):8,(3,9):9,
    (4,1):4,(4,2):4,(4,3):4,(4,4):4,(4,5):5,(4,6):6,(4,7):7,(4,8):8,(4,9):9,
    (5,1):5,(5,2):5,(5,3):5,(5,4):5,(5,5):5,(5,6):6,(5,7):7,(5,8):8,(5,9):9,
    (6,1):6,(6,2):6,(6,3):6,(6,4):6,(6,5):6,(6,6):6,(6,7):7,(6,8):8,(6,9):9,
    (7,1):7,(7,2):7,(7,3):7,(7,4):7,(7,5):7,(7,6):7,(7,7):7,(7,8):8,(7,9):9,
    (8,1):8,(8,2):8,(8,3):8,(8,4):8,(8,5):8,(8,6):8,(8,7):8,(8,8):8,(8,9):9,
    (9,1):9,(9,2):9,(9,3):9,(9,4):9,(9,5):9,(9,6):9,(9,7):9,(9,8):9,(9,9):9,
}


def _clamp(val, lo, hi):
    return max(lo, min(hi, val))


def calc_chair_height_score(base: int, under_desk: bool) -> int:
    return base + (1 if under_desk else 0)


def calc_pan_depth_score(base: int, non_adjustable: bool) -> int:
    return base + (1 if non_adjustable else 0)


def calc_armrest_score(base: int, hard_surface: bool, too_wide: bool, non_adjustable: bool) -> int:
    return base + (1 if hard_surface else 0) + (1 if too_wide else 0) + (1 if non_adjustable else 0)


def calc_back_support_score(base: int, surface_too_high: bool, non_adjustable: bool) -> int:
    return base + (1 if surface_too_high else 0) + (1 if non_adjustable else 0)


def calc_monitor_score(base: int, too_far: bool, neck_twist: bool, glare: bool,
                       no_doc_holder: bool, non_adjustable: bool) -> int:
    return (base
            + (1 if too_far else 0)
            + (1 if neck_twist else 0)
            + (1 if glare else 0)
            + (1 if no_doc_holder else 0)
            + (1 if non_adjustable else 0))


def calc_phone_score(base: int, neck_shoulder_hold: bool, no_hands_free: bool) -> int:
    return base + (2 if neck_shoulder_hold else 0) + (1 if no_hands_free else 0)


def calc_mouse_score(base: int, diff_surfaces: bool, pinch_grip: bool, palmrest: bool) -> int:
    return base + (2 if diff_surfaces else 0) + (1 if pinch_grip else 0) + (1 if palmrest else 0)


def calc_keyboard_score(base: int, deviation: bool, too_high: bool,
                        overhead: bool, non_adjustable: bool) -> int:
    return (base
            + (1 if deviation else 0)
            + (1 if too_high else 0)
            + (1 if overhead else 0)
            + (1 if non_adjustable else 0))


def calc_section_a(chair_height: int, pan_depth: int, armrest: int, back: int, duration: int) -> dict:
    seat_pan = _clamp(chair_height + pan_depth, 2, 8)
    armrest_back = _clamp(armrest + back, 2, 9)
    table_a = TABLE_A.get((seat_pan, armrest_back), TABLE_A[(_clamp(seat_pan,2,8), _clamp(armrest_back,2,9))])
    chair_score = _clamp(table_a + duration, 1, 10)
    return {
        "chair_height_score": chair_height,
        "pan_depth_score": pan_depth,
        "armrest_score": armrest,
        "back_support_score": back,
        "seat_pan_combined": seat_pan,
        "armrest_back_combined": armrest_back,
        "table_a_score": table_a,
        "chair_duration": duration,
        "section_a_score": chair_score,
    }


def calc_section_b(monitor: int, phone: int, duration: int) -> dict:
    monitor_axis = _clamp(monitor + duration, 0, 7)
    phone_axis = _clamp(phone + duration, 0, 6)
    section_b = TABLE_B.get(
        (phone_axis, monitor_axis),
        TABLE_B[(_clamp(phone_axis,0,6), _clamp(monitor_axis,0,7))]
    )
    return {
        "monitor_score": monitor,
        "phone_score": phone,
        "monitor_axis": monitor_axis,
        "phone_axis": phone_axis,
        "section_b_duration": duration,
        "section_b_score": section_b,
    }


def calc_section_c(mouse: int, keyboard: int, duration: int) -> dict:
    keyboard_axis = _clamp(keyboard + duration, 0, 7)
    mouse_axis = _clamp(mouse + duration, 0, 7)
    section_c = TABLE_C.get(
        (mouse_axis, keyboard_axis),
        TABLE_C[(_clamp(mouse_axis,0,7), _clamp(keyboard_axis,0,7))]
    )
    return {
        "mouse_score": mouse,
        "keyboard_score": keyboard,
        "mouse_axis": mouse_axis,
        "keyboard_axis": keyboard_axis,
        "section_c_duration": duration,
        "section_c_score": section_c,
    }


def calc_final(section_a: int, section_b: int, section_c: int) -> dict:
    b_clamped = _clamp(section_b, 1, 9)
    c_clamped = _clamp(section_c, 1, 9)
    section_d = TABLE_D.get(
        (b_clamped, c_clamped),
        TABLE_D[(_clamp(b_clamped,1,9), _clamp(c_clamped,1,9))]
    )
    a_clamped = _clamp(section_a, 1, 10)
    d_clamped = _clamp(section_d, 1, 9)
    rosa_final = max(a_clamped, d_clamped)

    if rosa_final <= 4:
        risk_level = "ต่ำ"
        risk_color = "success"
        risk_desc = "ยังไม่จำเป็นต้องมีการปรับปรุงในขณะนี้"
        risk_action = "ติดตามและสังเกตอาการเป็นระยะ"
    elif rosa_final == 5:
        risk_level = "ปานกลาง"
        risk_color = "warning"
        risk_desc = "จำเป็นต้องมีการตรวจสอบและศึกษาเพิ่มเติม"
        risk_action = "ควรปรึกษาผู้เชี่ยวชาญด้านการยศาสตร์"
    else:
        risk_level = "สูง"
        risk_color = "danger"
        risk_desc = "จำเป็นต้องมีการแก้ไขโดยทันที"
        risk_action = "ปรับปรุงสภาพแวดล้อมการทำงานทันที และปรึกษาผู้เชี่ยวชาญ"

    return {
        "section_d_score": section_d,
        "rosa_final_score": rosa_final,
        "risk_level": risk_level,
        "risk_color": risk_color,
        "risk_description": risk_desc,
        "risk_action": risk_action,
    }


def calculate_rosa(data: dict) -> dict:
    # Section A
    ch = calc_chair_height_score(data["chair_height_base"], data.get("chair_under_desk", False))
    pd = calc_pan_depth_score(data["pan_depth_base"], data.get("pan_non_adjustable", False))
    ar = calc_armrest_score(
        data["armrest_base"],
        data.get("armrest_hard_surface", False),
        data.get("armrest_too_wide", False),
        data.get("armrest_non_adjustable", False),
    )
    bs = calc_back_support_score(
        data["back_base"],
        data.get("back_surface_too_high", False),
        data.get("back_non_adjustable", False),
    )
    sec_a = calc_section_a(ch, pd, ar, bs, data["chair_duration"])

    # Section B
    mon = calc_monitor_score(
        data["monitor_base"],
        data.get("monitor_too_far", False),
        data.get("monitor_neck_twist", False),
        data.get("monitor_glare", False),
        data.get("monitor_no_doc_holder", False),
        data.get("monitor_non_adjustable", False),
    )
    ph = calc_phone_score(
        data["phone_base"],
        data.get("phone_neck_shoulder", False),
        data.get("phone_no_hands_free", False),
    )
    sec_b = calc_section_b(mon, ph, data["section_b_duration"])

    # Section C
    ms = calc_mouse_score(
        data["mouse_base"],
        data.get("mouse_diff_surfaces", False),
        data.get("mouse_pinch_grip", False),
        data.get("mouse_palmrest", False),
    )
    kb = calc_keyboard_score(
        data["keyboard_base"],
        data.get("keyboard_deviation", False),
        data.get("keyboard_too_high", False),
        data.get("keyboard_overhead", False),
        data.get("keyboard_non_adjustable", False),
    )
    sec_c = calc_section_c(ms, kb, data["section_c_duration"])

    final = calc_final(sec_a["section_a_score"], sec_b["section_b_score"], sec_c["section_c_score"])

    return {**sec_a, **sec_b, **sec_c, **final}
