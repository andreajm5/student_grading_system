from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Column, Field, SQLModel
from sqlmodel.sql.sqltypes import AutoString


class UserRole(str, Enum):
    """Available user roles in the system."""

    STUDENT = "STUDENT"
    TEACHER = "TEACHER"


class UserBase(SQLModel):
    """Shared user fields."""

    # SQLModel does not allow using Field(index=True, ...) together with sa_column.
    # Define index/unique constraints directly on the SQLAlchemy Column instead.
    email: str = Field(sa_column=Column(AutoString, unique=True, index=True))
    full_name: str
    role: UserRole = Field(default=UserRole.STUDENT)


class User(UserBase, table=True):
    """User table model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str


class ClassroomBase(SQLModel):
    """Shared classroom fields."""

    name: str
    description: Optional[str] = None


class Classroom(ClassroomBase, table=True):
    """Classroom table model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    teacher_id: int = Field(foreign_key="user.id")


class ClassroomEnrollment(SQLModel, table=True):
    """Many-to-many relation between classrooms and student users."""

    classroom_id: int = Field(foreign_key="classroom.id", primary_key=True)
    student_id: int = Field(foreign_key="user.id", primary_key=True)


class LessonBase(SQLModel):
    """Shared lesson fields."""

    title: str
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class Lesson(LessonBase, table=True):
    """Lesson table model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    classroom_id: int = Field(foreign_key="classroom.id")


class AssignmentBase(SQLModel):
    """Shared assignment fields."""

    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    max_score: float = 100.0
    is_published: bool = True


class Assignment(AssignmentBase, table=True):
    """Assignment table model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lesson.id")


class SubmissionBase(SQLModel):
    """Shared submission fields."""

    content: Optional[str] = None
    file_path: Optional[str] = None


class Submission(SubmissionBase, table=True):
    """Submission table model."""

    id: Optional[int] = Field(default=None, primary_key=True)
    assignment_id: int = Field(foreign_key="assignment.id")
    student_id: int = Field(foreign_key="user.id")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

    # Grading fields
    score: Optional[float] = None
    feedback: Optional[str] = None
    graded_at: Optional[datetime] = None
    graded_by: Optional[int] = Field(default=None, foreign_key="user.id")

