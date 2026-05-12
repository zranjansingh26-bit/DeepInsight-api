"""
DeepInsight Starter Suite — File Parser Engine.

Parses uploaded CSV, XLSX, and JSON files into pandas DataFrames
with validation, error handling, and size limits.
"""

import io
import logging
from typing import Optional

import pandas as pd
from fastapi import UploadFile

from config import get_settings

logger = logging.getLogger(__name__)

# Supported extensions
SUPPORTED_EXTENSIONS = {"csv", "xlsx", "xls", "json"}

# Content-type mapping
CONTENT_TYPE_MAP = {
    "csv": "text/csv",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "xls": "application/vnd.ms-excel",
    "json": "application/json",
}


def get_file_extension(filename: str) -> str:
    """Extract and validate file extension."""
    if not filename or "." not in filename:
        raise ValueError(f"Invalid filename: {filename}")
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: .{ext}. "
            f"Supported types: {', '.join(SUPPORTED_EXTENSIONS)}"
        )
    return ext


async def parse_upload(file: UploadFile) -> tuple[pd.DataFrame, str, bytes]:
    """
    Parse an uploaded file into a DataFrame.

    Returns:
        Tuple of (DataFrame, file_extension, raw_bytes)
    """
    settings = get_settings()

    # Read file content
    content = await file.read()
    await file.seek(0)  # Reset for potential re-read

    # Validate size
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_upload_size_mb:
        raise ValueError(
            f"File size ({size_mb:.1f} MB) exceeds maximum "
            f"({settings.max_upload_size_mb} MB)."
        )

    ext = get_file_extension(file.filename or "")
    logger.info("Parsing %s file: %s (%.2f MB)", ext, file.filename, size_mb)

    try:
        df = parse_bytes(content, ext)
    except Exception as e:
        logger.error("Failed to parse file %s: %s", file.filename, str(e))
        raise ValueError(f"Failed to parse file: {str(e)}") from e

    if df.empty:
        raise ValueError("The uploaded file contains no data.")

    logger.info(
        "Parsed %s: %d rows × %d columns",
        file.filename,
        len(df),
        len(df.columns),
    )
    return df, ext, content


def parse_bytes(content: bytes, ext: str) -> pd.DataFrame:
    """Parse raw bytes into a DataFrame based on extension."""
    buffer = io.BytesIO(content)

    if ext == "csv":
        try:
            return pd.read_csv(buffer, low_memory=False)
        except UnicodeDecodeError:
            logger.warning("UTF-8 decoding failed for %s, falling back to latin-1", ext)
            buffer.seek(0)
            return pd.read_csv(buffer, low_memory=False, encoding="latin-1")
    elif ext in ("xlsx", "xls"):
        return pd.read_excel(buffer, engine="openpyxl")
    elif ext == "json":
        return pd.read_json(buffer)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


def get_content_type(ext: str) -> str:
    """Get the MIME content type for a file extension."""
    return CONTENT_TYPE_MAP.get(ext, "application/octet-stream")