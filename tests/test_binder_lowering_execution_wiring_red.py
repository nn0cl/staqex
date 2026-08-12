"""AT-TDD Phase 1 Red: LISS-0052 binder lowering execution wiring.

Reproduces the gap recorded in
docs/issues/LISS-0052-binder-lowering-execution-wiring.md: ADR 0088
Decision 3 promises finite-binder lowering produces "a concrete Pauli
Operator tree suitable for the existing Hamiltonian/Suzuki path", but the
implementation produces only an inspection `dict` under
`qpu_ir["binder_lowering"]`, while the AST bound to the operator name stays
`OpBinder` -- which no execution path can consume. Separately,
`compile_sparse_pauli` has no `OpIndexed` handler at all, so `Z[0]` fails
even outside a binder.

Expected to fail until Phase 2 Green wires lowering into an executable
OpExpr and adds OpIndexed support.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402
from compiler.staqex.host import run_source  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _run(source: str, *, seed: int = 7):
    return run_source(source, settings={"target": "local", "seed": seed}, stdout=io.StringIO())


def _emit(source: str):
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    return QASM3Emitter(route=False).emit_unit(compiled.unit)


# ---------------------------------------------------------------------------
# OpIndexed over a Pauli base must work outside a binder too -- this is a
# prerequisite the binder path itself depends on.
# ---------------------------------------------------------------------------

_INDEXED_PAULI_OUTSIDE_BINDER = """
package t
pub fn main() -> Unit {
    QubitRegister<2> register = system()
    Operator H = 1.0545718e-19 * (Z[0] * Z[1])
    State a = |+>
    State b = |0>
    State (a, b) = evolve { (a, b) under H for 0.1.fs using Suzuki(order = 2, steps = 4) }.run()
    State b = |0>
    measure a
}
"""

_HAND_WRITTEN_ZZ = """
package t
pub fn main() -> Unit {
    QubitRegister<2> register = system()
    Operator H = 1.0545718e-19 * (Z[0] * Z[1])
    State a = |+>
    State b = |0>
    State (a, b) = evolve { (a, b) under H for 0.1.fs using Suzuki(order = 2, steps = 4) }.run()
    State b = |0>
    measure a
}
"""


def test_indexed_pauli_runs_outside_a_binder() -> None:
    result = _run(_INDEXED_PAULI_OUTSIDE_BINDER)
    hand = _run(_HAND_WRITTEN_ZZ)

    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[0].marginal == hand.measurements[0].marginal


def test_indexed_pauli_emits_qasm_outside_a_binder() -> None:
    assert _emit(_INDEXED_PAULI_OUTSIDE_BINDER).ok


# ---------------------------------------------------------------------------
# The binder-lowered open chain must run and emit QASM, matching the
# hand-written 3-term equivalent numerically.
# ---------------------------------------------------------------------------

_BINDER_CHAIN = """
package t
pub fn main() -> Unit {
    QubitRegister<4> register = system()
    Operator H = sum (i in Index<0..2>) {
        1.0545718e-19 * Z[i] * Z[next(i)]
    }
    State a = |+>
    State b = |0>
    State c = |0>
    State d = |0>
    State (a, b, c, d) = evolve { (a, b, c, d) under H for 0.1.fs using Suzuki(order = 2, steps = 4) }.run()
    State b = |0>
    State c = |0>
    State d = |0>
    measure a
}
"""

_HAND_WRITTEN_CHAIN = """
package t
pub fn main() -> Unit {
    QubitRegister<4> register = system()
    Operator H = 1.0545718e-19 * (Z[0] * Z[1] + Z[1] * Z[2] + Z[2] * Z[3])
    State a = |+>
    State b = |0>
    State c = |0>
    State d = |0>
    State (a, b, c, d) = evolve { (a, b, c, d) under H for 0.1.fs using Suzuki(order = 2, steps = 4) }.run()
    State b = |0>
    State c = |0>
    State d = |0>
    measure a
}
"""


def test_binder_chain_runs_and_matches_hand_written_equivalent() -> None:
    result = _run(_BINDER_CHAIN)
    hand = _run(_HAND_WRITTEN_CHAIN)

    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[0].marginal == hand.measurements[0].marginal


def test_binder_chain_emits_qasm() -> None:
    assert _emit(_BINDER_CHAIN).ok


def test_binder_lowering_provenance_is_retained() -> None:
    """Provenance stays provenance -- this must not regress once lowering
    also produces an executable value."""
    compiled = compile_source(_BINDER_CHAIN)
    assert compiled.ok, compiled.diagnostics

    lowering = compiled.qpu_ir["binder_lowering"]["H"]
    assert lowering["domain"] == {"start": 0, "end": 2, "inclusive": True}
    assert lowering["expanded_terms"] == 3
    assert lowering["resource_check"] == "passed"
    assert lowering["provenance"]["binder_variable"] == "i"


if __name__ == "__main__":
    tests = [
        test_indexed_pauli_runs_outside_a_binder,
        test_indexed_pauli_emits_qasm_outside_a_binder,
        test_binder_chain_runs_and_matches_hand_written_equivalent,
        test_binder_chain_emits_qasm,
        test_binder_lowering_provenance_is_retained,
    ]
    passed, failed = 0, 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:  # noqa: BLE001 -- Red run report, not production code
            failed += 1
            print(f"RED (expected): {test.__name__}: {type(e).__name__}: {e}")
    print(f"\n{passed} passed, {failed} failed (Red until Phase 2 Green)")
