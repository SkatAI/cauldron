from langchain_openai import ChatOpenAI

from cauldron.settings import settings


class ChatOpenRouter(ChatOpenAI):
    """ChatOpenAI subclass configured for OpenRouter."""

    def __init__(self, **kwargs: object) -> None:
        defaults: dict[str, object] = {
            "openai_api_key": settings.openrouter_api_key,
            "openai_api_base": settings.openrouter_base_url,
            "model_name": settings.openrouter_model,
            "temperature": 0.0,
        }
        defaults.update(kwargs)
        super().__init__(**defaults)


def get_llm() -> ChatOpenRouter:
    return ChatOpenRouter()
