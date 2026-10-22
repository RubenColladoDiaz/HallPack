import os
import subprocess
import sys
import tempfile
from pathlib import Path

from hallpack.__main__ import findRequiredArtifacts


ROOT = Path(__file__).resolve().parents[1]


def run(*arguments):
    environment = os.environ.copy()
    environment["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-m", "hallpack", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=environment,
    )


def write_audit_files(directory):
    (directory / "build.sh").write_text(
        'TOOL_NAME="hubsync"\nTOOL_VERSION="01.02.03"\n',
        encoding="utf-8",
    )
    (directory / "pyproject.toml").write_text(
        '[project]\nname = "hubsync"\nversion = "01.02.03"\n',
        encoding="utf-8",
    )
    (directory / "versions.txt").write_text(
        "01.01.00\n01.02.03\n",
        encoding="utf-8",
    )
    (directory / "CHANGELOG.ver").write_text(
        "Version: 01.02.03\n"
        "Date: 10/10/2026\n"
        "Date: 09/10/2026\n"
        "- XHUB-101 change one\n"
        "Date: 08/10/2026\n"
        "- XHUB-102 change two\n"
        "- footer\n",
        encoding="utf-8",
    )
    (directory / "git_log.txt").write_text(
        "abc XHUB-101 change one\nabc XHUB-102 change two\n",
        encoding="utf-8",
    )


