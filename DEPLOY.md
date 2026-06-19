# Guía de Deployment — CreaBits Tutor

## Qué es esto

**CreaBits Tutor** es una aplicación web de tutoría inteligente para niños de 8–10 años que aprenden programación con Scratch. Usa una IA (tutor LLM) que guía a los niños con hints progresivos y preguntas socráticas.

### Componentes desplegados

```
[Navegador del niño]
        │
        ▼ :80
┌──────────────────┐
│  NGINX (frontend) │  ← Sirve la app React + proxy de API
└────────┬─────────┘
         │ /api/  →  proxy interno
         ▼ :8000
┌──────────────────┐
│  FastAPI (backend)│  ← Lógica, LLM, validaciones
└────────┬─────────┘
         │ asyncpg
         ▼ :5432
┌──────────────────┐
│  PostgreSQL 17   │  ← Datos de sesiones, mensajes, feedback
└──────────────────┘
         │
   [volumen Docker]   ← Datos persisten aunque se reinicie todo
```

---

## Requisitos del servidor

- Linux (Ubuntu/Debian recomendado)
- Docker >= 24.x instalado
- Docker Compose v2 (incluido en Docker moderno como `docker compose`)
- Puerto 80 abierto en el firewall
- ~2 GB de RAM disponibles

Verificar que Docker esté instalado:
```bash
docker --version
docker compose version
```

---

## Primera instalación

### 1. Subir el código al servidor

**Opción A — con git:**
```bash
git clone <url-del-repo> /opt/creabits
cd /opt/creabits/bits_scratch_tutor
```

**Opción B — copiar desde tu PC (scp):**
```bash
# Desde tu máquina local:
scp -r bits_scratch_tutor root@207.244.241.125:/opt/creabits/
```

### 2. Crear el archivo `.env` en el servidor

```bash
cd /opt/creabits/bits_scratch_tutor

# Copiar la plantilla
cp env.docker.example .env

# Editar con tus valores reales
nano .env
```

Contenido mínimo del `.env`:
```env
DB_PASSWORD=EligirPasswordSeguro123!
CORS_ORIGINS=http://207.244.241.125,http://localhost
LLM_MODE=mock
GEMINI_API_KEY=
OPENROUTER_API_KEY=
ADMIN_FINISH_CODE=99999
```

> El `.env` nunca se sube a git (está en .gitignore). Es el único archivo con secretos.

### 3. Construir y levantar

```bash
docker compose up -d --build
```

Esto hace automáticamente en orden:
1. Construye las imágenes de backend y frontend (~3 min la primera vez)
2. Levanta PostgreSQL y espera que esté listo
3. Corre `alembic upgrade head` → crea las 14 tablas en la BD
4. Corre el seed → carga juegos, categorías y estudiantes demo
5. Arranca la API FastAPI
6. Levanta nginx sirviendo la app React en el puerto 80

### 4. Verificar que todo funciona

```bash
# Ver estado de los contenedores
docker compose ps

# Health check de la API
curl http://localhost/health
# Debe responder: {"status":"ok"}

# Verificar que los juegos están en la BD
curl http://localhost/api/v1/games/
# Debe responder con el catálogo de juegos

# Ver logs en tiempo real
docker compose logs -f
```

Abrir en el navegador: `http://207.244.241.125`

---

## Tablas creadas automáticamente

Alembic gestiona el esquema. Las tablas se crean solas la primera vez y nunca se recrean si ya existen:

| Tabla | Contenido |
|---|---|
| `grupos` | Grupos de estudiantes |
| `estudiantes` | Códigos anónimos de los niños |
| `sesiones` | Cada sesión de uso de la app |
| `conversaciones` | Una conversación por juego/sesión |
| `mensajes` | Mensajes del chat (niño + tutor IA) |
| `juegos` | Catálogo de juegos Scratch |
| `versiones_juego` | Versiones con prompts pedagógicos e hints |
| `categorias_juego` | Animaciones, Juegos, Historias, Libre |
| `asentimientos` | Registro de consentimientos |
| `feedback_sesion` | Rating 1-5 + comentario del estudiante |
| `eventos` | Log de eventos del sistema |
| `usuarios_app` | Administradores |
| `exportaciones` | Registros de exportaciones de datos |
| `auditoria` | Auditoría general |

