"""SV-01: Lit-Lift — scalars promote to State; no bare classical results."""

from __future__ import annotations

import sys
from pathlib import Path

from harness import AssertionFailure, State, as_main, assertNormEquals, assertSuperposition, assertTypeIsState, lift
from harness.report import CaseResult

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # Case 1: integer literal lift
    try:
        s = lift(10)
        assertTypeIsState(s, payload=int)
        assertNormEquals(s, 1.0)
        assertSuperposition(s, {10: 1.0})
        # must not be bare int
        if type(s) is int:
            raise AssertionFailure("TYPE_NOT_STATE", "bare int leaked")
        out.append(
            CaseResult(
                "SV-01",
                "sv01-int-lift",
                "Lit-Lift int 10 → State<Int>",
                True,
                ["assertTypeIsState", "assertNormEquals", "assertSuperposition"],
            )
        )
    except AssertionFailure as e:
        out.append(CaseResult("SV-01", "sv01-int-lift", "Lit-Lift int 10 → State<Int>", False, error_code=e.code, message=str(e)))

    # Case 2: float literal lift
    try:
        s = lift(0.01)
        assertTypeIsState(s, payload=float)
        assertNormEquals(s, 1.0)
        assertSuperposition(s, {0.01: 1.0})
        out.append(
            CaseResult(
                "SV-01",
                "sv01-float-lift",
                "Lit-Lift 0.01 → State<Float>",
                True,
                ["assertTypeIsState", "assertNormEquals", "assertSuperposition"],
            )
        )
    except AssertionFailure as e:
        out.append(CaseResult("SV-01", "sv01-float-lift", "Lit-Lift 0.01 → State<Float>", False, error_code=e.code, message=str(e)))

    # Case 3: arithmetic stays in State
    try:
        a = lift(10)
        b = lift(20)
        c = a + b
        assertTypeIsState(c)
        assertNormEquals(c, 1.0)
        assertSuperposition(c, {30: 1.0})
        if isinstance(c, (int, float)):
            raise AssertionFailure("TYPE_NOT_STATE", "arithmetic leaked classical scalar")
        out.append(
            CaseResult(
                "SV-01",
                "sv01-add-state",
                "10 + 20 as State ops → State(30)",
                True,
                ["assertTypeIsState", "assertNormEquals", "assertSuperposition"],
            )
        )
    except AssertionFailure as e:
        out.append(CaseResult("SV-01", "sv01-add-state", "10 + 20 as State ops", False, error_code=e.code, message=str(e)))

    # Case 4: Dirac alias
    try:
        s = State.dirac(42)
        assertTypeIsState(s, payload=int)
        assertNormEquals(s, 1.0)
        out.append(
            CaseResult(
                "SV-01",
                "sv01-Dirac",
                "Dirac(42) is State<Int>",
                True,
                ["assertTypeIsState", "assertNormEquals"],
            )
        )
    except AssertionFailure as e:
        out.append(CaseResult("SV-01", "sv01-Dirac", "Dirac(42)", False, error_code=e.code, message=str(e)))

    # Case 5: production typechecker Lit-Lift
    try:
        src = as_main("State x = 10\nState y = 0.01\nState z = x + 20\nMeasure z\n")
        result = compile_source(src)
        if result.checker is None:
            raise AssertionFailure("TYPE_NOT_STATE", "typechecker missing")
        for name, payload in (("x", "Int"), ("y", "Float"), ("z", "Int")):
            ty = result.checker.env.get(name)
            if ty is None or ty.kind != "State" or ty.payload != payload:
                raise AssertionFailure(
                    "TYPE_NOT_STATE",
                    f"{name} typed {ty}, expected State<{payload}>",
                )
        hard = [d for d in result.diagnostics if d.get("code") == "TYPE_NOT_STATE"]
        if hard:
            raise AssertionFailure("TYPE_NOT_STATE", str(hard))
        out.append(
            CaseResult(
                "SV-01",
                "sv01-compiler-lit-lift",
                "typechecker assigns State<T> to literals / arith",
                True,
                ["assertTypeIsState (compiler)"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-01",
                "sv01-compiler-lit-lift",
                "typechecker Lit-Lift",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    return out
