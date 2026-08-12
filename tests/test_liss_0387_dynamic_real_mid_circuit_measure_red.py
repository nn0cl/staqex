"""AT-TDD Phase 1 Red: LISS-0387 real dynamic-lane mid-circuit measurement.

Target: docs/specs/staqex-dynamic-qpu-lane.md (LISS-0387 section, to be
synced at Green) / docs/architecture/adr/0200-dynamic-lane-real-kernel-execution.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import DynamicQpuStmt, KetLit, MatchStmt  # noqa: E402
from compiler.staqex.host_input_port import MappingHostInputAdapter  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.runtime.joint import Joint  # noqa: E402


_SOURCE_MEASURE_ONLY = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        State q = |0>
        Controller<Bit> bit = Measure q
        match bit {
            0 => { }
            1 => { }
        }
    }
    State<Int> observed = Coin()
    Measure observed
}
"""


def _codes(diagnostics) -> set[str]:
    return {str(d.get("code", "")) for d in diagnostics}


def test_measure_only_program_consistent_outcome_runs_to_completion() -> None:
    """Scenario: a supplied outcome consistent with the prepared state (q =
    |0>, outcome "0") lets execution proceed normally -- the Static tail
    (`observed = Coin(); Measure observed`) still produces a real sample.
    """
    compiled = compile_source(_SOURCE_MEASURE_ONLY)
    assert compiled.unit is not None

    host_input = MappingHostInputAdapter({"dynamic:bit": "0"})
    evaluator = Evaluator(seed=0, host_input=host_input)
    result = evaluator.run_unit(compiled.unit)

    assert result.measure is not None
    assert result.measure.vacuum is False


def test_measure_only_program_inconsistent_outcome_vacuums_the_run() -> None:
    """Scenario: real collapse checks consistency against amplitudes, not a
    bookkeeping label. `state q = |0>` deterministically prepares q = 0;
    supplying outcome "1" for the mid-circuit Measure is physically
    impossible (zero probability). A genuine Lueders projection
    (`project_coord`) must Vacuum the run -- a label-only implementation
    would accept any supplied outcome unconditionally and proceed normally.
    """
    compiled = compile_source(_SOURCE_MEASURE_ONLY)
    assert compiled.unit is not None

    host_input = MappingHostInputAdapter({"dynamic:bit": "1"})
    evaluator = Evaluator(seed=0, host_input=host_input)
    result = evaluator.run_unit(compiled.unit)

    assert result.measure is not None
    assert result.measure.vacuum is True, (
        "expected the physically-impossible supplied outcome to Vacuum the "
        "run via real project_coord collapse; a non-Vacuum result means "
        "the outcome was accepted as a label without checking amplitudes"
    )


_SOURCE_MATCH_REUSE = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        State q = |0>
        Controller<Bit> bit = Measure q
        match bit {
            0 => { apply(X, q) }
            1 => { }
        }
    }
    State<Int> observed = Coin()
    Measure observed
}
"""


def test_match_arm_reuse_applies_gate_for_real() -> None:
    """Scenario: post-Measure reuse inside a match arm actually evolves
    state (Decision 3), not a capability-flag bookkeeping decision.
    `apply(X, q)` inside the matching arm (bit=0, consistent with the
    prepared |0>) must flip q to a real 1 via the normal Call dispatch --
    exercised directly at the Joint boundary since block-end trace-out
    (Decision 5) removes q from the publicly observable result.
    """
    compiled = compile_source(_SOURCE_MATCH_REUSE)
    assert compiled.unit is not None
    dynamic_stmt = next(
        s for s in compiled.unit.main.body.stmts if isinstance(s, DynamicQpuStmt)
    )
    match_stmt = next(
        s for s in dynamic_stmt.body.stmts if isinstance(s, MatchStmt)
    )
    arm0 = next(a for a in match_stmt.arms if a.pattern == "0")

    evaluator = Evaluator(seed=0)
    joint = Joint.unit()
    joint = evaluator._bind_names(
        joint, ["q"], KetLit(label="0", span=dynamic_stmt.span), logs=[], inspect_out=None
    )
    joint = evaluator._run_dynamic_arm_body(joint, arm0.body.stmts)

    q_values = {world.assign.get("q") for world in joint.worlds}
    assert q_values == {1}, (
        f"expected apply(X, q) to flip q to 1 via real Call dispatch, got "
        f"{q_values!r}"
    )


def test_hir_dynamic_measure_bind_does_not_trigger_implicit_discard() -> None:
    """Controller<T> = Measure wire must be recognized as consuming `wire`
    for the linear-use checker (LISS-0387 Decision 4), not flagged as an
    implicit discard the way an untouched `state` var would be.
    """
    compiled = compile_source(_SOURCE_MEASURE_ONLY)
    codes = _codes(compiled.diagnostics)

    assert "LINEAR_IMPLICIT_DISCARD" not in codes
