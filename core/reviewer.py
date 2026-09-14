from tools.code_reader import read_code
from tools.rule_checker import check_code_rules
from tools.style_checker import run_ruff
from tools.security_checker import run_bandit
from tools.complexity_checker import (
    analyze_complexity,
    complexity_to_issues
)

from core.aggregator import aggregate_issues

from tools.project_scanner import find_python_files

def review_file(file_path: str) -> dict:
    """
    对单个 Python 文件执行完整静态审查。
    """

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

    return {
        "file_path": file_path,
        "code": code,
        "review_result": review_result,
        "complexity": complexity_results
    }




def review_project(
    project_path: str
) -> dict:
    """
    审查整个 Python 项目。
    """

    files = find_python_files(
        project_path
    )

    file_results = []

    total_issues = 0

    severity_count = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0
    }

    for file_path in files:

        result = review_file(
            file_path
        )

        file_results.append(
            result
        )

        review_result = result[
            "review_result"
        ]

        total_issues += review_result[
            "total"
        ]

        counts = review_result[
            "severity_count"
        ]

        for severity in severity_count:

            severity_count[
                severity
            ] += counts.get(
                severity,
                0
            )

    return {
        "project_path": project_path,
        "file_count": len(files),
        "total_issues": total_issues,
        "severity_count": severity_count,
        "files": file_results
    }