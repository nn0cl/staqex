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
            "sv18-h-evolve-length",
            "H-evolve for Length → DIMENSION_MISMATCH_ERROR",
            "DIMENSION_MISMATCH_ERROR",
            as_main(
                """
state psi = |0>
state out = evolve { psi under Z for 1.0.m }.run()
measure out
"""
            ),
        ),
        (
            "sv18-interfer-independent",
            "independent interfer → INTERFER_INDEPENDENT_STATE_ERROR",
            "INTERFER_INDEPENDENT_STATE_ERROR",
            as_main(
                """
state a = coin()
state b = coin()
state left = mix (a) { 0 -> 0, else -> 1 }
state right = mix (b) { 0 -> 1, else -> 2 }
state z = interfer(left, right)
measure z
"""
            ),
        ),
        (
            "sv18-expect-mix",
            "psi + expect → EXPECT_CLASSICAL_ONLY_ERROR",
            "EXPECT_CLASSICAL_ONLY_ERROR",
            as_main(
                """
state psi = |+>
state ez = expect(Z, psi)
state weird = psi + ez
measure weird
"""
            ),
        ),
        (
            "sv18-evolve-tuple-swap",
            "Length↔Momentum evolve result → DIMENSION_MISMATCH_ERROR",
            "DIMENSION_MISMATCH_ERROR",
            as_main(
                """
State<Length> x0 = dirac(1.0.m)
State<Momentum> p0 = dirac(1.0.kg_m_s)
state (x, p) = evolve (x0, p0) times 1 { (p, x) }
measure x
"""
            ),
        ),
        (
            "sv18-length-eq-float",
            "Length == bare Float → DIMENSION_MISMATCH_ERROR",
            "DIMENSION_MISMATCH_ERROR",
            as_main(
                """
State<Length> x = dirac(1.0.m)
state b = x == 1.0
measure b
"""
            ),
        ),
        (
            "sv18-when-in-ctrl",
            "when in ctrl → NESTED_WHEN_ERROR",
            "NESTED_WHEN_ERROR",
            as_main(
                """
state a = coin()
state r = mix (mix (a) { 0 -> 0, else -> 1 }) { 0 -> 10, else -> 20 }
measure r
"""
            ),
        ),
        (
            "sv18-coin-in-evolve",
            "coin inside evolve → COIN_IN_EVOLVE_ERROR",
            "COIN_IN_EVOLVE_ERROR",
            as_main(
                """
state x = dirac(0)
state y = evolve x times 1 {
  let c = coin()
  c
}
measure y
"""
            ),
        ),
        (
            "sv18-interfer-shared-ok",
            "shared-lineage interfer accepted",
            None,
            as_main(
                """
state slit = coin()
state a = mix (slit) { 0 -> 0, else -> 1 }
state b0 = mix (slit) { 0 -> 1, else -> 2 }
state b = phase(b0, pi)
state screen = interfer(a, b)
measure screen
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
