"""SV-25: Open-controlled ocapply — U on |0…0⟩ (ADR 0047)."""

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
        in {"PARSE_ERROR", "NON_UNITARY_TRANSFORM_ERROR", "TYPE_NOT_STATE"}
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
State c = |0>
State t = |0>
State t = ocapply(c, X, t)
measure t
"""
            )
        )
        st = State(result.joint.marginal("t"), payload_type=int)
        assertSuperposition(st, {1: 1.0})
        out.append(
            CaseResult(
                "SV-25",
                "sv25-ocx-on-zero",
                "ocapply(c,X,t) on |00⟩ → |01⟩",
                True,
                ["ocapply"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-25",
                "sv25-ocx-on-zero",
                "ocapply(c,X,t) on |00⟩ → |01⟩",
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
State c = |1>
State t = |0>
State t = ocapply(c, X, t)
measure t
"""
            )
        )
        st = State(result.joint.marginal("t"), payload_type=int)
        assertSuperposition(st, {0: 1.0})
        out.append(
            CaseResult(
                "SV-25",
                "sv25-ocx-idle-on-one",
                "ocapply idle when ctrl=|1⟩",
                True,
                ["open"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-25",
                "sv25-ocx-idle-on-one",
                "ocapply idle when ctrl=|1⟩",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # dual open: both |0⟩
    try:
        result, _ = _eval(
            as_main(
                """
State a = |0>
State b = |0>
State t = |0>
State t = ocapply(a, b, X, t)
measure t
"""
            )
        )
        st = State(result.joint.marginal("t"), payload_type=int)
        assertSuperposition(st, {1: 1.0})
        # one ctrl |1| → idle
        result2, _ = _eval(
            as_main(
                """
State a = |0>
State b = |1>
State t = |0>
State t = ocapply(a, b, X, t)
measure t
"""
            )
        )
        st2 = State(result2.joint.marginal("t"), payload_type=int)
        assertSuperposition(st2, {0: 1.0})
        out.append(
            CaseResult(
                "SV-25",
                "sv25-dual-open",
                "ocapply(a,b,X,t) needs both ctrls |0⟩",
                True,
                ["multi-open"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-25",
                "sv25-dual-open",
                "ocapply(a,b,X,t) needs both ctrls |0⟩",
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
            raise AssertionFailure("MEASURE", "no measure")
        out.append(
            CaseResult(
                "SV-25",
                "sv25-example",
                "open_control.sqx runs",
                True,
                ["examples"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-25",
                "sv25-example",
                "open_control.sqx runs",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    return out
