# Website Redesign Concept

## Objective

Generate a bold, modern website redesign concept for a client proposal. Scrape their current site, redesign it with agent-generated HTML/CSS, render polished screenshots, and export to Figma for editing and client presentation.

**Cost per run: $0** — all AI work is done by the agent within the Claude Code session.

## Prerequisites

- Python 3.10+
- Dependencies installed: `pip install -r requirements.txt && playwright install chromium`
- `FIGMA_ACCESS_TOKEN` set in `.env` (optional, for Figma export features)

## Required Inputs

| Input | Required | Description |
|-------|----------|-------------|
| Client website URL | Yes | The live URL to scrape (e.g., `https://example.com`) |
| Pages to redesign | No | Comma-separated paths (default: `/` homepage only) |
| Design style | No | `bold-modern`, `minimal-clean`, or `creative-agency` (default: `bold-modern`) |

---

## Steps

### Step 1: Scrape the Current Website

**Tool:** `tools/scrape_website.py`

```bash
python tools/scrape_website.py --url https://clientsite.com --pages /,/about,/services
```

**What it does:**
- Captures full-page screenshots at 1440px desktop resolution
- Extracts all text content, navigation, images, colors, and fonts
- Downloads the logo and key hero images
- Saves everything to `.tmp/scrape_{domain}/`

**Verify:** Open `.tmp/scrape_{domain}/screenshots/homepage.png` to confirm the page captured correctly. Check `site_data.json` to confirm content extraction looks reasonable.

**Troubleshooting:**
- If the page shows a cookie banner covering content, the tool attempts auto-dismiss. If it fails, the screenshot will still capture — the redesign step works from the extracted text, not the screenshot alone.
- If images fail to download, the redesign will use placeholder images instead.
- For sites with heavy JavaScript (SPAs), the tool waits for network idle and scrolls to trigger lazy loading.
- If the scraper exits with `FATAL: Cannot reach {url}`, you have no network access. **Do not proceed.** Tell the user and suggest: enable network egress in sandbox settings, add the domain to the allowlist, or run the scraper locally.

### Step 1.5: Validate Before Proceeding (MANDATORY)

**STOP — Before proceeding to Step 2, verify ALL of the following:**

- [ ] `site_data.json` exists and has `"scrape_status": "success"`
- [ ] `"source"` field is `"live_scrape"` (not `"fallback"` or missing)
- [ ] `downloaded_assets` is NOT empty (at minimum, a logo should be captured)
- [ ] `raw_styles.colors` contains real CSS values extracted from the page
- [ ] At least one page has 3+ sections with real text content
- [ ] Screenshots exist in `.tmp/scrape_{domain}/screenshots/` and show the actual website (not a blank/error page)

**If ANY of these fail: STOP. Do not generate a redesign.**

A redesign built on wrong brand colors, made-up content, or placeholder data is worse than no redesign. Tell the user what failed and give them options to fix it (network access, manual data, running locally).

### Step 2: Generate the Redesign (Agent-Driven)

**This step is performed by the agent directly — no script to run.**

**Prerequisite:** Step 1.5 validation must pass. If you cannot confirm the scraped data came from the live website, do NOT proceed.

The agent:
1. Reads `.tmp/scrape_{domain}/site_data.json` for content and structure
2. Views the screenshots in `.tmp/scrape_{domain}/screenshots/` to see the current layout
3. Follows the **Design Principles** section below to determine the visual direction
4. Creates `.tmp/redesign_{domain}/pages/` directory
5. Writes one complete HTML file per page using the Write tool

**For each page, the agent generates a self-contained HTML file with:**
- `<!DOCTYPE html>` and proper document structure
- Tailwind CSS via CDN: `<script src="https://cdn.tailwindcss.com"></script>`
- Google Fonts via `<link>` tags
- Responsive design using Tailwind breakpoints (mobile-first)
- All original text content preserved exactly
- Original images referenced via absolute URLs from the client's site
- A working mobile hamburger menu via vanilla JavaScript
- Smooth scroll behavior and hover transitions on interactive elements

**Verify:** Open the generated HTML file in a browser at 1440px width. Check that:
- All original text content is present and unmodified
- The design looks polished, modern, and distinctive (not generic)
- Responsive breakpoints work (resize the browser to tablet and mobile)
- Images load correctly

