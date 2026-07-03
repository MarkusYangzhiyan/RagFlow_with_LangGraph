"""提供证据检索相关的测试替身。

Fake 不访问真实 RAGFlow，而是返回测试预设结果，
并记录节点向它发送的 RetrievalRequest。
"""

from dataclasses import dataclass, field

from bidguard.application.ports.evidence_retriever import (
    RetrievalRequest,
    RetrievalResult,
)


@dataclass(slots=True)
class FakeEvidenceRetriever:
    """返回预设检索结果，并记录收到的请求。"""

    result: RetrievalResult

    requests: list[RetrievalRequest] = field(
        default_factory=list,
        init=False,
    )

    async def retrieve(
        self,
        request: RetrievalRequest,
    ) -> RetrievalResult:
        """记录请求并返回测试预设结果。"""

        self.requests.append(request)

        return self.result