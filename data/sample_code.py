import os
import subprocess


PASSWORD = "123456"


def calculate(expression):
    return eval(expression)


def run_command(command):
    os.system(command)


def dangerous_shell(command):
    subprocess.call(
        command,
        shell=True
    )