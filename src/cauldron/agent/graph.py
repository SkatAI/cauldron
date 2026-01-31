from functools import partial

from langgraph.graph import END, START, StateGraph

from cauldron.agent.nodes.content_moderator import moderate_content
from cauldron.agent.nodes.result_aggregator import aggregate_results
from cauldron.agent.nodes.section_checker import check_sections
from cauldron.agent.state import ValidationState
from cauldron.config.sections import SectionsConfig
from cauldron.llm.client import ChatOpenRouter


def _should_moderate(state: ValidationState) -> str:
    """Skip moderation if content is empty."""
    content = state.get("content", "")
    if not content or not content.strip():
        return "aggregate_results"
    return "moderate_content"


def build_graph(sections_config: SectionsConfig, llm: ChatOpenRouter) -> StateGraph:
    """Build the validation LangGraph workflow."""
    graph = StateGraph(ValidationState)

    graph.add_node("check_sections", partial(check_sections, config=sections_config))
    graph.add_node("moderate_content", partial(moderate_content, llm=llm))
    graph.add_node("aggregate_results", aggregate_results)

    graph.add_edge(START, "check_sections")
    graph.add_conditional_edges("check_sections", _should_moderate)
    graph.add_edge("moderate_content", "aggregate_results")
    graph.add_edge("aggregate_results", END)

    return graph


def compile_graph(sections_config: SectionsConfig, llm: ChatOpenRouter):
    """Compile the validation graph into a runnable."""
    graph = build_graph(sections_config, llm)
    return graph.compile()
