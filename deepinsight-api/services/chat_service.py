"""
DeepInsight Starter Suite — Chat Service.

Manages chat sessions and messages, integrating with the LLM client
and context builder for conversational data analysis.
"""

import json
import logging
from typing import Any

from db import repository
from engines.context_builder import build_context, build_system_prompt, build_followup_prompt
from services.dataset_service import get_dataset, get_dataframe
from services.llm_client import chat_completion, chat_completion_stream

logger = logging.getLogger(__name__)

# In-memory dedup cache: session_id -> list of previously suggested questions
_followup_cache: dict[str, list[str]] = {}


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


async def generate_smart_followups(
    session_id: str,
    conversation_history: list[dict],
    context: str,
) -> list[str]:
    """
    Generate dataset-aware, deduped follow-up questions for a chat session.
    Uses a dedicated LLM call with specialised prompt.
    """
    global _followup_cache
    already_asked = _followup_cache.get(session_id, [])

    prompt = build_followup_prompt(context, conversation_history, already_asked)

    try:
        response = await chat_completion(
            system_prompt="You are a data analytics assistant. Respond with a JSON array only.",
            user_message=prompt,
        )
        raw = response.answer.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        questions = json.loads(raw)
        if not isinstance(questions, list):
            raise ValueError("Not a list")
        questions = [str(q) for q in questions[:5]]

        # Deduplicate against cache
        new_qs = [q for q in questions if q not in already_asked]

        # Update cache
        _followup_cache[session_id] = (already_asked + new_qs)[-30:]

        return new_qs or questions  # fallback to all if everything was deduped
    except Exception as e:
        logger.warning("Smart followup generation failed: %s", e)
        return [
            "Would you like to see a trend analysis?",
            "Should I run anomaly detection on this dataset?",
            "Would you like a forecast for the next 30 days?",
        ]


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


async def send_message_stream(
    session_id: str, user_message: str,
):
    """
    Process a user message and return an async generator for streaming the response.
    Saves the full message to DB after completion.
    """
    session = repository.get_chat_session(session_id)
    if not session:
        raise ValueError(f"Chat session {session_id} not found.")

    dataset = get_dataset(session["dataset_id"])
    if not dataset:
        raise ValueError(f"Dataset {session['dataset_id']} not found.")

    df = get_dataframe(dataset)
    context = build_context(df, dataset)
    system_prompt = build_system_prompt(context)

    messages = repository.get_chat_messages(session_id)
    chat_history = [
        {"role": m["role"], "content": m["content"]}
        for m in messages[-20:]
    ]

    repository.save_chat_message(
        session_id=session_id,
        role="user",
        content=user_message,
    )

    full_response = ""
    async for chunk in chat_completion_stream(
        system_prompt=system_prompt,
        user_message=user_message,
        chat_history=chat_history,
    ):
        full_response += chunk
        yield chunk

    # Generate smart follow-up questions after streaming completes
    all_messages = chat_history + [{"role": "user", "content": user_message}]
    followups = await generate_smart_followups(session_id, all_messages, context)

    # Save to DB with follow-up questions
    repository.save_chat_message(
        session_id=session_id,
        role="assistant",
        content=full_response,
        follow_up_questions=followups,
    )

    # Emit terminal SSE event with follow-up questions
    followup_event = json.dumps({"questions": followups})
    yield f"[FOLLOWUP]{followup_event}"



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
