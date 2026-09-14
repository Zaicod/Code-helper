from pathlib import Path


def find_python_files(project_path: str) -> list[str]:
    """
    递归查找项目中的所有 Python 文件。
    """

    project = Path(project_path)

    if not project.exists():
        raise FileNotFoundError(
            f"项目路径不存在: {project_path}"
        )

    if not project.is_dir():
        raise ValueError(
            f"该路径不是目录: {project_path}"
        )

    python_files = []

    for file_path in project.rglob("*.py"):

        # 忽略常见无关目录
        ignored_parts = {
            ".venv",
            "venv",
            "__pycache__",
            ".git",
            "site-packages"
        }

        if any(
            part in ignored_parts
            for part in file_path.parts
        ):
            continue

        python_files.append(
            str(file_path)
        )

    return python_files