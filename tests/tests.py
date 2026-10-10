import subprocess

def run(command):
    return subprocess.check_output("python -m hallpack " + command, shell=True, text=True).strip()