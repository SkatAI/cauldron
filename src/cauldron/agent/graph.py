from functools import partial
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from cauldron.agent.nodes.content_moderator import moderate_content
from cauldron.agent.nodes.quality_evaluator import evaluate_quality
from cauldron.agent.nodes.result_aggregator import aggregate_results
from cauldron.agent.state import ValidationState
from cauldron.llm.client import ChatOpenRouter


def _should_moderate(state: ValidationState) -> str:
    """Skip moderation if content is empty."""
    content = state.get("content", "")
    if not content or not content.strip():
        return "aggregate_results"
    return "moderate_content"


def build_graph(llm: ChatOpenRouter) -> StateGraph[ValidationState]:
    """Build the validation LangGraph workflow."""
    graph: StateGraph[ValidationState] = StateGraph(ValidationState)

    graph.add_node("evaluate_quality", partial(evaluate_quality, llm=llm))
    graph.add_node("moderate_content", partial(moderate_content, llm=llm))
    graph.add_node("aggregate_results", aggregate_results)

    graph.add_edge(START, "evaluate_quality")
    graph.add_conditional_edges("evaluate_quality", _should_moderate)
    graph.add_edge("moderate_content", "aggregate_results")
    graph.add_edge("aggregate_results", END)

    return graph


def compile_graph(llm: ChatOpenRouter) -> CompiledStateGraph[Any]:
    """Compile the validation graph into a runnable."""
    graph = build_graph(llm)
    return graph.compile()
