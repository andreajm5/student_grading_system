from fastapi import APIRouter


router = APIRouter()


@router.get("/health", summary="Health check")
def health() -> dict:
    """
    Lightweight health endpoint for monitoring.

    Returns:
        dict: Simple status payload.
    """
    return {"status": "healthy"}

