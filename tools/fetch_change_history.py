#!/usr/bin/env python3
"""Pull account change history from Google Ads API.

Auto-detects what changes were made in the account during a reporting period:
budget changes, bid strategy changes, keyword additions/removals, status changes, etc.

Usage:
    python tools/fetch_change_history.py --start-date 2026-02-01 --end-date 2026-02-28

Output:
    .tmp/change_history_{start}_{end}.json (raw data)
    .tmp/change_history_summary_{start}_{end}.md (human-readable summary)

Note: The Change Event API only returns the last 30 days of data.
"""

import argparse
import json
import os
import sys
from datetime import date, datetime

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.lib.google_ads_client import (
    get_customer_id,
    get_google_ads_client,
    is_test_mode,
    run_gaql_query,
)

SAMPLE_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", ".tmp", "sample_data", "change_history.json")

GAQL_QUERY = """
SELECT
    change_event.change_date_time,
    change_event.change_resource_type,
    change_event.change_resource_name,
    change_event.resource_change_operation,
    change_event.changed_fields,
    change_event.client_type,
    change_event.user_email,
    change_event.old_resource,
    change_event.new_resource
FROM change_event
WHERE change_event.change_date_time >= '{start_date}'
    AND change_event.change_date_time <= '{end_date} 23:59:59'
ORDER BY change_event.change_date_time DESC
LIMIT 10000
"""


def parse_change_rows(rows) -> list[dict]:
    """Convert API rows to flat dicts."""
    parsed = []
    for row in rows:
        event = row.change_event
        parsed.append({
            "date_time": str(event.change_date_time),
            "resource_type": event.change_resource_type.name,
            "resource_name": event.change_resource_name,
            "operation": event.resource_change_operation.name,
            "changed_fields": str(event.changed_fields) if event.changed_fields else "",
            "client_type": event.client_type.name,
            "user_email": event.user_email,
        })
    return parsed


def summarize_changes(changes: list[dict]) -> str:
    """Group changes by type and produce a human-readable markdown summary."""
    if not changes:
        return "No changes detected during this period.\n"

    # Group by resource type
    by_type = {}
    for change in changes:
        rtype = change["resource_type"]
        if rtype not in by_type:
            by_type[rtype] = []
        by_type[rtype].append(change)

    # Group by operation
    by_operation = {}
    for change in changes:
        op = change["operation"]
        if op not in by_operation:
            by_operation[op] = 0
        by_operation[op] += 1

    lines = [
        "# Account Change History Summary\n",
        f"**Total changes:** {len(changes)}\n",
        "## Changes by Operation\n",
    ]

    for op, count in sorted(by_operation.items()):
        lines.append(f"- {op}: {count}")

    lines.append("\n## Changes by Resource Type\n")

    type_labels = {
        "CAMPAIGN": "Campaign Changes",
        "AD_GROUP": "Ad Group Changes",
        "AD_GROUP_CRITERION": "Keyword/Targeting Changes",
        "AD_GROUP_AD": "Ad Changes",
        "CAMPAIGN_BUDGET": "Budget Changes",
        "CAMPAIGN_CRITERION": "Campaign Targeting Changes",
        "AD_GROUP_BID_MODIFIER": "Bid Modifier Changes",
    }

    for rtype, type_changes in sorted(by_type.items()):
        label = type_labels.get(rtype, rtype)
        lines.append(f"### {label} ({len(type_changes)})\n")

        for change in type_changes[:20]:  # Cap at 20 per type for readability
            date_str = change["date_time"][:10] if change["date_time"] else "unknown"
            op = change["operation"]
            user = change["user_email"] or "system"
            resource = change["resource_name"].split("/")[-1] if change["resource_name"] else "unknown"

            lines.append(f"- **{date_str}** [{op}] by {user}")
            if change["changed_fields"]:
                lines.append(f"  - Fields: {change['changed_fields']}")

        if len(type_changes) > 20:
            lines.append(f"- _...and {len(type_changes) - 20} more_")

        lines.append("")

    return "\n".join(lines)


def check_30_day_limit(start_date_str: str):
    """Warn if the start date is more than 30 days ago."""
    from datetime import timedelta

    start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    days_ago = (date.today() - start).days
    if days_ago > 30:
        cutoff = date.today() - timedelta(days=30)
        print(f"WARNING: Start date is {days_ago} days ago. The Change Event API only "
              f"returns the last 30 days of data. Changes before {cutoff} "
              f"will not appear.", file=sys.stderr)
        return True
    return False


def main():
    parser = argparse.ArgumentParser(description="Pull change history from Google Ads")
    parser.add_argument("--customer-id", help="Google Ads customer ID (defaults to env var)")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output-file", help="Output JSON path (auto-generated if omitted)")
    args = parser.parse_args()

    json_output = args.output_file or f".tmp/change_history_{args.start_date}_{args.end_date}.json"
    md_output = f".tmp/change_history_summary_{args.start_date}_{args.end_date}.md"

    if is_test_mode():
        print("[TEST MODE] Loading sample data instead of calling Google Ads API")
        if os.path.exists(SAMPLE_DATA_PATH):
            with open(SAMPLE_DATA_PATH) as f:
                changes = json.load(f)
            os.makedirs(os.path.dirname(json_output), exist_ok=True)
            with open(json_output, "w") as f:
                json.dump(changes, f, indent=2)
            summary = summarize_changes(changes)
            with open(md_output, "w") as f:
                f.write(summary)
            print(f"Loaded {len(changes)} changes from sample data")
            print(f"Raw data: {json_output}")
            print(f"Summary: {md_output}")
        else:
            print(f"No sample data found at {SAMPLE_DATA_PATH}")
            print("Run: python tools/generate_sample_data.py --client-name 'Test' --month 2026-02")
            sys.exit(1)
        return

    customer_id = get_customer_id(args.customer_id)
    client = get_google_ads_client()

    has_gap = check_30_day_limit(args.start_date)

    query = GAQL_QUERY.format(start_date=args.start_date, end_date=args.end_date)
    rows = run_gaql_query(client, customer_id, query)
    changes = parse_change_rows(rows)

    os.makedirs(os.path.dirname(json_output), exist_ok=True)

    with open(json_output, "w") as f:
        json.dump(changes, f, indent=2)

    summary = summarize_changes(changes)
    with open(md_output, "w") as f:
        f.write(summary)

    print(f"Change history ({args.start_date} to {args.end_date}): {len(changes)} changes")
    print(f"Raw data: {json_output}")
    print(f"Summary: {md_output}")

    if has_gap:
        print("NOTE: Some changes may be missing due to the 30-day API limit.", file=sys.stderr)

    if not changes:
        print("WARNING: No changes found. This could mean no changes were made, "
              "or the account is a test account.", file=sys.stderr)


if __name__ == "__main__":
    main()
