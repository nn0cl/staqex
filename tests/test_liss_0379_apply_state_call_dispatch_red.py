"""AT-TDD: LISS-0379 -- apply(ch, State) MIXED_STATE_TYPE_ERROR covers
a Call returning State, not just a bare Var.

Design decision: docs/issues/LISS-0379-apply-state-call-dispatch.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source  # noqa: E402


def _codes(result) -> set[str]:
    return {diagnostic.get("code") for diagnostic in result.diagnostics}


_VAR_SRC = """
package t
pub fn main() -> Unit {
    State<Qubit> psi = |0>
    Channel ch = KrausChannel([[[1.0, 0.0], [0.0, 1.0]]])
    DensityState<Qubit> rho = apply(ch, psi)
    Measure rho
}
"""

_CALL_SRC = """
package t
fn id(s: State<Qubit>) -> State<Qubit> {
    return s
}
pub fn main() -> Unit {
    State<Qubit> psi = |0>
    Channel ch = KrausChannel([[[1.0, 0.0], [0.0, 1.0]]])
    DensityState<Qubit> rho = apply(ch, id(psi))
    Measure rho
}
"""


def test_apply_state_var_is_rejected() -> None:
    compiled = compile_source(_VAR_SRC)
    assert "MIXED_STATE_TYPE_ERROR" in _codes(compiled), compiled.diagnostics


def test_apply_state_call_is_rejected_the_same_way() -> None:
    compiled = compile_source(_CALL_SRC)
    assert "MIXED_STATE_TYPE_ERROR" in _codes(compiled), compiled.diagnostics
