import uuid
from datetime import date, datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin


class Group(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "grupos"

    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    descripcion: Mapped[str | None] = mapped_column(Text)
    fecha_inicio: Mapped[date | None] = mapped_column(Date)
    fecha_fin: Mapped[date | None] = mapped_column(Date)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")


class AppUser(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "usuarios_app"
    __table_args__ = (
        CheckConstraint(
            "rol IN ('researcher','teacher','technical_admin','super_admin')",
            name="ck_usuarios_app_rol",
        ),
    )

    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    nombre_completo: Mapped[str] = mapped_column(Text, nullable=False)
    rol: Mapped[str] = mapped_column(String(32), nullable=False)
    grupo_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("grupos.id", ondelete="SET NULL"))
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    ultimo_acceso_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Student(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "estudiantes"
    __table_args__ = (
        CheckConstraint("edad IS NULL OR edad BETWEEN 8 AND 10", name="ck_estudiantes_edad"),
        CheckConstraint(
            "genero_opcion IS NULL OR genero_opcion IN ('femenino','masculino','prefiero_no_decir','otro')",
            name="ck_estudiantes_genero",
        ),
        CheckConstraint(
            "experiencia_scratch IS NULL OR experiencia_scratch IN ('ninguna','un_poco','mucha')",
            name="ck_estudiantes_experiencia_scratch",
        ),
        CheckConstraint(
            "experiencia_ia IS NULL OR experiencia_ia IN ('ninguna','alguna','frecuente')",
            name="ck_estudiantes_experiencia_ia",
        ),
    )

    codigo_publico: Mapped[str] = mapped_column(Text, unique=True, nullable=False, index=True)
    grupo_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("grupos.id", ondelete="SET NULL"))
    nombre_completo: Mapped[str | None] = mapped_column(Text)
    email_referencia: Mapped[str | None] = mapped_column(Text)
    notas_investigador: Mapped[str | None] = mapped_column(Text)
    edad: Mapped[int | None] = mapped_column(SmallInteger)
    genero_opcion: Mapped[str | None] = mapped_column(String(32))
    experiencia_scratch: Mapped[str | None] = mapped_column(String(32))
    experiencia_ia: Mapped[str | None] = mapped_column(String(32))
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")


class GameCategory(Base):
    __tablename__ = "categorias_juego"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    nombre: Mapped[str] = mapped_column(Text, nullable=False)
    icono: Mapped[str | None] = mapped_column(Text)
    color_hex: Mapped[str | None] = mapped_column(Text)
    descripcion: Mapped[str | None] = mapped_column(Text)
    orden: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=0, server_default="0")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")


class Game(CreatedAtMixin, Base):
    __tablename__ = "juegos"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    categoria_id: Mapped[str | None] = mapped_column(
        ForeignKey("categorias_juego.id", ondelete="SET NULL"),
        index=True,
    )
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    icono: Mapped[str | None] = mapped_column(Text)
    descripcion_corta: Mapped[str | None] = mapped_column(Text)
    url_video: Mapped[str | None] = mapped_column(Text)
    duracion_estimada_min: Mapped[int | None] = mapped_column(SmallInteger)
    es_proyecto_libre: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    categoria: Mapped[GameCategory | None] = relationship()


class GameVersion(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "versiones_juego"
    __table_args__ = (UniqueConstraint("juego_id", "version", name="uq_versiones_juego_juego_version"),)

    juego_id: Mapped[str] = mapped_column(ForeignKey("juegos.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[str] = mapped_column(Text, nullable=False)
    instruccion_nino: Mapped[str] = mapped_column(Text, nullable=False)
    objetivos_pedagogicos: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    pistas_progresivas: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    criterios_completado: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    preguntas_frecuentes_esperadas: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")


class LearningSession(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "sesiones"
    __table_args__ = (
        CheckConstraint(
            "estado IN ('activa','cerrada','abandonada','anulada')",
            name="ck_sesiones_estado",
        ),
    )

    estudiante_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False, index=True)
    grupo_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("grupos.id", ondelete="SET NULL"), index=True)
    inicio_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    fin_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    asentimiento_aceptado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    dispositivo_tipo: Mapped[str | None] = mapped_column(Text)
    estado: Mapped[str] = mapped_column(String(16), nullable=False, default="activa", server_default="activa")
    modo_llm: Mapped[str] = mapped_column(String(16), nullable=False, default="mock", server_default="mock")
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)


class Assent(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "asentimientos"

    sesion_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sesiones.id", ondelete="CASCADE"), nullable=False, index=True)
    estudiante_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False, index=True)
    version_texto: Mapped[str] = mapped_column(Text, nullable=False)
    aceptado: Mapped[bool] = mapped_column(Boolean, nullable=False)
    aceptado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class Conversation(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "conversaciones"
    __table_args__ = (
        CheckConstraint("estado IN ('activa','cerrada','abandonada')", name="ck_conversaciones_estado"),
    )

    sesion_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sesiones.id", ondelete="CASCADE"), nullable=False, index=True)
    estudiante_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False, index=True)
    juego_id: Mapped[str] = mapped_column(ForeignKey("juegos.id", ondelete="RESTRICT"), nullable=False, index=True)
    version_juego_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("versiones_juego.id", ondelete="SET NULL"))
    estado: Mapped[str] = mapped_column(String(16), nullable=False, default="activa", server_default="activa")
    inicio_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    fin_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)


