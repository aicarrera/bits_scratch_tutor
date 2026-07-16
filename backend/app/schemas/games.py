import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class GameCategoryResponse(BaseModel):
    id: str
    nombre: str
    icono: str | None
    color_hex: str | None
    descripcion: str | None
    orden: int

    model_config = ConfigDict(from_attributes=True)


class GameResponse(BaseModel):
    id: str
    categoria_id: str | None
    titulo: str
    icono: str | None
    descripcion_corta: str | None
    duracion_estimada_min: int | None
    es_proyecto_libre: bool
    instruccion_nino: str
    version_juego_id: uuid.UUID | None
    version: str | None
    objetivos_pedagogicos: list[Any] = []
    color_acento: str | None = None
    url_video: str | None = None


class GamesCatalogResponse(BaseModel):
    categorias: list[GameCategoryResponse]
    juegos: list[GameResponse]


class GameVersionSummary(BaseModel):
    id: uuid.UUID
    version: str
    instruccion_nino: str
    system_prompt: str
    prompt_version: str
    creado_en: datetime | None = None
