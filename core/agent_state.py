from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolTrace:
    step: int
    tool_name: str
    arguments: dict
    result: Any
    error: str | None = None


@dataclass
class AgentState:
    task: str
    traces: list[ToolTrace] = field(default_factory=list)
    final_answer: str | None = None

    def add_trace(
        self,
        step: int,
        tool_name: str,
        arguments: dict,
        result: Any,
        error: str | None = None
    ):
        self.traces.append(
            ToolTrace(
                step=step,
                tool_name=tool_name,
                arguments=arguments,
                result=result,
                error=error
            )
        )