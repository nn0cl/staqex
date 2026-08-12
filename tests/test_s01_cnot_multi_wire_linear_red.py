"""AT-TDD: multi-wire in-place ``cnot`` bind (S01 linear alignment)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402


def test_cnot_multi_wire_rebind_keeps_both_linear() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Operator ZZ = Z * Z
        State ctrl = |1>
        State tgt = |0>
        State (ctrl, tgt) = cnot(ctrl, tgt)
        State corr = expect(ZZ, ctrl, tgt)
        State viewed = inspect(corr)
        State tgt = |0>
        measure ctrl
    }
    """
    codes = {d.get("code", "") for d in compile_source(src).diagnostics}
    assert "LINEAR_DUPLICATE_USE" not in codes, codes
    assert "LINEAR_IMPLICIT_DISCARD" not in codes, codes

    result = run_source(src, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 1


def test_s01_tri_register_compiles_clean() -> None:
    path = _REPO / "examples/showcase/S01_quantum_disaster_response/main_tri_register.sqx"
    from compiler.staqex.pipeline import compile_path

    compiled = compile_path(path)
    hard = {
        d.get("code", "")
        for d in compiled.diagnostics
        if d.get("code") in {"LINEAR_DUPLICATE_USE", "LINEAR_IMPLICIT_DISCARD", "PARSE_ERROR"}
    }
    assert not hard, compiled.diagnostics
    assert compiled.ok, compiled.diagnostics


if __name__ == "__main__":
    test_cnot_multi_wire_rebind_keeps_both_linear()
    print("PASS cnot multi")
    test_s01_tri_register_compiles_clean()
    print("PASS s01 tri")
    print("OK")
