"""Google Drive MCP tools for client brief and report management.

Folder convention on Drive:
    {ROOT_FOLDER}/
        {Client Name}/
            brief.md
            reports/
                {Client Name} - Google Ads Report - {Month Year}.md
"""

import io
import logging
import os

from app import mcp
from security import log_tool_call, sanitize_for_drive_query, validate_client_name

logger = logging.getLogger(__name__)

# --- Internal helpers (not exposed as MCP tools) ---


def _get_drive_service():
    """Build and return an authenticated Google Drive API service.

    Uses a service account JSON key (for server deployment) or OAuth
    credentials (for local dev). Credentials are read from environment
    variables, never from the caller.
    """
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    # Prefer service account for server deployment
    sa_key_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY_PATH")
    if sa_key_path and os.path.exists(sa_key_path):
        scopes = ["https://www.googleapis.com/auth/drive"]
        creds = service_account.Credentials.from_service_account_file(
            sa_key_path, scopes=scopes
        )
        return build("drive", "v3", credentials=creds)

    # Fallback: OAuth refresh token (for local dev / migration from CLI tools)
    from google.oauth2.credentials import Credentials

    refresh_token = os.getenv("GOOGLE_DRIVE_REFRESH_TOKEN")
    client_id = os.getenv("GOOGLE_DRIVE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_DRIVE_CLIENT_SECRET")

    if refresh_token and client_id and client_secret:
        creds = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=["https://www.googleapis.com/auth/drive"],
        )
        return build("drive", "v3", credentials=creds)

    raise RuntimeError(
        "No Google Drive credentials configured. "
        "Set GOOGLE_SERVICE_ACCOUNT_KEY_PATH or GOOGLE_DRIVE_REFRESH_TOKEN + CLIENT_ID + CLIENT_SECRET."
    )


def _get_root_folder_id() -> str:
    folder_id = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID")
    if not folder_id:
        raise RuntimeError("GOOGLE_DRIVE_ROOT_FOLDER_ID not set.")
    return folder_id


def _find_folder(service, name: str, parent_id: str) -> dict | None:
    safe_name = sanitize_for_drive_query(name)
    query = (
        f"name = '{safe_name}' and '{parent_id}' in parents "
        f"and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    results = (
        service.files()
        .list(q=query, fields="files(id, name, modifiedTime)", pageSize=1)
        .execute()
    )
    files = results.get("files", [])
    return files[0] if files else None


def _find_or_create_folder(service, name: str, parent_id: str) -> str:
    existing = _find_folder(service, name, parent_id)
    if existing:
        return existing["id"]
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def _find_file(service, name: str, folder_id: str) -> dict | None:
    safe_name = sanitize_for_drive_query(name)
    query = f"name = '{safe_name}' and '{folder_id}' in parents and trashed = false"
    results = (
        service.files()
        .list(
            q=query,
            fields="files(id, name, mimeType, modifiedTime)",
            pageSize=1,
        )
        .execute()
    )
    files = results.get("files", [])
    return files[0] if files else None


def _download_as_text(service, file_id: str) -> str:
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    from googleapiclient.http import MediaIoBaseDownload

    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buffer.getvalue().decode("utf-8")


def _upload_text(
    service,
    content: str,
    name: str,
    folder_id: str,
    file_id: str | None = None,
) -> dict:
    from googleapiclient.http import MediaInMemoryUpload

    media = MediaInMemoryUpload(
        content.encode("utf-8"), mimetype="text/markdown", resumable=False
    )
    if file_id:
        result = (
            service.files()
            .update(fileId=file_id, media_body=media, fields="id, name")
            .execute()
        )
    else:
        metadata = {"name": name, "parents": [folder_id]}
        result = (
            service.files()
            .create(body=metadata, media_body=media, fields="id, name")
            .execute()
        )
    return result


def _list_files_in_folder(
    service, folder_id: str, name_filter: str | None = None
) -> list[dict]:
    query_parts = [f"'{folder_id}' in parents", "trashed = false"]
    if name_filter:
        safe_filter = sanitize_for_drive_query(name_filter)
        query_parts.append(f"name contains '{safe_filter}'")
    query = " and ".join(query_parts)
    all_files = []
    page_token = None
    while True:
        results = (
            service.files()
            .list(
                q=query,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime)",
                pageSize=100,
                pageToken=page_token,
                orderBy="modifiedTime desc",
            )
            .execute()
        )
        all_files.extend(results.get("files", []))
        page_token = results.get("nextPageToken")
        if not page_token:
            break
    return all_files


# --- MCP Tools ---


