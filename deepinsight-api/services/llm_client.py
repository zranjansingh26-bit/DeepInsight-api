"""
DeepInsight Starter Suite — LLM Client.

Unified interface for Anthropic Claude and OpenAI GPT.
Auto-detects which API key is available and routes accordingly.
"""

import json
import logging
import re
from typing import Any

from config import get_settings

logger = logging.getLogger(__name__)


class LLMResponse:
    """Structured LLM response."""

    def __init__(self, answer: str, follow_up_questions: list[str] | None = None):
        self.answer = answer
        self.follow_up_questions = follow_up_questions or []


async def chat_completion(
    system_prompt: str,
    user_message: str,
    chat_history: list[dict[str, str]] | None = None,
) -> LLMResponse:
    """
    Send a chat completion request to the configured LLM provider.
    """
    settings = get_settings()
    provider = settings.active_llm

    if provider == "claude":
        return await _anthropic_completion(
            system_prompt, user_message, chat_history, settings.anthropic_api_key
        )
    elif provider == "openai":
        return await _openai_completion(
            system_prompt, user_message, chat_history, settings.openai_api_key
        )
    elif provider == "gemini":
        return await _gemini_completion(
            system_prompt, user_message, chat_history, settings.gemini_api_key
        )
    else:
        raise RuntimeError(
            "No LLM provider configured or keys missing. Set ANTHROPIC_API_KEY, OPENAI_API_KEY, or GEMINI_API_KEY."
        )


async def _anthropic_completion(
    system_prompt: str,
    user_message: str,
    chat_history: list[dict[str, str]] | None,
    api_key: str,
) -> LLMResponse:
    """Call Anthropic Claude API."""
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    messages = []
    if chat_history:
        for msg in chat_history[-10:]:  # Last 10 messages for context
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2048,
            system=system_prompt,
            messages=messages,
        )
        raw_text = response.content[0].text
        return _parse_response(raw_text)
    except Exception as e:
        logger.error("Anthropic API error: %s", str(e))
        raise RuntimeError(f"LLM request failed: {str(e)}") from e


async def _openai_completion(
    system_prompt: str,
    user_message: str,
    chat_history: list[dict[str, str]] | None,
    api_key: str,
) -> LLMResponse:
    """Call OpenAI GPT API."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    messages = [{"role": "system", "content": system_prompt}]
    if chat_history:
        for msg in chat_history[-10:]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"],
            })
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=2048,
            temperature=0.7,
        )
        raw_text = response.choices[0].message.content or ""
        return _parse_response(raw_text)
    except Exception as e:
        logger.error("OpenAI API error: %s", str(e))
        raise RuntimeError(f"LLM request failed: {str(e)}") from e


async def _gemini_completion(
    system_prompt: str,
    user_message: str,
    chat_history: list[dict[str, str]] | None,
    api_key: str,
) -> LLMResponse:
    """Call Google Gemini API."""
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-flash-latest")

    # Construct messages for Gemini
    contents = []
    if chat_history:
        for msg in chat_history[-10:]:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [msg["content"]]})
    
    # Gemini doesn't have a direct "system" role in the same way, 
    # but we can prepend it to the message or use the new system_instruction param.
    model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        system_instruction=system_prompt
    )

    try:
        response = model.generate_content(user_message)
        raw_text = response.text
        return _parse_response(raw_text)
    except Exception as e:
        logger.error("Gemini API error: %s", str(e))
        raise RuntimeError(f"LLM request failed: {str(e)}") from e


def _parse_response(raw_text: str) -> LLMResponse:
    """
    Parse the LLM response to extract the answer and follow-up questions.
    Attempts to find a JSON array of follow-up questions in the response.
    """
    follow_ups: list[str] = []

    # Try to find JSON array of follow-up questions
    json_pattern = r'"follow_up_questions"\s*:\s*(\[.*?\])'
    match = re.search(json_pattern, raw_text, re.DOTALL)
    if match:
        try:
            follow_ups = json.loads(match.group(1))
            # Remove the JSON block from the answer
            answer = raw_text[:match.start()].strip()
            # Clean trailing punctuation artifacts
            answer = answer.rstrip(",").rstrip("{").strip()
        except json.JSONDecodeError:
            answer = raw_text
    else:
        answer = raw_text

    # Fallback: look for numbered follow-up questions
    if not follow_ups:
        lines = raw_text.split("\n")
        capture = False
        answer_lines = []
        for line in lines:
            stripped = line.strip()
            if "follow" in stripped.lower() and "question" in stripped.lower():
                capture = True
                continue
            if capture and stripped.startswith(("1.", "2.", "3.", "-", "•")):
                q = stripped.lstrip("0123456789.-•) ").strip()
                if q:
                    follow_ups.append(q)
            else:
                answer_lines.append(line)
        if follow_ups:
            answer = "\n".join(answer_lines).strip()

    return LLMResponse(answer=answer, follow_up_questions=follow_ups[:5])
