"""SV-31: User-module import linker (ADR 0054)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

from harness import AssertionFailure
from harness.report import CaseResult

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import FunDecl, StateBind  # noqa: E402
from compiler.staqex.pipeline import compile_path  # noqa: E402
from compiler.staqex.run import run_path  # noqa: E402

_EX09 = _REPO / "examples" / "basics" / "B09_multi_file_modules"
_ENTRY = _EX09 / "main_multi_file_modules.sqx"

HARD = {
    "FORBIDDEN_KEYWORD",
    "EARLY_COLLAPSE_ERROR",
    "NESTED_WHEN_ERROR",
    "PARSE_ERROR",
    "LEX_ERROR",
    "MODULE_NOT_FOUND_ERROR",
    "MODULE_CYCLE_ERROR",
    "NON_UNITARY_TRANSFORM_ERROR",
}


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    # --- linked compile of official multi-file example ---
    try:
        if not _ENTRY.is_file():
            raise AssertionFailure("PARSE_ERROR", f"missing {_ENTRY}")
        compiled = compile_path(_ENTRY)
        hard = [d for d in compiled.diagnostics if d.get("code") in HARD]
        if hard:
            raise AssertionFailure(hard[0]["code"], str(hard))
        if compiled.unit is None or compiled.unit.main is None:
            raise AssertionFailure("PARSE_ERROR", "no main after link")
        # Class fields are linked; Operator values are explicit main bindings.
        stmt_names: list[str] = []
        for s in compiled.unit.main.body.stmts:
            if isinstance(s, StateBind):
                stmt_names.extend(s.names)
        for need in ("walk_operator",):
            if need not in stmt_names:
                raise AssertionFailure(
                    "MODULE_NOT_FOUND_ERROR",
                    f"linked main missing harvested symbol `{need}`: {stmt_names}",
                )
        funs = {d.name for d in compiled.unit.decls if isinstance(d, FunDecl)}
        if "step_quantum_walk" not in funs or "build_coin_operator" not in funs:
            raise AssertionFailure(
                "MODULE_NOT_FOUND_ERROR",
                f"missing library fns in {funs}",
            )
        out.append(
            CaseResult(
                "SV-31",
                "sv31-link-symbols",
                "compile_path merges class fields + explicit Operator + funs",
                True,
                ["compile_path", "merge"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-31",
                "sv31-link-symbols",
                "compile_path symbol merge",
                False,
                error_code=e.code,
                message=str(e),
            )
        )
    except Exception as e:  # noqa: BLE001
        out.append(
            CaseResult(
                "SV-31",
                "sv31-link-symbols",
                "compile_path symbol merge",
                False,
                error_code="UNEXPECTED_EXCEPTION",
                message=str(e),
            )
        )

    # --- linked run ---
    try:
        buf = io.StringIO()
        result = run_path(_ENTRY, seed=0, stdout=buf)
        if not result.compile_ok:
            raise AssertionFailure("PARSE_ERROR", str(result.diagnostics))
        if result.eval.measure is None:
            raise AssertionFailure("EARLY_COLLAPSE_ERROR", "missing Measure")
        out.append(
            CaseResult(
                "SV-31",
                "sv31-linked-run",
                "main_multi_file_modules.sqx import+Evolve runs",
                True,
                ["run_path", "step_quantum_walk"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-31",
                "sv31-linked-run",
                "linked run",
                False,
                error_code=e.code,
                message=str(e),
            )
        )
    except Exception as e:  # noqa: BLE001
        out.append(
            CaseResult(
                "SV-31",
                "sv31-linked-run",
                "linked run",
                False,
                error_code="UNEXPECTED_EXCEPTION",
                message=str(e),
            )
        )

    # --- missing import → MODULE_NOT_FOUND_ERROR ---
    try:
        # Write a temp entry that imports a missing module under examples
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            entry = root / "main.sqx"
            entry.write_text(
                """
package tmp.modtest
import tmp.modtest.does_not_exist
pub fn main() -> Unit {
    State x = Dirac(0)
    Measure x
}
""",
                encoding="utf-8",
            )
            diags = compile_path(entry).diagnostics
            codes = [d.get("code") for d in diags]
            if "MODULE_NOT_FOUND_ERROR" not in codes:
                raise AssertionFailure(
                    "PARSE_ERROR", f"expected MODULE_NOT_FOUND_ERROR, got {codes}"
                )
        out.append(
            CaseResult(
                "SV-31",
                "sv31-missing-import",
                "unresolved import → MODULE_NOT_FOUND_ERROR",
                True,
                ["MODULE_NOT_FOUND_ERROR"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-31",
                "sv31-missing-import",
                "missing import",
                False,
                error_code=e.code,
                message=str(e),
            )
        )
    except Exception as e:  # noqa: BLE001
        out.append(
            CaseResult(
                "SV-31",
                "sv31-missing-import",
                "missing import",
                False,
                error_code="UNEXPECTED_EXCEPTION",
                message=str(e),
            )
        )

    # --- class Type-First fields parse in isolation ---
    try:
        src = """
package t
class Env {
    Length L = 1.0.m
    Delta<Time> dt = 0.1.s
}
pub fn main() -> Unit {
    State x = Dirac(0)
    Measure x
}
"""
        from compiler.staqex.ast_nodes import ClassDecl  # noqa: E402
        from compiler.staqex.lexer import Lexer  # noqa: E402
        from compiler.staqex.parser import Parser  # noqa: E402

        tokens, _ = Lexer(src).tokenize()
        unit = Parser(tokens).parse()
        classes = [d for d in unit.decls if isinstance(d, ClassDecl)]
        if not classes or len(classes[0].fields) != 2:
            raise AssertionFailure(
                "PARSE_ERROR", f"expected 2 class fields, got {classes}"
            )
        out.append(
            CaseResult(
                "SV-31",
                "sv31-class-fields",
                "class Type-First fields parse",
                True,
                ["class", "Type-First"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-31",
                "sv31-class-fields",
                "class fields",
                False,
                error_code=e.code,
                message=str(e),
            )
        )
    except Exception as e:  # noqa: BLE001
        out.append(
            CaseResult(
                "SV-31",
                "sv31-class-fields",
                "class fields",
                False,
                error_code="UNEXPECTED_EXCEPTION",
                message=str(e),
            )
        )

    return out
