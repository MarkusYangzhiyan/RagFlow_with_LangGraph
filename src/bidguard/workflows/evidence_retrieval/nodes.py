from langgraph.runtime import Runtime

from bidguard.application.ports.evidence_retriever import RetrievalRequest
from bidguard.workflows.evidence_retrieval.context import EvidenceRetrievalContext
from bidguard.workflows.evidence_retrieval.state import (
    EvidenceRetrievalState,
    RetrievalStatus,
)


def initialize_state_node(state: EvidenceRetrievalState) -> EvidenceRetrievalState:
    """
    验证检索输入，并初始化证据检索子图状态。
    """

    project_id = state["project_id"].strip()
    query_text = state["query_text"].strip()

    if not project_id:
        raise ValueError("project_id 不能为空")

    if not query_text:
        raise ValueError("query_text 不能为空")

    top_k = state.get("top_k", 10)
    minimum_score = state.get("minimum_score", 0.0)
    max_attempts = state.get("max_attempts", 3)

    if not 1 <= top_k <= 100:
        raise ValueError("top_k 必须在 1 到 100 之间")

    if not 0.0 <= minimum_score <= 1.0:
        raise ValueError("minimum_score 必须在 0.0 到 1.0 之间")

    if not 1 <= max_attempts <= 5:
        raise ValueError("max_attempts 必须在 1 到 5 之间")

    return {
        "project_id": project_id,
        "query_text": query_text,
        "artifact_roles": state.get("artifact_roles", ()),
        "document_ids": state.get("document_ids", ()),
        "top_k": top_k,
        "minimum_score": minimum_score,
        "max_attempts": max_attempts,
        "active_query": query_text,
        "query_history": (query_text,),
        "evidence": (),
        "attempt_count": 0,
        "status": RetrievalStatus.PENDING,
        "requires_human_review": False,
        "error_message": None,
        "total_candidate": 0,
        "elapsed_ms" : 0,
        "backend_request_id": None,
    }


async def retrieve_evidence_node(
    state: EvidenceRetrievalState,
    runtime: Runtime[EvidenceRetrievalContext],
) -> EvidenceRetrievalState:
    """调用证据检索接口，并将标准检索结果写回 State。"""

    request = RetrievalRequest(
        project_id=state["project_id"],
        query_text=state["active_query"],
        artifact_roles=state["artifact_roles"],
        document_ids=state["document_ids"],
        top_k=state["top_k"],
        minimum_score=state["minimum_score"],
    )

    result = await runtime.context.retriever.retrieve(request)

    return {
        **state,
        "evidence": result.evidence,
        "attempt_count": state["attempt_count"] + 1,
        "status": RetrievalStatus.RETRIEVED,
        "total_candidates": result.total_candidates,
        "elapsed_ms": result.elapsed_ms,
        "backend_request_id": result.backend_request_id,
        "error_message": None,
    }