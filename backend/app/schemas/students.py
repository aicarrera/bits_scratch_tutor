import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StudentCodeRequest(BaseModel):
    codigo_publico: str = Field(min_length=1, max_length=80)


class StudentResponse(BaseModel):
    id: uuid.UUID
    codigo_publico: str
    grupo_id: uuid.UUID | None
    edad: int | None
    genero_opcion: str | None
    experiencia_scratch: str | None
    experiencia_ia: str | None
    activo: bool
    creado_en: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class StudentCodeResponse(BaseModel):
    estudiante: StudentResponse


class StudentCreateRequest(BaseModel):
    codigo_publico: str = Field(min_length=1, max_length=80)
    grupo_id: uuid.UUID | None = None
    edad: int | None = Field(default=None, ge=8, le=10)
    genero_opcion: str | None = None
    experiencia_scratch: str | None = None
    experiencia_ia: str | None = None
    activo: bool = True


class StudentUpdateRequest(BaseModel):
    grupo_id: uuid.UUID | None = None
    edad: int | None = Field(default=None, ge=8, le=10)
    genero_opcion: str | None = None
    experiencia_scratch: str | None = None
    experiencia_ia: str | None = None
    activo: bool | None = None
