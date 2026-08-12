"""AT-TDD Phase 1 Red: LISS-0032 Jordan-Wigner numerical mapping (ADR 0093).

Reproduces the gap recorded in
docs/issues/LISS-0032-typed-second-quantized-operators.md and formalized in
docs/architecture/decision-themes/dec-0005-quantum-operations-and-runtime.md: `map(H,
JordanWigner)` records only a name string in the Symbolic IR today and
produces no executable Pauli operator, so a second-quantized program
type-checks but cannot be run on the SV simulator or lowered to QASM.

Per the Adjudicator's explicit acceptance criterion (2026-07-25): both the
simulator path (`run`) and the QASM path (`emit-qasm`) must work for a
mapped Hamiltonian -- neither alone is acceptance. Scope includes one-body
and two-body fermionic terms (Bravyi-Kitaev, Boson, and Spin mappings
remain deferred per ADR 0093).

Expected to fail until Phase 2 Green implements the mapping.
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


def _marginals_close(a: dict, b: dict, *, tol: float = 1e-9) -> bool:
    keys = set(a) | set(b)
    return all(abs(a.get(k, 0.0) - b.get(k, 0.0)) < tol for k in keys)


def _run(source: str, *, seed: int = 7):
    return run_source(source, settings={"target": "local", "seed": seed}, stdout=io.StringIO())


def _emit_ok(source: str) -> bool:
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    return QASM3Emitter(route=False).emit_unit(compiled.unit).ok


# ---------------------------------------------------------------------------
# One-body, diagonal (number operator): n_0 = a†_0 a_0 = (I - Z_0) / 2
# ---------------------------------------------------------------------------

_NUMBER_OPERATOR_JW = """
package t
pub fn main() -> Unit {
    FermionOperator<Orbitals> H = 1.0545718e-19 * create[0] * annihilate[0]
    QubitOperator<Qubits> mapped = map(H, JordanWigner)
    state psi = |+>
    state psi = evolve { psi under mapped for 1.0.fs using Suzuki(order = 2, steps = 8) }.run()
    measure psi
}
"""

_NUMBER_OPERATOR_HAND_WRITTEN = """
package t
pub fn main() -> Unit {
    Operator H = 5.272859e-20 * I - 5.272859e-20 * Z[0]
    state psi = |+>
    state psi = evolve { psi under H for 1.0.fs }.run()
    measure psi
}
"""


def test_diagonal_number_operator_runs_and_matches_hand_written_pauli() -> None:
    jw = _run(_NUMBER_OPERATOR_JW)
    hand = _run(_NUMBER_OPERATOR_HAND_WRITTEN)

    assert jw.status == "succeeded", jw.diagnostics
    assert hand.status == "succeeded"
    assert _marginals_close(
        jw.measurements[0].marginal, hand.measurements[0].marginal
    )


def test_diagonal_number_operator_emits_qasm() -> None:
    assert _emit_ok(_NUMBER_OPERATOR_JW)


# ---------------------------------------------------------------------------
# One-body hopping, adjacent sites (no parity string):
# a†_0 a_1 + a†_1 a_0 = (X_0 X_1 + Y_0 Y_1) / 2
# ---------------------------------------------------------------------------

_HOPPING_ADJACENT_JW = """
package t
pub fn main() -> Unit {
    FermionOperator<Orbitals> H = 1.0545718e-19 * create[0] * annihilate[1] + 1.0545718e-19 * create[1] * annihilate[0]
    QubitOperator<Qubits> mapped = map(H, JordanWigner)
    state a = |+>
    state b = |0>
    state (a, b) = evolve { (a, b) under mapped for 1.0.fs using Suzuki(order = 2, steps = 8) }.run()
    state b = |0>
    measure a
}
"""

_HOPPING_ADJACENT_HAND_WRITTEN = """
package t
pub fn main() -> Unit {
    Operator H = 5.272859e-20 * (X[0] * X[1]) + 5.272859e-20 * (Y[0] * Y[1])
    state a = |+>
    state b = |0>
    state (a, b) = evolve { (a, b) under H for 1.0.fs }.run()
    state b = |0>
    measure a
}
"""


def test_adjacent_hopping_term_runs_and_matches_hand_written_pauli() -> None:
    jw = _run(_HOPPING_ADJACENT_JW)
    hand = _run(_HOPPING_ADJACENT_HAND_WRITTEN)

    assert jw.status == "succeeded", jw.diagnostics
    assert _marginals_close(
        jw.measurements[0].marginal, hand.measurements[0].marginal
    )


def test_adjacent_hopping_term_emits_qasm() -> None:
    assert _emit_ok(_HOPPING_ADJACENT_JW)


# ---------------------------------------------------------------------------
# One-body hopping with a parity (Z) string between non-adjacent sites:
# a†_0 a_2 + a†_2 a_0 = (X_0 Z_1 X_2 + Y_0 Z_1 Y_2) / 2
# ---------------------------------------------------------------------------

_HOPPING_WITH_PARITY_JW = """
package t
pub fn main() -> Unit {
    FermionOperator<Orbitals> H = 1.0545718e-19 * create[0] * annihilate[2] + 1.0545718e-19 * create[2] * annihilate[0]
    QubitOperator<Qubits> mapped = map(H, JordanWigner)
    state a = |+>
    state b = |0>
    state c = |0>
    state (a, b, c) = evolve { (a, b, c) under mapped for 1.0.fs using Suzuki(order = 2, steps = 8) }.run()
    state b = |0>
    state c = |0>
    measure a
}
"""

_HOPPING_WITH_PARITY_HAND_WRITTEN = """
package t
pub fn main() -> Unit {
    Operator H = 5.272859e-20 * (X[0] * Z[1] * X[2]) + 5.272859e-20 * (Y[0] * Z[1] * Y[2])
    state a = |+>
    state b = |0>
    state c = |0>
    state (a, b, c) = evolve { (a, b, c) under H for 1.0.fs }.run()
    state b = |0>
    state c = |0>
    measure a
}
"""


def test_nonadjacent_hopping_term_carries_parity_string() -> None:
    """The Z-string between operator indices is what makes JW nontrivial;
    a mapping that dropped it would still run, but would compute the wrong
    physics. Comparing against the explicit hand-written Z-string form
    catches that class of error, not just "did it crash"."""
    jw = _run(_HOPPING_WITH_PARITY_JW)
    hand = _run(_HOPPING_WITH_PARITY_HAND_WRITTEN)

    assert jw.status == "succeeded", jw.diagnostics
    assert _marginals_close(
        jw.measurements[0].marginal, hand.measurements[0].marginal
    )


def test_nonadjacent_hopping_term_emits_qasm() -> None:
    assert _emit_ok(_HOPPING_WITH_PARITY_JW)


# ---------------------------------------------------------------------------
# Two-body density-density interaction (in scope per the Adjudicator's
# 2026-07-25 decision -- NOT deferred):
# n_0 n_1 = a†_0 a_0 a†_1 a_1 = (I - Z_0 - Z_1 + Z_0 Z_1) / 4
# ---------------------------------------------------------------------------

_TWO_BODY_DENSITY_JW = """
package t
pub fn main() -> Unit {
    FermionOperator<Orbitals> H = 1.0545718e-19 * create[0] * create[1] * annihilate[1] * annihilate[0]
    QubitOperator<Qubits> mapped = map(H, JordanWigner)
    state a = |+>
    state b = |+>
    state (a, b) = evolve { (a, b) under mapped for 1.0.fs using Suzuki(order = 2, steps = 8) }.run()
    state b = |0>
    measure a
}
"""

_TWO_BODY_DENSITY_HAND_WRITTEN = """
package t
pub fn main() -> Unit {
    Operator H = 2.6364295e-20 * I - 2.6364295e-20 * Z[0] - 2.6364295e-20 * Z[1] + 2.6364295e-20 * (Z[0] * Z[1])
    state a = |+>
    state b = |+>
    state (a, b) = evolve { (a, b) under H for 1.0.fs }.run()
    state b = |0>
    measure a
}
"""


def test_two_body_density_density_runs_and_matches_hand_written_pauli() -> None:
    jw = _run(_TWO_BODY_DENSITY_JW)
    hand = _run(_TWO_BODY_DENSITY_HAND_WRITTEN)

    assert jw.status == "succeeded", jw.diagnostics
    assert _marginals_close(
        jw.measurements[0].marginal, hand.measurements[0].marginal
    )


def test_two_body_density_density_emits_qasm() -> None:
    assert _emit_ok(_TWO_BODY_DENSITY_JW)


# ---------------------------------------------------------------------------
# Provenance: mapping name and qubit count must be recorded (ADR 0093 #6)
# ---------------------------------------------------------------------------


def test_mapping_provenance_records_name_and_qubit_count() -> None:
    compiled = compile_source(_NUMBER_OPERATOR_JW)
    assert compiled.ok, compiled.diagnostics

    mappings = compiled.symbolic_ir["resolved"]["mappings"]
    assert len(mappings) == 1
    record = mappings[0]
    assert record["operator"] == "mapped"
    assert record["mapping"] == "JordanWigner"
    assert record["qubit_count"] == 1


def test_two_body_mapping_provenance_records_qubit_count() -> None:
    compiled = compile_source(_TWO_BODY_DENSITY_JW)
    assert compiled.ok, compiled.diagnostics

    mappings = compiled.symbolic_ir["resolved"]["mappings"]
    assert mappings[0]["qubit_count"] == 2


# ---------------------------------------------------------------------------
# No silent fallback: Boson/Spin mapping remain deferred (ADR 0093) and must
# produce an explicit diagnostic, never a silently accepted/garbage operator.
# ---------------------------------------------------------------------------

_BOSON_MAPPING_ATTEMPT = """
package t
pub fn main() -> Unit {
    BosonOperator<Modes> H = create[0] * annihilate[0]
    QubitOperator<Qubits> mapped = map(H, JordanWigner)
    state psi = |0>
    measure psi
}
"""


def test_boson_mapping_is_explicitly_diagnosed_not_silently_accepted() -> None:
    result = _run(_BOSON_MAPPING_ATTEMPT)

    assert result.status == "failed"
    codes = {d.get("code") for d in result.diagnostics}
    assert "SECOND_QUANTIZATION_MAPPING_UNSUPPORTED" in codes


if __name__ == "__main__":
    tests = [
        test_diagonal_number_operator_runs_and_matches_hand_written_pauli,
        test_diagonal_number_operator_emits_qasm,
        test_adjacent_hopping_term_runs_and_matches_hand_written_pauli,
        test_adjacent_hopping_term_emits_qasm,
        test_nonadjacent_hopping_term_carries_parity_string,
        test_nonadjacent_hopping_term_emits_qasm,
        test_two_body_density_density_runs_and_matches_hand_written_pauli,
        test_two_body_density_density_emits_qasm,
        test_mapping_provenance_records_name_and_qubit_count,
        test_two_body_mapping_provenance_records_qubit_count,
        test_boson_mapping_is_explicitly_diagnosed_not_silently_accepted,
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
