from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.students import StudentCodeRequest, StudentCodeResponse
from app.services.students import StudentsService

router = APIRouter()


@router.post("/validate-code", response_model=StudentCodeResponse)
async def validate_code(payload: StudentCodeRequest, db: AsyncSession = Depends(get_db)) -> StudentCodeResponse:
    student = await StudentsService(db).validate_code(payload.codigo_publico)
    return StudentCodeResponse(estudiante=student)
