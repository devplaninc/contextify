from langgraph.graph.state import CompiledStateGraph
from langgraph.graph.state import StateGraph

from dev_observer.analysis.code.nodes import AnalysisState
from dev_observer.analysis.code.nodes import CodeResearchNodes
from dev_observer.prompts.provider import PromptsProvider


def create_code_research_graph(
        prompts: PromptsProvider,
) -> CompiledStateGraph[AnalysisState, AnalysisState, AnalysisState]:
    nodes = CodeResearchNodes(prompts)
    workflow = StateGraph(AnalysisState)
    workflow.add_node("analyze", nodes.analyze_node)
    workflow.set_entry_point("analyze")
    return workflow.compile()
