"""Build Fake DynamicExecRequest from Kernel AST (LISS-0383).

Host settings key mid-circuit outcomes by controller name. Capability demand
inference (LISS-0385) is not attached here — Fake retain reject-on-demand when
a request already carries demand flags (see FakeDynamicExecutor tests).
"""

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping

from .ast_nodes import (
    CompilationUnit,
    DynamicQpuStmt,
    MatchStmt,
    MeasureExpr,
    StateBind,
    Var,
)
from .dynamic_qpu import (
    ControllerValue,
    DynamicCapabilityDemand,
    DynamicExecRequest,
    MatchPlan,
    MergeObligation,
    OutcomeToken,
)

FAKE_DYNAMIC_PROFILES = frozenset({"SIM0_EXACT", "CH1_DIGITAL_RESEARCH"})

# Host Fake gate may proceed despite these compile hard codes (Plan lock).
# LINEAR_IMPLICIT_DISCARD: mid-circuit measure inside dynamic qpu consumes a
# linear wire that Static accounting still flags; Fake Host path skips that
# lane in the Kernel evaluator (LISS-0383).
FAKE_BYPASS_HARD_CODES = frozenset(
    {
        "DYNAMIC_CAPABILITY_REQUIRED_ERROR",
        "DYNAMIC_UNSUPPORTED_FEATURE_ERROR",
        "LINEAR_IMPLICIT_DISCARD",
    }
)


def resolve_fake_dynamic_profile(settings: Mapping[str, Any]) -> str | None:
    """Return a P0 Fake profile id when Host Fake gate is present and valid."""

    profile = settings.get("dynamic_fake_profile")
    if isinstance(profile, str) and profile in FAKE_DYNAMIC_PROFILES:
        return profile
    return None


def unit_has_dynamic_qpu(unit: CompilationUnit) -> bool:
    if unit.main is None:
        return False
    return any(isinstance(stmt, DynamicQpuStmt) for stmt in unit.main.body.stmts)


def build_dynamic_exec_request(
    unit: CompilationUnit,
    *,
    profile_id: str,
    supplied_outcomes_by_controller: Mapping[str, str],
) -> DynamicExecRequest | None:
    """Build one Fake request from the first ``dynamic qpu`` block, or None."""

    if unit.main is None:
        return None
    dynamic = next(
        (stmt for stmt in unit.main.body.stmts if isinstance(stmt, DynamicQpuStmt)),
        None,
    )
    if dynamic is None:
        return None

    tokens: list[OutcomeToken] = []
    controllers: list[ControllerValue] = []
    token_by_controller: dict[str, str] = {}
    match_plan: MatchPlan | None = None
    joint_id = "j0"

    for body_stmt in dynamic.body.stmts:
        bind = _controller_measure_bind(body_stmt)
        if bind is not None:
            controller_name, _wire = bind
            token_id = f"tok-{len(tokens)}"
            tokens.append(
                OutcomeToken(
                    token_id=token_id,
                    joint_correlation_id=joint_id,
                    outcome_domain=("0", "1"),
                )
            )
            controllers.append(
                ControllerValue(
                    name=controller_name,
                    value="pending",
                    phase="dynamic",
                )
            )
            token_by_controller[controller_name] = token_id
            continue

        if isinstance(body_stmt, MatchStmt) and match_plan is None:
            measurement_token = token_by_controller.get(body_stmt.scrutinee)
            if measurement_token is None:
                continue
            arms = tuple((arm.pattern, arm.pattern) for arm in body_stmt.arms)
            match_plan = MatchPlan(token_id=measurement_token, arms=arms)

    if not tokens:
        return None

    if match_plan is None:
        match_plan = MatchPlan(
            token_id=tokens[0].token_id,
            arms=(("0", "0"), ("1", "1")),
        )
        merge = MergeObligation(
            joint_correlation_id=joint_id,
            required_merges=0,
            recorded_merges=0,
        )
    else:
        merge = MergeObligation(
            joint_correlation_id=joint_id,
            required_merges=1,
            recorded_merges=1,
        )

    supplied: dict[str, str] = {}
    for controller_name, token_id in token_by_controller.items():
        if controller_name in supplied_outcomes_by_controller:
            supplied[token_id] = str(supplied_outcomes_by_controller[controller_name])

    return DynamicExecRequest(
        lane="dynamic",
        profile_id=profile_id,
        tokens=tuple(tokens),
        controllers=tuple(controllers),
        match_plan=match_plan,
        merge_obligation=merge,
        capability_demand=DynamicCapabilityDemand(
            needs_reset=False,
            needs_reuse=False,
            needs_latency=False,
        ),
        supplied_outcomes=MappingProxyType(supplied),
        escapes_to_theory=False,
        controls_shape=False,
        selects_deployment=False,
    )


def _controller_measure_bind(statement: object) -> tuple[str, str] | None:
    """Return (controller_name, measured_wire) for Controller = measure wire."""

    if not isinstance(statement, StateBind):
        return None
    if statement.ty is None or statement.ty.name != "Controller":
        return None
    if not isinstance(statement.expr, MeasureExpr):
        return None
    if not statement.names:
        return None
    if not isinstance(statement.expr.expr, Var):
        return None
    return statement.names[0], statement.expr.expr.name
