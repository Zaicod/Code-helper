from core.reviewer import review_project


def main():

    project_path = (
        "data/demo_project"
    )

    result = review_project(
        project_path
    )

    print("=" * 60)
    print("项目代码审查结果")
    print("=" * 60)

    print(
        f"Project: "
        f"{result['project_path']}"
    )

    print(
        f"Python Files: "
        f"{result['file_count']}"
    )

    print(
        f"Total Issues: "
        f"{result['total_issues']}"
    )

    print(
        f"Severity: "
        f"{result['severity_count']}"
    )

    print("\n文件详情")

    for file_result in result["files"]:

        review = file_result[
            "review_result"
        ]

        print("-" * 60)

        print(
            file_result[
                "file_path"
            ]
        )

        print(
            f"Issues: "
            f"{review['total']}"
        )


if __name__ == "__main__":
    main()