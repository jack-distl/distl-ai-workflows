"""MCP server entry point. Registers all tool modules and starts the server.

Run locally:
    cd server && python main.py

Deploy to Cloud Run:
    See Dockerfile and deploy instructions in this directory.
"""

import logging
import os

# Configure logging before importing tool modules
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)

# Import the shared server instance
from app import mcp  # noqa: E402

# Import tool modules to register their @mcp.tool() decorators
import google_ads_tools  # noqa: E402, F401
import google_drive_tools  # noqa: E402, F401

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
    )
