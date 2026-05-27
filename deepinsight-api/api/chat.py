"""
DeepInsight Starter Suite — Chat API Routes.

Endpoints for managing chat sessions and sending messages.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

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

@router.post(
    "/{session_id}/message/stream",
    summary="Send message and stream response",
    description="Send a message and receive an AI-generated response via Server-Sent Events (SSE).",
)
async def send_message_stream_endpoint(
    session_id: str,
    request: ChatMessageRequest,
    user: UserContext = Depends(get_current_user),
):
    """Stream response from the AI assistant."""
    try:
        # Validate session belongs to user (implicit via dataset)
        session = await chat_service.get_history(session_id)
        if not session:
            raise ValueError("Session not found")
            
        async def event_generator():
            try:
                async for chunk in chat_service.send_message_stream(session_id, request.message):
                    # Format as SSE
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                yield f"event: error\ndata: {str(e)}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Chat stream failed for session %s", session_id)
        raise HTTPException(status_code=500, detail="Message stream failed.")


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


@router.post(
    "/{session_id}/followups",
    summary="Get smart follow-up questions",
    description="Generate dataset-aware, contextual follow-up question suggestions.",
)
async def get_followup_questions(
    session_id: str,
    user: UserContext = Depends(get_current_user),
):
    """Regenerate smart follow-up questions for a session on demand."""
    try:
        history = await chat_service.get_history(session_id)
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in history["messages"][-20:]
        ]

        # Build context
        from db import repository
        from services.dataset_service import get_dataset, get_dataframe
        from engines.context_builder import build_context

        dataset = get_dataset(history["dataset_id"])
        if not dataset:
            raise ValueError("Dataset not found")
        df = get_dataframe(dataset)
        context = build_context(df, dataset)

        questions = await chat_service.generate_smart_followups(
            session_id=session_id,
            conversation_history=messages,
            context=context,
        )
        return {"session_id": session_id, "questions": questions}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception("Followup generation failed for session %s", session_id)
        raise HTTPException(status_code=500, detail="Failed to generate follow-up questions.")