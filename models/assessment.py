from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PersonalInfo(BaseModel):
    name: str
    gender: str                   # ชาย / หญิง / ไม่ระบุ
    age: int
    weight: float                 # kg
    height: float                 # cm
    waist: float                  # inches
    diseases: List[str] = []      # โรคประจำตัว (list)
    diseases_other: str = ""
    job_type: str
    department: str
    work_years: int = 0
    work_months: int = 0
    computer_hours: float         # ชั่วโมง/วัน


class ChairSection(BaseModel):
    # Chair height
    chair_height_base: int        # 1=good, 2=too low/high, 3=no foot contact
    chair_under_desk: bool = False   # +1
    # Pan depth
    pan_depth_base: int           # 1=good, 2=too long/short
    pan_non_adjustable: bool = False  # +1
    # Armrest
    armrest_base: int             # 1=good, 2=too high/low
    armrest_hard_surface: bool = False   # +1
    armrest_too_wide: bool = False       # +1
    armrest_non_adjustable: bool = False # +1
    # Back support
    back_base: int                # 1=good, 2=no/wrong support
    back_surface_too_high: bool = False  # +1
    back_non_adjustable: bool = False    # +1
    # Duration
    chair_duration: int           # -1 / 0 / +1


class MonitorPhoneSection(BaseModel):
    # Monitor
    monitor_base: int             # 1=good, 2=too low, 3=too high
    monitor_too_far: bool = False      # +1
    monitor_neck_twist: bool = False   # +1
    monitor_glare: bool = False        # +1
    monitor_no_doc_holder: bool = False # +1
    monitor_non_adjustable: bool = False # +1
    # Phone
    phone_base: int               # 1=good, 2=too far
    phone_neck_shoulder: bool = False  # +2
    phone_no_hands_free: bool = False  # +1
    # Duration
    section_b_duration: int       # -1 / 0 / +1


class MouseKeyboardSection(BaseModel):
    # Mouse
    mouse_base: int               # 1=good, 2=reaching
    mouse_diff_surfaces: bool = False  # +2
    mouse_pinch_grip: bool = False     # +1
    mouse_palmrest: bool = False       # +1
    # Keyboard
    keyboard_base: int            # 1=good, 2=wrist extended
    keyboard_deviation: bool = False   # +1
    keyboard_too_high: bool = False    # +1
    keyboard_overhead: bool = False    # +1
    keyboard_non_adjustable: bool = False # +1
    # Duration
    section_c_duration: int       # -1 / 0 / +1


class AssessmentSubmit(BaseModel):
    personal: PersonalInfo
    chair: ChairSection
    monitor_phone: MonitorPhoneSection
    mouse_keyboard: MouseKeyboardSection


class AssessmentResult(BaseModel):
    id: Optional[str] = None
    timestamp: Optional[datetime] = None
    personal: PersonalInfo
    # Raw section scores
    chair_height_score: int
    pan_depth_score: int
    armrest_score: int
    back_support_score: int
    seat_pan_combined: int
    armrest_back_combined: int
    table_a_score: int
    chair_duration: int
    section_a_score: int
    monitor_score: int
    phone_score: int
    monitor_axis: int
    phone_axis: int
    section_b_duration: int
    section_b_score: int
    mouse_score: int
    keyboard_score: int
    mouse_axis: int
    keyboard_axis: int
    section_c_duration: int
    section_c_score: int
    # Final
    section_d_score: int
    rosa_final_score: int
    risk_level: str
    risk_color: str
    risk_description: str
    risk_action: str
    pdf_url: Optional[str] = None
