from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    google_credentials_json: str = ""        # path to service-account JSON file
    google_sheet_id: str = ""                # Google Sheet ID
    google_drive_folder_id: str = ""         # Google Drive folder ID for PDFs
    admin_password: str = "admin1234"        # dashboard password
    app_title: str = "ระบบประเมินความเสี่ยง ROSA"
    app_version: str = "1.0.0"

    class Config:
        env_file = ".env"


settings = Settings()
