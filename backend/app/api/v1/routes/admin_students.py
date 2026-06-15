import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import require_admin_code
from app.db.database import get_db
from app.schemas.students import StudentCreateRequest, StudentResponse, StudentUpdateRequest
from app.services.students import StudentsService

router = APIRouter(dependencies=[Depends(require_admin_code)])


@router.get("/", response_model=list[StudentResponse])
async def list_students(db: AsyncSession = Depends(get_db)) -> list[StudentResponse]:
    return await StudentsService(db).list_students()


@router.post("/", response_model=StudentResponse)
async def create_student(payload: StudentCreateRequest, db: AsyncSession = Depends(get_db)) -> StudentResponse:
    return await StudentsService(db).create_student(payload)


@router.patch("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: uuid.UUID,
    payload: StudentUpdateRequest,
    db: AsyncSession = Depends(get_db),
) -> StudentResponse:
    return await StudentsService(db).update_student(student_id, payload)
