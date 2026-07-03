import pytest
from langgraph.runtime import Runtime


from bidguard.application.ports.evidence_retriever import RetrievalResult
from bidguard.domain.models.evidence import EvidenceChunk,EvidenceSource
from bidguard.domain.enums.artifact_role import ArtifactRole
from bidguard.workflows.evidence_retrieval.state import EvidenceRetrievalState, RetrievalStatus
from bidguard.workflows.evidence_retrieval.context import EvidenceRetrievalContext
from bidguard.workflows.evidence_retrieval.nodes import (
    initialize_state_node,
    retrieve_evidence_node,
)
from tests.fakes.evidence_retriever import FakeEvidenceRetriever

#---------------------------------------------------------------------------------------
# test 1
#---------------------------------------------------------------------------------------
"""
测试最小输入是否被补齐
"""
def test_initialize_state_node_sets_default_and_normalizes_input() -> None:
    """
    最小输入应被清理，并补齐所有默认状态。
    """

    input_state: EvidenceRetrievalState = {
        "project_id": " PRJ-0001 ",
        "query_text": " 运维服务期限是什么？ ",
    }

    result = initialize_state_node(input_state)

    assert result == {
        "project_id": "PRJ-0001",
        "query_text": "运维服务期限是什么？",
        "artifact_roles": (),
        "document_ids": (),
        "top_k": 10,
        "minimum_score": 0.0,
        "max_attempts": 3,
        "active_query": "运维服务期限是什么？",
        "query_history": ("运维服务期限是什么？",),
        "evidence": (),
        "attempt_count": 0,
        "status": RetrievalStatus.PENDING,
        "requires_human_review": False,
        "error_message": None,
        "total_candidate": 0,
        "elapsed_ms": 0,
        "backend_request_id":None
    }

#---------------------------------------------------------------------------------------
# test 2
#---------------------------------------------------------------------------------------
"""
测试调用者输入是否被正确保存
"""
def test_initialize_state_preserves_optional_configuration() -> None:
    """调用者主动提供的检索配置应被保留。"""

    input_state: EvidenceRetrievalState = {
        "project_id": "PRJ-0001",
        "query_text": "查询运维服务期限",
        "artifact_roles": (
            ArtifactRole.TENDER_DOCUMENT,
            ArtifactRole.CORRECTION_NOTICE,
        ),
        "document_ids": ("DOC-0001", "DOC-0002"),
        "top_k": 5,
        "minimum_score": 0.6,
        "max_attempts": 2,
    }

    result = initialize_state_node(input_state)

    assert result["artifact_roles"] == (
        ArtifactRole.TENDER_DOCUMENT,
        ArtifactRole.CORRECTION_NOTICE,
    )
    assert result["document_ids"] == ("DOC-0001", "DOC-0002")
    assert result["top_k"] == 5
    assert result["minimum_score"] == 0.6
    assert result["max_attempts"] == 2

#---------------------------------------------------------------------------------------
# test 3 
#---------------------------------------------------------------------------------------
"""
使用多组不同的数据，重复执行同一个测试函数
测试project_id, query_text 为空的时候
"""
@pytest.mark.parametrize(
    ("project_id", "query_text", "expected_message"),
    [
        ("", "正常问题", "project_id 不能为空"),
        ("   ", "正常问题", "project_id 不能为空"),
        ("PRJ-0001", "", "query_text 不能为空"),
        ("PRJ-0001", "   ", "query_text 不能为空"),
    ],
)

def test_initialize_state_rejects_blank_required_fields(
    project_id: str,
    query_text: str,
    expected_message: str,
) -> None:
    """项目编号和查询内容不能为空或纯空格。"""

    input_state: EvidenceRetrievalState = {
        "project_id": project_id,
        "query_text": query_text,
    }

    with pytest.raises(ValueError, match=expected_message):
        initialize_state_node(input_state)

