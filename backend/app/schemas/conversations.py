import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BloqueSugerido(BaseModel):
    id: str
    imagen: str
    nombre: str | None = None


class MessageResponse(BaseModel):
    id: uuid.UUID
    conversacion_id: uuid.UUID
    sesion_id: uuid.UUID
    estudiante_id: uuid.UUID
    rol: str
    contenido: str
    orden_mensaje: int
    creado_en: datetime | None
    proveedor_llm: str | None
    modelo_llm: str | None
    prompt_version: str | None
    input_tokens: int | None
    output_tokens: int | None
    metadata: dict[str, Any] = Field(default_factory=dict)
    fase: str | None = None
    bloques_sugeridos: list[BloqueSugerido] = Field(default_factory=list)


class GameOpenRequest(BaseModel):
    student_id: uuid.UUID
    game_id: str
    force_new: bool = False


class ConversationCreateRequest(BaseModel):
    sesion_id: uuid.UUID
    juego_id: str


class ConversationResponse(BaseModel):
    id: uuid.UUID
    sesion_id: uuid.UUID
    estudiante_id: uuid.UUID
    juego_id: str
    version_juego_id: uuid.UUID | None
    estado: str
    inicio_en: datetime | None
    fin_en: datetime | None
    mensajes: list[MessageResponse]

    model_config = ConfigDict(from_attributes=True)


class MessageCreateRequest(BaseModel):
    contenido: str = Field(min_length=1, max_length=4000)


class MessageExchangeResponse(BaseModel):
    mensaje_nino: MessageResponse
    mensaje_tutor: MessageResponse


class GameOpenResponse(BaseModel):
    sesion_id: uuid.UUID | None = None
    estado_sesion: str | None = None
    conversation: ConversationResponse | None = None
    ya_completado: bool = False
    historial_completado: ConversationResponse | None = None


class GameCompletionEntry(BaseModel):
    orden: int
    sesion_id: uuid.UUID
    completado_en: datetime | None
    conversation: ConversationResponse


class GameHistoryItem(BaseModel):
    game_id: str
    game_titulo: str
    game_icono: str | None
    completions: list[GameCompletionEntry]


class StudentGameHistoryResponse(BaseModel):
    historial: list[GameHistoryItem]
