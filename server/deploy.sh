#!/usr/bin/env bash
# -----------------------------------------------------------------
# Deploy MCP Server to Google Cloud Run
#
# Prerequisites:
#   - Google Cloud CLI (gcloud) installed and authenticated
#   - A GCP project with Cloud Run and Secret Manager enabled
#
# Usage:
#   ./deploy.sh                  # First-time setup + deploy
#   ./deploy.sh --update-only    # Just rebuild and redeploy
# -----------------------------------------------------------------

set -euo pipefail

# ----- Configuration (edit these) -----
PROJECT_ID="${GCP_PROJECT_ID:?Set GCP_PROJECT_ID environment variable}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="distl-mcp-server"
# --------------------------------------

echo ""
echo "=================================="
echo "  MCP Server Deploy"
echo "=================================="
echo ""
echo "Project:  $PROJECT_ID"
echo "Region:   $REGION"
echo "Service:  $SERVICE_NAME"
echo ""

# --- Helper ---
secret_exists() {
    gcloud secrets describe "$1" --project="$PROJECT_ID" &>/dev/null
}

create_or_update_secret() {
    local name="$1"
    local prompt_text="$2"

    if secret_exists "$name"; then
        echo "Secret '$name' already exists."
        read -rp "  Update it? (y/N): " update
        if [[ "$update" =~ ^[Yy]$ ]]; then
            read -rsp "  New value for $name: " value
            echo ""
            echo -n "$value" | gcloud secrets versions add "$name" \
                --project="$PROJECT_ID" --data-file=-
            echo "  Updated."
        fi
    else
        read -rsp "$prompt_text" value
        echo ""
        echo -n "$value" | gcloud secrets create "$name" \
            --project="$PROJECT_ID" \
            --replication-policy="automatic" \
            --data-file=-
        echo "  Created."
    fi
}

# --- First-time setup ---
if [[ "${1:-}" != "--update-only" ]]; then
    echo "--- Setting up secrets in Google Secret Manager ---"
    echo ""
    echo "These are stored securely in Google's infrastructure."
    echo "They are never written to disk or checked into Git."
    echo ""

    create_or_update_secret "mcp-api-key" \
        "MCP API Key (the shared password for the server): "

    create_or_update_secret "google-ads-developer-token" \
        "Google Ads Developer Token: "

    create_or_update_secret "google-ads-client-id" \
        "Google Ads Client ID: "

    create_or_update_secret "google-ads-client-secret" \
        "Google Ads Client Secret: "

    create_or_update_secret "google-ads-refresh-token" \
        "Google Ads Refresh Token: "

    create_or_update_secret "google-ads-login-customer-id" \
        "Google Ads Login Customer ID (MCC, no dashes): "

    create_or_update_secret "google-drive-root-folder-id" \
        "Google Drive Root Folder ID: "

    echo ""
    echo "--- Secrets configured ---"
    echo ""
fi

# --- Build and deploy ---
echo "--- Building and deploying to Cloud Run ---"
echo ""

gcloud run deploy "$SERVICE_NAME" \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --source=. \
    --port=8000 \
    --no-allow-unauthenticated \
    --set-secrets="\
MCP_API_KEY=mcp-api-key:latest,\
GOOGLE_ADS_DEVELOPER_TOKEN=google-ads-developer-token:latest,\
GOOGLE_ADS_CLIENT_ID=google-ads-client-id:latest,\
GOOGLE_ADS_CLIENT_SECRET=google-ads-client-secret:latest,\
GOOGLE_ADS_REFRESH_TOKEN=google-ads-refresh-token:latest,\
GOOGLE_ADS_LOGIN_CUSTOMER_ID=google-ads-login-customer-id:latest,\
GOOGLE_DRIVE_ROOT_FOLDER_ID=google-drive-root-folder-id:latest" \
    --min-instances=0 \
    --max-instances=3 \
    --memory=512Mi \
    --timeout=120

echo ""
echo "--- Deploy complete ---"
echo ""

# Get the URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" \
    --project="$PROJECT_ID" \
    --region="$REGION" \
    --format="value(status.url)")

echo "Your MCP server is live at:"
echo "  $SERVICE_URL"
echo ""
echo "Give your team these two values:"
echo "  DISTL_MCP_SERVER_URL=$SERVICE_URL/mcp/"
echo "  DISTL_MCP_API_KEY=(the password you set for mcp-api-key)"
echo ""
