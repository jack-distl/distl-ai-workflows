#!/usr/bin/env python3
"""One-time setup: Authenticate with Google Drive API and save token.json.

Run this interactively once. It opens a browser for consent, then saves
token.json in the project root. Subsequent Drive tool runs will use this
cached token and auto-refresh it.

Prerequisites:
    - credentials.json in the project root (downloaded from Google Cloud Console)
    - Google Drive API enabled in your Cloud project
"""

import os
import sys

SCOPES = ["https://www.googleapis.com/auth/drive"]
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), "..")
CREDENTIALS_PATH = os.path.join(PROJECT_ROOT, "credentials.json")
TOKEN_PATH = os.path.join(PROJECT_ROOT, "token.json")


def main():
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"Error: {CREDENTIALS_PATH} not found.")
        print()
        print("To get this file:")
        print("1. Go to Google Cloud Console > APIs & Services > Credentials")
        print("2. Create an OAuth 2.0 Client ID (Desktop app type)")
        print("3. Download the JSON and save it as credentials.json in the project root")
        sys.exit(1)

    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        print("Error: Required packages not installed.")
        print("Run: pip install google-api-python-client google-auth-oauthlib")
        sys.exit(1)

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        if creds and creds.valid:
            print("token.json already exists and is valid.")
            print("Delete token.json and re-run this script to re-authenticate.")
            return

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    creds = flow.run_local_server(port=0)

    with open(TOKEN_PATH, "w") as f:
        f.write(creds.to_json())

    # Quick validation
    service = build("drive", "v3", credentials=creds)
    about = service.about().get(fields="user").execute()
    user_email = about.get("user", {}).get("emailAddress", "unknown")

    print()
    print("=" * 60)
    print(f"SUCCESS! Authenticated as: {user_email}")
    print(f"Token saved to: {TOKEN_PATH}")
    print()
    print("Your Google Drive tools are now ready to use.")
    print("=" * 60)


if __name__ == "__main__":
    main()
