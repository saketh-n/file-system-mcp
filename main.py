# main.py
from __future__ import annotations

import sys
from pathlib import Path

from path_safety import BASE_DIR  # ensures consistent base dir module-wide
from server import mcp            # importing server registers all @mcp.tool() functions


def main() -> None:
    """
    Entry point for file-system-mcp.

    Startup flow:
      1) Ensure ~/mcp_notes exists
      2) Import and register tools (happens when importing `server`)
      3) Start the MCP server loop (blocks forever waiting for requests)

    When running correctly, the process will appear to "hang" in the terminal.
    That's expected: it's waiting for MCP client requests.
    """
    # Ensure base directory exists (path_safety also does this, but it doesn't hurt to be explicit)
    Path(BASE_DIR).mkdir(parents=True, exist_ok=True)

    # Optional: print where we're rooted (helpful for debugging)
    print(f"[file-system-mcp] Root directory: {BASE_DIR}", file=sys.stderr)

    # Start the server loop (this blocks)
    mcp.run()


if __name__ == "__main__":
    main()
