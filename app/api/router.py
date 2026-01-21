from fastapi import APIRouter

from app.api import auth, users, classrooms, lessons, assignments, submissions, grading, health


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(classrooms.router, prefix="/classrooms", tags=["classrooms"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
api_router.include_router(assignments.router, prefix="/assignments", tags=["assignments"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["submissions"])
api_router.include_router(grading.router, prefix="/grading", tags=["grading"])
api_router.include_router(health.router, tags=["health"])

