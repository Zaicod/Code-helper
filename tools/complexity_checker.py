from radon.complexity import cc_visit
from core.models import ReviewIssue

def analyze_complexity(code: str) -> list:
    """
    使用 Radon 分析 Python 代码的圈复杂度。

    Parameters
    ----------
    code : str
        Python 源代码。

    Returns
    -------
    list
        每个函数/方法的复杂度分析结果。
    """
    results = cc_visit(code)

    complexity_results = []

    for item in results:
        complexity_results.append({
            "name": item.name,
            "type": item.letter,
            "line": item.lineno,
            "complexity": item.complexity
        })

    return complexity_results

def complexity_to_issues(results: list) -> list[ReviewIssue]:
    
    issues = []

    for item in results:

        complexity = item["complexity"]

        if complexity >= 15:
            severity = "high"

        elif complexity >= 10:
            severity = "medium"

        else:
            continue

        issues.append(
            ReviewIssue(
                source="radon",
                category="maintainability",
                rule="high-complexity",
                severity=severity,
                line=item["line"],
                column=None,
                message=(
                    f"函数 {item['name']} 的圈复杂度为 "
                    f"{complexity}，等级为 {item['rank']}。"
                ),
                suggestion="建议拆分函数、减少嵌套和条件分支。"
            )
        )
    return issues