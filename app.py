import streamlit as st
import pandas as pd

from core.reviewer import review_project
from core.report_generator import generate_project_report
from core.source_utils import get_code_snippet
from agents.project_review_agent import review_project_with_llm


# ============================================================
# 1. 页面配置
# ============================================================

st.set_page_config(
    page_title="智能代码审查助手",
    page_icon="🔍",
    layout="wide"
)


# ============================================================
# 2. Session State 初始化
# ============================================================

# 保存静态代码审查结果
if "review_result" not in st.session_state:
    st.session_state.review_result = None

# 保存 Qwen AI 审查结果
if "llm_review" not in st.session_state:
    st.session_state.llm_review = None

# 保存当前已经审查的项目路径
if "reviewed_project_path" not in st.session_state:
    st.session_state.reviewed_project_path = None


# ============================================================
# 3. 页面标题
# ============================================================

st.title("🔍 智能代码审查助手")

st.write(
    "基于 AST、Ruff、Bandit、Radon 和 Qwen "
    "大语言模型的智能代码审查系统"
)

st.divider()


# ============================================================
# 4. 项目路径输入
# ============================================================

project_path = st.text_input(
    "请输入 Python 项目路径",
    value="data/demo_project",
    help="请输入包含 Python 源代码的项目目录"
)


# ============================================================
# 5. 开始代码审查
# ============================================================

if st.button(
    "开始审查",
    type="primary"
):

    if not project_path.strip():

        st.error(
            "请输入有效的项目路径。"
        )

    else:

        try:

            with st.spinner(
                "正在分析项目代码，请稍候..."
            ):

                result = review_project(
                    project_path
                )

            # 保存审查结果
            st.session_state.review_result = result

            # 保存当前项目路径
            st.session_state.reviewed_project_path = (
                project_path
            )

            # 新项目重新分析后清除旧 AI 结果
            st.session_state.llm_review = None

            st.success(
                "代码审查完成！"
            )

        except Exception as e:

            st.error(
                f"代码审查失败：{e}"
            )


# ============================================================
# 6. 获取 Session 中的审查结果
# ============================================================

result = st.session_state.review_result


# ============================================================
# 7. 如果已经完成审查，则展示 Dashboard
# ============================================================

