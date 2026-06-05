"""Initial CreaBits Tutor schema.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-05
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "grupos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nombre", sa.Text(), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("fecha_inicio", sa.Date(), nullable=True),
        sa.Column("fecha_fin", sa.Date(), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_grupos_activo", "grupos", ["activo"])

    op.create_table(
        "usuarios_app",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("nombre_completo", sa.Text(), nullable=False),
        sa.Column("rol", sa.String(length=32), nullable=False),
        sa.Column("grupo_id", sa.Uuid(), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ultimo_acceso_en", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "rol IN ('researcher','teacher','technical_admin','super_admin')",
            name="ck_usuarios_app_rol",
        ),
        sa.ForeignKeyConstraint(["grupo_id"], ["grupos.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_usuarios_app_grupo_id", "usuarios_app", ["grupo_id"])
    op.create_index("ix_usuarios_app_rol", "usuarios_app", ["rol"])

    op.create_table(
        "estudiantes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("codigo_publico", sa.Text(), nullable=False),
        sa.Column("grupo_id", sa.Uuid(), nullable=True),
        sa.Column("edad", sa.SmallInteger(), nullable=True),
        sa.Column("genero_opcion", sa.String(length=32), nullable=True),
        sa.Column("experiencia_scratch", sa.String(length=32), nullable=True),
        sa.Column("experiencia_ia", sa.String(length=32), nullable=True),
        sa.Column("activo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("edad IS NULL OR edad BETWEEN 8 AND 10", name="ck_estudiantes_edad"),
        sa.CheckConstraint(
            "genero_opcion IS NULL OR genero_opcion IN ('femenino','masculino','prefiero_no_decir','otro')",
            name="ck_estudiantes_genero",
        ),
        sa.CheckConstraint(
            "experiencia_scratch IS NULL OR experiencia_scratch IN ('ninguna','un_poco','mucha')",
            name="ck_estudiantes_experiencia_scratch",
        ),
        sa.CheckConstraint(
            "experiencia_ia IS NULL OR experiencia_ia IN ('ninguna','alguna','frecuente')",
            name="ck_estudiantes_experiencia_ia",
        ),
        sa.ForeignKeyConstraint(["grupo_id"], ["grupos.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("codigo_publico"),
    )
    op.create_index("ix_estudiantes_codigo_publico", "estudiantes", ["codigo_publico"])
    op.create_index("ix_estudiantes_grupo_id", "estudiantes", ["grupo_id"])

    op.create_table(
        "categorias_juego",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("nombre", sa.Text(), nullable=False),
        sa.Column("icono", sa.Text(), nullable=True),
        sa.Column("color_hex", sa.Text(), nullable=True),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("orden", sa.SmallInteger(), server_default="0", nullable=False),
        sa.Column("activo", sa.Boolean(), server_default="true", nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "juegos",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("categoria_id", sa.Text(), nullable=True),
        sa.Column("titulo", sa.Text(), nullable=False),
        sa.Column("icono", sa.Text(), nullable=True),
        sa.Column("descripcion_corta", sa.Text(), nullable=True),
        sa.Column("duracion_estimada_min", sa.SmallInteger(), nullable=True),
        sa.Column("es_proyecto_libre", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("activo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias_juego.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_juegos_activo", "juegos", ["activo"])
    op.create_index("ix_juegos_categoria_id", "juegos", ["categoria_id"])

    op.create_table(
        "versiones_juego",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("juego_id", sa.Text(), nullable=False),
        sa.Column("version", sa.Text(), nullable=False),
        sa.Column("instruccion_nino", sa.Text(), nullable=False),
        sa.Column("objetivos_pedagogicos", sa.JSON(), nullable=False),
        sa.Column("pistas_progresivas", sa.JSON(), nullable=False),
        sa.Column("criterios_completado", sa.JSON(), nullable=False),
        sa.Column("preguntas_frecuentes_esperadas", sa.JSON(), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("activo", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["juego_id"], ["juegos.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("juego_id", "version", name="uq_versiones_juego_juego_version"),
    )
    op.create_index("ix_versiones_juego_juego_id", "versiones_juego", ["juego_id"])
    op.create_index("ix_versiones_juego_activo", "versiones_juego", ["activo"])

    op.create_table(
        "sesiones",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("estudiante_id", sa.Uuid(), nullable=False),
        sa.Column("grupo_id", sa.Uuid(), nullable=True),
        sa.Column("inicio_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("fin_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("asentimiento_aceptado", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("dispositivo_tipo", sa.Text(), nullable=True),
        sa.Column("estado", sa.String(length=16), server_default="activa", nullable=False),
        sa.Column("modo_llm", sa.String(length=16), server_default="mock", nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.CheckConstraint("estado IN ('activa','cerrada','abandonada','anulada')", name="ck_sesiones_estado"),
        sa.ForeignKeyConstraint(["estudiante_id"], ["estudiantes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["grupo_id"], ["grupos.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sesiones_estudiante_id", "sesiones", ["estudiante_id"])
    op.create_index("ix_sesiones_grupo_id", "sesiones", ["grupo_id"])
    op.create_index("ix_sesiones_inicio_en", "sesiones", ["inicio_en"])

    op.create_table(
        "asentimientos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("sesion_id", sa.Uuid(), nullable=False),
        sa.Column("estudiante_id", sa.Uuid(), nullable=False),
        sa.Column("version_texto", sa.Text(), nullable=False),
        sa.Column("aceptado", sa.Boolean(), nullable=False),
        sa.Column("aceptado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["estudiante_id"], ["estudiantes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sesion_id"], ["sesiones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_asentimientos_estudiante_id", "asentimientos", ["estudiante_id"])
    op.create_index("ix_asentimientos_sesion_id", "asentimientos", ["sesion_id"])

    op.create_table(
        "conversaciones",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("sesion_id", sa.Uuid(), nullable=False),
        sa.Column("estudiante_id", sa.Uuid(), nullable=False),
        sa.Column("juego_id", sa.Text(), nullable=False),
        sa.Column("version_juego_id", sa.Uuid(), nullable=True),
        sa.Column("estado", sa.String(length=16), server_default="activa", nullable=False),
        sa.Column("inicio_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("fin_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.CheckConstraint("estado IN ('activa','cerrada','abandonada')", name="ck_conversaciones_estado"),
        sa.ForeignKeyConstraint(["estudiante_id"], ["estudiantes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["juego_id"], ["juegos.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["sesion_id"], ["sesiones.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["version_juego_id"], ["versiones_juego.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversaciones_estudiante_id", "conversaciones", ["estudiante_id"])
    op.create_index("ix_conversaciones_juego_id", "conversaciones", ["juego_id"])
    op.create_index("ix_conversaciones_sesion_id", "conversaciones", ["sesion_id"])

    op.create_table(
        "mensajes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("conversacion_id", sa.Uuid(), nullable=False),
        sa.Column("sesion_id", sa.Uuid(), nullable=False),
        sa.Column("estudiante_id", sa.Uuid(), nullable=False),
        sa.Column("rol", sa.String(length=16), nullable=False),
        sa.Column("contenido", sa.Text(), nullable=False),
        sa.Column("orden_mensaje", sa.Integer(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("proveedor_llm", sa.Text(), nullable=True),
        sa.Column("modelo_llm", sa.Text(), nullable=True),
        sa.Column("prompt_version", sa.Text(), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.CheckConstraint("rol IN ('nino','tutor','sistema')", name="ck_mensajes_rol"),
        sa.CheckConstraint("input_tokens IS NULL OR input_tokens >= 0", name="ck_mensajes_input_tokens"),
        sa.CheckConstraint("output_tokens IS NULL OR output_tokens >= 0", name="ck_mensajes_output_tokens"),
        sa.ForeignKeyConstraint(["conversacion_id"], ["conversaciones.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["estudiante_id"], ["estudiantes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sesion_id"], ["sesiones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("conversacion_id", "orden_mensaje", name="uq_mensajes_conversacion_orden"),
    )
    op.create_index("ix_mensajes_conversacion_id", "mensajes", ["conversacion_id"])
    op.create_index("ix_mensajes_conversacion_orden", "mensajes", ["conversacion_id", "orden_mensaje"])
    op.create_index("ix_mensajes_creado_en", "mensajes", ["creado_en"])
    op.create_index("ix_mensajes_estudiante_id", "mensajes", ["estudiante_id"])
    op.create_index("ix_mensajes_sesion_id", "mensajes", ["sesion_id"])

    op.create_table(
        "eventos",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("estudiante_id", sa.Uuid(), nullable=True),
        sa.Column("sesion_id", sa.Uuid(), nullable=True),
        sa.Column("conversacion_id", sa.Uuid(), nullable=True),
        sa.Column("tipo_evento", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["conversacion_id"], ["conversaciones.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["estudiante_id"], ["estudiantes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sesion_id"], ["sesiones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_eventos_conversacion_id", "eventos", ["conversacion_id"])
    op.create_index("ix_eventos_creado_en", "eventos", ["creado_en"])
    op.create_index("ix_eventos_estudiante_id", "eventos", ["estudiante_id"])
    op.create_index("ix_eventos_sesion_id", "eventos", ["sesion_id"])
    op.create_index("ix_eventos_tipo_evento", "eventos", ["tipo_evento"])

    op.create_table(
        "feedback_sesion",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("sesion_id", sa.Uuid(), nullable=False),
        sa.Column("estudiante_id", sa.Uuid(), nullable=False),
        sa.Column("nivel_satisfaccion", sa.SmallInteger(), nullable=False),
        sa.Column("etiqueta", sa.Text(), nullable=True),
        sa.Column("comentario_extra", sa.Text(), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("nivel_satisfaccion BETWEEN 1 AND 5", name="ck_feedback_nivel_satisfaccion"),
        sa.ForeignKeyConstraint(["estudiante_id"], ["estudiantes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sesion_id"], ["sesiones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("sesion_id", name="uq_feedback_sesion"),
    )
    op.create_index("ix_feedback_sesion_estudiante_id", "feedback_sesion", ["estudiante_id"])
    op.create_index("ix_feedback_sesion_nivel_satisfaccion", "feedback_sesion", ["nivel_satisfaccion"])
    op.create_index("ix_feedback_sesion_sesion_id", "feedback_sesion", ["sesion_id"])

    op.create_table(
        "exportaciones",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("solicitado_por", sa.Uuid(), nullable=True),
        sa.Column("formato", sa.String(length=8), nullable=False),
        sa.Column("alcance", sa.String(length=32), nullable=False),
        sa.Column("filtros", sa.JSON(), nullable=False),
        sa.Column("total_registros", sa.Integer(), nullable=True),
        sa.Column("archivo_path", sa.Text(), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("formato IN ('json','csv')", name="ck_exportaciones_formato"),
        sa.CheckConstraint(
            "alcance IN ('sesiones','mensajes','feedback','eventos','dataset_completo')",
            name="ck_exportaciones_alcance",
        ),
        sa.CheckConstraint("total_registros IS NULL OR total_registros >= 0", name="ck_exportaciones_total"),
        sa.ForeignKeyConstraint(["solicitado_por"], ["usuarios_app.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_exportaciones_creado_en", "exportaciones", ["creado_en"])
    op.create_index("ix_exportaciones_solicitado_por", "exportaciones", ["solicitado_por"])

    op.create_table(
        "auditoria",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("usuario_id", sa.Uuid(), nullable=True),
        sa.Column("accion", sa.Text(), nullable=False),
        sa.Column("entidad", sa.Text(), nullable=False),
        sa.Column("entidad_id", sa.Text(), nullable=True),
        sa.Column("detalle", sa.JSON(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios_app.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auditoria_accion", "auditoria", ["accion"])
    op.create_index("ix_auditoria_entidad", "auditoria", ["entidad"])
    op.create_index("ix_auditoria_usuario_id", "auditoria", ["usuario_id"])


def downgrade() -> None:
    for table in [
        "auditoria",
        "exportaciones",
        "feedback_sesion",
        "eventos",
        "mensajes",
        "conversaciones",
        "asentimientos",
        "sesiones",
        "versiones_juego",
        "juegos",
        "categorias_juego",
        "estudiantes",
        "usuarios_app",
        "grupos",
    ]:
        op.drop_table(table)
