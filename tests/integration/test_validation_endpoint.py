import pytest

from cauldron.api.v1.schemas import ValidationError


@pytest.mark.integration
class TestValidationEndpoint:
    def test_health_check(self, test_client):
        response = test_client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_validate_valid_content(self, test_client, mock_graph, valid_markdown):
        mock_graph.ainvoke.return_value = {"all_errors": []}
        response = test_client.post("/v1/validate", json={"content": valid_markdown})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "valid"
        assert data["errors"] == []

    def test_validate_invalid_content(self, test_client, mock_graph):
        mock_graph.ainvoke.return_value = {
            "all_errors": [
                ValidationError(
                    code="missing_section",
                    message="Required section 'Tone' is missing",
                    detail=None,
                )
            ]
        }
        response = test_client.post("/v1/validate", json={"content": "# Personality\nSome text."})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "invalid"
        assert len(data["errors"]) == 1
        assert data["errors"][0]["code"] == "missing_section"

    def test_validate_empty_content(self, test_client):
        response = test_client.post("/v1/validate", json={"content": ""})
        assert response.status_code == 422

    def test_validate_missing_content(self, test_client):
        response = test_client.post("/v1/validate", json={})
        assert response.status_code == 422

    def test_validate_graph_error(self, test_client, mock_graph):
        mock_graph.ainvoke.side_effect = RuntimeError("LLM unavailable")
        response = test_client.post("/v1/validate", json={"content": "# Test"})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "invalid"
        assert data["errors"][0]["code"] == "internal_error"
