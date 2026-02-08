import pytest

from cauldron.api.v1.schemas import QualityCriterion, QualityEvaluation, ValidationError


@pytest.mark.integration
class TestValidationEndpoint:
    def test_health_check(self, test_client):
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_validate_valid_content(self, test_client, mock_graph, valid_markdown, auth_headers):
        mock_graph.ainvoke.return_value = {"all_errors": []}
        response = test_client.post("/v1/validate", json={"content": valid_markdown}, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "valid"
        assert data["errors"] == []

    def test_validate_valid_content_with_quality(
        self, test_client, mock_graph, valid_markdown, auth_headers
    ):
        quality_eval = QualityEvaluation(
            criteria=[
                QualityCriterion(name="Clarté du rôle", justification="Bien défini"),
            ],
            advice="Continuer ainsi.",
        )
        mock_graph.ainvoke.return_value = {
            "all_errors": [],
            "quality_evaluation": quality_eval,
        }
        response = test_client.post("/v1/validate", json={"content": valid_markdown}, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "valid"
        assert data["quality"] is not None
        assert len(data["quality"]["criteria"]) == 1

    def test_validate_toxic_content(self, test_client, mock_graph, auth_headers):
        mock_graph.ainvoke.return_value = {
            "all_errors": [
                ValidationError(
                    code="toxic_content",
                    message="Le contenu contient du contenu toxique",
                    detail="Hate speech detected",
                )
            ]
        }
        response = test_client.post("/v1/validate", json={"content": "# Toxic content"}, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "invalid"
        assert len(data["errors"]) == 1
        assert data["errors"][0]["code"] == "toxic_content"

    def test_validate_empty_content(self, test_client, auth_headers):
        response = test_client.post("/v1/validate", json={"content": ""}, headers=auth_headers)
        assert response.status_code == 422

    def test_validate_missing_content(self, test_client, auth_headers):
        response = test_client.post("/v1/validate", json={}, headers=auth_headers)
        assert response.status_code == 422

    def test_validate_graph_error(self, test_client, mock_graph, auth_headers):
        mock_graph.ainvoke.side_effect = RuntimeError("LLM unavailable")
        response = test_client.post("/v1/validate", json={"content": "# Test"}, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "invalid"
        assert data["errors"][0]["code"] == "internal_error"

    def test_validate_requires_bff_secret_when_configured(
        self, test_client, monkeypatch, mock_graph
    ):
        monkeypatch.setattr("cauldron.main.settings.bff_shared_secret", "test-secret")
        mock_graph.ainvoke.return_value = {"all_errors": []}

        unauthorized = test_client.post("/v1/validate", json={"content": "# Test"})
        assert unauthorized.status_code == 401
        assert unauthorized.json() == {"detail": "Unauthorized"}

        authorized = test_client.post(
            "/v1/validate",
            json={"content": "# Test"},
            headers={"X-BFF-Secret": "test-secret"},
        )
        assert authorized.status_code == 200

    def test_health_remains_public_when_bff_secret_configured(self, test_client, monkeypatch):
        monkeypatch.setattr("cauldron.main.settings.bff_shared_secret", "test-secret")

        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
