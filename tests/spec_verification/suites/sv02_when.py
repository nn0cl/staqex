"""SV-02: when preserves both worldlines (non-destructive)."""

from __future__ import annotations

from harness import AssertionFailure, State, assertNormEquals, assertSuperposition, assertTypeIsState
from harness.report import CaseResult


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    try:
        Coin = State.coin()
        # mix (coin()) { 0 -> "A", else -> "B" }
        joined = Coin.when(
            {0: lambda: State.dirac("A")},
            else_arm=lambda: State.dirac("B"),
            payload_type=str,
        )
        assertTypeIsState(joined, payload=str)
        assertNormEquals(joined, 1.0)
        assertSuperposition(joined, {"A": 0.5, "B": 0.5})
        out.append(
            CaseResult(
                "SV-02",
                "sv02-when-Coin",
                "Mix (Coin) keeps A and B at 0.5",
                True,
                ["assertTypeIsState", "assertNormEquals", "assertSuperposition"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-02",
                "sv02-when-Coin",
                "Mix (Coin) keeps A and B at 0.5",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    try:
        # both arms are themselves superpositions — masses multiply
        Coin = State.coin()
        joined = Coin.when(
            {
                0: lambda: State({10: 0.5, 20: 0.5}, payload_type=int),
            },
            else_arm=lambda: State.dirac(99),
            payload_type=int,
        )
        assertNormEquals(joined, 1.0)
        assertSuperposition(joined, {10: 0.25, 20: 0.25, 99: 0.5})
        out.append(
            CaseResult(
                "SV-02",
                "sv02-when-nested",
                "when mixes nested State arms",
                True,
                ["assertNormEquals", "assertSuperposition"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-02",
                "sv02-when-nested",
                "when mixes nested State arms",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    return out
