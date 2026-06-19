import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import Settings
from app.models import LearningSession, SessionFeedback
from app.repositories.sessions import SessionsRepository
from app.repositories.students import StudentsRepository
from app.schemas.sessions import (
    SessionCreateRequest,
    SessionFeedbackRequest,
    SessionFeedbackResponse,
    SessionFinishRequest,
    SessionResponse,
)
from app.services.serializers import serialize_feedback, serialize_session


class SessionsService:
    def __init__(self, db: AsyncSession, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self.repo = SessionsRepository(db)
        self.students_repo = StudentsRepository(db)

    async def create_session(self, payload: SessionCreateRequest) -> SessionResponse:
        if not payload.asentimiento_aceptado:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El asentimiento debe estar aceptado.")
        student = await self.students_repo.get(payload.estudiante_id)
        if student is None or not student.activo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado o inactivo.")
        active_session = await self.repo.get_active_for_student(student.id)
        if active_session is not None:
            return serialize_session(active_session)
        session = LearningSession(
            estudiante_id=student.id,
            grupo_id=student.grupo_id,
            asentimiento_aceptado=True,
            dispositivo_tipo=payload.dispositivo_tipo,
            modo_llm=self.settings.llm_mode,
            metadata_json=payload.metadata,
        )
        saved = await self.repo.create(session, payload.version_texto)
        return serialize_session(saved)

    async def finish_session(self, session_id: uuid.UUID, payload: SessionFinishRequest) -> SessionResponse:
        if payload.admin_code != self.settings.admin_finish_code:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Código de profesor inválido.")
        session = await self.repo.get(session_id)
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada.")
        if session.estado == "cerrada":
            return serialize_session(session)
        saved = await self.repo.close(session)
        return serialize_session(saved)

    async def submit_feedback(
        self,
        session_id: uuid.UUID,
        payload: SessionFeedbackRequest,
    ) -> SessionFeedbackResponse:
        session = await self.repo.get(session_id)
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada.")
        feedback = SessionFeedback(
            sesion_id=session.id,
            estudiante_id=session.estudiante_id,
            nivel_satisfaccion=payload.nivel_satisfaccion,
            etiqueta=payload.etiqueta,
            comentario_extra=payload.comentario_extra,
        )
        saved = await self.repo.save_feedback(feedback)
        return serialize_feedback(saved)
