"""SV-08: Phase 3 — Prelude/Math, CLI check, inspect/snapshot, DAG IR."""

from __future__ import annotations

import io
import sys
import tempfile
from pathlib import Path

from harness import AssertionFailure, as_main, assertNormEquals, assertSuperposition
from harness.report import CaseResult
from harness.state import State

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.cli import cmd_check, build_parser  # noqa: E402
from compiler.staqex.ir.dag import lower_source_ast  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402
from compiler.staqex.stdlib.prelude import PRELUDE_NAMES, is_prelude  # noqa: E402


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # Prelude names
    try:
        for n in ("coin", "dirac", "vacuum", "inspect", "map", "Math"):
            if not is_prelude(n):
                raise AssertionFailure("TYPE_NOT_STATE", f"{n} missing from prelude")
        if "if" in PRELUDE_NAMES:
            raise AssertionFailure("FORBIDDEN_KEYWORD", "if must not be prelude")
        out.append(
            CaseResult(
                "SV-08",
                "sv08-prelude",
                "Prelude includes prep/combinators/Math",
                True,
                ["prelude"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult("SV-08", "sv08-prelude", "prelude", False, error_code=e.code, message=str(e))
        )

    # Math.sin on State<Float>
    try:
        src = as_main("""
State phase = mix (coin()) {
  0 -> 0.0,
  else -> 1.5707963267948966,
}
State s = Math.sin(phase)
measure s
""")
        compiled = compile_source(src)
        if compiled.unit is None:
            raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
        ev = Evaluator(seed=0)
        result = ev.run_unit(compiled.unit, stdout=io.StringIO())
        marg = result.joint.marginal("s")
        # sin(0)=0, sin(π/2)=1
        st = State({round(k, 10): v for k, v in marg.items()}, payload_type=float)
        assertNormEquals(st, 1.0)
        # allow float key fuzz
        keys = sorted(marg.keys())
        if len(keys) != 2:
            raise AssertionFailure("SUPERPOSITION_MISMATCH", f"keys={keys}")
        vals = sorted(float(k) for k in keys)
        if abs(vals[0] - 0.0) > 1e-9 or abs(vals[1] - 1.0) > 1e-9:
            raise AssertionFailure("SUPERPOSITION_MISMATCH", f"sin masses keys {vals}")
        out.append(
            CaseResult(
                "SV-08",
                "sv08-math-sin",
                "Math.sin pushforward on State<Float>",
                True,
                ["assertSuperposition", "Math.sin"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-08",
                "sv08-math-sin",
                "Math.sin",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # inspect non-destructive + identity bind
    try:
        src = as_main("""
State x = coin()
State y = inspect(x)
measure y
""")
        buf = io.StringIO()
        compiled = compile_source(src)
        ev = Evaluator(seed=0, inspect_sink=buf)
        result = ev.run_unit(compiled.unit, stdout=io.StringIO())
        st = State(result.joint.marginal("y"), payload_type=int)
        assertSuperposition(st, {0: 0.5, 1: 0.5})
        if "mass" not in buf.getvalue():
            raise AssertionFailure("SUPERPOSITION_MISMATCH", f"inspect log empty: {buf.getvalue()!r}")
        if result.rng_calls_before_measure != 0:
            raise AssertionFailure("NORM_MISMATCH", "inspect must not use RngPort")
        out.append(
            CaseResult(
                "SV-08",
                "sv08-inspect",
                "inspect logs table; identity on joint",
                True,
                ["inspect"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-08",
                "sv08-inspect",
                "inspect",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # snapshot CSV sink
    try:
        with tempfile.TemporaryDirectory() as td:
            path = str(Path(td) / "log.csv")
            src = f"""
State x = coin()
snapshot x to {path}
measure x
"""
            # sink must be ident — write via stdout Console instead
            src = as_main("""
State x = coin()
snapshot x to stdout
measure x
""")
            buf = io.StringIO()
            compiled = compile_source(src)
            ev = Evaluator(seed=0)
            result = ev.run_unit(compiled.unit, stdout=buf)
            text = buf.getvalue()
            if "value" not in text or "mass" not in text:
                raise AssertionFailure("SUPERPOSITION_MISMATCH", f"snapshot missing csv: {text!r}")
            if not any("snapshot:stdout" in log for log in result.logs):
                raise AssertionFailure("SUPERPOSITION_MISMATCH", f"logs={result.logs}")
        out.append(
            CaseResult(
                "SV-08",
                "sv08-snapshot",
                "snapshot writes CSV host log",
                True,
                ["snapshot"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-08",
                "sv08-snapshot",
                "snapshot",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # staqex check catches forbidden
    try:
        parser = build_parser()
        args = parser.parse_args(
            ["check", "-e", as_main("State x = coin()\nif (x) {}\nmeasure x\n")]
        )
        import contextlib

        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = cmd_check(args)
        if code != 1:
            raise AssertionFailure("FORBIDDEN_KEYWORD", f"check exit {code}")
        out.append(
            CaseResult(
                "SV-08",
                "sv08-cli-check",
                "staqex check fails on Forbidden",
                True,
                ["cli check"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-08",
                "sv08-cli-check",
                "cli check",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # DAG IR extraction
    try:
        src = as_main("State x = coin()\nState y = x + x\nmeasure y\n")
        compiled = compile_source(src)
        dag = lower_source_ast(compiled.unit)
        kinds = dag.summary()["kinds"]
        if "coin" not in kinds or "binop" not in kinds or "measure" not in kinds:
            raise AssertionFailure("PARSE_ERROR", f"dag kinds={kinds}")
        if dag.measure is None:
            raise AssertionFailure("EARLY_COLLAPSE_ERROR", "dag missing measure node")
        dot = dag.to_dot()
        if "digraph" not in dot:
            raise AssertionFailure("PARSE_ERROR", "bad DOT")
        out.append(
            CaseResult(
                "SV-08",
                "sv08-dag-ir",
                "AST lowers to DAG IR with measure sink",
                True,
                ["dag ir"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-08",
                "sv08-dag-ir",
                "dag ir",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    return out
