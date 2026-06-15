from fastapi import APIRouter

from app.api.v1.routes import admin_students, conversations, games, sessions, students

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(games.router, prefix="/games", tags=["games"])
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])
api_router.include_router(admin_students.router, prefix="/admin/students", tags=["admin-students"])
