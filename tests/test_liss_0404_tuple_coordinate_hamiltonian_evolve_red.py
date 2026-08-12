"""AT-TDD Phase 1 Red: LISS-0404 Pauli-term Hamiltonian evolution on
tuple-valued coordinates.

Target: docs/architecture/adr/0205-tuple-coordinate-register-bridge.md /
docs/issues/LISS-0404-tuple-coordinate-hamiltonian-evolve.md.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator, KernelError  # noqa: E402
from compiler.staqex.runtime.joint import Joint, World  # noqa: E402


_SOURCE_H = """
package t
pub fn main() -> Unit {
    Energy scale = 1.0.eV to J
    Operator H_raw = 1.0 * Z[0] + 1.0 * X[0] + 1.0 * (Z[0] * Z[1])
    Operator H = scale * H_raw
    state q0 = |0>
    state q1 = |+>
    Time dur = 0.6.fs
    state (q0, q1) = evolve { (q0, q1) under H for dur }.run()
    measure q0 tracing_out q1
}
"""


def _build_h_terms(evaluator: Evaluator):
    from compiler.staqex.runtime.hamiltonian import op_n_qubits
    from compiler.staqex.runtime.sparse_pauli import compile_sparse_pauli

    op_ast = evaluator.operators["H"]
    nq = op_n_qubits(op_ast, evaluator.operators, evaluator.scalars)
    terms = compile_sparse_pauli(
        op_ast, env=evaluator.operators, scalars=evaluator.scalars, n_qubits=nq
    )
    return nq, terms


def test_evolve_under_tuple_coordinate_matches_separate_coordinates_exactly() -> None:
    """The ADR 0205 cross-check, promoted to an automated regression test:
    evolving |0>|+> under the same Hamiltonian via the existing
    nq-separate-names path and via a tuple-valued single coordinate must
    give identical results to float precision.
    """
    compiled = compile_source(_SOURCE_H)
    assert compiled.unit is not None, compiled.diagnostics
    evaluator = Evaluator(seed=0)
    result = evaluator.run_unit(compiled.unit)
    assert result.measure is not None
    existing_marginal = result.measure.marginal

    # Build the identical Hamiltonian terms via the same source, then
    # evolve a hand-built tuple-valued coordinate carrying the same
    # |0>|+> initial state (amp 1/sqrt(2) on (0,0) and (0,1)).
    evaluator2 = Evaluator(seed=0)
    evaluator2.run_unit(compiled.unit)  # populate evaluator2.operators["H"]
    nq, terms = _build_h_terms(evaluator2)
    assert nq == 2

    s = 1 / math.sqrt(2)
    joint = Joint(
        worlds=[
            World(assign={"psi": (0, 0)}, amp=s + 0j),
            World(assign={"psi": (0, 1)}, amp=s + 0j),
        ]
    )
    dur_s = 0.6e-15  # 0.6 fs in seconds
    out = evaluator2._hamiltonian_evolve_tuple_coordinate(joint, "psi", nq, terms, dur_s)

    tuple_marginal = {0: 0.0, 1: 0.0}
    for w in out.worlds:
        tuple_marginal[w.assign["psi"][0]] += abs(w.amp) ** 2

    # Floating-point summation order differs slightly between this test's
    # hand-built World list and the real compile->run pipeline (last-digit
    # noise only, ~1e-16 relative) -- math.isclose, not exact equality.
    assert math.isclose(tuple_marginal[0], existing_marginal[0], rel_tol=1e-9)
    assert math.isclose(tuple_marginal[1], existing_marginal[1], rel_tol=1e-9)


def test_evolve_under_tuple_coordinate_dispatches_from_source() -> None:
    """The full end-to-end source-level path: evolve psi under H where
    psi is a tuple-valued coordinate from prepare_selection.
    """
    source = """
package t
pub fn main() -> Unit {
    Energy scale = 1.0.eV to J
    Operator H_raw = 1.0 * Z[0] + 1.0 * X[0] + 1.0 * (Z[0] * Z[1])
    Operator H = scale * H_raw
    state psi = prepare_selection(2)
    state psi = evolve { psi under H for 0.6.fs }.run()
    measure psi
}
"""
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    evaluator = Evaluator(seed=0)
    result = evaluator.run_unit(compiled.unit)
    assert result.measure is not None
    assert result.measure.vacuum is False
    assert isinstance(result.measure.value, tuple)
    assert len(result.measure.value) == 2
    # Not the untouched uniform distribution -- the Hamiltonian must have
    # actually redistributed amplitude, not been silently ignored.
    assert len(result.measure.marginal) > 0
    uniform = {k: 0.25 for k in ((0, 0), (0, 1), (1, 0), (1, 1))}
    assert result.measure.marginal != uniform


def test_tuple_width_mismatch_fails_closed() -> None:
    """A tuple coordinate whose width doesn't match the Hamiltonian's own
    inferred qubit count must fail closed, not crash or silently truncate.
    """
    source = """
package t
pub fn main() -> Unit {
    Energy scale = 1.0.eV to J
    Operator H_raw = 1.0 * Z[0] + 1.0 * X[0] + 1.0 * (Z[0] * Z[1])
    Operator H = scale * H_raw
    state psi = prepare_selection(3)
    state psi = evolve { psi under H for 0.6.fs }.run()
    measure psi
}
"""
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    evaluator = Evaluator(seed=0)
    raised = False
    try:
        evaluator.run_unit(compiled.unit)
    except KernelError:
        raised = True
    assert raised


def test_existing_separate_coordinate_evolve_is_unaffected() -> None:
    """Regression guard: the existing nq-separate-names evolve path must
    remain byte-for-byte unaffected by this Issue.
    """
    compiled = compile_source(_SOURCE_H)
    assert compiled.unit is not None, compiled.diagnostics
    evaluator = Evaluator(seed=0)
    result = evaluator.run_unit(compiled.unit)
    assert result.measure is not None
    assert math.isclose(result.measure.marginal[0], 0.6078963648762783, rel_tol=1e-9)
    assert math.isclose(result.measure.marginal[1], 0.39210363512372154, rel_tol=1e-9)
