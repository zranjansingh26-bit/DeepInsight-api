"""Tests for the dataset and analysis API routes (mocked Supabase)."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


# ── Mock auth dependency ─────────────────────────────────────

def _override_auth():
    """Override auth to return a fake user."""
    from models.schemas import UserContext
    return UserContext(user_id="test-user-123", email="test@example.com")


app.dependency_overrides = {}


class TestHealthEndpoints:
    """Test public health endpoints (no auth required)."""

    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "supabase_configured" in data
        assert "llm_configured" in data


class TestDatasetEndpoints:
    """Test dataset API endpoints."""

    def test_upload_no_auth(self):
        """Upload without auth should return 401."""
        response = client.post(
            "/api/datasets/upload",
            files={"file": ("test.csv", b"a,b\n1,2\n3,4", "text/csv")},
        )
        assert response.status_code == 401

    def test_get_dataset_no_auth(self):
        """Get dataset without auth should return 401."""
        response = client.get("/api/datasets/some-id")
        assert response.status_code == 401


class TestAnalysisEndpoints:
    """Test analysis API endpoints."""

    def test_run_analysis_no_auth(self):
        """Run analysis without auth should return 401."""
        response = client.post(
            "/api/analysis/run/some-id",
            json={"analysis_types": ["quality"]},
        )
        assert response.status_code == 401

    def test_get_analysis_no_auth(self):
        """Get analysis without auth should return 401."""
        response = client.get("/api/analysis/some-id/quality")
        assert response.status_code == 401


class TestChatEndpoints:
    """Test chat API endpoints."""

    def test_create_session_no_auth(self):
        response = client.post(
            "/api/chat/sessions",
            json={"dataset_id": "test-id"},
        )
        assert response.status_code == 401

    def test_send_message_no_auth(self):
        response = client.post(
            "/api/chat/some-session/message",
            json={"message": "Hello"},
        )
        assert response.status_code == 401


class TestReportEndpoints:
    """Test report API endpoints."""

    def test_generate_report_no_auth(self):
        response = client.post(
            "/api/reports/generate",
            json={"dataset_id": "test-id", "format": "json"},
        )
        assert response.status_code == 401
