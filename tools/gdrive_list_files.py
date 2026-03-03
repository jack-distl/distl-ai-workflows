#!/usr/bin/env python3
"""List files in a Google Drive folder.

Usage:
    python tools/gdrive_list_files.py --folder-id FOLDER_ID
    python tools/gdrive_list_files.py --folder-id FOLDER_ID --name-filter "client name"
    python tools/gdrive_list_files.py --folder-id FOLDER_ID --mime-type "text/markdown"

Output: JSON array to stdout with file name, id, mimeType, modifiedTime.
"""

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.lib.gdrive_client import get_drive_service, get_root_folder_id, list_files


def main():
    parser = argparse.ArgumentParser(description="List files in a Google Drive folder")
    parser.add_argument("--folder-id", help="Drive folder ID (defaults to GOOGLE_DRIVE_ROOT_FOLDER_ID)")
    parser.add_argument("--name-filter", help="Filter files by name (partial match)")
    parser.add_argument("--mime-type", help="Filter by MIME type")
    args = parser.parse_args()

    folder_id = args.folder_id or get_root_folder_id()

    service = get_drive_service()
    files = list_files(service, folder_id, name_filter=args.name_filter, mime_type=args.mime_type)

    print(json.dumps(files, indent=2))

    if not files:
        print(f"No files found in folder {folder_id}", file=sys.stderr)
    else:
        print(f"Found {len(files)} file(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
