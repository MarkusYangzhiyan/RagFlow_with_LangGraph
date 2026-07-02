from pydantic import BaseModel, ConfigDict, Field

from bidguard.domain.enums.artifact_role import ArtifactRole

"""
定义 Pydantic 数据模型类
最终一条完整证据的数据结构类似：
{
  "content": "投标人应提供三年运维服务。",
  "relevance_score": 0.92,
  "rank": 1,
  "source": {
    "project_id": "PRJ-0001",
    "document_id": "DOC-0001",
    "document_version": null,
    "artifact_role": "tender_document",
    "page_number": 12,
    "section_path": [
      "第三章",
      "技术要求"
    ],
    "chunk_id": "chunk-001"
  }
}
"""



class EvidenceSource(BaseModel):
    """证据来源数据模型类：
    证据在原始文档中的可追溯来源。这条证据来自哪个项目、哪个文档、哪一页、哪个 Chunk？"""

    ## 定义整个模型的配置
    model_config = ConfigDict(
        extra = 'forbid',       # 禁止传入模型中没有定义的字段
        frozen = True           # 模型创建完成后,禁止重新修改字段
    )

    ## 数据模型字段设置(7个)
    project_id: str = Field(min_length=1)       # Field添加字段约束：字符串长度至少为 1
    document_id: str = Field(min_length=1)
    document_version: str | None = None         
    artifact_role: ArtifactRole

    page_number: int | None = Field(
        default=None,
        ge=1,
    )

    section_path: tuple[str, ...] = ()
    chunk_id: str = Field(min_length=1)


class EvidenceChunk(BaseModel):
    """证据片段数据模型类：
    经过检索和重排后返回给 Agent 的标准证据片段。
    Agent 检索到了什么内容、相关性是多少、排名第几、来自哪里？"""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    ## 4个字段
    content: str = Field(min_length=1)

    ### ragflow检索分数
    relevance_score: float = Field(
        ge=0.0,                 # greater than or equal, 即 >= 0
        le=1.0,                 # less than or equal, 即 <= 1
    )

    rank: int = Field(ge=1)     # 检索排名
    source: EvidenceSource      