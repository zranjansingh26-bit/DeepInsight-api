"""
DeepInsight Starter Suite — Chat API Routes.

Endpoints for managing chat sessions and sending messages.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from api.auth import get_current_user
from models.schemas import (
    ChatHistoryResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    ChatSessionCreate,
    ChatSessionResponse,
    UserContext,
)
from services import chat_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/sessions",
    response_model=ChatSessionResponse,
    summary="Create chat session",
    description="Create a new chat session linked to a dataset.",
)
async def create_session(
    request: ChatSessionCreate,
    user: UserContext = Depends(get_current_user),
):
    """Create a new chat session for conversational analysis."""
    try:
        session = await chat_service.create_session(
            dataset_id=request.dataset_id,
            user_id=user.user_id,
            title=request.title,
        )
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Failed to create chat session")
        # In development, return the actual error message for easier debugging
        detail = f"Failed to create session: {str(e)}"
        raise HTTPException(status_code=500, detail=detail)


@router.post(
    "/{session_id}/message",
    response_model=ChatMessageResponse,
    summary="Send message",
    description="Send a message and receive an AI-generated response.",
)
async def send_message(
    session_id: str,
    request: ChatMessageRequest,
    user: UserContext = Depends(get_current_user),
):
    """Send a message to the AI assistant and get a response."""
    try:
        response = await chat_service.send_message(
            session_id=session_id,
            user_message=request.message,
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.exception("Chat message failed for session %s", session_id)
        raise HTTPException(status_code=500, detail="Message processing failed.")


@router.get(
    "/{session_id}/history",
    response_model=ChatHistoryResponse,
    summary="Get chat history",
    description="Retrieve the full message history for a chat session.",
)
async def get_history(
    session_id: str,
    user: UserContext = Depends(get_current_user),
):
    """Fetch all messages for a chat session."""
    try:
        history = await chat_service.get_history(session_id)
        return history
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Failed to fetch history for session %s", session_id)
        raise HTTPException(status_code=500, detail="Failed to fetch history.")