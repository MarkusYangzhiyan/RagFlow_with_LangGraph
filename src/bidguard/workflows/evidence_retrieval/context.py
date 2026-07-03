"""定义证据检索子图的运行依赖。
State 是 Agent 的工作记录，Context 是 Agent 运行时携带的工具箱。"""

from dataclasses import dataclass

from bidguard.application.ports.evidence_retriever import EvidenceRetriever


@dataclass(
    frozen=True,
    slots=True          # 无法对该对象增加属性
)
class EvidenceRetrievalContext:
    """证据检索子图运行期间使用的外部依赖。"""

    retriever: EvidenceRetriever