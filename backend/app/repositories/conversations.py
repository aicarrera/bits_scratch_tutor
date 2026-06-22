import uuid
from sqlalchemy import Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, Event, LearningSession, Message


class ConversationsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, conversation_id: uuid.UUID) -> Conversation | None:
        return await self.db.get(Conversation, conversation_id)

    async def get_active_for_session_game(self, session_id: uuid.UUID, game_id: str) -> Conversation | None:
        return await self.db.scalar(
            select(Conversation).where(
                Conversation.sesion_id == session_id,
                Conversation.juego_id == game_id,
                Conversation.estado == "activa",
            )
        )

    async def get_resumable_by_student_game(
        self, student_id: uuid.UUID, game_id: str
    ) -> Conversation | None:
        """Find the most recent non-closed conversation for a student+game pair."""
        return await self.db.scalar(
            select(Conversation)
            .join(LearningSession, Conversation.sesion_id == LearningSession.id)
            .where(
                Conversation.estudiante_id == student_id,
                Conversation.juego_id == game_id,
                Conversation.estado != "cerrada",
                LearningSession.estado != "cerrada",
            )
            .order_by(Conversation.inicio_en.desc())
        )

    async def get_completed_by_student_game(
        self, student_id: uuid.UUID, game_id: str
    ) -> Conversation | None:
        """Find the most recent conversation for a student+game where the teacher closed the session."""
        return await self.db.scalar(
            select(Conversation)
            .join(LearningSession, Conversation.sesion_id == LearningSession.id)
            .where(
                Conversation.estudiante_id == student_id,
                Conversation.juego_id == game_id,
                LearningSession.estado == "cerrada",
            )
            .order_by(Conversation.inicio_en.desc())
        )

    async def get_all_completions_for_student(
        self, student_id: uuid.UUID
    ) -> list[Row[tuple[Conversation, LearningSession]]]:
        """All conversations where the teacher closed the session, ordered by game then finish time."""
        result = await self.db.execute(
            select(Conversation, LearningSession)
            .join(LearningSession, Conversation.sesion_id == LearningSession.id)
            .where(
                Conversation.estudiante_id == student_id,
                LearningSession.estado == "cerrada",
            )
            .order_by(Conversation.juego_id, LearningSession.fin_en.asc())
        )
        return list(result.all())

    async def reactivate_conversation(self, conversation: Conversation) -> Conversation:
        conversation.estado = "activa"
        conversation.fin_en = None
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def create(self, conversation: Conversation, initial_message: Message) -> Conversation:
        self.db.add(conversation)
        await self.db.flush()
        initial_message.conversacion_id = conversation.id
        self.db.add(initial_message)
        self.db.add(
            Event(
                estudiante_id=conversation.estudiante_id,
                sesion_id=conversation.sesion_id,
                conversacion_id=conversation.id,
                tipo_evento="game_selected",
                payload={"game_id": conversation.juego_id},
            )
        )
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation

    async def list_messages(self, conversation_id: uuid.UUID) -> list[Message]:
        result = await self.db.scalars(
            select(Message).where(Message.conversacion_id == conversation_id).order_by(Message.orden_mensaje.asc())
        )
        return list(result)

    async def next_order(self, conversation_id: uuid.UUID) -> int:
        current = await self.db.scalar(
            select(func.max(Message.orden_mensaje)).where(Message.conversacion_id == conversation_id)
        )
        return int(current or 0) + 1

    async def add_message(self, message: Message) -> Message:
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
