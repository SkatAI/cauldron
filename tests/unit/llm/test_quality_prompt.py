from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate

from cauldron.llm.quality_prompt import (
    QUALITY_HUMAN,
    QUALITY_SYSTEM,
    _EVALUATOR_PROMPT_PATH,
    get_quality_prompt,
    quality_prompt,
)


def test_evaluator_prompt_file_exists():
    """The French evaluator prompt file must exist."""
    assert _EVALUATOR_PROMPT_PATH.exists(), f"Missing: {_EVALUATOR_PROMPT_PATH}"


def test_evaluator_prompt_file_not_empty():
    """The evaluator prompt file should have content."""
    content = _EVALUATOR_PROMPT_PATH.read_text(encoding="utf-8")
    assert len(content) > 100, "Evaluator prompt file seems too short"


def test_evaluator_prompt_contains_criteria():
    """The evaluator prompt should mention the 8 evaluation criteria."""
    content = _EVALUATOR_PROMPT_PATH.read_text(encoding="utf-8")
    assert "Clarté du rôle" in content
    assert "Traits de comportement" in content
    assert "Style de communication" in content


def test_quality_system_template_has_json_structure():
    """The system template should include JSON output format instructions."""
    assert '"criteria"' in QUALITY_SYSTEM
    assert '"overall_score"' in QUALITY_SYSTEM
    assert '"advice"' in QUALITY_SYSTEM
    assert "Clarté du rôle" in QUALITY_SYSTEM


def test_quality_human_template_has_content_placeholder():
    """The human template should have a {content} placeholder."""
    assert "{content}" in QUALITY_HUMAN


def test_get_quality_prompt_returns_chat_prompt_template():
    """get_quality_prompt() should return a valid ChatPromptTemplate."""
    prompt = get_quality_prompt()
    assert isinstance(prompt, ChatPromptTemplate)


def test_quality_prompt_has_two_messages():
    """The prompt should have system and human messages."""
    prompt = get_quality_prompt()
    assert len(prompt.messages) == 2


def test_quality_prompt_can_format_with_content():
    """The prompt should format correctly with content input."""
    prompt = get_quality_prompt()
    formatted = prompt.format_messages(content="# Test Persona\nDescription here.")
    assert len(formatted) == 2
    # System message should contain the evaluator instructions
    assert "Clarté du rôle" in formatted[0].content
    # Human message should contain the test content
    assert "Test Persona" in formatted[1].content


def test_quality_prompt_module_level_instance():
    """The module-level quality_prompt should be ready to use."""
    assert isinstance(quality_prompt, ChatPromptTemplate)
    assert len(quality_prompt.messages) == 2