**Iteration:** If the result isn't right, ask the agent to regenerate with feedback. Alternatively, edit the HTML directly — it's standard Tailwind.

### Step 3: Render and Screenshot

**Tool:** `tools/render_and_screenshot.py`

```bash
python tools/render_and_screenshot.py \
  --redesign-dir .tmp/redesign_clientsite_com \
  --original-dir .tmp/scrape_clientsite_com
```

**What it does:**
- Opens each HTML file in Chromium via Playwright
- Captures full-page screenshots at desktop (1440px), tablet (768px), and mobile (375px)
- Creates before/after comparison images (if original screenshots available)
- Saves to `.tmp/renders_{domain}/`

**Verify:** Check the comparison images in `.tmp/renders_{domain}/comparisons/` — these are great for proposals.

### Step 4: Export to Figma

**Tool:** `tools/export_to_figma.py`

#### Option A: Figma MCP Server (Best — editable layers)

If you have the Figma MCP server configured:

```bash
python tools/export_to_figma.py \
  --project-dir .tmp/redesign_clientsite_com \
  --method mcp --port 8080
```

This starts a local server. Then use the Figma MCP `generate_figma_design` tool to capture each page URL into Figma as editable vector layers.

**Figma MCP setup (one-time):**
```bash
claude mcp add --transport http figma https://mcp.figma.com/mcp
```

#### Option B: Screenshot Import (Simple — works immediately)

```bash
python tools/export_to_figma.py \
  --project-dir .tmp/redesign_clientsite_com \
  --renders-dir .tmp/renders_clientsite_com \
  --method screenshots
```

This generates:
- Design tokens JSON (importable via Figma "Design Tokens" plugin)
- Step-by-step instructions for manual import
- All screenshots organized by viewport

#### Option C: html.to.design Plugin

