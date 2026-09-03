from tools.code_reader import read_code
from tools.syntax_checker import analyze_code_structure

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


if __name__ == "__main__":
	main()