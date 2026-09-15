from pathlib import Path


def generate_project_report(
    project_result: dict,
    output_path: str = "outputs/project_review_report.md"
) -> str:
    """
    根据项目级审查结果生成 Markdown 报告。
    """

    lines = []

    lines.append("# Project Code Review Report")
    lines.append("")

    # =========================
    # 1. 项目概览
    # =========================

    lines.append("## 1. Project Overview")
    lines.append("")

    lines.append(
        f"- Project path: `{project_result['project_path']}`"
    )

    lines.append(
        f"- Python files: {project_result['file_count']}"
    )

    lines.append(
        f"- Total issues: {project_result['total_issues']}"
    )

    lines.append("")

    # =========================
    # 2. 严重程度统计
    # =========================

    lines.append("## 2. Severity Summary")
    lines.append("")

    counts = project_result["severity_count"]

    lines.append("| Severity | Count |")
    lines.append("|---|---:|")

    lines.append(
        f"| Critical | {counts['critical']} |"
    )

    lines.append(
        f"| High | {counts['high']} |"
    )

    lines.append(
        f"| Medium | {counts['medium']} |"
    )

    lines.append(
        f"| Low | {counts['low']} |"
    )

    lines.append(
        f"| Info | {counts['info']} |"
    )

    lines.append("")

    # =========================
    # 3. 文件问题统计
    # =========================

    lines.append("## 3. File Risk Summary")
    lines.append("")

    lines.append(
        "| File | Issues | Critical | High | Medium | Low |"
    )

    lines.append(
        "|---|---:|---:|---:|---:|---:|"
    )

    file_results = project_result["files"]

    # 按问题数量从高到低排序
    sorted_files = sorted(
        file_results,
        key=lambda x: x["review_result"]["total"],
        reverse=True
    )

    for file_result in sorted_files:

        review = file_result["review_result"]

        file_counts = review["severity_count"]

        lines.append(
            f"| `{file_result['file_path']}` "
            f"| {review['total']} "
            f"| {file_counts['critical']} "
            f"| {file_counts['high']} "
            f"| {file_counts['medium']} "
            f"| {file_counts['low']} |"
        )

    lines.append("")

    # =========================
    # 4. 文件详细结果
    # =========================

    lines.append("## 4. File Review Details")
    lines.append("")

    for file_index, file_result in enumerate(
        sorted_files,
        1
    ):

        file_path = file_result["file_path"]

        review = file_result["review_result"]

        lines.append(
            f"### 4.{file_index} `{file_path}`"
        )

        lines.append("")

        lines.append(
            f"- Total issues: {review['total']}"
        )

        lines.append("")

        issues = review["issues"]

        if not issues:
            lines.append(
                "No issues were found in this file."
            )
            lines.append("")
            continue

        for issue_index, issue in enumerate(
            issues,
            1
        ):

            lines.append(
                f"#### Issue {issue_index} "
                f"[{issue.severity.upper()}] "
                f"{issue.rule}"
            )

            lines.append("")

            lines.append(
                f"- Source: `{issue.source}`"
            )

            lines.append(
                f"- Category: `{issue.category}`"
            )

            lines.append(
                f"- Line: "
                f"{issue.line if issue.line is not None else 'Unknown'}"
            )

            if issue.column is not None:
                lines.append(
                    f"- Column: {issue.column}"
                )

            lines.append(
                f"- Problem: {issue.message}"
            )

            if issue.suggestion:
                lines.append(
                    f"- Suggestion: {issue.suggestion}"
                )

            lines.append("")

    # =========================
    # 5. 结论
    # =========================

    lines.append("## 5. Review Conclusion")
    lines.append("")

    lines.append(
        f"The project contains "
        f"{project_result['file_count']} Python files "
        f"and {project_result['total_issues']} detected issues."
    )

    lines.append("")

    report = "\n".join(lines)

    output = Path(output_path)

    output.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output.write_text(
        report,
        encoding="utf-8"
    )

    return report