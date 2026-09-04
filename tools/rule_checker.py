import ast

def check_code_rules(code: str) -> list:
    """
    使用AST检查一些常见的危险代码模式

    Returns
    ----------
    list
        问题列表
    """

    tree = ast.parse(code)

    issuse = []

    for node in ast.walk(tree):

        #1. 监测 eval()
        if isinstance(node, ast.Call):
            if(
                isinstance(node.func, ast.Name)
                and node.func.id == "eval"
            ):
                issuse.append({
                    "type": "security",
                    "rule": "dangerous-eval",
                    "severity": "high",
                    "line": node.lineno,
                    "message": "检测到eval(), 可能执行不可信代码!"
                })

        #2. 检测exec()
        if isinstance(node, ast.Call):
            if(
                isinstance(node.func, ast.Name)
                and node.func.id == "exec"
            ):
                issuse.append({
                    "type": "security",
                    "rule": "dangerous-exec",
                    "severity": "high",
                    "line": node.lineno,
                    "message": "检测到exec(), 可能执行任意代码!"
                })

        #3. 检测 os.system(...)
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):

                if(
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "os"
                    and node.func.attr == "system"
                ):
                    issuse.append({
                        "type": "security",
                        "rule": "os-system",
                        "severity": "high",
                        "line": node.lineno,
                        "message": "检测到 os.system()，需要注意命令注入风险。"
                    })

        #检测 except
        if isinstance(node, ast.ExceptHandler):

            if node.type is None:
                issuse.append({
                    "type": "quality",
                    "rule": "bare-except",
                    "severity": "medium",
                    "line": node.lineno,
                    "message": "检测到裸 except，可能隐藏真实异常。"
                })

            #检测 except: pass
            if(
                len(node.body) == 1
                and isinstance(node.body[0], ast.Pass)
            ):
                issuse.append({
                    "type": "quality",
                    "rule": "silent-exception",
                    "severity": "medium",
                    "line": node.lineno,
                    "message": "异常被直接忽略，可能导致错误静默发生。"
                })
    return issuse
