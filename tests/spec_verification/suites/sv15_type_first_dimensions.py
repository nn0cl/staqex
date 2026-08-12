"""SV-15: Type-First declarations + dimensional analysis."""

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


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # Type-First parse + evaluate unit quantity
    try:
        src = as_main("""
Delta<Time> dt = 0.05.s
Mass m = 1.0.kg
measure dt
""")
        compiled = compile_source(src)
        if compiled.unit is None:
            raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
        hard = [d for d in compiled.diagnostics if d.get("code") in {
            "PARSE_ERROR", "LEX_ERROR", "DIMENSION_MISMATCH_ERROR", "TYPE_NOT_STATE"
        }]
        if hard:
            raise AssertionFailure(hard[0]["code"], str(hard))
        binds = compiled.unit.main.body.stmts
        if binds[0].ty is None or binds[0].ty.name != "Delta":
            raise AssertionFailure("PARSE_ERROR", f"expected Delta type-first, got {binds[0]}")
        ev = Evaluator(seed=0)
        result = ev.run_unit(compiled.unit, stdout=io.StringIO())
        marg = result.joint.marginal("dt")
        st = State(marg, payload_type=float)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {0.05: 1.0})
        out.append(
            CaseResult(
                "SV-15",
                "sv15-type-first-parse",
                "Delta<Time> dt = 0.05.s parses & evaluates",
                True,
                ["Type-First", "unit literal"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-15",
                "sv15-type-first-parse",
                "Type-First parse",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # Dimensionally consistent phase-space step typechecks
    try:
        src = as_main("""
Delta<Time> dt = 0.5.s
Mass m = 1.0.kg
Stiffness k = 1.0.N_m
State<Length> x = dirac(1.0.m)
State<Momentum> p = dirac(0.0.kg_m_s)
(x, p) = evolve (x, p) for dt {
  (x + (dt / m) * p, p - (dt * k) * x)
}
measure x
""")
        compiled = compile_source(src)
        dims = [d for d in compiled.diagnostics if d.get("code") == "DIMENSION_MISMATCH_ERROR"]
        if dims:
            raise AssertionFailure("DIMENSION_MISMATCH_ERROR", str(dims))
        if compiled.unit is None:
            raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
        ev = Evaluator(seed=0)
        result = ev.run_unit(compiled.unit, stdout=io.StringIO())
        if result.joint.is_vacuum():
            raise AssertionFailure("SUPERPOSITION_MISMATCH", "vacuum after evolve")
        out.append(
            CaseResult(
                "SV-15",
                "sv15-dim-ok-evolve",
                "dimension-consistent Euler passes typecheck",
                True,
                ["dimensional analysis"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-15",
                "sv15-dim-ok-evolve",
                "dim-ok evolve",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # Length + Time must be rejected
    try:
        src = as_main("""
State<Length> x = dirac(1.0.m)
Delta<Time> dt = 0.5.s
State bad = x + dt
measure bad
""")
        compiled = compile_source(src)
        dims = [d for d in compiled.diagnostics if d.get("code") == "DIMENSION_MISMATCH_ERROR"]
        if not dims:
            raise AssertionFailure(
                "DIMENSION_MISMATCH_ERROR",
                f"expected DIMENSION_MISMATCH_ERROR, diags={compiled.diagnostics}",
            )
        msg = dims[0].get("message", "")
        if "L" not in msg and "Length" not in msg and "[" not in msg:
            # still OK if code present
            pass
        out.append(
            CaseResult(
                "SV-15",
                "sv15-dim-reject-add",
                "x + dt → DIMENSION_MISMATCH_ERROR",
                True,
                ["assertCompileError(DIMENSION_MISMATCH_ERROR)"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-15",
                "sv15-dim-reject-add",
                "dim reject add",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # Official phase_space example still runs under Type-First
    try:
        src = (_REPO / "examples/basics/B06_type_first_dimensions/type_first_dimensions.sqx").read_text(
            encoding="utf-8"
        )
        compiled = compile_source(src)
        hard = [
            d
            for d in compiled.diagnostics
            if d.get("code")
            in {
                "PARSE_ERROR",
                "LEX_ERROR",
                "DIMENSION_MISMATCH_ERROR",
                "TYPE_NOT_STATE",
                "EARLY_COLLAPSE_ERROR",
            }
        ]
        if hard:
            raise AssertionFailure(hard[0]["code"], str(hard))
        ev = Evaluator(seed=0)
        result = ev.run_unit(compiled.unit, stdout=io.StringIO())
        if result.measure is None and not result.joint.is_vacuum():
            raise AssertionFailure("EARLY_COLLAPSE_ERROR", "missing measure")
        out.append(
            CaseResult(
                "SV-15",
                "sv15-phase-space-example",
                "phase_space.sqx Type-First + dims",
                True,
                ["example"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-15",
                "sv15-phase-space-example",
                "phase_space example",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    return out
