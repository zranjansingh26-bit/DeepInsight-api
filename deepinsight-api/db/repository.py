"""
DeepInsight Starter Suite — Data Access Repository.

All Supabase database and storage operations are encapsulated here
to keep services and API routes decoupled from the data layer.
"""

import io
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from db.client import get_service_client
from config import get_settings

logger = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────


def _new_id() -> str:
    return str(uuid.uuid4())


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── Dataset Operations ───────────────────────────────────────


def create_dataset(
    user_id: str,
    file_name: str,
    file_type: str,
    storage_path: str,
    row_count: int,
    column_count: int,
    null_percentage: float,
    quality_score: int,
    column_metadata: list[dict],
) -> dict:
    """Insert a new dataset record and return it."""
    client = get_service_client()
    record = {
        "id": _new_id(),
        "user_id": user_id,
        "file_name": file_name,
        "file_type": file_type,
        "storage_path": storage_path,
        "row_count": row_count,
        "column_count": column_count,
        "null_percentage": null_percentage,
        "quality_score": quality_score,
        "column_metadata": column_metadata,
        "created_at": _now(),
        "updated_at": _now(),
    }
    result = client.table("datasets").insert(record).execute()
    logger.info("Database result: %s", result)
    if not result.data:
        logger.error("Insert failed: No data returned from database")
        raise RuntimeError("Failed to create dataset in database.")
    logger.info("Created dataset %s for user %s", record["id"], user_id)
    return result.data[0]


