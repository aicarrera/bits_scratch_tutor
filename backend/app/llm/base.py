from dataclasses import dataclass, field

from app.models import Conversation, Game, GameVersion, Message


@dataclass
class TutorReply:
    text: str
    provider: str
    model: str | None
    prompt_version: str | None
    input_tokens: int | None = None
    output_tokens: int | None = None
    fase: str = "responder"
    bloques_sugeridos: list[dict] = field(default_factory=list)
    necesita_aclaracion: bool = False
    razonamiento_pedagogico: str = ""
    metadata: dict[str, object] = field(default_factory=dict)


class TutorLLM:
    async def generate_reply(
        self,
        conversation: Conversation,
        game: Game,
        version: GameVersion | None,
        history: list[Message],
        user_text: str,
    ) -> TutorReply:
        raise NotImplementedError
