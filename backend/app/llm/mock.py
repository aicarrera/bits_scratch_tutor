from app.llm.base import TutorLLM, TutorReply
from app.models import Conversation, Game, GameVersion, Message


class MockTutorLLM(TutorLLM):
    async def generate_reply(
        self,
        conversation: Conversation,
        game: Game,
        version: GameVersion | None,
        history: list[Message],
        user_text: str,
    ) -> TutorReply:
        normalized = user_text.lower()
        exercise_responses = {
            "ej_001": [
                "¡Buena pregunta! Mira la categoría Movimiento. ¿Qué bloque crees que mueve al gato?",
                "Casi lo tienes. Prueba una acción pequeña y dime qué pasó.",
                "Para repetir un baile, busca un bloque que haga algo muchas veces.",
            ],
            "ej_002": [
                "La mariposa puede cambiar de disfraz. ¿Qué bloque de Apariencia podría ayudarte?",
                "Si quieres que se vea suave, agrega una espera pequeñita entre cambios.",
            ],
            "ej_003": [
                "Para sumar puntos necesitas una variable. ¿Cómo llamarías a esa variable?",
                "Primero prueba detectar si toca la estrella. Luego pensamos en sumar.",
                "Las flechas suelen vivir en Eventos. ¿Qué evento aparece cuando presionas una tecla?",
            ],
            "ej_004": [
                "Cuando alguien salta, cambia su posición Y. ¿Qué número probarías primero?",
                "Los obstáculos pueden moverse desde la derecha hacia la izquierda.",
            ],
            "ej_005": [
                "Para un diálogo claro, haz que un personaje hable y luego envíe un mensaje al otro.",
                "Piensa en una frase corta para el primer personaje. ¿Qué diría?",
            ],
            "ej_006": [
                "Un cambio de fondo puede marcar una nueva escena. ¿Cuál sería la primera escena?",
                "Cuando el fondo cambie, un personaje puede decir o hacer algo distinto.",
            ],
            "proyecto_libre": [
                "Me gusta esa idea. Dividámosla en tres pasos: personaje, acción y meta. ¿Cuál hacemos primero?",
                "Suena creativo. ¿Quieres empezar por el escenario o por lo que hará el personaje?",
            ],
        }
        if "punto" in normalized or "variable" in normalized:
            text = "Para contar algo, crea una variable como puntos. ¿En qué momento debería subir?"
        elif "no" in normalized and ("entiendo" in normalized or "puedo" in normalized):
            text = "Está bien ir despacio. Dime qué parte ves en Scratch y te doy una pista corta."
        else:
            options = exercise_responses.get(game.id, exercise_responses["proyecto_libre"])
            text = options[len(history) % len(options)]
        prompt_version = f"{game.id}_{version.version}" if version else None
        return TutorReply(
            text=text,
            provider="mock",
            model="mock-rules-v1",
            prompt_version=prompt_version,
            metadata={
                "mode": "mock",
                "game_id": game.id,
                "conversation_id": str(conversation.id),
            },
        )
