"""Configuration loader for Depo Audio OS backend."""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Union
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator

# Locate and load .env file from the backend root directory
ENV_PATH = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)


class Settings(BaseModel):
    """Application settings validated via Pydantic."""

    supabase_url: str
    supabase_service_role_key: str
    supabase_jwt_secret: str
    cors_allowed_origins: List[str] = ["http://localhost:5173"]

    @field_validator("cors_allowed_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            origins = [origin.strip() for origin in v.split(",") if origin.strip()]
            return origins if origins else ["http://localhost:5173"]
        return v


def load_settings() -> Settings:
    """Load and validate settings from environment variables."""
    raw_cors = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173")
    return Settings(
        supabase_url=os.getenv("SUPABASE_URL"),  # type: ignore[arg-type]
        supabase_service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),  # type: ignore[arg-type]
        supabase_jwt_secret=os.getenv("SUPABASE_JWT_SECRET"),  # type: ignore[arg-type]
        cors_allowed_origins=raw_cors,
    )


# Module-level singleton instance - fails fast at startup if configuration is invalid
settings = load_settings()
