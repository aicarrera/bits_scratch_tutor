import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.llm.base import TutorLLM
from app.models import Conversation, Message
from app.repositories.conversations import ConversationsRepository
from app.repositories.games import GamesRepository
from app.repositories.sessions import SessionsRepository
from app.schemas.conversations import ConversationResponse, MessageExchangeResponse
from app.services.serializers import serialize_conversation, serialize_message


class ConversationsService:
    def __init__(self, db: AsyncSession, llm: TutorLLM) -> None:
        self.db = db
        self.llm = llm
        self.repo = ConversationsRepository(db)
        self.sessions_repo = SessionsRepository(db)
        self.games_repo = GamesRepository(db)

    async def open_conversation(self, session_id: uuid.UUID, game_id: str) -> ConversationResponse:
        session = await self.sessions_repo.get(session_id)
        if session is None or session.estado != "activa":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión activa no encontrada.")
        game = await self.games_repo.get_game(game_id)
        if game is None or not game.activo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Juego no encontrado.")
        existing = await self.repo.get_active_for_session_game(session_id, game_id)
        if existing is not None:
            return serialize_conversation(existing, await self.repo.list_messages(existing.id))
        version = await self.games_repo.get_active_version(game_id)
        conversation = Conversation(
            sesion_id=session.id,
            estudiante_id=session.estudiante_id,
            juego_id=game.id,
            version_juego_id=version.id if version else None,
            metadata_json={"origen": "seleccion_juego", "modo": "libre" if game.es_proyecto_libre else "guiado"},
        )
        initial_message = Message(
            conversacion_id=uuid.uuid4(),
            sesion_id=session.id,
            estudiante_id=session.estudiante_id,
            rol="tutor",
            contenido=version.instruccion_nino if version else "Cuéntame qué quieres crear hoy.",
            orden_mensaje=1,
            proveedor_llm="system",
            modelo_llm=None,
            prompt_version=f"{game.id}_{version.version}" if version else None,
            metadata_json={"message_type": "initial_instruction"},
        )
        saved = await self.repo.create(conversation, initial_message)
        return serialize_conversation(saved, await self.repo.list_messages(saved.id))

    async def get_conversation(self, conversation_id: uuid.UUID) -> ConversationResponse:
        conversation = await self.repo.get(conversation_id)
        if conversation is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación no encontrada.")
        return serialize_conversation(conversation, await self.repo.list_messages(conversation.id))

    async def send_message(self, conversation_id: uuid.UUID, content: str) -> MessageExchangeResponse:
        conversation = await self.repo.get(conversation_id)
        if conversation is None or conversation.estado != "activa":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversación activa no encontrada.")
        game = await self.games_repo.get_game(conversation.juego_id)
        if game is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Juego no encontrado.")
        version = await self.games_repo.get_active_version(game.id)
        order = await self.repo.next_order(conversation.id)
        child_message = Message(
            conversacion_id=conversation.id,
            sesion_id=conversation.sesion_id,
            estudiante_id=conversation.estudiante_id,
            rol="nino",
            contenido=content.strip(),
            orden_mensaje=order,
            metadata_json={"source": "student_chat"},
        )
        saved_child = await self.repo.add_message(child_message)
        history = await self.repo.list_messages(conversation.id)
        reply = await self.llm.generate_reply(conversation, game, version, history, content.strip())
        tutor_metadata = {
            **reply.metadata,
            "fase": reply.fase,
            "bloques_sugeridos": reply.bloques_sugeridos,
            "razonamiento_pedagogico": reply.razonamiento_pedagogico,
            "necesita_aclaracion": reply.necesita_aclaracion,
        }
        tutor_message = Message(
            conversacion_id=conversation.id,
            sesion_id=conversation.sesion_id,
            estudiante_id=conversation.estudiante_id,
            rol="tutor",
            contenido=reply.text,
            orden_mensaje=order + 1,
            proveedor_llm=reply.provider,
            modelo_llm=reply.model,
            prompt_version=reply.prompt_version,
            input_tokens=reply.input_tokens,
            output_tokens=reply.output_tokens,
            metadata_json=tutor_metadata,
        )
        saved_tutor = await self.repo.add_message(tutor_message)
        return MessageExchangeResponse(
            mensaje_nino=serialize_message(saved_child),
            mensaje_tutor=serialize_message(saved_tutor),
        )
