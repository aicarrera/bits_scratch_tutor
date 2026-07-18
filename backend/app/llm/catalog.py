"""Catálogo de bloques de Scratch y armado del contexto del ejercicio.

Centraliza lo que antes estaba duplicado en `gemini.py` y `openrouter.py`:
carga del catálogo `bloques_slim.json`, utilidades sobre él y el armado del
bloque "EJERCICIO ACTUAL" que se inyecta en el system prompt del tutor.

`build_game_context` es donde el tutor recibe el contexto de cada juego: título,
instrucción, objetivos, pistas y —lo nuevo— la SOLUCIÓN DE REFERENCIA y los
BLOQUES CLAVE del ejercicio (columnas `descripcion_solucion` y `bloques_clave`
de la tabla `juegos`). Los códigos de `bloques_clave` se traducen a su nombre
usando el mismo catálogo, y cualquier dato ausente se omite (nunca se inventa).
"""

from __future__ import annotations

import json
import pathlib
import re
from functools import lru_cache

from app.models import Game, GameVersion

_CODE_RE = re.compile(r"[a-z][a-z0-9_]+")


# --------------------------------------------------------------------------- #
#  Prompt base compartido del tutor (Hint Progression)                        #
#  Fuente única de verdad para gemini.py y openrouter.py, para que no vuelvan  #
#  a divergir. Openrouter añade además OPENROUTER_JSON_TAIL (Gemini usa        #
#  response_schema, así que no lo necesita).                                   #
# --------------------------------------------------------------------------- #

HINT_PROGRESSION_BASE = """\
Eres Bit, un tutor amigable de programación visual en Scratch para niños de 8 a 10 años.

Tu objetivo es ayudar al estudiante a APRENDER, no resolver el ejercicio por él.

CÓMO RESPONDER SEGÚN LA SITUACIÓN:

1. Si el estudiante saluda o hace charla casual → responde corto y cálido. Fase: "responder".

2. Si pregunta algo factual ("¿qué hace este bloque?", "¿dónde está X?") → responde directo. Fase: "responder".

3. Si te pide ayuda con el ejercicio por primera vez → muéstrale UN bloque relevante e invítalo a PREDECIR qué hace antes de probarlo. Fase: "predecir".
   Ejemplo: "Mira este bloque 👇 ¿Qué crees que va a pasar si lo pones? Pruébalo y me cuentas."

4. Si ya intentó algo y no le funciona, o sigue atascado → dale una pista MÁS CONCRETA. Las pistas van escalando:
   - Pista 1 (vaga): describe la categoría de bloques a explorar.
   - Pista 2 (más concreta): describe qué tipo de bloque buscar.
   - Pista 3 (mostrar el bloque): incluye el bloque directamente en bloques_sugeridos.
   Fase: "pista".

5. Si el estudiante ya razonó bien y solo le falta confirmación → confírmalo y muestra el bloque. Fase: "confirmar".

ESTRATEGIA PREDICCIÓN Y VERIFICACIÓN:
- Cuando muestres un bloque, invita a predecir qué hace ANTES de probarlo, luego a probarlo.
- Ejemplos de invitación: "¡Pruébalo y cuéntame qué pasa!", "Arrástralo y dime cómo se ve", "Ponlo en tu programa y dale a la bandera verde 🚩".
- Esto es mejor que preguntas abstractas porque los niños responden mejor a lo concreto.

REGLAS GENERALES:
- Nunca des la solución completa de un solo golpe. Escala las pistas.
- Lenguaje simple, frases cortas. Una o dos oraciones suelen bastar.
- Emojis con moderación (máximo uno por respuesta).
- No puedes ver el programa del estudiante. Si necesitas saberlo, pregúntalo (necesita_aclaracion=true).
- Usa SOLO bloques del catálogo proporcionado.

SOBRE bloques_sugeridos:
- En "predecir": incluye el bloque sobre el que invitas a predecir.
- En "pista": incluye bloque SOLO en la pista 3 (la más concreta).
- En "responder": solo si la pregunta es sobre un bloque específico.
- En "confirmar": sí muestra el bloque que corresponde.
- El campo "imagen" debe ser exactamente el id del bloque (ej: "movimiento_mover_pasos").

SOBRE opciones_respuesta (MUY IMPORTANTE — son botones que el niño tocará para responderte):
- Devuelve SIEMPRE entre 2 y 3 opciones, salvo que tu mensaje no espere ninguna respuesta del niño (en ese caso, lista vacía).
- Cada opción es lo que DIRÍA EL NIÑO, en primera persona, MUY corta (2 a 5 palabras), en español simple. Sin emojis.
- Las opciones deben tener sentido como respuesta directa a tu pregunta y llevar la conversación hacia el objetivo del ejercicio.
- Incluye SIEMPRE una opción "de escape" para el niño que no sabe (ej: "No estoy seguro", "Ayúdame", "Dame otra pista").
- Adapta según la fase:
  * "predecir": opciones de predicción concretas + una de duda. Ej: ["El gato se mueve", "El programa empieza", "No estoy seguro"].
  * "pista": opciones de progreso. Ej: ["Ya lo encontré", "Sigo sin verlo", "Dame otra pista"].
  * "confirmar": opciones de avance. Ej: ["Sí, ya lo puse", "No, ayúdame"].
  * "responder": si hiciste una pregunta, ofrece opciones; si solo respondiste un dato, puede ir vacío o una sola opción para seguir (ej: ["¡Entendido!"]).
- No repitas literalmente el texto del bloque; usa lenguaje natural de niño.
- Nunca pongas la solución completa dentro de una opción.
"""


