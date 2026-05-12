"""
DeepInsight Starter Suite — Application Configuration.

Uses Pydantic BaseSettings for validated, typed configuration
loaded from environment variables and .env files.
"""

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Supabase ──────────────────────────────────────────────
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""
    supabase_storage_bucket: str = "datasets"

    # ── LLM Providers ────────────────────────────────────────
    llm_provider: str = "Claude"  # Claude | OpenAI | Gemini
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # ── Email ────────────────────────────────────────────────
    resend_api_key: Optional[str] = None
    gmail_user: Optional[str] = None
    gmail_app_password: Optional[str] = None

    # ── Application ──────────────────────────────────────────
    app_env: str = "development"
    app_name: str = "DeepInsight Starter Suite"
    app_version: str = "1.0.0"
    log_level: str = "INFO"
    cors_origins: str = "*"

    # ── Server ───────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    # ── Limits ───────────────────────────────────────────────
    max_upload_size_mb: int = 50

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse comma-separated CORS origins."""
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def has_anthropic(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def has_openai(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def active_llm(self) -> str:
        """Return the configured LLM provider, falling back if key missing."""
        provider = self.llm_provider.strip().lower()
        if provider == "claude" and self.has_anthropic:
            return "claude"
        if provider == "openai" and self.has_openai:
            return "openai"
        if provider == "gemini" and self.has_gemini:
            return "gemini"
        # Auto-fallback order
        if self.has_anthropic:
            return "claude"
        if self.has_openai:
            return "openai"
        if self.has_gemini:
            return "gemini"
        return "none"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()