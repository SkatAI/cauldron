from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from cauldron.api.v1.schemas import ValidateRequest
from cauldron.config.loader import load_sections_config
from cauldron.config.sections import SectionsConfig

FIXTURES_DIR = Path(__file__).parent


@pytest.fixture
def sections_config() -> SectionsConfig:
    return load_sections_config(Path(__file__).parent.parent / "config" / "required_sections.yaml")


@pytest.fixture
def valid_markdown() -> str:
    return """\
# Simulation d'entretien sociologique - Persona Marie

## Contexte de l'entretien
Simulation d'une recherche sociologique.

## PROFIL PERSONNEL

### Résumé du profil
Étudiante en sociologie, curieuse et engagée.

### Donneés sociodemographiques
*   **Prénom** : Marie
*   **âge** : 23

### **PARCOURS ACADÉMIQUE**
*   **Niveau d'études** : Master 2

### Style de Langage et d'Expression
*   **Niveau de Langage :** Courant

### **Méthode de Réflexion et d'Argumentation**
Raisonnement inductif.

## Rapport avec l'intelligence Artificielle
Description du rapport avec l'IA.

## Instructions pour l'entretien
Tu incarnes Marie lors d'un entretien sociologique.
"""


@pytest.fixture
def invalid_markdown_missing_sections() -> str:
    return """\
# Simulation d'entretien sociologique - Persona Marie

## Contexte de l'entretien
Simulation d'une recherche sociologique.

## PROFIL PERSONNEL

### Résumé du profil
Étudiante en sociologie.
"""


@pytest.fixture
def mock_llm():
    llm = MagicMock()
    return llm


@pytest.fixture
def mock_graph():
    graph = AsyncMock()
    return graph


@pytest.fixture
def test_client(mock_graph):
    from cauldron.main import create_app

    app = create_app()
    app.state.graph = mock_graph
    return TestClient(app)


@pytest.fixture
def validate_request_valid(valid_markdown) -> ValidateRequest:
    return ValidateRequest(content=valid_markdown)
