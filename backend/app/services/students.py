import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Student
from app.repositories.students import StudentsRepository
from app.schemas.students import StudentCreateRequest, StudentResponse, StudentUpdateRequest
from app.services.serializers import serialize_student


class StudentsService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = StudentsRepository(db)

    async def validate_code(self, code: str) -> StudentResponse:
        student = await self.repo.get_by_code(code)
        if student is None or not student.activo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No reconozco ese código. Pídele ayuda a tu profe.",
            )
        return serialize_student(student)

    async def list_students(self) -> list[StudentResponse]:
        students = await self.repo.list()
        return [serialize_student(student) for student in students]

    async def create_student(self, payload: StudentCreateRequest) -> StudentResponse:
        student = Student(
            codigo_publico=payload.codigo_publico,
            grupo_id=payload.grupo_id,
            edad=payload.edad,
            genero_opcion=payload.genero_opcion,
            experiencia_scratch=payload.experiencia_scratch,
            experiencia_ia=payload.experiencia_ia,
            activo=payload.activo,
        )
        try:
            saved = await self.repo.create(student)
        except IntegrityError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código ya existe.") from exc
        return serialize_student(saved)

    async def update_student(self, student_id: uuid.UUID, payload: StudentUpdateRequest) -> StudentResponse:
        student = await self.repo.get(student_id)
        if student is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado.")
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(student, key, value)
        saved = await self.repo.save(student)
        return serialize_student(saved)
