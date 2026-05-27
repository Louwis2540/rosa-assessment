import json, os

A_COLS = [0, 188, 375, 563, 750, 940]
B_OFF = 1188
B_COLS = [0, 170, 340, 510, 680, 850, 1020]
bc = lambda i: B_OFF + B_COLS[i]

Y_CHAIR=(195,335); Y_PAN=(465,660); Y_ARM=(830,1055)
Y_BACK=(1180,1400); Y_MON=(195,335); Y_TEL=(545,665)
Y_MOUSE=(915,1055); Y_KEY=(1235,1395)

crops = {
 "chair_height_good":   {"y0":Y_CHAIR[0],"y1":Y_CHAIR[1],"x0":A_COLS[0],"x1":A_COLS[1],"label":"เข่า 90 (1)",         "section":"A1 ความสูงเบาะ","type":"option"},
 "chair_height_low":    {"y0":Y_CHAIR[0],"y1":Y_CHAIR[1],"x0":A_COLS[1],"x1":A_COLS[2],"label":"เตี้ยเกิน (2)",        "section":"A1 ความสูงเบาะ","type":"option"},
 "chair_height_high":   {"y0":Y_CHAIR[0],"y1":Y_CHAIR[1],"x0":A_COLS[2],"x1":A_COLS[3],"label":"สูงเกิน (2)",          "section":"A1 ความสูงเบาะ","type":"option"},
 "chair_height_nofeet": {"y0":Y_CHAIR[0],"y1":Y_CHAIR[1],"x0":A_COLS[3],"x1":A_COLS[4],"label":"เท้าไม่ถึงพื้น (3)",  "section":"A1 ความสูงเบาะ","type":"option"},
 "chair_under_desk":    {"y0":Y_CHAIR[0],"y1":Y_CHAIR[1],"x0":A_COLS[4],"x1":A_COLS[5],"label":"ขาชนใต้โต๊ะ (+1)",    "section":"A1 ความสูงเบาะ","type":"modifier"},
 "pan_depth_good":      {"y0":Y_PAN[0],"y1":Y_PAN[1],"x0":A_COLS[0],"x1":A_COLS[1],    "label":"ความลึกพอดี (1)",      "section":"A2 ความลึกเบาะ","type":"option"},
 "pan_depth_long":      {"y0":Y_PAN[0],"y1":Y_PAN[1],"x0":A_COLS[1],"x1":A_COLS[2],    "label":"ลึกเกิน (2)",          "section":"A2 ความลึกเบาะ","type":"option"},
 "pan_depth_short":     {"y0":Y_PAN[0],"y1":Y_PAN[1],"x0":A_COLS[2],"x1":A_COLS[3],    "label":"ตื้นเกิน (2)",         "section":"A2 ความลึกเบาะ","type":"option"},
 "armrest_good":        {"y0":Y_ARM[0],"y1":Y_ARM[1],"x0":A_COLS[0],"x1":A_COLS[1],    "label":"แขนพักพอดี (1)",       "section":"A3 แขนพัก","type":"option"},
 "armrest_high":        {"y0":Y_ARM[0],"y1":Y_ARM[1],"x0":A_COLS[1],"x1":A_COLS[2],    "label":"สูง/ต่ำเกิน (2)",      "section":"A3 แขนพัก","type":"option"},
 "armrest_hard":        {"y0":Y_ARM[0],"y1":Y_ARM[1],"x0":A_COLS[2],"x1":A_COLS[3],    "label":"พื้นผิวแข็ง (+1)",     "section":"A3 แขนพัก","type":"modifier"},
 "armrest_wide":        {"y0":Y_ARM[0],"y1":Y_ARM[1],"x0":A_COLS[3],"x1":A_COLS[4],    "label":"กว้างเกิน (+1)",        "section":"A3 แขนพัก","type":"modifier"},
 "back_good":           {"y0":Y_BACK[0],"y1":Y_BACK[1],"x0":A_COLS[0],"x1":A_COLS[1],  "label":"รองรับเอวดี (1)",      "section":"A4 พนักพิง","type":"option"},
 "back_no_lumbar":      {"y0":Y_BACK[0],"y1":Y_BACK[1],"x0":A_COLS[1],"x1":A_COLS[2],  "label":"ไม่มีรองรับเอว (2)",   "section":"A4 พนักพิง","type":"option"},
 "back_angled":         {"y0":Y_BACK[0],"y1":Y_BACK[1],"x0":A_COLS[2],"x1":A_COLS[3],  "label":"เอนมากเกิน (2)",       "section":"A4 พนักพิง","type":"option"},
 "back_none":           {"y0":Y_BACK[0],"y1":Y_BACK[1],"x0":A_COLS[3],"x1":A_COLS[4],  "label":"ไม่มีพนักพิง (2)",     "section":"A4 พนักพิง","type":"option"},
 "back_surface_high":   {"y0":Y_BACK[0],"y1":Y_BACK[1],"x0":A_COLS[4],"x1":A_COLS[5],  "label":"โต๊ะสูงเกิน (+1)",     "section":"A4 พนักพิง","type":"modifier"},
 "monitor_good":        {"y0":Y_MON[0],"y1":Y_MON[1],"x0":bc(0),"x1":bc(1),            "label":"หน้าจอพอดี (1)",        "section":"B1 หน้าจอ","type":"option"},
 "monitor_low":         {"y0":Y_MON[0],"y1":Y_MON[1],"x0":bc(1),"x1":bc(2),            "label":"ต่ำเกิน (2)",           "section":"B1 หน้าจอ","type":"option"},
 "monitor_high":        {"y0":Y_MON[0],"y1":Y_MON[1],"x0":bc(2),"x1":bc(3),            "label":"สูงเกิน (3)",           "section":"B1 หน้าจอ","type":"option"},
 "monitor_neck_twist":  {"y0":Y_MON[0],"y1":Y_MON[1],"x0":bc(3),"x1":bc(4),            "label":"บิดคอ (+1)",            "section":"B1 หน้าจอ","type":"modifier"},
 "monitor_glare":       {"y0":Y_MON[0],"y1":Y_MON[1],"x0":bc(4),"x1":bc(5),            "label":"แสงสะท้อน (+1)",        "section":"B1 หน้าจอ","type":"modifier"},
 "monitor_no_holder":   {"y0":Y_MON[0],"y1":Y_MON[1],"x0":bc(5),"x1":bc(6),            "label":"ไม่มีที่วางเอกสาร (+1)","section":"B1 หน้าจอ","type":"modifier"},
 "phone_good":          {"y0":Y_TEL[0],"y1":Y_TEL[1],"x0":bc(0),"x1":bc(0)+220,        "label":"โทรศัพท์ปกติ (1)",      "section":"B2 โทรศัพท์","type":"option"},
 "phone_far":           {"y0":Y_TEL[0],"y1":Y_TEL[1],"x0":bc(0)+220,"x1":bc(0)+620,    "label":"เอื้อมหยิบ (2)",        "section":"B2 โทรศัพท์","type":"option"},
 "phone_neck":          {"y0":Y_TEL[0],"y1":Y_TEL[1],"x0":bc(0)+620,"x1":bc(0)+920,    "label":"หนีบคอ (+2)",           "section":"B2 โทรศัพท์","type":"modifier"},
 "mouse_good":          {"y0":Y_MOUSE[0],"y1":Y_MOUSE[1],"x0":bc(0),"x1":bc(1),        "label":"เมาส์พอดี (1)",         "section":"C1 เมาส์","type":"option"},
 "mouse_reach":         {"y0":Y_MOUSE[0],"y1":Y_MOUSE[1],"x0":bc(1),"x1":bc(2),        "label":"เอื้อมเมาส์ (2)",       "section":"C1 เมาส์","type":"option"},
 "mouse_diff_surfaces": {"y0":Y_MOUSE[0],"y1":Y_MOUSE[1],"x0":bc(2),"x1":bc(3),        "label":"คนละระดับ (+2)",         "section":"C1 เมาส์","type":"modifier"},
 "mouse_pinch":         {"y0":Y_MOUSE[0],"y1":Y_MOUSE[1],"x0":bc(3),"x1":bc(4),        "label":"หยิกจับ (+1)",          "section":"C1 เมาส์","type":"modifier"},
 "mouse_palmrest":      {"y0":Y_MOUSE[0],"y1":Y_MOUSE[1],"x0":bc(4),"x1":bc(5),        "label":"ที่รองฝ่ามือ (+1)",     "section":"C1 เมาส์","type":"modifier"},
 "keyboard_good":       {"y0":Y_KEY[0],"y1":Y_KEY[1],"x0":bc(0),"x1":bc(1),            "label":"ข้อมือตรง (1)",         "section":"C2 คีย์บอร์ด","type":"option"},
 "keyboard_extended":   {"y0":Y_KEY[0],"y1":Y_KEY[1],"x0":bc(1),"x1":bc(2),            "label":"ข้อมือแอ่น (2)",        "section":"C2 คีย์บอร์ด","type":"option"},
 "keyboard_deviation":  {"y0":Y_KEY[0],"y1":Y_KEY[1],"x0":bc(2),"x1":bc(3),            "label":"ข้อมือบิด (+1)",        "section":"C2 คีย์บอร์ด","type":"modifier"},
 "keyboard_too_high":   {"y0":Y_KEY[0],"y1":Y_KEY[1],"x0":bc(3),"x1":bc(4),            "label":"คีย์บอร์ดสูง (+1)",     "section":"C2 คีย์บอร์ด","type":"modifier"},
 "keyboard_overhead":   {"y0":Y_KEY[0],"y1":Y_KEY[1],"x0":bc(4),"x1":bc(5),            "label":"เอื้อมสูง (+1)",        "section":"C2 คีย์บอร์ด","type":"modifier"},
}

os.makedirs("config", exist_ok=True)
with open("config/crops.json","w",encoding="utf-8") as f:
    json.dump(crops, f, ensure_ascii=False, indent=2)
print("crops.json saved:", len(crops), "entries")
