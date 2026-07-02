"""构建证据检索 LangGraph 子图。"""

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from bidguard.workflows.evidence_retrieval.nodes import initialize_state_node
from bidguard.workflows.evidence_retrieval.state import (
    EvidenceRetrievalInput,
    EvidenceRetrievalState,
)

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



# if __name__ == "__main__":
#     graph = build_evidence_retrieval_graph()
#     result = graph.invoke(
#         {"project_id":"PRJ-001",
#          "query_text":"运维服务期限是什么？"}
#     )
#     print(result)