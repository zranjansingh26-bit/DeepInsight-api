"""
DeepInsight Starter Suite — Organizations API.

Manage multi-tenant workspaces, team members, and shared resources.
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

class CreateOrgRequest(BaseModel):
    name: str
    domain: str = None

class InviteMemberRequest(BaseModel):
    email: str
    role: str = "member"


@router.post("/")
async def create_organization(
    request: CreateOrgRequest,
    user: UserContext = Depends(get_current_user)
) -> dict[str, Any]:
    """Create a new organization and make the creator an admin."""
    client = get_service_client()
    
    # 1. Create org
    res = client.table("organizations").insert({
        "name": request.name,
        "domain": request.domain
    }).execute()
    
    org = res.data[0]
    org_id = org["id"]
    
    # 2. Add membership
    # We'll use the profile org_id for now as the active org, and create a membership record
    client.table("profiles").update({"org_id": org_id, "role": "admin"}).eq("id", user.user_id).execute()
    
    return {"status": "success", "organization": org}


@router.get("/")
async def list_organizations(user: UserContext = Depends(get_current_user)):
    """List organizations the user belongs to."""
    client = get_service_client()
    
    # For MVP, user belongs to max 1 org via profile
    res = client.table("profiles").select("org_id, organizations(*)").eq("id", user.user_id).execute()
    if not res.data or not res.data[0].get("organizations"):
        return []
        
    return [res.data[0]["organizations"]]


@router.get("/{org_id}/members")
async def get_org_members(org_id: str, user: UserContext = Depends(get_current_user)):
    """List all members of an organization."""
    client = get_service_client()
    
    # Check if user is in org
    user_res = client.table("profiles").select("org_id").eq("id", user.user_id).execute()
    if not user_res.data or user_res.data[0]["org_id"] != org_id:
        raise HTTPException(status_code=403, detail="Not a member of this organization")
        
    res = client.table("profiles").select("id, email, display_name, role").eq("org_id", org_id).execute()
    return res.data
