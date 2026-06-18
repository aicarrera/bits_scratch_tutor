import json
import pathlib
from functools import lru_cache

from app.core.settings import Settings
from app.llm.base import TutorLLM, TutorReply
from app.models import Conversation, Game, GameVersion, Message

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

FORMATO DE RESPUESTA — debes devolver ÚNICAMENTE un objeto JSON con esta estructura exacta:
{
  "respuesta": "texto para el niño",
  "fase": "predecir" | "pista" | "confirmar" | "responder",
  "bloques_sugeridos": [{"id": "...", "imagen": "...", "nombre": "..."}],
  "necesita_aclaracion": true | false,
  "razonamiento_pedagogico": "explicación interna breve"
}
No incluyas nada fuera del JSON.
"""


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


class OpenRouterTutorLLM(TutorLLM):
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
        from openai import AsyncOpenAI

        bloques_data = _load_bloques()
        ids_validos = _bloques_ids(bloques_data)

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
        system_prompt = (
            _HINT_PROGRESSION_BASE
            + game_context
            + f"\nCATÁLOGO DE BLOQUES DISPONIBLES:\n{catalog_json}\n"
        )

        transcript_parts = []
        for msg in history[-14:]:
            role_label = "Niño" if msg.rol == "nino" else "Bit"
            transcript_parts.append(f"{role_label}: {msg.contenido}")
        transcript = "\n".join(transcript_parts)

        user_content = (
            f"Historial reciente:\n{transcript}\n\n"
            f"Nuevo mensaje del estudiante: {user_text}\n"
            "Responde como Bit en español para un niño. Devuelve SOLO el JSON estructurado."
        )

        prompt_version = f"{game.id}_{version.version}" if version else game.id
        model = self.settings.openrouter_model

        client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.settings.openrouter_api_key,
        )

        try:
            completion = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            raw = completion.choices[0].message.content or "{}"
            data = json.loads(raw)

            respuesta = data.get("respuesta", "Cuéntame más, ¿qué ves en Scratch?")
            fase = data.get("fase", "responder")
            necesita_aclaracion = bool(data.get("necesita_aclaracion", False))
            razonamiento = data.get("razonamiento_pedagogico", "")

            bloques_raw = data.get("bloques_sugeridos", [])
            bloques_out = [
                {"id": b["id"], "imagen": b["id"], "nombre": _bloque_nombre(bloques_data, b["id"])}
                for b in bloques_raw
                if isinstance(b, dict) and b.get("id") in ids_validos
            ]

            usage = completion.usage
            return TutorReply(
                text=respuesta,
                provider="openrouter",
                model=model,
                prompt_version=prompt_version,
                input_tokens=usage.prompt_tokens if usage else None,
                output_tokens=usage.completion_tokens if usage else None,
                fase=fase,
                bloques_sugeridos=bloques_out,
                necesita_aclaracion=necesita_aclaracion,
                razonamiento_pedagogico=razonamiento,
                metadata={
                    "mode": "openrouter",
                    "game_id": game.id,
                    "conversation_id": str(conversation.id),
                    "fase": fase,
                    "bloques_sugeridos": bloques_out,
                    "razonamiento_pedagogico": razonamiento,
                    "necesita_aclaracion": necesita_aclaracion,
                },
            )

        except Exception as exc:
            return TutorReply(
                text="Probemos paso a paso. ¿Qué ves ahora en Scratch?",
                provider="openrouter",
                model=model,
                prompt_version=prompt_version,
                fase="responder",
                metadata={
                    "mode": "openrouter",
                    "error": str(exc),
                    "game_id": game.id,
                    "fase": "responder",
                    "bloques_sugeridos": [],
                },
            )
