from collections import Counter
from core.models import ReviewIssue

SEVERITY_ORDER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "info": 0
}

def aggregate_issues(issues: list[ReviewIssue]) -> dict:
    """
    对代码审查问题进行：
    1. 去重
    2. 排序
    3. 统计
    """

    unique_issues = []

    seen = set()

    for issue in issues:

        key = (
            issue.source,
            issue.rule,
            issue.line,
            issue.message
        )

        if key not in seen:
            seen.add(key)
            unique_issues.append(issue)

    #按严重程度排序
    unique_issues.sort(
        key= lambda x:SEVERITY_ORDER.get(
            x.severity.lower(),
            0
        ),
        reverse=True
    )

    #统计严重程度
    severity_count = Counter(
        issue.severity.lower() for issue in unique_issues
    )

    return {
        "total": len(unique_issues),

        "severity_count": {
            "critical": severity_count.get("critical", 0),
            "high": severity_count.get("high", 0),
            "medium": severity_count.get("medium", 0),
            "low": severity_count.get("low", 0),
            "info": severity_count.get("info", 0),
        },

        "issues": unique_issues
    }