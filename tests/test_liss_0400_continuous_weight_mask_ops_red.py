"""AT-TDD Phase 1 Red: LISS-0400 `weight` / `mask` continuous ops.

Target: docs/architecture/adr/0204-continuous-lane-b-type-world.md /
docs/issues/LISS-0400-continuous-weight-mask-ops.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.continuous_field import ContinuousFieldValue  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.runtime.joint import Joint  # noqa: E402


def _codes(diagnostics) -> set[str]:
    return {str(d.get("code", "")) for d in diagnostics}


class _FakeContinuousFieldAdapter:
    def field(self, source: str, domain: str) -> str:
        return f"host-ref::{source}::{domain}"


_SOURCE_WEIGHT_MASK = """
package t
pub fn main() -> Unit {
    Continuous damage = field_from_host("damage_proxy_v1", "Omega")
    Continuous flood = field_from_host("inundation_v1", "Omega")
    Continuous impassable = field_from_host("road_block_field", "Omega")
    Continuous risk = weight(damage, flood)
    Continuous masked = mask(risk, impassable)
    state zone = |0>
    measure zone
}
"""


def test_weight_and_mask_compile_without_hard_gate_errors() -> None:
    compiled = compile_source(_SOURCE_WEIGHT_MASK)
    codes = _codes(compiled.diagnostics)
    assert "CONTINUOUS_ESCAPE_ERROR" not in codes
    assert "TYPE_NOT_STATE" not in codes


def test_weight_and_mask_do_not_false_positive_discard() -> None:
    """`damage`/`flood`/`risk`/`impassable` are all consumed by the next
    weight/mask call (ordinary linear move); only the final `masked` is
    genuinely unconsumed here and should be flagged.
    """
    compiled = compile_source(_SOURCE_WEIGHT_MASK)
    codes = _codes(compiled.diagnostics)
    assert "LINEAR_IMPLICIT_DISCARD" in codes
    # Confirm it is specifically `masked` being flagged, not an earlier
    # (wrongly-unconsumed) intermediate root.
    messages = " ".join(
        str(d.get("message", "")) for d in compiled.diagnostics
        if d.get("code") == "LINEAR_IMPLICIT_DISCARD"
    )
    assert "masked" in messages
    assert "damage" not in messages
    assert "flood" not in messages
    assert "risk" not in messages


def test_weight_composes_a_new_handle_referencing_its_inputs() -> None:
    compiled = compile_source(_SOURCE_WEIGHT_MASK)
    assert compiled.unit is not None, compiled.diagnostics
    binds = {
        s.names[0]: s.expr
        for s in compiled.unit.main.body.stmts
        if hasattr(s, "names")
    }

    evaluator = Evaluator(seed=0, continuous_field=_FakeContinuousFieldAdapter())
    joint = Joint.unit()
    for local_name in ("damage", "flood", "impassable"):
        joint = evaluator._bind_names(
            joint, [local_name], binds[local_name], logs=[], inspect_out=None
        )
    joint = evaluator._bind_names(joint, ["risk"], binds["risk"], logs=[], inspect_out=None)
    joint = evaluator._bind_names(joint, ["masked"], binds["masked"], logs=[], inspect_out=None)

    risk = evaluator.objects["risk"]
    masked = evaluator.objects["masked"]
    assert isinstance(risk, ContinuousFieldValue)
    assert risk.op == "weight"
    assert risk.inputs == (evaluator.objects["damage"], evaluator.objects["flood"])
    assert isinstance(masked, ContinuousFieldValue)
    assert masked.op == "mask"
    assert masked.inputs == (risk, evaluator.objects["impassable"])
    # Continuous composition never touches the Joint.
    assert joint.worlds == Joint.unit().worlds


def test_weight_accepts_optional_third_argument() -> None:
    source = """
package t
pub fn main() -> Unit {
    Continuous damage = field_from_host("damage_proxy_v1", "Omega")
    Continuous flood = field_from_host("inundation_v1", "Omega")
    Continuous fire = field_from_host("fire_index_v1", "Omega")
    Continuous risk = weight(damage, flood, fire)
    state zone = |0>
    measure zone
}
"""
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    dynamic_ok = _codes(compiled.diagnostics)
    assert "CONTINUOUS_ESCAPE_ERROR" not in dynamic_ok

    binds = {
        s.names[0]: s.expr
        for s in compiled.unit.main.body.stmts
        if hasattr(s, "names")
    }
    evaluator = Evaluator(seed=0, continuous_field=_FakeContinuousFieldAdapter())
    joint = Joint.unit()
    for local_name in ("damage", "flood", "fire"):
        joint = evaluator._bind_names(
            joint, [local_name], binds[local_name], logs=[], inspect_out=None
        )
    joint = evaluator._bind_names(joint, ["risk"], binds["risk"], logs=[], inspect_out=None)
    risk = evaluator.objects["risk"]
    assert len(risk.inputs) == 3
