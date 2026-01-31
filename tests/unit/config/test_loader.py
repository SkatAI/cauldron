from pathlib import Path

import pytest

from cauldron.config.loader import load_sections_config


def test_load_sections_config():
    config = load_sections_config(
        Path(__file__).parent.parent.parent.parent / "config" / "required_sections.yaml"
    )
    assert len(config.sections) == 4
    names = [s.name for s in config.sections]
    assert "Personality" in names
    assert "Tone" in names
    assert "Behavior" in names
    assert "Constraints" in names
    assert all(s.required for s in config.sections)


def test_load_sections_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_sections_config("nonexistent.yaml")
