"""Verifica de punta a punta que el proveedor de PRODUCCIÓN (openrouter) inyecta
la solución de referencia y los bloques clave del juego en el system prompt real,
usando un Game real de la base y el modelo google/gemini-3.5-flash.

Se intercepta la llamada a la API (sin red) para capturar el prompt enviado.
"""

import json
import sys
import types

from app.core.settings import Settings
from app.llm.openrouter import OpenRouterTutorLLM
from app.repositories.games import GamesRepository


def _install_fake_openai(monkeypatch, captured: dict) -> None:
    class FakeCompletions:
        async def create(self, **kwargs):
            captured["messages"] = kwargs["messages"]
            captured["model"] = kwargs["model"]
            content = json.dumps(
                {
                    "respuesta": "¿Qué crees que hace este bloque?",
                    "fase": "responder",
                    "bloques_sugeridos": [],
                    "opciones_respuesta": ["No estoy seguro"],
                    "necesita_aclaracion": False,
                    "razonamiento_pedagogico": "",
                }
            )
            msg = types.SimpleNamespace(content=content)
            choice = types.SimpleNamespace(message=msg)
            usage = types.SimpleNamespace(prompt_tokens=1, completion_tokens=1)
            return types.SimpleNamespace(choices=[choice], usage=usage)

    class FakeChat:
        def __init__(self) -> None:
            self.completions = FakeCompletions()

    class FakeAsyncOpenAI:
        def __init__(self, **kwargs) -> None:
            self.chat = FakeChat()

    fake_module = types.ModuleType("openai")
    fake_module.AsyncOpenAI = FakeAsyncOpenAI
    monkeypatch.setitem(sys.modules, "openai", fake_module)


def _settings() -> Settings:
    return Settings(
        llm_mode="openrouter",
        openrouter_api_key="test-key",
        openrouter_model="google/gemini-3.5-flash",
    )


async def test_prompt_incluye_solucion_y_bloques_cuando_existen(db_session, monkeypatch) -> None:
    captured: dict = {}
    _install_fake_openai(monkeypatch, captured)

    repo = GamesRepository(db_session)
    game = await repo.get_game("ej_001")  # tiene descripcion_solucion + bloques_clave
    version = await repo.get_active_version("ej_001")

    llm = OpenRouterTutorLLM(_settings())
    reply = await llm.generate_reply(
        conversation=types.SimpleNamespace(id="conv-1"),
        game=game,
        version=version,
        history=[],
        user_text="hola, ¿me ayudas?",
    )

    system_prompt = captured["messages"][0]["content"]
    # 1) usa el modelo pedido
    assert captured["model"] == "google/gemini-3.5-flash"
    # 2) la solución de referencia del juego está en el prompt
    assert "SOLUCIÓN DE REFERENCIA" in system_prompt
    assert game.descripcion_solucion[:40] in system_prompt
    # 3) los bloques clave están, traducidos a su nombre real del catálogo
    assert "BLOQUES CLAVE DE ESTE EJERCICIO" in system_prompt
    assert "eventos_bandera_verde" in system_prompt
    assert "Al presionar bandera verde" in system_prompt
    # 4) el guardrail anti-spoiler viaja en el prompt de producción
    assert "Nunca pongas la solución completa dentro de una opción" in system_prompt
    assert reply.provider == "openrouter"
    assert reply.model == "google/gemini-3.5-flash"


async def test_prompt_omite_solucion_y_bloques_cuando_son_null(db_session, monkeypatch) -> None:
    captured: dict = {}
    _install_fake_openai(monkeypatch, captured)

    repo = GamesRepository(db_session)
    game = await repo.get_game("proyecto_libre")  # sin solución ni bloques
    version = await repo.get_active_version("proyecto_libre")
    assert game.descripcion_solucion is None
    assert game.bloques_clave is None

    llm = OpenRouterTutorLLM(_settings())
    await llm.generate_reply(
        conversation=types.SimpleNamespace(id="conv-2"),
        game=game,
        version=version,
        history=[],
        user_text="quiero crear algo",
    )

    system_prompt = captured["messages"][0]["content"]
    # sin datos → no aparecen esas secciones (no se inventan)
    assert "SOLUCIÓN DE REFERENCIA" not in system_prompt
    assert "BLOQUES CLAVE DE ESTE EJERCICIO" not in system_prompt
    # pero el prompt base y el título del juego sí siguen
    assert "Proyecto libre" in system_prompt
