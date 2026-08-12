"""AT-TDD: LISS-0376 -- the unitarity guard's quantum-lineage tracker
(`_expr_is_quantum`) recognizes a `superpose`-bound state, not just a
ket-bound one (was silently tracking a superpose-bound state as
non-quantum, so a subsequent non-unitary transform on it was never
checked).

Design decision: docs/issues/LISS-0376-unitarity-superpose-dispatch.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source  # noqa: E402

_BASELINE_KET_BOUND_SRC = """
package t
pub fn main() -> Unit {
    QubitRegister<1> register = system()
    State psi = |0>
    State bad = map(psi, x -> 0)
    measure bad
}
"""

_SUPERPOSE_BOUND_SRC = """
package t
pub fn main() -> Unit {
    QubitRegister<1> register = system()
    State control = |+>
    State psi = |0>
    State sp = superpose(control) { 0 -> psi, 1 -> psi }
    State bad = map(sp, x -> 0)
    measure bad
}
"""


def test_baseline_ket_bound_non_unitary_map_is_rejected() -> None:
    """Regression guard: the already-working ket-bound form must keep
    rejecting a bit-collapsing map."""
    compiled = compile_source(_BASELINE_KET_BOUND_SRC)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "NON_UNITARY_TRANSFORM_ERROR" in codes, compiled.diagnostics


def test_superpose_bound_non_unitary_map_is_rejected_the_same_way() -> None:
    """The identical non-unitary transform on a superpose-bound state
    must be rejected identically, not silently unchecked."""
    compiled = compile_source(_SUPERPOSE_BOUND_SRC)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "NON_UNITARY_TRANSFORM_ERROR" in codes, compiled.diagnostics
