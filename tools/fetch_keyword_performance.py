#!/usr/bin/env python3
"""Pull keyword-level performance data including quality score from Google Ads API.

Usage:
    python tools/fetch_keyword_performance.py --start-date 2026-02-01 --end-date 2026-02-28

Output: CSV file in .tmp/ with keyword metrics.
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

SAMPLE_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", ".tmp", "sample_data", "keyword_performance.csv")

GAQL_QUERY = """
SELECT
    campaign.name,
    ad_group.name,
    ad_group_criterion.keyword.text,
    ad_group_criterion.keyword.match_type,
    ad_group_criterion.status,
    ad_group_criterion.quality_info.quality_score,
    metrics.impressions,
    metrics.clicks,
    metrics.ctr,
    metrics.average_cpc,
    metrics.cost_micros,
    metrics.conversions,
    metrics.search_impression_share
FROM keyword_view
WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
    AND campaign.status != 'REMOVED'
    AND ad_group.status != 'REMOVED'
    AND ad_group_criterion.status != 'REMOVED'
ORDER BY metrics.cost_micros DESC
"""


def parse_keyword_rows(rows) -> list[dict]:
    """Convert API rows to flat dicts."""
    parsed = []
    for row in rows:
        metrics = row.metrics
        criterion = row.ad_group_criterion
        parsed.append({
            "campaign": row.campaign.name,
            "ad_group": row.ad_group.name,
            "keyword": criterion.keyword.text,
            "match_type": criterion.keyword.match_type.name,
            "status": criterion.status.name,
            "quality_score": criterion.quality_info.quality_score if criterion.quality_info.quality_score else None,
            "impressions": metrics.impressions,
            "clicks": metrics.clicks,
            "ctr": round(metrics.ctr * 100, 2),
            "avg_cpc": round(metrics.average_cpc / 1_000_000, 2),
            "cost": round(metrics.cost_micros / 1_000_000, 2),
            "conversions": round(metrics.conversions, 1),
            "cpa": round((metrics.cost_micros / 1_000_000) / metrics.conversions, 2) if metrics.conversions > 0 else None,
            "search_impression_share": round(metrics.search_impression_share * 100, 1) if metrics.search_impression_share else None,
        })
    return parsed


def main():
    parser = argparse.ArgumentParser(description="Pull keyword performance from Google Ads")
    parser.add_argument("--customer-id", help="Google Ads customer ID (defaults to env var)")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output-file", help="Output CSV path (auto-generated if omitted)")
    args = parser.parse_args()

    output = args.output_file or f".tmp/keyword_performance_{args.start_date}_{args.end_date}.csv"

    if is_test_mode():
        print("[TEST MODE] Loading sample data instead of calling Google Ads API")
        if os.path.exists(SAMPLE_DATA_PATH):
            df = pd.read_csv(SAMPLE_DATA_PATH)
            os.makedirs(os.path.dirname(output), exist_ok=True)
            df.to_csv(output, index=False)
            print(f"Loaded {len(df)} rows from sample data → {output}")
        else:
            print(f"No sample data found at {SAMPLE_DATA_PATH}")
            print("Run: python tools/generate_sample_data.py --client-name 'Test' --month 2026-02")
            sys.exit(1)
        return

    customer_id = get_customer_id(args.customer_id)
    client = get_google_ads_client()

    query = GAQL_QUERY.format(start_date=args.start_date, end_date=args.end_date)
    rows = run_gaql_query(client, customer_id, query)
    data = parse_keyword_rows(rows)

    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    df.to_csv(output, index=False)

    print(f"Keyword performance ({args.start_date} to {args.end_date}): {len(data)} keywords")
    print(f"Saved to: {output}")

    if not data:
        print("WARNING: No keyword data returned. If using a test account, this is expected.", file=sys.stderr)


if __name__ == "__main__":
    main()
