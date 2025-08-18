from langgraph.graph.state import CompiledStateGraph
from langgraph.graph.state import StateGraph

from dev_observer.analysis.code.nodes import AnalysisState
from dev_observer.analysis.code.nodes import CodeResearchNodes
from dev_observer.prompts.provider import PromptsProvider
from dev_observer.storage.provider import StorageProvider
from dev_observer.tokenizer.provider import TokenizerProvider


def create_code_research_graph(
        prompts: PromptsProvider,
        tokenizer: TokenizerProvider,
        storage: StorageProvider,
) -> CompiledStateGraph[AnalysisState, AnalysisState, AnalysisState]:
    nodes = CodeResearchNodes(prompts, tokenizer, storage)
    workflow = StateGraph(AnalysisState)
    workflow.add_node("analyze", nodes.analyze_node)
    workflow.set_entry_point("analyze")
    return workflow.compile()
