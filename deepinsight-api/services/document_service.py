"""
DeepInsight Starter Suite — Document Service.

Orchestrates document parsing, chunking, AI analysis, and storage.
"""

import logging
import uuid
import time
from typing import Dict, Any

from db.client import get_service_client
from db.repository import upload_file_to_storage
from config import get_settings
from engines.doc_intelligence import (
    parse_pdf, parse_docx, parse_pptx,
    chunk_document, generate_ai_summary
)

logger = logging.getLogger(__name__)

async def process_document_async(
    user_id: str,
    filename: str,
    file_bytes: bytes,
    mime_type: str,
    org_id: str = None
) -> Dict[str, Any]:
    """
    Process a document: parse text, upload to storage, and run AI analysis.
    Usually run as a background task.
    """
    settings = get_settings()
    client = get_service_client()
    
    # 1. Create DB record as 'processing'
    doc_id = str(uuid.uuid4())
    doc_record = {
        "id": doc_id,
        "user_id": user_id,
        "org_id": org_id,
        "filename": filename,
        "storage_path": f"{user_id}/docs/{doc_id}_{filename}",
        "status": "processing",
        "created_at": time.strftime('%Y-%m-%d %H:%M:%S+00:00')
    }
    client.table("documents").insert(doc_record).execute()
    
    try:
        # 2. Extract Text
        text = ""
        if "pdf" in mime_type:
            text = parse_pdf(file_bytes)
        elif "word" in mime_type or "docx" in filename:
            text = parse_docx(file_bytes)
        elif "powerpoint" in mime_type or "presentation" in mime_type or "pptx" in filename:
            text = parse_pptx(file_bytes)
        else:
             # Assume text
             text = file_bytes.decode('utf-8', errors='ignore')
             
        # 3. AI Analysis
        chunks = chunk_document(text)
        analysis_result = await generate_ai_summary(chunks)
        
        # 4. Upload original to storage
        storage_path = upload_file_to_storage(
            user_id,
            f"{doc_id}_{filename}",
            file_bytes,
            mime_type,
            bucket=settings.supabase_storage_bucket
        )
        
        # 5. Update DB record to 'ready'
        client.table("documents").update({
            "status": "ready",
            "storage_path": storage_path,
            "extracted_text": text[:5000], # Save first 5k chars for quick preview
            "ai_summary": analysis_result.get("summary", ""),
            "metadata": {
                "entities": analysis_result.get("entities", []),
                "risks": analysis_result.get("risks", []),
                "recommendations": analysis_result.get("recommendations", []),
                "chunk_count": len(chunks)
            }
        }).eq("id", doc_id).execute()
        
        return {"status": "success", "doc_id": doc_id}
        
    except Exception as e:
        logger.error(f"Document processing failed for {filename}: {e}")
        client.table("documents").update({
            "status": "failed",
            "metadata": {"error": str(e)}
        }).eq("id", doc_id).execute()
        raise
