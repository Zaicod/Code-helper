import json
import subprocess
import sys
from core.models import ReviewIssue

def run_bandit(file_path: str) -> list:
    """
    使用 Bandit 对 Python 文件进行安全检查。

    Parameters
    ----------
    file_path : str
        待检查 Python 文件路径。

    Returns
    -------
    list
        统一格式的安全问题列表。
    """

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "bandit",
            "-f",
            "json",
            "-q",
            file_path
        ],
        capture_output=True,
        text=True
    )

    if not result.stdout.strip():
        return []

    try:
        bandit_result = json.loads(result.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"无法解析 Bandit 输出: \n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    issues = []

    for item in bandit_result.get("result",[]):
        issues.append(
            ReviewIssue(
                source="bandit",
                category="security",
                rule=item.get("test_id"),
                severity=item.get(
                    "issue_severity",
                    "LOW"
                ).lower(),
                line=item.get("line_number"),
                column=None,
                message=item.get("issue_text")
            )
        )
    return issues