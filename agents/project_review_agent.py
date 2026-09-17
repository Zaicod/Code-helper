import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from core.models import (
    LLMReviewIssue,
    LLMReviewResult
)


load_dotenv()


# ============================================================
# 1. 初始化千问客户端
# ============================================================

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),

    base_url=os.getenv(
        "QWEN_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
)


# 明确指定千问 Coder 模型
MODEL = os.getenv(
    "QWEN_MODEL",
    "kimi-k2.7-code"
)


# ============================================================
# 2. 将项目静态分析结果整理成文本
# ============================================================

def build_project_summary(
    project_result: dict
) -> str:

    lines = []

    lines.append(
        f"项目路径: "
        f"{project_result['project_path']}"
    )

    lines.append(
        f"Python 文件数: "
        f"{project_result['file_count']}"
    )

    lines.append(
        f"问题总数: "
        f"{project_result['total_issues']}"
    )

    lines.append(
        f"严重程度统计: "
        f"{project_result['severity_count']}"
    )

    lines.append("")

    for file_result in project_result["files"]:

        review = file_result[
            "review_result"
        ]

        lines.append(
            f"文件: "
            f"{file_result['file_path']}"
        )

        lines.append(
            f"问题数量: "
            f"{review['total']}"
        )

        for issue in review["issues"]:

            lines.append(
                f"- [{issue.severity}] "
                f"{issue.category} | "
                f"{issue.rule} | "
                f"Line {issue.line} | "
                f"{issue.message}"
            )

        lines.append("")

    return "\n".join(lines)


# ============================================================
# 3. 调用千问进行项目级代码审查
# ============================================================

def review_project_with_llm(
    project_result: dict
) -> LLMReviewResult | None:

    project_summary = (
        build_project_summary(
            project_result
        )
    )

    system_prompt = """
你是通义千问驱动的资深 Python 代码审查专家。

你需要结合静态分析工具的结果，对整个 Python 项目进行综合代码审查。

静态分析工具包括：

- AST
- Ruff
- Bandit
- Radon

请重点分析：

1. Security
2. Correctness
3. Maintainability
4. Performance
5. Readability
6. 跨文件设计问题
7. 项目级风险

要求：

- 不要简单重复静态工具输出
- 优先总结项目级问题
- 可以发现静态工具遗漏的语义问题
- 可以发现跨文件依赖问题
- 不要虚构不存在的问题
- 建议必须明确、可执行
- severity 只能是：
  critical
  high
  medium
  low
  info

必须返回合法 JSON。
不要输出 Markdown。
不要输出 JSON 以外的内容。
"""

    user_prompt = f"""
以下是一个 Python 项目的静态代码审查结果：

{project_summary}

请对整个项目进行综合分析。

返回以下 JSON：

{{
    "overall_score": 0到100之间的整数,

    "summary": "项目整体代码质量总结",

    "issues": [
        {{
            "category": "security / correctness / maintainability / performance / readability",

            "severity": "critical / high / medium / low / info",

            "line": null,

            "problem": "项目存在的问题",

            "reason": "为什么这是一个问题",

            "suggestion": "具体如何修改"
        }}
    ]
}}
"""

    try:

        response = (
            client.chat.completions.create(
                model=MODEL,

                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],

                response_format={
                    "type": "json_object"
                }
            )
        )

    except Exception as e:

        print(
            f"[QWEN ERROR] "
            f"千问项目级审查失败：{e}"
        )

        return None


    # ========================================================
    # 4. 读取千问返回内容
    # ========================================================

    content = (
        response
        .choices[0]
        .message
        .content
    )


    # ========================================================
    # 5. JSON 解析
    # ========================================================

    try:

        data = json.loads(
            content
        )

    except json.JSONDecodeError:

        print(
            "[QWEN ERROR] "
            "千问返回内容不是合法 JSON。"
        )

        return None


    # ========================================================
    # 6. 转成项目内部数据模型
    # ========================================================

    issues = []

    for item in data.get(
        "issues",
        []
    ):

        issues.append(
            LLMReviewIssue(

                category=item[
                    "category"
                ],

                severity=item[
                    "severity"
                ],

                line=item.get(
                    "line"
                ),

                problem=item[
                    "problem"
                ],

                reason=item[
                    "reason"
                ],

                suggestion=item[
                    "suggestion"
                ]
            )
        )


    return LLMReviewResult(

        overall_score=data[
            "overall_score"
        ],

        summary=data[
            "summary"
        ],

        issues=issues
    )