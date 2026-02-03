from unittest.mock import MagicMock

from cauldron.agent.graph import build_graph


def test_build_graph_creates_nodes():
    llm = MagicMock()
    graph = build_graph(llm)
    assert "evaluate_quality" in graph.nodes
    assert "moderate_content" in graph.nodes
    assert "aggregate_results" in graph.nodes