class Message(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "mensajes"
    __table_args__ = (
        CheckConstraint("rol IN ('nino','tutor','sistema')", name="ck_mensajes_rol"),
        CheckConstraint("input_tokens IS NULL OR input_tokens >= 0", name="ck_mensajes_input_tokens"),
        CheckConstraint("output_tokens IS NULL OR output_tokens >= 0", name="ck_mensajes_output_tokens"),
        UniqueConstraint("conversacion_id", "orden_mensaje", name="uq_mensajes_conversacion_orden"),
    )

    conversacion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversaciones.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sesion_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sesiones.id", ondelete="CASCADE"), nullable=False, index=True)
    estudiante_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False, index=True)
    rol: Mapped[str] = mapped_column(String(16), nullable=False)
    contenido: Mapped[str] = mapped_column(Text, nullable=False)
    orden_mensaje: Mapped[int] = mapped_column(Integer, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    proveedor_llm: Mapped[str | None] = mapped_column(Text)
    modelo_llm: Mapped[str | None] = mapped_column(Text)
    prompt_version: Mapped[str | None] = mapped_column(Text)
    input_tokens: Mapped[int | None] = mapped_column(Integer)
    output_tokens: Mapped[int | None] = mapped_column(Integer)
    metadata_json: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, nullable=False, default=dict)


class Event(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "eventos"

    estudiante_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("estudiantes.id", ondelete="CASCADE"), index=True)
    sesion_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sesiones.id", ondelete="CASCADE"), index=True)
    conversacion_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("conversaciones.id", ondelete="SET NULL"), index=True)
    tipo_evento: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)


class SessionFeedback(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "feedback_sesion"
    __table_args__ = (
        CheckConstraint("nivel_satisfaccion BETWEEN 1 AND 5", name="ck_feedback_nivel_satisfaccion"),
        UniqueConstraint("sesion_id", name="uq_feedback_sesion"),
    )

    sesion_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("sesiones.id", ondelete="CASCADE"), nullable=False, index=True)
    estudiante_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("estudiantes.id", ondelete="CASCADE"), nullable=False, index=True)
    nivel_satisfaccion: Mapped[int] = mapped_column(SmallInteger, nullable=False, index=True)
    etiqueta: Mapped[str | None] = mapped_column(Text)
    comentario_extra: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class ExportLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "exportaciones"
    __table_args__ = (
        CheckConstraint("formato IN ('json','csv')", name="ck_exportaciones_formato"),
        CheckConstraint(
            "alcance IN ('sesiones','mensajes','feedback','eventos','dataset_completo')",
            name="ck_exportaciones_alcance",
        ),
        CheckConstraint("total_registros IS NULL OR total_registros >= 0", name="ck_exportaciones_total"),
    )

    solicitado_por: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("usuarios_app.id", ondelete="SET NULL"), index=True)
    formato: Mapped[str] = mapped_column(String(8), nullable=False)
    alcance: Mapped[str] = mapped_column(String(32), nullable=False)
    filtros: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    total_registros: Mapped[int | None] = mapped_column(Integer)
    archivo_path: Mapped[str | None] = mapped_column(Text)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)


class AuditLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "auditoria"

    usuario_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("usuarios_app.id", ondelete="SET NULL"), index=True)
    accion: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    entidad: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    entidad_id: Mapped[str | None] = mapped_column(Text)
    detalle: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
