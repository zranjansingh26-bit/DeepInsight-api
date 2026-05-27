"""
DeepInsight Starter Suite — Audit Service.

Logs actions and user activity for security and compliance.
"""

import logging
from db.client import get_service_client

logger = logging.getLogger(__name__)

def log_action(user_id: str, org_id: str, action: str, resource_type: str, resource_id: str, details: dict = None) -> None:
    """Log an audit event asynchronously (bypasses RLS)."""
    try:
        client = get_service_client()
        client.table("audit_logs").insert({
            "user_id": user_id,
            "org_id": org_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {}
        }).execute()
    except Exception as e:
        logger.error(f"Failed to write audit log ({action}): {e}")
