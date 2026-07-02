"""定义招投标项目中不同文档的业务角色。

枚举成员使用大写名称供 Python 代码调用；
对应的小写字符串用于 CSV、JSON、数据库和接口传输。
"""

from enum import StrEnum


class ArtifactRole(StrEnum):
    """招投标项目中的文档业务角色。"""

    TENDER_NOTICE = "tender_notice"  # 招标公告或采购公告
    TENDER_DOCUMENT = "tender_document"  # 正式招标文件或采购文件
    TECHNICAL_ATTACHMENT = "technical_attachment"  # 技术参数、需求清单等附件
    CORRECTION_NOTICE = "correction_notice"  # 更正公告、澄清文件或补充公告
    AWARD_NOTICE = "award_notice"  # 中标公告或成交公告
    AWARD_ATTACHMENT = "award_attachment"  # 中标结果相关附件
    TEMPLATE = "template"  # 招标方提供的响应格式、表格或文件模板
    SYNTHETIC_RESPONSE = "synthetic_response"  # 为开发和测试人工构造的投标响应