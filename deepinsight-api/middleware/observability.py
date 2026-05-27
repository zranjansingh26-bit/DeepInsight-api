"""
DeepInsight — Observability Middleware.

Provides request tracing, performance metrics, and error tracking.
"""

import logging
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from threading import Lock

from fastapi import Request

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Thread-safe in-memory metrics collector for API observability."""

    def __init__(self):
        self._lock = Lock()
        self._request_count = 0
        self._error_count = 0
        self._latencies: list[float] = []
        self._endpoint_counts: dict[str, int] = defaultdict(int)
        self._status_counts: dict[int, int] = defaultdict(int)
        self._started_at = datetime.now(timezone.utc)

    def record_request(self, path: str, status_code: int, latency_ms: float):
        with self._lock:
            self._request_count += 1
            self._latencies.append(latency_ms)
            self._endpoint_counts[path] += 1
            self._status_counts[status_code] += 1
            if status_code >= 500:
                self._error_count += 1

            # Keep only last 10000 latencies to prevent memory leak
            if len(self._latencies) > 10000:
                self._latencies = self._latencies[-5000:]

    def get_summary(self) -> dict:
        with self._lock:
            latencies = sorted(self._latencies) if self._latencies else [0]
            p50 = latencies[len(latencies) // 2]
            p95 = latencies[int(len(latencies) * 0.95)]
            p99 = latencies[int(len(latencies) * 0.99)]

            return {
                "uptime_seconds": (datetime.now(timezone.utc) - self._started_at).total_seconds(),
                "total_requests": self._request_count,
                "total_errors": self._error_count,
                "error_rate": (self._error_count / max(self._request_count, 1)) * 100,
                "latency_ms": {
                    "p50": round(p50, 2),
                    "p95": round(p95, 2),
                    "p99": round(p99, 2),
                    "avg": round(sum(latencies) / max(len(latencies), 1), 2),
                },
                "top_endpoints": dict(
                    sorted(self._endpoint_counts.items(), key=lambda x: x[1], reverse=True)[:10]
                ),
                "status_distribution": dict(self._status_counts),
            }


# Global singleton
metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    return metrics
