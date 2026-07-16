from app.core.settings import Settings
from app.llm.base import TutorLLM, TutorReply
from app.llm.prompts import build_system_instruction
from app.models import Conversation, Game, GameVersion, Message


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

        client = genai.Client(api_key=self.settings.gemini_api_key)
        # Prompt base de Bit (andamiaje socrático) + referencia privada del juego actual
        # (solución, bloques clave traducidos a su etiqueta real de Scratch y video).
        # Los datos ausentes se omiten; nunca se inventan.
        system_instruction = build_system_instruction(
            titulo=game.titulo,
            descripcion_solucion=game.descripcion_solucion,
            bloques_clave=game.bloques_clave,
            url_video=game.url_video,
            base_prompt=version.system_prompt if version else None,
        )
        transcript = "\n".join(
            f"{message.orden_mensaje}. {'Estudiante' if message.rol == 'nino' else 'Bit'}: {message.contenido}"
            for message in history[-16:]
        )
        contents = (
            f"Historial reciente:\n{transcript}\n\n"
            f"Nuevo mensaje del estudiante: {user_text}\n"
            "Responde siguiendo tus reglas: breve, cálido, una sola pregunta o pista por turno."
        )
        response = client.models.generate_content(
            model=self.settings.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
            ),
        )
        prompt_version = f"{game.id}_{version.version}" if version else None
        usage = response.usage_metadata
        return TutorReply(
            text=response.text or "Probemos paso a paso. ¿Qué ves ahora en Scratch?",
            provider="gemini",
            model=response.model_version or self.settings.gemini_model,
            prompt_version=prompt_version,
            input_tokens=usage.prompt_token_count if usage else None,
            output_tokens=usage.candidates_token_count if usage else None,
            metadata={
                "mode": "gemini",
                "game_id": game.id,
                "conversation_id": str(conversation.id),
                "response_id": response.response_id,
            },
        )
