from app.models import Conversation, Game, GameCategory, GameVersion, LearningSession, Message, SessionFeedback, Student
from app.schemas.conversations import ConversationResponse, MessageResponse
from app.schemas.games import GameCategoryResponse, GameResponse
from app.schemas.sessions import SessionFeedbackResponse, SessionResponse
from app.schemas.students import StudentResponse


def serialize_student(student: Student) -> StudentResponse:
    return StudentResponse.model_validate(student)


def serialize_session(session: LearningSession) -> SessionResponse:
    return SessionResponse.model_validate(session)


def serialize_feedback(feedback: SessionFeedback) -> SessionFeedbackResponse:
    return SessionFeedbackResponse.model_validate(feedback)


def serialize_category(category: GameCategory) -> GameCategoryResponse:
    return GameCategoryResponse.model_validate(category)


def serialize_game(game: Game, version: GameVersion | None, category: GameCategory | None) -> GameResponse:
    return GameResponse(
        id=game.id,
        categoria_id=game.categoria_id,
        titulo=game.titulo,
        icono=game.icono,
        descripcion_corta=game.descripcion_corta,
        duracion_estimada_min=game.duracion_estimada_min,
        url_video=game.url_video,
        es_proyecto_libre=game.es_proyecto_libre,
        instruccion_nino=version.instruccion_nino if version else "Cuéntame qué quieres construir hoy.",
        version_juego_id=version.id if version else None,
        version=version.version if version else None,
        objetivos_pedagogicos=version.objetivos_pedagogicos if version else [],
        color_acento=category.color_hex if category else None,
    )


def serialize_message(message: Message) -> MessageResponse:
    meta = message.metadata_json or {}
    raw_bloques = meta.get("bloques_sugeridos", [])
    from app.schemas.conversations import BloqueSugerido
    bloques = [BloqueSugerido(**b) for b in raw_bloques if isinstance(b, dict)]
    raw_opciones = meta.get("opciones_respuesta", [])
    opciones = [o for o in raw_opciones if isinstance(o, str) and o.strip()]
    return MessageResponse(
        id=message.id,
        conversacion_id=message.conversacion_id,
        sesion_id=message.sesion_id,
        estudiante_id=message.estudiante_id,
        rol=message.rol,
        contenido=message.contenido,
        orden_mensaje=message.orden_mensaje,
        creado_en=message.creado_en,
        proveedor_llm=message.proveedor_llm,
        modelo_llm=message.modelo_llm,
        prompt_version=message.prompt_version,
        input_tokens=message.input_tokens,
        output_tokens=message.output_tokens,
        metadata=meta,
        fase=meta.get("fase"),
        bloques_sugeridos=bloques,
        opciones_respuesta=opciones,
    )


def serialize_conversation(conversation: Conversation, messages: list[Message]) -> ConversationResponse:
    return ConversationResponse(
        id=conversation.id,
        sesion_id=conversation.sesion_id,
        estudiante_id=conversation.estudiante_id,
        juego_id=conversation.juego_id,
        version_juego_id=conversation.version_juego_id,
        estado=conversation.estado,
        inicio_en=conversation.inicio_en,
        fin_en=conversation.fin_en,
        mensajes=[serialize_message(message) for message in messages],
    )
