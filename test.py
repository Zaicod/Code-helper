from tools.project_scanner import find_python_files


files = find_python_files(
    "data/demo_project"
)

for file in files:
    print(file)