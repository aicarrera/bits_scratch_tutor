import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import Settings, get_settings
from app.db.database import get_db
from app.llm.factory import build_llm
from app.schemas.conversations import (
    ConversationCreateRequest,
    ConversationResponse,
    GameOpenRequest,
    GameOpenResponse,
    MessageCreateRequest,
    MessageExchangeResponse,
    StudentGameHistoryResponse,
)
from app.services.conversations import ConversationsService

router = APIRouter()


@router.post("/open", response_model=GameOpenResponse)
async def open_or_resume_game(
    payload: GameOpenRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> GameOpenResponse:
    return await ConversationsService(db, build_llm(settings)).open_or_resume(payload.student_id, payload.game_id, payload.force_new)


@router.get("/history/{student_id}", response_model=StudentGameHistoryResponse)
async def get_student_game_history(
    student_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> StudentGameHistoryResponse:
    return await ConversationsService(db, build_llm(settings)).get_student_game_history(student_id)


@router.post("/", response_model=ConversationResponse)
async def open_conversation(
    payload: ConversationCreateRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ConversationResponse:
    return await ConversationsService(db, build_llm(settings)).open_conversation(payload.sesion_id, payload.juego_id)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> ConversationResponse:
    return await ConversationsService(db, build_llm(settings)).get_conversation(conversation_id)


@router.post("/{conversation_id}/messages", response_model=MessageExchangeResponse)
async def send_message(
    conversation_id: uuid.UUID,
    payload: MessageCreateRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> MessageExchangeResponse:
    return await ConversationsService(db, build_llm(settings)).send_message(conversation_id, payload.contenido)
