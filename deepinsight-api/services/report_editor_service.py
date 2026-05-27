"""
DeepInsight Starter Suite — Report Editor Service.

Orchestrates AI report creation, versioning, and revisions.
"""

import logging
import json
from typing import Any

from db.client import get_service_client
from services import llm_client
from services import report_service

logger = logging.getLogger(__name__)

async def create_initial_report(user_id: str, dataset_id: str, title: str) -> dict[str, Any]:
    """Generate an initial AI report and save version 1."""
    client = get_service_client()
    
    # Generate the initial narrative structure
    narrative = await report_service._generate_executive_narrative(dataset_id)
    
    # Store in DB as version 1
    report_record = {
        "user_id": user_id,
        "dataset_id": dataset_id,
        "title": title,
        "content_json": {"narrative": narrative, "sections": []},
        "version": 1
    }
    
    result = client.table("report_documents").insert(report_record).execute()
    return result.data[0]


async def revise_report(user_id: str, report_id: str, instruction: str) -> dict[str, Any]:
    """Revise an existing report based on an AI instruction and bump version."""
    client = get_service_client()
    
    # 1. Fetch current report
    res = client.table("report_documents").select("*").eq("id", report_id).eq("user_id", user_id).execute()
    if not res.data:
        raise ValueError("Report not found")
        
    current_report = res.data[0]
    current_content = current_report["content_json"]
    current_version = current_report["version"]
    
    # 2. Ask LLM to apply instruction
    prompt = (
        f"You are a professional business analyst editing a report.\n"
        f"Current Report JSON:\n{json.dumps(current_content)}\n\n"
        f"Instruction from user: {instruction}\n\n"
        f"Return ONLY the updated JSON. Preserve existing structure where possible."
    )
    
    ai_resp = await llm_client.chat_completion(
        system_prompt="Return strict JSON matching the input schema.",
        user_message=prompt
    )
    
    # Crude JSON extraction
    clean_text = ai_resp.answer.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:-3]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:-3]
        
    try:
        new_content = json.loads(clean_text)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse LLM revised JSON: {clean_text}")
        raise RuntimeError("AI generated invalid document structure.")
        
    new_version = current_version + 1
    
    # 3. Save Revision log
    client.table("report_revisions").insert({
        "report_id": report_id,
        "instruction": instruction,
        "version": new_version,
        "diff": {"old": current_content, "new": new_content} # crude diff for now
    }).execute()
    
    # 4. Update Main Report
    updated_report = client.table("report_documents").update({
        "content_json": new_content,
        "version": new_version
    }).eq("id", report_id).execute()
    
    return updated_report.data[0]


def get_report_history(report_id: str) -> list[dict[str, Any]]:
    """Get the revision history for a report."""
    client = get_service_client()
    res = client.table("report_revisions").select(
        "id, instruction, version, created_at"
    ).eq("report_id", report_id).order("version", desc=True).execute()
    return res.data
