"""AT-TDD Phase 1 Red: LISS-0390 dynamic-lane `reset` keyword.

Target: docs/architecture/adr/0199-dynamic-qubit-reuse-reset.md
(Amendment, reset keyword) / LISS-0390.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import DynamicQpuStmt, KetLit  # noqa: E402
from compiler.staqex.dynamic_capability import (  # noqa: E402
    infer_dynamic_capability_demand,
)
from compiler.staqex.dynamic_qpu import (  # noqa: E402
    ControllerValue,
    DynamicCapabilityDemand,
    DynamicExecRequest,
    FakeDynamicExecutor,
    MatchPlan,
    MergeObligation,
    OutcomeToken,
)
from compiler.staqex.host import submit_source  # noqa: E402
from compiler.staqex.host_input_port import MappingHostInputAdapter  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.runtime.joint import Joint  # noqa: E402
from types import MappingProxyType  # noqa: E402


_SOURCE_RESET = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        State q = |0>
        Controller<Bit> bit = measure q
        reset q
    }
    State<Int> observed = coin()
    measure observed
}
"""

_SOURCE_RESET_THEN_REMEASURE = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        State q = |0>
        Controller<Bit> bit = measure q
        apply(X, q)
        reset q
        Controller<Bit> bit2 = measure q
    }
    State<Int> observed = coin()
    measure observed
}
"""


def _codes(diagnostics) -> set[str]:
    return {str(d.get("code", "")) for d in diagnostics}


def test_reset_outside_dynamic_qpu_fails_closed() -> None:
    """Scenario: reset outside dynamic qpu fails closed."""
    source = """
package t
pub fn main() -> Unit {
    State q = |0>
    reset q
    measure q
}
"""
    job = submit_source(source, settings={})
    result = job.result()

    assert result.status == "failed"


def test_reset_inside_dynamic_qpu_genuinely_reinitializes() -> None:
    """Scenario: reset inside dynamic qpu genuinely reinitializes the wire.

    Starts q in a non-|0> state (via apply(X, q) before reset) so a
    label-only / no-op implementation would leave q at 1, while a real
    reset (trace_out + re-prepare |0>) leaves it at 0 -- verified directly
    at the Evaluator/Joint boundary since block-end disposal removes q
    from the public JobResult (same constraint as LISS-0387).
    """
    compiled = compile_source(
        """
package t
pub fn main() -> Unit {
    dynamic qpu {
        State q = |0>
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
    # Run the block's statements directly (measure-free path) to inspect
    # the joint before LISS-0387 Decision 5's block-end trace-out.
    joint = evaluator._run_dynamic_arm_body(joint, dynamic_stmt.body.stmts)

    q_values = {world.assign.get("q") for world in joint.worlds}
    assert q_values == {0}, (
        f"expected reset q to force q back to 0 via trace_out + re-prepare, "
        f"got {q_values!r}"
    )


def test_reset_wire_is_usable_again_after_reset() -> None:
    """Scenario: reset wire is usable again after reset.

    q is measured (bit=0), flipped to 1 via apply(X, q), then reset back
    to |0>. A second measurement supplying "0" is only physically
    consistent if reset genuinely forced q back to |0> -- if reset were a
    no-op, q would still be 1 and the second measure would vacuum,
    surfacing as dynamic_trace.physical_outcome_confirmed=False
    (LISS-0389). This is a stronger check than JobResult.status alone,
    which stays "succeeded" even for a vacuum run.
    """
    job = submit_source(
        _SOURCE_RESET_THEN_REMEASURE,
        settings={
            "dynamic_fake_profile": "SIM0_EXACT",
            "dynamic_supplied_outcomes": {"bit": "0", "bit2": "0"},
        },
    )
    result = job.result()

    assert result.status == "succeeded"
    assert result.dynamic_trace is not None
    assert result.dynamic_trace.physical_outcome_confirmed is True, (
        "expected reset to force q back to |0> so the second measure "
        "(outcome 0) is physically consistent; False means reset did not "
        "genuinely reinitialize the wire"
    )


def test_needs_reset_is_inferred_and_accepted_on_simulator_profiles() -> None:
    """Scenario: needs_reset is inferred and no longer rejected on
    simulator-class profiles.
    """
    compiled = compile_source(_SOURCE_RESET)
    demand = infer_dynamic_capability_demand(compiled.unit)
    assert demand.needs_reset is True

    request = DynamicExecRequest(
        lane="dynamic",
        profile_id="SIM0_EXACT",
        tokens=(
            OutcomeToken(
                token_id="tok-0", joint_correlation_id="j0", outcome_domain=("0", "1")
            ),
        ),
        controllers=(ControllerValue(name="bit", value="pending", phase="dynamic"),),
        match_plan=MatchPlan(token_id="tok-0", arms=(("0", "0"), ("1", "1"))),
        merge_obligation=MergeObligation(
            joint_correlation_id="j0", required_merges=0, recorded_merges=0
        ),
        capability_demand=DynamicCapabilityDemand(
            needs_reset=True, needs_reuse=False, needs_latency=False
        ),
        supplied_outcomes=MappingProxyType({"tok-0": "0"}),
        escapes_to_theory=False,
        controls_shape=False,
        selects_deployment=False,
    )
    outcome = FakeDynamicExecutor().execute(request)

    assert outcome.status == "accepted"


def test_hir_reset_of_unknown_wire_fails_closed() -> None:
    """Resetting a wire never introduced in the same dynamic qpu block
    fails closed at compile time (LISS-0390 Decision 4 boundary).
    """
    source = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        State q = |0>
        Controller<Bit> bit = measure q
        reset ghost
    }
    State<Int> observed = coin()
    measure observed
}
"""
    compiled = compile_source(source)
    codes = _codes(compiled.diagnostics)

    assert "DYN_RESET_UNKNOWN_WIRE" in codes
