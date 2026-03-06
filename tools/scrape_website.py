#!/usr/bin/env python3
"""
scrape_website.py — Scrape a client's website for redesign concept generation.

Captures full-page screenshots, extracts text/images/structure, and downloads
key assets using Playwright headless browser.

Usage:
    python tools/scrape_website.py --url https://example.com
    python tools/scrape_website.py --url https://example.com --pages /,/about,/services
    python tools/scrape_website.py --url https://example.com --output-dir .tmp/my_project
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from playwright.sync_api import sync_playwright


def sanitize_domain(url: str) -> str:
    """Extract and sanitize domain name for use as a directory name."""
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    return re.sub(r"[^a-zA-Z0-9_-]", "_", domain)


def sanitize_page_name(page_path: str) -> str:
    """Convert a URL path to a safe filename."""
    if page_path == "/" or page_path == "":
        return "homepage"
    name = page_path.strip("/").replace("/", "_")
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name)


def dismiss_cookie_banners(page):
    """Attempt to dismiss common cookie consent banners."""
    selectors = [
        "button[id*='accept']",
        "button[class*='accept']",
        "button[id*='consent']",
        "button[class*='consent']",
        "button[id*='cookie']",
        "button[class*='cookie']",
        "a[id*='accept']",
        "a[class*='accept']",
        "[data-testid*='accept']",
        "[data-testid*='cookie']",
    ]
    for selector in selectors:
        try:
            el = page.query_selector(selector)
            if el and el.is_visible():
                el.click()
                time.sleep(0.5)
                return True
        except Exception:
            continue
    return False


def scroll_full_page(page):
    """Scroll through the full page to trigger lazy-loaded content."""
    page.evaluate("""
        async () => {
            const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
            if (!document.body) return;
            const height = document.body.scrollHeight || 0;
            const step = window.innerHeight || 800;
            for (let y = 0; y < height; y += step) {
                window.scrollTo(0, y);
                await delay(200);
            }
            window.scrollTo(0, 0);
        }
    """)
    time.sleep(1)


def extract_page_content(page) -> dict:
    """Extract structured content from the current page via DOM traversal."""
    return page.evaluate("""
        () => {
            const result = {
                title: document.title || '',
                meta_description: '',
                sections: [],
                images: [],
                navigation: [],
                raw_styles: {
                    colors: [],
                    background_colors: [],
                    fonts: [],
                    font_sizes: {},
                }
            };

            // Meta description
            const metaDesc = document.querySelector('meta[name="description"]');
            if (metaDesc) result.meta_description = metaDesc.getAttribute('content') || '';

            // Navigation
            const navElements = document.querySelectorAll('nav a, header a, [role="navigation"] a');
            const navSet = new Set();
            navElements.forEach(a => {
                const text = a.textContent.trim();
                const href = a.getAttribute('href');
                if (text && href && !navSet.has(text)) {
                    navSet.add(text);
                    result.navigation.push({ text, href });
                }
            });

            // Images
            document.querySelectorAll('img').forEach(img => {
                const src = img.src;
                const alt = img.alt || '';
                const width = img.naturalWidth || img.width;
                const height = img.naturalHeight || img.height;
                if (src && !src.startsWith('data:')) {
                    result.images.push({ src, alt, width, height });
                }
            });

            // Extract sections by semantic HTML
            const sectionSelectors = [
                { selector: 'header', type: 'header' },
                { selector: '[class*="hero"], [id*="hero"], section:first-of-type', type: 'hero' },
                { selector: 'main section, main > div > div, article', type: 'content' },
                { selector: 'footer', type: 'footer' }
            ];

            // Collect all text content by section
            const processedElements = new Set();

            function extractText(element) {
                const texts = [];
                const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, null, false);
                while (walker.nextNode()) {
                    const text = walker.currentNode.textContent.trim();
                    if (text && text.length > 1) {
                        const parent = walker.currentNode.parentElement;
                        const tag = parent ? parent.tagName.toLowerCase() : 'span';
                        texts.push({ tag, text });
                    }
                }
                return texts;
            }

            // Header
            const header = document.querySelector('header');
            if (header) {
                processedElements.add(header);
                const logoImg = header.querySelector('img[class*="logo"], img[alt*="logo"], a[class*="brand"] img, a[class*="logo"] img, header img:first-of-type');
                result.sections.push({
                    type: 'header',
                    logo_src: logoImg ? logoImg.src : null,
                    content: extractText(header)
                });
            }

            // All sections in main content
            const allSections = document.querySelectorAll('section, [class*="section"], main > div > div');
            allSections.forEach((section, index) => {
                if (processedElements.has(section)) return;
                processedElements.add(section);

                const heading = section.querySelector('h1, h2, h3');
                const isHero = index === 0 || section.matches('[class*="hero"], [id*="hero"]');

                result.sections.push({
                    type: isHero ? 'hero' : 'content',
                    heading: heading ? heading.textContent.trim() : null,
                    content: extractText(section)
                });
            });

            // Footer
            const footer = document.querySelector('footer');
            if (footer && !processedElements.has(footer)) {
                result.sections.push({
                    type: 'footer',
                    content: extractText(footer)
                });
            }

            // Extract computed styles from key elements
            const colorSet = new Set();
            const bgColorSet = new Set();
            const fontSet = new Set();

            const sampleElements = document.querySelectorAll('h1, h2, h3, h4, p, a, button, header, footer, section, [class*="hero"]');
            sampleElements.forEach(el => {
                const styles = window.getComputedStyle(el);
                colorSet.add(styles.color);
                bgColorSet.add(styles.backgroundColor);
                fontSet.add(styles.fontFamily.split(',')[0].trim().replace(/['"]/g, ''));
            });

            // Font sizes for headings and body
            ['h1', 'h2', 'h3', 'h4', 'p'].forEach(tag => {
                const el = document.querySelector(tag);
                if (el) {
                    const styles = window.getComputedStyle(el);
                    result.raw_styles.font_sizes[tag] = styles.fontSize;
                }
            });

            result.raw_styles.colors = [...colorSet].filter(c => c !== 'rgba(0, 0, 0, 0)');
            result.raw_styles.background_colors = [...bgColorSet].filter(c => c !== 'rgba(0, 0, 0, 0)');
            result.raw_styles.fonts = [...fontSet].filter(f => f.length > 0);

            return result;
        }
    """)


def download_asset(url: str, output_dir: Path, timeout: int = 10) -> str | None:
    """Download an asset and return the local filename, or None on failure."""
    try:
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        # Determine filename from URL
        parsed = urlparse(url)
        filename = os.path.basename(parsed.path) or "asset"
        if "." not in filename:
            content_type = response.headers.get("content-type", "")
            ext = ".png" if "png" in content_type else ".jpg" if "jpeg" in content_type or "jpg" in content_type else ".bin"
            filename += ext

        filepath = output_dir / filename
        # Avoid overwriting
        counter = 1
        while filepath.exists():
            stem = filepath.stem
            filepath = output_dir / f"{stem}_{counter}{filepath.suffix}"
            counter += 1

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return filepath.name
    except Exception as e:
        print(f"  Warning: Failed to download {url}: {e}")
        return None


def scrape_page(page, url: str, page_path: str, output_dir: Path) -> dict:
    """Scrape a single page and return its data."""
    page_name = sanitize_page_name(page_path)
    full_url = urljoin(url, page_path)

    print(f"\n--- Scraping: {full_url} ---")

    # Navigate to page
    try:
        page.goto(full_url, wait_until="networkidle", timeout=30000)
    except Exception:
        print(f"  Timeout on initial load, waiting for DOM content...")
        try:
            page.goto(full_url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"  Error loading {full_url}: {e}")
            return {"page": page_path, "error": str(e)}

    # Dismiss cookie banners
    dismiss_cookie_banners(page)

    # Scroll to trigger lazy loading
    scroll_full_page(page)

    # Take screenshot
    screenshots_dir = output_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    screenshot_path = screenshots_dir / f"{page_name}.png"

    print(f"  Capturing screenshot...")
    # Use CDP to take full-page screenshot — bypasses Playwright's font-wait hang
    import base64 as b64mod
    cdp = page.context.new_cdp_session(page)
    # Get page dimensions via CDP layout metrics
    try:
        layout = cdp.send("Page.getLayoutMetrics")
        css_size = layout.get("cssContentSize") or layout.get("contentSize") or {}
        width = int(css_size.get("width", 0)) or 1440
        height = int(css_size.get("height", 0)) or 900
    except Exception:
        width, height = 1440, 900
    height = min(height, 15000)
    width = max(width, 1440)
    # Expand viewport to full page for capture
    cdp.send("Emulation.setDeviceMetricsOverride", {
        "width": width, "height": height, "deviceScaleFactor": 1, "mobile": False,
    })
    page.wait_for_timeout(1000)
    result = cdp.send("Page.captureScreenshot", {"format": "png"})
    cdp.send("Emulation.clearDeviceMetricsOverride")
    cdp.detach()
    with open(screenshot_path, "wb") as f:
        f.write(b64mod.b64decode(result["data"]))
    print(f"  Saved: {screenshot_path}")

    # Extract content
    print(f"  Extracting content...")
    content = extract_page_content(page)
    content["url"] = full_url
    content["page_path"] = page_path
    content["page_name"] = page_name
    content["screenshot"] = str(screenshot_path)

    # Download key assets (logo, hero images)
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    downloaded_assets = []

    # Download logo if found
    for section in content.get("sections", []):
        if section.get("type") == "header" and section.get("logo_src"):
            local_name = download_asset(section["logo_src"], assets_dir)
            if local_name:
                section["logo_local"] = local_name
                downloaded_assets.append(local_name)

    # Download first few meaningful images (hero images, etc.)
    image_count = 0
    for img in content.get("images", []):
        if image_count >= 5:
            break
        # Skip tiny images (likely icons/tracking pixels)
        if img.get("width", 100) < 50 or img.get("height", 100) < 50:
            continue
        local_name = download_asset(img["src"], assets_dir)
        if local_name:
            img["local_file"] = local_name
            downloaded_assets.append(local_name)
            image_count += 1

    content["downloaded_assets"] = downloaded_assets
    print(f"  Extracted {len(content['sections'])} sections, {len(content['images'])} images, {len(content['navigation'])} nav items")

    return content


def check_network_access(url: str, timeout: int = 10) -> bool:
    """Pre-check: can we actually reach this URL? Returns True if reachable."""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        return response.status_code < 500
    except Exception:
        return False


def validate_page_data(page_data: dict) -> bool:
    """Check if a scraped page has real content (not an error or empty shell)."""
    if "error" in page_data:
        return False
    sections = page_data.get("sections", [])
    if len(sections) < 2:
        return False
    total_text = 0
    for section in sections:
        for item in section.get("content", []):
            total_text += len(item.get("text", ""))
    if total_text < 50:
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Scrape a website for redesign concept generation")
    parser.add_argument("--url", required=True, help="Target website URL (e.g., https://example.com)")
    parser.add_argument("--pages", default="/", help="Comma-separated page paths to scrape (default: /)")
    parser.add_argument("--output-dir", default=None, help="Output directory (default: .tmp/scrape_{domain})")
    args = parser.parse_args()

    # Normalize URL
    url = args.url.rstrip("/")
    if not url.startswith("http"):
        url = "https://" + url

    # Parse page paths
    page_paths = [p.strip() for p in args.pages.split(",") if p.strip()]

    # Set up output directory
    domain = sanitize_domain(url)
    output_dir = Path(args.output_dir) if args.output_dir else Path(f".tmp/scrape_{domain}")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Scraping {url}")
    print(f"Pages: {page_paths}")
    print(f"Output: {output_dir}")

    # --- NETWORK PRE-CHECK ---
    print(f"\nChecking network access to {url}...")
    if not check_network_access(url):
        print(f"\n{'='*60}")
        print(f"FATAL: Cannot reach {url}")
        print(f"{'='*60}")
        print(f"The scraper has no network access to this site.")
        print(f"No site_data.json was saved — refusing to generate fake data.")
        print(f"\nTo fix this:")
        print(f"  1. Check your internet connection")
        print(f"  2. If running in a sandbox, enable network egress or")
        print(f"     add '{urlparse(url).netloc}' to the domain allowlist")
        print(f"  3. Run this script locally instead")
        sys.exit(1)
    print(f"  OK — site is reachable")

    site_data = {
        "url": url,
        "domain": domain,
        "pages": [],
        "scrape_status": "in_progress",
        "source": "live_scrape",
        "scrape_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-remote-fonts", "--disable-gpu"],
        )
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )
        page = context.new_page()

        # Block font downloads to prevent screenshot hangs in sandboxed environments
        def handle_route(route):
            if route.request.resource_type == "font":
                route.abort()
            else:
                route.continue_()
        page.route("**/*", handle_route)

        failed_pages = []
        for page_path in page_paths:
            page_data = scrape_page(page, url, page_path, output_dir)
            if validate_page_data(page_data):
                site_data["pages"].append(page_data)
            else:
                error_msg = page_data.get("error", "Empty or insufficient content extracted")
                print(f"  FAILED: {page_path} — {error_msg}")
                failed_pages.append({"page": page_path, "error": error_msg})

        browser.close()

    # --- POST-SCRAPE VALIDATION ---
    if len(site_data["pages"]) == 0:
        print(f"\n{'='*60}")
        print(f"FATAL: All pages failed to scrape — no valid data collected")
        print(f"{'='*60}")
        print(f"Failed pages: {[fp['page'] for fp in failed_pages]}")
        print(f"No site_data.json was saved — refusing to generate fake data.")
        print(f"\nCheck that the URL is correct and the site is publicly accessible.")
        sys.exit(1)

    if failed_pages:
        site_data["failed_pages"] = failed_pages
        print(f"\nWarning: {len(failed_pages)} of {len(page_paths)} pages failed to scrape")

    site_data["scrape_status"] = "success"

    # Save site data
    site_data_path = output_dir / "site_data.json"
    with open(site_data_path, "w") as f:
        json.dump(site_data, f, indent=2, default=str)

    print(f"\n=== Scraping complete ===")
    print(f"Site data: {site_data_path}")
    print(f"Screenshots: {output_dir / 'screenshots'}")
    print(f"Assets: {output_dir / 'assets'}")
    print(f"Pages scraped: {len(site_data['pages'])} of {len(page_paths)}")

    return site_data


if __name__ == "__main__":
    main()
