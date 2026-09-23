"""Continuous-field and finiteization evaluation services.

The evaluator owns runtime maps, seed, and injected ports.  This module only
coordinates the existing host boundary and returns the existing Joint/value
objects.
"""

from __future__ import annotations

from typing import Any

from ...ast_nodes import Call, Var
from ...continuous_field import ContinuousFieldValue, continuous_pipeline_ops
from ...host_monte_carlo import (
    APPROX_EQUAL_WIDTH,
    EqualWidthHistogramMonteCarlo,
    HostRngAdapter,
    MonteCarloInjectError,
    MonteCarloSpec,
)
from ..joint import Joint
from .context import EvaluatorContext
from .errors import KernelError
from .values import evaluate_value


def _seed(context: EvaluatorContext, expr: Call, index: int) -> int | None:
    seed = context._runtime_seed()
    if len(expr.args) == index + 1:
        seed_raw = evaluate_value(context, expr.args[index], {})
        if type(seed_raw) is not int:
            raise KernelError("finiteize seed must be Int")
        return seed_raw
    return seed


def _continuous_port(context: EvaluatorContext) -> Any:
    port = context._continuous_field_port()
    if port is None:
        raise KernelError(
            "CONTINUOUS_FIELD_PORT_MISSING: no ContinuousFieldPort configured"
        )
    return port


def bind_finiteize(
    context: EvaluatorContext, joint: Joint, name: str, expr: Call
) -> Joint:
    """Bind a host equal-width histogram for a continuous interval."""
    if len(expr.args) not in (4, 5):
        raise KernelError("finiteize requires (lo, hi, n_bins, n_samples[, seed])")
    lo = float(evaluate_value(context, expr.args[0], {}))
    hi = float(evaluate_value(context, expr.args[1], {}))
    n_bins_raw = evaluate_value(context, expr.args[2], {})
    n_samples_raw = evaluate_value(context, expr.args[3], {})
    if type(n_bins_raw) is not int or type(n_samples_raw) is not int:
        raise KernelError("finiteize n_bins and n_samples must be Int")
    seed = _seed(context, expr, 4)
    if hi <= lo:
        raise KernelError("finiteize requires hi > lo")
    if n_bins_raw < 1 or n_samples_raw < 1:
        raise KernelError(
            "finiteize requires n_bins >= 1 and n_samples >= 1"
        )

    width = hi - lo

    def continuous_draw(rng: Any, _lo: float = lo, _width: float = width) -> float:
        return _lo + _width * float(rng.random())

    spec = MonteCarloSpec(
        domain_label=name,
        interval=(lo, hi),
        n_bins=n_bins_raw,
        n_samples=n_samples_raw,
        approximation=APPROX_EQUAL_WIDTH,
        coordinate=name,
        provenance={"surface": "finiteize", "draw": "uniform_interval"},
        seed=seed,
    )
    try:
        inject = EqualWidthHistogramMonteCarlo().sample_to_finite(
            spec,
            HostRngAdapter(seed=seed),
            continuous_draw=continuous_draw,
        )
    except MonteCarloInjectError as exc:
        raise KernelError(f"{exc.code}: {exc}") from exc
    context._store_runtime_object(
        f"__finiteize_prov_{name}", dict(inject.provenance)
    )
    return joint.bind_split(
        name, {label: float(mass) for label, mass in inject.atoms}
    )


def bind_finiteize_continuous(
    context: EvaluatorContext, joint: Joint, name: str, expr: Call
) -> Joint:
    """Discretize an opaque ContinuousFieldValue through the existing port."""
    if len(expr.args) not in (4, 5):
        raise KernelError(
            "finiteize(Continuous, lo, hi, n_bins[, seed]) requires 4-5 arguments"
        )
    if not isinstance(expr.args[0], Var):
        raise KernelError("finiteize Continuous source must be a bound name")
    continuous_value = context._object_environment()[expr.args[0].name]
    lo = float(evaluate_value(context, expr.args[1], {}))
    hi = float(evaluate_value(context, expr.args[2], {}))
    n_bins_raw = evaluate_value(context, expr.args[3], {})
    if type(n_bins_raw) is not int:
        raise KernelError("finiteize n_bins must be Int")
    seed = _seed(context, expr, 4)
    if hi <= lo:
        raise KernelError("finiteize requires hi > lo")
    if n_bins_raw < 1:
        raise KernelError("finiteize requires n_bins >= 1")
    port = _continuous_port(context)
    dist = port.discretize(continuous_value, lo=lo, hi=hi, n_bins=n_bins_raw, seed=seed)
    context._store_runtime_object(
        f"__finiteize_prov_{name}",
        {
            "surface": "finiteize",
            "source": "continuous",
            "interval": [lo, hi],
            "n_bins": n_bins_raw,
            "discretization": {
                "domain": name,
                "basis": "EqualWidthHistogram",
                "resolution": n_bins_raw,
            },
            "continuous_pipeline": continuous_pipeline_ops(continuous_value),
            "finite_approximation": True,
            "note": (
                "finite histogram approximation of a Continuous value; "
                "not the continuous field"
            ),
        },
    )
    return joint.bind_split(
        name, {label: float(mass) for label, mass in dist.items()}
    )


def bind_field_from_host(
    context: EvaluatorContext, joint: Joint, name: str, expr: Call
) -> Joint:
    """Create an opaque continuous host handle without evaluating its field."""
    if len(expr.args) != 2:
        raise KernelError("field_from_host requires (source, domain)")
    source = evaluate_value(context, expr.args[0], {})
    domain = evaluate_value(context, expr.args[1], {})
    if not isinstance(source, str) or not isinstance(domain, str):
        raise KernelError("field_from_host requires string (source, domain)")
    port = _continuous_port(context)
    host_ref = port.field(source, domain)
    context._store_runtime_object(
        name, ContinuousFieldValue(op="field_from_host", host_ref=host_ref)
    )
    return joint


def bind_continuous_compose(
    context: EvaluatorContext,
    joint: Joint,
    name: str,
    expr: Call,
    *,
    op_name: str,
    arity: tuple[int, int],
) -> Joint:
    """Compose opaque Continuous handles; no pointwise math is evaluated."""
    lo, hi = arity
    if not (lo <= len(expr.args) <= hi):
        raise KernelError(
            f"{op_name} requires {lo}-{hi} Continuous arguments"
            if lo != hi
            else f"{op_name} requires {lo} Continuous arguments"
        )
    objects = context._object_environment()
    inputs: list[ContinuousFieldValue] = []
    for arg in expr.args:
        if not isinstance(arg, Var):
            raise KernelError(
                f"{op_name} arguments must be Continuous-bound names"
            )
        value = objects.get(arg.name)
        if not isinstance(value, ContinuousFieldValue):
            raise KernelError(
                f"{op_name} argument `{arg.name}` is not a Continuous value"
            )
        inputs.append(value)
    context._store_runtime_object(
        name, ContinuousFieldValue(op=op_name, inputs=tuple(inputs))
    )
    return joint
