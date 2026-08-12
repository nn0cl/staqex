"""SV-05: Vacuum (ADR 0034) and comparison → State<Bool>."""

from __future__ import annotations

import sys
from pathlib import Path

from harness import AssertionFailure, State, as_main, assertNormEquals, assertSuperposition, assertTypeIsState, assertVacuum, lift
from harness.report import CaseResult

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import BinOp, StateBind  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # Case 1: project rejects all → vacuum; map/measure safe
    try:
        s = State.coin()
        vac = s.project(lambda x: x > 10)  # never true
        assertVacuum(vac)
        mapped = vac.map(lambda x: x * 2)
        assertVacuum(mapped)
        outcome = mapped.measure()
        if not outcome.is_vacuum or outcome.norm > 0:
            raise AssertionFailure("NOT_VACUUM", f"measure of vacuum not empty: {outcome}")
        out.append(
            CaseResult(
                "SV-05",
                "sv05-vacuum-project",
                "full-reject project → vacuum; map/measure safe",
                True,
                ["assertVacuum", "assertNormEquals"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-05",
                "sv05-vacuum-project",
                "full-reject project → vacuum",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # Case 2: comparison returns State[bool]
    try:
        a = State({1: 0.5, 3: 0.5}, payload_type=int)
        b = lift(2)
        cmp = a >= b  # True on 3, False on 1
        assertTypeIsState(cmp, payload=bool)
        assertNormEquals(cmp, 1.0)
        assertSuperposition(cmp, {False: 0.5, True: 0.5})
        if isinstance(cmp, bool):
            raise AssertionFailure("TYPE_NOT_STATE", "comparison leaked bare bool")
        out.append(
            CaseResult(
                "SV-05",
                "sv05-compare-state-bool",
                "A >= B → State<Boolean> superposition",
                True,
                ["assertTypeIsState<Bool>", "assertNormEquals", "assertSuperposition"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-05",
                "sv05-compare-state-bool",
                "A >= B → State<Boolean>",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # Case 3: explicit vacuum()
    try:
        v = State.vacuum(payload_type=int)
        assertVacuum(v)
        out.append(
            CaseResult(
                "SV-05",
                "sv05-vacuum-ctor",
                "State.vacuum() is norm-0",
                True,
                ["assertVacuum"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-05",
                "sv05-vacuum-ctor",
                "State.vacuum()",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    # Case 4: compiler types `>=` as State<Bool>
    try:
        src = as_main("State a = 3\nState b = 2\nState c = a >= b\nmeasure c\n")
        result = compile_source(src)
        if result.unit is None or result.checker is None:
            raise AssertionFailure("TYPE_NOT_STATE", "compile failed")
        ty = result.checker.env.get("c")
        if ty is None or ty.kind != "State" or ty.payload != "Bool":
            raise AssertionFailure("TYPE_NOT_STATE", f"c typed {ty}, expected State<Bool>")
        # find BinOp >= in AST
        found = False
        for stmt in result.unit.main.body.stmts:
            if isinstance(stmt, StateBind) and stmt.name == "c" and isinstance(stmt.expr, BinOp):
                if stmt.expr.op == ">=":
                    found = True
                    t = result.checker.type_of(stmt.expr)
                    if t is None or t.payload != "Bool":
                        raise AssertionFailure("TYPE_NOT_STATE", f"BinOp typed {t}")
        if not found:
            raise AssertionFailure("TYPE_NOT_STATE", ">= BinOp not found in AST")
        out.append(
            CaseResult(
                "SV-05",
                "sv05-compiler-compare-bool",
                "typechecker: >= → State<Bool>",
                True,
                ["assertTypeIsState<Bool> (compiler)"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-05",
                "sv05-compiler-compare-bool",
                "typechecker compare",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    return out
