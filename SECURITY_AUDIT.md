# Security Audit Report

**Date:** 2026-03-06
**Scope:** Full codebase — tools/, server/, workflows/, configuration files

---

## Executive Summary

This audit identified **2 CRITICAL**, **4 HIGH**, **9 MEDIUM**, and **14 LOW** severity findings across the codebase. The most urgent issues are a vulnerable Pillow dependency that enables remote code execution via malicious images (directly relevant since this project scrapes untrusted websites), HTTP servers binding to all network interfaces, and an authentication bypass flag with no environment guard.

No command injection, SQL injection, XSS, hardcoded credentials, or unsafe deserialization was found.

---

## CRITICAL Findings

### C1: Pillow version allows CVE-2026-25990 (RCE via malicious images)
- **File:** `requirements.txt:2`
- **Detail:** `Pillow>=10.0.0` allows installation of versions affected by an out-of-bounds write in the PSD handler (affects 10.3.0 through 12.1.0). This is an RCE-class vulnerability. Since this project scrapes external websites and processes their images, it is directly exposed.
- **Fix:** Pin `Pillow>=12.1.1`

### C2: HTTP servers bound to 0.0.0.0 expose local files to the network
- **Files:** `tools/render_and_screenshot.py:47`, `tools/export_to_figma.py:228`
- **Detail:** Both tools start `SimpleHTTPRequestHandler` servers bound to `""` (all interfaces). Any files in the served directory become accessible to anyone on the network, including directory listing. These directories may contain scraped site data, design tokens, and generated HTML.
- **Fix:** Change `("", port)` to `("127.0.0.1", port)` in both files

---

## HIGH Findings

### H1: MCP_AUTH_DISABLED bypasses all authentication without safeguard
- **File:** `server/security.py:38-39`
- **Detail:** Setting `MCP_AUTH_DISABLED=true` bypasses all API key authentication. If this is accidentally set in production, the entire MCP server is unauthenticated. There is no secondary guard (e.g., requiring `ENVIRONMENT=development`).
- **Fix:** Only honor `MCP_AUTH_DISABLED` when `ENVIRONMENT=development` is also set

### H2: setup.sh echoes secrets to terminal
- **File:** `setup.sh:38-44`
- **Detail:** Secrets (MCP API Key, OpenAI API Key, Google API Key) are read with `read -rp` which echoes input to the terminal. The script comments claim "they won't be visible as you type" — this is incorrect. Only `read -rsp` suppresses echo.
- **Fix:** Change to `read -rsp` for all secret inputs, add `echo ""` after each read

### H3: SSRF in scrape_website.py — no URL validation
- **File:** `tools/scrape_website.py:227,265,357`
- **Detail:** The `--url` argument is passed directly to `requests.head()`, `page.goto()`, and asset URLs are fetched with `requests.get()` with no validation. URLs like `http://169.254.169.254/latest/meta-data/` (AWS metadata), `http://localhost:xxxx`, or `file:///etc/passwd` could probe internal services.
- **Fix:** Validate URLs against an allowlist of schemes (http/https only), resolve hostnames, and block private/reserved IP ranges (10.x, 172.16-31.x, 192.168.x, 127.x, 169.254.x)

### H4: .env file created with world-readable permissions
- **File:** `setup.sh:48-57`
- **Detail:** The `.env` file is created with default umask permissions (typically 644), making API keys readable by any user on the system.
- **Fix:** Add `chmod 600 "$ENV_FILE"` after creation, or set `umask 077` before writing

---

## MEDIUM Findings

### M1: WebSocket connections bypass authentication
- **File:** `server/main.py:52,87`
- **Detail:** Auth middleware only checks `scope["type"] == "http"`. WebSocket connections pass through unauthenticated.
- **Fix:** Add explicit WebSocket auth check or reject WebSocket scope

### M2: No rate limiting on MCP server
- **File:** `server/main.py`
- **Detail:** No rate limiting on API endpoints. A compromised or abused API key could exhaust Google Ads/Drive API quotas.
- **Fix:** Add rate limiting middleware (e.g., `slowapi`)

### M3: Docker container runs as root
- **File:** `server/Dockerfile`
- **Detail:** No `USER` directive — application runs as root inside the container.
- **Fix:** Add `RUN useradd --create-home appuser` and `USER appuser`

### M4: Unpinned dependency versions (server)
- **File:** `server/requirements.txt`
- **Detail:** All server dependencies use `>=` without upper bounds. Builds are not reproducible and vulnerable to supply chain attacks.
- **Fix:** Use a lockfile (`pip freeze > requirements.lock`) or pin exact versions

