import os
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === Step 1: Ambil dan validasi Environment Variables ===

# Ambil dan cek credential GDrive
raw_credential = os.environ.get("GDRIVE_CREDENTIALS")
if not raw_credential:
    raise ValueError("Missing GDRIVE_CREDENTIALS environment variable. Pastikan sudah di-set di GitHub Secrets dan dikaitkan di workflow.")

try:
    creds = json.loads(raw_credential)
    # Jika hasil pertama masih string, decode sekali lagi
    if isinstance(creds, str):
        creds = json.loads(creds)
except json.JSONDecodeError as e:
    raise ValueError(f"GDRIVE_CREDENTIALS is not valid JSON. Error: {str(e)}")

# Ambil dan cek folder ID
SHARED_DRIVE_ID = os.environ.get("GDRIVE_FOLDER_ID")
if not SHARED_DRIVE_ID:
    raise ValueError("Missing GDRIVE_FOLDER_ID environment variable. Pastikan sudah di-set di GitHub Secrets.")

# === Step 2: Bangun koneksi ke Google Drive API ===
credentials = Credentials.from_service_account_info(
    creds,
    scopes=["https://www.googleapis.com/auth/drive"]
)
service = build('drive', 'v3', credentials=credentials)

# === Step 3: Fungsi Upload Rekursif ===
def upload_directory(local_dir_path, parent_drive_id):
    for item_name in os.listdir(local_dir_path):
        item_path = os.path.join(local_dir_path, item_name)
        if os.path.isdir(item_path):
            folder_meta = {
                'name': item_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_drive_id]
            }
            created_folder = service.files().create(
                body=folder_meta,
                fields='id',
                supportsAllDrives=True
            ).execute()
            new_folder_id = created_folder["id"]
            print(f"Created folder: {item_name} (ID: {new_folder_id})")

            upload_directory(item_path, new_folder_id)
        else:
            print(f"Uploading file: {item_name}")
            file_meta = {
                'name': item_name,
                'parents': [parent_drive_id]
            }
            media = MediaFileUpload(item_path, resumable=True)
            service.files().create(
                body=file_meta,
                media_body=media,
                fields='id',
                supportsAllDrives=True
            ).execute()

# === Step 4: Proses Upload dari "./mlruns/0" ===
local_mlruns_0 = "./mlruns/0"

for run_id in os.listdir(local_mlruns_0):
    run_id_local_path = os.path.join(local_mlruns_0, run_id)
    if os.path.isdir(run_id_local_path):
        run_id_folder_meta = {
            'name': run_id,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [SHARED_DRIVE_ID]
        }
        run_id_folder = service.files().create(
            body=run_id_folder_meta,
            fields='id',
            supportsAllDrives=True
        ).execute()
        run_id_folder_id = run_id_folder["id"]
        print(f"Created run_id folder: {run_id} (ID: {run_id_folder_id})")

        upload_directory(run_id_local_path, run_id_folder_id)

print("All run_id folders and files have been uploaded directly to Shared Drive!")
