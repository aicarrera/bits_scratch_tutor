#!/usr/bin/env python3
"""
build_sqlite.py — Reconstruye una base SQLite local a partir del backup
(pg_dumpall en texto plano) `db_cluster-09-08-2026@21-16-40.backup`.

Solo se importa el esquema `public` (el dominio de CreaBits Tutor); los esquemas
`auth`, `storage`, `realtime` y `vault` son infraestructura de Supabase y no
contienen datos del estudio.

Uso:
    python build_sqlite.py            # genera creabits_paper.db junto al script
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parent
BACKUP = BASE.parent / "db_cluster-09-08-2026@21-16-40.backup"
DB_PATH = BASE / "creabits_paper.db"

# Tablas del esquema public que importamos, con el tipo SQLite de cada columna.
# (SQLite es dinámico; los tipos son documentación + afinidad para ORDER BY.)
TABLES: dict[str, list[tuple[str, str]]] = {
    "alembic_version": [("version_num", "TEXT")],
    "grupos": [
        ("id", "TEXT"), ("nombre", "TEXT"), ("descripcion", "TEXT"),
        ("fecha_inicio", "TEXT"), ("fecha_fin", "TEXT"),
        ("activo", "INTEGER"), ("creado_en", "TEXT"),
    ],
    "categorias_juego": [
        ("id", "TEXT"), ("nombre", "TEXT"), ("icono", "TEXT"),
        ("color_hex", "TEXT"), ("descripcion", "TEXT"),
        ("orden", "INTEGER"), ("activo", "INTEGER"),
    ],
    "juegos": [
        ("id", "TEXT"), ("categoria_id", "TEXT"), ("titulo", "TEXT"),
        ("icono", "TEXT"), ("descripcion_corta", "TEXT"),
        ("duracion_estimada_min", "INTEGER"), ("es_proyecto_libre", "INTEGER"),
        ("activo", "INTEGER"), ("creado_en", "TEXT"), ("url_video", "TEXT"),
        ("descripcion_solucion", "TEXT"), ("bloques_clave", "TEXT"),
    ],
    "versiones_juego": [
        ("id", "TEXT"), ("juego_id", "TEXT"), ("version", "TEXT"),
        ("instruccion_nino", "TEXT"), ("objetivos_pedagogicos", "TEXT"),
        ("pistas_progresivas", "TEXT"), ("criterios_completado", "TEXT"),
        ("preguntas_frecuentes_esperadas", "TEXT"), ("system_prompt", "TEXT"),
        ("activo", "INTEGER"), ("creado_en", "TEXT"),
    ],
    "estudiantes": [
        ("id", "TEXT"), ("codigo_publico", "TEXT"), ("grupo_id", "TEXT"),
        ("nombre_completo", "TEXT"), ("email_referencia", "TEXT"),
        ("notas_investigador", "TEXT"), ("edad", "INTEGER"),
        ("genero_opcion", "TEXT"), ("experiencia_scratch", "TEXT"),
        ("experiencia_ia", "TEXT"), ("activo", "INTEGER"), ("creado_en", "TEXT"),
    ],
    "sesiones": [
        ("id", "TEXT"), ("estudiante_id", "TEXT"), ("grupo_id", "TEXT"),
        ("inicio_en", "TEXT"), ("fin_en", "TEXT"),
        ("asentimiento_aceptado", "INTEGER"), ("dispositivo_tipo", "TEXT"),
        ("estado", "TEXT"), ("modo_llm", "TEXT"), ("metadata", "TEXT"),
    ],
    "conversaciones": [
        ("id", "TEXT"), ("sesion_id", "TEXT"), ("estudiante_id", "TEXT"),
        ("juego_id", "TEXT"), ("version_juego_id", "TEXT"), ("estado", "TEXT"),
        ("inicio_en", "TEXT"), ("fin_en", "TEXT"), ("metadata", "TEXT"),
    ],
    "mensajes": [
        ("id", "TEXT"), ("conversacion_id", "TEXT"), ("sesion_id", "TEXT"),
        ("estudiante_id", "TEXT"), ("rol", "TEXT"), ("contenido", "TEXT"),
        ("orden_mensaje", "INTEGER"), ("creado_en", "TEXT"),
        ("proveedor_llm", "TEXT"), ("modelo_llm", "TEXT"),
        ("prompt_version", "TEXT"), ("input_tokens", "INTEGER"),
        ("output_tokens", "INTEGER"), ("metadata", "TEXT"),
    ],
    "feedback_sesion": [
        ("id", "TEXT"), ("sesion_id", "TEXT"), ("estudiante_id", "TEXT"),
        ("nivel_satisfaccion", "INTEGER"), ("etiqueta", "TEXT"),
        ("comentario_extra", "TEXT"), ("creado_en", "TEXT"),
    ],
    "asentimientos": [
        ("id", "TEXT"), ("sesion_id", "TEXT"), ("estudiante_id", "TEXT"),
        ("version_texto", "TEXT"), ("aceptado", "INTEGER"), ("aceptado_en", "TEXT"),
    ],
    "eventos": [
        ("id", "TEXT"), ("estudiante_id", "TEXT"), ("sesion_id", "TEXT"),
        ("conversacion_id", "TEXT"), ("tipo_evento", "TEXT"),
        ("payload", "TEXT"), ("creado_en", "TEXT"),
    ],
    "usuarios_app": [
        ("id", "TEXT"), ("email", "TEXT"), ("nombre_completo", "TEXT"),
        ("rol", "TEXT"), ("grupo_id", "TEXT"), ("activo", "INTEGER"),
        ("creado_en", "TEXT"), ("ultimo_acceso_en", "TEXT"),
    ],
    "auditoria": [
        ("id", "TEXT"), ("usuario_id", "TEXT"), ("accion", "TEXT"),
        ("entidad", "TEXT"), ("entidad_id", "TEXT"), ("detalle", "TEXT"),
        ("creado_en", "TEXT"),
    ],
    "exportaciones": [
        ("id", "TEXT"), ("solicitado_por", "TEXT"), ("formato", "TEXT"),
        ("alcance", "TEXT"), ("filtros", "TEXT"), ("total_registros", "INTEGER"),
        ("archivo_path", "TEXT"), ("creado_en", "TEXT"),
    ],
}

# Columnas booleanas de PostgreSQL ('t'/'f') → 1/0 en SQLite.
BOOL_COLS = {
    "activo", "es_proyecto_libre", "asentimiento_aceptado", "aceptado",
}

COPY_RE = re.compile(r"^COPY public\.(\w+) \(([^)]*)\) FROM stdin;$")

# Todas las marcas de tiempo del backup son UTC con sufijo `+00`, que SQLite no
# sabe parsear. Estas vistas exponen versiones normalizadas:
#   *_utc   → 'YYYY-MM-DD HH:MM:SS(.ffffff)'  (apta para julianday/strftime)
#   *_local → hora de Ecuador (America/Guayaquil = UTC-5 todo el año)
# Todo el análisis del paper se hace sobre estas vistas.
VIEWS_SQL = """
CREATE VIEW v_sesiones AS
SELECT
    s.id, s.estudiante_id, s.grupo_id, s.estado, s.modo_llm,
    s.asentimiento_aceptado, s.metadata,
    substr(s.inicio_en, 1, length(s.inicio_en) - 3)                                   AS inicio_utc,
    substr(s.fin_en,    1, length(s.fin_en)    - 3)                                   AS fin_utc,
    datetime(substr(s.inicio_en, 1, length(s.inicio_en) - 3), '-5 hours')             AS inicio_local,
    datetime(substr(s.fin_en,    1, length(s.fin_en)    - 3), '-5 hours')             AS fin_local,
    date(substr(s.inicio_en, 1, length(s.inicio_en) - 3), '-5 hours')                 AS fecha_local,
    (julianday(substr(s.fin_en,    1, length(s.fin_en)    - 3))
     - julianday(substr(s.inicio_en, 1, length(s.inicio_en) - 3))) * 1440.0           AS duracion_min
