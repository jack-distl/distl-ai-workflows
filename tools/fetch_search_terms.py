#!/usr/bin/env python3
"""Pull search terms report from Google Ads API.

Usage:
    python tools/fetch_search_terms.py --start-date 2026-02-01 --end-date 2026-02-28
    python tools/fetch_search_terms.py --customer-id 1234567890 --start-date 2026-02-01 --end-date 2026-02-28

Output: CSV file in .tmp/ with search term metrics + coverage % summary.
"""

import argparse
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.lib.google_ads_client import (
    get_customer_id,
    get_google_ads_client,
    is_test_mode,
    run_gaql_query,
)

SAMPLE_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", ".tmp", "sample_data", "search_terms.csv")

SEARCH_TERMS_QUERY = """
SELECT
    search_term_view.search_term,
    search_term_view.status,
    campaign.name,
    ad_group.name,
    metrics.impressions,
    metrics.clicks,
    metrics.ctr,
    metrics.average_cpc,
    metrics.cost_micros,
    metrics.conversions
FROM search_term_view
WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
    AND metrics.impressions > 0
ORDER BY metrics.impressions DESC
LIMIT 10000
"""

# Separate query to get total campaign impressions for coverage calculation
CAMPAIGN_IMPRESSIONS_QUERY = """
SELECT
    metrics.impressions
FROM campaign
WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
    AND campaign.status != 'REMOVED'
"""


def parse_search_term_rows(rows) -> list[dict]:
    """Convert API rows to flat dicts."""
    parsed = []
    for row in rows:
        metrics = row.metrics
        parsed.append({
            "search_term": row.search_term_view.search_term,
            "status": row.search_term_view.status.name,
            "campaign": row.campaign.name,
            "ad_group": row.ad_group.name,
            "impressions": metrics.impressions,
            "clicks": metrics.clicks,
            "ctr": round(metrics.ctr * 100, 2),
            "avg_cpc": round(metrics.average_cpc / 1_000_000, 2),
            "cost": round(metrics.cost_micros / 1_000_000, 2),
            "conversions": round(metrics.conversions, 1),
            "cpa": round((metrics.cost_micros / 1_000_000) / metrics.conversions, 2) if metrics.conversions > 0 else None,
        })
    return parsed


def calculate_coverage(client, customer_id: str, start_date: str, end_date: str, search_term_impressions: int) -> float:
    """Calculate what % of total campaign impressions are visible in search terms."""
    query = CAMPAIGN_IMPRESSIONS_QUERY.format(start_date=start_date, end_date=end_date)
    rows = run_gaql_query(client, customer_id, query)
    total_campaign_impressions = sum(row.metrics.impressions for row in rows)

    if total_campaign_impressions == 0:
        return 0.0
    return round((search_term_impressions / total_campaign_impressions) * 100, 1)


def main():
    parser = argparse.ArgumentParser(description="Pull search terms from Google Ads")
    parser.add_argument("--customer-id", help="Google Ads customer ID (defaults to env var)")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output-file", help="Output CSV path (auto-generated if omitted)")
    args = parser.parse_args()

    output = args.output_file or f".tmp/search_terms_{args.start_date}_{args.end_date}.csv"

    if is_test_mode():
        print("[TEST MODE] Loading sample data instead of calling Google Ads API")
        if os.path.exists(SAMPLE_DATA_PATH):
            df = pd.read_csv(SAMPLE_DATA_PATH)
            os.makedirs(os.path.dirname(output), exist_ok=True)
            df.to_csv(output, index=False)
            print(f"Loaded {len(df)} rows from sample data → {output}")
            print(f"Search term coverage: N/A (test mode)")
        else:
            print(f"No sample data found at {SAMPLE_DATA_PATH}")
            print("Run: python tools/generate_sample_data.py --client-name 'Test' --month 2026-02")
            sys.exit(1)
        return

    customer_id = get_customer_id(args.customer_id)
    client = get_google_ads_client()

    query = SEARCH_TERMS_QUERY.format(start_date=args.start_date, end_date=args.end_date)
    rows = run_gaql_query(client, customer_id, query)
    data = parse_search_term_rows(rows)

    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    df.to_csv(output, index=False)

    total_st_impressions = df["impressions"].sum() if not df.empty else 0
    coverage = calculate_coverage(client, customer_id, args.start_date, args.end_date, total_st_impressions)

    print(f"Search terms ({args.start_date} to {args.end_date}): {len(data)} terms")
    print(f"Saved to: {output}")
    print(f"Search term coverage: {coverage}% of campaign impressions visible")

    if coverage < 60:
        print(f"WARNING: Only {coverage}% of impressions have visible search terms. "
              "Google is suppressing significant data for privacy.", file=sys.stderr)

    if not data:
        print("WARNING: No search term data returned. If using a test account, this is expected.", file=sys.stderr)


if __name__ == "__main__":
    main()
