#!/usr/bin/env python3
"""
run_queries.py — Ejecuta los .sql de `sql/` contra creabits_paper.db y
escribe los resultados en `out/` (Markdown + CSV), para que cada número
del paper sea trazable hasta su consulta.

Cada consulta se delimita con un comentario `-- @name <slug>` justo antes
del SELECT. El script imprime la consulta y su resultado.

Uso:
    python run_queries.py                 # ejecuta todos los sql/*.sql
    python run_queries.py 02_tabla2.sql   # ejecuta uno
"""

from __future__ import annotations

import re
import sqlite3
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
DB = BASE / "creabits_paper.db"
SQL_DIR = BASE / "sql"
OUT_DIR = BASE / "out"

# Se ejecutan siempre antes que nada, en este orden: primero se completan
# las edades que faltaban usando la hoja de asistencia en papel, luego se
# definen las vistas de alcance.
SETUP = [SQL_DIR / "00a_hoja_asistencia.sql", SQL_DIR / "00_scope.sql"]

NAME_RE = re.compile(r"^--\s*@name\s+(\S+)\s*$", re.MULTILINE)


def split_queries(sql_text: str) -> list[tuple[str, str]]:
    """Divide un archivo .sql en (nombre, consulta) usando los `-- @name`."""
    marks = list(NAME_RE.finditer(sql_text))
    out: list[tuple[str, str]] = []
    for i, m in enumerate(marks):
        start = m.end()
        end = marks[i + 1].start() if i + 1 < len(marks) else len(sql_text)
        body = sql_text[start:end].strip()
        # descarta el bloque de comentarios que encabeza la siguiente consulta
        body = re.sub(r"\n-{10,}[\s\S]*$", "", body).strip()
        if body:
            out.append((m.group(1), body))
    return out


def main() -> None:
    if not DB.exists():
        raise SystemExit("Falta creabits_paper.db — ejecuta antes build_sqlite.py")

    OUT_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB)
    for setup in SETUP:
        conn.executescript(setup.read_text(encoding="utf-8"))
    conn.commit()

    targets = (
        [SQL_DIR / a for a in sys.argv[1:]]
        if len(sys.argv) > 1
        else sorted(p for p in SQL_DIR.glob("*.sql") if p not in SETUP)
    )

    pd.set_option("display.width", 200)
    pd.set_option("display.max_rows", 300)
    pd.set_option("display.max_colwidth", 60)

    for path in targets:
        md: list[str] = [f"# Resultados — `{path.name}`\n"]
        print(f"\n{'=' * 78}\n{path.name}\n{'=' * 78}")
        for name, query in split_queries(path.read_text(encoding="utf-8")):
            df = pd.read_sql(query, conn)
            print(f"\n--- {name} ---")
            print(df.to_string(index=False))
            df.to_csv(OUT_DIR / f"{path.stem}__{name}.csv", index=False)
            md.append(f"## {name}\n\n```sql\n{query}\n```\n")
            md.append(df.to_markdown(index=False) + "\n")
        (OUT_DIR / f"{path.stem}.md").write_text("\n".join(md), encoding="utf-8")

    conn.close()
    print(f"\nResultados escritos en {OUT_DIR}")


if __name__ == "__main__":
    main()