1. Open a redesigned HTML file in your browser
2. Use the [html.to.design](https://html.to.design) Figma plugin to capture the page
3. This creates editable Figma layers similar to the MCP approach

---

## Expected Outputs

After a full run, you'll have:

```
.tmp/
  scrape_{domain}/
    screenshots/         # Original site screenshots
    assets/              # Downloaded logo, hero images
    site_data.json       # Structured content + styles
  redesign_{domain}/
    pages/               # Generated HTML files (open in browser)
    figma/
      design_tokens.json
      export_instructions.md
  renders_{domain}/
    desktop/             # Desktop screenshots
    tablet/              # Tablet screenshots
    mobile/              # Mobile screenshots
    comparisons/         # Before/after side-by-side images
```

---

## Design Principles

These are the agent's design instructions. When generating a redesign, follow the selected style preset AND the general principles below.

### General Principles (apply to all styles)

**Anti-"AI Slop" Rules:**
- NEVER use Inter, Roboto, Arial, Open Sans, or system fonts — these scream generic AI output
- NEVER default to purple gradients on white backgrounds
- NEVER use evenly-distributed, timid color palettes — commit to a dominant color with sharp accents
- NEVER create cookie-cutter symmetric layouts with identical card grids
- Every page should feel like a human designer made bold, intentional choices

**Typography:**
- Choose distinctive Google Fonts that match the brand personality
- Modern sans-serif options: Space Grotesk, Clash Display, Cabinet Grotesk, Satoshi, General Sans, Outfit, Plus Jakarta Sans, Sora, Manrope
- Editorial/luxury options: Playfair Display, Fraunces, Lora, Cormorant, DM Serif Display
- Use dramatic size contrast between headings and body (hero headings: 56-96px, body: 16-18px)
- Letter-spacing adjustments on headings for visual impact

**Color Strategy:**
- Start from the client's existing brand colors (found in `site_data.json` > `raw_styles`)
- Elevate and modernize the palette — deeper, richer, more confident
- Define a clear hierarchy: dominant color, secondary, accent
- Use CSS custom properties for palette consistency across the page

**Layout:**
- Create visual rhythm through varied section heights and spacing
- Break away from uniform padding — some sections tight, some with generous breathing room
- Use overlapping elements, offset grids, or asymmetric arrangements for visual interest
- Full-bleed sections interspersed with contained content for pacing

**Motion & Interaction (CSS only):**
- Smooth hover transitions on buttons, links, and cards (0.2-0.3s ease)
- Subtle scale or shadow changes on card hover
- Smooth scroll behavior (`scroll-behavior: smooth`)
- Focus on one or two high-impact CSS animations (e.g., a hero fade-in) rather than scattering micro-interactions everywhere

**Images:**
- Reference original image URLs from the client's site using absolute URLs
- For decorative or background images the client doesn't have, use `https://placehold.co/{width}x{height}/{bg_hex}/{text_hex}` with colors from the palette
- Hero sections should use gradient overlays on top of images for text readability

**Technical Requirements:**
- Single self-contained HTML file per page
- Tailwind CSS via CDN: `<script src="https://cdn.tailwindcss.com"></script>`
- Google Fonts via `<link>` in `<head>`
- Inline `<style>` blocks only for custom animations or styles Tailwind can't handle
- Vanilla JavaScript for mobile menu toggle and any scroll interactions
- Mobile-first responsive design using Tailwind breakpoints (`sm:`, `md:`, `lg:`, `xl:`)
- Must look polished at 1440px width

**Content Rules:**
- Preserve ALL original text content exactly — headlines, body copy, CTAs, navigation items, footer text
- Do not invent, rewrite, or omit any text from the client's site
- Preserve the brand identity — reference the original logo and maintain brand recognition
- Only change the visual presentation, not the message

### Style Preset: Bold & Modern (default)

```
Direction: Confident, high-impact, contemporary
```

- Extra large, confident typography with dramatic size contrasts (hero headings 64-96px)
- High-contrast color palette — dominant dark or vibrant primary with sharp accent colors
- Generous whitespace and breathing room between sections
- Full-bleed hero sections with gradient overlays or bold background colors
- Card-based layouts with subtle shadows and hover lift effects
- Diagonal section dividers or overlapping elements for visual dynamism
- Modern UI patterns: floating/glassmorphism nav, sticky CTA bars, animated counters
- Dark sections alternating with light for visual rhythm

### Style Preset: Minimal & Clean

```
Direction: Refined, restrained, sophisticated
```

- Refined typography with elegant sans-serif fonts and generous letter-spacing
- Muted, restrained color palette — mostly neutrals with one carefully chosen accent
- Maximum whitespace — let the content breathe, less is more
- Thin borders and subtle dividers instead of heavy visual elements
- No gradients, minimal shadows — flat and clean
- Simple grid layouts with generous margins
- Understated hover effects (color shifts, underline animations)
- Focus on content hierarchy through typography and spacing alone

### Style Preset: Creative Agency

```
Direction: Editorial, artistic, boundary-pushing
```

- Mix of serif display fonts for headings and clean sans-serif for body
- Rich, layered color palette with unexpected accent combinations
- Asymmetric layouts that intentionally break the grid
- Large hero images or textured backgrounds
- Creative use of overlapping elements, text layered over images with blend modes
- Magazine-style editorial layouts for content sections
- Custom cursor effects and interactive hover states indicated in CSS
- Varied column widths and non-standard section compositions

---

## Edge Cases

- **Sites behind authentication** — Not supported. Scrape public pages only.
- **Single-page apps (React/Vue/Angular)** — Playwright handles JS rendering. The tool waits for hydration.
- **Very long pages (10,000px+)** — Screenshots may be very large. Consider splitting sections.
- **Non-English sites** — Fully supported. The tool preserves whatever text content is on the page.
- **Sites that block scrapers** — The tool uses a standard Chrome user agent. Most sites allow this. If blocked, provide screenshots manually.

## Known Limitations

- Redesign is visual only — no functional interactivity beyond CSS hover/transitions
- Generated HTML uses original image URLs — if those change, images will break
- Figma MCP capture requires a Figma Dev or Full seat
- Multi-page sites with shared layouts may have slight inconsistencies between pages — review for consistency

## Iteration

If the redesign quality isn't right:
1. **Ask the agent to regenerate** with specific feedback ("make the hero bolder", "use darker colors", "more whitespace")
2. **Try a different style** — switch from `bold-modern` to `creative-agency`
3. **Edit the HTML directly** — the generated files are standard HTML/Tailwind, easy to tweak by hand
4. **Re-run steps 3-4** after any changes to get updated screenshots and Figma exports

## Changelog

- 2026-03-06: Revised to agent-driven approach — no separate API calls, $0 per run
- 2026-03-04: Initial version — scrape, redesign, render, export pipeline
