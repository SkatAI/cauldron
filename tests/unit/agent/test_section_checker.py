from cauldron.agent.nodes.section_checker import check_sections
from cauldron.agent.state import ValidationState
from cauldron.api.v1.schemas import ErrorCode


def test_all_sections_present(sections_config, valid_markdown):
    state = ValidationState(content=valid_markdown)
    result = check_sections(state, config=sections_config)
    assert result["section_errors"] == []


def test_missing_sections(sections_config, invalid_markdown_missing_sections):
    state = ValidationState(content=invalid_markdown_missing_sections)
    result = check_sections(state, config=sections_config)
    errors = result["section_errors"]
    assert len(errors) == 2
    missing_names = {e.message for e in errors}
    assert "Required section 'Behavior' is missing" in missing_names
    assert "Required section 'Constraints' is missing" in missing_names
    assert all(e.code == ErrorCode.MISSING_SECTION for e in errors)


def test_empty_content(sections_config):
    state = ValidationState(content="")
    result = check_sections(state, config=sections_config)
    errors = result["section_errors"]
    assert len(errors) == 4


def test_heading_level_variations(sections_config):
    content = """### Personality
Some text.
### Tone
Some text.
### Behavior
Some text.
### Constraints
Some text.
"""
    state = ValidationState(content=content)
    result = check_sections(state, config=sections_config)
    assert result["section_errors"] == []
