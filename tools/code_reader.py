from pathlib import Path

def read_code(file_path: str) -> str:
	"""
	读取Python源代码文件

    Parameters
    ----------
    file_path : str
        Python 文件路径。

    Returns
    -------
    str
        文件中的代码内容。
	"""
	path = Path(file_path)

	if not path.exists():
		raise FileNotFoundError(
			f"文件不存在: {file_path}"
		)

	if path.suffix != ".py":
		raise ValueError(
			"当前仅支持python文件"
		)

	return path.read_text(encoding="utf-8")