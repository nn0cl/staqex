"""AT-TDD Phase 1 Red: LISS-0011 multi-qubit symbolic Lindblad operators.

Reproduces the gap recorded in LISS-0011's "Completed slice boundary":
"General operator algebra... remain deferred follow-ups." Direct
investigation (2026-07-25, after the LISS-0051 parser fix) found the
remaining gap is narrow: `runtime/evaluator.py`'s
`_resolve_lindblad_hamiltonian` / `_resolve_lindblad_jumps` hardcode
`n_qubits=1` via `_compile_one_qubit_operator`, even though `DensityState`
construction and `runtime.lindblad.evolve_lindblad` (the RK4 integrator)
are already fully general over matrix dimension. A 2-qubit symbolic
Hamiltonian or jump operator fails with
`Pauli site 1 out of range for 1 qubits` -- not because the runtime can't
handle it, but because the resolver never asks for more than 1 qubit.

Expected to fail until Phase 2 Green infers the qubit count from the
DensityState source instead of hardcoding it.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import run_source  # noqa: E402


def _main(body: str) -> str:
    return f"""
    package t
    pub fn main() -> Unit {{
        {body}
    }}
    """


_TWO_QUBIT_HAMILTONIAN_PROGRAM = _main(
    """
    Operator H = X[0] * X[1]
    DensityState<Qubit> rho = DensityState(RawMatrix([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0]
    ]))
    DensityState<Qubit> evolved = lindblad(rho, H, JumpSet([]), 0.1)
    Measure evolved
    """
)


def test_two_qubit_symbolic_hamiltonian_matches_analytic_reference() -> None:
    """H = X[0]*X[1] pairs |00> <-> |11>; starting in |00>, this is exactly
    a single-qubit X rotation restricted to a 2D subspace, so
    P(|11>) = sin^2(t) and P(|00>) = cos^2(t) -- an exact, independently
    verifiable reference, not just "did it run"."""
    result = run_source(_TWO_QUBIT_HAMILTONIAN_PROGRAM)

    assert result.status == "succeeded", result.diagnostics
    marginal = result.measurements[0].marginal
    assert abs(marginal.get(3, 0.0) - math.sin(0.1) ** 2) < 1e-6
    assert abs(marginal.get(0, 0.0) - math.cos(0.1) ** 2) < 1e-6
    assert marginal.get(1, 0.0) < 1e-9
    assert marginal.get(2, 0.0) < 1e-9


_TWO_QUBIT_JUMP_PROGRAM = _main(
    """
    Operator H = X[0] * X[1]
    Operator decay = X[0] * X[1]
    DensityState<Qubit> rho = DensityState(RawMatrix([
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0]
    ]))
    DensityState<Qubit> evolved = lindblad(rho, H, JumpSet([decay]), 0.1)
    Measure evolved
    """
)


def test_two_qubit_symbolic_jump_operator_runs() -> None:
    result = run_source(_TWO_QUBIT_JUMP_PROGRAM)

    assert result.status == "succeeded", result.diagnostics
    marginal = result.measurements[0].marginal
    assert abs(sum(marginal.values()) - 1.0) < 1e-6


def test_one_qubit_symbolic_hamiltonian_still_works() -> None:
    """Regression pin: the already-shipped 1-qubit slice (LISS-0011/0040)
    must be unaffected by inferring qubit count instead of hardcoding it."""
    result = run_source(
        _main(
            """
            Operator H = X
            DensityState<Qubit> rho = DensityState(
                RawMatrix([[1.0, 0.0], [0.0, 0.0]])
            )
            DensityState<Qubit> evolved = lindblad(rho, H, [], 0.1)
            Measure evolved
            """
        )
    )

    assert result.status == "succeeded", result.diagnostics
    assert result.measurements[0].marginal[1] > 0.009
    assert result.measurements[0].marginal[1] < 0.011


if __name__ == "__main__":
    tests = [
        test_two_qubit_symbolic_hamiltonian_matches_analytic_reference,
        test_two_qubit_symbolic_jump_operator_runs,
        test_one_qubit_symbolic_hamiltonian_still_works,
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
