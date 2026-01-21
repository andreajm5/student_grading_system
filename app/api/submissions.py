import os
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlmodel import Session, select

from app.api.deps import db_session, get_current_user
from app.core.config import settings
from app.models.models import Assignment, Classroom, ClassroomEnrollment, Lesson, Submission, User, UserRole
from app.schemas.schemas import SubmissionCreate, SubmissionRead


router = APIRouter()


def _ensure_student_enrolled_for_assignment(
    session: Session,
    assignment: Assignment,
    student_id: int,
) -> None:
    """
    Ensure the student is enrolled in the classroom associated with the assignment.

    Args:
        session: Database session.
        assignment: Assignment entity.
        student_id: Student user ID.

    Raises:
        HTTPException: If the student is not enrolled.
    """
    lesson = session.get(Lesson, assignment.lesson_id)
    if lesson is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    classroom = session.get(Classroom, lesson.classroom_id)
    if classroom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Classroom not found")

    enrollment = session.get(
        ClassroomEnrollment,
        {"classroom_id": classroom.id, "student_id": student_id},
    )
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student is not enrolled in this classroom",
        )


def _save_uploaded_file(file: UploadFile) -> str:
    """
    Persist an uploaded file to disk and return its path.

    Args:
        file: Incoming uploaded file.

    Returns:
        str: Relative file path where the file is stored.
    """
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
    safe_name = file.filename or "submission"
    file_name = f"{timestamp}_{safe_name}"
    file_path = os.path.join(settings.UPLOAD_DIR, file_name)

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    return file_path


@router.post(
    "/assignments/{assignment_id}/submissions",
    response_model=SubmissionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_submission(
    assignment_id: int,
    session: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
    payload: SubmissionCreate = Depends(),
    file: Optional[UploadFile] = File(default=None),
) -> SubmissionRead:
    """
    Create a submission for an assignment as a student.

    The current user must be a STUDENT and enrolled in the classroom for the assignment.
    """
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can create submissions",
        )

    assignment = session.get(Assignment, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    _ensure_student_enrolled_for_assignment(session, assignment, current_user.id)

    file_path: Optional[str] = None
    if file is not None:
        file.file.seek(0, os.SEEK_END)
        size = file.file.tell()
        file.file.seek(0)
        if size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is too large",
            )
        file_path = _save_uploaded_file(file)

    submission = Submission(
        assignment_id=assignment_id,
        student_id=current_user.id,
        content=payload.content,
        file_path=file_path,
    )
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return SubmissionRead.model_validate(submission, from_attributes=True)


@router.get(
    "/assignments/{assignment_id}/submissions",
    response_model=List[SubmissionRead],
)
def list_submissions_for_assignment(
    assignment_id: int,
    session: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> List[SubmissionRead]:
    """
    List submissions for an assignment.

    - Teachers can view all submissions for assignments they own.
    - Students can only view their own submissions.
    """
    assignment = session.get(Assignment, assignment_id)
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    if current_user.role == UserRole.TEACHER:
        # Ensure teacher owns the classroom via lesson->classroom.
        lesson = session.get(Lesson, assignment.lesson_id)
        if lesson is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
        classroom = session.get(Classroom, lesson.classroom_id)
        if classroom is None or classroom.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view submissions for this assignment",
            )
        statement = select(Submission).where(Submission.assignment_id == assignment_id)
    else:
        # Student: restrict to own submissions.
        statement = select(Submission).where(
            Submission.assignment_id == assignment_id,
            Submission.student_id == current_user.id,
        )

    results = session.exec(statement).all()
    return [SubmissionRead.model_validate(item, from_attributes=True) for item in results]


@router.get("/{submission_id}", response_model=SubmissionRead)
def get_submission(
    submission_id: int,
    session: Session = Depends(db_session),
    current_user: User = Depends(get_current_user),
) -> SubmissionRead:
    """
    Retrieve a single submission.

    - Students can only view their own submissions.
    - Teachers can view submissions for assignments they own.
    """
    submission = session.get(Submission, submission_id)
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    assignment = session.get(Assignment, submission.assignment_id)
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    if current_user.role == UserRole.STUDENT and submission.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this submission",
        )

    if current_user.role == UserRole.TEACHER:
        lesson = session.get(Lesson, assignment.lesson_id)
        classroom = session.get(Classroom, lesson.classroom_id) if lesson else None
        if classroom is None or classroom.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this submission",
            )

    return SubmissionRead.model_validate(submission, from_attributes=True)

