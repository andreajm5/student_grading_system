from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import db_session, require_teacher
from app.models.models import Assignment, Classroom, Lesson, Submission, User
from app.schemas.schemas import GradeUpdate, SubmissionRead


router = APIRouter()


@router.post(
    "/submissions/{submission_id}/grade",
    response_model=SubmissionRead,
    status_code=status.HTTP_200_OK,
)
def grade_submission(
    submission_id: int,
    payload: GradeUpdate,
    session: Session = Depends(db_session),
    current_teacher: User = Depends(require_teacher),
) -> SubmissionRead:
    """
    Grade a submission as a teacher.

    Teachers may only grade submissions for assignments in classrooms they own.
    """
    submission = session.get(Submission, submission_id)
    if submission is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")

    assignment = session.get(Assignment, submission.assignment_id)
    if assignment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment not found")

    lesson = session.get(Lesson, assignment.lesson_id)
    classroom = session.get(Classroom, lesson.classroom_id) if lesson else None
    if classroom is None or classroom.teacher_id != current_teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to grade this submission",
        )

    if payload.score is not None:
        submission.score = payload.score
    if payload.feedback is not None:
        submission.feedback = payload.feedback
    submission.graded_at = datetime.utcnow()
    submission.graded_by = current_teacher.id

    session.add(submission)
    session.commit()
    session.refresh(submission)
    return SubmissionRead.model_validate(submission, from_attributes=True)


@router.patch(
    "/submissions/{submission_id}/grade",
    response_model=SubmissionRead,
)
def update_grade(
    submission_id: int,
    payload: GradeUpdate,
    session: Session = Depends(db_session),
    current_teacher: User = Depends(require_teacher),
) -> SubmissionRead:
    """
    Update an existing grade.

    This endpoint behaves the same as `grade_submission` but uses PATCH semantics.
    """
    return grade_submission(
        submission_id=submission_id,
        payload=payload,
        session=session,
        current_teacher=current_teacher,
    )

