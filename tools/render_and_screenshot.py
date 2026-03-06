#!/usr/bin/env python3
"""
render_and_screenshot.py — Render redesigned HTML files and capture screenshots.

Opens generated HTML files in a real Chromium browser via Playwright, waits for
fonts/images to load, and captures full-page screenshots at desktop, tablet,
and mobile viewports. Can also start a local server for manual review or
Figma MCP capture.

Usage:
    python tools/render_and_screenshot.py --redesign-dir .tmp/redesign_example_com
    python tools/render_and_screenshot.py --redesign-dir .tmp/redesign_example_com --serve --port 8080
"""

import argparse
import http.server
import json
import os
import signal
import socketserver
import sys
import threading
import time
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 375, "height": 812},
}


def start_local_server(directory: str, port: int) -> tuple[socketserver.TCPServer, threading.Thread]:
    """Start a simple HTTP server in a background thread."""
    handler = http.server.SimpleHTTPRequestHandler

    class QuietHandler(handler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

        def log_message(self, format, *args):
            pass  # Suppress request logs

    server = socketserver.TCPServer(("127.0.0.1", port), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def capture_screenshots(html_path: Path, output_dir: Path, port: int = 0) -> dict:
    """Capture screenshots of an HTML file at multiple viewports."""
    page_name = html_path.stem
    results = {}

    import base64 as b64mod

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-remote-fonts", "--disable-gpu"],
        )

        for viewport_name, viewport_size in VIEWPORTS.items():
            viewport_dir = output_dir / viewport_name
            viewport_dir.mkdir(parents=True, exist_ok=True)

            context = browser.new_context(viewport=viewport_size)
            page = context.new_page()

            # Block font downloads to prevent screenshot hangs
            def handle_route(route):
                if route.request.resource_type == "font":
                    route.abort()
                else:
                    route.continue_()
            page.route("**/*", handle_route)

            # Use local server URL if port provided, otherwise file:// protocol
            if port > 0:
                url = f"http://localhost:{port}/pages/{html_path.name}"
            else:
                url = f"file://{html_path.absolute()}"

            try:
                page.goto(url, wait_until="networkidle", timeout=15000)
            except Exception:
                # Fallback: just wait for DOM
                try:
                    page.goto(url, wait_until="domcontentloaded", timeout=10000)
                    page.wait_for_timeout(3000)
                except Exception as e:
                    print(f"  Error loading {page_name} at {viewport_name}: {e}")
                    context.close()
                    continue

            # Wait for animations to settle
            page.wait_for_timeout(2000)

            # Use CDP to take screenshot — bypasses font-wait hang
            screenshot_path = viewport_dir / f"{page_name}.png"
            cdp = context.new_cdp_session(page)
            try:
                layout = cdp.send("Page.getLayoutMetrics")
                css_size = layout.get("cssContentSize") or layout.get("contentSize") or {}
                width = int(css_size.get("width", 0)) or viewport_size["width"]
                height = int(css_size.get("height", 0)) or viewport_size["height"]
            except Exception:
                width, height = viewport_size["width"], viewport_size["height"]
            height = min(height, 15000)
            cdp.send("Emulation.setDeviceMetricsOverride", {
                "width": width, "height": height, "deviceScaleFactor": 1, "mobile": viewport_name == "mobile",
            })
            page.wait_for_timeout(500)
            result = cdp.send("Page.captureScreenshot", {"format": "png"})
            cdp.send("Emulation.clearDeviceMetricsOverride")
            cdp.detach()
            with open(screenshot_path, "wb") as f:
                f.write(b64mod.b64decode(result["data"]))
            results[viewport_name] = str(screenshot_path)

            context.close()

        browser.close()

    return results


def create_comparison_image(
    original_screenshot: str,
    redesign_screenshot: str,
    output_path: Path,
):
    """Create a side-by-side before/after comparison image."""
    try:
        original = Image.open(original_screenshot)
        redesign = Image.open(redesign_screenshot)

        # Normalize heights: use the shorter of the two (capped at a reasonable height)
        max_height = min(original.height, redesign.height, 4000)

        # Scale both to same width
        target_width = 720

        orig_ratio = target_width / original.width
        orig_resized = original.resize(
            (target_width, min(int(original.height * orig_ratio), max_height)),
            Image.Resampling.LANCZOS,
        )

        redesign_ratio = target_width / redesign.width
        redesign_resized = redesign.resize(
            (target_width, min(int(redesign.height * redesign_ratio), max_height)),
            Image.Resampling.LANCZOS,
        )

        # Use the taller height for the comparison
        comparison_height = max(orig_resized.height, redesign_resized.height)

        # Create comparison canvas with labels
        label_height = 40
        gap = 20
        canvas_width = target_width * 2 + gap
        canvas_height = comparison_height + label_height

        canvas = Image.new("RGB", (canvas_width, canvas_height), (245, 245, 245))

        # Paste images
        canvas.paste(orig_resized, (0, label_height))
        canvas.paste(redesign_resized, (target_width + gap, label_height))

        canvas.save(str(output_path), quality=90)
        return True
    except Exception as e:
        print(f"  Warning: Could not create comparison image: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Render redesigned HTML and capture screenshots")
    parser.add_argument("--redesign-dir", required=True, help="Path to redesign output directory")
    parser.add_argument("--output-dir", default=None, help="Output directory for screenshots")
    parser.add_argument("--original-dir", default=None, help="Path to original scrape directory (for comparisons)")
    parser.add_argument("--serve", action="store_true", help="Start a local HTTP server after rendering")
    parser.add_argument("--port", type=int, default=8080, help="Port for local server (default: 8080)")
    args = parser.parse_args()

    redesign_dir = Path(args.redesign_dir)
    pages_dir = redesign_dir / "pages"

    if not pages_dir.exists():
        print(f"Error: Pages directory not found: {pages_dir}")
        sys.exit(1)

    # Find HTML files
    html_files = sorted(pages_dir.glob("*.html"))
    if not html_files:
        print(f"Error: No HTML files found in {pages_dir}")
        sys.exit(1)

    # Load manifest if available
    manifest_path = redesign_dir / "redesign_manifest.json"
    manifest = {}
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)

    domain = manifest.get("domain", "unknown")

    # Set up output directory
    output_dir = Path(args.output_dir) if args.output_dir else Path(f".tmp/renders_{domain}")
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Rendering {len(html_files)} pages")
    print(f"Output: {output_dir}")

    # Start a local server for rendering (CDN scripts need HTTP context)
    server = None
    port = args.port
    try:
        server, _ = start_local_server(str(redesign_dir), port)
        print(f"Local server started on port {port}")
    except OSError:
        print(f"Port {port} in use, trying {port + 1}")
        port += 1
        try:
            server, _ = start_local_server(str(redesign_dir), port)
        except OSError:
            print("Warning: Could not start local server, using file:// protocol")
            port = 0

    # Capture screenshots for each page
    all_results = {}
    for html_file in html_files:
        page_name = html_file.stem
        print(f"\n  Rendering: {page_name}")

        results = capture_screenshots(html_file, output_dir, port=port)
        all_results[page_name] = results

        for viewport, path in results.items():
            print(f"    {viewport}: {path}")

    # Create comparison images if original screenshots available
    original_dir = Path(args.original_dir) if args.original_dir else None
    if original_dir and (original_dir / "screenshots").exists():
        comparisons_dir = output_dir / "comparisons"
        comparisons_dir.mkdir(exist_ok=True)
        print(f"\n  Creating before/after comparisons...")

        for page_name, results in all_results.items():
            desktop_redesign = results.get("desktop")
            # Try to find matching original screenshot
            original_screenshot = original_dir / "screenshots" / f"{page_name}.png"
            if not original_screenshot.exists():
                original_screenshot = original_dir / "screenshots" / "homepage.png"

            if desktop_redesign and original_screenshot.exists():
                comparison_path = comparisons_dir / f"{page_name}_comparison.png"
                success = create_comparison_image(
                    str(original_screenshot),
                    desktop_redesign,
                    comparison_path,
                )
                if success:
                    print(f"    Comparison: {comparison_path}")

    # Save render manifest
    render_manifest = {
        "domain": domain,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pages": all_results,
        "viewports": VIEWPORTS,
    }
    render_manifest_path = output_dir / "render_manifest.json"
    with open(render_manifest_path, "w") as f:
        json.dump(render_manifest, f, indent=2)

    print(f"\n=== Rendering complete ===")
    print(f"Screenshots: {output_dir}")
    print(f"Manifest: {render_manifest_path}")

    # Keep server running if --serve flag
    if args.serve and server:
        print(f"\nLocal server running at http://localhost:{port}/pages/")
        print("Press Ctrl+C to stop")
        try:
            signal.pause()
        except (KeyboardInterrupt, AttributeError):
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        finally:
            server.shutdown()
    elif server:
        server.shutdown()


if __name__ == "__main__":
    main()
