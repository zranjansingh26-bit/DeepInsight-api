"""
DeepInsight Starter Suite — Report Service.

Generates JSON, HTML, and PDF reports from analysis results.
"""

import io
import json
import logging
from datetime import datetime, timezone
from typing import Any

from db import repository
from services.dataset_service import get_dataset
from models.schemas import ReportFormat

logger = logging.getLogger(__name__)


async def generate_report(
    dataset_id: str,
    report_format: ReportFormat,
    analysis_types: list[str] | None = None,
) -> dict[str, Any]:
    """
    Generate a report for a dataset in the specified format.

    Args:
        dataset_id: ID of the dataset
        report_format: Output format (json, html, pdf)
        analysis_types: Optional filter for specific analysis types

    Returns:
        Report response with content or download URL.
    """
    dataset = get_dataset(dataset_id)
    if not dataset:
        raise ValueError(f"Dataset {dataset_id} not found.")

    # Fetch all analyses
    analyses = repository.get_all_analyses(dataset_id)
    if analysis_types:
        analyses = [a for a in analyses if a["analysis_type"] in analysis_types]

    report_data = _build_report_data(dataset, analyses)

    if report_format == ReportFormat.JSON:
        return {
            "dataset_id": dataset_id,
            "format": "json",
            "content": report_data,
        }
    elif report_format == ReportFormat.HTML:
        html = _render_html_report(report_data)
        return {
            "dataset_id": dataset_id,
            "format": "html",
            "html_content": html,
        }
    elif report_format == ReportFormat.PDF:
        pdf_bytes = _generate_pdf_report(report_data)
        # Upload to storage
        storage_path = repository.upload_file_to_storage(
            user_id=dataset["user_id"],
            file_name=f"report_{dataset_id[:8]}.pdf",
            file_content=pdf_bytes,
            content_type="application/pdf",
        )
        return {
            "dataset_id": dataset_id,
            "format": "pdf",
            "download_url": storage_path,
        }
    else:
        raise ValueError(f"Unsupported report format: {report_format}")


def _build_report_data(
    dataset: dict, analyses: list[dict]
) -> dict[str, Any]:
    """Build the structured report data."""
    return {
        "title": f"DeepInsight Report — {dataset['file_name']}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "id": dataset["id"],
            "file_name": dataset["file_name"],
            "file_type": dataset["file_type"],
            "row_count": dataset["row_count"],
            "column_count": dataset["column_count"],
            "quality_score": dataset["quality_score"],
            "null_percentage": dataset["null_percentage"],
            "columns": dataset.get("column_metadata", []),
        },
        "analyses": [
            {
                "type": a["analysis_type"],
                "results": a["results"],
                "chart_count": len(a.get("charts", [])),
                "created_at": a["created_at"],
            }
            for a in analyses
        ],
        "summary": {
            "total_analyses": len(analyses),
            "analysis_types": [a["analysis_type"] for a in analyses],
        },
    }


def _render_html_report(report_data: dict) -> str:
    """Render an HTML report from report data."""
    dataset = report_data["dataset"]
    analyses = report_data["analyses"]

    analyses_html = ""
    for a in analyses:
        results_json = json.dumps(a["results"], indent=2, default=str)
        analyses_html += f"""
        <div class="card">
            <h3>{a['type'].replace('_', ' ').title()}</h3>
            <p class="meta">Generated: {a.get('created_at', 'N/A')}</p>
            <pre><code>{results_json}</code></pre>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_data['title']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: #0f172a; color: #e2e8f0;
            padding: 2rem; line-height: 1.6;
        }}
        .container {{ max-width: 960px; margin: 0 auto; }}
        h1 {{
            font-size: 1.8rem; margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        h2 {{ font-size: 1.3rem; margin: 1.5rem 0 0.75rem; color: #a5b4fc; }}
        h3 {{ font-size: 1.1rem; color: #c4b5fd; margin-bottom: 0.5rem; }}
        .card {{
            background: #1e293b; border-radius: 12px;
            padding: 1.25rem; margin-bottom: 1rem;
            border: 1px solid #334155;
        }}
        .meta {{ font-size: 0.8rem; color: #64748b; margin-bottom: 0.5rem; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.75rem; }}
        .stat {{
            background: #1e293b; border-radius: 8px; padding: 1rem;
            text-align: center; border: 1px solid #334155;
        }}
        .stat-value {{ font-size: 1.5rem; font-weight: 700; color: #6366f1; }}
        .stat-label {{ font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem; }}
        pre {{
            background: #0f172a; border-radius: 8px; padding: 1rem;
            overflow-x: auto; font-size: 0.8rem; color: #cbd5e1;
        }}
        .footer {{
            margin-top: 2rem; padding-top: 1rem;
            border-top: 1px solid #334155;
            font-size: 0.75rem; color: #64748b; text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{report_data['title']}</h1>
        <p class="meta">Generated: {report_data['generated_at']}</p>

        <h2>Dataset Overview</h2>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{dataset['row_count']:,}</div>
                <div class="stat-label">Rows</div>
            </div>
            <div class="stat">
                <div class="stat-value">{dataset['column_count']}</div>
                <div class="stat-label">Columns</div>
            </div>
            <div class="stat">
                <div class="stat-value">{dataset['quality_score']}%</div>
                <div class="stat-label">Quality Score</div>
            </div>
            <div class="stat">
                <div class="stat-value">{dataset['null_percentage']}%</div>
                <div class="stat-label">Null %</div>
            </div>
        </div>

        <h2>Analysis Results ({report_data['summary']['total_analyses']})</h2>
        {analyses_html}

        <div class="footer">
            DeepInsight Starter Suite &mdash; AI-Powered Analytics
        </div>
    </div>
</body>
</html>"""
    return html


def _generate_pdf_report(report_data: dict) -> bytes:
    """Generate a PDF report using fpdf2."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, report_data["title"], new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, f"Generated: {report_data['generated_at']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    # Dataset overview
    dataset = report_data["dataset"]
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Dataset Overview", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"File: {dataset['file_name']}  |  Type: {dataset['file_type']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Rows: {dataset['row_count']:,}  |  Columns: {dataset['column_count']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Quality Score: {dataset['quality_score']}%  |  Null: {dataset['null_percentage']}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # Analyses
    for a in report_data["analyses"]:
        pdf.set_font("Helvetica", "B", 12)
        title = a["type"].replace("_", " ").title()
        pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Courier", "", 8)
        results_text = json.dumps(a["results"], indent=2, default=str)
        # Truncate long results for PDF
        if len(results_text) > 3000:
            results_text = results_text[:3000] + "\n... [truncated]"
        for line in results_text.split("\n"):
            pdf.cell(0, 4, line[:120], new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    # Footer
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 6, "DeepInsight Starter Suite - AI-Powered Analytics", new_x="LMARGIN", new_y="NEXT", align="C")

    return pdf.output()
