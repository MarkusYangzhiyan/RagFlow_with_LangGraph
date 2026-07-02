"""构建证据检索 LangGraph 子图。"""

from langchain.graph import END,START,StateGraph
from langgraph.graph.state import CompiledStateGraph

from bidguard.workflows.evidence_retrieval.state import (
    EvidenceRetrievalInput,
    EvidenceRetrievalState,
    RetrievalStatus
)
from bidguard.workflows.evidence_retrieval.nodes import initialize_state_node


EvidenceRetrievalGraph = CompiledStateGraph[
    EvidenceRetrievalState,
    None,
    EvidenceRetrievalInput,
    EvidenceRetrievalState,
]


def build_evidence_retrieval_graph() -> EvidenceRetrievalGraph:
    """创建并编译证据检索子图。"""

    builder = StateGraph(
        EvidenceRetrievalState,
        input_schema=EvidenceRetrievalInput,
        output_schema=EvidenceRetrievalState,
    )

    builder.add_node(
        "initialize_state_node",
        initialize_state_node,
    )

    builder.add_edge(
        START,
        "initialize_state_node",
    )

    builder.add_edge(
        "initialize_state_node",
        END,
    )

    return builder.compile(
        name="evidence-retrieval",
    )
