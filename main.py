from tools.code_reader import read_code
from tools.rule_checker import check_code_rules
from tools.style_checker import run_ruff
from tools.security_checker import run_bandit
from tools.complexity_checker import (
    analyze_complexity,
    complexity_to_issues
)


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

    print("=" * 60)
    print("统一代码审查结果")
    print("=" * 60)

    if not all_issues:
        print("未发现问题。")
        return

    for issue in all_issues:

        location = (
            f"Line {issue.line}"
            if issue.line is not None
            else "Unknown line"
        )

        print(
            f"[{issue.severity.upper()}] "
            f"{issue.source} | "
            f"{issue.category} | "
            f"{location}"
        )

        print(
            f"Rule: {issue.rule}"
        )

        print(
            f"Problem: {issue.message}"
        )

        if issue.suggestion:
            print(
                f"Suggestion: {issue.suggestion}"
            )

        print("-" * 60)


if __name__ == "__main__":
    main()