def get_dataset(dataset_id: str) -> Optional[dict]:
    """Fetch a single dataset by ID."""
    client = get_service_client()
    try:
        result = client.table("datasets").select("*").eq("id", dataset_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        logger.warning("Failed to fetch dataset %s: %s", dataset_id, e)
        return None


def list_datasets(user_id: str) -> list[dict]:
    """List all datasets for a user."""
    client = get_service_client()
    result = (
        client.table("datasets")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


# ── Analysis Operations ──────────────────────────────────────


def save_analysis(
    dataset_id: str,
    analysis_type: str,
    results: dict[str, Any],
    charts: list[dict],
) -> dict:
    """Insert or update an analysis result."""
    client = get_service_client()

    # Upsert: delete existing then insert
    client.table("analysis_results").delete().eq(
        "dataset_id", dataset_id
    ).eq("analysis_type", analysis_type).execute()

    record = {
        "id": _new_id(),
        "dataset_id": dataset_id,
        "analysis_type": analysis_type,
        "results": results,
        "charts": charts,
        "created_at": _now(),
    }
    result = client.table("analysis_results").insert(record).execute()
    if not result.data:
        logger.error("Failed to save analysis: No data returned from database")
        raise RuntimeError(f"Failed to save {analysis_type} analysis.")
    logger.info("Saved %s analysis for dataset %s", analysis_type, dataset_id)
    return result.data[0]


def get_analysis(
    dataset_id: str, analysis_type: str
) -> Optional[dict]:
    """Fetch a cached analysis result."""
    client = get_service_client()
    try:
        result = (
            client.table("analysis_results")
            .select("*")
            .eq("dataset_id", dataset_id)
            .eq("analysis_type", analysis_type)
            .execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        logger.warning("Failed to fetch analysis for dataset %s: %s", dataset_id, e)
        return None


def get_all_analyses(dataset_id: str) -> list[dict]:
    """Fetch all analysis results for a dataset."""
    client = get_service_client()
    try:
        result = (
            client.table("analysis_results")
            .select("*")
            .eq("dataset_id", dataset_id)
            .order("created_at", desc=True)
            .execute()
        )
        return result.data
    except Exception as e:
        logger.warning("Failed to fetch analyses for dataset %s: %s", dataset_id, e)
        return []


# ── Chat Operations ──────────────────────────────────────────


def create_chat_session(
    dataset_id: str, user_id: str, title: str = "New Chat"
) -> dict:
    """Create a new chat session linked to a dataset."""
    client = get_service_client()
    record = {
        "id": _new_id(),
        "dataset_id": dataset_id,
        "user_id": user_id,
        "title": title,
        "created_at": _now(),
        "updated_at": _now(),
    }
    try:
        result = client.table("chat_sessions").insert(record).execute()
        if not result.data:
            logger.error("Failed to create chat session: No data returned from database")
            raise RuntimeError("Failed to create chat session in database.")
        logger.info("Created chat session %s", record["id"])
        return result.data[0]
    except Exception as e:
        logger.error("Chat session creation failed: %s", str(e))
        raise


def get_chat_session(session_id: str) -> Optional[dict]:
    """Fetch a chat session by ID."""
    client = get_service_client()
    try:
        result = (
            client.table("chat_sessions").select("*").eq("id", session_id).execute()
        )
        return result.data[0] if result.data else None
    except Exception as e:
        logger.warning("Failed to fetch chat session %s: %s", session_id, e)
        return None


def save_chat_message(
    session_id: str,
    role: str,
    content: str,
    follow_up_questions: list[str] | None = None,
) -> dict:
    """Save a chat message."""
    client = get_service_client()
    record = {
        "id": _new_id(),
        "session_id": session_id,
        "role": role,
        "content": content,
        "follow_up_questions": follow_up_questions or [],
        "created_at": _now(),
    }
    result = client.table("chat_messages").insert(record).execute()
    if not result.data:
        logger.error("Failed to save chat message: No data returned from database")
        raise RuntimeError("Failed to save message in database.")
    return result.data[0]


def get_chat_messages(session_id: str) -> list[dict]:
    """Fetch all messages for a chat session in chronological order."""
    client = get_service_client()
    try:
        result = (
            client.table("chat_messages")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at", desc=False)
            .execute()
        )
        return result.data
    except Exception as e:
        logger.warning("Failed to fetch chat messages for session %s: %s", session_id, e)
        return []


# ── Storage Operations ───────────────────────────────────────


def upload_file_to_storage(
    user_id: str,
    file_name: str,
    file_content: bytes,
    content_type: str = "application/octet-stream",
) -> str:
    """
    Upload a file to Supabase Storage.
    Returns the storage path.
    """
    settings = get_settings()
    client = get_service_client()
    storage_path = f"{user_id}/{_new_id()}_{file_name}"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            client.storage.from_(settings.supabase_storage_bucket).upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": content_type},
            )
            logger.info("Uploaded file to storage: %s (attempt %d)", storage_path, attempt + 1)
            return storage_path
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error("Final storage upload attempt failed for path %s: %s", storage_path, str(e))
                if "bucket" in str(e).lower():
                    raise RuntimeError(f"Storage bucket '{settings.supabase_storage_bucket}' not found or inaccessible.") from e
                raise RuntimeError(f"Failed to upload file to storage: {str(e)}") from e
            
            logger.warning("Upload attempt %d failed: %s. Retrying in 2 seconds...", attempt + 1, str(e))
            import time
            time.sleep(2)

    return storage_path
def download_file_from_storage(storage_path: str) -> bytes:
    """Download a file from Supabase Storage."""
    settings = get_settings()
    client = get_service_client()

    max_retries = 3
    for attempt in range(max_retries):
        try:
            data = client.storage.from_(settings.supabase_storage_bucket).download(
                storage_path
            )
            logger.info("Downloaded file from storage: %s", storage_path)
            return data
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error("Final storage download attempt failed for path %s: %s", storage_path, str(e))
                raise RuntimeError(f"Failed to download file from storage: {str(e)}") from e
            
            logger.warning("Download attempt %d failed: %s. Retrying in 2 seconds...", attempt + 1, str(e))
            import time
            time.sleep(2)
    
    # Should not reach here if max_retries > 0 and exception is raised
    return b""

