"""Health check endpoint router for Depo Audio OS."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    """Public liveness health check endpoint.

    Returns HTTP 200 with {'status': 'ok'} without database or auth dependencies.
    """
    return {"status": "ok"}
