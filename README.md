# ระบบประเมินความเสี่ยง ROSA (Rapid Office Strain Assessment)

## การติดตั้งและใช้งาน

### 1. ติดตั้ง Python dependencies

```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า Google API

#### 2.1 สร้าง Google Cloud Project
1. ไปที่ [Google Cloud Console](https://console.cloud.google.com)
2. สร้าง Project ใหม่ (หรือใช้ที่มีอยู่)
3. เปิดใช้งาน APIs:
   - **Google Sheets API**
   - **Google Drive API**

#### 2.2 สร้าง Service Account
1. ไปที่ IAM & Admin → Service Accounts → Create Service Account
2. ตั้งชื่อ เช่น `rosa-assessment`
3. สร้าง Key (JSON) และดาวน์โหลด → บันทึกเป็น `credentials.json` ในโฟลเดอร์โปรเจกต์

#### 2.3 สร้าง Google Sheet
1. สร้าง Google Sheet ใหม่
2. Share กับ email ของ Service Account (ที่อยู่ใน `credentials.json` ในช่อง `client_email`) — ให้สิทธิ์ **Editor**
3. คัดลอก Sheet ID จาก URL

#### 2.4 สร้าง Google Drive Folder
1. สร้างโฟลเดอร์ใน Google Drive สำหรับเก็บ PDF
2. Share กับ Service Account email — ให้สิทธิ์ **Editor**
3. คัดลอก Folder ID จาก URL

### 3. ตั้งค่า Environment Variables

```bash
cp .env.example .env
# แก้ไขค่าใน .env
```

### 4. รันแบบ Local

```bash
uvicorn main:app --reload --port 8000
```

เปิด browser ที่ http://localhost:8000

---

## Deploy บน Google Cloud Run

### ขั้นตอน

```bash
# 1. ติดตั้ง Google Cloud CLI และ login
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Build & Push Docker image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/rosa-assessment

# 3. Deploy to Cloud Run
gcloud run deploy rosa-assessment \
  --image gcr.io/YOUR_PROJECT_ID/rosa-assessment \
  --platform managed \
  --region asia-southeast1 \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_SHEET_ID=xxx,GOOGLE_DRIVE_FOLDER_ID=xxx,ADMIN_PASSWORD=xxx
```

> **หมายเหตุ:** ไฟล์ `credentials.json` ควรใส่เป็น Secret Manager แทนการ copy ลงใน image

---

## โครงสร้างโปรเจกต์

```
rosa-assessment/
├── main.py                  # FastAPI application
├── config.py                # Settings
├── requirements.txt
├── Dockerfile
├── .env.example
├── models/
│   └── assessment.py        # Pydantic data models
├── services/
│   ├── rosa_scorer.py       # ROSA scoring engine (tables + logic)
│   ├── sheets_service.py    # Google Sheets integration
│   ├── drive_service.py     # Google Drive PDF upload
│   └── pdf_service.py       # PDF generation (ReportLab)
├── templates/
│   ├── base.html
│   ├── home.html            # Landing page
│   ├── assess.html          # Assessment form (5 steps)
│   ├── result.html          # Individual result
│   ├── dashboard.html       # Admin dashboard
│   └── login.html           # Dashboard login
└── static/
    ├── css/style.css
    └── js/assessment.js     # Form wizard logic
```

---

## การตีความคะแนน ROSA

| คะแนน | ระดับความเสี่ยง | ความหมาย |
|--------|-----------------|----------|
| 1–4   | ต่ำ             | ยังไม่จำเป็นต้องแก้ไข |
| 5–6   | ปานกลาง         | ควรตรวจสอบและปรับปรุง |
| 7–10  | สูง             | จำเป็นต้องแก้ไขโดยทันที |

---

## Dashboard

เข้า `/dashboard?pw=YOUR_ADMIN_PASSWORD`

---

*ROSA – Rapid Office Strain Assessment by Michael Sonne, MHK, CK.*
