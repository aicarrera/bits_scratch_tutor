import json
import pathlib
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel

from app.core.settings import Settings
from app.llm.base import TutorLLM, TutorReply
from app.models import Conversation, Game, GameVersion, Message


# --------------------------------------------------------------------------- #
#  Block catalog — loaded once from disk                                       #
# --------------------------------------------------------------------------- #

@lru_cache(maxsize=1)
def _load_bloques() -> dict:
    path = pathlib.Path(__file__).parent.parent / "data" / "bloques_slim.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _bloques_ids(bloques_data: dict) -> set[str]:
    return {b["id"] for b in bloques_data.get("bloques", [])}


def _bloque_nombre(bloques_data: dict, bloque_id: str) -> str:
    for b in bloques_data.get("bloques", []):
        if b["id"] == bloque_id:
            return b.get("nombre", bloque_id)
    return bloque_id


def _clean_opciones(raw: list, limit: int = 3, max_len: int = 40) -> list[str]:
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


# --------------------------------------------------------------------------- #
#  Pydantic schema for structured Gemini output                                #
# --------------------------------------------------------------------------- #

class _BloqueSugeridoOut(BaseModel):
    id: str
    imagen: str
    nombre: str


class _RespuestaTutorOut(BaseModel):
    respuesta: str
    fase: Literal["predecir", "pista", "confirmar", "responder"]
    bloques_sugeridos: list[_BloqueSugeridoOut]
    opciones_respuesta: list[str]
    necesita_aclaracion: bool
    razonamiento_pedagogico: str


# --------------------------------------------------------------------------- #
#  Base Hint Progression system prompt template                                #
# --------------------------------------------------------------------------- #

_HINT_PROGRESSION_BASE = """\
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


# --------------------------------------------------------------------------- #
#  GeminiTutorLLM                                                              #
# --------------------------------------------------------------------------- #

class GeminiTutorLLM(TutorLLM):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate_reply(
        self,
        conversation: Conversation,
        game: Game,
        version: GameVersion | None,
        history: list[Message],
        user_text: str,
    ) -> TutorReply:
        from google import genai
        from google.genai import types

        bloques_data = _load_bloques()
        ids_validos = _bloques_ids(bloques_data)

        # Build system instruction
        game_context = (
            f"\nEJERCICIO ACTUAL:\n"
            f"Título: {game.titulo}\n"
            f"Instrucción al niño: {version.instruccion_nino if version else 'Crea algo divertido con Scratch.'}\n"
        )
        if version and version.objetivos_pedagogicos:
            game_context += f"Objetivos: {', '.join(str(o) for o in version.objetivos_pedagogicos)}\n"
        if version and version.pistas_progresivas:
            game_context += f"Pistas progresivas disponibles: {json.dumps(version.pistas_progresivas, ensure_ascii=False)}\n"

        catalog_json = json.dumps(bloques_data, ensure_ascii=False)
        system_instruction = (
            _HINT_PROGRESSION_BASE
            + game_context
            + f"\nCATÁLOGO DE BLOQUES DISPONIBLES:\n{catalog_json}\n"
        )

        # Build conversation transcript
        transcript_parts = []
        for msg in history[-14:]:
            role_label = "Niño" if msg.rol == "nino" else "Bit"
            transcript_parts.append(f"{role_label}: {msg.contenido}")
        transcript = "\n".join(transcript_parts)

        contents = (
            f"Historial reciente de la conversación:\n{transcript}\n\n"
            f"Nuevo mensaje del estudiante: {user_text}\n"
            "Responde como Bit en español para un niño. Devuelve JSON estructurado."
        )

        client = genai.Client(api_key=self.settings.gemini_api_key)
        prompt_version = f"{game.id}_{version.version}" if version else game.id

        try:
            response = client.models.generate_content(
                model=self.settings.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.3,
                    response_mime_type="application/json",
                    response_schema=_RespuestaTutorOut,
                ),
            )

            data = _RespuestaTutorOut.model_validate_json(response.text or "{}")

            # Validate blocks against catalog
            bloques_validos = [
                b for b in data.bloques_sugeridos if b.id in ids_validos
            ]
            bloques_out = [
                {"id": b.id, "imagen": b.id, "nombre": _bloque_nombre(bloques_data, b.id)}
                for b in bloques_validos
            ]

            # Sanitize quick-reply options: short, non-empty, de-duplicated, capped at 3
            opciones_out = _clean_opciones(data.opciones_respuesta)

            input_tokens = None
            output_tokens = None
            if response.usage_metadata:
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count

            return TutorReply(
                text=data.respuesta,
                provider="gemini",
                model=self.settings.gemini_model,
                prompt_version=prompt_version,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                fase=data.fase,
                bloques_sugeridos=bloques_out,
                opciones_respuesta=opciones_out,
                necesita_aclaracion=data.necesita_aclaracion,
                razonamiento_pedagogico=data.razonamiento_pedagogico,
                metadata={
                    "mode": "gemini",
                    "game_id": game.id,
                    "conversation_id": str(conversation.id),
                    "fase": data.fase,
                    "bloques_sugeridos": bloques_out,
                    "opciones_respuesta": opciones_out,
                    "razonamiento_pedagogico": data.razonamiento_pedagogico,
                    "necesita_aclaracion": data.necesita_aclaracion,
                },
            )

        except Exception as exc:
            # Fallback to plain text on error
            return TutorReply(
                text="Probemos paso a paso. ¿Qué ves ahora en Scratch?",
                provider="gemini",
                model=self.settings.gemini_model,
                prompt_version=prompt_version,
                fase="responder",
                metadata={
                    "mode": "gemini",
                    "error": str(exc),
                    "game_id": game.id,
                    "fase": "responder",
                    "bloques_sugeridos": [],
                },
            )
