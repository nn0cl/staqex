"""AT-TDD: LISS-0129 typed `state name: State<T> = …` surface annotations.

LISS-0418 update: the colon-annotation surface form (`state x: State<T> =
e`) was a way to write an explicit `State<T>` annotation while still using
the `state` keyword (ADR 0115). Once lowercase `state` was retired
(LISS-0418, ADR 0191 amendment), this surface spelling has no reason to
exist -- the identical need is already covered by Type-First
(`State<T> x = e`, unaffected, still tested below). The colon form itself
now correctly fails to parse (no grammar accepts `name: Type` after a
Type-First head).
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import StateBind  # noqa: E402
from compiler.staqex.host import run_source  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(source).diagnostics}


def _main_binds(source: str) -> list[StateBind]:
    compiled = compile_source(source)
    assert compiled.unit is not None, compiled.diagnostics
    assert compiled.unit.main is not None
    return [
        stmt
        for stmt in compiled.unit.main.body.stmts
        if isinstance(stmt, StateBind)
    ]


def test_type_first_annotated_state_bind_parses_with_type_ref() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        State<Qubit> x = |0>
        measure x
    }
    """
    compiled = compile_source(source)
    assert "PARSE_ERROR" not in _codes(source), compiled.diagnostics
    binds = _main_binds(source)
    assert len(binds) == 1
    assert binds[0].names == ["x"]
    assert binds[0].ty is not None
    assert binds[0].ty.name == "State"
    assert binds[0].ty.args[0].name == "Qubit"


def test_type_first_annotated_state_bind_compiles_and_runs() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        State<Qubit> x = |0>
        measure x
    }
    """
    compiled = compile_source(source)
    hard = [
        d
        for d in compiled.diagnostics
        if d.get("code") not in {
            "QSEM_FINITE_EVIDENCE_MISSING",
            "QSEM_APPROXIMATION_OBLIGATION_MISSING",
        }
    ]
    assert compiled.ok or not hard, hard
    result = run_source(source, settings={"target": "local", "seed": 1}, stdout=io.StringIO())
    assert result.status == "succeeded", result.diagnostics


def test_type_first_annotation_mismatch_is_type_error() -> None:
    source = """
    package t
    pub fn main() -> Unit {
        State<Length> x = |0>
        measure x
    }
    """
    codes = _codes(source)
    assert "PARSE_ERROR" not in codes
    assert codes & {
        "TYPE_MISMATCH",
        "DIMENSION_MISMATCH_ERROR",
        "LOCAL_DIMENSION_TYPE_ERROR",
        "PRODUCT_TYPE_MISMATCH",
    }


def test_colon_annotation_surface_form_no_longer_parses() -> None:
    """LISS-0418: the `state x: State<T> = e` colon surface form is
    retired along with lowercase `state` itself -- `State x: ... = ...`
    (Type-First head followed by a colon) has no grammar production."""
    source = """
    package t
    pub fn main() -> Unit {
        State x: State<Qubit> = |0>
        measure x
    }
    """
    codes = _codes(source)
    assert "PARSE_ERROR" in codes


def test_type_first_and_inference_remain() -> None:
    tf = """
    package t
    pub fn main() -> Unit {
        State<Qubit> x = |0>
        measure x
    }
    """
    infer = """
    package t
    pub fn main() -> Unit {
        State x = |0>
        measure x
    }
    """
    assert "PARSE_ERROR" not in _codes(tf)
    assert "PARSE_ERROR" not in _codes(infer)


if __name__ == "__main__":
    test_type_first_annotated_state_bind_parses_with_type_ref()
    test_type_first_annotated_state_bind_compiles_and_runs()
    test_type_first_annotation_mismatch_is_type_error()
    test_colon_annotation_surface_form_no_longer_parses()
    test_type_first_and_inference_remain()
    print("OK — typed surface annotations")
