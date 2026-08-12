"""AT-TDD: LISS-0375 -- the ADR 0045 NESTED_WHEN_ERROR static guard
covers a `mix` reachable through a `*|*` tensor product, not just the
directly-nested form (was silently bypassable when the nested `mix`
was wrapped in a tensor expression).

Design decision: docs/issues/LISS-0375-nested-when-tensor-dispatch.md
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source  # noqa: E402

_DIRECT_SRC = """
package t
pub fn main() -> Unit {
    QubitRegister<1> register = system()
    Bit c = 0
    Bit d = 0
    State bad = mix (c) { 0 -> mix (d) {0 -> |0>, else -> |1>}, else -> |0> }
    measure bad
}
"""

_TENSOR_WRAPPED_SRC = """
package t
pub fn main() -> Unit {
    QubitRegister<2> register = system()
    Bit c = 0
    Bit d = 0
    State a = |0>
    State ab = a *|* (mix (c) { 0 -> mix (d) {0 -> |0>, else -> |1>}, else -> |0> })
    measure ab
}
"""


def test_direct_nested_mix_is_rejected() -> None:
    """Regression guard: the already-working direct form must keep
    rejecting a nested mix."""
    compiled = compile_source(_DIRECT_SRC)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "NESTED_WHEN_ERROR" in codes, compiled.diagnostics


def test_tensor_wrapped_nested_mix_is_rejected_the_same_way() -> None:
    """The identical coherence violation, reached only through a *|*
    tensor product, must be rejected identically, not silently
    bypassed."""
    compiled = compile_source(_TENSOR_WRAPPED_SRC)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "NESTED_WHEN_ERROR" in codes, compiled.diagnostics
