"""
DeepInsight Starter Suite — Documents API Routes.

Endpoints for uploading and analyzing unstructured documents (PDF, DOCX).
"""

import logging
from typing import Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from api.auth import get_current_user
from models.schemas import UserContext
from db.client import get_service_client
from tasks.document_tasks import process_document_task

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    user: UserContext = Depends(get_current_user)
) -> dict[str, Any]:
    """
    Upload a document (PDF, DOCX, PPTX) for background processing and AI summarization.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
        
    file_bytes = await file.read()
    
    # Offload to Celery background task
    task = process_document_task.delay(
        user_id=user.user_id,
        filename=file.filename,
        file_bytes=file_bytes,
        mime_type=file.content_type,
        org_id=user.org_id if hasattr(user, 'org_id') else None
    )
    
    return {
        "status": "processing",
        "message": "Document sent for analysis.",
        "task_id": task.id,
        "filename": file.filename
    }


@router.get("/")
async def list_documents(user: UserContext = Depends(get_current_user)):
    """List all documents for the current user."""
    client = get_service_client()
    try:
        res = client.table("documents").select(
            "id, filename, status, created_at"
        ).eq("user_id", user.user_id).order("created_at", desc=True).execute()
        return res.data
    except Exception as e:
        logger.error(f"Failed to fetch documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")


@router.get("/{doc_id}")
async def get_document(doc_id: str, user: UserContext = Depends(get_current_user)):
    """Get processed document details."""
    client = get_service_client()
    try:
        res = client.table("documents").select("*").eq("id", doc_id).eq("user_id", user.user_id).execute()
        if not res.data:
            raise HTTPException(status_code=404, detail="Document not found")
        return res.data[0]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch document: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch document")
