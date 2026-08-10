"""AT-TDD Phase 1 Red: LISS-0395 dynamic-lane arm-body statement
unification (fixes arm-only wire leak; enables chained mid-circuit
measurement inside a `match` arm).

Target: docs/specs/staqex-dynamic-qpu-lane.md (LISS-0395 section) /
docs/issues/LISS-0395-dynamic-lane-arm-body-unification.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import DynamicQpuStmt, KetLit  # noqa: E402
from compiler.staqex.host import submit_source  # noqa: E402
from compiler.staqex.host_input_port import MappingHostInputAdapter  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.runtime.joint import Joint  # noqa: E402


def _codes(diagnostics) -> set[str]:
    return {str(d.get("code", "")) for d in diagnostics}


_SOURCE_ARM_ONLY_WIRE = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        state q = |0>
        state r = |0>
        Controller<Bit> bit = measure q
        match bit {
            0 => { reset r }
            1 => { }
        }
    }
    State<Int> observed = coin()
    measure observed
}
"""


def test_wire_only_touched_inside_arm_is_traced_out_at_block_end() -> None:
    """Scenario 1: `r` is introduced at the top level but only ever
    `reset` *inside* a match arm -- never top-level-measured or
    top-level-reset. Confirmed by direct execution (see LISS-0395 Plan
    Design verification point 1) that today `dynamically_measured` never
    learns about `r`, so the block-end trace_out loop skips it and it
    leaks into the surrounding Joint.
    """
    compiled = compile_source(_SOURCE_ARM_ONLY_WIRE)
    assert compiled.unit is not None
    dynamic_stmt = next(
        s for s in compiled.unit.main.body.stmts if isinstance(s, DynamicQpuStmt)
    )

    host_input = MappingHostInputAdapter({"dynamic:bit": "0"})
    evaluator = Evaluator(seed=0, host_input=host_input)
    joint = Joint.unit()
    joint = evaluator._bind_names(
        joint, ["q"], KetLit(label="0", span=dynamic_stmt.span), logs=[], inspect_out=None
    )
    joint = evaluator._bind_names(
        joint, ["r"], KetLit(label="0", span=dynamic_stmt.span), logs=[], inspect_out=None
    )
    out = evaluator._run_dynamic_qpu_block(joint, dynamic_stmt, logs=[], inspect_out=None)

    assert all("r" not in world.assign for world in out.worlds), (
        "expected `r` to be traced out at dynamic-block end even though it "
        "was only ever touched inside a match arm; found it still present "
        f"in {[w.assign for w in out.worlds]!r}"
    )


_SOURCE_CHAINED_MEASURE = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        state q = |0>
        state q2 = |0>
        Controller<Bit> bit = measure q
        match bit {
            0 => {
                Controller<Bit> bit2 = measure q2
                match bit2 {
                    0 => { }
                    1 => { }
                }
            }
            1 => { }
        }
    }
    State<Int> observed = coin()
    measure observed
}
"""


def test_chained_measure_inside_arm_runs_without_kernel_error() -> None:
    """Scenario 2: a second Controller-measure written inside a match arm,
    followed by a nested match dispatching on it, must genuinely execute
    -- not raise `KernelError("cannot bind expr MeasureExpr")` the way it
    does today (confirmed in Plan Design verification point 2). A
    Host-supplied outcome for `bit2` consistent with the prepared `q2 =
    |0>` state must let the run succeed.
    """
    job = submit_source(
        _SOURCE_CHAINED_MEASURE,
        settings={
            "dynamic_fake_profile": "SIM0_EXACT",
            "dynamic_supplied_outcomes": {"bit": "0", "bit2": "0"},
        },
    )
    result = job.result()

    assert result.status == "succeeded", (
        f"expected the chained measure to execute for real instead of "
        f"raising KernelError; got status={result.status!r}"
    )
    assert result.dynamic_trace is not None
    assert result.dynamic_trace.physical_outcome_confirmed is True


def test_chained_measure_inconsistent_outcome_vacuums_for_real() -> None:
    """Scenario 3: the chained measure must be a real `project_coord`
    collapse, not a bookkeeping label -- supplying "1" for `bit2` is
    physically impossible against the prepared `q2 = |0>`, so the run must
    vacuum (physical_outcome_confirmed=False), proving real collapse
    rather than label acceptance.
    """
    job = submit_source(
        _SOURCE_CHAINED_MEASURE,
        settings={
            "dynamic_fake_profile": "SIM0_EXACT",
            "dynamic_supplied_outcomes": {"bit": "0", "bit2": "1"},
        },
    )
    result = job.result()

    assert result.status == "succeeded"
    assert result.dynamic_trace is not None
    assert result.dynamic_trace.physical_outcome_confirmed is False, (
        "expected the physically-impossible bit2 outcome to vacuum the run "
        "via a real project_coord collapse of q2"
    )


_SOURCE_CHAINED_MEASURE_NO_DISCARD = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        state q = |0>
        state q2 = |0>
        Controller<Bit> bit = measure q
        match bit {
            0 => { Controller<Bit> bit2 = measure q2 }
            1 => { }
        }
    }
    State<Int> observed = coin()
    measure observed
}
"""


def test_hir_controller_measure_inside_arm_does_not_false_positive_discard() -> None:
    """Scenario 4: once `hir.py` recognizes a Controller-measure inside a
    match arm as consuming its wire (mirroring the existing top-level
    treatment), a measured-and-untouched-again `q2` must NOT be flagged as
    LINEAR_IMPLICIT_DISCARD.
    """
    compiled = compile_source(_SOURCE_CHAINED_MEASURE_NO_DISCARD)
    codes = _codes(compiled.diagnostics)

    assert "LINEAR_IMPLICIT_DISCARD" not in codes


def test_existing_direct_call_site_still_works_unchanged() -> None:
    """Regression guard (backward compatibility): the existing 2-positional-
    arg call shape `evaluator._run_dynamic_arm_body(joint, stmts)` used by
    LISS-0387/0390's own tests must keep working unchanged after
    `_run_dynamic_arm_body` gains new optional `controller_values` /
    `dynamically_measured` parameters.
    """
    compiled = compile_source(
        """
package t
pub fn main() -> Unit {
    dynamic qpu {
        state q = |0>
        apply(X, q)
        reset q
    }
    State<Int> observed = coin()
    measure observed
}
"""
    )
    assert compiled.unit is not None
    dynamic_stmt = next(
        s for s in compiled.unit.main.body.stmts if isinstance(s, DynamicQpuStmt)
    )

    evaluator = Evaluator(seed=0)
    joint = Joint.unit()
    joint = evaluator._bind_names(
        joint, ["q"], KetLit(label="0", span=dynamic_stmt.span), logs=[], inspect_out=None
    )
    joint = evaluator._run_dynamic_arm_body(joint, dynamic_stmt.body.stmts)

    q_values = {world.assign.get("q") for world in joint.worlds}
    assert q_values == {0}
