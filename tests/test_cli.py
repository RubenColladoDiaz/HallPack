import subprocess

def run(command):
    return subprocess.check_output("python -m hallpack " + command, shell=True, text=True).strip()

def test_resolve_branch_specific():
    assert run("resolve-branch --branches data/tarea1/remote_branches.txt ORION_4.12.3") == "releases/ORION_4.12.X"

def test_resolve_branch_general():
    assert run("resolve-branch --branches data/tarea1/remote_branches.txt ORION_4.9.1") == "releases/ORION_4.X"


def test_resolve_branch_rc():
    assert run("resolve-branch --branches data/tarea1/remote_branches.txt VEGA_2.7_RC2") == "releases/VEGA_2.X"


def test_resolve_branch_stable():
    assert run("resolve-branch --branches data/tarea1/remote_branches.txt LYRA_EDITOR_1.38.0") == "releases/LYRA_EDITOR_1.X_stable"

def test_resolve_branch_not_found():
    assert run("resolve-branch --branches data/tarea1/remote_branches.txt NOVA_2.1") == "ERROR para NOVA_2.1"

def test_next_version_patch():
    assert run("next-version 03.04.00 patch") == "03.04.01"


def test_next_version_minor():
    assert run("next-version 03.04.07 minor") == "03.05.00"


def test_next_version_major():
    assert run("next-version 03.04.07 major") == "04.00.00"

def test_next_version_bad_format():
    assert run("next-version 1.2 patch") == "No son 3 campos"


def test_next_version_over_99():
    assert run("next-version 03.99.99 patch") == "No se permite que se pase de 99"