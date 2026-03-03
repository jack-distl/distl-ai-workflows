# MCP Server + Google Ads Reporting — Implementation Plan

## Context

The team uses Claude Code (desktop app, cloud environment) conversationally — no terminal, no local tooling. The current Google Ads reporting skill is a manual Claude prompt where specialists provide context and data by hand. We want to automate the data pulls and Drive storage while keeping the specialist experience identical: they just talk to Claude.

Google Ads + Drive are the first integrations, but the team will grow to 10s of API credentials across different workflows. The MCP server we build here becomes the **central secure API gateway** for all of them — credentials never leave the server.

**Critical constraint:** API credentials must never exist in the Claude Code environment. Security is non-negotiable.

## Why the CLI Tools Don't Work

The Python CLI tools currently in `tools/` assume:
- Someone runs `pip install` and `python tools/...` from a terminal
- `.env` with Google credentials lives in the project directory
- `credentials.json` / `token.json` are on the local filesystem

None of that works for a cloud-based team that just talks to Claude. The credentials problem alone kills it — you can't store Google API tokens in a Claude Code sandbox.

## The Architecture: MCP Server

**MCP (Model Context Protocol)** is purpose-built for exactly this. An MCP server:
- Runs on **your infrastructure** (not in Claude Code)
- Holds all Google credentials server-side
- Exposes clean tool interfaces that Claude Code calls natively
- The team never sees credentials, API keys, or terminal commands

```
Specialist talks to Claude Code
    → Claude reads workflow SOP from the repo
    → Claude calls MCP tools (feels like native capabilities)
        → MCP server (your infrastructure) authenticates with Google
        → Returns data to Claude
    → Claude analyses, generates report
    → Claude calls MCP tool to save report to Drive
```

The specialist's experience: "Run the February report for Acme Corp" → Claude does everything.

## What Changes

| Component | Before (CLI tools) | After (MCP server) |
|-----------|-------------------|---------------------|
| Google API calls | Python scripts run locally | MCP server on your infrastructure |
| Credentials | `.env` in the repo | Server-side only, never exposed |
| Data processing | pandas in Claude Code sandbox | MCP returns structured data, Claude reasons over it |
| Team setup | `pip install`, configure `.env` | Just open the project (`.mcp.json` points to server) |
| Specialist experience | Would need to understand tooling | Just talks to Claude |

## What We Build

### 1. MCP Server — `server/` directory (Python, deployed separately)

A Python MCP server using the `mcp` SDK that wraps Google Ads API + Google Drive API. Lives in this repo for version control, gets deployed to Cloud Run.

**Google Ads tools exposed:**

| Tool | Inputs | Returns |
|------|--------|---------|
| `google_ads_list_accounts` | — | Accounts under MCC |
| `google_ads_campaign_performance` | customer_id, start_date, end_date | Campaign metrics as structured text |
| `google_ads_search_terms` | customer_id, start_date, end_date | Search terms + coverage % |
| `google_ads_keyword_performance` | customer_id, start_date, end_date | Keyword metrics + quality scores |
| `google_ads_change_history` | customer_id, start_date, end_date | Grouped change summary |

**Google Drive tools exposed:**

| Tool | Inputs | Returns |
|------|--------|---------|
| `drive_read_brief` | client_name | Brief content as text |
| `drive_save_brief` | client_name, content | Confirmation + file URL |
| `drive_get_latest_report` | client_name | Latest report content as text |
| `drive_save_report` | client_name, month, content | Confirmation + file URL |

**Key design decisions:**
- MCP tools return **structured text**, not raw CSVs — Claude reasons over it directly
- All cost_micros conversion happens server-side — Claude gets dollar amounts
- Search term coverage % calculated server-side
- Change history grouped and summarized server-side
- 30-day change history limit handled with a warning in the response
- Server manages Drive folder convention (creates client folders and reports subfolders automatically)

### 2. `.mcp.json` — repo root, shared via git

```json
{
  "mcpServers": {
    "google-ads-reporting": {
      "type": "http",
      "url": "${GOOGLE_ADS_MCP_URL}"
    }
  }
}
```

URL via environment variable — admin configures once per team member's machine. Specialists never touch it.

### 3. `workflows/google_ads_reporting.md` — revised SOP

Same 7-stage structure, references MCP tool names instead of CLI commands:

