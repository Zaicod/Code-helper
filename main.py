from tools.code_reader import read_code
from tools.syntax_checker import analyze_code_structure
from tools.rule_checker import check_code_rules
from tools.style_checker import run_ruff
from tools.complexity_checker import analyze_complexity

def main():
	file_path = "data/sample_code.py"

	code = read_code(file_path)

	print("=" * 50)
	print("待审查代码")
	print("=" * 50)
	print(code)

	structure = analyze_code_structure(code)

	print("\n" + "=" * 50)
	print("代码结构分析")
	print("=" * 50)

	print("Imports:")
	for item in structure["imports"]:
		print(
			f" - {item['name']}"
			f"(line {item['line']})"
		)

	print("\nFunctions:")
	for item in structure["functions"]:
		print(
			f" - {item['name']}"
			f"(line {item['line']})"
		)

	print("\nClasses:")
	for item in structure["classes"]:
		print(
			f" - {item['name']}"
			f"(line {item['line']})"
		)

	#规则检查
	issues = check_code_rules(code)

	print("\n" + "=" * 50)
	print("规则检查")
	print("=" * 50)

	if not issues:
		print("未发现问题")

	for issue in issues:
		print(
            f"[{issue['severity'].upper()}] "
            f"Line {issue['line']} | "
            f"{issue['rule']} | "
            f"{issue['message']}"
        )

	#Ruff
	ruff_issues = run_ruff(file_path)
	print("\n" + "=" * 50)
	print("Ruff 静态分析")
	print("=" * 50)

	if not ruff_issues:
		print("Ruff 未发现问题")

	for issue in ruff_issues:
		print(
			f"[{issue['severity'].upper()}] "
            f"Line {issue['line']}:{issue['column']} | "
            f"{issue['rule']} | "
            f"{issue['message']}"
		)

	print("\n" + "=" * 50)
	print("圈复杂度分析")
	print("=" * 50)

	#radon算函数复杂度
	complexity_results = analyze_complexity(code)

	if not complexity_results:
		print("未检测到函数或方法。")

	for item in complexity_results:
		print(
			f"{item['name']} | "
			f"Line {item['line']} | "
			f"Complexity: {item['complexity']} | "
			f"Grade: {item['type']}"
		)


if __name__ == "__main__":
	main()