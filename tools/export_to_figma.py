#!/usr/bin/env python3
"""
export_to_figma.py — Export website redesign concepts to Figma.

Supports two export methods:
1. Figma MCP Server (recommended): Captures live HTML as editable Figma layers
2. Screenshot package: Creates a structured deliverable with screenshots and
   design tokens that can be manually imported into Figma

Usage:
    python tools/export_to_figma.py --project-dir .tmp/redesign_example_com --renders-dir .tmp/renders_example_com
    python tools/export_to_figma.py --project-dir .tmp/redesign_example_com --method mcp --port 8080
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

import requests
from dotenv import load_dotenv

load_dotenv()


def extract_design_tokens(project_dir: Path) -> dict:
    """Extract design tokens from the redesign manifest and HTML files."""
    tokens = {
        "colors": {},
        "fontFamilies": {},
        "fontSizes": {},
        "spacing": {},
    }

    # Try to load the original site data for brand colors
    # Look for site_data in a sibling scrape directory
    parent = project_dir.parent
    domain = project_dir.name.replace("redesign_", "")
    scrape_dir = parent / f"scrape_{domain}"
    site_data_path = scrape_dir / "site_data.json"

    if site_data_path.exists():
        with open(site_data_path) as f:
            site_data = json.load(f)

        # Extract colors from scraped site
        for page in site_data.get("pages", []):
            styles = page.get("raw_styles", {})

            # Colors
            for i, color in enumerate(styles.get("colors", [])[:5]):
                tokens["colors"][f"original-{i+1}"] = {
                    "value": color,
                    "type": "color",
                    "description": "Original site color",
                }

            # Fonts
            for i, font in enumerate(styles.get("fonts", [])[:3]):
                tokens["fontFamilies"][f"original-{i+1}"] = {
                    "value": font,
                    "type": "fontFamilies",
                    "description": "Original site font",
                }

            # Font sizes
            for tag, size in styles.get("font_sizes", {}).items():
                tokens["fontSizes"][tag] = {
                    "value": size.replace("px", ""),
                    "type": "fontSizes",
                    "description": f"Original {tag} size",
                }

    # Parse redesign HTML files to extract new design tokens
    pages_dir = project_dir / "pages"
    if pages_dir.exists():
        for html_file in pages_dir.glob("*.html"):
            content = html_file.read_text()

            # Extract Google Fonts references
            import re

            font_matches = re.findall(r"family=([^&\"']+)", content)
            for match in font_matches:
                fonts = match.replace("+", " ").split("|")
                for font in fonts:
                    font_name = font.split(":")[0].strip()
                    if font_name:
                        tokens["fontFamilies"][font_name.lower().replace(" ", "-")] = {
                            "value": font_name,
                            "type": "fontFamilies",
                            "description": "Redesign font",
                        }

            # Extract CSS custom properties
            css_var_matches = re.findall(r"--([a-zA-Z-]+):\s*([^;]+);", content)
            for var_name, var_value in css_var_matches:
                var_value = var_value.strip()
                if "#" in var_value or "rgb" in var_value or "hsl" in var_value:
                    tokens["colors"][var_name] = {
                        "value": var_value,
                        "type": "color",
                        "description": "Redesign CSS variable",
                    }

    return tokens


def generate_export_instructions(
    project_dir: Path,
    renders_dir: Path,
    tokens: dict,
    method: str,
    port: int = 8080,
) -> str:
    """Generate human-readable export instructions."""
    domain = project_dir.name.replace("redesign_", "")

    lines = [
        f"# Figma Export Instructions — {domain}",
        "",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    if method == "mcp":
        lines.extend([
            "## Method: Figma MCP Server (Recommended)",
            "",
            "The redesigned pages are being served locally. Use the Figma MCP",
            "server's `generate_figma_design` tool to capture them as editable",
            "Figma layers.",
            "",
            "### Setup (one-time)",
            "",
            "1. Ensure you have a Figma Dev or Full seat",
            "2. Add the Figma MCP server to Claude Code:",
            "   ```",
            "   claude mcp add --transport http figma https://mcp.figma.com/mcp",
            "   ```",
            "",
            "### Capture pages",
            "",
        ])

        pages_dir = project_dir / "pages"
        if pages_dir.exists():
            for html_file in sorted(pages_dir.glob("*.html")):
                page_name = html_file.stem
                url = f"http://localhost:{port}/pages/{html_file.name}"
                lines.append(f"- **{page_name}**: `generate_figma_design` with URL `{url}`")

        lines.extend([
            "",
            "Each capture creates an editable Figma frame with proper layers,",
            "text nodes, and image fills.",
        ])
    else:
        lines.extend([
            "## Method: Manual Import",
            "",
            "### Step 1: Create a new Figma file",
            "",
            f'1. Open Figma and create a new file named "{domain} — Redesign Concept"',
            "2. Create a page for each redesigned page",
            "",
            "### Step 2: Import screenshots",
            "",
            "For each page, import the rendered screenshots:",
            "",
        ])

        if renders_dir.exists():
            for viewport in ["desktop", "tablet", "mobile"]:
                viewport_dir = renders_dir / viewport
                if viewport_dir.exists():
                    for img in sorted(viewport_dir.glob("*.png")):
                        lines.append(f"- **{img.stem} ({viewport})**: `{img}`")

        lines.extend([
            "",
            "### Step 3: Import design tokens (optional)",
            "",
            "Install the 'Design Tokens' plugin in Figma, then import the",
            f"tokens file at: `{project_dir / 'figma' / 'design_tokens.json'}`",
            "",
            "### Step 4: View live HTML (optional)",
            "",
            "Open the HTML files directly in a browser for interactive preview:",
            "",
        ])

        pages_dir = project_dir / "pages"
        if pages_dir.exists():
            for html_file in sorted(pages_dir.glob("*.html")):
                lines.append(f"- **{html_file.stem}**: `{html_file.absolute()}`")

    # Add comparison images section
    comparisons_dir = renders_dir / "comparisons" if renders_dir else None
    if comparisons_dir and comparisons_dir.exists():
        lines.extend([
            "",
            "## Before/After Comparisons",
            "",
        ])
        for img in sorted(comparisons_dir.glob("*.png")):
            lines.append(f"- **{img.stem}**: `{img}`")

    return "\n".join(lines)


def start_local_server(directory: str, port: int) -> socketserver.TCPServer:
    """Start a local HTTP server for MCP capture."""

    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

        def log_message(self, format, *args):
            pass

    server = socketserver.TCPServer(("127.0.0.1", port), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main():
    parser = argparse.ArgumentParser(description="Export website redesign to Figma")
    parser.add_argument("--project-dir", required=True, help="Path to redesign directory")
    parser.add_argument("--renders-dir", default=None, help="Path to rendered screenshots directory")
    parser.add_argument("--method", default="screenshots", choices=["mcp", "screenshots"], help="Export method")
    parser.add_argument("--port", type=int, default=8080, help="Port for local server (MCP method)")
    parser.add_argument("--project-name", default=None, help="Name for the Figma file")
    args = parser.parse_args()

    project_dir = Path(args.project_dir)
    if not project_dir.exists():
        print(f"Error: Project directory not found: {project_dir}")
        sys.exit(1)

    domain = project_dir.name.replace("redesign_", "")

    # Find renders directory
    renders_dir = Path(args.renders_dir) if args.renders_dir else Path(f".tmp/renders_{domain}")
    if not renders_dir.exists():
        print(f"Warning: Renders directory not found: {renders_dir}")
        print("Run render_and_screenshot.py first for screenshot-based export")

    # Set up figma output directory
    figma_dir = project_dir / "figma"
    figma_dir.mkdir(parents=True, exist_ok=True)

    print(f"Exporting to Figma: {domain}")
    print(f"Method: {args.method}")

    # Extract design tokens
    print("  Extracting design tokens...")
    tokens = extract_design_tokens(project_dir)

    tokens_path = figma_dir / "design_tokens.json"
    with open(tokens_path, "w") as f:
        json.dump(tokens, f, indent=2)
    print(f"  Design tokens: {tokens_path}")

    server = None
    if args.method == "mcp":
        # Start local server for MCP capture
        try:
            server = start_local_server(str(project_dir), args.port)
            print(f"  Local server started on port {args.port}")
            print(f"  Pages available at: http://localhost:{args.port}/pages/")
        except OSError as e:
            print(f"  Error starting server on port {args.port}: {e}")
            print(f"  Try a different port with --port")
            sys.exit(1)

    # Generate export instructions
    instructions = generate_export_instructions(
        project_dir, renders_dir, tokens, args.method, args.port
    )

    instructions_path = figma_dir / "export_instructions.md"
    with open(instructions_path, "w") as f:
        f.write(instructions)

    print(f"  Instructions: {instructions_path}")

    print(f"\n=== Figma export ready ===")
    print(f"Output: {figma_dir}")

    if args.method == "mcp":
        print(f"\nLocal server running at http://localhost:{args.port}/pages/")
        print("Use Figma MCP's generate_figma_design tool to capture each page.")
        print("Press Ctrl+C to stop the server when done.")
        try:
            signal.pause()
        except (KeyboardInterrupt, AttributeError):
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        finally:
            if server:
                server.shutdown()
    elif args.method == "screenshots":
        print(f"\nFollow the instructions in: {instructions_path}")
        print("Import screenshots into Figma manually or use html.to.design plugin.")

    if server:
        server.shutdown()


if __name__ == "__main__":
    main()
