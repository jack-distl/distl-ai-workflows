"""
Compare Paid vs Organic Keywords — Gap Finder

Takes two lists of keywords (paid and organic) from Ahrefs data
and identifies keywords where the domain is paying for traffic
but has no meaningful organic ranking.

Usage:
    Called by Claude during the signal-paid-organic-gap workflow.
    Input: JSON from Ahrefs site-explorer-paid-pages and site-explorer-organic-keywords.
    Output: Gap analysis with flagged keywords and summary.

This script does not make API calls — it processes data that Claude
has already retrieved from Ahrefs via MCP.
"""

import json
import sys


def compare_keywords(paid_keywords_json: str, organic_keywords_json: str, organic_threshold: int = 50) -> dict:
    """
    Compare paid keywords against organic rankings to find gaps.

    Args:
        paid_keywords_json: JSON string of paid keyword data from Ahrefs.
            Expected format: list of dicts with at least 'keyword' field.
            Optional fields: 'volume', 'traffic', 'position'.
        organic_keywords_json: JSON string of organic keyword data from Ahrefs.
            Expected format: list of dicts with at least 'keyword' and 'position' fields.
        organic_threshold: Position above which a keyword is considered
            "not ranking" (default: 50).

    Returns:
        dict with gap analysis results.
    """
    paid_data = json.loads(paid_keywords_json)
    organic_data = json.loads(organic_keywords_json)

    # Build organic keyword lookup: keyword -> best position
    organic_lookup = {}
    for item in organic_data:
        kw = item.get("keyword", "").lower().strip()
        pos = item.get("position", 999)
        if kw and (kw not in organic_lookup or pos < organic_lookup[kw]["position"]):
            organic_lookup[kw] = {
                "position": pos,
                "traffic": item.get("traffic", 0),
                "volume": item.get("volume", 0),
            }

    # Find gaps: paid keywords with no meaningful organic ranking
    gaps = []
    covered = []

    for item in paid_data:
        kw = item.get("keyword", "").lower().strip()
        if not kw:
            continue

        paid_info = {
            "keyword": kw,
            "paid_volume": item.get("volume", 0),
            "paid_traffic": item.get("traffic", 0),
        }

        organic_match = organic_lookup.get(kw)

        if organic_match is None:
            # Not ranking at all
            paid_info["organic_position"] = None
            paid_info["gap_reason"] = "no_organic_ranking"
            gaps.append(paid_info)
        elif organic_match["position"] > organic_threshold:
            # Ranking but too low to matter
            paid_info["organic_position"] = organic_match["position"]
            paid_info["gap_reason"] = f"position_{organic_match['position']}_below_threshold"
            gaps.append(paid_info)
        else:
            # Has meaningful organic ranking
            paid_info["organic_position"] = organic_match["position"]
            covered.append(paid_info)

    # Sort gaps by volume (highest opportunity first)
    gaps.sort(key=lambda x: x.get("paid_volume", 0), reverse=True)

    # Calculate summary metrics
    total_paid = len(gaps) + len(covered)
    gap_count = len(gaps)
    gap_percentage = round((gap_count / total_paid * 100), 1) if total_paid > 0 else 0
    total_gap_volume = sum(g.get("paid_volume", 0) for g in gaps)

    return {
        "total_paid_keywords": total_paid,
        "gap_keywords": gap_count,
        "covered_keywords": len(covered),
        "gap_percentage": gap_percentage,
        "total_gap_search_volume": total_gap_volume,
        "top_gaps": gaps[:10],  # Top 10 by volume
        "should_flag": gap_count >= 3 or gap_percentage > 50,
        "summary": _build_summary(gaps, gap_count, gap_percentage, total_paid),
    }


def _build_summary(gaps: list, gap_count: int, gap_percentage: float, total_paid: int) -> str:
    """Build a human-readable summary for the Monday.com Signal Detail field."""
    if gap_count == 0:
        return "No paid/organic gap found. All paid keywords have organic coverage."

    top_keywords = [g["keyword"] for g in gaps[:5]]
    keyword_list = ", ".join(f"'{kw}'" for kw in top_keywords)

    summary = (
        f"Bidding on {gap_count} keywords with no meaningful organic ranking "
        f"({gap_percentage}% of {total_paid} paid keywords). "
        f"Top gaps: {keyword_list}."
    )

    total_volume = sum(g.get("paid_volume", 0) for g in gaps)
    if total_volume > 0:
        summary += f" Combined monthly search volume of gap keywords: {total_volume:,}."

    return summary


if __name__ == "__main__":
    # CLI usage: python compare_paid_organic.py <paid_json_file> <organic_json_file>
    if len(sys.argv) < 3:
        print("Usage: python compare_paid_organic.py <paid_keywords.json> <organic_keywords.json>")
        print("       Optional third argument: organic_threshold (default: 50)")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        paid_json = f.read()
    with open(sys.argv[2]) as f:
        organic_json = f.read()

    threshold = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    result = compare_keywords(paid_json, organic_json, threshold)

    print(json.dumps(result, indent=2))
