from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import db_session, require_teacher
from app.models.models import Assignment, Classroom, Lesson
from app.models.models import User
from app.schemas.schemas import AssignmentCreate, AssignmentRead


router = APIRouter()


def _ensure_lesson_owned_by_teacher(
    session: Session,
    lesson_id: int,
    teacher_id: int,
) -> Lesson:
    """
    Ensure the lesson belongs to a classroom owned by the given teacher.

    Args:
        session: Database session.
        lesson_id: Target lesson ID.
        teacher_id: Teacher user ID.

    Returns:
        Lesson: The resolved lesson.

    Raises:
        HTTPException: If the lesson or classroom is not found or unauthorized.
    """
    lesson = session.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")

    classroom = session.get(Classroom, lesson.classroom_id)
    if classroom is None or classroom.teacher_id != teacher_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to manage assignments for this lesson",
        )
    return lesson


@router.post("", response_model=AssignmentRead, status_code=status.HTTP_201_CREATED)
def create_assignment(
    payload: AssignmentCreate,
    session: Session = Depends(db_session),
    current_teacher: User = Depends(require_teacher),
) -> AssignmentRead:
    """
    Create an assignment under a lesson owned by the current teacher.
    """
    _ensure_lesson_owned_by_teacher(session, payload.lesson_id, current_teacher.id)

    assignment = Assignment(
        lesson_id=payload.lesson_id,
        title=payload.title,
        description=payload.description,
        due_at=payload.due_at,
        max_score=payload.max_score,
        is_published=payload.is_published,
    )
    session.add(assignment)
    session.commit()
    session.refresh(assignment)
    return AssignmentRead.model_validate(assignment, from_attributes=True)


@router.get("/lessons/{lesson_id}", response_model=List[AssignmentRead])
def list_assignments_for_lesson(
    lesson_id: int,
    session: Session = Depends(db_session),
    current_teacher: User = Depends(require_teacher),
) -> List[AssignmentRead]:
    """
    List assignments for a lesson owned by the current teacher.
    """
    _ensure_lesson_owned_by_teacher(session, lesson_id, current_teacher.id)
    statement = select(Assignment).where(Assignment.lesson_id == lesson_id)
    results = session.exec(statement).all()
    return [AssignmentRead.model_validate(item, from_attributes=True) for item in results]


@router.get("/{assignment_id}", response_model=AssignmentRead)
def get_assignment(
    assignment_id: int,
    session: Session = Depends(db_session),
    current_teacher: User = Depends(require_teacher),
) -> AssignmentRead:
    """
    Retrieve a single assignment, ensuring it is under a lesson owned by the current teacher.
    """
    assignment = session.get(Assignment, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    _ensure_lesson_owned_by_teacher(session, assignment.lesson_id, current_teacher.id)
    return AssignmentRead.model_validate(assignment, from_attributes=True)

