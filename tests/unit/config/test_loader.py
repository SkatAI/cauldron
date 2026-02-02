from pathlib import Path

import pytest

from cauldron.config.loader import load_sections_config


def test_load_sections_config():
    config = load_sections_config(
        Path(__file__).parent.parent.parent.parent / "config" / "required_sections.yaml"
    )
    assert len(config.sections) == 9
    names = [s.name for s in config.sections]
    assert "Contexte de l'entretien" in names
    assert "Profil personnel" in names
    assert "Parcours académique" in names


def test_load_sections_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_sections_config("nonexistent.yaml")
