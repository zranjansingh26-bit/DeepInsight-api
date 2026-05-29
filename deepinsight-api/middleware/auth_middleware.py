"""
DeepInsight — Auth Middleware.

Injects user context into request.state for all protected routes.
Exempt paths bypass authentication checks.
"""

import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

# Paths that do not require authentication
EXEMPT_PATHS = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
}

EXEMPT_PREFIXES = (
    "/api/auth/",
    "/api/billing/webhook",
    "/_next/",         # Next.js assets
    "/favicon",
)


class AuthContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware that:
    1. Adds a unique request ID to every request
    2. Adds timing headers
    3. Logs auth context for protected routes
    """

    async def dispatch(self, request: Request, call_next):
        import uuid

        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Skip auth checks for exempt paths
        path = request.url.path
        is_exempt = path in EXEMPT_PATHS or path.startswith(EXEMPT_PREFIXES)
        request.state.auth_exempt = is_exempt

        # Time the request
        start = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000

        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Request-Duration"] = f"{duration_ms:.1f}ms"

        return response
