from tools.code_reader import read_code
from tools.rule_checker import check_code_rules
from tools.style_checker import run_ruff
from tools.security_checker import run_bandit
from tools.complexity_checker import (
    analyze_complexity,
    complexity_to_issues
)

from core.aggregator import aggregate_issues
from agents.review_agent import review_code_with_llm


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
    print("静态分析汇总")
    print("=" * 60)

    print(
        f"Total Issues: "
        f"{review_result['total']}"
    )

    llm_review = review_code_with_llm(
    code,
    review_result
    )

    print("\n" + "=" * 60)
    print("Qwen 综合代码审查")
    print("=" * 60)

    print(
        f"Overall Score: "
        f"{llm_review.overall_score}/100"
    )

    print("\nSummary:")

    print(
        llm_review.summary
    )

    print("\nLLM Findings:")

    if not llm_review.issues:
        print(
            "Qwen 未发现额外问题。"
        )

    for issue in llm_review.issues:

        print("-" * 60)

        print(
            f"[{issue.severity.upper()}] "
            f"{issue.category} | "
            f"Line {issue.line}"
        )

        print(
            f"Problem: {issue.problem}"
        )

        print(
            f"Reason: {issue.reason}"
        )

        print(
            f"Suggestion: {issue.suggestion}"
        )

if __name__ == "__main__":
    main()