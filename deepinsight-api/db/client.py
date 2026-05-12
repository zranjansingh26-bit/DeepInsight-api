"""
DeepInsight Starter Suite — Supabase Client.

Provides lazily-initialized Supabase clients for both anon and
service-role access patterns.
"""

import logging
from functools import lru_cache

from supabase import Client, ClientOptions, create_client

from config import get_settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get the Supabase client using the anon key.
    Used for operations that respect Row Level Security.
    """
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_anon_key:
        logger.warning("Supabase credentials not configured — database features disabled.")
        raise RuntimeError("Supabase URL and anon key are required.")

    client = create_client(settings.supabase_url, settings.supabase_anon_key, options=ClientOptions(postgrest_client_timeout=120, storage_client_timeout=120))
    logger.info("Supabase anon client initialized.")
    return client


@lru_cache()
def get_service_client() -> Client:
    """
    Get the Supabase client using the service-role key.
    Bypasses Row Level Security — use for admin operations only.
    """
    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_service_role_key:
        logger.warning("Service-role key not configured — admin features disabled.")
        raise RuntimeError("Supabase URL and service-role key are required.")

    client = create_client(settings.supabase_url, settings.supabase_service_role_key, options=ClientOptions(postgrest_client_timeout=120, storage_client_timeout=120))
    logger.info("Supabase service-role client initialized.")
    return client