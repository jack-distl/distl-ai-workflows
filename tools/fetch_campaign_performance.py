#!/usr/bin/env python3
"""Pull campaign-level performance data from Google Ads API.

Usage:
    python tools/fetch_campaign_performance.py --start-date 2026-02-01 --end-date 2026-02-28
    python tools/fetch_campaign_performance.py --start-date 2026-02-01 --end-date 2026-02-28 \
        --compare-from 2026-01-01 --compare-to 2026-01-31
    python tools/fetch_campaign_performance.py --customer-id 1234567890 --start-date 2026-02-01 --end-date 2026-02-28

Output: CSV files in .tmp/ with campaign metrics.
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

SAMPLE_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", ".tmp", "sample_data", "campaign_performance.csv")

GAQL_QUERY = """
SELECT
    campaign.id,
    campaign.name,
    campaign.status,
    campaign.advertising_channel_type,
    campaign.bidding_strategy_type,
    metrics.impressions,
    metrics.clicks,
    metrics.ctr,
    metrics.average_cpc,
    metrics.cost_micros,
    metrics.conversions,
    metrics.conversions_value,
    metrics.cost_per_conversion,
    metrics.search_impression_share,
    metrics.search_budget_lost_impression_share,
    metrics.search_rank_lost_impression_share
FROM campaign
WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
    AND campaign.status != 'REMOVED'
ORDER BY campaign.name
"""


def parse_campaign_rows(rows) -> list[dict]:
    """Convert Google Ads API rows to flat dicts with human-readable values."""
    parsed = []
    for row in rows:
        campaign = row.campaign
        metrics = row.metrics
        parsed.append({
            "campaign_id": campaign.id,
            "campaign_name": campaign.name,
            "status": campaign.status.name,
            "channel_type": campaign.advertising_channel_type.name,
            "bid_strategy": campaign.bidding_strategy_type.name,
            "impressions": metrics.impressions,
            "clicks": metrics.clicks,
            "ctr": round(metrics.ctr * 100, 2),
            "avg_cpc": round(metrics.average_cpc / 1_000_000, 2),
            "cost": round(metrics.cost_micros / 1_000_000, 2),
            "conversions": round(metrics.conversions, 1),
            "conversion_value": round(metrics.conversions_value, 2),
            "cpa": round(metrics.cost_per_conversion / 1_000_000, 2) if metrics.cost_per_conversion else 0,
            "search_impression_share": round(metrics.search_impression_share * 100, 1) if metrics.search_impression_share else None,
            "search_budget_lost_is": round(metrics.search_budget_lost_impression_share * 100, 1) if metrics.search_budget_lost_impression_share else None,
            "search_rank_lost_is": round(metrics.search_rank_lost_impression_share * 100, 1) if metrics.search_rank_lost_impression_share else None,
        })
    return parsed


def pull_period(client, customer_id: str, start_date: str, end_date: str, output_path: str):
    """Pull campaign performance for a single period and save to CSV."""
    query = GAQL_QUERY.format(start_date=start_date, end_date=end_date)
    rows = run_gaql_query(client, customer_id, query)
    data = parse_campaign_rows(rows)

    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Campaign performance ({start_date} to {end_date}): {len(data)} campaigns")
    print(f"Saved to: {output_path}")

    if not data:
        print("WARNING: No data returned. If using a test account, this is expected.", file=sys.stderr)

    return df


def main():
    parser = argparse.ArgumentParser(description="Pull campaign performance from Google Ads")
    parser.add_argument("--customer-id", help="Google Ads customer ID (defaults to env var)")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--compare-from", help="Comparison period start date")
    parser.add_argument("--compare-to", help="Comparison period end date")
    parser.add_argument("--output-file", help="Output CSV path (auto-generated if omitted)")
    args = parser.parse_args()

    if is_test_mode():
        print("[TEST MODE] Loading sample data instead of calling Google Ads API")
        if os.path.exists(SAMPLE_DATA_PATH):
            df = pd.read_csv(SAMPLE_DATA_PATH)
            output = args.output_file or f".tmp/campaign_performance_{args.start_date}_{args.end_date}.csv"
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

    output = args.output_file or f".tmp/campaign_performance_{args.start_date}_{args.end_date}.csv"
    pull_period(client, customer_id, args.start_date, args.end_date, output)

    if args.compare_from and args.compare_to:
        compare_output = f".tmp/campaign_performance_{args.compare_from}_{args.compare_to}.csv"
        pull_period(client, customer_id, args.compare_from, args.compare_to, compare_output)


if __name__ == "__main__":
    main()
