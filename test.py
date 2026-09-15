from core.reviewer import review_project
from core.report_generator import generate_project_report


def main():

    project_path = "data/demo_project"

    # 项目审查
    project_result = review_project(
        project_path
    )

    # 输出终端摘要
    print("=" * 60)
    print("项目代码审查结果")
    print("=" * 60)

    print(
        f"Project: "
        f"{project_result['project_path']}"
    )

    print(
        f"Python Files: "
        f"{project_result['file_count']}"
    )

    print(
        f"Total Issues: "
        f"{project_result['total_issues']}"
    )

    print(
        f"Severity: "
        f"{project_result['severity_count']}"
    )

    # 生成报告
    generate_project_report(
        project_result,
        "outputs/project_review_report.md"
    )

    print("\n" + "=" * 60)
    print("项目审查报告已生成")
    print("=" * 60)

    print(
        "outputs/project_review_report.md"
    )


if __name__ == "__main__":
    main()