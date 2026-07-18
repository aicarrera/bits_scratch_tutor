import json

from app.core.settings import Settings
from app.llm.base import TutorLLM, TutorReply
from app.llm.catalog import (
    HINT_PROGRESSION_BASE,
    OPENROUTER_JSON_TAIL,
    bloque_nombre,
    bloques_ids,
    build_game_context,
    clean_opciones,
    load_bloques,
)
from app.models import Conversation, Game, GameVersion, Message

# OpenRouter necesita instruir el JSON de salida explícitamente (no hay response_schema).
_HINT_PROGRESSION_BASE = HINT_PROGRESSION_BASE + OPENROUTER_JSON_TAIL


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

        bloques_data = load_bloques()
        ids_validos = bloques_ids(bloques_data)

        game_context = build_game_context(game, version, bloques_data)

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
                {"id": b["id"], "imagen": b["id"], "nombre": bloque_nombre(bloques_data, b["id"])}
                for b in bloques_raw
                if isinstance(b, dict) and b.get("id") in ids_validos
            ]

            opciones_out = clean_opciones(data.get("opciones_respuesta", []))

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
                opciones_respuesta=opciones_out,
                necesita_aclaracion=necesita_aclaracion,
                razonamiento_pedagogico=razonamiento,
                metadata={
                    "mode": "openrouter",
                    "game_id": game.id,
                    "conversation_id": str(conversation.id),
                    "fase": fase,
                    "bloques_sugeridos": bloques_out,
                    "opciones_respuesta": opciones_out,
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
