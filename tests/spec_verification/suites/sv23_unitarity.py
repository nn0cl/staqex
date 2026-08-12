"""SV-23: Static unitarity checks — NON_UNITARY_TRANSFORM_ERROR (ADR 0045/0053)."""

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
            "sv23-project-predicate",
            "project(psi, λ) → PREDICATE_PROJECTOR_ERROR",
            "PREDICATE_PROJECTOR_ERROR",
            as_main(
                """
State psi = |+>
State bad = project(psi, x -> x == 0)
Measure bad
"""
            ),
        ),
        (
            "sv23-map-constant",
            "map(_, x -> 0) on ket → NON_UNITARY_TRANSFORM_ERROR",
            "NON_UNITARY_TRANSFORM_ERROR",
            as_main(
                """
State psi = |+>
State bad = map(psi, x -> 0)
Measure bad
"""
            ),
        ),
        (
            "sv23-when-collapse",
            "when arms same literal on ket → NON_UNITARY_TRANSFORM_ERROR",
            "NON_UNITARY_TRANSFORM_ERROR",
            as_main(
                """
State psi = |+>
State bad = Mix (psi) { 0 -> 7, else -> 7 }
Measure bad
"""
            ),
        ),
        (
            "sv23-apply-non-unitary",
            "apply(2X) → NON_UNITARY_TRANSFORM_ERROR",
            "NON_UNITARY_TRANSFORM_ERROR",
            as_main(
                """
Operator Bad = 2.0 * X
State psi = |0>
State psi = apply(Bad, psi)
Measure psi
"""
            ),
        ),
        (
            "sv23-apply-hadamard-ok",
            "normalized (X+Z)/√2 apply accepted",
            None,
            as_main(
                """
Operator Had = 0.7071067811865476 * (X + Z)
State psi = |0>
State psi = apply(Had, psi)
Measure psi
"""
            ),
        ),
        (
            "sv23-hilbert-project-ok",
            "project(psi, |0>) Hilbert projector accepted",
            None,
            as_main(
                """
State psi = |0>
State p = project(psi, |0>)
Measure p
"""
            ),
        ),
        (
            "sv23-Coin-project-banned",
            "project on classical Coin → PREDICATE_PROJECTOR_ERROR",
            "PREDICATE_PROJECTOR_ERROR",
            as_main(
                """
State s = Coin()
State kept = project(s, v -> v == 1)
Measure kept
"""
            ),
        ),
    ]

    for case_id, title, expect, src in cases:
        try:
            codes = _codes(src)
            if expect is None:
                if any(
                    c in codes
                    for c in {
                        "NON_UNITARY_TRANSFORM_ERROR",
                        "PREDICATE_PROJECTOR_ERROR",
                        "CANNOT_MEASURE_CLASSICAL_VALUE_ERROR",
                    }
                ):
                    raise AssertionFailure("UNEXPECTED", f"unexpected: {codes}")
            else:
                if expect not in codes:
                    raise AssertionFailure(expect, f"got {codes}")
            out.append(
                CaseResult("SV-23", case_id, title, True, [expect or "ok"])
            )
        except AssertionFailure as e:
            out.append(
                CaseResult(
                    "SV-23",
                    case_id,
                    title,
                    False,
                    [],
                    error_code=e.code,
                    message=str(e.message),
                )
            )

    try:
        src = (_REPO / "tests/fixtures/staqex/gauge_symmetry.sqx").read_text(
            encoding="utf-8"
        )
        codes = _codes(src)
        bad = {
            "NON_UNITARY_TRANSFORM_ERROR",
            "PREDICATE_PROJECTOR_ERROR",
            "CANNOT_MEASURE_CLASSICAL_VALUE_ERROR",
            "PARSE_ERROR",
        }
        if any(c in codes for c in bad):
            raise AssertionFailure("DIAG", str(codes))
        out.append(
            CaseResult(
                "SV-23",
                "sv23-gauge-u1-ok",
                "gauge_symmetry U(1) phase+Hilbert project accepted",
                True,
                ["examples"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-23",
                "sv23-gauge-u1-ok",
                "gauge_symmetry U(1) phase+Hilbert project accepted",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    return out
