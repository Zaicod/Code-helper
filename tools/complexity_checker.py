from radon.complexity import cc_visit

def analyze_complexity(code: str) -> list:
    """
    使用 Radon 分析 Python 代码的圈复杂度。

    Parameters
    ----------
    code : str
        Python 源代码。

    Returns
    -------
    list
        每个函数/方法的复杂度分析结果。
    """
    results = cc_visit(code)

    complexity_results = []

    for item in results:
        complexity_results.append({
            "name": item.name,
            "type": item.letter,
            "line": item.lineno,
            "complexity": item.complexity
        })

    return complexity_results