"""定义证据检索能力的应用层接口。"""

from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from bidguard.domain.enums.artifact_role import ArtifactRole
from bidguard.domain.models.evidence import EvidenceChunk


class RetrievalRequest(BaseModel):
    """LangGraph 节点向检索服务发起的标准请求。"""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    project_id: str = Field(min_length=1)
    query_text: str = Field(min_length=1)

    # 一次检索允许查询多种角色文档，且检索请求创建后不可被任意修改
    artifact_roles: tuple[ArtifactRole, ...] = ()
    document_ids: tuple[str, ...] = ()

    top_k: int = Field(default=10, ge=1, le=100)
    minimum_score: float = Field(default=0.0, ge=0.0, le=1.0)


class RetrievalResult(BaseModel):
    """检索服务返回给 LangGraph 节点的标准结果。"""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    evidence: tuple[EvidenceChunk, ...] = ()
    total_candidates: int = Field(ge=0)

    # 本次检索耗时 ms:millisecond = 毫秒
    elapsed_ms: int = Field(ge=0)

    # 后端检索服务为本次请求分配的唯一编号
    backend_request_id: str | None = None


# 协议或者接口类
"""
一个对象如果想成为“证据检索器”，必须提供什么方法。
方法名称：retrieve
必须异步：async
输入：RetrievalRequest
输出：RetrievalResult
"""


class EvidenceRetriever(Protocol):
    """所有证据检索实现都必须满足的接口。"""

    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResult:
        """根据标准请求检索证据。"""
        ...
