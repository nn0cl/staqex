"""SV-26: Mixed open/filled control polarities `!c` (ADR 0048)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

from harness import AssertionFailure, as_main, assertSuperposition
from harness.report import CaseResult
from harness.state import State

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def _eval(src: str, seed: int = 0):
    compiled = compile_source(src)
    if compiled.unit is None:
        raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
    hard = [d for d in compiled.diagnostics if d.get("code") in {"PARSE_ERROR", "LEX_ERROR"}]
    if hard:
        raise AssertionFailure(hard[0]["code"], str(hard))
    return Evaluator(seed=seed).run_unit(compiled.unit, stdout=io.StringIO()), compiled


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    try:
        result, _ = _eval(
            as_main(
                """
State a = |1>
State b = |0>
State t = |0>
State t = capply(a, !b, X, t)
Measure t
"""
            )
        )
        assertSuperposition(State(result.joint.marginal("t"), payload_type=int), {1: 1.0})
        out.append(
            CaseResult(
                "SV-26",
                "sv26-mixed-fire",
                "capply(a,!b,X,t) on |10⟩|0⟩ → flip t",
                True,
                ["!"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-26",
                "sv26-mixed-fire",
                "capply(a,!b,X,t) on |10⟩|0⟩ → flip t",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    try:
        result, _ = _eval(
            as_main(
                """
State a = |1>
State b = |1>
State t = |0>
State t = capply(a, !b, X, t)
Measure t
"""
            )
        )
        assertSuperposition(State(result.joint.marginal("t"), payload_type=int), {0: 1.0})
        out.append(
            CaseResult(
                "SV-26",
                "sv26-mixed-idle",
                "capply(a,!b,X,t) idle on |11⟩",
                True,
                ["polarity"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-26",
                "sv26-mixed-idle",
                "capply(a,!b,X,t) idle on |11⟩",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # !a, !b ≡ ocapply
    try:
        r1, _ = _eval(
            as_main(
                """
State a = |0>
State b = |0>
State t = |0>
State t = capply(!a, !b, X, t)
Measure t
"""
            )
        )
        r2, _ = _eval(
            as_main(
                """
State a = |0>
State b = |0>
State t = |0>
State t = ocapply(a, b, X, t)
Measure t
"""
            )
        )
        if abs(r1.joint.marginal("t").get(1, 0) - 1.0) > 1e-9:
            raise AssertionFailure("NORM", str(r1.joint.marginal("t")))
        if abs(r2.joint.marginal("t").get(1, 0) - 1.0) > 1e-9:
            raise AssertionFailure("NORM", str(r2.joint.marginal("t")))
        out.append(
            CaseResult(
                "SV-26",
                "sv26-double-bang-eq-ocapply",
                "capply(!a,!b,X,t) ≡ ocapply(a,b,X,t)",
                True,
                ["ocapply"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-26",
                "sv26-double-bang-eq-ocapply",
                "capply(!a,!b,X,t) ≡ ocapply(a,b,X,t)",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    try:
        src = (_REPO / "examples/applied/A01_quantum_attention_toy/main_quantum_attention_toy.sqx").read_text(
            encoding="utf-8"
        )
        result, _ = _eval(src)
        if result.measure is None:
            raise AssertionFailure("MEASURE", "no Measure")
        out.append(
            CaseResult(
                "SV-26",
                "sv26-example",
                "mixed_control.sqx runs",
                True,
                ["examples"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-26",
                "sv26-example",
                "mixed_control.sqx runs",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    return out
