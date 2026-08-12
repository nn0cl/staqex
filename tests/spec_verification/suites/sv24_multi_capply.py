"""SV-24: Multi-controlled capply / toffoli (ADR 0046)."""

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
    hard = [
        d
        for d in compiled.diagnostics
        if d.get("code")
        in {
            "PARSE_ERROR",
            "NON_UNITARY_TRANSFORM_ERROR",
            "TYPE_NOT_STATE",
        }
    ]
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
State b = |1>
State t = |0>
State t = capply(a, b, X, t)
Measure t
"""
            )
        )
        st = State(result.joint.marginal("t"), payload_type=int)
        assertSuperposition(st, {1: 1.0})
        out.append(
            CaseResult(
                "SV-24",
                "sv24-ccx-flip",
                "capply(a,b,X,t) on |110⟩ → |111⟩",
                True,
                ["CCX"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-24",
                "sv24-ccx-flip",
                "capply(a,b,X,t) on |110⟩ → |111⟩",
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
State b = |0>
State t = |0>
State t = toffoli(a, b, t)
Measure t
"""
            )
        )
        st = State(result.joint.marginal("t"), payload_type=int)
        assertSuperposition(st, {0: 1.0})
        out.append(
            CaseResult(
                "SV-24",
                "sv24-toffoli-idle",
                "toffoli with ctrl≠11 leaves |0⟩",
                True,
                ["toffoli"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-24",
                "sv24-toffoli-idle",
                "toffoli with ctrl≠11 leaves |0⟩",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # single-ctrl still ≡ cnot
    try:
        r1, _ = _eval(
            as_main(
                """
State a = |+>
State b = |0>
State b = cnot(a, b)
Measure b
"""
            )
        )
        r2, _ = _eval(
            as_main(
                """
State a = |+>
State b = |0>
State b = capply(a, X, b)
Measure b
"""
            )
        )
        if r1.joint.marginal("b") != r2.joint.marginal("b"):
            # compare approx
            m1, m2 = r1.joint.marginal("b"), r2.joint.marginal("b")
            for k in set(m1) | set(m2):
                if abs(m1.get(k, 0) - m2.get(k, 0)) > 1e-9:
                    raise AssertionFailure("MISMATCH", f"{m1} vs {m2}")
        out.append(
            CaseResult(
                "SV-24",
                "sv24-single-ctrl-compat",
                "single-ctrl capply(X) still ≡ cnot",
                True,
                ["compat"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-24",
                "sv24-single-ctrl-compat",
                "single-ctrl capply(X) still ≡ cnot",
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
                "SV-24",
                "sv24-example",
                "toffoli.sqx runs",
                True,
                ["examples"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-24",
                "sv24-example",
                "toffoli.sqx runs",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    return out