def test_resolve_branch_specific():
    result = run(
        "resolve-branch",
        "--branches",
        "data/tarea1/remote_branches.txt",
        "ORION_4.12.3",
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "releases/ORION_4.12.X"


def test_resolve_branch_general():
    result = run(
        "resolve-branch",
        "--branches",
        "data/tarea1/remote_branches.txt",
        "ORION_4.9.1",
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "releases/ORION_4.X"


def test_resolve_branch_release_candidate():
    result = run(
        "resolve-branch",
        "--branches",
        "data/tarea1/remote_branches.txt",
        "VEGA_2.7_RC2",
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "releases/VEGA_2.X"


def test_resolve_branch_stable():
    result = run(
        "resolve-branch",
        "--branches",
        "data/tarea1/remote_branches.txt",
        "LYRA_EDITOR_1.38.0",
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "releases/LYRA_EDITOR_1.X_stable"


def test_resolve_branch_accepts_multiple_tags():
    result = run(
        "resolve-branch",
        "--branches",
        "data/tarea1/remote_branches.txt",
        "ORION_4.12.3",
        "VEGA_2.7_RC2",
    )
    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "releases/ORION_4.12.X",
        "releases/VEGA_2.X",
    ]


def test_resolve_branch_rejects_malformed_tag():
    result = run(
        "resolve-branch",
        "--branches",
        "data/tarea1/remote_branches.txt",
        "invalid",
    )
    assert result.returncode == 1
    assert "ERROR: formato de tag inválido: invalid" in result.stderr


def test_resolve_branch_reports_missing_branch():
    result = run(
        "resolve-branch",
        "--branches",
        "data/tarea1/remote_branches.txt",
        "NOVA_2.1",
    )
    assert result.returncode == 1
    assert "ERROR para NOVA_2.1" in result.stderr


def test_next_version_patch():
    result = run("next-version", "03.04.00", "patch")
    assert result.returncode == 0
    assert result.stdout.strip() == "03.04.01"


def test_next_version_minor_resets_patch():
    result = run("next-version", "03.04.07", "minor")
    assert result.returncode == 0
    assert result.stdout.strip() == "03.05.00"


def test_next_version_major_resets_minor_and_patch():
    result = run("next-version", "03.04.07", "major")
    assert result.returncode == 0
    assert result.stdout.strip() == "04.00.00"


def test_next_version_rejects_wrong_number_of_fields():
    result = run("next-version", "1.2", "patch")
    assert result.returncode == 1
    assert "No son 3 campos" in result.stdout


def test_next_version_rejects_fields_not_two_digits():
    result = run("next-version", "1.02.03", "patch")
    assert result.returncode == 1
    assert "alguno de los campos no son 2 digitos" in result.stderr


def test_next_version_rejects_non_numeric_fields():
    result = run("next-version", "aa.02.03", "patch")
    assert result.returncode == 1
    assert "alguno de los campos no son 2 digitos" in result.stderr


def test_next_version_rejects_increment_over_99():
    result = run("next-version", "03.99.99", "patch")
    assert result.returncode == 1
    assert "No se permite que se pase de 99" in result.stderr


def test_next_version_rejects_unknown_increment_type():
    result = run("next-version", "03.04.00", "unknown")
    assert result.returncode == 2
    assert "invalid choice" in result.stderr


def test_audit_accepts_consistent_release_files():
    with tempfile.TemporaryDirectory() as temp_dir:
        directory = Path(temp_dir)
        write_audit_files(directory)

        result = run("audit", str(directory))

    assert result.returncode == 0
    assert result.stdout.strip() == "OK"


def test_audit_reports_all_release_problems():
    with tempfile.TemporaryDirectory() as temp_dir:
        directory = Path(temp_dir)
        write_audit_files(directory)
        (directory / "build.sh").write_text(
            'TOOL_NAME="different"\nTOOL_VERSION="01.02.04"\n',
            encoding="utf-8",
        )
        (directory / "CHANGELOG.ver").write_text(
            "Version: 01.02.03\n"
            "Date: 08/10/2026\n"
            "Date: 09/10/2026\n"
            "- XHUB-999 change one\n"
            "Date: 10/10/2026\n"
            "- XHUB-102 change two\n"
            "- footer\n",
            encoding="utf-8",
        )

        result = run("audit", str(directory))

    assert result.returncode == 1
    assert "La version no se encuentra en versions.txt" in result.stderr
    assert "Los archivos contienen versiones distintas" in result.stderr
    assert "Los nombres no concuerdan" in result.stderr
    assert "Fechas desordenadas" in result.stderr
    assert "Los logs de git_log y CHANGELOG no coinciden" in result.stderr


def test_audit_reports_missing_version_in_build_file():
    with tempfile.TemporaryDirectory() as temp_dir:
        directory = Path(temp_dir)
        write_audit_files(directory)
        (directory / "build.sh").write_text('TOOL_NAME="hubsync"\n', encoding="utf-8")

        result = run("audit", str(directory))

    assert result.returncode == 1
    assert "no se encontró TOOL_VERSION en build.sh" in result.stderr


def test_plan_lists_changed_engine_and_games_and_reports_differences():
    result = run(
        "plan",
        "--hall",
        "data/tarea3/hall_state.json",
        "--target",
        "data/tarea3/target.json",
        "--index",
        "data/tarea3/index",
    )

    assert result.returncode == 0
    assert "Descargar engine ORION 4.12.3:" in result.stdout
    assert "Descargar engine VEGA 2.7_RC2:" in result.stdout
    assert "Descargar game DRGF 02.04.00:" in result.stdout
    assert "Descargar game GLDR" not in result.stdout
    assert "Descargar game PHNX" not in result.stdout
    assert "La version de motor ha cambiado." in result.stdout
    assert "El juego PHNX está en la sala pero no en el target." in result.stdout
    assert "El juego LKCH está en el target pero no en la sala." in result.stdout
    assert "ciclo de paginación" in result.stderr


def test_find_required_artifacts_skips_unchanged_items_and_non_release_items():
    hall_state = {
        "mixes": [
            {
                "name": "MIX",
                "engine": "ORION_4.12.3",
                "games": [{"acronym": "DRGF", "version": "02.04.00"}],
            }
        ]
    }
    target = {
        "mixes": [
            {
                "name": "MIX",
                "engine": "ORION_4.12.3",
                "games": [{"acronym": "DRGF", "version": "02.04.00"}],
            }
        ]
    }
    artifacts = [
        {
            "kind": "game",
            "name": "DRGF",
            "version": "02.04.00",
            "repository": "staging",
        }
    ]
    notes = []

    downloads = findRequiredArtifacts(hall_state, target, artifacts, notes)

    assert downloads == []
    assert notes == []


def test_find_required_artifacts_reports_missing_engine_and_game():
    hall_state = {"mixes": []}
    target = {
        "mixes": [
            {
                "name": "NEW_MIX",
                "engine": "ORION_4.12.3",
                "games": [{"acronym": "DRGF", "version": "02.04.00"}],
            }
        ]
    }
    notes = []

    downloads = findRequiredArtifacts(hall_state, target, [], notes)

    assert downloads == []
    assert notes == [
        "No se encontró en releases el motor ORION 4.12.3.",
        "No se encontró en releases el juego DRGF 02.04.00.",
    ]
