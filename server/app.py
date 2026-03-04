"""Shared FastMCP server instance. Import this in all tool modules."""

from fastmcp import FastMCP

mcp = FastMCP(
    name="distl-reporting",
    version="1.0.0",
)
