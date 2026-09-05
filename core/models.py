from dataclasses import dataclass
from typing import Optional

@dataclass
class ReviewIssue:
    source: str
    category: str
    rule: str
    severity: str
    line: Optional[int]
    column: Optional[int]
    message: str
    suggestion: Optional[str] = None

@dataclass
class LLMReviewIssue:
    category: str
    severity: str
    line: Optional[int]
    problem: str
    reason: str
    suggestion: str


@dataclass
class LLMReviewResult:
    overall_score: int
    summary: str
    issues: list[LLMReviewIssue]

    