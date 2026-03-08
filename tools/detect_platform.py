"""Detect the ecommerce platform powering a website.

Checks HTTP headers and HTML source for platform-specific indicators.
Outputs JSON to stdout with the detected platform and confidence level.

Usage:
    python tools/detect_platform.py --url https://example.com [--timeout 15]
"""

import argparse
import json
import logging
import re
import sys
from urllib.parse import urlparse

import requests

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

PLATFORM_SIGNATURES = {
    "Shopify": {
        "source": [
            r"cdn\.shopify\.com",
            r"Shopify\.theme",
            r"myshopify\.com",
            r"shopify-section",
            r"shopify\.com/s/files",
            r'"shopify"',
        ],
        "headers": {
            "X-ShopId": None,
            "X-Shopify-Stage": None,
        },
        "meta_generator": r"Shopify",
    },
    "WooCommerce": {
        "source": [
            r"woocommerce",
            r"wc-blocks",
            r"/wp-content/plugins/woocommerce",
            r"wc-add-to-cart",
            r"woocommerce-product",
        ],
        "headers": {},
        "meta_generator": r"WooCommerce",
    },
    "Magento": {
        "source": [
            r"Mage\.",
            r"/static/frontend/Magento",
            r"mage/cookies",
            r"magento",
            r"Magento_Ui",
        ],
        "headers": {
            "X-Magento-Tags": None,
        },
        "meta_generator": r"Magento",
    },
    "BigCommerce": {
        "source": [
            r"bigcommerce\.com",
            r"stencil-utils",
            r"BigCommerce",
            r"data-content-region",
        ],
        "headers": {
            "X-BC-Store-Version": None,
        },
        "meta_generator": r"BigCommerce",
    },
    "Squarespace": {
        "source": [
            r"squarespace\.com",
            r"static\.squarespace",
            r"sqs-block",
        ],
        "headers": {
            "X-ServedBy": "squarespace",
        },
        "meta_generator": r"Squarespace",
    },
    "Wix": {
        "source": [
            r"wix\.com",
            r"wixstatic\.com",
            r"X-Wix",
        ],
        "headers": {
            "X-Wix-Request-Id": None,
        },
        "meta_generator": r"Wix",
    },
}

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}. Only http/https allowed.")
    if not parsed.hostname:
        raise ValueError("URL must include a hostname.")
    return url


def detect_platform(url: str, timeout: int = 15) -> dict:
    result = {
        "url": url,
        "platform": "Unknown",
        "confidence": "none",
        "indicators": [],
    }

    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=True,
        )
        resp.raise_for_status()
    except requests.exceptions.SSLError:
        try:
            resp = requests.get(
                url,
                timeout=timeout,
                headers={"User-Agent": USER_AGENT},
                allow_redirects=True,
                verify=False,
            )
        except requests.RequestException as e:
            result["error"] = f"Request failed: {e}"
            return result
    except requests.RequestException as e:
        result["error"] = f"Request failed: {e}"
        return result

    headers = resp.headers
    source = resp.text[:200_000]  # Cap at 200KB to avoid memory issues

    scores: dict[str, list[str]] = {}

    for platform, sigs in PLATFORM_SIGNATURES.items():
        indicators = []

        # Check HTML source patterns
        for pattern in sigs["source"]:
            if re.search(pattern, source, re.IGNORECASE):
                indicators.append(f"Source pattern matched: {pattern}")

        # Check response headers
        for header, expected_value in sigs["headers"].items():
            header_val = headers.get(header)
            if header_val is not None:
                if expected_value is None or expected_value.lower() in header_val.lower():
                    indicators.append(f"Header found: {header}={header_val}")

        # Check meta generator tag
        if sigs.get("meta_generator"):
            generator_match = re.search(
                r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)["\']',
                source,
                re.IGNORECASE,
            )
            if generator_match and re.search(
                sigs["meta_generator"], generator_match.group(1), re.IGNORECASE
            ):
                indicators.append(f"Meta generator: {generator_match.group(1)}")

        if indicators:
            scores[platform] = indicators

    if scores:
        # Pick platform with most indicators
        best_platform = max(scores, key=lambda p: len(scores[p]))
        indicator_count = len(scores[best_platform])

        if indicator_count >= 3:
            confidence = "high"
        elif indicator_count == 2:
            confidence = "medium"
        else:
            confidence = "low"

        result["platform"] = best_platform
        result["confidence"] = confidence
        result["indicators"] = scores[best_platform]

        # Note if multiple platforms detected (unusual but possible)
        if len(scores) > 1:
            others = [p for p in scores if p != best_platform]
            result["also_detected"] = {p: scores[p] for p in others}

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Detect the ecommerce platform of a website"
    )
    parser.add_argument("--url", required=True, help="Website URL to check")
    parser.add_argument(
        "--timeout",
        type=int,
        default=15,
        help="Request timeout in seconds (default: 15)",
    )
    args = parser.parse_args()

    try:
        url = validate_url(args.url)
    except ValueError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    logger.info(f"Detecting platform for {url}...")
    result = detect_platform(url, timeout=args.timeout)
    print(json.dumps(result, indent=2))

    if result.get("error"):
        sys.exit(1)


if __name__ == "__main__":
    main()
