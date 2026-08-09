"""AT-TDD Phase 1 Red: LISS-0384 JobResult.dynamic_trace (ADR 0198).

Target behavior is docs/specs/staqex-dynamic-jobresult-trace.md.
These tests intentionally describe not-yet-implemented Host DTO behavior.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import MappingProxyType

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.dynamic_qpu import DynamicExecResult  # noqa: E402
from compiler.staqex.host import (  # noqa: E402
    DynamicTraceReport,
    Job,
    JobResult,
    MeasurementEnvelope,
    project_dynamic_trace,
)
from compiler.staqex.observation import (  # noqa: E402
    CheckpointIdentity,
    ObservationReport,
    ObservationRequest,
)


def _measurement() -> MeasurementEnvelope:
    return MeasurementEnvelope(
        value=0,
        marginal={0: 1.0},
        vacuum=False,
        sink="stdout",
        output="0",
    )


def _observation() -> ObservationReport:
    request = ObservationRequest(
        checkpoint=CheckpointIdentity(name="energy", stage="final"),
        observable="energy(H)",
        projection="expectation",
        target_lane="qpu",
        source_formula="expectation(H)",
    )
    return ObservationReport(
        request=request,
        job_id="job-dyn-001",
        values={"expectation": -1.0},
        provenance={"shots": 100},
    )


def _fake_exec_result() -> DynamicExecResult:
    return DynamicExecResult(
        status="succeeded",
        diagnostics=(),
        selected_arm="1",
        consumed_tokens=("tok-0",),
        controller_bindings=MappingProxyType({"bit": "1"}),
        physical_execution_claimed=False,
        selected_alternative=None,
    )


def test_static_only_job_leaves_dynamic_trace_unset() -> None:
    """Scenario: Static-only Job leaves dynamic_trace unset."""
    measurement = _measurement()
    result = JobResult(status="succeeded", measurements=(measurement,))
    job = Job("job-static-001", result)

    assert job.result().dynamic_trace is None
    assert job.result().measurements == (measurement,)
    assert job.result().observations == ()


def test_dynamic_fake_report_does_not_pollute_measurements() -> None:
    """Scenario: Dynamic Fake report does not pollute measurements."""
    exec_result = _fake_exec_result()
    trace = project_dynamic_trace(
        exec_result,
        lane="dynamic",
        profile_id="SIM0_EXACT",
    )
    result = JobResult(status="succeeded", dynamic_trace=trace)

    assert isinstance(trace, DynamicTraceReport)
    assert result.dynamic_trace is trace
    assert result.dynamic_trace.controller_bindings == {"bit": "1"}
    assert result.dynamic_trace.physical_execution_claimed is False
    assert result.measurements == ()


def test_sibling_channels_when_static_terminal_measure_coexists() -> None:
    """Scenario: Sibling channels when Static terminal measure coexists."""
    measurement = _measurement()
    trace = project_dynamic_trace(
        _fake_exec_result(),
        lane="dynamic",
        profile_id="SIM0_EXACT",
    )
    result = JobResult(
        status="succeeded",
        measurements=(measurement,),
        dynamic_trace=trace,
    )

    assert result.measurements == (measurement,)
    assert result.dynamic_trace is trace
    assert len(result.measurements) == 1
    assert result.measurements[0] is measurement


def test_positional_construction_of_pre_observation_fields_remains_valid() -> None:
    """Scenario: Positional construction of pre-observation fields remains valid."""
    measurement = _measurement()
    report = _observation()
    result = JobResult(
        "succeeded",
        (measurement,),
        (),
        {},
        (report,),
    )

    assert result.status == "succeeded"
    assert result.measurements == (measurement,)
    assert result.diagnostics == ()
    assert result.metadata == {}
    assert result.observations == (report,)
    assert result.dynamic_trace is None
