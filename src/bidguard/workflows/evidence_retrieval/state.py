from enum import StrEnum
from typing import NotRequired, TypedDict

from bidguard.domain.enums.artifact_role import ArtifactRole
from bidguard.domain.models.evidence import EvidenceChunk

"""
证据检索子图state
"""

class RetrievalStatus(StrEnum):
    """证据检索 Agent 的运行状态。"""

    PENDING = "pending"             # 任务刚开始，尚未调用检索服务
    RETRIEVING = "retrieving"       # Agent正在调用ragflow检索证据
    SUFFICIENT = "sufficient"       # 当前证据已经足够支持后续分析
    INSUFFICIENT = "insufficient"   # 虽然检索到证据，但是证据不足
    FAILED = "failed"               # 检索流程执行失败
    HUMAN_REVIEW = "human_review"   # 需要人工介入


class EvidenceRetrievalInput(TypedDict):
    """调用证据检索 Agent 时允许输入的字段。"""

    project_id: str
    query_text: str 

    artifact_roles: NotRequired[tuple[ArtifactRole, ...]]       # NotRequired 可以缺失且不需要默认值
    document_ids: NotRequired[tuple[str, ...]]

    top_k: NotRequired[int]
    minimum_score: NotRequired[float]
    max_attempts: NotRequired[int]


class EvidenceRetrievalState(EvidenceRetrievalInput):   # 继承EvidenceRetrevalInput,拥有其所有字段
    """证据检索 Agent 在节点之间传递的完整状态。"""

    active_query: NotRequired[str]                      # 当前真正发送给ragflow查询的query
    query_history: NotRequired[tuple[str, ...]]         # 记录本次任务使用的所有查询
    evidence: NotRequired[tuple[EvidenceChunk, ...]]    # 当前检索到的证据片段
    attempt_count: NotRequired[int]                     # 记录检索次数
    status: NotRequired[RetrievalStatus]                # 当前检索流程状态
    requires_human_review: NotRequired[bool]            # 是否需要人工介入
    error_message: NotRequired[str | None]              # 保存错误信息