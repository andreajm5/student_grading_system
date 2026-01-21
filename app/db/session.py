import time
from contextlib import contextmanager
from typing import Iterator

from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
)


def create_db_and_tables() -> None:
    """
    Create database tables based on SQLModel metadata.

    In production, prefer running migrations with Alembic instead of
    relying on automatic table creation at startup.
    """
    from app.models import models  # noqa: F401  # Ensure models are imported

    # MySQL containers may take a few seconds to become ready.
    # We retry to avoid hard startup failures in Docker Compose.
    attempts = 20
    delay_seconds = 1
    last_error = None
    for _ in range(attempts):
        try:
            SQLModel.metadata.create_all(engine)
            return
        except Exception as exc:  # pragma: no cover
            last_error = exc
            time.sleep(delay_seconds)

    if last_error:
        raise last_error


@contextmanager
def get_session() -> Iterator[Session]:
    """
    Provide a SQLModel session for FastAPI dependencies.

    Yields:
        Session: Database session.
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

