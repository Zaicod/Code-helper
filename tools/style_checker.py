import json
import subprocess
from core.models import ReviewIssue

def run_ruff(file_path: str) -> list:
    """
    使用 Ruff 对 Python 文件进行静态代码检查。

    Parameters
    ----------
    file_path : str
        待检查的 Python 文件路径。

    Returns
    -------
    list
        统一格式的问题列表。
    """

    result = subprocess.run(
        [   "python",
            "-m",
            "ruff",
            "check",
            file_path,
            "--output-format",
            "json",
        ],
        capture_output=True,
        text=True
    )

    if not result.stdout.strip():
        return []

    try:
        ruff_results = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"无法解析 Ruff 输出: \n{result.stdout}\n{result.stderr}"
        )

    issues = []

    for item in ruff_results:
        issues.append(
            ReviewIssue(
                source="ruff",
                category="quality",
                rule=item["code"],
                severity="low",
                line=item["location"]["row"],
                column=item["location"]["column"],
                message=item["message"]
            )
        )

    return issues