from datetime import datetime, timedelta, timezone
import hashlib
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# bcrypt has a 72-byte input limit. `bcrypt_sha256` transparently hashes long
# passwords with SHA-256 first, then applies bcrypt. This avoids runtime errors
# and is a common best practice when using bcrypt.
pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.

    Args:
        plain_password: Raw password provided by the user.
        hashed_password: Stored bcrypt hash.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Args:
        password: Raw password.

    Returns:
        str: Bcrypt hash suitable for storage.
    """
    # Safety net: if the runtime ever falls back to plain bcrypt (72-byte input limit),
    # pre-hash long inputs to avoid 500 errors during registration/login.
    if len(password.encode("utf-8")) > 72:
        password = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_minutes: Optional[int] = None) -> str:
    """
    Create a signed JWT access token.

    Args:
        data: Claims to include in the token payload.
        expires_minutes: Optional custom expiration in minutes.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire_delta = expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_delta)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Args:
        token: Encoded JWT token.

    Returns:
        dict[str, Any]: Decoded payload.

    Raises:
        JWTError: If the token is invalid or expired.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

