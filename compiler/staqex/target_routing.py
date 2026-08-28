"""Provider-neutral target layout, routing, native translation, and scheduling.

Uses synthetic immutable TargetSnapshot fixtures. Does not import Physics IR,
Semantic IR, provider SDKs, or live capability ports (LISS-0099).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Any, Mapping


Diagnostic = dict[str, Any]
STAGE_PROVENANCE = ("layout", "routing", "native", "schedule")


@dataclass(frozen=True, slots=True)
class LogicalResourceId:
    logical_id: str


@dataclass(frozen=True, slots=True)
class LogicalOperation:
    operation_id: str
    kind: str
    resources: tuple[LogicalResourceId, ...]


@dataclass(frozen=True, slots=True)
class TargetSnapshot:
    snapshot_id: str
    profile_id: str
    schema_version: str
    physical_qubits: tuple[int, ...]
    connectivity: tuple[tuple[int, int], ...]
    native_operations: tuple[str, ...]
    measurement_supported: bool
    reset_supported: bool
    timing_resolution: str
    max_concurrent_measurements: int
    max_logical_qubits: int


@dataclass(frozen=True, slots=True)
class LayoutResult:
    stage: str
    mapping: dict[str, int]
    profile_id: str
    provenance: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class InsertedOperation:
    operation_id: str
    kind: str
    physical_pair: tuple[int, int]
    justification_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RoutingResult:
    stage: str
    insertions: tuple[InsertedOperation, ...]
    logical_resources: tuple[LogicalResourceId, ...]
    provenance: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NativeTranslation:
    stage: str
    translations: tuple[tuple[str, str], ...]
    reject_reasons: tuple[str, ...]
    provenance: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ScheduleResult:
    stage: str
    timing_resolution: str
    barriers: tuple[str, ...]
    concurrency_assumptions: tuple[str, ...]
    provenance: tuple[str, ...]
    depth: int = 0
    duration: str = "unknown"


@dataclass(frozen=True, slots=True)
class TargetPipelineResult:
    pipeline_id: str
    status: str
    layout: LayoutResult
    routing: RoutingResult
    native: NativeTranslation
    schedule: ScheduleResult
    diagnostics: tuple[Diagnostic, ...]
    provenance: tuple[str, ...]
    selected_alternative: str | None
    cost: dict[str, int] | None = None
    measurement_mapping: tuple[tuple[str, str], ...] = ()
    artifact: None = None
    allocation: None = None
    qasm: None = None
    partial_artifact: None = None
    physical_execution_claimed: bool = False


def _diagnostic(code: str, message: str) -> Diagnostic:
    return {"code": code, "message": message}


def _empty_layout(profile_id: str = "") -> LayoutResult:
    return LayoutResult(
        stage="layout",
        mapping={},
        profile_id=profile_id,
        provenance=("layout",),
    )


def _empty_routing(
    *, logical_resources: tuple[LogicalResourceId, ...] = ()
) -> RoutingResult:
    return RoutingResult(
        stage="routing",
        insertions=(),
        logical_resources=logical_resources,
        provenance=("routing",),
    )


def _empty_native(*, reject_reasons: tuple[str, ...] = ()) -> NativeTranslation:
    return NativeTranslation(
        stage="native",
        translations=(),
        reject_reasons=reject_reasons,
        provenance=("native",),
    )


def _empty_schedule(timing_resolution: str = "") -> ScheduleResult:
    return ScheduleResult(
        stage="schedule",
        timing_resolution=timing_resolution,
        barriers=(),
        concurrency_assumptions=(),
        provenance=("schedule",),
    )


def _infeasible(
    *,
    pipeline_id: str,
    code: str,
    message: str,
    layout: LayoutResult | None = None,
    routing: RoutingResult | None = None,
    native: NativeTranslation | None = None,
    schedule: ScheduleResult | None = None,
) -> TargetPipelineResult:
    return TargetPipelineResult(
        pipeline_id=pipeline_id,
        status="infeasible",
        layout=layout or _empty_layout(),
        routing=routing or _empty_routing(),
        native=native or _empty_native(),
        schedule=schedule or _empty_schedule(),
        diagnostics=(_diagnostic(code, message),),
        provenance=STAGE_PROVENANCE,
        selected_alternative=None,
    )


def _snapshot_is_valid(snapshot: TargetSnapshot) -> bool:
    return bool(
        snapshot.snapshot_id
        and snapshot.profile_id
        and snapshot.schema_version
        and snapshot.physical_qubits
        and snapshot.timing_resolution
        and snapshot.max_logical_qubits > 0
        and snapshot.max_concurrent_measurements > 0
    )


def _adjacency(snapshot: TargetSnapshot) -> dict[int, set[int]]:
    graph: dict[int, set[int]] = {qubit: set() for qubit in snapshot.physical_qubits}
    for left, right in snapshot.connectivity:
        if left in graph and right in graph:
            graph[left].add(right)
            graph[right].add(left)
    return graph


def _shortest_path(
    graph: Mapping[int, set[int]], start: int, goal: int
) -> tuple[int, ...] | None:
    if start == goal:
        return (start,)
    queue: deque[tuple[int, ...]] = deque(((start,),))
    seen = {start}
    while queue:
        path = queue.popleft()
        node = path[-1]
        for neighbor in sorted(graph.get(node, ())):
            if neighbor in seen:
                continue
            nxt = path + (neighbor,)
            if neighbor == goal:
                return nxt
            seen.add(neighbor)
            queue.append(nxt)
    return None


def _apply_physical_swap(mapping: dict[str, int], left: int, right: int) -> None:
    logical_left = next(
        (logical for logical, physical in mapping.items() if physical == left),
        None,
    )
    logical_right = next(
        (logical for logical, physical in mapping.items() if physical == right),
        None,
    )
    if logical_left is not None:
        mapping[logical_left] = right
    if logical_right is not None:
        mapping[logical_right] = left


def _build_layout(
    resources: tuple[LogicalResourceId, ...],
    snapshot: TargetSnapshot,
    preferred: Mapping[str, int],
) -> LayoutResult:
    mapping: dict[str, int] = {}
    used: set[int] = set()
    for resource in resources:
        if resource.logical_id in preferred:
            physical = preferred[resource.logical_id]
            mapping[resource.logical_id] = physical
            used.add(physical)
    for resource in resources:
        if resource.logical_id in mapping:
            continue
        for physical in snapshot.physical_qubits:
            if physical not in used:
                mapping[resource.logical_id] = physical
                used.add(physical)
                break
    return LayoutResult(
        stage="layout",
        mapping=mapping,
        profile_id=snapshot.profile_id,
        provenance=("layout", "snapshot:" + snapshot.snapshot_id),
    )


def _native_supported(kind: str, native_operations: tuple[str, ...]) -> bool:
    if kind in native_operations:
        return True
    if kind == "h":
        return "rz" in native_operations and "sx" in native_operations
    return False


def _native_target(kind: str, native_operations: tuple[str, ...]) -> str:
    if kind in native_operations:
        return kind
    return "sx+rz"


def _route_two_qubit(
    *,
    operation: LogicalOperation,
    mapping: dict[str, int],
    graph: Mapping[int, set[int]],
    swap_counter: list[int],
) -> tuple[InsertedOperation, ...] | None:
    left_id = operation.resources[0].logical_id
    right_id = operation.resources[1].logical_id
    path = _shortest_path(graph, mapping[left_id], mapping[right_id])
    if path is None:
        return None
    if len(path) <= 2:
        return ()

    insertions: list[InsertedOperation] = []
    for index in range(len(path) - 1, 1, -1):
        left, right = path[index - 1], path[index]
        pair = (min(left, right), max(left, right))
        swap_counter[0] += 1
        insertions.append(
            InsertedOperation(
                operation_id=f"swap.{swap_counter[0]}",
                kind="swap",
                physical_pair=pair,
                justification_ids=(operation.operation_id,),
            )
        )
        _apply_physical_swap(mapping, left, right)
    return tuple(insertions)


def _route_operations(
    *,
    operations: tuple[LogicalOperation, ...],
    resources: tuple[LogicalResourceId, ...],
    layout: LayoutResult,
    snapshot: TargetSnapshot,
    pipeline_id: str,
) -> RoutingResult | TargetPipelineResult:
    working_map = dict(layout.mapping)
    graph = _adjacency(snapshot)
    insertions: list[InsertedOperation] = []
    swap_counter = [0]
    for operation in operations:
        if len(operation.resources) < 2:
            continue
        routed = _route_two_qubit(
            operation=operation,
            mapping=working_map,
            graph=graph,
            swap_counter=swap_counter,
        )
        if routed is None:
            return _infeasible(
                pipeline_id=pipeline_id,
                code="TARGET_TOPOLOGY_INFEASIBLE",
                message="no connectivity path for two-qubit operation",
                layout=layout,
                routing=RoutingResult(
                    stage="routing",
                    insertions=tuple(insertions),
                    logical_resources=resources,
                    provenance=("routing", "topology-reject"),
                ),
                schedule=_empty_schedule(snapshot.timing_resolution),
            )
        insertions.extend(routed)
    return RoutingResult(
        stage="routing",
        insertions=tuple(insertions),
        logical_resources=resources,
        provenance=("routing", "deterministic-v1"),
    )


def _translate_native(
    operations: tuple[LogicalOperation, ...],
    snapshot: TargetSnapshot,
) -> NativeTranslation:
    translations: list[tuple[str, str]] = []
    rejects: list[str] = []
    for operation in operations:
        if _native_supported(operation.kind, snapshot.native_operations):
            translations.append(
                (
                    operation.kind,
                    _native_target(operation.kind, snapshot.native_operations),
                )
            )
        else:
            rejects.append(operation.kind)
    return NativeTranslation(
        stage="native",
        translations=tuple(translations),
        reject_reasons=tuple(rejects),
        provenance=("native",),
    )


def _build_schedule(snapshot: TargetSnapshot, *, depth: int = 0) -> ScheduleResult:
    return ScheduleResult(
        stage="schedule",
        timing_resolution=snapshot.timing_resolution,
        barriers=("barrier.end",),
        concurrency_assumptions=(
            f"max_concurrent_measurements={snapshot.max_concurrent_measurements}",
        ),
        provenance=("schedule",),
        depth=depth,
        duration="finite",
    )


def _cost(
    operations: tuple[LogicalOperation, ...], routing: RoutingResult
) -> dict[str, int]:
    return {
        "swap_count": len(routing.insertions),
        "total_operations": len(operations) + len(routing.insertions),
    }


def _measurement_mapping(plan: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    return tuple(
        (str(logical), str(classical))
        for logical, classical in tuple(plan.get("measurements", ()))
    )


def _with_artifact_evidence(
    result: TargetPipelineResult,
    plan: Mapping[str, Any],
    *,
    provenance_suffix: str,
) -> TargetPipelineResult:
    """Attach target-neutral artifact evidence to measurement-aware results."""
    return TargetPipelineResult(
        pipeline_id=result.pipeline_id,
        status=result.status,
        layout=result.layout,
        routing=result.routing,
        native=result.native,
        schedule=result.schedule,
        diagnostics=result.diagnostics,
        provenance=(*result.provenance, provenance_suffix),
        selected_alternative=result.selected_alternative,
        cost=result.cost,
        measurement_mapping=_measurement_mapping(plan),
        physical_execution_claimed=False,
    )


def run_target_pipeline(
    plan: Mapping[str, Any],
    snapshot: TargetSnapshot | None,
) -> TargetPipelineResult:
    plan_id = str(plan.get("plan_id", "plan.anonymous"))
    pipeline_id = f"target.{plan_id}"
    resources: tuple[LogicalResourceId, ...] = tuple(plan.get("resources", ()))
    operations: tuple[LogicalOperation, ...] = tuple(plan.get("operations", ()))
    preferred: Mapping[str, int] = dict(plan.get("preferred_physical", {}) or {})

    if snapshot is None:
        return _infeasible(
            pipeline_id=pipeline_id,
            code="TARGET_SNAPSHOT_REQUIRED",
            message="versioned TargetSnapshot is required",
        )
    if not _snapshot_is_valid(snapshot):
        return _infeasible(
            pipeline_id=pipeline_id,
            code="TARGET_SNAPSHOT_INVALID",
            message="TargetSnapshot is missing required versioned fields",
            layout=_empty_layout(snapshot.profile_id),
            schedule=_empty_schedule(snapshot.timing_resolution),
        )
    if len(resources) > snapshot.max_logical_qubits:
        return _infeasible(
            pipeline_id=pipeline_id,
            code="TARGET_CAPACITY_EXCEEDED",
            message="logical width exceeds snapshot max_logical_qubits",
            layout=_empty_layout(snapshot.profile_id),
            schedule=_empty_schedule(snapshot.timing_resolution),
        )

    layout = _build_layout(resources, snapshot, preferred)
    routed = _route_operations(
        operations=operations,
        resources=resources,
        layout=layout,
        snapshot=snapshot,
        pipeline_id=pipeline_id,
    )
    if isinstance(routed, TargetPipelineResult):
        if "measurements" in plan:
            return _with_artifact_evidence(
                routed,
                plan,
                provenance_suffix="artifact-none",
            )
        return routed

    native = _translate_native(operations, snapshot)
    if native.reject_reasons:
        result = _infeasible(
            pipeline_id=pipeline_id,
            code="TARGET_NATIVE_UNSUPPORTED",
            message=(
                "unsupported native operations: "
                + ", ".join(native.reject_reasons)
            ),
            layout=layout,
            routing=routed,
            native=native,
            schedule=_empty_schedule(snapshot.timing_resolution),
        )
        if "measurements" in plan:
            return _with_artifact_evidence(
                result,
                plan,
                provenance_suffix="artifact-none",
            )
        return result

    measurement_mapping = _measurement_mapping(plan)
    provenance = STAGE_PROVENANCE
    if "measurements" in plan:
        provenance = (*STAGE_PROVENANCE, "artifact-target-neutral")
    return TargetPipelineResult(
        pipeline_id=pipeline_id,
        status="verified",
        layout=layout,
        routing=routed,
        native=native,
        schedule=_build_schedule(
            snapshot,
            depth=len(operations) + len(routed.insertions),
        ),
        diagnostics=(),
        provenance=provenance,
        selected_alternative=None,
        cost=_cost(operations, routed),
        measurement_mapping=measurement_mapping,
    )


def _verify_stages(result: TargetPipelineResult) -> list[Diagnostic]:
    expected = (
        ("layout", result.layout.stage),
        ("routing", result.routing.stage),
        ("native", result.native.stage),
        ("schedule", result.schedule.stage),
    )
    return [
        _diagnostic(
            "TARGET_STAGE_MISMATCH",
            f"{name}.stage must be '{name}'",
        )
        for name, stage in expected
        if stage != name
    ]


def verify_target_pipeline(result: TargetPipelineResult) -> list[Diagnostic]:
    diagnostics = _verify_stages(result)
    layout_ids = set(result.layout.mapping)
    routing_ids = {item.logical_id for item in result.routing.logical_resources}
    if layout_ids != routing_ids:
        diagnostics.append(
            _diagnostic(
                "TARGET_LOGICAL_IDENTITY_BROKEN",
                "routing logical resources must match layout mapping identities",
            )
        )
    return diagnostics
