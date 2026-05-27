from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from config import settings
import os

SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
]


def _get_service():
    import json
    val = settings.google_credentials_json
    if not val:
        return None
    if val.strip().startswith("{"):
        creds = Credentials.from_service_account_info(json.loads(val), scopes=SCOPES)
    elif os.path.exists(val):
        creds = Credentials.from_service_account_file(val, scopes=SCOPES)
    else:
        return None
    return build("drive", "v3", credentials=creds)


def upload_pdf(local_path: str, filename: str) -> str:
    service = _get_service()
    if service is None:
        return ""
    folder_id = settings.google_drive_folder_id
    meta = {"name": filename, "parents": [folder_id] if folder_id else []}
    media = MediaFileUpload(local_path, mimetype="application/pdf")
    file = service.files().create(body=meta, media_body=media, fields="id,webViewLink").execute()
    # make it readable by anyone with link
    service.permissions().create(
        fileId=file["id"],
        body={"type": "anyone", "role": "reader"},
    ).execute()
    return file.get("webViewLink", "")
