# File System MCP -- Learning Summary

## Overview

Built a secure MCP (Model Context Protocol) server and a minimal MCP
client to understand:

-   JSON-RPC mechanics\
-   Tool registration & introspection\
-   Protocol vs application-level errors\
-   Transport abstraction (stdio)\
-   Secure sandbox design for AI tool execution

Goal: move beyond "using tools" and understand how model-tool systems
actually work.

------------------------------------------------------------------------

## What Is MCP?

MCP is a **JSON-RPC--based protocol** that allows models (e.g., Claude)
to call external tools.

Basic flow:

1.  Client sends `initialize`
2.  Server advertises capabilities
3.  Client calls `tools/list`
4.  Client calls `tools/call`
5.  Server returns model-consumable content blocks

MCP is: - Transport-agnostic - Self-describing - Extensible - Designed
for model integration

------------------------------------------------------------------------

## MCP Server

Implemented a filesystem MCP server restricted to:

    ~/mcp_notes

### Security Model

-   Reject absolute paths\
-   Normalize paths using `Path.resolve()`\
-   Enforce containment with `is_relative_to(BASE_DIR)`\
-   Block directory traversal (`../../`)\
-   Prevent writes outside sandbox

### Tools Implemented

-   `list_files`
-   `read_file`
-   `write_file`
-   `mkdir`

All tools: - Return structured `{ ok, data?, error? }` - Convert
exceptions into structured error objects - Auto-registered via
`@mcp.tool()`

------------------------------------------------------------------------

## MCP Client

Built a minimal client using:

-   `subprocess.Popen`
-   stdio transport
-   Manual JSON-RPC messages

Client performs:

-   `initialize`
-   `tools/list`
-   `tools/call`

This demonstrated that Claude Desktop simply: - Spawns the client -
Sends JSON-RPC messages - Displays results

------------------------------------------------------------------------

## Tool Response Structure

Tool results are wrapped as MCP content blocks:

``` json
{
  "result": {
    "content": [
      { "type": "text", "text": "{ ... tool JSON ... }" }
    ],
    "isError": false
  }
}
```

Key insight: MCP returns **model-consumable content**, not raw JSON.

------------------------------------------------------------------------

## Error Layers

### Protocol-Level Errors

Failures in JSON-RPC or transport: - Invalid JSON - Unknown method -
Server crash

### Application-Level Errors

Valid RPC call, but tool logic rejects input: - Invalid path - File not
found - Permission denied

------------------------------------------------------------------------

## Transport vs Protocol

MCP is **transport-agnostic**.

This project used: - `stdio`

But it could run over: - WebSocket - TCP - HTTP

Protocol stays the same. Only transport changes.

------------------------------------------------------------------------

## Key Takeaways

-   MCP is structured JSON-RPC for model-tool interaction
-   Servers are self-describing via `tools/list`
-   Tool results are designed for LLM consumption
-   Error handling is layered
-   Secure sandboxing is critical for tool safety
-   Claude Desktop is just a JSON-RPC client

This project clarified how modern AI runtimes integrate external
capabilities safely and systematically.
