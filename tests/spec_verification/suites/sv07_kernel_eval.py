"""SV-07: Kernel evaluator — correlation, when, project/Vacuum, Measure."""

from __future__ import annotations

import io
import sys
from pathlib import Path

from harness import AssertionFailure, as_main, assertNormEquals, assertSuperposition
from harness.report import CaseResult
from harness.state import State
from harness.canonical_execution import run_canonical

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.run import run_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # PoC A: correlated x + x
    try:
        src = as_main("State x = Coin()\nState y = x + x\nMeasure y\n")
        compiled = compile_source(src)
        if compiled.unit is None:
            raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
        ev = Evaluator(seed=0)
        result = run_canonical(compiled, ev, stdout=io.StringIO())
        marg = result.joint.marginal("y")
        st = State(marg, payload_type=int)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {0: 0.5, 2: 0.5})
        if 1 in marg:
            raise AssertionFailure("SUPERPOSITION_MISMATCH", "independent sum leaked mass on 1")
        if result.rng_calls_before_measure != 0:
            raise AssertionFailure("NORM_MISMATCH", "RNG used before Measure")
        out.append(
            CaseResult(
                "SV-07",
                "sv07-correlated-self-sum",
                "x+x correlated; no mass on 1",
                True,
                ["assertSuperposition", "assertNormEquals"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-07",
                "sv07-correlated-self-sum",
                "x+x correlated",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # when preserves both arms
    try:
        src = as_main("""
State c = Coin()
State z = Mix (c) {
  0 -> 10,
  else -> 20,
}
Measure z
""")
        compiled = compile_source(src)
        ev = Evaluator(seed=0)
        result = run_canonical(compiled, ev, stdout=io.StringIO())
        st = State(result.joint.marginal("z"), payload_type=int)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {10: 0.5, 20: 0.5})
        out.append(
            CaseResult(
                "SV-07",
                "sv07-when-mixture",
                "when keeps both worldlines",
                True,
                ["assertSuperposition", "assertNormEquals"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-07",
                "sv07-when-mixture",
                "when mixture",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # project all-reject → Vacuum; Measure safe
    try:
        src = as_main("""
State x = Coin()
State y = project(x, 99)
Measure y
""")
        compiled = compile_source(src)
        if compiled.unit is None:
            raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
        buf = io.StringIO()
        ev = Evaluator(seed=0)
        result = run_canonical(compiled, ev, stdout=buf)
        if not result.joint.is_vacuum():
            raise AssertionFailure("NOT_VACUUM", f"joint={result.joint.support_rows()}")
        if result.measure is None or not result.measure.vacuum:
            raise AssertionFailure("NOT_VACUUM", "Measure should report Vacuum")
        if buf.getvalue() != "":
            raise AssertionFailure("NOT_VACUUM", f"unexpected output {buf.getvalue()!r}")
        out.append(
            CaseResult(
                "SV-07",
                "sv07-project-Vacuum",
                "project reject-all → Vacuum Measure",
                True,
                ["assertVacuum"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-07",
                "sv07-project-Vacuum",
                "project Vacuum",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # map pushforward
    try:
        src = as_main("""
State x = Coin()
State y = map(x, v -> v * 10)
Measure y
""")
        compiled = compile_source(src)
        ev = Evaluator(seed=0)
        result = run_canonical(compiled, ev, stdout=io.StringIO())
        st = State(result.joint.marginal("y"), payload_type=int)
        assertSuperposition(st, {0: 0.5, 10: 0.5})
        out.append(
            CaseResult(
                "SV-07",
                "sv07-map",
                "map pushforward",
                True,
                ["assertSuperposition"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-07",
                "sv07-map",
                "map",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # interfer mixture
    try:
        src = as_main("""
State a = Dirac(1)
State b = Dirac(2)
State z = interfer(a, b)
Measure z
""")
        compiled = compile_source(src)
        ev = Evaluator(seed=0)
        result = run_canonical(compiled, ev, stdout=io.StringIO())
        st = State(result.joint.marginal("z"), payload_type=int)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {1: 0.5, 2: 0.5})
        out.append(
            CaseResult(
                "SV-07",
                "sv07-interfer",
                "interfer mixes arms",
                True,
                ["assertSuperposition", "assertNormEquals"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-07",
                "sv07-interfer",
                "interfer",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # terminal Measure samples
    try:
        src = as_main("State x = Dirac(42)\nMeasure x\n")
        buf = io.StringIO()
        rr = run_source(src, seed=1, stdout=buf)
        if not rr.compile_ok:
            raise AssertionFailure("PARSE_ERROR", str(rr.diagnostics))
        if rr.eval.measure is None or rr.eval.measure.value != 42:
            raise AssertionFailure("SUPERPOSITION_MISMATCH", f"got {rr.eval.measure}")
        if buf.getvalue().strip() != "42":
            raise AssertionFailure("SUPERPOSITION_MISMATCH", f"stdout={buf.getvalue()!r}")
        out.append(
            CaseResult(
                "SV-07",
                "sv07-Measure-stdout",
                "terminal Measure writes sample",
                True,
                ["Measure output"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-07",
                "sv07-Measure-stdout",
                "Measure stdout",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    return out
