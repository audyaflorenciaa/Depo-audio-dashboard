"""Supabase client factory for Depo Audio OS backend."""

from supabase import Client, create_client
from app.core.config import settings


def get_supabase_client() -> Client:
    """Create and return a Supabase client configured with the service role key.

    Note: This is a factory for subsequent domain/resource services and must NOT
    be invoked by public liveness health checks.
    """
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
