from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.session import get_session
from app.models.models import User, UserRole


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def db_session() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    """
    with get_session() as session:
        yield session


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(db_session),
) -> User:
    """
    Resolve the currently authenticated user from a JWT token.

    Args:
        token: Bearer token from the Authorization header.
        session: Database session.

    Returns:
        User: Authenticated user.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except (JWTError, ValueError):
        raise credentials_exception

    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if user is None:
        raise credentials_exception

    return user


def require_teacher(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensure the current user has a teacher role.

    Args:
        current_user: Authenticated user.

    Returns:
        User: The same user if authorized.

    Raises:
        HTTPException: If the user is not a teacher.
    """
    if current_user.role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher access required",
        )
    return current_user

