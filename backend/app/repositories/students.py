import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Student


class StudentsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_code(self, code: str) -> Student | None:
        normalized_code = code.strip().lower()
        return await self.db.scalar(select(Student).where(Student.codigo_publico == normalized_code))

    async def get(self, student_id: uuid.UUID) -> Student | None:
        return await self.db.get(Student, student_id)

    async def list(self) -> list[Student]:
        result = await self.db.scalars(select(Student).order_by(Student.creado_en.desc()))
        return list(result)

    async def create(self, student: Student) -> Student:
        student.codigo_publico = student.codigo_publico.strip().lower()
        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def save(self, student: Student) -> Student:
        await self.db.commit()
        await self.db.refresh(student)
        return student
