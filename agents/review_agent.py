import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from core.models import (
    ReviewIssue,
    LLMReviewIssue,
    LLMReviewResult,
)

from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
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
) -> LLMReviewResult | None:

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

    try:
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

    except AuthenticationError:
        print(
            "[LLM ERROR] Qwen API Key 无效或认证失败。"
        )
        return None

    except RateLimitError:
        print(
            "[LLM ERROR] Qwen API 请求过于频繁或额度受限。"
        )
        return None

    except APIConnectionError:
        print(
            "[LLM ERROR] 无法连接 Qwen API，请检查网络。"
        )
        return None

    except BadRequestError as e:
        print(
            f"[LLM ERROR] Qwen 请求失败：{e}"
        )
        return None

    except APIStatusError as e:
        print(
            f"[LLM ERROR] Qwen 服务返回异常状态："
            f"{e.status_code}"
        )
        return None

    except Exception as e:
        print(
            f"[LLM ERROR] 未知错误：{e}"
        )
        return None

    content = response.choices[0].message.content

    try:
        data = json.loads(content)

    except json.JSONDecodeError:
        print(
            "[LLM ERROR] Qwen 返回内容不是合法 JSON。"
        )
        return None

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