#---------------------------------------------------------------------------------------
# test 4 
#---------------------------------------------------------------------------------------
"""
测试top_k超出设置阈值
"""
@pytest.mark.parametrize("top_k", [0, 101])
def test_initialize_state_rejects_invalid_top_k(top_k: int) -> None:
    """top_k 必须处于允许范围内。"""

    input_state: EvidenceRetrievalState = {
        "project_id": "PRJ-0001",
        "query_text": "测试问题",
        "top_k": top_k,
    }

    with pytest.raises(ValueError, match="top_k 必须在 1 到 100 之间"):
        initialize_state_node(input_state)


#---------------------------------------------------------------------------------------
# test 5
#---------------------------------------------------------------------------------------
"""
测试最小分数是否在设置阈值中
"""
@pytest.mark.parametrize("minimum_score", [-0.1, 1.1])
def test_initialize_state_rejects_invalid_minimum_score(
    minimum_score: float,
) -> None:
    """最低相关性分数必须处于零到一之间。"""

    input_state: EvidenceRetrievalState = {
        "project_id": "PRJ-0001",
        "query_text": "测试问题",
        "minimum_score": minimum_score,
    }

    with pytest.raises(
        ValueError,
        match="minimum_score 必须在 0.0 到 1.0 之间",
    ):
        initialize_state_node(input_state)

#---------------------------------------------------------------------------------------
# test 6
#---------------------------------------------------------------------------------------
"""
测试检索次数
"""
@pytest.mark.parametrize("max_attempts", [0, 6])
def test_initialize_state_rejects_invalid_max_attempts(
    max_attempts: int,
) -> None:
    """最大检索次数必须处于允许范围内。"""

    input_state: EvidenceRetrievalState = {
        "project_id": "PRJ-0001",
        "query_text": "测试问题",
        "max_attempts": max_attempts,
    }

    with pytest.raises(
        ValueError,
        match="max_attempts 必须在 1 到 5 之间",
    ):
        initialize_state_node(input_state)


#---------------------------------------------------------------------------------------
# test 7
#---------------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_retrieve_evidence_node_calls_retriever_and_updates_state() -> None:
    """检索节点应调用 Retriever，并将检索结果写回 State。"""

    evidence = EvidenceChunk(
        content="投标人应提供三年运维服务。",
        relevance_score=0.92,
        rank=1,
        source=EvidenceSource(
            project_id="PRJ-0001",
            document_ids="DOC-0001",
            artifact_role=ArtifactRole.TENDER_DOCUMENT,
            page_number=12,
            section_path=("第三章", "技术要求"),
            chunk_id="chunk-001",
        ),
    )

    retrieval_result = RetrievalResult(
        evidence=(evidence,),
        total_candidates=8,
        elapsed_ms=25,
        backend_request_id="fake-request-001",
    )

    fake_retriever = FakeEvidenceRetriever(
        result=retrieval_result,
    )

    context = EvidenceRetrievalContext(
        retriever=fake_retriever,
    )

    runtime = Runtime(
        context=context,
    )

    input_state: EvidenceRetrievalState = {
        "project_id": "PRJ-0001",
        "query_text": "运维服务期限是什么？",
        "artifact_roles": (ArtifactRole.TENDER_DOCUMENT,),
        "document_ids": ("DOC-0001",),
        "top_k": 5,
        "minimum_score": 0.6,
    }

    initialized_state = initialize_state_node(input_state)

    result = await retrieve_evidence_node(
        initialized_state,
        runtime,
    )

    assert len(fake_retriever.requests) == 1

    received_request = fake_retriever.requests[0]

    assert received_request.project_id == "PRJ-0001"
    assert received_request.query_text == "运维服务期限是什么？"
    assert received_request.artifact_roles == (
        ArtifactRole.TENDER_DOCUMENT,
    )
    assert received_request.document_ids == ("DOC-0001",)
    assert received_request.top_k == 5
    assert received_request.minimum_score == 0.6

    assert result["evidence"] == (evidence,)
    assert result["attempt_count"] == 1
    assert result["status"] == RetrievalStatus.RETRIEVED
    assert result["total_candidates"] == 8
    assert result["elapsed_ms"] == 25
    assert result["backend_request_id"] == "fake-request-001"
    assert result["error_message"] is None