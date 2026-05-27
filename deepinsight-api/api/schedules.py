"""
DeepInsight Starter Suite — Schedules API.

Manage recurring jobs (e.g. weekly reports).
"""

import logging
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from api.auth import get_current_user
from models.schemas import UserContext
from db.client import get_service_client

logger = logging.getLogger(__name__)
router = APIRouter()

class CreateScheduleRequest(BaseModel):
    dataset_id: str
    job_type: str
    cron_expression: str
    config: dict = {}


@router.post("/")
async def create_schedule(
    request: CreateScheduleRequest,
    user: UserContext = Depends(get_current_user)
) -> dict[str, Any]:
    """Create a new recurring scheduled job."""
    client = get_service_client()
    
    res = client.table("scheduled_jobs").insert({
        "user_id": user.user_id,
        "dataset_id": request.dataset_id,
        "job_type": request.job_type,
        "cron_expression": request.cron_expression,
        "config": request.config
    }).execute()
    
    return {"status": "success", "schedule": res.data[0]}


@router.get("/")
async def list_schedules(user: UserContext = Depends(get_current_user)):
    """List all scheduled jobs for the user."""
    client = get_service_client()
    res = client.table("scheduled_jobs").select("*").eq("user_id", user.user_id).execute()
    return res.data


@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str, user: UserContext = Depends(get_current_user)):
    """Delete a scheduled job."""
    client = get_service_client()
    res = client.table("scheduled_jobs").delete().eq("id", schedule_id).eq("user_id", user.user_id).execute()
    return {"status": "success", "message": "Schedule deleted."}
