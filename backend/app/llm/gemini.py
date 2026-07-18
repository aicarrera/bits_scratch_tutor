import json
from typing import Literal

from pydantic import BaseModel

from app.core.settings import Settings
from app.llm.base import TutorLLM, TutorReply
from app.llm.catalog import (
    HINT_PROGRESSION_BASE,
    bloque_nombre,
    bloques_ids,
    build_game_context,
    clean_opciones,
    load_bloques,
)
from app.models import Conversation, Game, GameVersion, Message


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

        bloques_data = load_bloques()
        ids_validos = bloques_ids(bloques_data)

        # Build system instruction
        game_context = build_game_context(game, version, bloques_data)

        catalog_json = json.dumps(bloques_data, ensure_ascii=False)
        system_instruction = (
            HINT_PROGRESSION_BASE
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
                {"id": b.id, "imagen": b.id, "nombre": bloque_nombre(bloques_data, b.id)}
                for b in bloques_validos
            ]

            # Sanitize quick-reply options: short, non-empty, de-duplicated, capped at 3
            opciones_out = clean_opciones(data.opciones_respuesta)

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
