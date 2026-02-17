from __future__ import annotations

from typing import Optional
from mcp.server.fastmcp import FastMCP

from path_safety import resolve_safe_path, BASE_DIR
from models import (
    ToolError,
    DirEntry,
    ListFilesData,
    ReadFileData,
    WriteFileData,
    MkdirData,
    ListFilesResult,
    ReadFileResult,
    WriteFileResult,
    MkdirResult,
)

mcp = FastMCP("file-system-mcp")


def _rel_str(p):
    """Convert an absolute path under BASE_DIR to a relative string."""
    return str(p.relative_to(BASE_DIR.resolve()))


def _err(code: str, message: str, path: Optional[str] = None, details: Optional[dict] = None) -> ToolError:
    return ToolError(code=code, message=message, path=path, details=details)


@mcp.tool()
def list_files(subfolder: str = "") -> dict:
    """
    List files and directories inside a subfolder of ~/mcp_notes.

    Paths are always interpreted as relative to ~/mcp_notes and cannot escape that directory.

    Args:
        subfolder: Relative folder path (e.g. "notes" or "").

    Returns:
        { ok, data?, error? }
        data = { folder, entries: [{ name, is_dir, size_bytes? }, ...] }

    Examples:
        - list_files("") -> lists ~/mcp_notes
        - list_files("projects/2026") -> lists ~/mcp_notes/projects/2026
    """
    try:
        folder_path = resolve_safe_path(subfolder)

        if not folder_path.exists():
            return ListFilesResult(ok=False, error=_err("NOT_FOUND", "Folder does not exist.", subfolder)).model_dump()

        if not folder_path.is_dir():
            return ListFilesResult(ok=False, error=_err("NOT_A_DIRECTORY", "Provided path is not a directory.", subfolder)).model_dump()

        entries = []
        for item in folder_path.iterdir():
            entries.append(
                DirEntry(
                    name=item.name,
                    is_dir=item.is_dir(),
                    size_bytes=item.stat().st_size if item.is_file() else None,
                )
            )

        data = ListFilesData(folder=_rel_str(folder_path), entries=entries)
        return ListFilesResult(ok=True, data=data).model_dump()

    except ValueError as e:
        return ListFilesResult(ok=False, error=_err("PATH_INVALID", str(e), subfolder)).model_dump()
    except PermissionError as e:
        return ListFilesResult(ok=False, error=_err("PERMISSION_DENIED", "Permission denied.", subfolder)).model_dump()
    except OSError as e:
        # Catch-all for filesystem issues
        return ListFilesResult(ok=False, error=_err("IO_ERROR", "Filesystem error.", subfolder, {"errno": getattr(e, "errno", None)})).model_dump()


@mcp.tool()
def read_file(relative_path: str) -> dict:
    """
    Read a UTF-8 text file inside ~/mcp_notes.

    Args:
        relative_path: Relative file path (e.g. "notes/today.txt").

    Returns:
        { ok, data?, error? }
        data = { path, size_bytes, content }

    Examples:
        - read_file("notes/today.txt")
    """
    try:
        file_path = resolve_safe_path(relative_path)

        if not file_path.exists():
            return ReadFileResult(ok=False, error=_err("NOT_FOUND", "File does not exist.", relative_path)).model_dump()

        if not file_path.is_file():
            return ReadFileResult(ok=False, error=_err("NOT_A_FILE", "Provided path is not a file.", relative_path)).model_dump()

        # Read UTF-8 text; if you want binary support, add a separate tool
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ReadFileResult(
                ok=False,
                error=_err("DECODE_ERROR", "File is not valid UTF-8 text.", relative_path),
            ).model_dump()

        data = ReadFileData(path=_rel_str(file_path), size_bytes=file_path.stat().st_size, content=content)
        return ReadFileResult(ok=True, data=data).model_dump()

    except ValueError as e:
        return ReadFileResult(ok=False, error=_err("PATH_INVALID", str(e), relative_path)).model_dump()
    except PermissionError:
        return ReadFileResult(ok=False, error=_err("PERMISSION_DENIED", "Permission denied.", relative_path)).model_dump()
    except OSError as e:
        return ReadFileResult(ok=False, error=_err("IO_ERROR", "Filesystem error.", relative_path, {"errno": getattr(e, "errno", None)})).model_dump()


@mcp.tool()
def write_file(relative_path: str, content: str) -> dict:
    """
    Write UTF-8 text to a file inside ~/mcp_notes.

    Creates parent directories if needed.

    Args:
        relative_path: Relative file path (e.g. "notes/today.txt").
        content: Text content to write (UTF-8).

    Returns:
        { ok, data?, error? }
        data = { path, bytes_written }

    Examples:
        - write_file("notes/today.txt", "Hello MCP")
        - write_file("projects/2026/plan.md", "# Plan\\n...")
    """
    try:
        file_path = resolve_safe_path(relative_path)

        # Ensure parent directories exist
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return WriteFileResult(
                ok=False,
                error=_err("IO_ERROR", "Failed to create parent directories.", relative_path, {"errno": getattr(e, "errno", None)}),
            ).model_dump()

        # Write text
        try:
            bytes_written = file_path.write_text(content, encoding="utf-8")
        except OSError as e:
            return WriteFileResult(
                ok=False,
                error=_err("IO_ERROR", "Failed to write file.", relative_path, {"errno": getattr(e, "errno", None)}),
            ).model_dump()

        data = WriteFileData(path=_rel_str(file_path), bytes_written=bytes_written)
        return WriteFileResult(ok=True, data=data).model_dump()

    except ValueError as e:
        return WriteFileResult(ok=False, error=_err("PATH_INVALID", str(e), relative_path)).model_dump()
    except PermissionError:
        return WriteFileResult(ok=False, error=_err("PERMISSION_DENIED", "Permission denied.", relative_path)).model_dump()


@mcp.tool()
def mkdir(relative_path: str) -> dict:
    """
    Create a directory inside ~/mcp_notes.

    Creates intermediate directories if necessary.

    Args:
        relative_path: Relative directory path (e.g. "projects/2026").

    Returns:
        { ok, data?, error? }
        data = { folder }

    Examples:
        - mkdir("projects/2026")
        - mkdir("notes/daily/2026-02")
    """
    try:
        folder_path = resolve_safe_path(relative_path)

        try:
            folder_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return MkdirResult(
                ok=False,
                error=_err("IO_ERROR", "Failed to create directory.", relative_path, {"errno": getattr(e, "errno", None)}),
            ).model_dump()

        data = MkdirData(folder=_rel_str(folder_path))
        return MkdirResult(ok=True, data=data).model_dump()

    except ValueError as e:
        return MkdirResult(ok=False, error=_err("PATH_INVALID", str(e), relative_path)).model_dump()
    except PermissionError:
        return MkdirResult(ok=False, error=_err("PERMISSION_DENIED", "Permission denied.", relative_path)).model_dump()
