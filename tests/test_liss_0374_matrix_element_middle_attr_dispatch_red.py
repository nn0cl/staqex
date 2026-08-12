"""AT-TDD: LISS-0374 -- the matrix-element middle type check
(`_check_matrix_element_middle`) covers a class-method callee, not just
a bare Var name (was silently accepting `<0|b.getPsi|1>` when
`getPsi` returns State, even though the equivalent bare-name form
`<0|psi|1>` already correctly rejects it).

Design decision: docs/issues/LISS-0374-matrix-element-middle-attr-dispatch.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source  # noqa: E402

_BASELINE_BARE_VAR_SRC = """
package t
pub fn main() -> Unit {
    QubitRegister<1> register = system()
    State psi = |0>
    Float x = inner(|0>, psi(|1>))
    measure psi
}
"""

_CLASS_METHOD_MIDDLE_SRC = """
package t
class Box {
    val psi: State<Qubit>

    fn init(p: State<Qubit>) {
        this.psi = p
    }

    fn getPsi(x: State<Qubit>) -> State<Qubit> {
        return this.psi
    }
}
pub fn main() -> Unit {
    QubitRegister<1> register = system()
    State seed = |0>
    Box b = Box(seed)
    Float x = inner(|0>, b.getPsi(|1>))
    measure seed
}
"""


def test_baseline_bare_var_middle_is_rejected() -> None:
    """Regression guard: the already-working bare-name form must keep
    rejecting a State-kind middle."""
    compiled = compile_source(_BASELINE_BARE_VAR_SRC)
    assert not compiled.ok
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "OPERATOR_ALGEBRA_TYPE_ERROR" in codes, compiled.diagnostics


def test_class_method_middle_is_rejected_the_same_way() -> None:
    """The equivalent-shaped misuse through a class method returning
    State must be rejected identically, not silently accepted."""
    compiled = compile_source(_CLASS_METHOD_MIDDLE_SRC)
    assert not compiled.ok
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "OPERATOR_ALGEBRA_TYPE_ERROR" in codes, compiled.diagnostics
