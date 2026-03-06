"""MCP server entry point. Registers all tool modules and starts the server.

Run locally (dev mode, auth disabled):
    MCP_AUTH_DISABLED=true cd server && python main.py

Run locally (with auth):
    MCP_API_KEY=your-secret-key cd server && python main.py

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

# Import security to register auth middleware
from security import verify_api_key  # noqa: E402

logger = logging.getLogger(__name__)


# --- Authentication Middleware ---
# FastMCP uses Starlette under the hood for HTTP transport.
# We add ASGI middleware that checks the Authorization header
# before any request reaches the MCP tool handlers.


class APIKeyAuthMiddleware:
    """ASGI middleware that requires a valid Bearer token on every request.

    Checks the Authorization header against the MCP_API_KEY env var.
    Health check endpoints (/) are exempt for Cloud Run probes.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")

            # Allow health checks through (Cloud Run readiness probes)
            if path == "/" or path == "/health":
                await self.app(scope, receive, send)
                return

            # Extract Authorization header
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"authorization", b"").decode()

            # Expect "Bearer <token>"
            token = ""
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]

            if not verify_api_key(token):
                # Return 401 Unauthorized
                response_body = b'{"error": "Unauthorized"}'
                await send({
                    "type": "http.response.start",
                    "status": 401,
                    "headers": [
                        [b"content-type", b"application/json"],
                        [b"content-length", str(len(response_body)).encode()],
                    ],
                })
                await send({
                    "type": "http.response.body",
                    "body": response_body,
                })
                logger.warning("Rejected unauthorized request to %s", path)
                return

        await self.app(scope, receive, send)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))

    # Get the underlying ASGI app from FastMCP and wrap it with auth
    asgi_app = mcp.get_asgi_app(
        transport="streamable-http",
        host="0.0.0.0",
        port=port,
    )

    # Wrap with auth middleware
    authed_app = APIKeyAuthMiddleware(asgi_app)

    # Run with uvicorn
    import uvicorn
    uvicorn.run(authed_app, host="0.0.0.0", port=port)
