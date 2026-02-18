# mcp_client.py

import subprocess
import json
import threading
import sys
from pathlib import Path

SERVER_CMD = [
    "/Users/saketh/Documents/Resume Prep/AI Engineer Ramp-Up/mcp/file-system-mcp/.venv/bin/python",
    "/Users/saketh/Documents/Resume Prep/AI Engineer Ramp-Up/mcp/file-system-mcp/main.py",
]

def send(proc, payload):
    message = json.dumps(payload)
    proc.stdin.write(message + "\n")
    proc.stdin.flush()

def read_loop(proc):
    for line in proc.stdout:
        print("SERVER:", line.strip())

def main():
    proc = subprocess.Popen(
        SERVER_CMD,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    threading.Thread(target=read_loop, args=(proc,), daemon=True).start()

    # 1️⃣ Initialize
    send(proc, {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "manual-client", "version": "0.1"}
        }
    })

    # 2️⃣ List tools
    send(proc, {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    })

    # 3️⃣ Call list_files
    send(proc, {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "list_files",
            "arguments": {
                "subfolder": ""
            }
        }
    })

    proc.wait()

if __name__ == "__main__":
    main()
