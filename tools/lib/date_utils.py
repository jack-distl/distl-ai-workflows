"""Date range utilities for Google Ads reporting."""

import calendar
from datetime import date


def get_reporting_period(month_str: str) -> tuple[date, date]:
    """Given a month string like '2026-02', return (start_date, end_date) for that month."""
    year, month = map(int, month_str.split("-"))
    start = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end = date(year, month, last_day)
    return start, end


def get_comparison_period(start_date: date, end_date: date) -> tuple[date, date]:
    """Return the previous month's date range as comparison period."""
    if start_date.month == 1:
        prev_year = start_date.year - 1
        prev_month = 12
    else:
        prev_year = start_date.year
        prev_month = start_date.month - 1

    prev_start = date(prev_year, prev_month, 1)
    prev_last_day = calendar.monthrange(prev_year, prev_month)[1]
    prev_end = date(prev_year, prev_month, prev_last_day)
    return prev_start, prev_end


def format_date_for_gaql(d: date) -> str:
    """Format a Python date as a GAQL-compatible string (YYYY-MM-DD)."""
    return d.strftime("%Y-%m-%d")
