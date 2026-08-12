"""Five Meta Verification Assertions for Staqex Spec Verification."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .state import EPS, State


@dataclass
class AssertionFailure(Exception):
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


def assertNormEquals(state: State[Any], expected_norm: float, *, eps: float = EPS) -> None:
    if not isinstance(state, State):
        raise AssertionFailure("TYPE_NOT_STATE", f"assertNormEquals requires State, got {type(state)}")
    actual = state.norm()
    if abs(actual - expected_norm) > eps:
        raise AssertionFailure(
            "NORM_MISMATCH",
            f"norm={actual!r} expected={expected_norm!r} (eps={eps})",
        )


def assertSuperposition(
    state: State[Any],
    expected_bases: Mapping[Any, float],
    *,
    eps: float = EPS,
) -> None:
    if not isinstance(state, State):
        raise AssertionFailure("TYPE_NOT_STATE", f"assertSuperposition requires State, got {type(state)}")
    actual = state.support()
    exp_keys = set(expected_bases.keys())
    act_keys = set(actual.keys())
    if exp_keys != act_keys:
        raise AssertionFailure(
            "SUPERPOSITION_MISMATCH",
            f"support keys mismatch: actual={act_keys!r} expected={exp_keys!r}",
        )
    for k in exp_keys:
        if abs(actual[k] - expected_bases[k]) > eps:
            raise AssertionFailure(
                "SUPERPOSITION_MISMATCH",
                f"mass[{k!r}]={actual[k]!r} expected={expected_bases[k]!r}",
            )


def assertTypeIsState(expr: Any, *, payload: type | str | None = None) -> None:
    if not isinstance(expr, State):
        raise AssertionFailure(
            "TYPE_NOT_STATE",
            f"expected State[T], got classical {type(expr).__name__}: {expr!r}",
        )
    if payload is None:
        return
    pt = expr.payload_type
    aliases = {payload}
    if isinstance(payload, type):
        aliases.add(payload.__name__)
    if payload is bool:
        aliases.update({bool, "bool", "Boolean"})
    if pt not in aliases and pt is not payload:
        raise AssertionFailure(
            "TYPE_NOT_STATE",
            f"State payload_type={pt!r} expected={payload!r}",
        )


def assertVacuum(state: State[Any]) -> None:
    if not isinstance(state, State):
        raise AssertionFailure("TYPE_NOT_STATE", f"assertVacuum requires State, got {type(state)}")
    if not state.is_vacuum():
        raise AssertionFailure(
            "NOT_VACUUM",
            f"expected Vacuum (norm=0, empty support), got norm={state.norm()} support={state.support()}",
        )
    assertNormEquals(state, 0.0)


def assertCompileError(diagnostics: list[dict[str, Any]], expected_error_code: str) -> None:
    codes = [d.get("code") for d in diagnostics]
    if expected_error_code not in codes:
        raise AssertionFailure(
            "COMPILE_ERROR_MISSING",
            f"expected {expected_error_code} in diagnostics {codes}",
        )
