import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from cauldron.agent.nodes.quality_evaluator import evaluate_quality
from cauldron.agent.state import ValidationState


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


def _sample_quality_response():
    """Return a sample quality evaluation JSON response."""
    return {
        "criteria": [
            {"name": "Clarté du rôle", "justification": "Bien défini"},
            {
                "name": "Traits de comportement et attitude",
                "justification": "Suffisant",
            },
            {"name": "Style de communication", "justification": "Clair"},
            {"name": "Motivations et objectifs", "justification": "À améliorer"},
            {"name": "Contraintes et limitations", "justification": "Présentes"},
            {"name": "Instructions de cohérence", "justification": "Explicites"},
            {"name": "Pertinence contextuelle", "justification": "Parfait"},
            {"name": "Clarté et concision", "justification": "Bon équilibre"},
        ],
        "advice": "Améliorer les motivations du persona.",
    }


@pytest.mark.asyncio
async def test_quality_evaluation_success():
    mock_prompt = _make_mock_prompt(json.dumps(_sample_quality_response()))
    with patch("cauldron.agent.nodes.quality_evaluator.quality_prompt", mock_prompt):
        state = ValidationState(content="# Persona Test\nDescription du persona.")
        result = await evaluate_quality(state, llm=MagicMock())
        quality = result["quality_evaluation"]
        assert quality is not None
        assert len(quality.criteria) == 8
        assert quality.advice == "Améliorer les motivations du persona."


@pytest.mark.asyncio
async def test_quality_evaluation_parses_criteria():
    mock_prompt = _make_mock_prompt(json.dumps(_sample_quality_response()))
    with patch("cauldron.agent.nodes.quality_evaluator.quality_prompt", mock_prompt):
        state = ValidationState(content="# Persona Test")
        result = await evaluate_quality(state, llm=MagicMock())
        quality = result["quality_evaluation"]
        assert quality is not None
        criteria_names = [c.name for c in quality.criteria]
        assert "Clarté du rôle" in criteria_names
        assert "Pertinence contextuelle" in criteria_names


@pytest.mark.asyncio
async def test_quality_evaluation_with_markdown_fences():
    response_with_fences = f"```json\n{json.dumps(_sample_quality_response())}\n```"
    mock_prompt = _make_mock_prompt(response_with_fences)
    with patch("cauldron.agent.nodes.quality_evaluator.quality_prompt", mock_prompt):
        state = ValidationState(content="# Persona Test")
        result = await evaluate_quality(state, llm=MagicMock())
        quality = result["quality_evaluation"]
        assert quality is not None


@pytest.mark.asyncio
async def test_quality_evaluation_invalid_json():
    mock_prompt = _make_mock_prompt("not valid json at all")
    with patch("cauldron.agent.nodes.quality_evaluator.quality_prompt", mock_prompt):
        state = ValidationState(content="# Persona Test")
        result = await evaluate_quality(state, llm=MagicMock())
        assert result["quality_evaluation"] is None


@pytest.mark.asyncio
async def test_quality_evaluation_llm_exception():
    mock_prompt = _make_error_prompt(RuntimeError("LLM unavailable"))
    with patch("cauldron.agent.nodes.quality_evaluator.quality_prompt", mock_prompt):
        state = ValidationState(content="# Persona Test")
        result = await evaluate_quality(state, llm=MagicMock())
        assert result["quality_evaluation"] is None


@pytest.mark.asyncio
async def test_quality_evaluation_missing_fields():
    """Test handling of partial/missing fields in response."""
    partial_response = {
        "criteria": [{"name": "Test", "justification": "OK"}],
        # missing advice
    }
    mock_prompt = _make_mock_prompt(json.dumps(partial_response))
    with patch("cauldron.agent.nodes.quality_evaluator.quality_prompt", mock_prompt):
        state = ValidationState(content="# Persona Test")
        result = await evaluate_quality(state, llm=MagicMock())
        quality = result["quality_evaluation"]
        assert quality is not None
        assert quality.advice == ""
        assert len(quality.criteria) == 1