# Cola específica de OpenRouter: fuerza el JSON de salida (Gemini usa response_schema).
OPENROUTER_JSON_TAIL = """
FORMATO DE RESPUESTA — debes devolver ÚNICAMENTE un objeto JSON con esta estructura exacta:
{
  "respuesta": "texto para el niño",
  "fase": "predecir" | "pista" | "confirmar" | "responder",
  "bloques_sugeridos": [{"id": "...", "imagen": "...", "nombre": "..."}],
  "opciones_respuesta": ["...", "..."],
  "necesita_aclaracion": true | false,
  "razonamiento_pedagogico": "explicación interna breve"
}
No incluyas nada fuera del JSON.
"""


@lru_cache(maxsize=1)
def load_bloques() -> dict:
    path = pathlib.Path(__file__).parent.parent / "data" / "bloques_slim.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def bloques_ids(bloques_data: dict) -> set[str]:
    return {b["id"] for b in bloques_data.get("bloques", [])}


def bloque_nombre(bloques_data: dict, bloque_id: str) -> str:
    for b in bloques_data.get("bloques", []):
        if b["id"] == bloque_id:
            return b.get("nombre", bloque_id)
    return bloque_id


def clean_opciones(raw: list, limit: int = 3, max_len: int = 40) -> list[str]:
    """Normaliza las opciones de respuesta rápida: cortas, sin vacíos ni duplicados."""
    seen: set[str] = set()
    out: list[str] = []
    for item in raw or []:
        if not isinstance(item, str):
            continue
        text = item.strip()
        if not text or len(text) > max_len:
            continue
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(text)
        if len(out) >= limit:
            break
    return out


def parse_block_codes(raw: str | None) -> list[str]:
    """Extrae los códigos de bloque de un valor `bloques_clave`.

    Acepta el formato guardado en la base ('"a","b"'), una lista JSON o texto
    suelto: toma cualquier token con forma de código, conserva el orden y no
    repite.
    """
    if not raw:
        return []
    codes: list[str] = []
    for token in _CODE_RE.findall(raw):
        if token not in codes:
            codes.append(token)
    return codes


def build_game_context(game: Game, version: GameVersion | None, bloques_data: dict) -> str:
    """Arma el bloque "EJERCICIO ACTUAL" para el system prompt del tutor.

    Incluye la solución de referencia y los bloques clave solo cuando el juego
    los tiene; nunca inventa datos.
    """
    ctx = (
        "\nEJERCICIO ACTUAL:\n"
        f"Título: {game.titulo}\n"
        f"Instrucción al niño: {version.instruccion_nino if version else 'Crea algo divertido con Scratch.'}\n"
    )
    if version and version.objetivos_pedagogicos:
        ctx += f"Objetivos: {', '.join(str(o) for o in version.objetivos_pedagogicos)}\n"
    if version and version.pistas_progresivas:
        ctx += f"Pistas progresivas disponibles: {json.dumps(version.pistas_progresivas, ensure_ascii=False)}\n"

    if game.descripcion_solucion:
        ctx += (
            "\nSOLUCIÓN DE REFERENCIA (SOLO PARA TI, NO la reveles completa ni la copias tal cual; "
            "úsala como brújula para saber cuál es el siguiente paso y qué preguntar): "
            f"{game.descripcion_solucion}\n"
        )

    codes = parse_block_codes(game.bloques_clave)
    if codes:
        lineas = [f'- {code} ("{bloque_nombre(bloques_data, code)}")' for code in codes]
        ctx += (
            "\nBLOQUES CLAVE DE ESTE EJERCICIO (SOLO PARA TI, NO reveles la lista completa; úsala "
            "como guía. La solución de referencia usa estos bloques; cuando corresponda sugerir, "
            "prioriza estos ids y muestra solo UNO por turno):\n"
            + "\n".join(lineas)
            + "\n"
        )

    return ctx
