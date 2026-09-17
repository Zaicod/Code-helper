from agents.tool_calling_agent import (
    run_code_review_agent
)


def main():

    task = """
请检查 data/demo_project/utils.py。

重点关注安全问题。

如果需要，请自主选择合适的工具。
"""

    state = run_code_review_agent(
        task
    )

    print("\n")
    print("=" * 60)
    print("Agent Execution Trace")
    print("=" * 60)

    for trace in state.traces:

        print(
            f"\nStep {trace.step}"
        )

        print(
            f"Tool: {trace.tool_name}"
        )

        print(
            f"Arguments: {trace.arguments}"
        )

        if trace.error:

            print(
                f"Error: {trace.error}"
            )

        else:

            print(
                f"Result: {trace.result}"
            )

    print("\n")
    print("=" * 60)
    print("Agent Final Answer")
    print("=" * 60)

    print(
        state.final_answer
    )


if __name__ == "__main__":
    main()