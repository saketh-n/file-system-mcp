from pathlib import Path

BASE_DIR = (Path.home() / "mcp_notes")
BASE_DIR.mkdir(parents=True, exist_ok=True)


def resolve_safe_path(relative_path: str) -> Path:
    """
    Resolve a user-provided path safely within BASE_DIR.

    Rules:
      - Only relative paths allowed
      - Final resolved path must remain inside BASE_DIR
    """
    base = BASE_DIR.resolve()

    if relative_path is None or relative_path == "":
        return base

    rel = Path(relative_path)

    if rel.is_absolute():
        raise ValueError("Absolute paths are not allowed.")

    full = (base / rel).resolve()

    # Python 3.9+: proper path containment check
    if not full.is_relative_to(base):
        raise ValueError("Access denied: path outside ~/mcp_notes")

    return full
