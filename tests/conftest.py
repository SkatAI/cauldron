from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from cauldron.api.v1.schemas import ValidateRequest


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
