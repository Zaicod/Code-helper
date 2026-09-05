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

    