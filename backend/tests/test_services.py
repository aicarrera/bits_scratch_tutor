from fastapi import HTTPException
import pytest

from app.llm.mock import MockTutorLLM
from app.schemas.conversations import ConversationCreateRequest
from app.schemas.sessions import SessionCreateRequest, SessionFeedbackRequest, SessionFinishRequest
from app.services.conversations import ConversationsService
from app.services.games import GamesService
from app.services.sessions import SessionsService
from app.services.students import StudentsService


async def test_validate_code_success_and_invalid(db_session) -> None:
    service = StudentsService(db_session)
    student = await service.validate_code("tigre-azul-7")
    assert student.codigo_publico == "tigre-azul-7"

    with pytest.raises(HTTPException) as exc_info:
        await service.validate_code("no-existe")
    assert exc_info.value.status_code == 404


async def test_create_session_open_conversation_and_send_mock_message(db_session, settings) -> None:
    student = await StudentsService(db_session).validate_code("tigre-azul-7")
    session = await SessionsService(db_session, settings).create_session(
        SessionCreateRequest(estudiante_id=student.id, asentimiento_aceptado=True)
    )
    catalog = await GamesService(db_session).catalog()
    assert len(catalog.juegos) >= 1

    conversations = ConversationsService(db_session, MockTutorLLM())
    conversation = await conversations.open_conversation(session.id, "ej_003")
    assert conversation.juego_id == "ej_003"
    assert conversation.mensajes[0].rol == "tutor"

    exchange = await conversations.send_message(conversation.id, "No sé cómo sumar puntos")
    assert exchange.mensaje_nino.rol == "nino"
    assert exchange.mensaje_tutor.rol == "tutor"
    assert exchange.mensaje_tutor.proveedor_llm == "mock"


async def test_reuses_active_session_and_recovers_ordered_conversation(db_session, settings) -> None:
    student = await StudentsService(db_session).validate_code("tigre-azul-7")
    sessions = SessionsService(db_session, settings)

    first_session = await sessions.create_session(SessionCreateRequest(estudiante_id=student.id, asentimiento_aceptado=True))
    second_session = await sessions.create_session(SessionCreateRequest(estudiante_id=student.id, asentimiento_aceptado=True))

    assert first_session.id == second_session.id

    conversations = ConversationsService(db_session, MockTutorLLM())
    opened = await conversations.open_conversation(first_session.id, "ej_001")
    await conversations.send_message(opened.id, "Quiero mover el gato")

    reopened = await conversations.open_conversation(second_session.id, "ej_001")
    assert reopened.id == opened.id
    assert [message.rol for message in reopened.mensajes] == ["tutor", "nino", "tutor"]
    assert [message.orden_mensaje for message in reopened.mensajes] == [1, 2, 3]


async def test_finish_session_requires_admin_code(db_session, settings) -> None:
    student = await StudentsService(db_session).validate_code("tigre-azul-7")
    service = SessionsService(db_session, settings)
    session = await service.create_session(SessionCreateRequest(estudiante_id=student.id))

    with pytest.raises(HTTPException) as exc_info:
        await service.finish_session(session.id, SessionFinishRequest(admin_code="12345"))
    assert exc_info.value.status_code == 403

    closed = await service.finish_session(session.id, SessionFinishRequest(admin_code="99999"))
    assert closed.estado == "cerrada"
    assert closed.fin_en is not None


async def test_feedback_accepts_five_level_scale(db_session, settings) -> None:
    student = await StudentsService(db_session).validate_code("demo-ia-1")
    service = SessionsService(db_session, settings)
    session = await service.create_session(SessionCreateRequest(estudiante_id=student.id))

    feedback = await service.submit_feedback(
        session.id,
        SessionFeedbackRequest(nivel_satisfaccion=5, etiqueta="muy feliz"),
    )
    assert feedback.nivel_satisfaccion == 5
    assert feedback.etiqueta == "muy feliz"
