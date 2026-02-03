import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cauldron.agent.nodes.content_moderator import moderate_content
from cauldron.agent.state import ValidationState
from cauldron.api.v1.schemas import ErrorCode


def _make_mock_prompt(response_content: str):
    """Create a mock prompt that, when piped with llm, returns a chain with the given response."""
    response = MagicMock()
    response.content = response_content

    mock_prompt = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke = AsyncMock(return_value=response)
    mock_prompt.__or__ = MagicMock(return_value=mock_chain)
    return mock_prompt


def _make_error_prompt(error: Exception):
    """Create a mock prompt whose chain raises an exception."""
    mock_prompt = MagicMock()
    mock_chain = AsyncMock()
    mock_chain.ainvoke = AsyncMock(side_effect=error)
    mock_prompt.__or__ = MagicMock(return_value=mock_chain)
    return mock_prompt


@pytest.mark.asyncio
async def test_clean_content():
    mock_prompt = _make_mock_prompt(json.dumps({"is_toxic": False, "is_nsfw": False, "issues": []}))
    with patch("cauldron.agent.nodes.content_moderator.moderation_prompt", mock_prompt):
        state = ValidationState(content="Hello, I am a friendly assistant.")
        result = await moderate_content(state, llm=MagicMock())
        assert result["moderation_errors"] == []


@pytest.mark.asyncio
async def test_toxic_content():
    mock_prompt = _make_mock_prompt(
        json.dumps(
            {
                "is_toxic": True,
                "is_nsfw": False,
                "issues": [{"type": "toxic_content", "description": "Contains hate speech"}],
            }
        )
    )
    with patch("cauldron.agent.nodes.content_moderator.moderation_prompt", mock_prompt):
        state = ValidationState(content="Some toxic content here.")
        result = await moderate_content(state, llm=MagicMock())
        errors = result["moderation_errors"]
        assert len(errors) == 1
        assert errors[0].code == ErrorCode.TOXIC_CONTENT
        assert "contenu toxique" in errors[0].message


@pytest.mark.asyncio
async def test_nsfw_content():
    mock_prompt = _make_mock_prompt(
        json.dumps(
            {
                "is_toxic": False,
                "is_nsfw": True,
                "issues": [{"type": "nsfw_content", "description": "Contains explicit content"}],
            }
        )
    )
    with patch("cauldron.agent.nodes.content_moderator.moderation_prompt", mock_prompt):
        state = ValidationState(content="Some NSFW content here.")
        result = await moderate_content(state, llm=MagicMock())
        errors = result["moderation_errors"]
        assert len(errors) == 1
        assert errors[0].code == ErrorCode.NSFW_CONTENT


@pytest.mark.asyncio
async def test_invalid_json_response():
    mock_prompt = _make_mock_prompt("not valid json")
    with patch("cauldron.agent.nodes.content_moderator.moderation_prompt", mock_prompt):
        state = ValidationState(content="Some content.")
        result = await moderate_content(state, llm=MagicMock())
        errors = result["moderation_errors"]
        assert len(errors) == 1
        assert errors[0].code == ErrorCode.INTERNAL_ERROR


@pytest.mark.asyncio
async def test_llm_exception():
    mock_prompt = _make_error_prompt(RuntimeError("LLM unavailable"))
    with patch("cauldron.agent.nodes.content_moderator.moderation_prompt", mock_prompt):
        state = ValidationState(content="Some content.")
        result = await moderate_content(state, llm=MagicMock())
        errors = result["moderation_errors"]
        assert len(errors) == 1
        assert errors[0].code == ErrorCode.INTERNAL_ERROR
        assert "Échec de la vérification de modération" in errors[0].message
