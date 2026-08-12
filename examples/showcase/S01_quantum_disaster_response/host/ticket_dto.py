"""S01 TonightTicket mapping from Host JobResult (LISS-0243).

Disaster-ticket business logic stays in the showcase host layer — not Kernel.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from compiler.staqex.host import JobResult, MeasurementEnvelope

_HONESTY_NOTES = (
    "Language-spec showcase; not a city-wide optimum proof.",
    "Ticket is a Host mapping of JobResult, not a field dispatch system.",
    "plan.sample_value is the terminal Measure wire basis label, not a multi-field dispatch ID.",
)

_PLAN_MEANING = (
    "Terminal sample of tonight plan wire (plan0); two-level outcome under "
    "seeded SIM — not an optimal city plan identifier."
)

_MESSAGE_TRUNCATE = 240


class IncompleteMeasurementError(ValueError):
    """Raised when a JobResult has no usable terminal measurement."""


def _terminal_envelope(result: JobResult) -> MeasurementEnvelope:
    if not result.measurements:
        raise IncompleteMeasurementError(
            "JobResult has no measurements; cannot build TonightTicket"
        )
    envelope = result.measurements[-1]
    if envelope.vacuum:
        raise IncompleteMeasurementError(
            "Terminal measurement is Vacuum; refusing invented sample_value"
        )
    if envelope.value is None and not envelope.marginal:
        raise IncompleteMeasurementError(
            "Terminal measurement has no value or marginal; fail-closed"
        )
    return envelope


def _serialize_marginal(marginal: dict[Any, float]) -> dict[str, float]:
    return {str(key): float(mass) for key, mass in marginal.items()}


def _diagnostics(result: JobResult) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for item in result.diagnostics:
        code = str(item.get("code", "UNKNOWN"))
        message = str(item.get("message", ""))
        if len(message) > _MESSAGE_TRUNCATE:
            message = message[:_MESSAGE_TRUNCATE] + "…"
        out.append({"code": code, "message": message})
    return out


def build_tonight_ticket(
    result: JobResult,
    *,
    entry: str,
    seed: int,
    target: str = "local",
) -> dict[str, Any]:
    """Map a succeeded local JobResult into TonightTicket schema_version 1.

    Raises IncompleteMeasurementError on Vacuum / empty measurements.
    Never invents sample_value.
    """

    envelope = _terminal_envelope(result)
    meta_target = result.metadata.get("target", target)
    return {
        "schema_version": 1,
        "job": {
            "status": result.status,
            "target": str(meta_target),
            "seed": int(seed),
            "entry": entry,
        },
        "plan": {
            "sample_value": envelope.value,
            "marginal": _serialize_marginal(dict(envelope.marginal)),
            "Vacuum": False,
            "wire": "plan0",
            "meaning": _PLAN_MEANING,
        },
        "ops_context": {
            "seed": int(seed),
            "note": (
                "Optional Host context only; no invented fairness/KPI fields. "
                "Causal domain→Joint mapping lives in main_disaster_response.sqx header."
            ),
        },
        "diagnostics": _diagnostics(result),
        "honesty": {
            "execution": "sim-only",
            "live_qpu": False,
            "optimality_claim": False,
            "notes": list(_HONESTY_NOTES),
        },
        "provenance": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "tool": "s01-host-export",
        },
    }
