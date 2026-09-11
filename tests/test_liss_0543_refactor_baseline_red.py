"""Phase 1 Red contracts for generated behavior-preservation evidence."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


REPOSITORY = Path(__file__).resolve().parents[1]
GENERATOR = REPOSITORY / "scripts" / "capture-refactor-baseline.py"
CASES = REPOSITORY / "tests" / "fixtures" / "liss_0543" / "baseline-cases.toml"


def _generate(output: Path, *, cases: Path = CASES) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--root",
            str(REPOSITORY),
            "--cases",
            str(cases),
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def test_generated_baseline_is_byte_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"

    first_result = _generate(first)
    second_result = _generate(second)

    assert first_result.returncode == 0, first_result.stdout + first_result.stderr
    assert second_result.returncode == 0, second_result.stdout + second_result.stderr
    assert first.read_bytes() == second.read_bytes()


def test_baseline_contains_required_public_and_behavior_evidence(tmp_path: Path) -> None:
    output = tmp_path / "baseline.json"

    result = _generate(output)

    assert result.returncode == 0, result.stdout + result.stderr
    document = json.loads(output.read_text(encoding="utf-8"))
    assert document["schema_version"] == 1
    assert set(document["public_modules"]) == {
        "compiler.staqex.runtime.evaluator",
        "compiler.staqex.typecheck",
        "compiler.staqex.parser",
        "compiler.staqex.scientific_semantic_ir",
        "compiler.staqex.backend.qasm.lower",
        "compiler.staqex.pipeline",
    }
    assert set(document["cases"]) == {
        "runtime:b01-fixed-seed",
        "qasm:a08-entangled-ancilla",
        "diagnostic:missing-expression",
    }
    for evidence in document["cases"].values():
        assert evidence["status"] in {"accepted", "rejected"}
        assert evidence["sha256"].startswith("sha256:")


def test_baseline_contains_no_machine_specific_path_or_timestamp(tmp_path: Path) -> None:
    output = tmp_path / "baseline.json"

    result = _generate(output)

    assert result.returncode == 0, result.stdout + result.stderr
    rendered = output.read_text(encoding="utf-8")
    document = json.loads(rendered)
    assert str(REPOSITORY) not in rendered
    assert "generated_at" not in document
    assert "cwd" not in document


def test_missing_case_input_fails_without_partial_baseline(tmp_path: Path) -> None:
    cases = tmp_path / "invalid-cases.toml"
    cases.write_text(
        """\
version = 1

[[runtime_case]]
id = "runtime:missing"
source = "tests/fixtures/does-not-exist.sqx"
seed = 0
""",
        encoding="utf-8",
    )
    output = tmp_path / "baseline.json"

    result = _generate(output, cases=cases)

    assert result.returncode == 1, result.stdout + result.stderr
    assert "REFACTOR_BASELINE_INPUT_MISSING" in result.stdout
    assert not output.exists()
