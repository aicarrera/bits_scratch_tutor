from app.core.settings import Settings
from app.llm.base import TutorLLM, TutorReply
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
        system_instruction = version.system_prompt if version else (
            "Eres Bit, tutor de Scratch para niños. Responde breve, amable y con preguntas."
        )
        transcript = "\n".join(
            f"{message.orden_mensaje}. {'Estudiante' if message.rol == 'nino' else 'Bit'}: {message.contenido}"
            for message in history[-16:]
        )
        contents = (
            f"Juego: {game.titulo}\n"
            f"Conversación actual: {conversation.id}\n"
            f"Historial reciente:\n{transcript}\n\n"
            f"Nuevo mensaje del estudiante: {user_text}\n"
            "Responde con una pista breve en español para un niño de 8 a 10 años. "
            "No des la solución completa. Haz una sola pregunta o da una sola pista por turno."
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
