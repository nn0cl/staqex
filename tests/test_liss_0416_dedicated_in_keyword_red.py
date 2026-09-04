"""AT-TDD Phase 1 Red -> Green: dedicated `In` keyword.

Target: docs/issues/LISS-0416-dedicated-in-keyword.md.

`In` (LISS-0416) is reserved ahead of its consumer (LISS-0420's `Sigma`/`Pi`
binder) -- a genuinely separate token from lowercase `in`, not a case-
insensitive alias. No grammar production accepts `In` yet; that is expected
until LISS-0420 lands.
"""

from __future__ import annotations

from canonical_execution import run_canonical

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.lexer import Lexer  # noqa: E402
from compiler.staqex.tokens import TokenKind  # noqa: E402


def test_capital_in_lexes_as_distinct_token_kind() -> None:
    tokens, diags = Lexer("In").tokenize()
    assert not diags, diags
    assert tokens[0].kind == TokenKind.IN_SET
    assert tokens[0].lexeme == "In"


def test_lowercase_in_lexes_unaffected() -> None:
    tokens, diags = Lexer("in").tokenize()
    assert not diags, diags
    assert tokens[0].kind == TokenKind.IN
    assert tokens[0].lexeme == "in"


def test_forEach_lowercase_in_is_unaffected() -> None:
    from compiler.staqex.pipeline import compile_source
    from compiler.staqex.runtime.evaluator import Evaluator

    src = """
    package t
    pub fn main() -> Unit {
        ForEach q in register(2) {
            apply(X, q)
        }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = run_canonical(compiled, Evaluator(seed=0))
    assert result.measure is not None


def test_operator_dsl_sum_binder_lowercase_in_is_unaffected() -> None:
    """Regression guard: sum/product's own `in` stays lowercase until
    LISS-0420 migrates the binder itself -- not touched by this Issue."""
    from compiler.staqex.pipeline import compile_source
    from compiler.staqex.runtime.evaluator import Evaluator

    src = """
    package t
    pub fn main() -> Unit {
        Energy scale = 1.0.eV to J
        Operator H_raw = Sigma (i In 0..1) { Z[i] }
        Operator H = scale * H_raw
        State (a, b) = (|0>, |0>)
        State (a, b) = Evolve { (a, b) under H for 0.1.fs }.run()
        Measure a tracing_out b
    }
    """
    compiled = compile_source(src)
    assert compiled.unit is not None, compiled.diagnostics
    result = run_canonical(compiled, Evaluator(seed=0))
    assert result.measure is not None
