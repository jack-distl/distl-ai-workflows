# MCP Server Setup & Team Onboarding

## Overview

The MCP server lives in Google Cloud Run. It holds all sensitive credentials (Google Ads, Drive, etc.) so that team members never need access to them directly. The server is protected by a shared API key — a password that every request must include or it gets rejected.

All secrets are stored in Google Secret Manager. Nothing sensitive is in GitHub or in any file that gets shared.

---

## First-Time Server Deployment (Admin Only)

### Prerequisites

- Google Cloud CLI (`gcloud`) installed and authenticated
- A GCP project with Cloud Run and Secret Manager APIs enabled

### Steps

1. Open a terminal and go to the `server/` folder

2. Run the deploy script:
   ```
   GCP_PROJECT_ID=your-google-project-id ./deploy.sh
   ```

3. It will walk you through each value it needs:
   - **MCP API Key** — make up a long random password. You can generate one with:
     ```
     python3 -c "import secrets; print(secrets.token_urlsafe(32))"
     ```
   - **Google Ads Developer Token**
   - **Google Ads Client ID**
   - **Google Ads Client Secret**
   - **Google Ads Refresh Token**
   - **Google Ads Login Customer ID** (the MCC account ID, no dashes)
   - **Google Drive Root Folder ID**

4. The script stores all of these in Google Secret Manager (not in any file) and deploys the server

5. When it finishes, it prints the server URL. **Save this URL and the API key you chose.** You will give these to your team.

### Redeploying After Code Changes

If you update the server code and just need to redeploy (no secret changes):

```
GCP_PROJECT_ID=your-google-project-id ./deploy.sh --update-only
```

### Updating a Secret

Run the full deploy script (without `--update-only`). It will ask you for each secret whether you want to update it. Say yes only for the ones you want to change.

---

## Team Member Onboarding

### What You Give Them

Two values:
- **MCP Server URL** — the URL from the deploy step
- **MCP API Key** — the password you chose during deploy

### What They Do

1. Clone the repo
2. Run the setup script from the project root:
   ```
   ./setup.sh
   ```
3. It asks four questions:
   - **MCP Server URL** — paste what you gave them
   - **MCP API Key** — paste what you gave them
   - **OpenAI API Key** — their own key (or leave blank if not needed yet)
   - **Google API Key** — their own key (or leave blank if not needed yet)

4. Done. The script creates their `.env` file. This file is in `.gitignore` so it never gets uploaded to GitHub.

---

## When Someone Leaves the Team

1. Generate a new API key:
   ```
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. Update the server with the new key:
   ```
   cd server
   GCP_PROJECT_ID=your-google-project-id ./deploy.sh
   ```
   When it asks about `mcp-api-key`, say yes and paste the new key. Skip the rest.

3. Tell remaining team members to run `./setup.sh` again with the new API key.

---

## Adding a New MCP Server in the Future

If you build a second MCP server (e.g. for Slack, email, or another service):

1. Deploy it the same way — it gets its own URL and its own API key

2. Add it to `.mcp.json` in the project root:
   ```json
   {
     "mcpServers": {
       "distl-reporting": {
         "type": "http",
         "url": "${DISTL_MCP_SERVER_URL}",
         "headers": {
           "Authorization": "Bearer ${DISTL_MCP_API_KEY}"
         }
       },
       "new-server-name": {
         "type": "http",
         "url": "${NEW_SERVER_URL}",
         "headers": {
           "Authorization": "Bearer ${NEW_SERVER_API_KEY}"
         }
       }
     }
   }
   ```

3. Add the new env vars to `.env.example` so the setup script (or team members manually) can fill them in

4. Give the team the new URL and key

Each server has its own password. If one gets compromised, the others are unaffected.

---

## How Security Works

- **Credentials never leave the server.** Google Ads tokens, Drive service account keys — all stored in Google Secret Manager. A team member's laptop getting stolen doesn't compromise your Google accounts.

- **The API key is a gate, not a skeleton key.** Even with it, someone can only use the specific tools you've built (pull reports, read briefs, etc.). They can't run arbitrary queries or access other Google services.

- **Input validation blocks bad data.** Dates must be real dates. Customer IDs must be digits. Client names are restricted to normal characters. Malformed input gets rejected before it reaches any Google API.

- **Error messages don't leak internals.** If something breaks, the caller sees a generic message. Full details are in the server logs only.

- **Every tool call is logged.** The audit logger records what tool was called and with what parameters, so you can review usage anytime.

---

## Quick Reference

| Task | Command |
|------|---------|
| Deploy server (first time) | `cd server && GCP_PROJECT_ID=xxx ./deploy.sh` |
| Redeploy after code changes | `cd server && GCP_PROJECT_ID=xxx ./deploy.sh --update-only` |
| Set up a team member | Team member runs `./setup.sh` from project root |
| Generate a new API key | `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |
| Rotate API key after someone leaves | Update secret via deploy script, team re-runs `./setup.sh` |
