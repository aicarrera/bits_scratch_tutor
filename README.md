# CreaBits Tutor IA

Aplicación separada en frontend React/Vite y backend FastAPI para guardar sesiones, conversaciones y feedback anónimo de estudiantes.

## Backend

```bash
cd backend
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
python scripts/create_tables.py
python scripts/seed_initial_data.py  # opcional: carga catalogo y datos demo
python -m uvicorn app.main:app --reload
```

La API ya no crea tablas ni siembra datos al arrancar. `scripts/create_tables.py` aplica las migraciones de Alembic y `scripts/seed_initial_data.py` carga datos iniciales idempotentes como `tigre-azul-7`. Si dejas `DATABASE_URL` vacío, el backend usa SQLite local en `backend/creabits_dev.db`. Para PostgreSQL/Supabase configura `DATABASE_URL` en `backend/.env` y ejecuta esos mismos scripts antes de levantar la API.

## Frontend

```bash
cd frontend
npm install
npm run dev
```

El frontend lee `VITE_API_URL`; si no existe usa `http://127.0.0.1:8000`.

## Seguridad

No subas `.env`, `coneccion.md` ni credenciales reales al repositorio. La contraseña de Supabase que estuvo en texto plano debe rotarse desde el panel de Supabase.
