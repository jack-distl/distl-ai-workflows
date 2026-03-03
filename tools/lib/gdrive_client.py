"""Shared Google Drive API authentication and file helpers."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive"]
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "token.json")
CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "credentials.json")


def get_drive_service():
    """Build and return an authenticated Google Drive API service.

    Uses credentials.json + token.json (OAuth 2.0 InstalledAppFlow).
    On first run, opens a browser for consent and saves token.json.
    On subsequent runs, loads the cached token and auto-refreshes if needed.
    """
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print("Error: Required packages not installed.")
        print("Run: pip install google-api-python-client google-auth-oauthlib")
        sys.exit(1)

    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}")
                print("Re-run tools/google_drive_auth_setup.py to re-authenticate.")
                sys.exit(1)
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                print(f"Error: {CREDENTIALS_PATH} not found.")
                print("Download OAuth client credentials from Google Cloud Console.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "w") as token_file:
            token_file.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def get_root_folder_id() -> str:
    """Get the Google Ads Reporting root folder ID from .env."""
    folder_id = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID")
    if not folder_id:
        print("Error: GOOGLE_DRIVE_ROOT_FOLDER_ID not set in .env")
        sys.exit(1)
    return folder_id


def find_file(service, name: str, folder_id: str) -> dict | None:
    """Search for a file by name within a folder. Returns file metadata or None."""
    query = f"name = '{name}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(
        q=query,
        fields="files(id, name, mimeType, modifiedTime)",
        pageSize=1,
    ).execute()
    files = results.get("files", [])
    return files[0] if files else None


def find_folder(service, name: str, parent_id: str) -> dict | None:
    """Search for a folder by name within a parent folder."""
    query = (
        f"name = '{name}' and '{parent_id}' in parents "
        f"and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    results = service.files().list(
        q=query,
        fields="files(id, name, modifiedTime)",
        pageSize=1,
    ).execute()
    files = results.get("files", [])
    return files[0] if files else None


def create_folder(service, name: str, parent_id: str) -> str:
    """Create a folder in Drive and return its ID."""
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def find_or_create_folder(service, name: str, parent_id: str) -> str:
    """Find a folder by name, or create it if it doesn't exist. Returns folder ID."""
    existing = find_folder(service, name, parent_id)
    if existing:
        return existing["id"]
    return create_folder(service, name, parent_id)


def download_file(service, file_id: str, local_path: str) -> str:
    """Download a file from Drive to a local path. Returns the local path."""
    from googleapiclient.http import MediaIoBaseDownload
    import io

    request = service.files().get_media(fileId=file_id)
    os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)

    with open(local_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

    return local_path


def upload_file(
    service,
    local_path: str,
    name: str,
    folder_id: str,
    file_id: str | None = None,
    mime_type: str = "text/markdown",
) -> dict:
    """Upload a new file or update an existing file on Drive.

    Args:
        service: Drive API service
        local_path: Path to the local file to upload
        name: File name on Drive
        folder_id: Parent folder ID
        file_id: If provided, updates existing file (preserving shares/comments)
        mime_type: MIME type for the upload

    Returns:
        Dict with 'id' and 'name' of the uploaded file
    """
    from googleapiclient.http import MediaFileUpload

    media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)

    if file_id:
        result = service.files().update(
            fileId=file_id,
            media_body=media,
            fields="id, name",
        ).execute()
    else:
        metadata = {
            "name": name,
            "parents": [folder_id],
        }
        result = service.files().create(
            body=metadata,
            media_body=media,
            fields="id, name",
        ).execute()

    return result


def list_files(
    service,
    folder_id: str,
    name_filter: str | None = None,
    mime_type: str | None = None,
) -> list[dict]:
    """List files in a folder, optionally filtered by name or MIME type.

    Returns list of dicts with id, name, mimeType, modifiedTime.
    """
    query_parts = [f"'{folder_id}' in parents", "trashed = false"]
    if name_filter:
        query_parts.append(f"name contains '{name_filter}'")
    if mime_type:
        query_parts.append(f"mimeType = '{mime_type}'")

    query = " and ".join(query_parts)
    all_files = []
    page_token = None

    while True:
        results = service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
            pageSize=100,
            pageToken=page_token,
            orderBy="modifiedTime desc",
        ).execute()
        all_files.extend(results.get("files", []))
        page_token = results.get("nextPageToken")
        if not page_token:
            break

    return all_files