FROM sesiones s;

CREATE VIEW v_conversaciones AS
SELECT
    c.id, c.sesion_id, c.estudiante_id, c.juego_id, c.version_juego_id,
    c.estado, c.metadata,
    substr(c.inicio_en, 1, length(c.inicio_en) - 3)                                   AS inicio_utc,
    substr(c.fin_en,    1, length(c.fin_en)    - 3)                                   AS fin_utc,
    date(substr(c.inicio_en, 1, length(c.inicio_en) - 3), '-5 hours')                 AS fecha_local,
    (julianday(substr(c.fin_en,    1, length(c.fin_en)    - 3))
     - julianday(substr(c.inicio_en, 1, length(c.inicio_en) - 3))) * 1440.0           AS duracion_min
FROM conversaciones c;

CREATE VIEW v_mensajes AS
SELECT
    m.id, m.conversacion_id, m.sesion_id, m.estudiante_id, m.rol, m.contenido,
    m.orden_mensaje, m.proveedor_llm, m.modelo_llm, m.prompt_version,
    m.input_tokens, m.output_tokens, m.metadata,
    substr(m.creado_en, 1, length(m.creado_en) - 3)                                   AS creado_utc,
    datetime(substr(m.creado_en, 1, length(m.creado_en) - 3), '-5 hours')             AS creado_local,
    date(substr(m.creado_en, 1, length(m.creado_en) - 3), '-5 hours')                 AS fecha_local,
    length(m.contenido)                                        AS n_chars,
    (length(trim(m.contenido)) - length(replace(trim(m.contenido), ' ', '')) + 1)
                                                               AS n_palabras,
    CASE WHEN instr(m.contenido, '?') > 0
           OR instr(m.contenido, char(191)) > 0                -- '¿'
         THEN 1 ELSE 0 END                                     AS es_pregunta,
    json_extract(m.metadata, '$.fase')                         AS fase,
    json_array_length(
        COALESCE(json_extract(m.metadata, '$.bloques_sugeridos'), '[]')
    )                                                          AS n_bloques,
    json_array_length(
        COALESCE(json_extract(m.metadata, '$.opciones_respuesta'), '[]')
    )                                                          AS n_opciones
