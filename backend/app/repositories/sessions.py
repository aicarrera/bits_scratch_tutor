import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Assent, Conversation, Event, LearningSession, SessionFeedback


class SessionsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, session_id: uuid.UUID) -> LearningSession | None:
        return await self.db.get(LearningSession, session_id)

    async def create(self, session: LearningSession, assent_version: str) -> LearningSession:
        self.db.add(session)
        await self.db.flush()
        self.db.add(
            Assent(
                sesion_id=session.id,
                estudiante_id=session.estudiante_id,
                version_texto=assent_version,
                aceptado=session.asentimiento_aceptado,
            )
        )
        self.db.add(
            Event(
                estudiante_id=session.estudiante_id,
                sesion_id=session.id,
                tipo_evento="session_started",
                payload={"assent_version": assent_version},
            )
        )
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def close(self, session: LearningSession) -> LearningSession:
        now = datetime.now(timezone.utc)
        session.estado = "cerrada"
        session.fin_en = now
        active_conversations = await self.db.scalars(
            select(Conversation).where(Conversation.sesion_id == session.id, Conversation.estado == "activa")
        )
        for conversation in active_conversations:
            conversation.estado = "cerrada"
            conversation.fin_en = now
        self.db.add(
            Event(
                estudiante_id=session.estudiante_id,
                sesion_id=session.id,
                tipo_evento="session_closed",
                payload={"closed_by": "teacher_code"},
            )
        )
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def abandon(self, session: LearningSession) -> LearningSession:
        now = datetime.now(timezone.utc)
        session.estado = "abandonada"
        session.fin_en = now
        active_conversations = await self.db.scalars(
            select(Conversation).where(Conversation.sesion_id == session.id, Conversation.estado == "activa")
        )
        for conversation in active_conversations:
            conversation.estado = "abandonada"
            conversation.fin_en = now
        self.db.add(
            Event(
                estudiante_id=session.estudiante_id,
                sesion_id=session.id,
                tipo_evento="session_abandoned",
                payload={"closed_by": "student_exit"},
            )
        )
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def reactivate(self, session: LearningSession) -> LearningSession:
        session.estado = "activa"
        session.fin_en = None
        self.db.add(
            Event(
                estudiante_id=session.estudiante_id,
                sesion_id=session.id,
                tipo_evento="session_reactivated",
                payload={"from_estado": "abandonada"},
            )
        )
        await self.db.commit()
        await self.db.refresh(session)
        return session

    async def save_feedback(self, feedback: SessionFeedback) -> SessionFeedback:
        existing = await self.db.scalar(select(SessionFeedback).where(SessionFeedback.sesion_id == feedback.sesion_id))
        if existing is not None:
            existing.nivel_satisfaccion = feedback.nivel_satisfaccion
            existing.etiqueta = feedback.etiqueta
            existing.comentario_extra = feedback.comentario_extra
            saved = existing
        else:
            self.db.add(feedback)
            saved = feedback
        self.db.add(
            Event(
                estudiante_id=feedback.estudiante_id,
                sesion_id=feedback.sesion_id,
                tipo_evento="feedback_submitted",
                payload={"nivel_satisfaccion": feedback.nivel_satisfaccion, "etiqueta": feedback.etiqueta},
            )
        )
        await self.db.commit()
        await self.db.refresh(saved)
        return saved