if result is not None:

    st.divider()

    # ========================================================
    # 项目概览
    # ========================================================

    st.header("项目审查 Dashboard")

    st.caption(
        f"当前项目："
        f"{st.session_state.reviewed_project_path}"
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
            "平均问题 / 文件",
            f"{average_issues:.1f}"
        )


    # ========================================================
    # 8. 严重程度分布
    # ========================================================

    st.subheader("严重程度分布")

    severity_count = result[
        "severity_count"
    ]

    severity_df = pd.DataFrame(
        {
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
        }
    )

    st.bar_chart(
        severity_df,
        x="Severity",
        y="Count"
    )


    # ========================================================
    # 9. 文件风险排名
    # ========================================================

    st.subheader("文件风险排名")

    file_data = []

    for file_result in result["files"]:

        review = file_result[
            "review_result"
        ]

        file_data.append(
            {
                "File": file_result[
                    "file_path"
                ],
                "Issues": review[
                    "total"
                ]
            }
        )

    file_df = pd.DataFrame(
        file_data
    )

    if not file_df.empty:

        file_df = file_df.sort_values(
            by="Issues",
            ascending=False
        )

        st.bar_chart(
            file_df,
            x="File",
            y="Issues"
        )

    else:

        st.info(
            "项目中未发现 Python 文件。"
        )


    # ========================================================
    # 10. 问题类别分布
    # ========================================================

    st.subheader("问题类别分布")

    category_count = {}

    for file_result in result["files"]:

        review = file_result[
            "review_result"
        ]

        for issue in review["issues"]:

            category = (
                issue.category
            )

            category_count[
                category
            ] = (
                category_count.get(
                    category,
                    0
                )
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

        category_df = (
            category_df.sort_values(
                by="Count",
                ascending=False
            )
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


    # ========================================================
    # 11. 问题筛选
    # ========================================================

    st.divider()

    st.subheader("问题筛选")

    filter_col1, filter_col2 = (
        st.columns(2)
    )

    all_severities = [
        "critical",
        "high",
        "medium",
        "low",
        "info"
    ]

    with filter_col1:

        selected_severities = (
            st.multiselect(
                "选择严重程度",
                options=all_severities,
                default=all_severities
            )
        )

    all_categories = set()

    for file_result in result["files"]:

        for issue in (
            file_result[
                "review_result"
            ]["issues"]
        ):

            all_categories.add(
                issue.category
            )

    all_categories = sorted(
        all_categories
    )

    with filter_col2:

        selected_categories = (
            st.multiselect(
                "选择问题类别",
                options=all_categories,
                default=all_categories
            )
        )


    # ========================================================
    # 12. 文件审查结果
    # ========================================================

    st.subheader(
        "文件审查结果"
    )

    visible_issue_count = 0

    for file_result in result["files"]:

        review = file_result[
            "review_result"
        ]

        filtered_issues = []

        for issue in review[
            "issues"
        ]:

            severity_match = (
                issue.severity.lower()
                in selected_severities
            )

            category_match = (
                issue.category
                in selected_categories
            )

            if (
                severity_match
                and category_match
            ):

                filtered_issues.append(
                    issue
                )

        # 当前筛选条件下该文件无问题
        if not filtered_issues:
            continue

        visible_issue_count += len(
            filtered_issues
        )

        with st.expander(
            (
                f"{file_result['file_path']} "
                f"({len(filtered_issues)} 个匹配问题)"
            )
        ):

            for issue in (
                filtered_issues
            ):

                st.markdown(
                    f"""
### [{issue.severity.upper()}] `{issue.rule}`

- **来源：** `{issue.source}`
- **类别：** `{issue.category}`
- **行号：** {issue.line if issue.line is not None else "Unknown"}
- **问题：** {issue.message}
"""
                )

                # ------------------------------
                # 获取源码上下文
                # ------------------------------

                snippet = get_code_snippet(
                    file_result[
                        "file_path"
                    ],
                    issue.line,
                    context=3
                )

                st.markdown(
                    "**代码位置：**"
                )

                st.code(
                    snippet,
                    language="text"
                )

                # ------------------------------
                # 修复建议
                # ------------------------------

                if issue.suggestion:

                    st.info(
                        f"建议："
                        f"{issue.suggestion}"
                    )

                st.divider()


    if visible_issue_count == 0:

        st.info(
            "当前筛选条件下没有匹配的问题。"
        )


    # ========================================================
    # 13. Qwen AI 项目综合审查
    # ========================================================

    st.divider()

    st.header(
        "Qwen AI 综合审查"
    )

    st.write(
        "Qwen 将结合整个项目的静态分析结果，"
        "从安全性、正确性、可维护性、性能和可读性"
        "等方面进行项目级综合分析。"
    )

    if st.button(
        "生成 Qwen 综合审查"
    ):

        try:

            with st.spinner(
                "Qwen 正在分析项目..."
            ):

                llm_result = (
                    review_project_with_llm(
                        result
                    )
                )

            st.session_state.llm_review = (
                llm_result
            )

            if llm_result is None:

                st.warning(
                    "Qwen 综合审查暂时不可用。"
                )

            else:

                st.success(
                    "AI 综合审查完成！"
                )

        except Exception as e:

            st.error(
                f"Qwen 综合审查失败：{e}"
            )


    # ========================================================
    # 14. 始终展示已经生成的 AI 结果
    # ========================================================

    llm_review = (
        st.session_state.llm_review
    )

    if llm_review is not None:

        st.subheader(
            "AI 综合评分"
        )

        score_col1, score_col2 = (
            st.columns([1, 3])
        )

        with score_col1:

            st.metric(
                "Overall Score",
                (
                    f"{llm_review.overall_score}"
                    f"/100"
                )
            )

        with score_col2:

            st.markdown(
                "### 项目总结"
            )

            st.write(
                llm_review.summary
            )


        st.subheader(
            "AI 发现的问题"
        )

        if not llm_review.issues:

            st.success(
                "Qwen 未发现额外的项目级问题。"
            )

        else:

            for index, issue in enumerate(
                llm_review.issues,
                1
            ):

                with st.expander(
                    (
                        f"AI Issue {index} | "
                        f"{issue.severity.upper()} | "
                        f"{issue.category}"
                    )
                ):

                    st.markdown(
                        f"""
- **严重程度：** `{issue.severity.upper()}`
- **类别：** `{issue.category}`
- **行号：** {issue.line if issue.line is not None else "Project Level"}

### 问题

{issue.problem}

### 原因

{issue.reason}

### 建议

{issue.suggestion}
"""
                    )

    else:

        st.info(
            "尚未生成 Qwen AI 综合审查结果。"
        )


    # ========================================================
    # 15. 生成并下载项目报告
    # ========================================================

    st.divider()

    st.subheader(
        "审查报告"
    )

    try:

        report_text = (
            generate_project_report(
                result,
                "outputs/project_review_report.md"
            )
        )

        st.download_button(
            label="下载 Markdown 审查报告",
            data=report_text,
            file_name=(
                "project_review_report.md"
            ),
            mime="text/markdown"
        )

    except Exception as e:

        st.error(
            f"生成报告失败：{e}"
        )


# ============================================================
# 16. 尚未进行审查时的提示
# ============================================================

else:

    st.info(
        "请输入项目路径并点击“开始审查”。"
    )