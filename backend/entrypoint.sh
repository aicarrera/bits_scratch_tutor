#!/bin/bash
set -e

echo "==> Verificando conexión a la base de datos..."
python - <<'PYEOF'
import asyncio
import sys
import os

async def wait_for_db():
    import asyncpg

    raw = os.environ.get("DATABASE_URL", "")
    url = (
        raw
        .replace("postgresql+asyncpg://", "postgresql://")
        .replace("postgres+asyncpg://", "postgresql://")
    )

    max_retries = 30
    for attempt in range(1, max_retries + 1):
        try:
            conn = await asyncpg.connect(url)
            await conn.close()
            print(f"  Base de datos alcanzable.")
            return
        except Exception as exc:
            print(f"  Intento {attempt}/{max_retries}: {exc}")
            if attempt < max_retries:
                await asyncio.sleep(3)

    print("ERROR: No se pudo conectar a la base de datos después de todos los intentos.")
    sys.exit(1)

asyncio.run(wait_for_db())
PYEOF

echo "==> Aplicando migraciones de base de datos..."
alembic upgrade head

echo "==> Cargando datos iniciales (idempotente)..."
python scripts/seed_initial_data.py

echo "==> Iniciando servidor FastAPI..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
