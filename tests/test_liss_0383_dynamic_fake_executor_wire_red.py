"""AT-TDD Phase 1 Red: LISS-0383 Fake-gated dynamic Host path (ADR 0197).

Target: docs/specs/staqex-dynamic-qpu-lane.md § Fake-exec wire (LISS-0383).
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import MappingProxyType

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dynamic_qpu import (  # noqa: E402
    DynamicCapabilityDemand,
    DynamicExecRequest,
    FakeDynamicExecutor,
    MatchPlan,
    MergeObligation,
    OutcomeToken,
    ControllerValue,
)
from compiler.staqex.host import submit_source  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


_SOURCE_MATCH = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        state q = |0>
        Controller<Bit> bit = measure q
        match bit {
            0 => { apply(X, q) }
            1 => { apply(Z, q) }
        }
    }
    State<Int> observed = coin()
    measure observed
}
"""


def _codes(diagnostics: list[dict] | tuple[dict, ...]) -> set[str]:
    return {str(d.get("code", "")) for d in diagnostics}


def test_without_fake_gate_compile_still_rejects_dynamic_lane() -> None:
    """Scenario: without Fake gate, compile still rejects dynamic lane."""
    compiled = compile_source(_SOURCE_MATCH)
    codes = _codes(compiled.diagnostics)
    job = submit_source(_SOURCE_MATCH, settings={})

    assert "DYNAMIC_CAPABILITY_REQUIRED_ERROR" in codes
    assert "DYNAMIC_UNSUPPORTED_FEATURE_ERROR" in codes
    assert job.result().dynamic_trace is None


def test_with_fake_gate_and_supplied_outcomes_accepts_without_physical_claim() -> None:
    """Scenario: with Fake gate and supplied outcomes, Fake accepts without physical claim."""
    job = submit_source(
        _SOURCE_MATCH,
        settings={
            "dynamic_fake_profile": "SIM0_EXACT",
            # Host settings key mid-circuit tokens by controller name (Plan lock).
            "dynamic_supplied_outcomes": {"bit": "1"},
        },
    )
    result = job.result()

    assert result.status == "succeeded"
    assert result.dynamic_trace is not None
    assert result.dynamic_trace.physical_execution_claimed is False
    assert result.dynamic_trace.controller_bindings.get("bit") == "1"
    assert result.measurements  # Static terminal measure still present
    assert all(
        "bit" not in str(getattr(envelope, "value", ""))
        for envelope in result.measurements
    )


def test_fake_gate_present_but_reuse_demanded_still_fails_closed() -> None:
    """Scenario: Fake gate present but reset/reuse demanded still fails closed."""
    request = DynamicExecRequest(
        lane="dynamic",
        profile_id="SIM0_EXACT",
        tokens=(
            OutcomeToken(
                token_id="tok-0",
                joint_correlation_id="j0",
                outcome_domain=("0", "1"),
            ),
        ),
        controllers=(ControllerValue(name="bit", value="pending", phase="dynamic"),),
        match_plan=MatchPlan(token_id="tok-0", arms=(("0", "arm0"), ("1", "arm1"))),
        merge_obligation=MergeObligation(
            joint_correlation_id="j0",
            required_merges=1,
            recorded_merges=1,
        ),
        capability_demand=DynamicCapabilityDemand(
            needs_reset=False,
            needs_reuse=True,
            needs_latency=False,
        ),
        supplied_outcomes=MappingProxyType({"tok-0": "1"}),
        escapes_to_theory=False,
        controls_shape=False,
        selects_deployment=False,
    )
    outcome = FakeDynamicExecutor().execute(request)
    codes = {d.code for d in outcome.diagnostics}

    assert outcome.status == "rejected"
    assert "DYN_CAPABILITY_REUSE" in codes
    assert outcome.physical_execution_claimed is False
