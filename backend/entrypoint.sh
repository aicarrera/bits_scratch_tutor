#!/bin/bash
set -e

echo "==> Aplicando migraciones de base de datos..."
alembic upgrade head

echo "==> Cargando datos iniciales (idempotente)..."
python scripts/seed_initial_data.py

echo "==> Iniciando servidor FastAPI..."
exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
