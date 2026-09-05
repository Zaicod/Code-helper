import ast
from core.models import ReviewIssue

def check_code_rules(code: str) -> list:
    """
    使用AST检查一些常见的危险代码模式

    Returns
    ----------
    list
        问题列表
    """

    tree = ast.parse(code)

    issues = []

    for node in ast.walk(tree):

        #1. 监测 eval()
        if isinstance(node, ast.Call):
            if(
                isinstance(node.func, ast.Name)
                and node.func.id == "eval"
            ):
                issues.append(
                    ReviewIssue(
                        source="ast",
                        category="security",
                        rule="dangerous-eval",
                        severity="high",
                        line=node.lineno,
                        column=node.col_offset,
                        message="检测到 eval()，可能执行不可信代码。",
                        suggestion="避免直接使用 eval()，优先使用更安全的解析方式。"
                    )
                )

        #2. 检测exec()
        if isinstance(node, ast.Call):
            if(
                isinstance(node.func, ast.Name)
                and node.func.id == "exec"
            ):
                issues.append(
                    ReviewIssue(
                        source="ast",
                        category="security",
                        rule="dangerous-exec",
                        severity="high",
                        line=node.lineno,
                        column=node.col_offset,
                        message="检测到 exec()，可能执行任意代码。",
                        suggestion="避免执行来自外部或不可信来源的动态代码。"
                    )
                )

        #3. 检测 os.system(...)
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):

                if(
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "os"
                    and node.func.attr == "system"
                ):
                    issues.append(
                    ReviewIssue(
                        source="ast",
                        category="quality",
                        rule="bare-except",
                        severity="medium",
                        line=node.lineno,
                        column=node.col_offset,
                        message="检测到裸 except，可能捕获过多异常。",
                        suggestion="应捕获明确的异常类型。"
                    )
                )

        #检测 except
        if isinstance(node, ast.ExceptHandler):

            if node.type is None:
                    issues.append(
                    ReviewIssue(
                        source="ast",
                        category="quality",
                        rule="bare-except",
                        severity="medium",
                        line=node.lineno,
                        column=node.col_offset,
                        message="检测到裸 except，可能捕获过多异常。",
                        suggestion="应捕获明确的异常类型。"
                    )
                )

            #检测 except: pass
            if(
                len(node.body) == 1
                and isinstance(node.body[0], ast.Pass)
            ):
                 issues.append(
                    ReviewIssue(
                        source="ast",
                        category="quality",
                        rule="bare-except",
                        severity="medium",
                        line=node.lineno,
                        column=node.col_offset,
                        message="检测到裸 except，可能捕获过多异常。",
                        suggestion="应捕获明确的异常类型。"
                    )
                )
    return issues
