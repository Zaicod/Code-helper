from tools.code_reader import read_code
from tools.rule_checker import check_code_rules
from tools.style_checker import run_ruff
from tools.security_checker import run_bandit
from tools.complexity_checker import (
    analyze_complexity,
    complexity_to_issues
)

from core.aggregator import aggregate_issues


def main():

    file_path = "data/sample_code.py"

    code = read_code(file_path)

    ast_issues = check_code_rules(code)
    ruff_issues = run_ruff(file_path)
    bandit_issues = run_bandit(file_path)

    complexity_results = analyze_complexity(code)

    complexity_issues = complexity_to_issues(
        complexity_results
    )

    all_issues = (
        ast_issues
        + ruff_issues
        + bandit_issues
        + complexity_issues
    )

    review_result = aggregate_issues(
        all_issues
    )

    print("=" * 60)
    print("代码审查汇总")
    print("=" * 60)

    print(
        f"Total Issues: "
        f"{review_result['total']}"
    )

    counts = review_result[
        "severity_count"
    ]

    print(
        f"Critical: {counts['critical']} | "
        f"High: {counts['high']} | "
        f"Medium: {counts['medium']} | "
        f"Low: {counts['low']} | "
        f"Info: {counts['info']}"
    )

    print("\n" + "=" * 60)
    print("问题详情")
    print("=" * 60)

    for issue in review_result["issues"]:

        print(
            f"[{issue.severity.upper()}] "
            f"{issue.source} | "
            f"{issue.category} | "
            f"Line {issue.line}"
        )

        print(
            f"Rule: {issue.rule}"
        )

        print(
            f"Problem: {issue.message}"
        )

        if issue.suggestion:
            print(
                f"Suggestion: "
                f"{issue.suggestion}"
            )

        print("-" * 60)


if __name__ == "__main__":
    main()