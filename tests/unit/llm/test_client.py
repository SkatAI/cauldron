from unittest.mock import patch

from cauldron.llm.client import ChatOpenRouter, get_llm


def test_chat_open_router_defaults():
    with patch("cauldron.llm.client.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test-key"
        mock_settings.openrouter_base_url = "https://openrouter.ai/api/v1"
        mock_settings.openrouter_model = "test-model"
        client = ChatOpenRouter()
        assert client.model_name == "test-model"
        assert client.openai_api_key.get_secret_value() == "test-key"


def test_get_llm_returns_instance():
    with patch("cauldron.llm.client.settings") as mock_settings:
        mock_settings.openrouter_api_key = "test-key"
        mock_settings.openrouter_base_url = "https://openrouter.ai/api/v1"
        mock_settings.openrouter_model = "test-model"
        llm = get_llm()
        assert isinstance(llm, ChatOpenRouter)
