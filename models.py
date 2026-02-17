from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field


class ToolError(BaseModel):
    """
    Standard error object returned by all tools.
    """
    code: str = Field(..., description="Machine-readable error code (e.g., PATH_OUTSIDE_BASE).")
    message: str = Field(..., description="Human-readable error message.")
    path: Optional[str] = Field(None, description="The user-supplied path (if applicable).")
    details: Optional[Dict[str, Any]] = Field(None, description="Optional extra fields for debugging/clients.")


class DirEntry(BaseModel):
    name: str = Field(..., description="Filename or directory name (no path).")
    is_dir: bool = Field(..., description="True if entry is a directory.")
    size_bytes: Optional[int] = Field(None, description="Size in bytes for files; null for directories.")


class ListFilesData(BaseModel):
    folder: str = Field(..., description="Folder path relative to ~/mcp_notes that was listed.")
    entries: List[DirEntry] = Field(..., description="Directory entries.")


class ReadFileData(BaseModel):
    path: str = Field(..., description="File path relative to ~/mcp_notes.")
    size_bytes: int = Field(..., description="File size in bytes.")
    content: str = Field(..., description="UTF-8 decoded text content.")


class WriteFileData(BaseModel):
    path: str = Field(..., description="File path relative to ~/mcp_notes.")
    bytes_written: int = Field(..., description="Number of bytes written.")


class MkdirData(BaseModel):
    folder: str = Field(..., description="Folder path relative to ~/mcp_notes that was created/ensured.")


class ListFilesResult(BaseModel):
    ok: bool
    data: Optional[ListFilesData] = None
    error: Optional[ToolError] = None


class ReadFileResult(BaseModel):
    ok: bool
    data: Optional[ReadFileData] = None
    error: Optional[ToolError] = None


class WriteFileResult(BaseModel):
    ok: bool
    data: Optional[WriteFileData] = None
    error: Optional[ToolError] = None


class MkdirResult(BaseModel):
    ok: bool
    data: Optional[MkdirData] = None
    error: Optional[ToolError] = None
