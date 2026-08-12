"""AT-TDD Phase 1 Red: LISS-0383 Fake-gated dynamic Host path (ADR 0197).

Target: docs/specs/staqex-dynamic-qpu-lane.md § Fake-exec wire (LISS-0383).

Amended under LISS-0386 (Adjudicator 案C, 2026-08-09): the original success
fixture below (`_SOURCE_MATCH`) reuses the measured wire `q` inside its
`match` arms, which LISS-0385's `infer_dynamic_capability_demand` flags as
`needs_reuse=True`. Once LISS-0386 wires that inference into
`build_dynamic_exec_request`, this fixture must fail closed instead of
accept. The former "accepts" assertion now runs against a measure-only
fixture (`_SOURCE_MATCH_NO_REUSE`); `_SOURCE_MATCH` is repurposed below as
the "now fails closed end-to-end" regression.
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
        State q = |0>
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

_SOURCE_MATCH_NO_REUSE = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        State q = |0>
        Controller<Bit> bit = measure q
        match bit {
            0 => { }
            1 => { }
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
    """Scenario: with Fake gate and supplied outcomes, Fake accepts without physical claim.

    LISS-0386 amendment: uses the measure-only fixture (no post-measure
    reuse of the measured wire) so this scenario stays true once inferred
    capability demand is auto-attached.
    """
    job = submit_source(
        _SOURCE_MATCH_NO_REUSE,
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


def _dynamic_exec_request(*, needs_reset: bool, needs_reuse: bool) -> DynamicExecRequest:
    return DynamicExecRequest(
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
            needs_reset=needs_reset,
            needs_reuse=needs_reuse,
            needs_latency=False,
        ),
        supplied_outcomes=MappingProxyType({"tok-0": "1"}),
        escapes_to_theory=False,
        controls_shape=False,
        selects_deployment=False,
    )


def test_fake_gate_present_and_reuse_demanded_now_succeeds() -> None:
    """LISS-0388 (ADR 0200 Decision 3): reuse is repurposed for
    simulator-class profiles -- SIM0_EXACT has no live hardware and no
    physical qubit-recycling constraint, so a reuse-demanding request is
    accepted, not rejected (unlike before LISS-0387/0388).
    """
    request = _dynamic_exec_request(needs_reset=False, needs_reuse=True)
    outcome = FakeDynamicExecutor().execute(request)

    assert outcome.status == "accepted"
    assert outcome.physical_execution_claimed is False


def test_fake_gate_present_and_reset_demanded_now_succeeds() -> None:
    """LISS-0390 (ADR 0199 Amendment): reset is repurposed for
    simulator-class profiles, symmetric to LISS-0388's reuse treatment --
    SIM0_EXACT has no physical constraint against trace-out-then-reprepare
    either. Supersedes the LISS-0388 guard that asserted reset still
    rejected (reset execution is now implemented, LISS-0390).
    """
    request = _dynamic_exec_request(needs_reset=True, needs_reuse=False)
    outcome = FakeDynamicExecutor().execute(request)

    assert outcome.status == "accepted"
    assert outcome.physical_execution_claimed is False


def test_host_auto_attach_reuse_demand_now_succeeds_end_to_end() -> None:
    """LISS-0386 auto-attach still wires infer_dynamic_capability_demand
    into the Host path -- LISS-0388 (ADR 0200 Decision 3) changes what
    happens with that demand for simulator-class profiles: it now
    succeeds instead of failing closed. `_SOURCE_MATCH`'s prepared |0>
    plus supplied outcome "0" is physically consistent, so the real
    evaluator (LISS-0387) genuinely applies the matching arm's gate --
    proven directly at the Evaluator/Joint boundary by
    test_match_arm_reuse_applies_gate_for_real in
    test_liss_0387_dynamic_real_mid_circuit_measure_red.py (q is traced
    out at block end, so it is not observable via this JobResult).
    """
    job = submit_source(
        _SOURCE_MATCH,
        settings={
            "dynamic_fake_profile": "SIM0_EXACT",
            "dynamic_supplied_outcomes": {"bit": "0"},
        },
    )
    result = job.result()

    assert result.status == "succeeded"
    assert result.dynamic_trace is not None
    assert result.dynamic_trace.physical_execution_claimed is False
