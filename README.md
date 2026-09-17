# CodeReviewAgent

基于 Qwen Tool Calling 的智能代码审查 Agent，面向 Python 工程融合静态代码分析工具与大语言模型语义理解能力，实现代码质量、安全漏洞、复杂度及可维护性等多维度审查。

---

## 📝 项目简介

CodeReviewAgent 是一个面向 Python 项目的智能代码审查系统。

与单纯依赖大语言模型进行代码审查不同，本项目将传统静态分析工具与 Qwen 大语言模型结合，通过 Agent 自主选择分析工具并根据工具执行结果持续进行决策。

主要实现：

- 基于 Python AST 开发自定义规则引擎，检测 `eval`、`exec`、裸异常捕获等潜在风险代码；
- 设计统一 `ReviewIssue` 数据模型，对 AST、Ruff、Bandit、Radon 等多来源分析结果进行标准化；
- 集成 Ruff、Bandit、Radon，分别完成代码规范、安全漏洞及圈复杂度分析；
- 设计 Aggregator 模块，实现问题聚合、严重程度排序及统计；
- 基于 Qwen OpenAI-compatible API 实现 Tool Calling Agent；
- 实现 Agent Loop，使模型能够完成：

  `模型决策 → Tool Call → 工具执行 → Observation → 再决策 → Final Answer`

- 设计 `AgentState` 与 Tool Trace，记录工具调用步骤、参数、执行结果及最终回答；
- 实现 Python 项目级递归扫描和多文件代码审查；
- 使用 Streamlit 构建 Web Dashboard，实现风险统计、问题筛选、源码定位、AI 综合审查和 Markdown 报告导出。

---

## ✨ 核心功能

- [x] **多工具静态代码分析**

  集成 AST、Ruff、Bandit、Radon，对 Python 项目进行代码质量、安全性及复杂度分析。

- [x] **Qwen Tool-Calling Agent**

  Agent 根据用户任务自主决定是否调用源码读取、Ruff、Bandit、复杂度分析等工具，而非固定执行全部工具。

- [x] **Agent Loop 与状态管理**

  支持多轮 Tool Calling，并通过 `AgentState` 记录工具调用过程、Observation 和最终回答。

- [x] **项目级代码审查**

  递归扫描 Python 项目中的 `.py` 文件，对多个源文件进行统一分析和风险统计。

- [x] **Web Dashboard**

  提供项目概览、严重程度分布、文件风险排名、问题类别统计、问题筛选及源码片段定位。

- [x] **AI 项目综合审查**

  使用 Qwen 对静态分析结果进行项目级语义分析，并给出总体评分、风险总结和改进建议。

- [x] **审查报告导出**

  自动生成 Markdown 格式项目代码审查报告。

---

## 🏗 系统架构

```text
                     User Task
                         │
                         ▼
                 Qwen Review Agent
                         │
                  Tool Selection
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
      read_code         Ruff          Bandit
          │                              │
          └──────────────┬───────────────┘
                         │
                       Radon
                         │
                         ▼
                    Observation
                         │
                         ▼
                    Agent State
                         │
                  Need more tools?
                    │         │
                   Yes        No
                    │         │
                    └────┐    ▼
                         │ Final Answer
                         └───────