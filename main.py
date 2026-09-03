from tools.code_reader import read_code

def main():
	file_path = "data/sample_code.py"

	code = read_code(file_path)

	print("=" * 50)
	print("待审查代码")
	print("=" * 50)

	print(code)

if __name__ == "__main__":
	main()