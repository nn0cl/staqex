"""SV-16: Structured program syntax — package + pub fn main; top-level reject."""

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

    # package + pub fn main with Type-First + Measure runs
    try:
        src = as_main(
            """
Delta<Time> dt = 0.05.s
Measure dt
""",
            package="com.staqex.spec.sv16",
        )
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
            }
        ]
        if hard:
            raise AssertionFailure(hard[0]["code"], str(hard))
        if compiled.unit.package is None:
            raise AssertionFailure("PACKAGE_RESOLVE_ERROR", "package missing")
        if compiled.unit.main is None:
            raise AssertionFailure("PARSE_ERROR", "main missing")
        ev = Evaluator(seed=0)
        result = ev.run_unit(compiled.unit, stdout=io.StringIO())
        marg = result.joint.marginal("dt")
        st = State(marg, payload_type=float)
        assertNormEquals(st, 1.0)
        assertSuperposition(st, {0.05: 1.0})
        out.append(
            CaseResult(
                "SV-16",
                "sv16-main-ok",
                "package + pub fn main Type-First + Measure runs",
                True,
                ["main", "Type-First"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-16",
                "sv16-main-ok",
                "main ok",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # Packaged entry without main → TOPLEVEL_EXECUTION_ERROR
    # (ADR 0182: no-package sources default to experiment profile / bare main.)
    try:
        src = "package com.staqex.spec.sv16\nDelta<Time> dt = 0.05.s\n"
        compiled = compile_source(src)
        tops = [d for d in compiled.diagnostics if d.get("code") == "TOPLEVEL_EXECUTION_ERROR"]
        if not tops:
            raise AssertionFailure(
                "TOPLEVEL_EXECUTION_ERROR",
                f"expected TOPLEVEL_EXECUTION_ERROR, diags={compiled.diagnostics}",
            )
        if compiled.unit is not None and compiled.unit.main is not None:
            raise AssertionFailure("TOPLEVEL_EXECUTION_ERROR", "main must not be set")
        out.append(
            CaseResult(
                "SV-16",
                "sv16-toplevel-reject",
                "packaged Type-First without main → TOPLEVEL_EXECUTION_ERROR",
                True,
                ["assertCompileError(TOPLEVEL_EXECUTION_ERROR)"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-16",
                "sv16-toplevel-reject",
                "toplevel reject",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # package + import staqex.math.* + main parses
    try:
        src = as_main(
            """
State x = Coin()
Measure x
""",
            package="com.staqex.spec.sv16",
            imports=["staqex.math.*"],
        )
        compiled = compile_source(src)
        if compiled.unit is None:
            raise AssertionFailure("PARSE_ERROR", str(compiled.diagnostics))
        hard = [
            d
            for d in compiled.diagnostics
            if d.get("code") in {"PARSE_ERROR", "LEX_ERROR", "TOPLEVEL_EXECUTION_ERROR"}
        ]
        if hard:
            raise AssertionFailure(hard[0]["code"], str(hard))
        if compiled.unit.package is None:
            raise AssertionFailure("PACKAGE_RESOLVE_ERROR", "unit.package not set")
        if compiled.unit.package.path != ["com", "staqex", "spec", "sv16"]:
            raise AssertionFailure(
                "PACKAGE_RESOLVE_ERROR",
                f"package path={compiled.unit.package.path}",
            )
        if compiled.unit.main is None:
            raise AssertionFailure("PARSE_ERROR", "unit.main not set")
        if not compiled.unit.imports:
            raise AssertionFailure("PACKAGE_RESOLVE_ERROR", "imports empty")
        out.append(
            CaseResult(
                "SV-16",
                "sv16-package-import",
                "package + import staqex.math.* + main parses",
                True,
                ["unit.package", "unit.main"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-16",
                "sv16-package-import",
                "package import",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    return out
