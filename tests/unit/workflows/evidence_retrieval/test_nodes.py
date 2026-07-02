import pytest

from bidguard.domain.enums.artifact_role import ArtifactRole
from bidguard.workflows.evidence_retrieval.nodes import initialize_state_node
from bidguard.workflows.evidence_retrieval.state import EvidenceRetrievalState, RetrievalStatus

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