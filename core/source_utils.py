from pathlib import Path


def get_code_snippet(
    file_path: str,
    line_number: int | None,
    context: int = 3
) -> str:
    """
    获取问题行附近的源码片段。

    Parameters
    ----------
    file_path : str
        Python 文件路径

    line_number : int | None
        问题所在行

    context : int
        问题行前后各显示多少行

    Returns
    -------
    str
        带行号的源码片段
    """

    if line_number is None:
        return "无法确定问题所在行。"

    path = Path(file_path)

    if not path.exists():
        return "源代码文件不存在。"

    lines = path.read_text(
        encoding="utf-8"
    ).splitlines()

    if not lines:
        return "文件为空。"

    # line_number 从 1 开始
    target_index = line_number - 1

    if target_index < 0 or target_index >= len(lines):
        return "问题行号超出文件范围。"

    start = max(
        0,
        target_index - context
    )

    end = min(
        len(lines),
        target_index + context + 1
    )

    snippet_lines = []

    for index in range(start, end):

        current_line = index + 1

        marker = (
            ">>>"
            if current_line == line_number
            else "   "
        )

        snippet_lines.append(
            f"{marker} {current_line:4} | {lines[index]}"
        )

    return "\n".join(snippet_lines)