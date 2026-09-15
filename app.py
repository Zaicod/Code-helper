import streamlit as st
import pandas as pd

from core.reviewer import review_project
from core.report_generator import generate_project_report

st.set_page_config(
    page_title="智能代码审查助手",
    page_icon="🔍",
    layout="wide"
)


st.title("智能代码审查助手")

st.write(
    "基于 AST、Ruff、Bandit、Radon 和大语言模型的代码审查系统"
)


project_path = st.text_input(
    "请输入 Python 项目路径",
    value="data/demo_project"
)


if st.button("开始审查"):

    if not project_path.strip():

        st.error(
            "请输入项目路径。"
        )

    else:

        try:

            with st.spinner(
                "正在分析项目代码..."
            ):

                result = review_project(
                    project_path
                )

            st.success(
                "代码审查完成！"
            )

            st.subheader(
                "项目概览"
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric(
                    "Python 文件",
                    result["file_count"]
                )

            with col2:

                st.metric(
                    "问题总数",
                    result["total_issues"]
                )

            with col3:

                high_risk = (
                    result["severity_count"]["critical"]
                    + result["severity_count"]["high"]
                )

                st.metric(
                    "高风险问题",
                    high_risk
                )

            with col4:

                if result["file_count"] > 0:

                    average_issues = (
                        result["total_issues"]
                        / result["file_count"]
                    )

                else:
                    average_issues = 0

                st.metric(
                    "平均问题/文件",
                    f"{average_issues:.1f}"
                )


            st.subheader("严重程度分布")

            severity_count = result["severity_count"]

            severity_df = pd.DataFrame({
                "Severity": [
                    "Critical",
                    "High",
                    "Medium",
                    "Low",
                    "Info"
                ],
                "Count": [
                    severity_count["critical"],
                    severity_count["high"],
                    severity_count["medium"],
                    severity_count["low"],
                    severity_count["info"]
                ]
            })

            st.bar_chart(
                severity_df,
                x="Severity",
                y="Count"
            )

            st.subheader("文件风险排名")

            file_data = []

            for file_result in result["files"]:

                review = file_result["review_result"]

                file_data.append({
                    "File": file_result["file_path"],
                    "Issues": review["total"]
                })


            file_df = pd.DataFrame(
                file_data
            )

            file_df = file_df.sort_values(
                by="Issues",
                ascending=False
            )

            st.bar_chart(
                file_df,
                x="File",
                y="Issues"
            )

            st.subheader("问题类别分布")

            category_count = {}

            for file_result in result["files"]:

                review = file_result["review_result"]

                for issue in review["issues"]:

                    category = issue.category

                    category_count[category] = (
                        category_count.get(category, 0)
                        + 1
                    )


            category_df = pd.DataFrame(
                [
                    {
                        "Category": category,
                        "Count": count
                    }
                    for category, count
                    in category_count.items()
                ]
            )


            if not category_df.empty:

                category_df = category_df.sort_values(
                    by="Count",
                    ascending=False
                )

                st.bar_chart(
                    category_df,
                    x="Category",
                    y="Count"
                )

            else:

                st.info(
                    "暂无问题类别数据。"
                )

            st.subheader("问题筛选")

            all_severities = [
                "critical",
                "high",
                "medium",
                "low",
                "info"
            ]

            selected_severities = st.multiselect(
                "选择严重程度",
                options=all_severities,
                default=all_severities
            )

            all_categories = set()

            for file_result in result["files"]:
                for issue in file_result["review_result"]["issues"]:
                    all_categories.add(issue.category)

            all_categories = sorted(all_categories)

            selected_categories = st.multiselect(
                "选择问题类别",
                options=all_categories,
                default=all_categories
            )


            st.subheader(
                "文件审查结果"
            )

            for file_result in result["files"]:

                review = file_result["review_result"]

                filtered_issues = []

                for issue in review["issues"]:

                    severity_match = (
                        issue.severity.lower()
                        in selected_severities
                    )

                    category_match = (
                        issue.category
                        in selected_categories
                    )

                    if severity_match and category_match:
                        filtered_issues.append(issue)

                if not filtered_issues:
                    continue

                with st.expander(
                    f"{file_result['file_path']} "
                    f"({len(filtered_issues)} 个匹配问题)"
                ):

                    for issue in filtered_issues:

                        st.markdown(
                            f"""
                                **[{issue.severity.upper()}]**
                                `{issue.rule}`

                                - 来源：`{issue.source}`
                                - 类别：`{issue.category}`
                                - 行号：{issue.line}
                                - 问题：{issue.message}
                             """
                        )

                        if issue.suggestion:
                            st.markdown(
                                f"- 建议：{issue.suggestion}"
                            )

                        st.divider()

            report_text = generate_project_report(
                result,
                "outputs/project_review_report.md"
            )
            st.download_button(
                label="下载 Markdown 审查报告",
                data=report_text,
                file_name="project_review_report.md",
                mime="text/markdown"
            )


        except Exception as e:

            st.error(
                f"代码审查失败：{e}"
            )