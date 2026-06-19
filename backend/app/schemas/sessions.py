import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class SessionCreateRequest(BaseModel):
    estudiante_id: uuid.UUID
    asentimiento_aceptado: bool = True
    version_texto: str = "asentimiento-v1"
    dispositivo_tipo: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    id: uuid.UUID
    estudiante_id: uuid.UUID
    grupo_id: uuid.UUID | None
    inicio_en: datetime | None
    fin_en: datetime | None
    asentimiento_aceptado: bool
    dispositivo_tipo: str | None
    estado: str
    modo_llm: str

    model_config = ConfigDict(from_attributes=True)


class SessionFinishRequest(BaseModel):
    admin_code: str = Field(min_length=1, max_length=80)


class SessionFeedbackRequest(BaseModel):
    nivel_satisfaccion: int = Field(ge=1, le=5)
    etiqueta: str | None = Field(default=None, max_length=80)
    comentario_extra: str | None = Field(default=None, max_length=500)


class SessionFeedbackResponse(BaseModel):
    id: uuid.UUID
    sesion_id: uuid.UUID
    estudiante_id: uuid.UUID
    nivel_satisfaccion: int
    etiqueta: str | None
    comentario_extra: str | None
    creado_en: datetime | None

    model_config = ConfigDict(from_attributes=True)
