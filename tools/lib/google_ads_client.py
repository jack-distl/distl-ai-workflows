"""Shared Google Ads API authentication and query helpers."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()


def is_test_mode() -> bool:
    """Check if we're running in test mode (sample data instead of live API)."""
    return os.getenv("TEST_MODE", "true").lower() == "true"


def get_google_ads_client():
    """Build and return an authenticated GoogleAdsClient from .env values.

    Required env vars:
        GOOGLE_ADS_DEVELOPER_TOKEN
        GOOGLE_ADS_CLIENT_ID
        GOOGLE_ADS_CLIENT_SECRET
        GOOGLE_ADS_REFRESH_TOKEN
        GOOGLE_ADS_LOGIN_CUSTOMER_ID
    """
    try:
        from google.ads.googleads.client import GoogleAdsClient
    except ImportError:
        print("Error: google-ads package not installed. Run: pip install google-ads>=29.0.0")
        sys.exit(1)

    required_vars = [
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
    ]

    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        print(f"Error: Missing required env vars: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in your Google Ads API credentials.")
        sys.exit(1)

    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        "use_proto_plus": True,
    }

    return GoogleAdsClient.load_from_dict(config)


def get_customer_id(cli_customer_id: str | None = None) -> str:
    """Get the customer ID from CLI arg or env var. Returns ID without dashes."""
    customer_id = cli_customer_id or os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")
    if not customer_id:
        print("Error: No customer ID provided. Use --customer-id or set GOOGLE_ADS_LOGIN_CUSTOMER_ID in .env")
        sys.exit(1)
    return customer_id.replace("-", "")


def run_gaql_query(client, customer_id: str, query: str) -> list:
    """Execute a GAQL query via SearchStream and return all rows.

    Uses streaming for memory efficiency on large accounts.
    """
    ga_service = client.get_service("GoogleAdsService")
    rows = []
    stream = ga_service.search_stream(customer_id=customer_id, query=query)
    for batch in stream:
        for row in batch.results:
            rows.append(row)
    return rows
