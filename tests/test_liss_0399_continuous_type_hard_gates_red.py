"""AT-TDD Phase 1 Red: LISS-0399 `Continuous<T>` type + `ContinuousFieldPort`
+ hard gates.

Target: docs/architecture/adr/0204-continuous-lane-b-type-world.md /
docs/issues/LISS-0399-continuous-type-hard-gates.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.runtime.joint import Joint  # noqa: E402


def _codes(diagnostics) -> set[str]:
    return {str(d.get("code", "")) for d in diagnostics}


_SOURCE_FIELD_ONLY = """
package t
pub fn main() -> Unit {
    Continuous damage = field_from_host("damage_proxy_v1", "Omega")
    state zone = |0>
    measure zone
}
"""


def test_continuous_bind_is_not_confused_with_state() -> None:
    """A `Continuous` bind must not be treated as a `State` bind -- no
    LINEAR discard confusion, no spurious quantum-carrier diagnostics for
    `damage` itself (its own discard status is covered by a separate
    test below).
    """
    compiled = compile_source(_SOURCE_FIELD_ONLY)
    assert compiled.unit is not None, compiled.diagnostics


_SOURCE_FIELD_UNCONSUMED = """
package t
pub fn main() -> Unit {
    Continuous damage = field_from_host("damage_proxy_v1", "Omega")
    state zone = |0>
    measure zone
}
"""


def test_unconsumed_continuous_root_is_flagged_discarded() -> None:
    """Scenario: `damage` is introduced but never finiteized (finiteize
    does not exist until LISS-0401) -- must be flagged
    LINEAR_IMPLICIT_DISCARD, same as an untouched `state` root.
    """
    compiled = compile_source(_SOURCE_FIELD_UNCONSUMED)
    codes = _codes(compiled.diagnostics)
    assert "LINEAR_IMPLICIT_DISCARD" in codes


_SOURCE_MEASURE_CONTINUOUS = """
package t
pub fn main() -> Unit {
    Continuous damage = field_from_host("damage_proxy_v1", "Omega")
    measure damage
}
"""


def test_measuring_a_continuous_value_fails_closed() -> None:
    """Scenario: `measure damage` where `damage` is Continuous must be
    rejected. Discovered during Green implementation: the top-level
    `measure` statement already calls the existing, generic
    `_assert_is_state` allowlist check (`TYPE_NOT_STATE`) -- once
    `Continuous` is a real, distinct `Ty.kind` not in that allowlist, this
    gate fires for free, no new diagnostic code needed here. (The earlier
    Plan-stage probe that found `evolve`/`apply` permissive used the
    *dynamic-lane* Controller path specifically, a separately laxer code
    path -- top-level/main-lane checking is stricter, confirmed here.)
    """
    compiled = compile_source(_SOURCE_MEASURE_CONTINUOUS)
    codes = _codes(compiled.diagnostics)
    assert "TYPE_NOT_STATE" in codes


_SOURCE_EVOLVE_CONTINUOUS = """
package t
pub fn main() -> Unit {
    Continuous damage = field_from_host("damage_proxy_v1", "Omega")
    state r = evolve { damage under H for 1.0 }.run()
    measure r
}
"""


def test_evolving_a_continuous_value_fails_closed() -> None:
    """Scenario: `evolve { damage under H for 1.0 }.run()` must be
    rejected. Same free-gate discovery as the measure test above:
    `_assert_is_state` already rejects the bind result's non-State kind.
    """
    compiled = compile_source(_SOURCE_EVOLVE_CONTINUOUS)
    codes = _codes(compiled.diagnostics)
    assert "TYPE_NOT_STATE" in codes


_SOURCE_APPLY_CONTINUOUS = """
package t
pub fn main() -> Unit {
    Continuous damage = field_from_host("damage_proxy_v1", "Omega")
    apply(X, damage)
    state zone = |0>
    measure zone
}
"""


def test_applying_a_gate_to_a_continuous_value_fails_closed() -> None:
    """Scenario: `apply(X, damage)` must be rejected with
    CONTINUOUS_ESCAPE_ERROR -- confirmed via direct compilation
    (Controller stand-in) that `apply` accepts a non-wire operand
    silently today.
    """
    compiled = compile_source(_SOURCE_APPLY_CONTINUOUS)
    codes = _codes(compiled.diagnostics)
    assert "CONTINUOUS_ESCAPE_ERROR" in codes


class _FakeContinuousFieldAdapter:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def field(self, source: str, domain: str) -> str:
        self.calls.append((source, domain))
        return f"host-ref::{source}::{domain}"


def test_field_from_host_dispatches_through_the_port() -> None:
    """Scenario: `field_from_host(source, domain)` calls the injected
    ContinuousFieldPort exactly once and binds an opaque Kernel-side
    handle (never a Joint World) -- the Joint itself is unchanged.
    """
    from compiler.staqex.continuous_field import ContinuousFieldValue

    compiled = compile_source(_SOURCE_FIELD_ONLY)
    assert compiled.unit is not None, compiled.diagnostics
    bind_stmt = compiled.unit.main.body.stmts[0]

    fake_port = _FakeContinuousFieldAdapter()
    evaluator = Evaluator(seed=0, continuous_field=fake_port)
    joint = Joint.unit()
    out = evaluator._bind_names(joint, ["damage"], bind_stmt.expr, logs=[], inspect_out=None)

    assert fake_port.calls == [("damage_proxy_v1", "Omega")]
    assert out.worlds == joint.worlds, "Continuous binding must not touch the Joint"
    handle = evaluator.objects["damage"]
    assert isinstance(handle, ContinuousFieldValue)
    assert handle.op == "field_from_host"


def test_field_from_host_without_port_fails_closed() -> None:
    """No ContinuousFieldPort configured -> clear KernelError, not a
    crash or silent no-op.
    """
    from compiler.staqex.runtime.evaluator import KernelError

    compiled = compile_source(_SOURCE_FIELD_ONLY)
    assert compiled.unit is not None, compiled.diagnostics
    bind_stmt = compiled.unit.main.body.stmts[0]

    evaluator = Evaluator(seed=0)
    joint = Joint.unit()
    try:
        evaluator._bind_names(joint, ["damage"], bind_stmt.expr, logs=[], inspect_out=None)
        raised = False
    except KernelError:
        raised = True
    assert raised
