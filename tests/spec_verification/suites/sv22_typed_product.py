"""SV-22: Typed product State<(A,B)>, *|* inference, trace_out (ADR 0044)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

from harness import AssertionFailure, as_main, assertNormEquals, assertSuperposition
from harness.report import CaseResult
from harness.state import State

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.typecheck import TypeChecker  # noqa: E402


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
            "LEX_ERROR",
            "TOPLEVEL_EXECUTION_ERROR",
            "DIMENSION_MISMATCH_ERROR",
            "TYPE_NOT_STATE",
            "PRODUCT_ARITY_ERROR",
            "PRODUCT_BIND_ERROR",
            "PRODUCT_TYPE_MISMATCH",
        }
    ]
    if hard:
        raise AssertionFailure(hard[0]["code"], str(hard))
    return Evaluator(seed=seed).run_unit(compiled.unit, stdout=io.StringIO()), compiled


def _codes(src: str) -> list[str]:
    return [d.get("code", "") for d in compile_source(src).diagnostics]


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # Parse + run typed product DTQW prep
    try:
        result, compiled = _eval(
            as_main(
                """
State<Qubit> c0 = |0>
State<Position> x0 = Dirac(0)
State<(Qubit, Position)> (c, x) = c0 *|* x0
Measure x
"""
            )
        )
        st = State(result.joint.marginal("x"), payload_type=int)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {0: 1.0})
        # env types after check
        tc = TypeChecker()
        tc.check_unit(compiled.unit)
        if tc.env.get("c") is None or "Qubit" not in str(tc.env["c"]):
            raise AssertionFailure("TYPE", f"c env={tc.env.get('c')}")
        if tc.env.get("x") is None or "Position" not in str(tc.env["x"]):
            raise AssertionFailure("TYPE", f"x env={tc.env.get('x')}")
        out.append(
            CaseResult(
                "SV-22",
                "sv22-typed-product-bind",
                "State<(Qubit, Position)> (c,x)=… splits carriers",
                True,
                ["TypeRef Tuple", "*|*"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-22",
                "sv22-typed-product-bind",
                "State<(Qubit, Position)> (c,x)=… splits carriers",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # Single-name product → PRODUCT_BIND_ERROR
    try:
        codes = _codes(
            as_main(
                """
State<(Qubit, Position)> walker = |0> *|* Dirac(0)
Measure walker
"""
            )
        )
        if "PRODUCT_BIND_ERROR" not in codes:
            raise AssertionFailure("PRODUCT_BIND_ERROR", f"got {codes}")
        out.append(
            CaseResult(
                "SV-22",
                "sv22-product-single-name",
                "State<(A,B)> single name → PRODUCT_BIND_ERROR",
                True,
                ["PRODUCT_BIND_ERROR"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-22",
                "sv22-product-single-name",
                "State<(A,B)> single name → PRODUCT_BIND_ERROR",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # Arity mismatch
    try:
        codes = _codes(
            as_main(
                """
State<(Qubit, Position, Int)> (a, b) = |0> *|* Dirac(0)
Measure a
"""
            )
        )
        if "PRODUCT_ARITY_ERROR" not in codes:
            raise AssertionFailure("PRODUCT_ARITY_ERROR", f"got {codes}")
        out.append(
            CaseResult(
                "SV-22",
                "sv22-product-arity",
                "3-carrier type vs 2 names → PRODUCT_ARITY_ERROR",
                True,
                ["PRODUCT_ARITY_ERROR"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-22",
                "sv22-product-arity",
                "3-carrier type vs 2 names → PRODUCT_ARITY_ERROR",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # Payload mismatch Length vs Qubit
    try:
        codes = _codes(
            as_main(
                """
State<(Length, Position)> (a, b) = |0> *|* Dirac(0)
Measure b
"""
            )
        )
        if "PRODUCT_TYPE_MISMATCH" not in codes:
            raise AssertionFailure("PRODUCT_TYPE_MISMATCH", f"got {codes}")
        out.append(
            CaseResult(
                "SV-22",
                "sv22-product-payload-mismatch",
                "Length vs Qubit component → PRODUCT_TYPE_MISMATCH",
                True,
                ["PRODUCT_TYPE_MISMATCH"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-22",
                "sv22-product-payload-mismatch",
                "Length vs Qubit component → PRODUCT_TYPE_MISMATCH",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # trace_out typed run
    try:
        result, _ = _eval(
            as_main(
                """
State<(Qubit, Position)> (c, x) = |+> *|* Dirac(0)
State _t = trace_out(c)
Measure x
"""
            )
        )
        st = State(result.joint.marginal("x"), payload_type=int)
        assertSuperposition(st, {0: 1.0})
        out.append(
            CaseResult(
                "SV-22",
                "sv22-trace-out-typed",
                "typed product + trace_out leaves |0⟩ on Position",
                True,
                ["trace_out"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-22",
                "sv22-trace-out-typed",
                "typed product + trace_out leaves |0⟩ on Position",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    # dtqw example
    try:
        src = (_REPO / "tests/fixtures/staqex/dtqw.sqx").read_text(encoding="utf-8")
        result, _ = _eval(src)
        if result.measure is None:
            raise AssertionFailure("MEASURE", "no Measure")
        out.append(
            CaseResult(
                "SV-22",
                "sv22-dtqw-typed-example",
                "typed dtqw.sqx runs",
                True,
                ["examples"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-22",
                "sv22-dtqw-typed-example",
                "typed dtqw.sqx runs",
                False,
                [],
                error_code=e.code,
                message=str(e.message),
            )
        )

    return out
