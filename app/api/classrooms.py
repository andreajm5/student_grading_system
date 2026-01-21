from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.api.deps import db_session, require_teacher
from app.models.models import Classroom, ClassroomEnrollment, User, UserRole
from app.schemas.schemas import ClassroomCreate, ClassroomRead, EnrollmentCreate


router = APIRouter()


@router.post("", response_model=ClassroomRead, status_code=status.HTTP_201_CREATED)
def create_classroom(
    payload: ClassroomCreate,
    session: Session = Depends(db_session),
    current_teacher: User = Depends(require_teacher),
) -> ClassroomRead:
    """
    Create a new classroom owned by the current teacher.
    """
    classroom = Classroom(
        name=payload.name,
        description=payload.description,
        teacher_id=current_teacher.id,
    )
    session.add(classroom)
    session.commit()
    session.refresh(classroom)
    return ClassroomRead.model_validate(classroom, from_attributes=True)


@router.get("", response_model=List[ClassroomRead])
def list_classrooms(
    session: Session = Depends(db_session),
    current_teacher: User = Depends(require_teacher),
) -> List[ClassroomRead]:
    """
    List classrooms owned by the current teacher.
    """
    statement = select(Classroom).where(Classroom.teacher_id == current_teacher.id)
    results = session.exec(statement).all()
    return [ClassroomRead.model_validate(item, from_attributes=True) for item in results]


@router.get("/{classroom_id}", response_model=ClassroomRead)
def get_classroom(
    classroom_id: int,
    session: Session = Depends(db_session),
    current_teacher: User = Depends(require_teacher),
) -> ClassroomRead:
    """
    Retrieve a classroom by ID, ensuring it belongs to the current teacher.
    """
    classroom = session.get(Classroom, classroom_id)
    if classroom is None or classroom.teacher_id != current_teacher.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")
    return ClassroomRead.model_validate(classroom, from_attributes=True)


@router.post("/{classroom_id}/enroll", status_code=status.HTTP_204_NO_CONTENT)
def enroll_student(
    classroom_id: int,
    payload: EnrollmentCreate,
    session: Session = Depends(db_session),
    current_teacher: User = Depends(require_teacher),
) -> None:
    """
    Enroll a student into a classroom.

    Only the owning teacher can enroll students into their classroom.
    """
    classroom = session.get(Classroom, classroom_id)
    if classroom is None or classroom.teacher_id != current_teacher.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")

    # Simple existence check; we only allow students to be enrolled.
    from app.models.models import User  # Local import to avoid circular dependency

    student = session.get(User, payload.student_id)
    if student is None or student.role != UserRole.STUDENT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid student_id")

    existing = session.get(
        ClassroomEnrollment, {"classroom_id": classroom_id, "student_id": payload.student_id}
    )
    if existing:
        # Idempotent enrollments: silently succeed if already enrolled.
        return

    enrollment = ClassroomEnrollment(classroom_id=classroom_id, student_id=payload.student_id)
    session.add(enrollment)
    session.commit()

