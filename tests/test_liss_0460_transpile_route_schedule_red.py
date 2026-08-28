"""AT-TDD Phase 1 Red: LISS-0460 target-neutral route and schedule evidence."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _api():
    from compiler.staqex.target_routing import (  # noqa: PLC0415
        LogicalOperation,
        LogicalResourceId,
        TargetSnapshot,
        run_target_pipeline,
    )

    return LogicalOperation, LogicalResourceId, TargetSnapshot, run_target_pipeline


def _snapshot(TargetSnapshot, *, edges=((0, 1), (1, 2)), native_ops=("rz", "sx", "cx")):
    return TargetSnapshot(
        snapshot_id="snap.synthetic.route",
        profile_id="synthetic.route.v1",
        schema_version="target-v1",
        physical_qubits=(0, 1, 2),
        connectivity=edges,
        native_operations=native_ops,
        measurement_supported=True,
        reset_supported=True,
        timing_resolution="1ns",
        max_concurrent_measurements=1,
        max_logical_qubits=3,
    )


def _plan(LogicalOperation, LogicalResourceId, *, remote: bool = True):
    resources = tuple(LogicalResourceId(f"q{index}") for index in range(2))
    return {
        "plan_id": "plan.route.schedule.0",
        "resources": resources,
        "operations": (
            LogicalOperation("op.h", "h", (resources[0],)),
            LogicalOperation("op.cx", "cx", resources),
        ),
        "preferred_physical": {"q0": 0, "q1": 2} if remote else {},
        "measurements": (("q1", "c0"),),
    }


def test_route_reports_cost_measurement_mapping_and_schedule_evidence() -> None:
    LogicalOperation, LogicalResourceId, TargetSnapshot, run_target_pipeline = _api()
    result = run_target_pipeline(
        _plan(LogicalOperation, LogicalResourceId),
        _snapshot(TargetSnapshot),
    )

    assert result.status == "verified"
    assert result.cost["swap_count"] == len(result.routing.insertions)
    assert result.cost["total_operations"] >= 2
    assert result.measurement_mapping == (("q1", "c0"),)
    assert result.schedule.depth >= 1
    assert result.schedule.duration == "finite"
    assert result.provenance[-1] == "artifact-target-neutral"


def test_route_and_schedule_are_deterministic_and_preserve_logical_identity() -> None:
    LogicalOperation, LogicalResourceId, TargetSnapshot, run_target_pipeline = _api()
    plan = _plan(LogicalOperation, LogicalResourceId)
    snapshot = _snapshot(TargetSnapshot)

    first = run_target_pipeline(plan, snapshot)
    second = run_target_pipeline(plan, snapshot)

    assert first.status == "verified"
    assert first.routing.insertions == second.routing.insertions
    assert first.cost == second.cost
    assert first.schedule == second.schedule
    assert tuple(first.layout.mapping) == ("q0", "q1")
    assert first.measurement_mapping == (("q1", "c0"),)


def test_unsupported_route_rejects_without_partial_target_artifact() -> None:
    LogicalOperation, LogicalResourceId, TargetSnapshot, run_target_pipeline = _api()
    plan = _plan(LogicalOperation, LogicalResourceId)
    result = run_target_pipeline(plan, _snapshot(TargetSnapshot, edges=((0, 1),)))

    assert result.status == "infeasible"
    assert result.artifact is None
    assert result.allocation is None
    assert result.qasm is None
    assert result.partial_artifact is None
    assert result.physical_execution_claimed is False


def test_unsupported_native_gate_preserves_provenance_without_fallback() -> None:
    LogicalOperation, LogicalResourceId, TargetSnapshot, run_target_pipeline = _api()
    plan = _plan(LogicalOperation, LogicalResourceId, remote=False)
    plan["operations"] = (
        LogicalOperation("op.unsupported", "u3", (LogicalResourceId("q0"),)),
    )
    result = run_target_pipeline(
        plan,
        _snapshot(TargetSnapshot, native_ops=("rz", "sx")),
    )

    assert result.status == "infeasible"
    assert result.diagnostics
    assert result.artifact is None
    assert result.qasm is None
    assert result.provenance[-1] == "artifact-none"


if __name__ == "__main__":
    tests = [
        test_route_reports_cost_measurement_mapping_and_schedule_evidence,
        test_route_and_schedule_are_deterministic_and_preserve_logical_identity,
        test_unsupported_route_rejects_without_partial_target_artifact,
        test_unsupported_native_gate_preserves_provenance_without_fallback,
    ]
    for test in tests:
        test()
    print("OK — LISS-0460 Red contract")