### M5: No authorization boundaries on Drive operations
- **File:** `server/google_drive_tools.py:189-351`
- **Detail:** Any authenticated MCP client can read/write to any client folder. No per-client authorization exists.
- **Fix:** Implement per-user authorization if multi-tenant access is planned

### M6: .gitignore missing critical patterns
- **File:** `.gitignore`
- **Detail:** Missing entries for `*.pem`, `*.key`, `.env.*` variants, `venv/`, `.venv/`
- **Fix:** Add `*.pem`, `*.key`, `*.p12`, `.env.*`, `venv/`, `.venv/`

### M7: Shell expansion corrupts secrets with metacharacters
- **File:** `setup.sh:50-56`
- **Detail:** Unquoted heredoc (`<<EOF`) means if a user pastes an API key containing `$`, backticks, or `!`, the value is interpreted by the shell rather than written literally.
- **Fix:** Use `<<'EOF'` (quoted heredoc) and inject values with `sed` or `printf`

### M8: Path traversal via CLI arguments (tools)
- **Files:** `tools/scrape_website.py:396`, `tools/render_and_screenshot.py:190,213`, `tools/export_to_figma.py:243,251`
- **Detail:** `--output-dir`, `--redesign-dir`, and `--project-dir` arguments are used without path validation. Arbitrary directories can be read from or written to.
- **Fix:** Validate that resolved paths are within expected working directories

### M9: MCP API key shared without secure channel guidance
- **File:** `workflows/server_setup_and_team_onboarding.md:63-64`
- **Detail:** No secure channel specified for transmitting the shared API key to team members.
- **Fix:** Add guidance to use a password manager shared vault or one-time secret sharing service

---

## LOW Findings

| # | File | Issue |
|---|------|-------|
| L1 | `tools/scrape_website.py:232` | Unsanitized filenames from remote URLs |
| L2 | `tools/scrape_website.py:57-64` | Broad exception handling hides security errors |
| L3 | `tools/render_and_screenshot.py:187` | No port range validation |
| L4 | `tools/render_and_screenshot.py:138` | Potential Pillow decompression bomb |
| L5 | `tools/export_to_figma.py:49` | Sensitive data may propagate via design tokens |
| L6 | `server/security.py:19-27` | API key cached globally, never refreshed |
| L7 | `server/security.py:50` | Client name regex allows potentially dangerous chars |
| L8 | `server/google_ads_tools.py:613` | User emails exposed in change history output |
| L9 | `server/google_drive_tools.py:227` | No file size limits on uploads |
| L10 | `server/google_drive_tools.py:306` | Month parameter not format-validated |
| L11 | `server/date_utils.py:7` | No input validation on date parsing |
| L12 | `server/requirements.txt` | No pinned secret versions in deploy |
| L13 | `.env.example:13` | Placeholder token value instead of empty string |
| L14 | `workflows/website_redesign_concept.md:229` | Client image URLs leak IP during proposal viewing |

---

## Positive Findings

These security best practices were observed:

- **No hardcoded credentials** — all secrets loaded from environment variables
- **No command injection** — no `subprocess`, `os.system`, or `shell=True` usage
- **No unsafe deserialization** — no `pickle`, `yaml.load`, or `eval`
- **No SQL injection** — GAQL queries use validated inputs
- **deploy.sh reads secrets silently** — uses `read -rsp` and pipes directly to GCP Secret Manager
- **Cloud Run configured with `--no-allow-unauthenticated`** — defense-in-depth
- **Error messages are generic** — stack traces logged server-side only, not returned to callers
- **.env.example contains no real secrets** — all values are empty/placeholder

---

## Recommended Fix Priority

| Priority | Findings | Effort |
|----------|----------|--------|
| **Immediate** | C1 (Pillow CVE), C2 (bind to localhost) | < 1 hour |
| **This week** | H1 (auth bypass guard), H2 (setup.sh echo), H3 (SSRF), H4 (.env perms) | 2-4 hours |
| **This sprint** | M1-M4 (WebSocket auth, rate limiting, Docker user, dep pinning) | 1-2 days |
| **Backlog** | M5-M9, all LOW findings | As capacity allows |

---

## How to Use This Report

1. Start with **Immediate** items — they are quick wins with the highest impact
2. Address **HIGH** items before any production deployment
3. Schedule **MEDIUM** items into sprint planning
4. Track **LOW** items in the backlog and address opportunistically
