"""
DeepInsight — AI Utilities API.

Provides generic AI-powered text summarization for arbitrary
analysis results (ML, Forecast, Anomaly Detection).
"""

import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.llm_client import chat_completion

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["AI Utilities"])


class SummarizeRequest(BaseModel):
    context: str          # JSON/text describing the analysis results
    section_type: str     # "ml" | "forecast" | "anomaly"
    dataset_name: str = "Dataset"


class SummarizeResponse(BaseModel):
    overview: str
    key_findings: str
    performance_summary: str
    risks_and_alerts: str
    recommendations: str
    conclusion: str


PROMPTS = {
    "ml": """You are a senior Data Scientist writing a board-ready ML Performance Report.
Given the following ML model comparison results, write a structured executive analysis.
Respond ONLY with valid JSON (no markdown fences) with exactly these keys:
{{
  "overview": "2-sentence business overview of what was modeled and why.",
  "key_findings": "Most important ML findings — best model, accuracy gaps, overfitting signals.",
  "performance_summary": "Detailed performance breakdown per model. Compare accuracy, F1, RMSE, R² etc.",
  "risks_and_alerts": "Data quality risks, class imbalance, low accuracy warnings, overfitting.",
  "recommendations": "3-5 specific actions: model to deploy, hyperparameter tuning, data collection.",
  "conclusion": "1-sentence confident deployment recommendation."
}}
Results:
{context}""",

    "forecast": """You are a senior Data Scientist writing a board-ready Time Series Forecast Report.
Given the following forecasting results, write a structured executive analysis.
Respond ONLY with valid JSON (no markdown fences) with exactly these keys:
{{
  "overview": "2-sentence business context — what is being forecasted and over what horizon.",
  "key_findings": "Most important forecast findings — trend direction, seasonality, inflection points.",
  "performance_summary": "Model accuracy, confidence intervals, forecast values summary.",
  "risks_and_alerts": "Forecast uncertainty, model assumptions, data stationarity issues.",
  "recommendations": "3-5 specific business actions based on the forecast trajectory.",
  "conclusion": "1-sentence confident business outlook based on the forecast."
}}
Results:
{context}""",

    "anomaly": """You are a senior Data Scientist writing a board-ready Anomaly Detection Report.
Given the following anomaly detection results, write a structured executive analysis.
Respond ONLY with valid JSON (no markdown fences) with exactly these keys:
{{
  "overview": "2-sentence business context — what anomalies were detected and in which dataset.",
  "key_findings": "Most critical anomalies — which columns, how many, severity assessment.",
  "performance_summary": "Detection method used, total count, per-column breakdown summary.",
  "risks_and_alerts": "High-risk anomaly clusters, potential fraud/error signals, data integrity issues.",
  "recommendations": "3-5 specific investigation and remediation actions.",
  "conclusion": "1-sentence risk assessment and urgency recommendation."
}}
Results:
{context}""",
}


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_results(req: SummarizeRequest):
    """Generate a structured AI executive summary for ML/Forecast/Anomaly results."""
    section = req.section_type.lower()
    prompt_template = PROMPTS.get(section, PROMPTS["ml"])
    prompt = prompt_template.format(context=req.context[:6000])

    default = {
        "overview": f"Analysis of {req.dataset_name} completed successfully.",
        "key_findings": "Results have been processed. Review the detailed metrics above.",
        "performance_summary": req.context[:500],
        "risks_and_alerts": "Review flagged metrics carefully before making business decisions.",
        "recommendations": "1. Validate results on a holdout set. 2. Monitor performance over time. 3. Collect more data if accuracy is low.",
        "conclusion": "Further validation is recommended before production deployment.",
    }

    try:
        response = await chat_completion(
            system_prompt="You are an expert Executive Business Analyst. Output only valid JSON.",
            user_message=prompt,
        )
        raw = response.answer.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        import json as _json
        data = _json.loads(raw)
        for k in default:
            if k not in data or not data[k]:
                data[k] = default[k]
        return SummarizeResponse(**{k: data.get(k, default[k]) for k in default})
    except Exception as e:
        logger.warning("Summary generation failed: %s", e)
        return SummarizeResponse(**default)
