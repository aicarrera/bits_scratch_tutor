"""Add descripcion_solucion and bloques_clave columns to juegos.

Estas columnas alimentan al tutor con la solución de referencia y los bloques
clave de cada juego. Pueden existir ya en algunos entornos (Supabase), por eso
las operaciones son idempotentes.

Revision ID: 0003_add_solucion_bloques_juegos
Revises: 0002_add_url_video_juegos
Create Date: 2026-07-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import context, op

revision: str = "0003_add_solucion_bloques_juegos"
down_revision: str | None = "0002_add_url_video_juegos"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _has_column(table: str, column: str) -> bool:
    # En modo offline (alembic --sql) no hay conexión que inspeccionar: se emite
    # el DDL de forma incondicional, ya que un script SQL no puede ser condicional.
    if context.is_offline_mode():
        return False
    inspector = sa.inspect(op.get_bind())
    return any(col["name"] == column for col in inspector.get_columns(table))


def upgrade() -> None:
    offline = context.is_offline_mode()
    if offline or not _has_column("juegos", "descripcion_solucion"):
        op.add_column("juegos", sa.Column("descripcion_solucion", sa.Text(), nullable=True))
    if offline or not _has_column("juegos", "bloques_clave"):
        op.add_column("juegos", sa.Column("bloques_clave", sa.Text(), nullable=True))


def downgrade() -> None:
    offline = context.is_offline_mode()
    if offline or _has_column("juegos", "bloques_clave"):
        op.drop_column("juegos", "bloques_clave")
    if offline or _has_column("juegos", "descripcion_solucion"):
        op.drop_column("juegos", "descripcion_solucion")
