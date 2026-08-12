"""Regression coverage for the migrated LISS-0051 operator parser path.

LISS-0054 makes bracketed indexed Pauli atoms the canonical spelling and
keeps genuine factory calls such as ``make_coin()`` in the generic grammar.
The tests below cover the migrated parser/runtime/QASM baseline.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import OpBin, OpHop, OpIndexed, OpPauli  # noqa: E402
from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402
from compiler.staqex.host import run_source  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _operator_expr(decl: str):
    compiled = compile_source(
        f"""
        package t
        pub fn main() -> Unit {{
            {decl}
            State psi = |0>
            measure psi
        }}
        """
    )
    assert compiled.ok, compiled.diagnostics
    for stmt in compiled.unit.main.body.stmts:
        if getattr(stmt, "names", None) == ["H"]:
            return stmt.expr
    raise AssertionError("no `H` bind found")


def test_indexed_pauli_atom_parses_as_op_indexed() -> None:
    expr = _operator_expr("Operator H = Z[0]")

    assert isinstance(expr, OpIndexed)
    assert isinstance(expr.base, OpPauli)
    assert expr.base.kind == "Z"
    assert expr.index.value == 0


def test_indexed_pauli_product_parses_as_op_bin() -> None:
    expr = _operator_expr("Operator H = Z[0] * Z[1]")

    assert isinstance(expr, OpBin)
    assert expr.op == "*"
    assert isinstance(expr.lhs, OpIndexed)
    assert isinstance(expr.lhs.base, OpPauli)
    assert expr.lhs.base.kind == "Z" and expr.lhs.index.value == 0
    assert isinstance(expr.rhs, OpIndexed)
    assert isinstance(expr.rhs.base, OpPauli)
    assert expr.rhs.base.kind == "Z" and expr.rhs.index.value == 1


def test_hop_call_parses_as_op_hop() -> None:
    expr = _operator_expr("Operator H = hop(0, 1)")

    assert isinstance(expr, OpHop)
    assert expr.i == 0
    assert expr.j == 1


_BARE_ZZ_PROGRAM = """
package t
pub fn main() -> Unit {
    Operator H = 1.0545718e-19 * (Z[0] * Z[1])
    State a = |+>
    State b = |0>
    State (a, b) = evolve { (a, b) under H for 0.1.fs using Suzuki(order = 2, steps = 4) }.run()
    State b = |0>
        State b = |0>
measure a
}
"""


def test_bare_pauli_product_hamiltonian_runs_on_sv_simulator() -> None:
    result = run_source(_BARE_ZZ_PROGRAM, settings={"target": "local", "seed": 7}, stdout=io.StringIO())

    assert result.status == "succeeded", result.diagnostics


def test_bare_pauli_product_hamiltonian_emits_qasm() -> None:
    compiled = compile_source(_BARE_ZZ_PROGRAM)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None

    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)
    assert emitted.ok, emitted.notes


def test_factory_call_pattern_is_unaffected() -> None:
    """`Operator k = make_coin()` (a genuine factory call, not a reserved
    Pauli-DSL atom name) must keep parsing as a generic Call, matching the
    heuristic's stated intent -- this pins the no-regression requirement."""
    from compiler.staqex.ast_nodes import Call

    compiled = compile_source(
        """
        package t
        fn make_coin() -> Operator {
            Operator k = X
            return k
        }
        pub fn main() -> Unit {
            Operator k = make_coin()
            State psi = |0>
            measure psi
        }
        """
    )
    assert compiled.ok, compiled.diagnostics
    for stmt in compiled.unit.main.body.stmts:
        if getattr(stmt, "names", None) == ["k"]:
            assert isinstance(stmt.expr, Call)
            return
    raise AssertionError("no `k` bind found")


if __name__ == "__main__":
    tests = [
        test_indexed_pauli_atom_parses_as_op_indexed,
        test_indexed_pauli_product_parses_as_op_bin,
        test_hop_call_parses_as_op_hop,
        test_bare_pauli_product_hamiltonian_runs_on_sv_simulator,
        test_bare_pauli_product_hamiltonian_emits_qasm,
        test_factory_call_pattern_is_unaffected,
    ]
    passed, failed = 0, 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:  # noqa: BLE001 -- Red run report, not production code
            failed += 1
            print(f"FAIL: {test.__name__}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed (Phase 3 migration)")
