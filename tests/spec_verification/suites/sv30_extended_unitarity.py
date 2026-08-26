"""SV-30: Extended static unitarity (ADR 0052)."""

from __future__ import annotations

import sys
from pathlib import Path

from harness import AssertionFailure, as_main
from harness.report import CaseResult

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(src: str) -> list[str]:
    return [d.get("code", "") for d in compile_source(src).diagnostics]


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    cases = [
        (
            "sv30-apply-fock",
            "apply(N+1/2) on qubit → NON_UNITARY_TRANSFORM_ERROR",
            "NON_UNITARY_TRANSFORM_ERROR",
            as_main(
                """
Operator H = N + 0.5
State psi = |0>
State psi = apply(H, psi)
Measure psi
"""
            ),
        ),
        (
            "sv30-apply-grid",
            "apply(½(P²+X²)) on qubit → NON_UNITARY_TRANSFORM_ERROR",
            "NON_UNITARY_TRANSFORM_ERROR",
            as_main(
                """
Operator H = 0.5 * (P * P + X * X)
State psi = |0>
State psi = apply(H, psi)
Measure psi
"""
            ),
        ),
        (
            "sv30-map-bit-collapse",
            "map(x -> x*0) on ket → NON_UNITARY_TRANSFORM_ERROR",
            "NON_UNITARY_TRANSFORM_ERROR",
            as_main(
                """
State psi = |+>
State bad = map(psi, x -> x * 0)
Measure bad
"""
            ),
        ),
        (
            "sv30-map-flip-ok",
            "map(x -> 1-x) on ket accepted",
            None,
            as_main(
                """
State psi = |+>
State ok = map(psi, x -> 1 - x)
Measure ok
"""
            ),
        ),
        (
            "sv30-capply-non-unitary",
            "capply(..., 2X, ...) → NON_UNITARY_TRANSFORM_ERROR",
            "NON_UNITARY_TRANSFORM_ERROR",
            as_main(
                """
Operator Bad = 2.0 * X
State a = |1>
State b = |0>
State b = capply(a, Bad, b)
Measure b
"""
            ),
        ),
        (
            "sv30-Evolve-non-hermitian",
            "Evolve under X*Y → NON_UNITARY_TRANSFORM_ERROR",
            "NON_UNITARY_TRANSFORM_ERROR",
            as_main(
                """
Operator Bad = X * Y
State psi = |0>
State psi = Evolve { psi under Bad for 1.0 }.run()
Measure psi
"""
            ),
        ),
        (
            "sv30-Evolve-grid-ok",
            "Evolve under X/P HO accepted",
            None,
            as_main(
                """
State psi = wavepacket(-4.0, 4.0, 16, 0.0, 0.7)
Operator H = 0.5 * (P * P + X * X)
State psi = Evolve { psi under H for 0.5 }.run()
Measure psi
"""
            ),
        ),
    ]

    for case_id, title, expect, src in cases:
        try:
            codes = _codes(src)
            if expect is None:
                if "NON_UNITARY_TRANSFORM_ERROR" in codes:
                    raise AssertionFailure(
                        "NON_UNITARY_TRANSFORM_ERROR", f"unexpected: {codes}"
                    )
            else:
                if expect not in codes:
                    raise AssertionFailure(expect, f"got {codes}")
            out.append(CaseResult("SV-30", case_id, title, True, [expect or "ok"]))
        except AssertionFailure as e:
            out.append(
                CaseResult(
                    "SV-30",
                    case_id,
                    title,
                    False,
                    [],
                    error_code=e.code,
                    message=str(e.message),
                )
            )

    return out
