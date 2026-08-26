"""AT-TDD: LISS-0330 real hbar Kernel primitive (WP-0095 work unit 1,
ADR 0195).

Verifies expm_ih/expm_ih_apply against a hand-computed closed-form
expected value (diagonal Hamiltonian eigenvalue phase), independent of
the Kernel's own Taylor-series matrix-exponential algorithm -- not a
self-consistency check.
"""

from __future__ import annotations

import cmath
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.runtime.matrix import expm_ih  # noqa: E402
from compiler.staqex.runtime.sparse_pauli import (  # noqa: E402
    PauliTerm,
    expm_ih_apply,
)
from compiler.staqex.stdlib.prelude import HBAR_SI, PRELUDE_CONSTANTS  # noqa: E402

_EV_TO_J = 1.602176634e-19
_FS_TO_S = 1e-15


def test_hbar_matches_codata_2018() -> None:
    assert HBAR_SI == 1.054571817e-34
    assert PRELUDE_CONSTANTS["hbar"] == HBAR_SI


def test_expm_ih_uses_real_hbar_not_natural_units() -> None:
    energy_gap_j = 1.0 * _EV_TO_J  # a real, literature-plausible gap
    half = energy_gap_j / 2.0
    t_seconds = 1.0 * _FS_TO_S

    h = [[complex(half), 0j], [0j, complex(-half)]]
    u = expm_ih(h, t_seconds)

    theta = half * t_seconds / HBAR_SI
    expected_00 = cmath.exp(-1j * theta)
    expected_11 = cmath.exp(1j * theta)

    assert abs(u[0][0] - expected_00) < 1e-9
    assert abs(u[1][1] - expected_11) < 1e-9
    assert abs(u[0][1]) < 1e-12
    assert abs(u[1][0]) < 1e-12
    # Confirms this is NOT the old natural-units (hbar = 1) formula --
    # that would give phase ~1e-19 * 1e-15 ~= 1e-34 (numerically ~1),
    # not the real ~1.5 rad this real hbar division produces.
    assert abs(theta) > 0.1


def test_sparse_expm_ih_apply_uses_real_hbar() -> None:
    energy_gap_j = 1.0 * _EV_TO_J
    half = energy_gap_j / 2.0
    t_seconds = 1.0 * _FS_TO_S

    terms = [PauliTerm(coeff=complex(half), kinds=("Z",))]
    vec = [1.0 + 0j, 0.0 + 0j]  # |0>, a Z eigenstate (+1)

    out = expm_ih_apply(terms, t_seconds, vec)

    theta = half * t_seconds / HBAR_SI
    expected = cmath.exp(-1j * theta)
    assert abs(out[0] - expected) < 1e-9
    assert abs(out[1]) < 1e-12


def test_unresolved_unit_fails_closed() -> None:
    from compiler.staqex.host import run_source

    src = """
package t
pub fn main() -> Unit {
    Float e = 1.0
    Operator H = e * Z
    State psi = |0>
    State psi = Evolve { psi under H for 1.0 }.run()
    Measure psi
}
"""
    result = run_source(src, settings={"target": "local", "seed": 0})

    assert result.status == "failed"
    codes = {d.get("code") for d in result.diagnostics}
    assert "EVOLVE_UNRESOLVED_UNIT_ERROR" in codes
