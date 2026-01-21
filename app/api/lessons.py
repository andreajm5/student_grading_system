from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.api.deps import db_session, require_teacher
from app.models.models import Classroom, Lesson, User
from app.schemas.schemas import LessonCreate, LessonRead


router = APIRouter()


@router.post("", response_model=LessonRead, status_code=status.HTTP_201_CREATED)
def create_lesson(
    payload: LessonCreate,
    session: Session = Depends(db_session),
    current_teacher: User = Depends(require_teacher),
) -> LessonRead:
    """
    Create a lesson under a classroom owned by the current teacher.
    """
    classroom = session.get(Classroom, payload.classroom_id)
    if classroom is None or classroom.teacher_id != current_teacher.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")

    lesson = Lesson(
        classroom_id=payload.classroom_id,
        title=payload.title,
        description=payload.description,
        scheduled_at=payload.scheduled_at,
    )
    session.add(lesson)
    session.commit()
    session.refresh(lesson)
    return LessonRead.model_validate(lesson, from_attributes=True)


@router.get("/classrooms/{classroom_id}", response_model=List[LessonRead])
def list_lessons_for_classroom(
    classroom_id: int,
    session: Session = Depends(db_session),
    current_teacher: User = Depends(require_teacher),
) -> List[LessonRead]:
    """
    List lessons for a classroom owned by the current teacher.
    """
    classroom = session.get(Classroom, classroom_id)
    if classroom is None or classroom.teacher_id != current_teacher.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")

    statement = select(Lesson).where(Lesson.classroom_id == classroom_id)
    results = session.exec(statement).all()
    return [LessonRead.model_validate(item, from_attributes=True) for item in results]

