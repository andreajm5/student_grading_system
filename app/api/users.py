from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.models import User
from app.schemas.schemas import UserRead


router = APIRouter()


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserRead:
    """
    Return the currently authenticated user.
    """
    return UserRead.model_validate(current_user, from_attributes=True)

