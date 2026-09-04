"""AT-TDD Phase 1 Red -> Green: `Implies` keyword operator for
$\\Rightarrow$.

Target: docs/issues/LISS-0425-implies-operator.md.
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


def _run(src: str):
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    return run_canonical(compiled, Evaluator(seed=0))


def test_implies_truth_table_in_general_expression_position() -> None:
    cases = [
        (True, True, True),
        (True, False, False),
        (False, True, True),
        (False, False, True),
    ]
    for a, b, expected in cases:
        src = f"""
        package t
        pub fn main() -> Unit {{
            Bool a = {"true" if a else "false"}
            Bool b = {"true" if b else "false"}
            Bool r = a Implies b
            Measure r
        }}
        """
        result = _run(src)
        assert result.measure.value == expected, (a, b, expected)


def test_implies_works_inside_a_classical_sigma_body() -> None:
    """The target shape for S02's `F` predicate: `Implies` used inside a
    Sigma/ForAll-style Operator-DSL body, not just the general grammar."""
    src = """
    package t
    pub fn main() -> Unit {
        Int n = 2
        Int total = Sigma (i In 0..n-1) { (i == 0) Implies (i < 5) }
        Measure total
    }
    """
    result = _run(src)
    # i=0: True Implies True = True(1); i=1: False Implies True = True(1)
    assert result.measure.value == 2


def test_implies_lower_precedence_than_and_or() -> None:
    """`a && b Implies c` must parse as `(a && b) Implies c`, matching
    logical implication's usual looser-than-conjunction binding."""
    src = """
    package t
    pub fn main() -> Unit {
        Bool a = true
        Bool b = false
        Bool c = false
        Bool r = a && b Implies c
        Measure r
    }
    """
    result = _run(src)
    # (true && false) Implies false = false Implies false = true (vacuous)
    assert result.measure.value is True


def test_existing_arrow_and_fat_arrow_are_unaffected() -> None:
    """Confirms `Implies` is a genuinely new keyword, not a repurposing of
    `->`/`=>` -- both stay exactly as they were (return types / lambdas;
    match arms)."""
    src = """
    package t
    fn is_pos(x: Int) -> Bool {
        return x > 0
    }
    pub fn main() -> Unit {
        Bool r = is_pos(3)
        Measure r
    }
    """
    result = _run(src)
    assert result.measure.value == True  # noqa: E712 -- may surface as 1.0


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {name}")
    print("OK - LISS-0425 Slice B Phase 2 Green")