1. **Load context:** `drive_read_brief` + `drive_get_latest_report`
2. **Confirm brief:** Present to specialist (or gather if missing, then `drive_save_brief`)
3. **Pull data + context:** `google_ads_change_history` (auto), then ask specialist for external context only
4. **Pull metrics:** `google_ads_campaign_performance`, `google_ads_search_terms`, `google_ads_keyword_performance`
5. **Analyse:** Claude reasons over the data against goals (unchanged — this is what Claude does best)
6. **Generate + store report:** Write report, `drive_save_report`
7. **Update brief:** `drive_save_brief` if goals changed

### 4. File structure after changes

```
distl-ai-workflows/
  .mcp.json                              # Points Claude Code sessions at the MCP server
  CLAUDE.md                              # WAT framework instructions (updated)
  workflows/
    google_ads_reporting.md              # The SOP Claude follows
  server/                                # MCP server (deployed to Cloud Run)
    main.py                              # Entry point + tool registration (extensible)
    google_ads_tools.py                  # Google Ads API tools
    google_drive_tools.py                # Google Drive API tools
    requirements.txt                     # Server-side deps
    Dockerfile                           # Cloud Run deployment
    .env.example                         # Credential template (for local dev only)
```

**Designed to grow.** Adding a new API integration means:
1. Add `server/new_api_tools.py` with the tool functions
2. Register it in `main.py`
3. Add the credentials to Secret Manager
4. Redeploy

No changes needed in Claude Code, `.mcp.json`, or team setup — new tools appear automatically.

### 5. What gets removed

The CLI tools are replaced by the MCP server. All the GAQL queries, data parsing, and Drive logic from the existing files gets **moved into** the server — the logic is reused, just restructured.

Remove from repo root:
- `tools/` — entire directory (replaced by `server/`)
- `requirements.txt` — project-root version (moved to `server/`)
- Credential-related entries from `.env.example`

## Security Model

| Layer | Protection |
|-------|-----------|
| Credential storage | **Google Secret Manager** — not env vars. Versioned, auditable, per-secret access policies. Scales to 10s/100s of credentials. |
| Claude Code isolation | Zero credentials in Claude Code sessions — MCP server is the only thing that talks to external APIs |
| MCP server access | API key or OAuth — only authorized Claude Code sessions connect |
| Audit trail | Server logs every tool call with timestamp, tool name, and parameters |
| Rate limiting | Server-side limits per tool — prevents runaway API costs |
| Account isolation | Server can restrict which ad accounts / resources each session accesses |
| Network | HTTPS only via Cloud Run. Server is the only entry point to external APIs. |
| Adding new APIs | Same pattern every time: credentials go in Secret Manager, tool code goes in server, nothing changes in Claude Code |

## Build Order

| Phase | What | Depends on |
|-------|------|------------|
| 1 | MCP server scaffold (`server/main.py`) | — |
| 2 | Drive MCP tools (`server/google_drive_tools.py`) | Phase 1 |
| 3 | Ads MCP tools (`server/google_ads_tools.py`) | Phase 1 |
| 4 | `.mcp.json` + revised workflow SOP | Phases 2-3 |
| 5 | `Dockerfile` + `.env.example` for deployment | Phase 1 |
| 6 | Remove old `tools/` directory | Phase 4 |

## Deployment: Google Cloud Run + Secret Manager

**Cloud Run** for the server:
- Already in the Google ecosystem (Ads API, Drive API, MCC)
- Scales to zero — near-zero cost for monthly reporting usage
- HTTPS out of the box, no cert management
- Deploy from Dockerfile: `gcloud run deploy`
- No server to maintain

**Secret Manager** for credentials:
- All API keys, OAuth tokens, and refresh tokens stored as secrets
- Cloud Run accesses them natively at runtime (no env vars to manage)
- Per-secret IAM policies — control exactly which service can read which credential
- Audit log on every secret access
- Version history — roll back if a credential rotation goes wrong
- Scales to hundreds of secrets without configuration complexity

## Verification Plan

1. **Server standalone:** Run MCP server locally, call each tool via MCP inspector, verify correct responses
2. **Claude Code integration:** Point Claude Code at local server via `.mcp.json`, confirm tools appear and return data
3. **End-to-end:** Specialist says "run the report for Test Client, February 2026." Confirm full flow: brief loads, data pulls, report generates, report saves to Drive
4. **Security check:** Verify no credentials appear in Claude Code session logs or context
