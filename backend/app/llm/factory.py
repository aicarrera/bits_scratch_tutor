from app.core.settings import Settings
from app.llm.base import TutorLLM
from app.llm.gemini import GeminiTutorLLM
from app.llm.mock import MockTutorLLM
from app.llm.openrouter import OpenRouterTutorLLM


def build_llm(settings: Settings) -> TutorLLM:
    if settings.llm_mode == "gemini" and settings.gemini_api_key:
        return GeminiTutorLLM(settings)
    if settings.llm_mode == "openrouter" and settings.openrouter_api_key:
        return OpenRouterTutorLLM(settings)
    return MockTutorLLM()
