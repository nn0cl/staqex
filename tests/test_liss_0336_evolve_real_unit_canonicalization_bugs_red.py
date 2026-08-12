"""AT-TDD: LISS-0336 -- fix two real-unit `evolve` bugs found while doing
WP-0095 work unit 6 (A11) design intake.

Bug 1: sparse_pauli.py's `_coalesce` uses an absolute 1e-15 epsilon that
silently zeroes real Joule-scale (eV ~ 1.6e-19 J) Hamiltonian
coefficients, turning `evolve` into a no-op identity transform for any
multi-qubit-Pauli-Operator built directly from `X[i]`/`Z[i]` atoms.

Bug 2: evaluator.py's `_hamiltonian_evolve_one_step` never canonicalizes
the evolve duration from its declared Time unit (fs/ps/ns) to seconds --
it reads the raw declared magnitude and uses it directly as seconds.

Both confirmed live via instrumented tracing during design intake; see
docs/issues/LISS-0336-evolve-real-unit-canonicalization-bugs.md.
"""

from __future__ import annotations

import cmath
import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import OpBin, OpPauli, OpVar, Span  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.runtime.sparse_pauli import compile_sparse_pauli  # noqa: E402

_EV_TO_J = 1.602176634e-19
_FS_TO_S = 1e-15
_HBAR_SI = 1.054571817e-34


def test_coalesce_does_not_drop_real_joule_scale_coefficients() -> None:
    sp = Span(line=1, col=1)
    op = OpBin(
        op="*",
        lhs=OpVar(name="e", span=sp),
        rhs=OpPauli(kind="X", site=None, span=sp),
        span=sp,
    )
    scalars = {"e": _EV_TO_J}
    terms = compile_sparse_pauli(op, env={}, scalars=scalars, n_qubits=1)
    assert len(terms) == 1, "real eV-scale coefficient must not be coalesced to zero"
    assert abs(terms[0].coeff - _EV_TO_J) < 1e-30


def test_evolve_duration_is_canonicalized_to_seconds_not_raw_magnitude() -> None:
    src = """
package t
pub fn main() -> Unit {
    Energy e = 1.0.eV to J
    Time dur = 1.0.fs
    State psi = |0>
    Operator H = e * Z
    State psi = evolve { psi under H for dur }.run()
    measure psi
}
"""
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = Evaluator(seed=0).run_unit(compiled.unit, stdout=io.StringIO())

    # H|0> = e * Z|0> = e|0> (Z eigenvalue +1 on |0>), so the correct
    # evolved amplitude is exp(-i * e * t_seconds / hbar) with
    # t_seconds = 1.0 fs canonicalized = 1e-15 s -- not the raw "1.0".
    theta_correct = _EV_TO_J * _FS_TO_S / _HBAR_SI
    expected = cmath.exp(-1j * theta_correct)

    amp = result.joint.worlds[0].amp
    assert abs(amp - expected) < 1e-6, (amp, expected, theta_correct)