FROM mensajes m;

CREATE VIEW v_feedback AS
SELECT
    f.id, f.sesion_id, f.estudiante_id, f.nivel_satisfaccion, f.etiqueta,
    f.comentario_extra,
    substr(f.creado_en, 1, length(f.creado_en) - 3)                                   AS creado_utc,
    date(substr(f.creado_en, 1, length(f.creado_en) - 3), '-5 hours')                 AS fecha_local
FROM feedback_sesion f;
"""

# Secuencias de escape del formato COPY TEXT de PostgreSQL.
UNESCAPE = {
    "b": "\b", "f": "\f", "n": "\n", "r": "\r",
    "t": "\t", "v": "\v", "\\": "\\",
}


def unescape(field: str) -> str | None:
    """Decodifica un campo del formato COPY TEXT. `\\N` → None (NULL)."""
    if field == r"\N":
        return None
    if "\\" not in field:
        return field
    out: list[str] = []
    i = 0
    n = len(field)
    while i < n:
        ch = field[i]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue
        i += 1
        if i >= n:
            out.append("\\")
            break
        nxt = field[i]
        if nxt in UNESCAPE:
            out.append(UNESCAPE[nxt])
            i += 1
        elif nxt == "x":  # \xHH hexadecimal
            hexpart = field[i + 1:i + 3]
            if len(hexpart) == 2 and all(c in "0123456789abcdefABCDEF" for c in hexpart):
                out.append(chr(int(hexpart, 16)))
                i += 3
            else:
                out.append("x")
                i += 1
        elif nxt.isdigit():  # \NNN octal
            octpart = field[i:i + 3]
            if len(octpart) == 3 and all(c in "01234567" for c in octpart):
                out.append(chr(int(octpart, 8)))
                i += 3
            else:
                out.append(nxt)
                i += 1
        else:
            out.append(nxt)
            i += 1
    return "".join(out)


def coerce(table: str, col: str, raw: str | None):
    """Aplica el tipo declarado en TABLES (bool → 0/1, INTEGER → int)."""
    if raw is None:
        return None
    if col in BOOL_COLS:
        return 1 if raw == "t" else 0
    decl = dict(TABLES[table]).get(col, "TEXT")
    if decl == "INTEGER":
        try:
            return int(raw)
        except ValueError:
            return None
    return raw


def main() -> None:
    if not BACKUP.exists():
        raise SystemExit(f"No se encontró el backup: {BACKUP}")

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode = OFF")
    conn.execute("PRAGMA synchronous = OFF")

    for table, cols in TABLES.items():
        coldefs = ", ".join(f'"{c}" {t}' for c, t in cols)
        conn.execute(f'CREATE TABLE "{table}" ({coldefs})')

    counts: dict[str, int] = {t: 0 for t in TABLES}
    skipped: dict[str, int] = {}

    with BACKUP.open("r", encoding="utf-8", newline="") as fh:
        current: str | None = None
        current_cols: list[str] = []
        buffer: list[tuple] = []

        for line in fh:
            line = line.rstrip("\n")

            if current is None:
                m = COPY_RE.match(line)
                if m:
                    tbl, colstr = m.group(1), m.group(2)
                    if tbl in TABLES:
                        current = tbl
                        current_cols = [c.strip() for c in colstr.split(", ")]
                        buffer = []
                    else:
                        skipped[tbl] = skipped.get(tbl, 0) + 1
                continue

            if line == r"\.":
                if buffer:
                    ph = ", ".join("?" * len(current_cols))
                    names = ", ".join(f'"{c}"' for c in current_cols)
                    conn.executemany(
                        f'INSERT INTO "{current}" ({names}) VALUES ({ph})', buffer
                    )
                    counts[current] += len(buffer)
                current, current_cols, buffer = None, [], []
                continue

            fields = line.split("\t")
            if len(fields) != len(current_cols):
                raise SystemExit(
                    f"[{current}] fila con {len(fields)} campos, "
                    f"se esperaban {len(current_cols)}: {line[:120]!r}"
                )
            buffer.append(
                tuple(
                    coerce(current, col, unescape(val))
                    for col, val in zip(current_cols, fields)
                )
            )

    # Índices para acelerar los joins del análisis.
    for stmt in (
        "CREATE INDEX ix_ses_est ON sesiones(estudiante_id)",
        "CREATE INDEX ix_conv_ses ON conversaciones(sesion_id)",
        "CREATE INDEX ix_conv_est ON conversaciones(estudiante_id)",
        "CREATE INDEX ix_msg_conv ON mensajes(conversacion_id)",
        "CREATE INDEX ix_msg_ses ON mensajes(sesion_id)",
        "CREATE INDEX ix_msg_est ON mensajes(estudiante_id)",
        "CREATE INDEX ix_fb_ses ON feedback_sesion(sesion_id)",
        "CREATE INDEX ix_ev_ses ON eventos(sesion_id)",
    ):
        conn.execute(stmt)

    conn.executescript(VIEWS_SQL)
    conn.commit()

    print(f"SQLite creada: {DB_PATH}")
    for t, n in counts.items():
        print(f"  {t:<20} {n:>6} filas")
    if skipped:
        print("\nEsquemas ignorados (infraestructura Supabase):",
              ", ".join(sorted(skipped)))
    conn.close()


if __name__ == "__main__":
    main()
