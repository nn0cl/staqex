"""SV-13: Physical surface — evolve times, tuple bind, correlated BinOp (Priority 1)."""

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

EVOLVE_HO = as_main("""
State bit = coin()
State x0 = mix (bit) {
  0 -> 0.0,
  else -> 1.0,
}
State p0 = mix (bit) {
  0 -> 1.0,
  else -> 0.0,
}
State (x, p) = evolve (x0, p0) times 1 {
  let x1 = x + 0.5 * p
  let p1 = p - 0.5 * x
  (x1, p1)
}
measure x
""")


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # Parse evolve + tuple bind
    try:
        compiled = compile_source(EVOLVE_HO)
        if compiled.unit is None:
            raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
        hard = [d for d in compiled.diagnostics if d.get("code") in {"PARSE_ERROR", "LEX_ERROR"}]
        if hard:
            raise AssertionFailure("PARSE_ERROR", str(hard))
        out.append(
            CaseResult(
                "SV-13",
                "sv13-evolve-parse",
                "evolve (x,p) times N {…} parses",
                True,
                ["parser"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-13",
                "sv13-evolve-parse",
                "evolve parse",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # Correlated Euler step: world0 (0,1)→(0.5,1.0); world1 (1,0)→(1.0,-0.5)
    try:
        compiled = compile_source(EVOLVE_HO)
        ev = Evaluator(seed=0)
        result = ev.run_unit(compiled.unit, stdout=io.StringIO())
        mx = result.joint.marginal("x")
        mp = result.joint.marginal("p")
        st_x = State({round(k, 10): v for k, v in mx.items()}, payload_type=float)
        assertNormEquals(st_x, 1.0)
        # expected x: 0.5 and 1.0 each 0.5
        xs = sorted(float(k) for k in mx)
        if abs(xs[0] - 0.5) > 1e-9 or abs(xs[1] - 1.0) > 1e-9:
            raise AssertionFailure("SUPERPOSITION_MISMATCH", f"x={mx}")
        ps = sorted(float(k) for k in mp)
        if abs(ps[0] - (-0.5)) > 1e-9 or abs(ps[1] - 1.0) > 1e-9:
            raise AssertionFailure("SUPERPOSITION_MISMATCH", f"p={mp}")
        # correlation: no independent product mass on (0.5, -0.5) alone without matching world
        rows = {(round(r["assignment"]["x"], 10), round(r["assignment"]["p"], 10)): r["mass"] for r in result.joint.support_rows()}
        if (0.5, 1.0) not in rows or (1.0, -0.5) not in rows:
            raise AssertionFailure("SUPERPOSITION_MISMATCH", f"rows={rows}")
        if (0.5, -0.5) in rows:
            raise AssertionFailure("SUPERPOSITION_MISMATCH", "decorrelated fake world")
        out.append(
            CaseResult(
                "SV-13",
                "sv13-evolve-correlated",
                "Euler evolve keeps (x,p) correlation",
                True,
                ["assertSuperposition", "joint"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-13",
                "sv13-evolve-correlated",
                "evolve correlated",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # times 2 matches hand Euler twice
    try:
        src = as_main("""
State x0 = dirac(0.0)
State p0 = dirac(1.0)
State (x, p) = evolve (x0, p0) times 2 {
  let x1 = x + 0.5 * p
  let p1 = p - 0.5 * x
  (x1, p1)
}
measure x
""")
        compiled = compile_source(src)
        ev = Evaluator(seed=0)
        result = ev.run_unit(compiled.unit, stdout=io.StringIO())
        # step1: (0.5, 1.0); step2: (0.5+0.5*1, 1-0.5*0.5)=(1.0, 0.75)
        x = list(result.joint.marginal("x").keys())[0]
        p = list(result.joint.marginal("p").keys())[0]
        if abs(float(x) - 1.0) > 1e-9 or abs(float(p) - 0.75) > 1e-9:
            raise AssertionFailure("SUPERPOSITION_MISMATCH", f"got x={x} p={p}")
        out.append(
            CaseResult(
                "SV-13",
                "sv13-evolve-times2",
                "times 2 matches two Euler steps",
                True,
                ["evolve"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-13",
                "sv13-evolve-times2",
                "times 2",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # examples rewritten still run
    try:
        for rel in (
            "examples/basics/B06_type_first_dimensions/type_first_dimensions.sqx",
            "tests/fixtures/staqex/classical_oscillator.sqx",
        ):
            src = (_REPO / rel).read_text(encoding="utf-8")
            compiled = compile_source(src)
            if compiled.unit is None:
                raise AssertionFailure("PARSE_ERROR", f"{rel}: {compiled.diagnostics}")
            ev = Evaluator(seed=0)
            ev.run_unit(compiled.unit, stdout=io.StringIO())
        out.append(
            CaseResult(
                "SV-13",
                "sv13-examples-evolve",
                "phase_space + oscillator use evolve",
                True,
                ["examples"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-13",
                "sv13-examples-evolve",
                "examples evolve",
                False,
                error_code=e.code,
                message=str(e),
            )
        )
    except Exception as e:  # noqa: BLE001
        out.append(
            CaseResult(
                "SV-13",
                "sv13-examples-evolve",
                "examples evolve",
                False,
                error_code="UNEXPECTED_EXCEPTION",
                message=str(e),
            )
        )

    return out
