"""
DeepInsight Starter Suite — Chat Service.

Manages chat sessions and messages, integrating with the LLM client
and context builder for conversational data analysis.
"""

import logging
from typing import Any

from db import repository
from engines.context_builder import build_context, build_system_prompt
from services.dataset_service import get_dataset, get_dataframe
from services.llm_client import chat_completion

logger = logging.getLogger(__name__)


async def create_session(
    dataset_id: str, user_id: str, title: str | None = None,
) -> dict[str, Any]:
    """Create a new chat session linked to a dataset."""
    dataset = get_dataset(dataset_id)
    if not dataset:
        raise ValueError(f"Dataset {dataset_id} not found.")

    session_title = title or f"Chat about {dataset['file_name']}"
    session = repository.create_chat_session(
        dataset_id=dataset_id,
        user_id=user_id,
        title=session_title,
    )
    logger.info("Created chat session %s for dataset %s", session["id"], dataset_id)
    return session


async def send_message(
    session_id: str, user_message: str,
) -> dict[str, Any]:
    """
    Process a user message:
    1. Fetch session and dataset
    2. Build context from dataset
    3. Get chat history
    4. Call LLM
    5. Save both user message and assistant response
    6. Return response
    """
    # Fetch session
    session = repository.get_chat_session(session_id)
    if not session:
        raise ValueError(f"Chat session {session_id} not found.")

    # Fetch dataset and build context
    dataset = get_dataset(session["dataset_id"])
    if not dataset:
        raise ValueError(f"Dataset {session['dataset_id']} not found.")

    df = get_dataframe(dataset)
    context = build_context(df, dataset)
    system_prompt = build_system_prompt(context)

    # Get recent chat history
    messages = repository.get_chat_messages(session_id)
    chat_history = [
        {"role": m["role"], "content": m["content"]}
        for m in messages[-20:]  # Last 20 messages
    ]

    # Save user message
    repository.save_chat_message(
        session_id=session_id,
        role="user",
        content=user_message,
    )

    # Call LLM
    llm_response = await chat_completion(
        system_prompt=system_prompt,
        user_message=user_message,
        chat_history=chat_history,
    )

    # Save assistant response
    saved = repository.save_chat_message(
        session_id=session_id,
        role="assistant",
        content=llm_response.answer,
        follow_up_questions=llm_response.follow_up_questions,
    )

    logger.info("Chat message processed for session %s", session_id)
    return {
        "id": saved["id"],
        "session_id": session_id,
        "role": "assistant",
        "content": llm_response.answer,
        "follow_up_questions": llm_response.follow_up_questions,
        "created_at": saved["created_at"],
    }


async def get_history(session_id: str) -> dict[str, Any]:
    """Fetch full chat history for a session."""
    session = repository.get_chat_session(session_id)
    if not session:
        raise ValueError(f"Chat session {session_id} not found.")

    messages = repository.get_chat_messages(session_id)
    return {
        "session_id": session_id,
        "dataset_id": session["dataset_id"],
        "title": session["title"],
        "messages": [
            {
                "id": m["id"],
                "session_id": m["session_id"],
                "role": m["role"],
                "content": m["content"],
                "follow_up_questions": m.get("follow_up_questions", []),
                "created_at": m["created_at"],
            }
            for m in messages
        ],
    }
