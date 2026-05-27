"""
DeepInsight Starter Suite — Jobs API Routes.

Endpoints for polling background task status (Celery).
"""

from fastapi import APIRouter, Depends, HTTPException
from celery.result import AsyncResult

from api.auth import get_current_user
from models.schemas import UserContext
from worker import celery_app

router = APIRouter()

@router.get("/{task_id}")
async def get_task_status(
    task_id: str,
    user: UserContext = Depends(get_current_user)
):
    """
    Get the status of a Celery background task.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
    }
    
    if task_result.state == "SUCCESS":
        response["result"] = task_result.result
    elif task_result.state == "FAILURE":
        response["error"] = str(task_result.result)
    elif task_result.state == "PROGRESS":
        # custom state for progress bars
        response["meta"] = task_result.info
        
    return response

@router.post("/{task_id}/cancel")
async def cancel_task(
    task_id: str,
    user: UserContext = Depends(get_current_user)
):
    """Cancel a running Celery background task."""
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {"status": "success", "message": f"Task {task_id} canceled."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

