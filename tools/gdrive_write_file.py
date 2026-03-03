#!/usr/bin/env python3
"""Upload or update a file on Google Drive.

Usage:
    # Create new file:
    python tools/gdrive_write_file.py --local-path .tmp/report.md --drive-file-name "Report Feb 2026" --folder-id FOLDER_ID

    # Update existing file (preserves sharing settings):
    python tools/gdrive_write_file.py --local-path .tmp/report.md --file-id EXISTING_FILE_ID

Output: Prints the Drive file ID and web link to stdout.
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.lib.gdrive_client import get_drive_service, upload_file


def main():
    parser = argparse.ArgumentParser(description="Upload or update a file on Google Drive")
    parser.add_argument("--local-path", required=True, help="Path to local file to upload")
    parser.add_argument("--drive-file-name", help="Name for the file on Drive (required for new files)")
    parser.add_argument("--folder-id", help="Target folder ID (required for new files)")
    parser.add_argument("--file-id", help="Existing file ID to update (omit to create new)")
    parser.add_argument("--mime-type", default="text/markdown", help="MIME type (default: text/markdown)")
    args = parser.parse_args()

    if not os.path.exists(args.local_path):
        print(f"Error: Local file not found: {args.local_path}")
        sys.exit(1)

    if not args.file_id and not (args.drive_file_name and args.folder_id):
        print("Error: For new files, provide --drive-file-name and --folder-id")
        print("       For updates, provide --file-id")
        sys.exit(1)

    service = get_drive_service()

    result = upload_file(
        service,
        local_path=args.local_path,
        name=args.drive_file_name or "",
        folder_id=args.folder_id or "",
        file_id=args.file_id,
        mime_type=args.mime_type,
    )

    file_id = result["id"]
    print(f"File ID: {file_id}")
    print(f"URL: https://drive.google.com/file/d/{file_id}/view")

    if args.file_id:
        print(f"Updated existing file: {result['name']}")
    else:
        print(f"Created new file: {result['name']}")


if __name__ == "__main__":
    main()
