from app.llm.base import TutorLLM, TutorReply
from app.models import Conversation, Game, GameVersion, Message

# Pre-defined structured responses per game (text, fase, blocks to show)
_GAME_RESPONSES: dict[str, list[tuple[str, str, list[str]]]] = {
    "ej_001": [
        (
            "Mira este bloque 👇 ¿Qué crees que hace si lo pones en el programa? ¡Pruébalo y cuéntame!",
            "predecir",
            ["eventos_bandera_verde"],
        ),
        (
            "¡Bien! Ahora para que el gato se mueva, fíjate en los bloques de Movimiento. ¿Cuál parece moverlo?",
            "pista",
            [],
        ),
        (
            "Para que baile de verdad, necesitas repetir los movimientos. ¿Ves algún bloque que repita algo?",
            "pista",
            ["control_repetir_veces"],
        ),
    ],
    "ej_002": [
        (
            "La mariposa puede cambiar de aspecto con sus disfraces. Mira este bloque 👇 ¿qué crees que hace?",
            "predecir",
            ["apariencia_siguiente_disfraz"],
        ),
        (
            "Si quieres que la animación se vea suave, agrega una pequeña pausa entre cambios.",
            "pista",
            ["control_esperar_segundos"],
        ),
    ],
    "ej_003": [
        (
            "Para mover al personaje con las flechas, necesitas un bloque que escuche el teclado. ¿Qué bloque usarías?",
            "predecir",
            ["eventos_tecla_presionada"],
        ),
        (
            "Para contar puntos, primero crea una variable. ¿La ves en la sección Variables?",
            "pista",
            ["variables_boton_crear"],
        ),
        (
            "Cuando el personaje toca la estrella, la variable de puntos debe cambiar. Mira este bloque 👇",
            "confirmar",
            ["variables_cambiar", "sensores_tocando"],
        ),
    ],
    "ej_004": [
        (
            "Para que el personaje salte, su posición Y debe subir. Mira este bloque 👇 ¿qué crees que hace?",
            "predecir",
            ["movimiento_cambiar_y"],
        ),
        (
            "Los obstáculos pueden moverse solos usando el bloque 'Por siempre'. ¿Lo encuentras en Control?",
            "pista",
            ["control_por_siempre"],
        ),
    ],
    "ej_005": [
        (
            "Para que dos personajes hablen en orden, uno debe esperar a que el otro termine. ¿Qué bloque ayuda con eso?",
            "predecir",
            ["apariencia_decir_segundos"],
        ),
        (
            "Para que el segundo personaje sepa cuándo hablar, puedes enviarle un mensaje. Mira este bloque 👇",
            "confirmar",
            ["eventos_enviar_mensaje", "eventos_al_recibir_mensaje"],
        ),
    ],
    "ej_006": [
        (
            "Para cambiar la escena de tu historia, necesitas cambiar el fondo. Mira este bloque 👇 ¿qué crees que hace?",
            "predecir",
            ["apariencia_cambiar_fondo"],
        ),
        (
            "Cuando el fondo cambie, puedes hacer que el personaje diga algo. ¿Qué bloque usarías para eso?",
            "pista",
            ["apariencia_decir_segundos"],
        ),
    ],
    "proyecto_libre": [
        (
            "¡Cuéntame qué quieres crear! ¿Tu idea tiene un personaje que se mueve, algo que el jugador controla, o una historia?",
            "responder",
            [],
        ),
        (
            "Buena idea. Empecemos por lo más importante: ¿qué debe pasar cuando arranca el programa?",
            "explorar",
            ["eventos_bandera_verde"],
        ),
    ],
}

_BLOCK_NAMES: dict[str, str] = {
    "eventos_bandera_verde": "Al presionar bandera verde",
    "eventos_tecla_presionada": "Al presionar tecla",
    "eventos_al_recibir_mensaje": "Al recibir mensaje",
    "eventos_enviar_mensaje": "Enviar mensaje",
    "movimiento_mover_pasos": "Mover pasos",
    "movimiento_cambiar_y": "Cambiar y",
    "movimiento_cambiar_x": "Cambiar x",
    "control_repetir_veces": "Repetir veces",
    "control_por_siempre": "Por siempre",
    "control_esperar_segundos": "Esperar segundos",
    "control_si_entonces": "Si entonces",
    "apariencia_siguiente_disfraz": "Siguiente disfraz",
    "apariencia_cambiar_disfraz": "Cambiar disfraz",
    "apariencia_decir_segundos": "Decir durante segundos",
    "apariencia_decir": "Decir",
    "apariencia_cambiar_fondo": "Cambiar fondo",
    "variables_boton_crear": "Crear una variable",
    "variables_cambiar": "Cambiar variable",
    "variables_fijar": "Fijar variable",
    "sensores_tocando": "Tocando objeto",
}


def _make_bloque(bloque_id: str) -> dict:
    return {
        "id": bloque_id,
        "imagen": bloque_id,
        "nombre": _BLOCK_NAMES.get(bloque_id, bloque_id),
    }


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

        if any(word in normalized for word in ("hola", "hi", "buenas", "hey")):
            text = "¡Hola! Soy Bit, tu tutor de Scratch. ¿Listo para crear algo genial?"
            fase = "responder"
            block_ids: list[str] = []
        elif "no entiendo" in normalized or ("no" in normalized and "puedo" in normalized):
            text = "Está bien, vamos despacio. Dime qué ves en Scratch y te doy una pista."
            fase = "responder"
            block_ids = []
        else:
            options = _GAME_RESPONSES.get(game.id, _GAME_RESPONSES["proyecto_libre"])
            child_messages = [m for m in history if m.rol == "nino"]
            idx = len(child_messages) % len(options)
            text, fase, block_ids = options[idx]

        bloques_sugeridos = [_make_bloque(bid) for bid in block_ids]
        prompt_version = f"{game.id}_{version.version}" if version else game.id

        return TutorReply(
            text=text,
            provider="mock",
            model="mock-hint-progression-v2",
            prompt_version=prompt_version,
            fase=fase,
            bloques_sugeridos=bloques_sugeridos,
            necesita_aclaracion=False,
            razonamiento_pedagogico=f"Mock: turno {len(history)}, juego {game.id}",
            metadata={
                "mode": "mock",
                "game_id": game.id,
                "conversation_id": str(conversation.id),
                "fase": fase,
                "bloques_sugeridos": bloques_sugeridos,
                "razonamiento_pedagogico": f"Mock: turno {len(history)}",
                "necesita_aclaracion": False,
            },
        )
