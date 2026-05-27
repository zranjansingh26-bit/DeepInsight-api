"""
DeepInsight Starter Suite — Audit API.

Endpoints for retrieving organizational audit logs.
"""

from fastapi import APIRouter, Depends, HTTPException
from api.auth import get_current_user
from models.schemas import UserContext
from db.client import get_service_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/")
async def get_audit_logs(
    limit: int = 50,
    user: UserContext = Depends(get_current_user)
):
    """Fetch audit logs for the current user's organization."""
    # Requires an Admin role in a real implementation
    if user.role != "admin" and user.plan != "enterprise":
        raise HTTPException(status_code=403, detail="Audit logs require Enterprise plan and Admin role.")
        
    client = get_service_client()
    try:
        # Get user org
        profile = client.table("profiles").select("org_id").eq("id", user.user_id).execute()
        if not profile.data or not profile.data[0].get("org_id"):
            return []
            
        org_id = profile.data[0]["org_id"]
        
        # Get logs
        logs = client.table("audit_logs").select("*").eq("org_id", org_id).order("created_at", desc=True).limit(limit).execute()
        return logs.data
    except Exception as e:
        logger.error(f"Failed to fetch audit logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch audit logs")
