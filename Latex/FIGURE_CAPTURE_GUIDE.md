# Guía de captura — Figura de interacción (`fig:ui`)

El `.tex` deja 4 placeholders en la figura `fig:ui`. Reemplaza cada uno con una
captura real de la app corriendo. Los nombres de archivo esperados son:

| Archivo esperado | Fase / feature | Qué debe verse |
|---|---|---|
| `fig/ui_predict.png` | **Predict** | Bit muestra **un** bloque y pregunta "¿qué crees que hace?"; badge morado "¿Qué crees que hace?"; botones de opción abajo. |
| `fig/ui_hint_block.png` | **Hint (nivel 3)** | Tras insistir que sigues atascado, Bit muestra el **bloque concreto** como tarjeta; badge amarillo "Pista". |
| `fig/ui_options.png` | **Response Options as Scaffolding** | Primer plano de los **botones naranja** (voz del niño) incluyendo la opción de escape ("No estoy seguro"), con el campo de texto libre visible. |
| `fig/ui_confirm.png` | **Confirm** | Badge verde "¡Así se hace!"; Bit confirma y muestra el bloque correcto. |

> Coloca los PNG en `Latex/fig/`. En el `.tex`, dentro de cada `subfigure`:
> borra la línea del `\fbox{...}` (el placeholder) y **descomenta** la línea
> `% \includegraphics[...]`.

---

## Cómo levantar la app para capturar

**Backend** (desde `backend/`, en modo mock no necesitas API key):
```bash
python -m venv .venv && .\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
copy .env.example .env          # LLM_MODE=mock ya viene por defecto
python scripts/create_tables.py
python scripts/seed_initial_data.py
python -m uvicorn app.main:app --reload
```

**Frontend** (desde `frontend/`):
```bash
npm install
npm run dev        # abre http://localhost:5173
```

> Para respuestas pedagógicas realistas (mejores para el paper), usa
> `LLM_MODE=gemini` y `GEMINI_API_KEY=...` en `backend/.env` en vez de `mock`.
> Recuerda: el modelo desplegado es **Gemini 2.5 Flash** (elegido sobre 3.x por
> latencia). El mock da respuestas fijas, suficientes para mostrar la UI pero
> no el razonamiento del tutor.

---

## Cómo llegar a cada estado dentro del chat

1. **Welcome** → escribe un código de estudiante demo (p. ej. `tigre-azul-7`, sembrado por `seed_initial_data.py`).
2. **Asentimiento** → acepta.
3. **Selección de juego** → elige **"Haz bailar al gato" 🐱** (es el ejercicio usado en el ejemplo del paper).
4. Dentro del chat:
   - **Predict** (`ui_predict.png`): escribe `Ayúdame` o toca una opción de ayuda. Bit mostrará un bloque e invitará a predecir → captura aquí.
   - **Options** (`ui_options.png`): en ese mismo turno, haz *zoom/crop* a los botones naranja de abajo (incluida la opción de escape) + el campo "O escribe tu propia respuesta...".
   - **Hint nivel 3** (`ui_hint_block.png`): responde varias veces que sigues atascado (`Sigo sin verlo`, `Dame otra pista`). Tras escalar, Bit mostrará el bloque concreto como tarjeta → captura.
   - **Confirm** (`ui_confirm.png`): indica que ya razonaste/pusiste el bloque (`Sí, ya lo puse`). Bit confirmará con badge verde → captura.

---

## Tips técnicos de captura (calidad de paper)

- Ancho de ventana ~1200–1400 px; captura el área del chat, no toda la pantalla.
- Exporta a **PNG** con buena densidad (idealmente 2×) para que no se vea pixelado en el PDF IEEE de dos columnas.
- Recorta márgenes vacíos; mantén visible el **badge de fase**, el **mensaje de Bit**, las **tarjetas de bloque** y los **botones**.
- Si un dato pudiera identificar a un niño, usa un código demo (`tigre-azul-7`) — los datos son anónimos por diseño, pero para un paper conviene una sesión de prueba.
- Mantén el mismo *zoom* del navegador en las 4 capturas para que se vean consistentes en la figura.

---

## Checklist antes de compilar el `.tex`

- [ ] Creada la carpeta `Latex/fig/` con los 4 PNG.
- [ ] En cada `subfigure`: `\fbox{...}` borrado y `\includegraphics` descomentado.
- [ ] Compilas con un motor que soporte UTF-8 (pdfLaTeX moderno, XeLaTeX o LuaLaTeX).
- [ ] `IEEEtran.cls` está junto al `.tex` (ya lo está en `Latex/`).
