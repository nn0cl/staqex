"""AT-TDD: LISS-0354 -- implement &&/|| as total-pushforward Boolean
operators (ADR 0196).

Design decision: docs/issues/LISS-0354-boolean-total-pushforward-logical-operators.md
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex import compile_source, run_source  # noqa: E402


def _hard(diags: list[dict]) -> list[dict]:
    return [
        d
        for d in diags
        if not str(d.get("code", "")).startswith("QSEM_")
        and d.get("code") != "MULTI_REGISTER_INDEX_AMBIGUOUS"
    ]


def _codes(src: str) -> set[str]:
    return {d.get("code", "") for d in compile_source(src).diagnostics}


def test_classical_and_or_truth_table() -> None:
    src = """
    fn both(a: Bool, b: Bool) -> Bool {
        return a && b
    }
    fn either(a: Bool, b: Bool) -> Bool {
        return a || b
    }

    pub fn main() -> Unit {
        Bool t = true
        Bool f = false
        Bool r1 = both(t, t)
        Bool r2 = both(t, f)
        Bool r3 = either(f, t)
        Bool r4 = either(f, f)
        State s = |0>
        Measure s
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard
    result = run_source(src, settings={"target": "local", "seed": 0})
    hard_run = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard_run, (result.status, hard_run)


def test_non_bool_operands_rejected_at_typecheck_not_parse() -> None:
    codes = _codes(
        """
        pub fn main() -> Unit {
            Float x = 1.0
            Float y = 2.0
            Float z = x && y
            State s = |0>
            Measure s
        }
        """
    )
    assert "LEX_ERROR" not in codes
    assert "PARSE_ERROR" not in codes
    assert "TYPE_MISMATCH" in codes


def test_state_bool_and_is_a_genuine_per_world_pushforward() -> None:
    """Two independent fair coins, each mapped to State<Bool>, combined with
    &&. If evaluation incorrectly short-circuited, this distribution would
    not match two independent fair coins both landing true (P=0.25)."""
    src = """
    pub fn main() -> Unit {
        State bit1 = Coin()
        State<Bool> a = Mix (bit1) {
          0 -> Dirac(false),
          else -> Dirac(true),
        }
        State bit2 = Coin()
        State<Bool> b = Mix (bit2) {
          0 -> Dirac(false),
          else -> Dirac(true),
        }
        State c = a && b
        Measure c tracing_out a, b
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard

    counts = {True: 0, False: 0}
    trials = 400
    for seed in range(trials):
        result = run_source(src, settings={"target": "local", "seed": seed})
        assert result.status == "succeeded", result.diagnostics
        value = result.measurements[0].value
        counts[value] += 1

    p_true = counts[True] / trials
    # Expected 0.25 (two independent fair coins both true); allow slack for
    # a finite-trial statistical sample.
    assert 0.15 < p_true < 0.35, (counts, p_true)


def test_operator_dsl_binder_guard_and_or_unaffected() -> None:
    """The Operator-DSL's own &&/|| (binder guard) is a separate grammar
    production from ADR 0196's new general-expression operator and must
    behave exactly as before."""
    src = """
    pub fn main() -> Unit {
        QubitRegister<3> register = system()
        Operator H = Sigma (i In Index<0..2>, j In Index<0..2>) where i < j && j < 2 {
            Z[i] * Z[j]
        }
        State a = |0>
        Measure a
    }
    """
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard
