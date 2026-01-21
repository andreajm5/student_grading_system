from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlmodel import SQLModel

from app.models.models import UserRole


class Token(BaseModel):
    """Access token payload."""

    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: UserRole


class TokenData(BaseModel):
    """Decoded token data."""

    user_id: Optional[int] = None


class LoginRequest(SQLModel):
    """Schema for JSON-based login."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserCreate(SQLModel):
    """Schema for user registration."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    email: EmailStr
    full_name: str = Field(alias="fullName")
    password: str = Field(min_length=8, max_length=128)
    role: UserRole


class UserRegister(SQLModel):
    """
    Schema for role-specific registration.

    This is used by endpoints like `/auth/register/student` and `/auth/register/teacher`
    to avoid clients sending arbitrary roles.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    email: EmailStr
    full_name: str = Field(alias="fullName")
    password: str = Field(min_length=8, max_length=128)


class UserRead(SQLModel):
    """Schema for returning user data."""

    id: int
    email: EmailStr
    full_name: str
    role: UserRole


class ClassroomCreate(SQLModel):
    """Schema for classroom creation."""

    name: str
    description: Optional[str] = None


class ClassroomRead(SQLModel):
    """Schema for returning classroom data."""

    id: int
    name: str
    description: Optional[str] = None
    teacher_id: int


class LessonCreate(SQLModel):
    """Schema for lesson creation."""

    classroom_id: int
    title: str
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class LessonRead(SQLModel):
    """Schema for returning lesson data."""

    id: int
    classroom_id: int
    title: str
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class AssignmentCreate(SQLModel):
    """Schema for assignment creation."""

    lesson_id: int
    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    max_score: float = 100.0
    is_published: bool = True


class AssignmentRead(SQLModel):
    """Schema for returning assignment data."""

    id: int
    lesson_id: int
    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    max_score: float
    is_published: bool


class SubmissionCreate(SQLModel):
    """Schema for creating a submission with optional text content."""

    content: Optional[str] = None


class SubmissionRead(SQLModel):
    """Schema for returning submission data."""

    id: int
    assignment_id: int
    student_id: int
    submitted_at: datetime
    content: Optional[str] = None
    file_path: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    graded_at: Optional[datetime] = None
    graded_by: Optional[int] = None


class GradeUpdate(SQLModel):
    """Schema for grading or updating a grade."""

    score: Optional[float] = None
    feedback: Optional[str] = None


class EnrollmentCreate(SQLModel):
    """Schema for enrolling a student into a classroom."""

    student_id: int

