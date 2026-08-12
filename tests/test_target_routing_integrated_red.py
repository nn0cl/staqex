"""AT-TDD Phase 1 Red: LISS-0092 integrated target-routing contract.

One suite covers ordered layout → routing → native → schedule stages,
synthetic TargetSnapshot constraints, logical identity survival, explicit
infeasibility, and Theory/Physics/Semantic isolation. Provider SDKs,
calibration, live LISS-0099 ports, and upstream IR mutation are absent.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _load_api():
    from compiler.staqex.target_routing import (
        InsertedOperation,
        LayoutResult,
        LogicalOperation,
        LogicalResourceId,
        NativeTranslation,
        RoutingResult,
        ScheduleResult,
        TargetPipelineResult,
        TargetSnapshot,
        run_target_pipeline,
        verify_target_pipeline,
    )

    return locals()


def _resource(api, logical_id: str = "q0"):
    return api["LogicalResourceId"](logical_id=logical_id)


def _operation(api, op_id: str, kind: str, resources: tuple[str, ...]):
    return api["LogicalOperation"](
        operation_id=op_id,
        kind=kind,
        resources=tuple(api["LogicalResourceId"](logical_id=item) for item in resources),
    )


def _snapshot(
    api,
    *,
    profile_id: str = "CH1_DIGITAL_RESEARCH",
    version: str = "1",
    qubits: int = 4,
    edges: tuple[tuple[int, int], ...] | None = None,
    native_ops: tuple[str, ...] = ("rz", "sx", "cx"),
    max_logical: int | None = None,
):
    if edges is None:
        edges = tuple((index, index + 1) for index in range(qubits - 1))
    return api["TargetSnapshot"](
        snapshot_id=f"snap.{profile_id.lower()}",
        profile_id=profile_id,
        schema_version=version,
        physical_qubits=tuple(range(qubits)),
        connectivity=edges,
        native_operations=native_ops,
        measurement_supported=True,
        reset_supported=True,
        timing_resolution="1ns",
        max_concurrent_measurements=1,
        max_logical_qubits=max_logical if max_logical is not None else qubits,
    )


def _plan(api, *, width: int = 2, include_cx: bool = True):
    resources = tuple(_resource(api, f"q{index}") for index in range(width))
    operations = [
        _operation(api, "op.h0", "h", ("q0",)),
    ]
    if include_cx and width >= 2:
        operations.append(_operation(api, "op.cx01", "cx", ("q0", "q1")))
    return {
        "plan_id": "plan.routing.0",
        "resources": resources,
        "operations": tuple(operations),
    }


def _codes(diagnostics) -> set[str]:
    return {diagnostic.get("code") for diagnostic in diagnostics}


def test_pipeline_exposes_ordered_stages_with_provenance() -> None:
    api = _load_api()
    result = api["run_target_pipeline"](_plan(api), _snapshot(api))

    assert isinstance(result, api["TargetPipelineResult"])
    assert result.status == "verified"
    assert result.layout.stage == "layout"
    assert result.routing.stage == "routing"
    assert result.native.stage == "native"
    assert result.schedule.stage == "schedule"
    assert result.provenance == (
        "layout",
        "routing",
        "native",
        "schedule",
    )
    assert api["verify_target_pipeline"](result) == []


def test_missing_or_invalid_snapshot_is_rejected() -> None:
    api = _load_api()
    plan = _plan(api)

    missing = api["run_target_pipeline"](plan, None)
    assert missing.status == "infeasible"
    assert "TARGET_SNAPSHOT_REQUIRED" in _codes(missing.diagnostics)

    invalid = api["TargetSnapshot"](
        snapshot_id="",
        profile_id="",
        schema_version="",
        physical_qubits=(),
        connectivity=(),
        native_operations=(),
        measurement_supported=False,
        reset_supported=False,
        timing_resolution="",
        max_concurrent_measurements=0,
        max_logical_qubits=0,
    )
    bad = api["run_target_pipeline"](plan, invalid)
    assert bad.status == "infeasible"
    assert "TARGET_SNAPSHOT_INVALID" in _codes(bad.diagnostics)


def test_logical_resource_identity_survives_routing() -> None:
    api = _load_api()
    plan = _plan(api, width=2)
    before = tuple(item.logical_id for item in plan["resources"])
    result = api["run_target_pipeline"](plan, _snapshot(api, qubits=4))

    after = tuple(item.logical_id for item in result.routing.logical_resources)
    assert before == after
    assert set(result.layout.mapping) == set(before)
    assert api["verify_target_pipeline"](result) == []


def test_disconnected_topology_is_explicitly_infeasible() -> None:
    api = _load_api()
    # Two components: 0-1 and 2-3, but CX needs q0-q1 path only — force CX
    # across disconnected pair by mapping demand onto non-edge endpoints.
    Snapshot = _snapshot(
        api,
        qubits=4,
        edges=((0, 1), (2, 3)),
    )
    plan = {
        "plan_id": "plan.disconnect",
        "resources": (_resource(api, "q0"), _resource(api, "q1")),
        "operations": (_operation(api, "op.cx", "cx", ("q0", "q1")),),
        "preferred_physical": {"q0": 0, "q1": 2},
    }
    result = api["run_target_pipeline"](plan, Snapshot)

    assert result.status == "infeasible"
    assert "TARGET_TOPOLOGY_INFEASIBLE" in _codes(result.diagnostics)
    assert result.selected_alternative is None


def test_over_capacity_plan_is_explicitly_infeasible() -> None:
    api = _load_api()
    Snapshot = _snapshot(api, qubits=2, max_logical=2)
    plan = _plan(api, width=3, include_cx=False)
    result = api["run_target_pipeline"](plan, Snapshot)

    assert result.status == "infeasible"
    assert "TARGET_CAPACITY_EXCEEDED" in _codes(result.diagnostics)
    assert result.selected_alternative is None


def test_deterministic_routing_inserts_swaps_when_needed() -> None:
    api = _load_api()
    Snapshot = _snapshot(api, qubits=3, edges=((0, 1), (1, 2)))
    plan = {
        "plan_id": "plan.swap",
        "resources": (_resource(api, "q0"), _resource(api, "q1")),
        "operations": (_operation(api, "op.cx", "cx", ("q0", "q1")),),
        "preferred_physical": {"q0": 0, "q1": 2},
    }
    first = api["run_target_pipeline"](plan, Snapshot)
    second = api["run_target_pipeline"](plan, Snapshot)

    assert first.status == "verified"
    assert first.routing.insertions
    assert all(isinstance(item, api["InsertedOperation"]) for item in first.routing.insertions)
    assert all(item.kind == "swap" for item in first.routing.insertions)
    assert first.routing.insertions == second.routing.insertions
    assert api["verify_target_pipeline"](first) == []


def test_native_translation_rejects_unsupported_operations() -> None:
    api = _load_api()
    Snapshot = _snapshot(api, native_ops=("rz", "sx"))  # no cx
    plan = _plan(api, width=2, include_cx=True)
    result = api["run_target_pipeline"](plan, Snapshot)

    assert result.status == "infeasible"
    assert "TARGET_NATIVE_UNSUPPORTED" in _codes(result.diagnostics)
    assert isinstance(result.native, api["NativeTranslation"])


def test_schedule_records_timing_and_barriers() -> None:
    api = _load_api()
    result = api["run_target_pipeline"](_plan(api), _snapshot(api))

    assert isinstance(result.schedule, api["ScheduleResult"])
    assert result.schedule.timing_resolution == "1ns"
    assert result.schedule.barriers
    assert result.schedule.concurrency_assumptions == ("max_concurrent_measurements=1",)
    assert api["verify_target_pipeline"](result) == []


def test_ch1_and_nh5_synthetic_snapshots_are_deterministic() -> None:
    api = _load_api()
    plan = _plan(api)
    ch1 = api["run_target_pipeline"](
        plan, _snapshot(api, profile_id="CH1_DIGITAL_RESEARCH", qubits=4)
    )
    nh5 = api["run_target_pipeline"](
        plan, _snapshot(api, profile_id="NH5_REFERENCE", qubits=8)
    )

    assert ch1.status == "verified"
    assert nh5.status == "verified"
    assert ch1.layout.profile_id == "CH1_DIGITAL_RESEARCH"
    assert nh5.layout.profile_id == "NH5_REFERENCE"
    assert api["run_target_pipeline"](
        plan, _snapshot(api, profile_id="CH1_DIGITAL_RESEARCH", qubits=4)
    ).routing.insertions == ch1.routing.insertions


def test_module_does_not_import_physics_or_semantic_ir() -> None:
    api = _load_api()
    import compiler.staqex.target_routing as mod

    assert not hasattr(mod, "PhysicsModule")
    assert not hasattr(mod, "QuantumSemanticModule")
    text = Path(mod.__file__).read_text(encoding="utf-8")
    assert "physics_ir" not in text
    assert "quantum_semantic_ir" not in text
    assert api["LayoutResult"] is not None
    assert api["RoutingResult"] is not None


def test_post_route_verifier_rejects_broken_logical_identity() -> None:
    api = _load_api()
    result = api["run_target_pipeline"](_plan(api), _snapshot(api))
    broken = api["TargetPipelineResult"](
        pipeline_id=result.pipeline_id,
        status="verified",
        layout=result.layout,
        routing=api["RoutingResult"](
            stage="routing",
            insertions=result.routing.insertions,
            logical_resources=(_resource(api, "q-missing"),),
            provenance=result.routing.provenance,
        ),
        native=result.native,
        schedule=result.schedule,
        diagnostics=(),
        provenance=result.provenance,
        selected_alternative=None,
    )

    assert "TARGET_LOGICAL_IDENTITY_BROKEN" in _codes(
        api["verify_target_pipeline"](broken)
    )


if __name__ == "__main__":
    tests = tuple(
        value
        for name, value in globals().items()
        if name.startswith("test_") and callable(value)
    )
    failures = 0
    for test in tests:
        try:
            test()
        except Exception as error:
            failures += 1
            print(f"FAIL {test.__name__}: {type(error).__name__}: {error}")
    print(
        f"LISS-0092 integrated Red: {len(tests) - failures} passed, {failures} failed"
    )
    raise SystemExit(1 if failures else 0)
