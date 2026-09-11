"""Depo Audio OS - Main FastAPI Application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.health.router import router as health_router

app = FastAPI(
    title="Depo Audio OS API",
    description="Automotive lighting workshop operating system backend API.",
    version="0.1.0",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Mount endpoints
app.include_router(health_router)
