import ast

def analyze_code_structure(code: str) -> dict:
    """
    使用AST分析python代码结构
    """
    tree = ast.parse(code)

    result = {
        "imports": [],
        "functions": [],
        "classes": []
    }

    for node in ast.walk(tree):

        #import os
        if isinstance(node, ast.Import):
            for name in node.names:
                result["imports"].append({
                    "name": name.name,
                    "line": node.lineno
                })

        #from pathlib import Path
        elif isinstance(node, ast.ImportFrom):
            module = node.module

            for name in node.names:
                result["imports"].append({
                    "name": f"{module}.{name.name}",
                    "line": node.lineno
                })

        #def xxx():
        elif isinstance(node, ast.FunctionDef):
            result["functions"].append({
                "name": node.name,
                "line": node.lineno
            })

        #class Xxx:
        elif isinstance(node, ast.ClassDef):
            result["classes"].append({
                "name": node.name,
                "line": node.lineno
            })

    return result