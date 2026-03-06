"""Shared security utilities: authentication, input validation, audit logging.

All incoming MCP requests pass through these checks before reaching tool logic.
"""

import functools
import hmac
import logging
import os
import re
import time
from datetime import datetime

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("audit")

# --- API Key Authentication ---

_API_KEY: str | None = None


def _get_api_key() -> str | None:
    """Load the expected API key from the environment (cached)."""
    global _API_KEY
    if _API_KEY is None:
        _API_KEY = os.getenv("MCP_API_KEY", "")
    return _API_KEY or None


def verify_api_key(provided: str) -> bool:
    """Constant-time comparison of the provided API key against the expected one.

    Uses hmac.compare_digest to prevent timing attacks.
    """
    expected = _get_api_key()
    if not expected:
        # No key configured — reject all requests in production, allow in dev
        if os.getenv("MCP_AUTH_DISABLED", "").lower() == "true":
            if os.getenv("ENVIRONMENT", "").lower() == "production":
                logger.error("MCP_AUTH_DISABLED is set but ENVIRONMENT=production. Rejecting request.")
                return False
            logger.warning("MCP_AUTH_DISABLED is true — authentication bypassed (dev mode).")
            return True
        logger.error("MCP_API_KEY not set and MCP_AUTH_DISABLED is not true. Rejecting request.")
        return False
    return hmac.compare_digest(provided.encode(), expected.encode())


# --- Input Validation ---

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_CUSTOMER_ID_RE = re.compile(r"^[\d\-]+$")
# Allow letters, numbers, spaces, hyphens, ampersands, periods, commas, apostrophes
_CLIENT_NAME_RE = re.compile(r"^[\w\s\-&.,\'\"()]+$", re.UNICODE)


def validate_date(value: str, field_name: str = "date") -> str:
    """Validate a date string is YYYY-MM-DD format and is a real date.

    Returns the validated date string.
    Raises ValueError if invalid.
    """
    if not _DATE_RE.match(value):
        raise ValueError(f"Invalid {field_name}: '{value}'. Must be YYYY-MM-DD format.")
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid {field_name}: '{value}'. Not a valid calendar date.")
    return value


def validate_customer_id(value: str) -> str:
    """Validate a Google Ads customer ID (digits, optionally with dashes).

    Returns the cleaned ID (digits only).
    Raises ValueError if invalid.
    """
    if not _CUSTOMER_ID_RE.match(value):
        raise ValueError(f"Invalid customer ID: '{value}'. Must contain only digits and dashes.")
    cleaned = value.replace("-", "")
    if not cleaned.isdigit() or len(cleaned) < 7 or len(cleaned) > 10:
        raise ValueError(f"Invalid customer ID: '{value}'. Must be 7-10 digits.")
    return cleaned


def validate_client_name(value: str) -> str:
    """Validate a client name for safe use in Drive API queries.

    Returns the validated name.
    Raises ValueError if invalid.
    """
    if not value or not value.strip():
        raise ValueError("Client name cannot be empty.")
    if len(value) > 200:
        raise ValueError("Client name too long (max 200 characters).")
    if not _CLIENT_NAME_RE.match(value):
        raise ValueError(
            f"Invalid client name: '{value}'. "
            "Only letters, numbers, spaces, hyphens, ampersands, periods, "
            "commas, apostrophes, and parentheses are allowed."
        )
    return value.strip()


def sanitize_for_drive_query(value: str) -> str:
    """Escape a string for safe use in Google Drive API query strings.

    Single quotes are escaped with a backslash as per Drive API docs.
    """
    return value.replace("\\", "\\\\").replace("'", "\\'")


# --- Audit Logging ---


def log_tool_call(tool_name: str, **params):
    """Log a tool invocation for audit purposes.

    Logs to the 'audit' logger at INFO level. In production, configure
    this logger to write to a persistent store (Cloud Logging, etc.).
    """
    # Filter out large content values from the log (e.g., full report text)
    safe_params = {}
    for k, v in params.items():
        if isinstance(v, str) and len(v) > 200:
            safe_params[k] = f"{v[:100]}... ({len(v)} chars)"
        else:
            safe_params[k] = v

    audit_logger.info(
        "tool_call: %s | params: %s",
        tool_name,
        safe_params,
    )
