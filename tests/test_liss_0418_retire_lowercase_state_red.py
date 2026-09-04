"""AT-TDD Phase 1 Red -> Green: retire lowercase `state`.

Target: docs/issues/LISS-0418-retire-lowercase-state.md.
"""

from __future__ import annotations

from canonical_execution import run_canonical

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.runtime.evaluator import Evaluator  # noqa: E402


def test_capitalized_state_bare_form_is_unaffected() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = run_canonical(compiled, Evaluator(seed=0))
    assert result.measure is not None


def test_capitalized_state_tuple_form_is_unaffected() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        State (a, b) = (|0>, |+>)
        Measure a tracing_out b
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = run_canonical(compiled, Evaluator(seed=0))
    assert result.measure is not None


def test_lowercase_state_bare_form_is_rejected_with_migration_diagnostic() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        state a = |0>
        Measure a
    }
    """
    compiled = compile_source(src)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "STATE_KEYWORD_RETIRED" in codes, compiled.diagnostics
    assert compiled.unit is None


def test_lowercase_state_tuple_form_is_rejected_with_migration_diagnostic() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        state (a, b) = (|0>, |+>)
        Measure a tracing_out b
    }
    """
    compiled = compile_source(src)
    codes = {d.get("code") for d in compiled.diagnostics}
    assert "STATE_KEYWORD_RETIRED" in codes, compiled.diagnostics
    assert compiled.unit is None


def test_state_is_usable_as_an_ordinary_identifier() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        Int state = 5
        Int y = state + 1
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = run_canonical(compiled, Evaluator(seed=0))
    assert result.measure is not None
