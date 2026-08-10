"""AT-TDD Phase 1 Red: LISS-0401 `finiteize` Continuous-argument overload.

Target: docs/architecture/adr/0204-continuous-lane-b-type-world.md /
docs/issues/LISS-0401-finiteize-continuous-overload.md.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Mapping

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

    def discretize(
        self,
        value: ContinuousFieldValue,
        *,
        lo: float,
        hi: float,
        n_bins: int,
        seed: int | None,
    ) -> Mapping[Any, float]:
        return {i: 1.0 / n_bins for i in range(n_bins)}


def _binds(compiled) -> dict:
    return {
        s.names[0]: s.expr for s in compiled.unit.main.body.stmts if hasattr(s, "names")
    }


_SOURCE_LANE_A_UNCHANGED = """
package t
pub fn main() -> Unit {
    state x = finiteize(0.0, 1.0, 4, 100, 0)
    measure x
}
"""


def test_lane_a_finiteize_grammar_is_unaffected() -> None:
    """Regression guard: the existing positional (lo, hi, n_bins,
    n_samples[, seed]) grammar must still work byte-for-byte.
    """
    compiled = compile_source(_SOURCE_LANE_A_UNCHANGED)
    assert compiled.unit is not None, compiled.diagnostics
    evaluator = Evaluator(seed=0)
    joint = Joint.unit()
    bind_stmt = compiled.unit.main.body.stmts[0]
    joint = evaluator._bind_names(
        joint, ["x"], bind_stmt.expr, logs=[], inspect_out=None
    )
    assert joint.worlds, "Lane A finiteize must still bind a real distribution"


_SOURCE_CONTINUOUS_FINITEIZE = """
package t
pub fn main() -> Unit {
    Continuous damage = field_from_host("damage_proxy_v1", "Omega")
    Continuous flood = field_from_host("inundation_v1", "Omega")
    Continuous impassable = field_from_host("road_block_field", "Omega")
    Continuous risk = weight(damage, flood)
    Continuous masked = mask(risk, impassable)
    state zone = finiteize(masked, 0.0, 1.0, 3, 0)
    measure zone
}
"""


def test_finiteize_accepts_a_continuous_value_and_binds_finite_state() -> None:
    compiled = compile_source(_SOURCE_CONTINUOUS_FINITEIZE)
    assert compiled.unit is not None, compiled.diagnostics
    binds = _binds(compiled)

    evaluator = Evaluator(seed=0, continuous_field=_FakeContinuousFieldAdapter())
    joint = Joint.unit()
    for local_name in ("damage", "flood", "impassable"):
        joint = evaluator._bind_names(
            joint, [local_name], binds[local_name], logs=[], inspect_out=None
        )
    joint = evaluator._bind_names(joint, ["risk"], binds["risk"], logs=[], inspect_out=None)
    joint = evaluator._bind_names(joint, ["masked"], binds["masked"], logs=[], inspect_out=None)
    joint = evaluator._bind_names(joint, ["zone"], binds["zone"], logs=[], inspect_out=None)

    assert joint.worlds, "finiteize(Continuous, ...) must bind a real finite distribution"
    zone_values = {w.assign.get("zone") for w in joint.worlds}
    assert zone_values == {0, 1, 2}


def test_finiteize_continuous_provenance_carries_pipeline_and_discretization() -> None:
    compiled = compile_source(_SOURCE_CONTINUOUS_FINITEIZE)
    assert compiled.unit is not None, compiled.diagnostics
    binds = _binds(compiled)

    evaluator = Evaluator(seed=0, continuous_field=_FakeContinuousFieldAdapter())
    joint = Joint.unit()
    for local_name in ("damage", "flood", "impassable"):
        joint = evaluator._bind_names(
            joint, [local_name], binds[local_name], logs=[], inspect_out=None
        )
    joint = evaluator._bind_names(joint, ["risk"], binds["risk"], logs=[], inspect_out=None)
    joint = evaluator._bind_names(joint, ["masked"], binds["masked"], logs=[], inspect_out=None)
    evaluator._bind_names(joint, ["zone"], binds["zone"], logs=[], inspect_out=None)

    prov = evaluator.objects["__finiteize_prov_zone"]
    assert prov["continuous_pipeline"] == ("weight", "mask")
    assert prov["discretization"]["basis"] == "EqualWidthHistogram"
    assert prov["discretization"]["resolution"] == 3


def test_continuous_root_consumed_by_finiteize_does_not_false_positive_discard() -> None:
    compiled = compile_source(_SOURCE_CONTINUOUS_FINITEIZE)
    codes = _codes(compiled.diagnostics)
    assert "LINEAR_IMPLICIT_DISCARD" not in codes


_SOURCE_DOUBLE_FINITEIZE = """
package t
pub fn main() -> Unit {
    Continuous damage = field_from_host("damage_proxy_v1", "Omega")
    state a = finiteize(damage, 0.0, 1.0, 2, 0)
    state b = finiteize(damage, 0.0, 1.0, 2, 0)
    measure a
}
"""


def test_second_finiteize_of_an_already_consumed_continuous_root_is_rejected() -> None:
    """ADR 0204 Decision 5: single-consumption only (CH-field-fork out of
    scope) -- a second finiteize of the same root must not be silently
    accepted as a free second consumption.
    """
    compiled = compile_source(_SOURCE_DOUBLE_FINITEIZE)
    codes = _codes(compiled.diagnostics)
    assert "LINEAR_DUPLICATE_USE" in codes