@mcp.tool()
async def drive_read_brief(client_name: str) -> str:
    """Read a client's strategy brief from Google Drive.

    Looks for brief.md inside the client's folder under the root reporting folder.
    Returns the brief text, or a message if no brief exists.

    Args:
        client_name: The client folder name on Google Drive (e.g. "Acme Corp")
    """
    try:
        client_name = validate_client_name(client_name)
    except ValueError as e:
        return str(e)

    log_tool_call("drive_read_brief", client_name=client_name)

    try:
        service = _get_drive_service()
        root_id = _get_root_folder_id()

        client_folder = _find_folder(service, client_name, root_id)
        if not client_folder:
            return f"No folder found for client '{client_name}'. A new brief will need to be created."

        brief = _find_file(service, "brief.md", client_folder["id"])
        if not brief:
            return f"Client folder '{client_name}' exists but no brief.md found. A new brief will need to be created."

        content = _download_as_text(service, brief["id"])
        return f"# Brief for {client_name}\n\n{content}"

    except Exception as e:
        logger.exception("drive_read_brief failed")
        return "Error reading brief. Check server logs for details."


@mcp.tool()
async def drive_save_brief(client_name: str, content: str) -> str:
    """Save or update a client's strategy brief on Google Drive.

    Creates the client folder if it doesn't exist. Updates the existing brief.md
    if one exists, or creates a new one.

    Args:
        client_name: The client folder name on Google Drive (e.g. "Acme Corp")
        content: The full brief text in markdown format
    """
    try:
        client_name = validate_client_name(client_name)
    except ValueError as e:
        return str(e)

    log_tool_call("drive_save_brief", client_name=client_name, content=content)

    try:
        service = _get_drive_service()
        root_id = _get_root_folder_id()

        client_folder_id = _find_or_create_folder(service, client_name, root_id)
        existing_brief = _find_file(service, "brief.md", client_folder_id)
        file_id = existing_brief["id"] if existing_brief else None

        result = _upload_text(service, content, "brief.md", client_folder_id, file_id)
        action = "Updated" if file_id else "Created"
        url = f"https://drive.google.com/file/d/{result['id']}/view"
        return f"{action} brief for {client_name}.\nFile: {url}"

    except Exception as e:
        logger.exception("drive_save_brief failed")
        return "Error saving brief. Check server logs for details."


@mcp.tool()
async def drive_get_latest_report(client_name: str) -> str:
    """Get the most recent monthly report for a client from Google Drive.

    Looks in {client_name}/reports/ for the most recently modified report file.
    Returns the report text, or a message if no reports exist.

    Args:
        client_name: The client folder name on Google Drive (e.g. "Acme Corp")
    """
    try:
        client_name = validate_client_name(client_name)
    except ValueError as e:
        return str(e)

    log_tool_call("drive_get_latest_report", client_name=client_name)

    try:
        service = _get_drive_service()
        root_id = _get_root_folder_id()

        client_folder = _find_folder(service, client_name, root_id)
        if not client_folder:
            return f"No folder found for client '{client_name}'. No previous reports."

        reports_folder = _find_folder(service, "reports", client_folder["id"])
        if not reports_folder:
            return f"No reports/ subfolder found for '{client_name}'. This will be the first report."

        files = _list_files_in_folder(service, reports_folder["id"])
        if not files:
            return f"Reports folder exists for '{client_name}' but is empty. This will be the first report."

        latest = files[0]  # Already sorted by modifiedTime desc
        content = _download_as_text(service, latest["id"])
        return f"# Latest Report: {latest['name']}\n\n{content}"

    except Exception as e:
        logger.exception("drive_get_latest_report failed")
        return "Error reading latest report. Check server logs for details."


@mcp.tool()
async def drive_save_report(
    client_name: str, month: str, content: str
) -> str:
    """Save a monthly report to Google Drive.

    Creates the client folder and reports/ subfolder if they don't exist.
    If a report for the same month already exists, it is updated.

    Args:
        client_name: The client folder name on Google Drive (e.g. "Acme Corp")
        month: The reporting month (e.g. "2026-02" or "February 2026")
        content: The full report text in markdown format
    """
    try:
        client_name = validate_client_name(client_name)
    except ValueError as e:
        return str(e)

    if not month or not month.strip():
        return "Month cannot be empty."

    log_tool_call("drive_save_report", client_name=client_name, month=month, content=content)

    try:
        service = _get_drive_service()
        root_id = _get_root_folder_id()

        client_folder_id = _find_or_create_folder(service, client_name, root_id)
        reports_folder_id = _find_or_create_folder(
            service, "reports", client_folder_id
        )

        report_name = f"{client_name} - Google Ads Report - {month}.md"
        existing = _find_file(service, report_name, reports_folder_id)
        file_id = existing["id"] if existing else None

        result = _upload_text(
            service, content, report_name, reports_folder_id, file_id
        )
        action = "Updated" if file_id else "Created"
        url = f"https://drive.google.com/file/d/{result['id']}/view"
        return f"{action} report: {report_name}\nFile: {url}"

    except Exception as e:
        logger.exception("drive_save_report failed")
        return "Error saving report. Check server logs for details."
