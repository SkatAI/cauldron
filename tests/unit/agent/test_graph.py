from unittest.mock import MagicMock

from cauldron.agent.graph import build_graph
from cauldron.config.sections import SectionConfig, SectionsConfig


def test_build_graph_creates_nodes():
    config = SectionsConfig(
        sections=[
            SectionConfig(name="Personality", heading_pattern="^#{1,3}\\s+Personality"),
        ]
    )
    llm = MagicMock()
    graph = build_graph(config, llm)
    assert "check_sections" in graph.nodes
    assert "moderate_content" in graph.nodes
    assert "aggregate_results" in graph.nodes
