"""
DeepInsight Starter Suite — Dataset Service.

Orchestrates file upload, parsing, quality analysis, and storage.
"""

import logging
from typing import Any

import pandas as pd
from fastapi import UploadFile

from db import repository
from engines.file_parser import parse_upload, get_content_type, parse_bytes
from engines.quality_checker import check_quality

logger = logging.getLogger(__name__)


async def upload_dataset(file: UploadFile, user_id: str) -> dict[str, Any]:
    """
    Full upload pipeline:
    1. Parse the uploaded file into a DataFrame
    2. Run quality checks
    3. Upload raw file to Supabase Storage
    4. Save metadata to database
    5. Return complete response
    """
    # Parse file
    df, ext, raw_bytes = await parse_upload(file)

    # Quality analysis
    quality = check_quality(df)

    # Upload to storage
    content_type = get_content_type(ext)
    storage_path = repository.upload_file_to_storage(
        user_id=user_id,
        file_name=file.filename or "upload",
        file_content=raw_bytes,
        content_type=content_type,
    )

    # Save dataset metadata to DB
    dataset = repository.create_dataset(
        user_id=user_id,
        file_name=file.filename or "upload",
        file_type=ext,
        storage_path=storage_path,
        row_count=quality["row_count"],
        column_count=quality["column_count"],
        null_percentage=quality["null_percentage"],
        quality_score=quality["quality_score"],
        column_metadata=quality["columns"],
    )

    logger.info("Dataset uploaded: %s (id=%s)", file.filename, dataset["id"])

    return {
        "id": dataset["id"],
        "file_name": dataset["file_name"],
        "file_type": dataset["file_type"],
        "row_count": dataset["row_count"],
        "column_count": dataset["column_count"],
        "null_percentage": dataset["null_percentage"],
        "quality_score": dataset["quality_score"],
        "columns": dataset["column_metadata"],
        "created_at": dataset["created_at"],
    }


def get_dataset(dataset_id: str) -> dict[str, Any] | None:
    """Fetch dataset metadata by ID."""
    return repository.get_dataset(dataset_id)


def get_dataframe(dataset: dict) -> pd.DataFrame:
    """
    Download the dataset file from storage and parse into DataFrame.
    """
    raw_bytes = repository.download_file_from_storage(dataset["storage_path"])
    return parse_bytes(raw_bytes, dataset["file_type"])


def list_user_datasets(user_id: str) -> list[dict]:
    """List all datasets for a user."""
    return repository.list_datasets(user_id)
