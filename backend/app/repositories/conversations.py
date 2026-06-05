import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, Event, Message


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

    async def add_message_pair(self, first: Message, second: Message) -> tuple[Message, Message]:
        self.db.add(first)
        self.db.add(second)
        await self.db.commit()
        await self.db.refresh(first)
        await self.db.refresh(second)
        return first, second
