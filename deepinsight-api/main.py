"""
DeepInsight Starter Suite — Main Application.

FastAPI application entry point with middleware, exception handlers,
and lifecycle events.
"""

import logging
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import sentry_sdk
import structlog
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config import get_settings
from middleware.auth_middleware import AuthContextMiddleware
from middleware.observability import get_metrics

# ── Logging Setup ────────────────────────────────────────────

settings = get_settings()

# Initialize Sentry
if getattr(settings, "sentry_dsn", None):
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        environment=settings.app_env
    )

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer() if settings.app_env == "development" else structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("deepinsight")

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)


# ── Lifecycle ────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("=" * 60)
    logger.info("  DeepInsight Starter Suite v%s", settings.app_version)
    logger.info("  Environment: %s", settings.app_env)
    logger.info("  Supabase: %s", "configured" if settings.supabase_url else "NOT configured")
    logger.info("  Anthropic: %s", "configured" if settings.has_anthropic else "not set")
    logger.info("  OpenAI: %s", "configured" if settings.has_openai else "not set")
    logger.info("=" * 60)
    logger.info("  API Docs:  http://%s:%d/docs", settings.host, settings.port)
    logger.info("  ReDoc:     http://%s:%d/redoc", settings.host, settings.port)
    logger.info("  Health:    http://%s:%d/", settings.host, settings.port)
    logger.info("=" * 60)
    yield
    logger.info("DeepInsight shutting down.")


# ── App Initialization ──────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    description=(
        "AI-powered analytics backend platform for uploading datasets, "
        "running automated data analysis, generating ML insights, "
        "and enabling conversational AI over uploaded data."
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS Middleware ──────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Custom Middleware ────────────────────────────────────────

app.add_middleware(AuthContextMiddleware)


# ── Request Logging Middleware ───────────────────────────────


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests with timing and record metrics."""
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    
    logger.info(
        "%s %s -> %d (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    
    get_metrics().record_request(
        path=request.url.path,
        status_code=response.status_code,
        latency_ms=duration_ms
    )
    
    return response


# ── Global Exception Handler ────────────────────────────────


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all exception handler for unhandled errors."""
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please try again later.",
            "type": type(exc).__name__,
        },
    )


# ── Register Routers ────────────────────────────────────────

from api.datasets import router as dataset_router
from api.analysis import router as analysis_router
from api.chat import router as chat_router
from api.reports import router as reports_router
from api.ml import router as ml_router
from api.forecast import router as forecast_router
from api.anomaly import router as anomaly_router
from api.billing import router as billing_router
from api.jobs import router as jobs_router
from api.documents import router as documents_router
from api.audit import router as audit_router
from api.connectors import router as connectors_router
from api.auth import router as auth_router
from api.admin import router as admin_router
from api.documents import router as documents_router
from api.report_editor import router as report_editor_router
from api.organizations import router as organizations_router
from api.schedules import router as schedules_router
from api.ai_utils import router as ai_utils_router

app.include_router(dataset_router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(analysis_router, prefix="/api/analysis", tags=["Analysis"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(reports_router, prefix="/api/reports", tags=["Reports"])
app.include_router(ml_router, prefix="/api/ml", tags=["Machine Learning"])
app.include_router(forecast_router, prefix="/api/forecast", tags=["Forecast"])
app.include_router(anomaly_router, prefix="/api/anomaly", tags=["Anomaly"])
app.include_router(billing_router, prefix="/api/billing", tags=["Billing"])
app.include_router(jobs_router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(documents_router, prefix="/api/documents", tags=["Documents"])
app.include_router(audit_router, prefix="/api/audit", tags=["Audit"])
app.include_router(connectors_router, prefix="/api/connectors", tags=["Connectors"])
app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(report_editor_router, prefix="/api/report-editor", tags=["Report Editor"])
app.include_router(organizations_router, prefix="/api/orgs", tags=["Organizations"])
app.include_router(schedules_router, prefix="/api/schedules", tags=["Schedules"])
app.include_router(ai_utils_router, tags=["AI Utilities"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)


@app.get("/health", tags=["Health"])
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "supabase_configured": bool(settings.supabase_url),
        "llm_configured": settings.has_anthropic or settings.has_openai,
    }


# ── Serve Landing Page ───────────────────────────────────────
import os
_current_dir = os.path.dirname(os.path.abspath(__file__))
_landing_dir = os.path.abspath(os.path.join(_current_dir, "..", "deepinsight-landing", "out"))
app.mount("/", StaticFiles(directory=_landing_dir, html=True), name="landing")