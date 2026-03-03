#!/usr/bin/env python3
"""One-time setup: Generate a Google Ads API refresh token via OAuth2 flow.

Run this interactively once. It opens a browser for consent, then prints the
refresh token. Paste the token into your .env file as GOOGLE_ADS_REFRESH_TOKEN.

Prerequisites:
    - GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET set in .env
    - These come from a Google Cloud project with the Google Ads API enabled
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()


def main():
    client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Error: GOOGLE_ADS_CLIENT_ID and GOOGLE_ADS_CLIENT_SECRET must be set in .env")
        print()
        print("To get these:")
        print("1. Go to Google Cloud Console > APIs & Services > Credentials")
        print("2. Create an OAuth 2.0 Client ID (Desktop app type)")
        print("3. Copy the client ID and secret into .env")
        sys.exit(1)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Error: google-auth-oauthlib not installed.")
        print("Run: pip install google-auth-oauthlib")
        sys.exit(1)

    SCOPES = ["https://www.googleapis.com/auth/adwords"]

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=SCOPES)
    creds = flow.run_local_server(port=0)

    print()
    print("=" * 60)
    print("SUCCESS! Your refresh token:")
    print()
    print(creds.refresh_token)
    print()
    print("Add this to your .env file as:")
    print(f"GOOGLE_ADS_REFRESH_TOKEN={creds.refresh_token}")
    print("=" * 60)


if __name__ == "__main__":
    main()
