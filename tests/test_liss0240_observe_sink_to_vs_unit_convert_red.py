"""AT-TDD: LISS-0240 Measure/Snapshot `to <sink>` vs unit convert."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402


def test_snapshot_to_stdout_parses_and_runs() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        State x = Coin()
        Snapshot x to stdout
        Measure x
    }
    """
    compiled = compile_source(src)
    codes = {d.get("code", "") for d in compiled.diagnostics}
    assert "PARSE_ERROR" not in codes, compiled.diagnostics
    assert compiled.ok, compiled.diagnostics

    buf = io.StringIO()
    result = run_source(src, seed=0, stdout=buf)
    assert result.compile_ok, result.diagnostics
    text = buf.getvalue()
    assert "value" in text and "mass" in text, text
    assert result.eval.measure is not None


def test_measure_to_stdout_parses() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        State x = Coin()
        Measure x to stdout
    }
    """
    compiled = compile_source(src)
    codes = {d.get("code", "") for d in compiled.diagnostics}
    assert "PARSE_ERROR" not in codes, compiled.diagnostics
    assert "TYPE_MISMATCH" not in codes, compiled.diagnostics
    assert compiled.ok, compiled.diagnostics


def test_explicit_unit_convert_still_parses() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Float m = 1.0
        Float kg = m to kg
        State s = Dirac(0)
        Measure s
    }
    """
    # May fail for other reasons; must not treat `to` as unavailable.
    compiled = compile_source(src)
    codes = {d.get("code", "") for d in compiled.diagnostics}
    assert "PARSE_ERROR" not in codes, compiled.diagnostics


if __name__ == "__main__":
    test_snapshot_to_stdout_parses_and_runs()
    print("PASS Snapshot")
    test_measure_to_stdout_parses()
    print("PASS Measure")
    test_explicit_unit_convert_still_parses()
    print("PASS unit convert")
    print("OK — LISS-0240")
