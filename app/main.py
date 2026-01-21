from fastapi import FastAPI

from app.core.config import settings
from app.db.session import create_db_and_tables
from app.api.router import api_router


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application instance.

    Returns:
        FastAPI: Configured FastAPI application.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        version="0.1.0",
    )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.on_event("startup")
    def on_startup() -> None:
        """
        FastAPI startup hook.

        This ensures database tables are created before handling requests.
        In production, prefer running migrations with Alembic instead.
        """
        create_db_and_tables()

    @app.get("/health", tags=["health"])
    def health_check() -> dict:
        """
        Simple health check endpoint.

        Returns:
            dict: Health status payload.
        """
        return {"status": "healthy"}

    return app


app = create_app()

