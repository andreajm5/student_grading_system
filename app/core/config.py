import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv


load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    """
    Read a boolean value from environment variables.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_int(name: str, default: int) -> int:
    """
    Read an integer value from environment variables.
    """
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    """
    Application settings loaded from environment variables.

    This is intentionally lightweight to avoid runtime parsing issues from complex
    dotenv values and to keep behavior stable across Python versions.
    """

    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Student Grading System")
    DEBUG: bool = _get_bool("DEBUG", True)
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")

    # Default points to MySQL exposed on the host from Docker (port 4005).
    # When running inside Docker Compose, docker-compose.yml overrides DATABASE_URL to use host `stu_grd_sys:3306`.
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mysql+mysqlconnector://root:Mjj19940919@localhost:4005/student_grading_db",
    )

    # Security / auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = _get_int("ACCESS_TOKEN_EXPIRE_MINUTES", 60)

    # CORS: comma-separated origins (dotenv-friendly)
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "")

    # File uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    MAX_UPLOAD_SIZE: int = _get_int("MAX_UPLOAD_SIZE", 10 * 1024 * 1024)

    def allowed_origins_list(self) -> List[str]:
        """
        Return allowed CORS origins as a list.
        """
        if not self.ALLOWED_ORIGINS:
            return []
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()

