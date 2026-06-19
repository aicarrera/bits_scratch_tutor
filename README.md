# CreaBits Tutor IA

Aplicación separada en frontend React/Vite y backend FastAPI para guardar sesiones, conversaciones y feedback anónimo de estudiantes.

## Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Por defecto usa SQLite local para desarrollo y siembra códigos demo como `tigre-azul-7`. Para PostgreSQL/Supabase configura `DATABASE_URL` en `backend/.env` y ejecuta Alembic o deja `AUTO_CREATE_TABLES=true` solo para el primer arranque controlado.

Para usar Gemini en las respuestas del tutor configura en `backend/.env`:

```bash
LLM_MODE=gemini
GEMINI_API_KEY=tu_clave
GEMINI_MODEL=gemini-2.5-flash
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

El frontend lee `VITE_API_URL`; si no existe usa `http://127.0.0.1:8000`.

## Seguridad

No subas `.env`, `coneccion.md` ni credenciales reales al repositorio. La contraseña de Supabase que estuvo en texto plano debe rotarse desde el panel de Supabase.
