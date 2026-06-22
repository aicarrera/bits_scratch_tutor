import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import get_settings
from app.llm.base import TutorLLM
from app.models import Conversation, LearningSession, Message
from app.repositories.conversations import ConversationsRepository
from app.repositories.games import GamesRepository
from app.repositories.sessions import SessionsRepository
from app.repositories.students import StudentsRepository
from app.schemas.conversations import (
    ConversationResponse,
    GameCompletionEntry,
    GameHistoryItem,
    GameOpenRequest,
    GameOpenResponse,
    MessageExchangeResponse,
    StudentGameHistoryResponse,
)
from app.services.serializers import serialize_conversation, serialize_message


class ConversationsService:
    def __init__(self, db: AsyncSession, llm: TutorLLM) -> None:
        self.db = db
        self.llm = llm
        self.repo = ConversationsRepository(db)
        self.sessions_repo = SessionsRepository(db)
        self.games_repo = GamesRepository(db)

    async def open_or_resume(self, student_id: uuid.UUID, game_id: str, force_new: bool = False) -> GameOpenResponse:
        game = await self.games_repo.get_game(game_id)
        if game is None or not game.activo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Juego no encontrado.")
        student = await StudentsRepository(self.db).get(student_id)
        if student is None or not student.activo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudiante no encontrado.")

        if not force_new:
            # Resume existing conversation if the session was never teacher-closed
            resumable = await self.repo.get_resumable_by_student_game(student_id, game_id)
            if resumable is not None:
                session = await self.sessions_repo.get(resumable.sesion_id)
                if session is not None and session.estado == "abandonada":
                    session = await self.sessions_repo.reactivate(session)
                    resumable = await self.repo.reactivate_conversation(resumable)
                messages = await self.repo.list_messages(resumable.id)
                return GameOpenResponse(
                    sesion_id=session.id,
                    estado_sesion=session.estado,
                    conversation=serialize_conversation(resumable, messages),
                )

            # Game was teacher-finished: show completed modal, no new session yet
            completed_conv = await self.repo.get_completed_by_student_game(student_id, game_id)
            if completed_conv is not None:
                messages = await self.repo.list_messages(completed_conv.id)
                return GameOpenResponse(
                    ya_completado=True,
                    historial_completado=serialize_conversation(completed_conv, messages),
                )

        # Create a brand-new session + conversation
        settings = get_settings()
        new_session = LearningSession(
            estudiante_id=student.id,
            grupo_id=student.grupo_id,
            asentimiento_aceptado=True,
            modo_llm=settings.llm_mode,
            metadata_json={"origen": "game_selection"},
        )
        saved_session = await self.sessions_repo.create(new_session, "asentimiento-v1")
        version = await self.games_repo.get_active_version(game_id)
        conversation = Conversation(
            sesion_id=saved_session.id,
            estudiante_id=student.id,
            juego_id=game.id,
            version_juego_id=version.id if version else None,
            metadata_json={"origen": "game_selection", "modo": "libre" if game.es_proyecto_libre else "guiado"},
        )
        initial_message = Message(
            conversacion_id=uuid.uuid4(),
            sesion_id=saved_session.id,
            estudiante_id=student.id,
            rol="tutor",
            contenido=version.instruccion_nino if version else "Cuéntame qué quieres crear hoy.",
            orden_mensaje=1,
            proveedor_llm="system",
            modelo_llm=None,
            prompt_version=f"{game.id}_{version.version}" if version else None,
            metadata_json={"message_type": "initial_instruction"},
        )
        saved_conv = await self.repo.create(conversation, initial_message)
        return GameOpenResponse(
            sesion_id=saved_session.id,
            estado_sesion=saved_session.estado,
            conversation=serialize_conversation(saved_conv, await self.repo.list_messages(saved_conv.id)),
        )

    async def get_student_game_history(self, student_id: uuid.UUID) -> StudentGameHistoryResponse:
        rows = await self.repo.get_all_completions_for_student(student_id)
        groups: dict[str, list] = {}
        for row in rows:
            conv, session = row[0], row[1]
            if conv.juego_id not in groups:
                groups[conv.juego_id] = []
            groups[conv.juego_id].append((conv, session))

        historial: list[GameHistoryItem] = []
        for game_id, completions in groups.items():
            game = await self.games_repo.get_game(game_id)
            entries: list[GameCompletionEntry] = []
            for orden, (conv, session) in enumerate(completions, start=1):
                messages = await self.repo.list_messages(conv.id)
                entries.append(
                    GameCompletionEntry(
                        orden=orden,
                        sesion_id=session.id,
                        completado_en=session.fin_en,
                        conversation=serialize_conversation(conv, messages),
                    )
                )
            historial.append(
                GameHistoryItem(
                    game_id=game_id,
                    game_titulo=game.titulo if game else game_id,
                    game_icono=game.icono if game else None,
                    completions=entries,
                )
            )
        return StudentGameHistoryResponse(historial=historial)

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
