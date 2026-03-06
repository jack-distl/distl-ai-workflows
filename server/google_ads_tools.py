"""Google Ads MCP tools for pulling reporting data.

All credentials are server-side. All cost_micros conversions, enum-to-string
mappings, and summary calculations happen here so Claude gets clean,
human-readable data.
"""

import logging
import os
from datetime import date, datetime, timedelta

from app import mcp
from security import log_tool_call, validate_customer_id, validate_date

logger = logging.getLogger(__name__)

# --- GAQL Queries ---

CAMPAIGN_PERFORMANCE_QUERY = """
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

CAMPAIGN_IMPRESSIONS_QUERY = """
SELECT
    metrics.impressions
FROM campaign
WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
    AND campaign.status != 'REMOVED'
"""

KEYWORD_PERFORMANCE_QUERY = """
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

CHANGE_HISTORY_QUERY = """
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

ACCESSIBLE_CUSTOMERS_QUERY = """
SELECT
    customer_client.id,
    customer_client.descriptive_name,
    customer_client.status,
    customer_client.manager
FROM customer_client
WHERE customer_client.status = 'ENABLED'
ORDER BY customer_client.descriptive_name
"""


# --- Internal helpers ---


def _get_google_ads_client():
    """Build an authenticated GoogleAdsClient from server-side env vars."""
    from google.ads.googleads.client import GoogleAdsClient

    required = [
        "GOOGLE_ADS_DEVELOPER_TOKEN",
        "GOOGLE_ADS_CLIENT_ID",
        "GOOGLE_ADS_CLIENT_SECRET",
        "GOOGLE_ADS_REFRESH_TOKEN",
        "GOOGLE_ADS_LOGIN_CUSTOMER_ID",
    ]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        raise RuntimeError(f"Missing Google Ads env vars: {', '.join(missing)}")

    config = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID"),
        "use_proto_plus": True,
    }
    return GoogleAdsClient.load_from_dict(config)


def _run_gaql(client, customer_id: str, query: str) -> list:
    """Execute a GAQL query via SearchStream and return all rows."""
    service = client.get_service("GoogleAdsService")
    rows = []
    stream = service.search_stream(customer_id=customer_id, query=query)
    for batch in stream:
        for row in batch.results:
            rows.append(row)
    return rows


def _fmt_currency(micros: int | float) -> str:
    return f"${micros / 1_000_000:,.2f}"


def _fmt_pct(value: float, decimals: int = 1) -> str:
    return f"{value * 100:.{decimals}f}%"


def _safe_pct(value, decimals: int = 1) -> str | None:
    if value:
        return f"{value * 100:.{decimals}f}%"
    return None


# --- MCP Tools ---


@mcp.tool()
async def google_ads_list_accounts() -> str:
    """List all accessible Google Ads accounts under the MCC (Manager account).

    Returns account IDs, names, and whether each is a manager account.
    No inputs required — uses server-side MCC credentials.
    """
    log_tool_call("google_ads_list_accounts")
    try:
        client = _get_google_ads_client()
        login_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "").replace("-", "")
        rows = _run_gaql(client, login_id, ACCESSIBLE_CUSTOMERS_QUERY)

        if not rows:
            return "No accessible accounts found under this MCC."

        lines = ["# Accessible Google Ads Accounts\n"]
        lines.append("| Account ID | Name | Type | Status |")
        lines.append("|-----------|------|------|--------|")
        for row in rows:
            cc = row.customer_client
            acct_type = "Manager" if cc.manager else "Client"
            lines.append(
                f"| {cc.id} | {cc.descriptive_name} | {acct_type} | {cc.status.name} |"
            )

        return "\n".join(lines)

    except Exception as e:
        logger.exception("google_ads_list_accounts failed")
        return "Error listing accounts. Check server logs for details."


@mcp.tool()
async def google_ads_campaign_performance(
    customer_id: str,
    start_date: str,
    end_date: str,
) -> str:
    """Pull campaign-level performance metrics from Google Ads.

    Returns a formatted table with impressions, clicks, CTR, CPC, cost,
    conversions, CPA, conversion value, and impression share data for
    each active campaign.

    Args:
        customer_id: Google Ads account ID (with or without dashes)
        start_date: Start of reporting period (YYYY-MM-DD)
        end_date: End of reporting period (YYYY-MM-DD)
    """
    try:
        cid = validate_customer_id(customer_id)
        start_date = validate_date(start_date, "start_date")
        end_date = validate_date(end_date, "end_date")
    except ValueError as e:
        return str(e)

    log_tool_call("google_ads_campaign_performance", customer_id=cid, start_date=start_date, end_date=end_date)

    try:
        client = _get_google_ads_client()
        query = CAMPAIGN_PERFORMANCE_QUERY.format(
            start_date=start_date, end_date=end_date
        )
        rows = _run_gaql(client, cid, query)

        if not rows:
            return (
                f"No campaign data returned for account {customer_id} "
                f"({start_date} to {end_date}). "
                "This could mean no active campaigns or a test account."
            )

        lines = [
            f"# Campaign Performance: {start_date} to {end_date}\n",
            f"Account: {customer_id}\n",
        ]

        # Summary totals
        total_impressions = sum(r.metrics.impressions for r in rows)
        total_clicks = sum(r.metrics.clicks for r in rows)
        total_cost = sum(r.metrics.cost_micros for r in rows)
        total_conversions = sum(r.metrics.conversions for r in rows)
        total_value = sum(r.metrics.conversions_value for r in rows)

        lines.append("## Account Totals")
        lines.append(f"- Impressions: {total_impressions:,}")
        lines.append(f"- Clicks: {total_clicks:,}")
        lines.append(
            f"- CTR: {total_clicks / total_impressions * 100:.2f}%"
            if total_impressions
            else "- CTR: N/A"
        )
        lines.append(f"- Cost: {_fmt_currency(total_cost)}")
        lines.append(f"- Conversions: {total_conversions:.1f}")
        lines.append(
            f"- CPA: {_fmt_currency(total_cost / total_conversions)}"
            if total_conversions
            else "- CPA: N/A (no conversions)"
        )
        lines.append(f"- Conversion Value: ${total_value:,.2f}")
        lines.append("")

        # Per-campaign detail
        lines.append("## By Campaign\n")
        for row in rows:
            c = row.campaign
            m = row.metrics

            lines.append(f"### {c.name}")
            lines.append(f"- Status: {c.status.name}")
            lines.append(f"- Channel: {c.advertising_channel_type.name}")
            lines.append(f"- Bid Strategy: {c.bidding_strategy_type.name}")
            lines.append(f"- Impressions: {m.impressions:,}")
            lines.append(f"- Clicks: {m.clicks:,}")
            lines.append(f"- CTR: {_fmt_pct(m.ctr, 2)}")
            lines.append(f"- Avg CPC: {_fmt_currency(m.average_cpc)}")
            lines.append(f"- Cost: {_fmt_currency(m.cost_micros)}")
            lines.append(f"- Conversions: {m.conversions:.1f}")
            if m.conversions > 0:
                lines.append(f"- CPA: {_fmt_currency(m.cost_per_conversion)}")
            else:
                lines.append("- CPA: N/A (no conversions)")
            lines.append(f"- Conversion Value: ${m.conversions_value:,.2f}")

            sis = _safe_pct(m.search_impression_share)
            if sis:
                lines.append(f"- Search Impression Share: {sis}")
            blis = _safe_pct(m.search_budget_lost_impression_share)
            if blis:
                lines.append(f"- Lost to Budget: {blis}")
            rlis = _safe_pct(m.search_rank_lost_impression_share)
            if rlis:
                lines.append(f"- Lost to Rank: {rlis}")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        logger.exception("google_ads_campaign_performance failed")
        return "Error pulling campaign performance. Check server logs for details."


@mcp.tool()
async def google_ads_search_terms(
    customer_id: str,
    start_date: str,
    end_date: str,
) -> str:
    """Pull search terms report from Google Ads with coverage calculation.

    Returns search terms that triggered ads, their metrics, and the percentage
    of total campaign impressions that are visible as search terms (coverage %).
    Low coverage means Google is suppressing data for privacy.

    Args:
        customer_id: Google Ads account ID (with or without dashes)
        start_date: Start of reporting period (YYYY-MM-DD)
        end_date: End of reporting period (YYYY-MM-DD)
    """
    try:
        cid = validate_customer_id(customer_id)
        start_date = validate_date(start_date, "start_date")
        end_date = validate_date(end_date, "end_date")
    except ValueError as e:
        return str(e)

    log_tool_call("google_ads_search_terms", customer_id=cid, start_date=start_date, end_date=end_date)

    try:
        client = _get_google_ads_client()

        # Pull search terms
        query = SEARCH_TERMS_QUERY.format(
            start_date=start_date, end_date=end_date
        )
        rows = _run_gaql(client, cid, query)

        # Pull total campaign impressions for coverage calculation
        camp_query = CAMPAIGN_IMPRESSIONS_QUERY.format(
            start_date=start_date, end_date=end_date
        )
        camp_rows = _run_gaql(client, cid, camp_query)
        total_campaign_impressions = sum(
            r.metrics.impressions for r in camp_rows
        )

        if not rows:
            return (
                f"No search term data for account {customer_id} "
                f"({start_date} to {end_date}). "
                "This could mean no Search campaigns or a test account."
            )

        # Calculate coverage
        total_st_impressions = sum(r.metrics.impressions for r in rows)
        coverage = (
            round(total_st_impressions / total_campaign_impressions * 100, 1)
            if total_campaign_impressions
            else 0
        )

        lines = [
            f"# Search Terms Report: {start_date} to {end_date}\n",
            f"Account: {customer_id}",
            f"Total search terms: {len(rows)}",
            f"Search term coverage: {coverage}% of campaign impressions visible",
        ]

        if coverage < 60:
            lines.append(
                f"WARNING: Only {coverage}% coverage — Google is suppressing "
                "significant search term data for privacy."
            )
        lines.append("")

        # Group by campaign for readability
        by_campaign: dict[str, list] = {}
        for row in rows:
            cname = row.campaign.name
            if cname not in by_campaign:
                by_campaign[cname] = []
            by_campaign[cname].append(row)

        for campaign_name, campaign_rows in by_campaign.items():
            lines.append(f"## {campaign_name}\n")
            lines.append(
                "| Search Term | Status | Impressions | Clicks | CTR | CPC | Cost | Conversions | CPA |"
            )
            lines.append(
                "|-------------|--------|------------|--------|-----|-----|------|-------------|-----|"
            )
            for row in campaign_rows:
                m = row.metrics
                cpa = (
                    _fmt_currency(m.cost_micros / m.conversions)
                    if m.conversions > 0
                    else "—"
                )
                lines.append(
                    f"| {row.search_term_view.search_term} "
                    f"| {row.search_term_view.status.name} "
                    f"| {m.impressions:,} "
                    f"| {m.clicks:,} "
                    f"| {_fmt_pct(m.ctr, 2)} "
                    f"| {_fmt_currency(m.average_cpc)} "
                    f"| {_fmt_currency(m.cost_micros)} "
                    f"| {m.conversions:.1f} "
                    f"| {cpa} |"
                )
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        logger.exception("google_ads_search_terms failed")
        return "Error pulling search terms. Check server logs for details."


@mcp.tool()
async def google_ads_keyword_performance(
    customer_id: str,
    start_date: str,
    end_date: str,
) -> str:
    """Pull keyword-level performance including quality scores from Google Ads.

    Returns metrics for each keyword including quality score, impression share,
    and cost data. Sorted by cost (highest first).

    Args:
        customer_id: Google Ads account ID (with or without dashes)
        start_date: Start of reporting period (YYYY-MM-DD)
        end_date: End of reporting period (YYYY-MM-DD)
    """
    try:
        cid = validate_customer_id(customer_id)
        start_date = validate_date(start_date, "start_date")
        end_date = validate_date(end_date, "end_date")
    except ValueError as e:
        return str(e)

    log_tool_call("google_ads_keyword_performance", customer_id=cid, start_date=start_date, end_date=end_date)

    try:
        client = _get_google_ads_client()
        query = KEYWORD_PERFORMANCE_QUERY.format(
            start_date=start_date, end_date=end_date
        )
        rows = _run_gaql(client, cid, query)

        if not rows:
            return (
                f"No keyword data for account {customer_id} "
                f"({start_date} to {end_date}). "
                "This could mean no active keywords or a test account."
            )

        lines = [
            f"# Keyword Performance: {start_date} to {end_date}\n",
            f"Account: {customer_id}",
            f"Total keywords: {len(rows)}\n",
        ]

        # Group by campaign > ad group
        structure: dict[str, dict[str, list]] = {}
        for row in rows:
            cname = row.campaign.name
            agname = row.ad_group.name
            if cname not in structure:
                structure[cname] = {}
            if agname not in structure[cname]:
                structure[cname][agname] = []
            structure[cname][agname].append(row)

        for campaign_name, ad_groups in structure.items():
            lines.append(f"## {campaign_name}\n")
            for ag_name, ag_rows in ad_groups.items():
                lines.append(f"### Ad Group: {ag_name}\n")
                lines.append(
                    "| Keyword | Match | QS | Impressions | Clicks | CTR | CPC | Cost | Conversions | CPA | IS |"
                )
                lines.append(
                    "|---------|-------|----|------------|--------|-----|-----|------|-------------|-----|-----|"
                )
                for row in ag_rows:
                    m = row.metrics
                    cr = row.ad_group_criterion
                    qs = (
                        str(cr.quality_info.quality_score)
                        if cr.quality_info.quality_score
                        else "—"
                    )
                    cpa = (
                        _fmt_currency(m.cost_micros / m.conversions)
                        if m.conversions > 0
                        else "—"
                    )
                    imp_share = _safe_pct(m.search_impression_share) or "—"
                    lines.append(
                        f"| {cr.keyword.text} "
                        f"| {cr.keyword.match_type.name} "
                        f"| {qs} "
                        f"| {m.impressions:,} "
                        f"| {m.clicks:,} "
                        f"| {_fmt_pct(m.ctr, 2)} "
                        f"| {_fmt_currency(m.average_cpc)} "
                        f"| {_fmt_currency(m.cost_micros)} "
                        f"| {m.conversions:.1f} "
                        f"| {cpa} "
                        f"| {imp_share} |"
                    )
                lines.append("")

        return "\n".join(lines)

    except Exception as e:
        logger.exception("google_ads_keyword_performance failed")
        return "Error pulling keyword performance. Check server logs for details."


@mcp.tool()
async def google_ads_change_history(
    customer_id: str,
    start_date: str,
    end_date: str,
) -> str:
    """Pull account change history from Google Ads.

    Detects what changes were made: budget changes, bid strategy changes,
    keyword additions/removals, status changes, etc. Changes are grouped
    by type with a human-readable summary.

    Note: The Change Event API only returns the last 30 days of data.

    Args:
        customer_id: Google Ads account ID (with or without dashes)
        start_date: Start of reporting period (YYYY-MM-DD)
        end_date: End of reporting period (YYYY-MM-DD)
    """
    try:
        cid = validate_customer_id(customer_id)
        start_date = validate_date(start_date, "start_date")
        end_date = validate_date(end_date, "end_date")
    except ValueError as e:
        return str(e)

    log_tool_call("google_ads_change_history", customer_id=cid, start_date=start_date, end_date=end_date)

    try:
        client = _get_google_ads_client()

        # Check 30-day limit
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        days_ago = (date.today() - start).days
        thirty_day_warning = ""
        if days_ago > 30:
            cutoff = date.today() - timedelta(days=30)
            thirty_day_warning = (
                f"\nWARNING: Start date is {days_ago} days ago. The Change Event "
                f"API only returns the last 30 days. Changes before {cutoff} "
                f"will not appear. Ask the specialist for manual context.\n"
            )

        query = CHANGE_HISTORY_QUERY.format(
            start_date=start_date, end_date=end_date
        )
        rows = _run_gaql(client, cid, query)

        if not rows:
            msg = (
                f"No changes detected for account {customer_id} "
                f"({start_date} to {end_date})."
            )
            if thirty_day_warning:
                msg += thirty_day_warning
            msg += "\nThis could mean no changes were made, or the account is a test account."
            return msg

        # Parse into dicts
        changes = []
        for row in rows:
            event = row.change_event
            changes.append(
                {
                    "date_time": str(event.change_date_time),
                    "resource_type": event.change_resource_type.name,
                    "resource_name": event.change_resource_name,
                    "operation": event.resource_change_operation.name,
                    "changed_fields": (
                        str(event.changed_fields) if event.changed_fields else ""
                    ),
                    "client_type": event.client_type.name,
                    "user_email": event.user_email,
                }
            )

        # Build summary
        lines = [
            f"# Account Change History: {start_date} to {end_date}\n",
            f"Account: {customer_id}",
            f"Total changes: {len(changes)}",
        ]

        if thirty_day_warning:
            lines.append(thirty_day_warning)

        # Group by operation
        by_operation: dict[str, int] = {}
        for c in changes:
            by_operation[c["operation"]] = by_operation.get(c["operation"], 0) + 1

        lines.append("\n## Changes by Operation\n")
        for op, count in sorted(by_operation.items()):
            lines.append(f"- {op}: {count}")

        # Group by resource type
        type_labels = {
            "CAMPAIGN": "Campaign Changes",
            "AD_GROUP": "Ad Group Changes",
            "AD_GROUP_CRITERION": "Keyword/Targeting Changes",
            "AD_GROUP_AD": "Ad Changes",
            "CAMPAIGN_BUDGET": "Budget Changes",
            "CAMPAIGN_CRITERION": "Campaign Targeting Changes",
            "AD_GROUP_BID_MODIFIER": "Bid Modifier Changes",
        }

        by_type: dict[str, list[dict]] = {}
        for c in changes:
            rtype = c["resource_type"]
            if rtype not in by_type:
                by_type[rtype] = []
            by_type[rtype].append(c)

        lines.append("\n## Changes by Type\n")
        for rtype, type_changes in sorted(by_type.items()):
            label = type_labels.get(rtype, rtype)
            lines.append(f"### {label} ({len(type_changes)})\n")

            for change in type_changes[:20]:
                date_str = (
                    change["date_time"][:10] if change["date_time"] else "unknown"
                )
                op = change["operation"]
                user = change["user_email"] or "system"
                lines.append(f"- **{date_str}** [{op}] by {user}")
                if change["changed_fields"]:
                    lines.append(f"  - Fields: {change['changed_fields']}")

            if len(type_changes) > 20:
                lines.append(f"- _...and {len(type_changes) - 20} more_")
            lines.append("")

        return "\n".join(lines)

    except Exception as e:
        logger.exception("google_ads_change_history failed")
        return "Error pulling change history. Check server logs for details."
