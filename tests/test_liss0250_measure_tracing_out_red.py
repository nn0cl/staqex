"""AT-TDD Phase 1 Red: LISS-0250 — `Measure … tracing_out …` (ADR 0173).

Gherkin (Then clauses drive assertions):

Feature: terminal Measure with explicit leftover partial trace
  Scenario: dialect ideal path compiles and runs without |0> hand-kill
    Given two live State carriers s0 and s1
    When main ends with `Measure s0 tracing_out s1`
    Then compile has no LINEAR_IMPLICIT_DISCARD / PARSE_ERROR
    And seed-0 evaluation yields a non-Vacuum Measure of s0
    And the residual joint has no s1 coordinate

  Scenario: unnamed leftover still discarded illegally
    Given s0, s1, s2 live and `Measure s0 tracing_out s1`
    Then LINEAR_IMPLICIT_DISCARD names s2

  Scenario: empty tracing_out list is rejected
    When `Measure s0 tracing_out`
    Then PARSE_ERROR (or equivalent fail-closed diagnostic)

  Scenario: primary listed as leftover is rejected
    When `Measure s0 tracing_out s0`
    Then LINEAR_DUPLICATE_USE (or TRACING_OUT_* with same obligation)

  Scenario: duplicate leftover names are rejected
    When `Measure s0 tracing_out s1, s1`
    Then LINEAR_DUPLICATE_USE (or TRACING_OUT_*)

  Scenario: Classical-bound trace_out consumes the State argument
    Given `Classical<Float> _t = trace_out(s1)` then `Measure s0`
    Then no LINEAR_IMPLICIT_DISCARD on s1
    And seed-0 evaluation succeeds
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402

_HARD = frozenset(
    {
        "LINEAR_IMPLICIT_DISCARD",
        "LINEAR_DUPLICATE_USE",
        "PARSE_ERROR",
        "LEX_ERROR",
        "TRACING_OUT_EMPTY",
        "TRACING_OUT_DUPLICATE",
        "TRACING_OUT_PRIMARY",
    }
)


def _codes(src: str) -> set[str]:
    return {str(d.get("code", "")) for d in compile_source(src).diagnostics}


def _hard(src: str) -> set[str]:
    return _codes(src) & _HARD


def _discard_messages(src: str) -> list[str]:
    return [
        str(d.get("message", ""))
        for d in compile_source(src).diagnostics
        if d.get("code") == "LINEAR_IMPLICIT_DISCARD"
    ]


def test_measure_tracing_out_compiles_without_hand_kill() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        State s0 = Coin()
        State s1 = Coin()
        Measure s0 tracing_out s1
    }
    """
    hard = _hard(src)
    assert "PARSE_ERROR" not in hard, hard
    assert "LINEAR_IMPLICIT_DISCARD" not in hard, hard
    assert "LINEAR_DUPLICATE_USE" not in hard, hard


def test_measure_tracing_out_runs_seed_zero_and_drops_leftover_coord() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        State s0 = |+>
        State s1 = |+>
        Measure s0 tracing_out s1
    }
    """
    result = run_source(src, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.vacuum is False
    assert result.eval.measure.value in (0, 1)
    coords = {name for w in result.eval.joint.worlds for name in w.assign}
    assert "s1" not in coords, coords
    assert "s0" in coords or result.eval.measure is not None


def test_unnamed_leftover_still_linear_implicit_discard() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        State s0 = Coin()
        State s1 = Coin()
        State s2 = Coin()
        Measure s0 tracing_out s1
    }
    """
    assert "LINEAR_IMPLICIT_DISCARD" in _codes(src)
    msgs = " ".join(_discard_messages(src))
    assert "s2" in msgs, msgs


def test_empty_tracing_out_list_is_rejected() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        State s0 = Coin()
        Measure s0 tracing_out
    }
    """
    codes = _codes(src)
    assert (
        "PARSE_ERROR" in codes
        or "TRACING_OUT_EMPTY" in codes
        or "LEX_ERROR" in codes
    ), codes


def test_primary_in_tracing_out_list_is_rejected() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        State s0 = Coin()
        Measure s0 tracing_out s0
    }
    """
    codes = _codes(src)
    assert (
        "LINEAR_DUPLICATE_USE" in codes
        or "TRACING_OUT_PRIMARY" in codes
        or "TRACING_OUT_DUPLICATE" in codes
    ), codes


def test_duplicate_tracing_out_names_are_rejected() -> None:
    src = """
    package t
    pub fn main() -> Unit {
        State s0 = Coin()
        State s1 = Coin()
        Measure s0 tracing_out s1, s1
    }
    """
    codes = _codes(src)
    assert (
        "LINEAR_DUPLICATE_USE" in codes
        or "TRACING_OUT_DUPLICATE" in codes
    ), codes


def test_classical_bound_trace_out_consumes_state_argument() -> None:
    """ADR 0173 companion: trace_out always consumes its State arg for LINEAR."""
    src = """
    package t
    pub fn main() -> Unit {
        State s0 = Coin()
        State s1 = Coin()
        Classical<Float> _t = trace_out(s1)
        Measure s0
    }
    """
    hard_discards = [
        d
        for d in compile_source(src).diagnostics
        if d.get("code") == "LINEAR_IMPLICIT_DISCARD"
        and "s1" in str(d.get("message", ""))
    ]
    assert hard_discards == [], hard_discards
    result = run_source(src, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.vacuum is False


if __name__ == "__main__":
    test_measure_tracing_out_compiles_without_hand_kill()
    print("PASS compile")
    test_measure_tracing_out_runs_seed_zero_and_drops_leftover_coord()
    print("PASS run")
    test_unnamed_leftover_still_linear_implicit_discard()
    print("PASS unnamed leftover")
    test_empty_tracing_out_list_is_rejected()
    print("PASS empty")
    test_primary_in_tracing_out_list_is_rejected()
    print("PASS primary")
    test_duplicate_tracing_out_names_are_rejected()
    print("PASS duplicate")
    test_classical_bound_trace_out_consumes_state_argument()
    print("PASS classical trace_out")
    print("OK")
