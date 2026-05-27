"""
DeepInsight Starter Suite — Connectors API Routes.

Endpoints for triggering data imports from external systems.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import logging

from api.auth import get_current_user
from models.schemas import UserContext
from services import connectors_service

logger = logging.getLogger(__name__)
router = APIRouter()

class PostgresConnectionRequest(BaseModel):
    connection_string: str
    query: str

class SnowflakeConnectionRequest(BaseModel):
    account: str
    user: str
    password: str
    warehouse: str
    database: str
    query: str

class S3ConnectionRequest(BaseModel):
    bucket: str
    file_key: str
    aws_access_key: str
    aws_secret_key: str


@router.post("/postgres")
async def import_postgres(
    request: PostgresConnectionRequest,
    user: UserContext = Depends(get_current_user)
):
    """Import data from an external PostgreSQL database."""
    try:
        result = await connectors_service.connect_postgres(
            request.connection_string, request.query
        )
        return {"message": "Data imported successfully", "details": result}
    except Exception as e:
        logger.error(f"Postgres import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/snowflake")
async def import_snowflake(
    request: SnowflakeConnectionRequest,
    user: UserContext = Depends(get_current_user)
):
    """Import data from a Snowflake data warehouse."""
    try:
        result = await connectors_service.connect_snowflake(
            request.account, request.user, request.password, 
            request.warehouse, request.database, request.query
        )
        return {"message": "Data imported successfully", "details": result}
    except Exception as e:
        logger.error(f"Snowflake import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/s3")
async def import_s3(
    request: S3ConnectionRequest,
    user: UserContext = Depends(get_current_user)
):
    """Import a file from an AWS S3 bucket."""
    try:
        result = await connectors_service.connect_s3(
            request.bucket, request.file_key, 
            request.aws_access_key, request.aws_secret_key
        )
        return {"message": "File downloaded successfully", "details": result}
    except Exception as e:
        logger.error(f"S3 import failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
