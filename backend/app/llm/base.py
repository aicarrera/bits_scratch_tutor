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
