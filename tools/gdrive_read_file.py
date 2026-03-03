#!/usr/bin/env python3
"""Download a file from Google Drive.

Usage:
    python tools/gdrive_read_file.py --file-id FILE_ID --output-path .tmp/brief.md
    python tools/gdrive_read_file.py --file-name "brief.md" --folder-id FOLDER_ID

Output: File saved to the specified local path (defaults to .tmp/).
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.lib.gdrive_client import get_drive_service, find_file, download_file


def main():
    parser = argparse.ArgumentParser(description="Download a file from Google Drive")
    parser.add_argument("--file-id", help="Direct Drive file ID")
    parser.add_argument("--file-name", help="File name to search for (use with --folder-id)")
    parser.add_argument("--folder-id", help="Folder to search in (used with --file-name)")
    parser.add_argument("--output-path", default=".tmp/downloaded_file", help="Local path to save file")
    args = parser.parse_args()

    if not args.file_id and not (args.file_name and args.folder_id):
        print("Error: Provide --file-id OR both --file-name and --folder-id")
        sys.exit(1)

    service = get_drive_service()

    file_id = args.file_id
    if not file_id:
        result = find_file(service, args.file_name, args.folder_id)
        if not result:
            print(f"Error: File '{args.file_name}' not found in folder {args.folder_id}")
            sys.exit(1)
        file_id = result["id"]
        print(f"Found file: {result['name']} (ID: {file_id})", file=sys.stderr)

    local_path = download_file(service, file_id, args.output_path)
    print(f"Downloaded to: {local_path}")


if __name__ == "__main__":
    main()