---

## Persistencia de datos

Los datos viven en un **volumen Docker nombrado** (`postgres_data`) en el disco del servidor. Este volumen existe independientemente de los contenedores.

| Acción | ¿Se pierden datos? |
|---|---|
| `docker compose restart` | No |
| `docker compose down` | **No** — el volumen sobrevive |
| `docker compose up --build` | **No** — solo reconstruye imágenes |
| Reiniciar el servidor | **No** — el volumen es disco |
| `docker compose down -v` | **SÍ** — `-v` borra volúmenes — NUNCA usar |

---

## Operaciones comunes

### Ver logs

```bash
docker compose logs -f              # todos los servicios
docker compose logs -f backend      # solo la API
docker compose logs -f frontend     # solo nginx
docker compose logs -f db           # solo postgres
```

### Reiniciar un servicio

```bash
docker compose restart backend
```

### Actualizar código (nuevo deploy)

```bash
git pull                             # actualizar código
docker compose up -d --build         # reconstruir y redeployar
```

Las tablas y datos NO se tocan. Alembic detecta que las migraciones ya están aplicadas y no hace nada.

### Parar todo

```bash
docker compose down    # para y elimina contenedores, datos intactos
```

### Conectarse directamente a la base de datos

```bash
docker exec -it $(docker compose ps -q db) psql -U creabits -d creabits
```

---

## Backup y restauración de datos

### Hacer backup

```bash
# Crear backup con timestamp
docker exec $(docker compose ps -q db) pg_dump -U creabits creabits \
  > backup_$(date +%Y%m%d_%H%M).sql

echo "Backup guardado: backup_$(date +%Y%m%d_%H%M).sql"
```

Guardar el archivo `.sql` fuera del servidor (descargarlo a tu PC o a un almacenamiento externo).

### Restaurar backup

```bash
# Solo si hay pérdida de datos
docker exec -i $(docker compose ps -q db) psql -U creabits creabits < backup_20250619_1200.sql
```

### Descargar backup a tu PC local

```bash
# Desde tu PC:
scp root@207.244.241.125:/opt/creabits/bits_scratch_tutor/backup_*.sql ./backups/
```

---

## Cambiar el modo LLM

El sistema soporta tres modos configurables en `.env`:

```env
# Sin API — respuestas mock para desarrollo/pruebas
LLM_MODE=mock

# Google Gemini (recomendado para producción)
LLM_MODE=gemini
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-2.5-flash

# OpenRouter (acceso a múltiples modelos)
LLM_MODE=openrouter
OPENROUTER_API_KEY=tu_api_key_aqui
OPENROUTER_MODEL=google/gemini-2.5-flash
```

Después de cambiar `.env`:
```bash
docker compose up -d backend    # solo reinicia el backend, no reconstruye
```

---

## Troubleshooting

### El backend falla al arrancar

```bash
docker compose logs backend
```

Causas comunes:
- La BD todavía no está lista → esperar unos segundos y `docker compose restart backend`
- Error en variable de entorno → revisar `.env`

### La app no carga en el navegador

```bash
docker compose ps    # verificar que frontend está Up
curl http://localhost/health   # verificar API desde el servidor
```

### Ver qué hay en la base de datos

```bash
docker exec -it $(docker compose ps -q db) psql -U creabits -d creabits -c "\dt"
docker exec -it $(docker compose ps -q db) psql -U creabits -d creabits -c "SELECT COUNT(*) FROM mensajes;"
```

---

## Estructura de archivos de deployment

```
bits_scratch_tutor/
├── docker-compose.yml        ← Orquestación de los 3 servicios
├── env.docker.example        ← Plantilla de variables (copiar a .env)
├── .env                      ← Secretos reales (NO en git)
├── DEPLOY.md                 ← Este documento
├── backend/
│   ├── Dockerfile            ← Imagen Python 3.12 + FastAPI
│   ├── entrypoint.sh         ← migrations → seed → uvicorn
│   └── .dockerignore
└── frontend/
    ├── Dockerfile            ← Build Node 22 → nginx alpine
    ├── nginx.conf            ← SPA + proxy /api/ → backend
    └── .dockerignore
```
