from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.api.deps import db_session
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.models import User, UserRole
from app.schemas.schemas import LoginRequest, Token, UserCreate, UserRead, UserRegister


router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, session: Session = Depends(db_session)) -> UserRead:
    """
    Register a new user.

    Email uniqueness is enforced at the application level before insertion.
    """
    existing = session.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        role=payload.role,
        hashed_password=get_password_hash(payload.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserRead.model_validate(user, from_attributes=True)


@router.post("/register/student", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_student(payload: UserRegister, session: Session = Depends(db_session)) -> UserRead:
    """
    Register a new STUDENT user.
    """
    return register_user(
        UserCreate(
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password,
            role=UserRole.STUDENT,
        ),
        session=session,
    )


@router.post("/register/teacher", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_teacher(payload: UserRegister, session: Session = Depends(db_session)) -> UserRead:
    """
    Register a new TEACHER user.
    """
    return register_user(
        UserCreate(
            email=payload.email,
            full_name=payload.full_name,
            password=payload.password,
            role=UserRole.TEACHER,
        ),
        session=session,
    )


@router.post("/login", response_model=Token)
def login(
    session: Session = Depends(db_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    Authenticate a user and return a JWT access token.

    The OAuth2 password flow sends username and password as form fields.
    """
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    # The access token embeds the user ID and role in JWT claims.
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return Token(access_token=access_token, user_id=user.id, role=user.role)


@router.post("/login/json", response_model=Token)
def login_json(payload: LoginRequest, session: Session = Depends(db_session)) -> Token:
    """
    Authenticate a user and return a JWT access token (JSON body).

    This endpoint is easier to use than OAuth2PasswordRequestForm in many clients.
    """
    statement = select(User).where(User.email == payload.email)
    user = session.exec(statement).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return Token(access_token=access_token, user_id=user.id, role=user.role)

