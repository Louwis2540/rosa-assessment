from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from config import settings
import json, os

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
]


def _get_service():
    val = settings.google_credentials_json
    if val:
        if val.strip().startswith("{"):
            try:
                creds = Credentials.from_service_account_info(json.loads(val), scopes=SCOPES)
                return build("drive", "v3", credentials=creds)
            except Exception as e:
                print(f"Drive creds from JSON failed: {e}, falling back to ADC")
        elif os.path.exists(val):
            creds = Credentials.from_service_account_file(val, scopes=SCOPES)
            return build("drive", "v3", credentials=creds)
    # Use Application Default Credentials (Cloud Run service account identity)
    import google.auth
    from google.auth.transport.requests import Request
    creds, _ = google.auth.default(scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def upload_pdf(local_path: str, filename: str) -> str:
    service = _get_service()
    if service is None:
        return ""
    folder_id = settings.google_drive_folder_id
    meta = {"name": filename, "parents": [folder_id] if folder_id else []}
    media = MediaFileUpload(local_path, mimetype="application/pdf")
    file = service.files().create(body=meta, media_body=media, fields="id,webViewLink").execute()
    service.permissions().create(
        fileId=file["id"],
        body={"type": "anyone", "role": "reader"},
    ).execute()
    return file.get("webViewLink", "")
