"""SV-18: Physical axiom typechecking (P0/P1 audit 2026-07-23)."""

from __future__ import annotations

import sys
from pathlib import Path

from harness import AssertionFailure, as_main, assertCompileError
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
            "sv18-h-Evolve-length",
            "H-Evolve for Length → DIMENSION_MISMATCH_ERROR",
            "DIMENSION_MISMATCH_ERROR",
            as_main(
                """
State psi = |0>
State out = Evolve { psi under Z for 1.0.m }.run()
Measure out
"""
            ),
        ),
        (
            "sv18-interfer-independent",
            "independent interfer → INTERFER_INDEPENDENT_STATE_ERROR",
            "INTERFER_INDEPENDENT_STATE_ERROR",
            as_main(
                """
State a = Coin()
State b = Coin()
State left = Mix (a) { 0 -> 0, else -> 1 }
State right = Mix (b) { 0 -> 1, else -> 2 }
State z = interfer(left, right)
Measure z
"""
            ),
        ),
        (
            "sv18-expect-Mix",
            "psi + expect → EXPECT_CLASSICAL_ONLY_ERROR",
            "EXPECT_CLASSICAL_ONLY_ERROR",
            as_main(
                """
State psi = |+>
State ez = expect(Z, psi)
State weird = psi + ez
Measure weird
"""
            ),
        ),
        (
            "sv18-Evolve-tuple-swap",
            "Length↔Momentum Evolve result → DIMENSION_MISMATCH_ERROR",
            "DIMENSION_MISMATCH_ERROR",
            as_main(
                """
State<Length> x0 = Dirac(1.0.m)
State<Momentum> p0 = Dirac(1.0.kg_m_s)
State (x, p) = Evolve (x0, p0) times 1 { (p, x) }
Measure x
"""
            ),
        ),
        (
            "sv18-length-eq-float",
            "Length == bare Float → DIMENSION_MISMATCH_ERROR",
            "DIMENSION_MISMATCH_ERROR",
            as_main(
                """
State<Length> x = Dirac(1.0.m)
State b = x == 1.0
Measure b
"""
            ),
        ),
        (
            "sv18-when-in-ctrl",
            "when in ctrl → NESTED_WHEN_ERROR",
            "NESTED_WHEN_ERROR",
            as_main(
                """
State a = Coin()
State r = Mix (Mix (a) { 0 -> 0, else -> 1 }) { 0 -> 10, else -> 20 }
Measure r
"""
            ),
        ),
        (
            "sv18-Coin-in-Evolve",
            "Coin inside Evolve → COIN_IN_EVOLVE_ERROR",
            "COIN_IN_EVOLVE_ERROR",
            as_main(
                """
State x = Dirac(0)
State y = Evolve x times 1 {
  let c = Coin()
  c
}
Measure y
"""
            ),
        ),
        (
            "sv18-interfer-shared-ok",
            "shared-lineage interfer accepted",
            None,
            as_main(
                """
State slit = Coin()
State a = Mix (slit) { 0 -> 0, else -> 1 }
State b0 = Mix (slit) { 0 -> 1, else -> 2 }
State b = phase(b0, pi)
State screen = interfer(a, b)
Measure screen
"""
            ),
        ),
    ]

    for case_id, title, want, src in cases:
        try:
            diags = compile_source(src).diagnostics
            codes = [d.get("code") for d in diags]
            if want is None:
                hard = {
                    "INTERFER_INDEPENDENT_STATE_ERROR",
                    "EXPECT_CLASSICAL_ONLY_ERROR",
                    "DIMENSION_MISMATCH_ERROR",
                    "NESTED_WHEN_ERROR",
                    "COIN_IN_EVOLVE_ERROR",
                    "PARSE_ERROR",
                }
                bad = [c for c in codes if c in hard]
                if bad:
                    raise AssertionFailure(bad[0], str(diags))
            else:
                assertCompileError(diags, want)
            out.append(
                CaseResult("SV-18", case_id, title, True, [want or "ok"])
            )
        except AssertionFailure as e:
            out.append(
                CaseResult(
                    "SV-18",
                    case_id,
                    title,
                    False,
                    error_code=e.code,
                    message=str(e),
                )
            )

    return out
