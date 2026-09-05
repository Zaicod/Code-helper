import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from core.models import (
    ReviewIssue,
    LLMReviewIssue,
    LLMReviewResult,
)


load_dotenv()


client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv(
        "QWEN_BASE_URL",
        "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
)


MODEL = os.getenv(
    "QWEN_MODEL",
    "qwen3-coder-plus"
)


def format_issues(
    issues: list[ReviewIssue]
) -> str:

    if not issues:
        return "静态分析工具未发现明显问题。"

    lines = []

    for i, issue in enumerate(issues, 1):

        lines.append(
            f"""
问题 {i}
来源: {issue.source}
类别: {issue.category}
规则: {issue.rule}
严重程度: {issue.severity}
行号: {issue.line}
描述: {issue.message}
建议: {issue.suggestion or "无"}
""".strip()
        )

    return "\n\n".join(lines)


def review_code_with_llm(
    code: str,
    review_result: dict
) -> LLMReviewResult:

    issues_text = format_issues(
        review_result["issues"]
    )

    system_prompt = """
你是一名资深 Python 代码审查工程师。

你需要结合源代码以及静态分析工具结果完成代码审查。

重点分析：

- Correctness
- Security
- Maintainability
- Performance
- Readability

要求：

1. 不要简单复制静态分析工具结果。
2. 可以补充静态分析工具遗漏的语义问题。
3. 不要虚构不存在的问题。
4. 给出明确、可操作的修复建议。
5. 严重程度只能是：
   critical
   high
   medium
   low
   info

请严格返回 JSON 格式。
不要输出 Markdown。
不要输出 ```json。
不要输出 JSON 之外的任何文字。
"""

    user_prompt = f"""
请审查下面的 Python 代码。

代码：

{code}

静态分析结果：

总问题数量：
{review_result["total"]}

严重程度统计：
{review_result["severity_count"]}

具体问题：

{issues_text}

请输出以下 JSON 结构：

{{
    "overall_score": 0到100之间的整数,
    "summary": "总体代码审查总结",
    "issues": [
        {{
            "category": "security / correctness / maintainability / performance / readability",
            "severity": "critical / high / medium / low / info",
            "line": 行号，如果无法确定则为 null,
            "problem": "具体问题",
            "reason": "为什么这是一个问题",
            "suggestion": "如何修改"
        }}
    ]
}}
"""

    response = client.chat.completions.create(
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

    content = response.choices[0].message.content

    data = json.loads(content)

    issues = []

    for item in data.get("issues", []):

        issues.append(
            LLMReviewIssue(
                category=item["category"],
                severity=item["severity"],
                line=item.get("line"),
                problem=item["problem"],
                reason=item["reason"],
                suggestion=item["suggestion"]
            )
        )

    return LLMReviewResult(
        overall_score=data["overall_score"],
        summary=data["summary"],
        issues=issues
    )