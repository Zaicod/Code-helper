import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from core.agent_state import AgentState
from tools.code_reader import read_code
from tools.style_checker import run_ruff
from tools.security_checker import run_bandit
from tools.complexity_checker import analyze_complexity
from tools.rule_checker import check_code_rules


# ============================================================
# 1. 环境配置
# ============================================================

env_path = (
    Path(__file__).resolve().parent.parent
    / ".env"
)

load_dotenv(env_path)


API_KEY = os.getenv(
    "LLM_API_KEY"
)

BASE_URL = os.getenv(
    "QWEN_BASE_URL",
    "https://dashscope.aliyuncs.com/compatible-mode/v1"
)

MODEL = os.getenv(
    "QWEN_MODEL",
    "qwen3.7-flash"
)


if not API_KEY:
    raise RuntimeError(
        "未读取到 DASHSCOPE_API_KEY"
    )


client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_code",
            "description": (
                "读取指定 Python 文件的源代码。"
                "当需要查看代码内容时使用。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Python 文件路径"
                    }
                },
                "required": [
                    "file_path"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "run_ruff",
            "description": (
                "使用 Ruff 检查 Python 代码的"
                "代码质量、风格和常见错误。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Python 文件路径"
                    }
                },
                "required": [
                    "file_path"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "run_bandit",
            "description": (
                "使用 Bandit 对 Python 文件"
                "进行安全漏洞扫描。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Python 文件路径"
                    }
                },
                "required": [
                    "file_path"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "analyze_complexity",
            "description": (
                "使用 Radon 分析 Python 代码"
                "的圈复杂度和可维护性风险。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Python 文件路径"
                    }
                },
                "required": [
                    "file_path"
                ]
            }
        }
    }
]



def execute_tool(
    tool_name: str,
    arguments: dict
):
    """
    根据 Qwen 返回的工具名，
    调用真正的 Python 工具。
    """

    if tool_name == "read_code":

        return read_code(
            arguments["file_path"]
        )

    elif tool_name == "run_ruff":

        issues = run_ruff(
            arguments["file_path"]
        )

        return [
            {
                "source": issue.source,
                "category": issue.category,
                "rule": issue.rule,
                "severity": issue.severity,
                "line": issue.line,
                "message": issue.message
            }
            for issue in issues
        ]

    elif tool_name == "run_bandit":

        issues = run_bandit(
            arguments["file_path"]
        )

        return [
            {
                "source": issue.source,
                "category": issue.category,
                "rule": issue.rule,
                "severity": issue.severity,
                "line": issue.line,
                "message": issue.message
            }
            for issue in issues
        ]

    elif tool_name == "analyze_complexity":

        code = read_code(
            arguments["file_path"]
        )

        return analyze_complexity(
            code
        )

    else:

        raise ValueError(
            f"未知工具: {tool_name}"
        )



def run_code_review_agent(
    user_task: str,
    max_steps: int = 8
) -> AgentState:

    state = AgentState(task=user_task)
    """
    Qwen Tool-Calling Agent。
    """

    messages = [
        {
            "role": "system",
            "content": """
你是一名资深 Python Code Review Agent。

你可以根据用户任务自主选择代码分析工具。

你的目标是：
1. 理解用户要求。
2. 根据需要调用工具。
3. 分析工具返回结果。
4. 必要时继续调用其他工具。
5. 最终给出综合代码审查结论。

原则：
- 不要无意义地调用所有工具。
- 根据用户问题选择必要工具。
- 安全问题优先考虑 Bandit。
- 代码质量问题优先考虑 Ruff。
- 复杂度和可维护性问题使用复杂度分析。
- 如果不知道代码内容，可以先读取代码。
- 不要虚构工具没有发现的问题。
"""
        },

        {
            "role": "user",
            "content": user_task
        }
    ]

    for step in range(max_steps):

        response = (
            client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto"
            )
        )

        message = (
            response
            .choices[0]
            .message
        )

        # 把 assistant 消息放进历史
        messages.append(
            message.model_dump(
                exclude_none=True
            )
        )

        tool_calls = (
            message.tool_calls
        )

        # ============================================
        # 没有 Tool Call
        # → Agent 认为任务完成
        # ============================================

        if not tool_calls:

            state.final_answer = (
                message.content
                or "Agent 未返回结果。"
            )

            return state

        # ============================================
        # 执行所有 Tool Call
        # ============================================

        for tool_call in tool_calls:

            tool_name = (
                tool_call
                .function
                .name
            )

            arguments = json.loads(
                tool_call
                .function
                .arguments
            )

            print(
                f"[Agent] 调用工具: "
                f"{tool_name}"
            )

            print(
                f"[Agent] 参数: "
                f"{arguments}"
            )

            try:

                tool_result = execute_tool(
                    tool_name,
                    arguments
                )

                state.add_trace(
                    step=step + 1,
                    tool_name=tool_name,
                    arguments=arguments,
                    result=tool_result
                )

            except Exception as e:

                tool_result = {
                    "error": str(e)
                }
                state.add_trace(
                    step=step + 1,
                    tool_name=tool_name,
                    arguments=arguments,
                    result=None,
                    error=str(e)
                )

            # 工具结果反馈给模型
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": (
                        tool_call.id
                    ),
                    "content": json.dumps(
                        tool_result,
                        ensure_ascii=False,
                        default=str
                    )
                }
            )

    state.final_answer = (
            "Agent 达到最大工具调用步骤，"
            "未能在限制内完成任务。"
        )

    return state