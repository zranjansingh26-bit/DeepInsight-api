"""
DeepInsight Starter Suite — Dataset API Routes.

Endpoints for uploading datasets and retrieving metadata.
"""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from api.auth import get_current_user
from models.schemas import DatasetDetail, DatasetUploadResponse, UserContext
from services import dataset_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/upload",
    response_model=DatasetUploadResponse,
    summary="Upload a dataset",
    description="Upload a CSV, XLSX, or JSON file for analysis.",
)
async def upload_dataset(
    file: UploadFile = File(...),
    user: UserContext = Depends(get_current_user),
):
    """Upload a dataset file and generate initial metadata."""
    try:
        result = await dataset_service.upload_dataset(file, user.user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception("Upload failed: %s", str(e))
        
        # In development, return the actual error for easier debugging
        from config import get_settings
        settings = get_settings()
        
        if settings.app_env.lower() == "development":
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Upload failed due to an internal server error.",
                    "error": str(e),
                    "type": type(e).__name__
                }
            )
            
        raise HTTPException(
            status_code=500,
            detail="Upload failed due to an internal server error. Please try again."
        )


@router.get(
    "/{dataset_id}",
    response_model=DatasetDetail,
    summary="Get dataset details",
    description="Retrieve full metadata for a dataset.",
)
async def get_dataset(
    dataset_id: str,
    user: UserContext = Depends(get_current_user),
):
    """Get dataset metadata by ID."""
    dataset = dataset_service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    # Verify ownership
    if dataset.get("user_id") != user.user_id:
        raise HTTPException(status_code=403, detail="Access denied.")

    return {
        "id": dataset["id"],
        "user_id": dataset["user_id"],
        "file_name": dataset["file_name"],
        "file_type": dataset["file_type"],
        "storage_path": dataset["storage_path"],
        "row_count": dataset["row_count"],
        "column_count": dataset["column_count"],
        "null_percentage": dataset["null_percentage"],
        "quality_score": dataset["quality_score"],
        "columns": dataset.get("column_metadata", []),
        "created_at": dataset["created_at"],
    }