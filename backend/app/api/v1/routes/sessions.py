import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import Settings, get_settings
from app.db.database import get_db
from app.schemas.sessions import (
    SessionCreateRequest,
    SessionFeedbackRequest,
    SessionFeedbackResponse,
    SessionFinishRequest,
    SessionResponse,
)
from app.services.sessions import SessionsService

router = APIRouter()


@router.post("/", response_model=SessionResponse)
async def create_session(
    payload: SessionCreateRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SessionResponse:
    return await SessionsService(db, settings).create_session(payload)


@router.post("/{session_id}/finish", response_model=SessionResponse)
async def finish_session(
    session_id: uuid.UUID,
    payload: SessionFinishRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SessionResponse:
    return await SessionsService(db, settings).finish_session(session_id, payload)


@router.post("/{session_id}/abandon", response_model=SessionResponse)
async def abandon_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SessionResponse:
    return await SessionsService(db, settings).abandon_session(session_id)


@router.post("/{session_id}/feedback", response_model=SessionFeedbackResponse)
async def submit_feedback(
    session_id: uuid.UUID,
    payload: SessionFeedbackRequest,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> SessionFeedbackResponse:
    return await SessionsService(db, settings).submit_feedback(session_id, payload)
