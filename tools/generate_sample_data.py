#!/usr/bin/env python3
"""Generate realistic sample data for testing the full reporting pipeline.

Creates sample CSVs and JSON that mimic what the Google Ads API would return,
so the entire workflow can be exercised with TEST_MODE=true.

Usage:
    python tools/generate_sample_data.py --client-name "Acme Corp" --month 2026-02
"""

import argparse
import json
import os
import random
import sys

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.lib.date_utils import get_reporting_period

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", ".tmp", "sample_data")


def generate_campaign_performance(client_name: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Generate sample campaign performance data."""
    campaigns = [
        {"name": f"{client_name} - Brand", "channel": "SEARCH", "bid_strategy": "TARGET_CPA"},
        {"name": f"{client_name} - Non-Brand", "channel": "SEARCH", "bid_strategy": "MAXIMIZE_CONVERSIONS"},
        {"name": f"{client_name} - Competitor", "channel": "SEARCH", "bid_strategy": "MANUAL_CPC"},
        {"name": f"{client_name} - Display Remarketing", "channel": "DISPLAY", "bid_strategy": "TARGET_CPA"},
        {"name": f"{client_name} - PMax", "channel": "PERFORMANCE_MAX", "bid_strategy": "MAXIMIZE_CONVERSION_VALUE"},
    ]

    rows = []
    for i, camp in enumerate(campaigns):
        impressions = random.randint(5000, 50000)
        clicks = int(impressions * random.uniform(0.02, 0.12))
        cost = round(clicks * random.uniform(1.50, 8.00), 2)
        conversions = round(clicks * random.uniform(0.02, 0.15), 1)
        conv_value = round(conversions * random.uniform(50, 200), 2)

        rows.append({
            "campaign_id": 10000 + i,
            "campaign_name": camp["name"],
            "status": "ENABLED",
            "channel_type": camp["channel"],
            "bid_strategy": camp["bid_strategy"],
            "impressions": impressions,
            "clicks": clicks,
            "ctr": round((clicks / impressions) * 100, 2) if impressions > 0 else 0,
            "avg_cpc": round(cost / clicks, 2) if clicks > 0 else 0,
            "cost": cost,
            "conversions": conversions,
            "conversion_value": conv_value,
            "cpa": round(cost / conversions, 2) if conversions > 0 else 0,
            "search_impression_share": round(random.uniform(30, 85), 1) if camp["channel"] == "SEARCH" else None,
            "search_budget_lost_is": round(random.uniform(5, 30), 1) if camp["channel"] == "SEARCH" else None,
            "search_rank_lost_is": round(random.uniform(5, 25), 1) if camp["channel"] == "SEARCH" else None,
        })

    return pd.DataFrame(rows)


def generate_search_terms(client_name: str) -> pd.DataFrame:
    """Generate sample search terms data."""
    terms = [
        # High-intent converters
        {"term": f"{client_name.lower()} services", "campaign": f"{client_name} - Brand", "type": "brand"},
        {"term": f"{client_name.lower()} pricing", "campaign": f"{client_name} - Brand", "type": "brand"},
        {"term": "best service provider near me", "campaign": f"{client_name} - Non-Brand", "type": "generic"},
        {"term": "affordable consulting services", "campaign": f"{client_name} - Non-Brand", "type": "generic"},
        {"term": "professional services quote", "campaign": f"{client_name} - Non-Brand", "type": "generic"},
        # Irrelevant / negative candidates
        {"term": "free service template", "campaign": f"{client_name} - Non-Brand", "type": "irrelevant"},
        {"term": "service provider jobs hiring", "campaign": f"{client_name} - Non-Brand", "type": "irrelevant"},
        {"term": "diy service guide", "campaign": f"{client_name} - Non-Brand", "type": "irrelevant"},
        # Competitor terms
        {"term": "competitor company reviews", "campaign": f"{client_name} - Competitor", "type": "competitor"},
        {"term": "competitor vs alternatives", "campaign": f"{client_name} - Competitor", "type": "competitor"},
        # More generic
        {"term": "top rated service company", "campaign": f"{client_name} - Non-Brand", "type": "generic"},
        {"term": "service provider cost", "campaign": f"{client_name} - Non-Brand", "type": "generic"},
        {"term": "emergency service help", "campaign": f"{client_name} - Non-Brand", "type": "generic"},
        {"term": "local service experts", "campaign": f"{client_name} - Non-Brand", "type": "generic"},
        {"term": "service consultation booking", "campaign": f"{client_name} - Non-Brand", "type": "generic"},
    ]

    rows = []
    for term_data in terms:
        impressions = random.randint(50, 5000)
        clicks = int(impressions * random.uniform(0.02, 0.15))
        cost = round(clicks * random.uniform(2.00, 10.00), 2)

        # Irrelevant terms get no conversions
        if term_data["type"] == "irrelevant":
            conversions = 0
        else:
            conversions = round(clicks * random.uniform(0.0, 0.12), 1)

        rows.append({
            "search_term": term_data["term"],
            "status": "NONE",
            "campaign": term_data["campaign"],
            "ad_group": f"{term_data['campaign']} - Main",
            "impressions": impressions,
            "clicks": clicks,
            "ctr": round((clicks / impressions) * 100, 2) if impressions > 0 else 0,
            "avg_cpc": round(cost / clicks, 2) if clicks > 0 else 0,
            "cost": cost,
            "conversions": conversions,
            "cpa": round(cost / conversions, 2) if conversions > 0 else None,
        })

    return pd.DataFrame(rows)


def generate_keyword_performance(client_name: str) -> pd.DataFrame:
    """Generate sample keyword performance data."""
    keywords = [
        {"keyword": f"{client_name.lower()}", "match": "EXACT", "campaign": f"{client_name} - Brand", "qs": 9},
        {"keyword": f"{client_name.lower()} services", "match": "PHRASE", "campaign": f"{client_name} - Brand", "qs": 8},
        {"keyword": "service provider", "match": "BROAD", "campaign": f"{client_name} - Non-Brand", "qs": 6},
        {"keyword": "professional consulting", "match": "PHRASE", "campaign": f"{client_name} - Non-Brand", "qs": 5},
        {"keyword": "service quote", "match": "EXACT", "campaign": f"{client_name} - Non-Brand", "qs": 7},
        {"keyword": "best service company", "match": "BROAD", "campaign": f"{client_name} - Non-Brand", "qs": 4},
        {"keyword": "affordable services near me", "match": "PHRASE", "campaign": f"{client_name} - Non-Brand", "qs": 6},
        {"keyword": "competitor name", "match": "EXACT", "campaign": f"{client_name} - Competitor", "qs": 3},
        {"keyword": "competitor alternative", "match": "BROAD", "campaign": f"{client_name} - Competitor", "qs": 4},
    ]

    rows = []
    for kw in keywords:
        impressions = random.randint(200, 15000)
        clicks = int(impressions * random.uniform(0.03, 0.12))
        cost = round(clicks * random.uniform(1.50, 9.00), 2)
        conversions = round(clicks * random.uniform(0.02, 0.10), 1)

        rows.append({
            "campaign": kw["campaign"],
            "ad_group": f"{kw['campaign']} - Main",
            "keyword": kw["keyword"],
            "match_type": kw["match"],
            "status": "ENABLED",
            "quality_score": kw["qs"],
            "impressions": impressions,
            "clicks": clicks,
            "ctr": round((clicks / impressions) * 100, 2) if impressions > 0 else 0,
            "avg_cpc": round(cost / clicks, 2) if clicks > 0 else 0,
            "cost": cost,
            "conversions": conversions,
            "cpa": round(cost / conversions, 2) if conversions > 0 else None,
            "search_impression_share": round(random.uniform(25, 80), 1),
        })

    return pd.DataFrame(rows)


def generate_change_history(client_name: str, month: str) -> list[dict]:
    """Generate sample change history data."""
    start, end = get_reporting_period(month)

    changes = [
        {
            "date_time": f"{start.isoformat()} 09:15:00",
            "resource_type": "CAMPAIGN_BUDGET",
            "resource_name": f"customers/1234567890/campaignBudgets/100",
            "operation": "UPDATE",
            "changed_fields": "amount_micros",
            "client_type": "GOOGLE_ADS_WEB_CLIENT",
            "user_email": "specialist@agency.com",
        },
        {
            "date_time": f"{start.replace(day=5).isoformat()} 14:30:00",
            "resource_type": "AD_GROUP_CRITERION",
            "resource_name": f"customers/1234567890/adGroupCriteria/200~300",
            "operation": "CREATE",
            "changed_fields": "",
            "client_type": "GOOGLE_ADS_WEB_CLIENT",
            "user_email": "specialist@agency.com",
        },
        {
            "date_time": f"{start.replace(day=8).isoformat()} 10:00:00",
            "resource_type": "AD_GROUP_CRITERION",
            "resource_name": f"customers/1234567890/adGroupCriteria/200~301",
            "operation": "CREATE",
            "changed_fields": "",
            "client_type": "GOOGLE_ADS_WEB_CLIENT",
            "user_email": "specialist@agency.com",
        },
        {
            "date_time": f"{start.replace(day=10).isoformat()} 11:45:00",
            "resource_type": "CAMPAIGN",
            "resource_name": f"customers/1234567890/campaigns/10002",
            "operation": "UPDATE",
            "changed_fields": "status",
            "client_type": "GOOGLE_ADS_WEB_CLIENT",
            "user_email": "specialist@agency.com",
        },
        {
            "date_time": f"{start.replace(day=15).isoformat()} 16:20:00",
            "resource_type": "AD_GROUP_AD",
            "resource_name": f"customers/1234567890/adGroupAds/200~400",
            "operation": "CREATE",
            "changed_fields": "",
            "client_type": "GOOGLE_ADS_WEB_CLIENT",
            "user_email": "specialist@agency.com",
        },
        {
            "date_time": f"{start.replace(day=18).isoformat()} 09:00:00",
            "resource_type": "CAMPAIGN",
            "resource_name": f"customers/1234567890/campaigns/10001",
            "operation": "UPDATE",
            "changed_fields": "bidding_strategy_type",
            "client_type": "GOOGLE_ADS_WEB_CLIENT",
            "user_email": "specialist@agency.com",
        },
    ]

    return changes


def main():
    parser = argparse.ArgumentParser(description="Generate sample data for testing")
    parser.add_argument("--client-name", required=True, help="Client name for sample data")
    parser.add_argument("--month", required=True, help="Month to generate data for (YYYY-MM)")
    args = parser.parse_args()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    random.seed(42)  # Reproducible data

    start, end = get_reporting_period(args.month)
    start_str = start.isoformat()
    end_str = end.isoformat()

    # Campaign performance
    df_campaigns = generate_campaign_performance(args.client_name, start_str, end_str)
    df_campaigns.to_csv(os.path.join(OUTPUT_DIR, "campaign_performance.csv"), index=False)
    print(f"Generated {len(df_campaigns)} campaigns → campaign_performance.csv")

    # Search terms
    df_search = generate_search_terms(args.client_name)
    df_search.to_csv(os.path.join(OUTPUT_DIR, "search_terms.csv"), index=False)
    print(f"Generated {len(df_search)} search terms → search_terms.csv")

    # Keyword performance
    df_keywords = generate_keyword_performance(args.client_name)
    df_keywords.to_csv(os.path.join(OUTPUT_DIR, "keyword_performance.csv"), index=False)
    print(f"Generated {len(df_keywords)} keywords → keyword_performance.csv")

    # Change history
    changes = generate_change_history(args.client_name, args.month)
    with open(os.path.join(OUTPUT_DIR, "change_history.json"), "w") as f:
        json.dump(changes, f, indent=2)
    print(f"Generated {len(changes)} changes → change_history.json")

    print(f"\nAll sample data saved to {OUTPUT_DIR}/")
    print("Set TEST_MODE=true in .env to use this data with the fetch tools.")


if __name__ == "__main__":
    main()
