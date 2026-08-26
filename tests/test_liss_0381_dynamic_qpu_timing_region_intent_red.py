"""AT-TDD Phase 1 Red: LISS-0381 Dynamic QPU timing intent (ADR 0193).

Target behavior is docs/specs/staqex-dynamic-qpu-lane.md § "Acceptance
scenarios — timing intent (ADR 0193, LISS-0381)", including vision §2.2
composition-stability scenarios. Kernel grammar/AST + Quantum Semantic IR
witness only; the dynamic lane remains non-executable.

These tests intentionally describe the not-yet-implemented behavior and
must fail against the current compiler, which only accepts
`dynamic qpu { … }` (no `within`), has no `timing_intent` field, and
emits no `TimingRegion`.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import get_args

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import DynamicQpuStmt, Stmt  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(diagnostics: list[dict[str, object]]) -> set[str]:
    return {str(d.get("code", "")) for d in diagnostics}


def _dynamic_stmts(compiled) -> list[DynamicQpuStmt]:
    if compiled.unit is None or compiled.unit.main is None:
        return []
    return [
        stmt
        for stmt in compiled.unit.main.body.stmts
        if isinstance(stmt, DynamicQpuStmt)
    ]


def _timing_regions(compiled) -> list[object]:
    if compiled.quantum_semantic_ir is None:
        return []
    return [
        region
        for region in compiled.quantum_semantic_ir.regions
        if type(region).__name__ == "TimingRegion"
    ]


def _timing_intents(compiled) -> set[str]:
    return {
        str(getattr(region, "timing_intent"))
        for region in _timing_regions(compiled)
    }


_SOURCE_WITHIN_COHERENT = """
package t
pub fn main() -> Unit {
    dynamic qpu within coherent_window {
        State<Int> flag = Coin()
        Measure flag
    }
    State<Int> observed = Coin()
    Measure observed
}
"""

_SOURCE_WITHIN_IDLE = """
package t
pub fn main() -> Unit {
    dynamic qpu within idle_window {
        State<Int> flag = Coin()
        Measure flag
    }
    State<Int> observed = Coin()
    Measure observed
}
"""

_SOURCE_NO_WITHIN = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        State<Int> flag = Coin()
        Measure flag
    }
    State<Int> observed = Coin()
    Measure observed
}
"""

_SOURCE_MALFORMED_WITHIN = """
package t
pub fn main() -> Unit {
    dynamic qpu within {
        State<Int> flag = Coin()
        Measure flag
    }
    State<Int> observed = Coin()
    Measure observed
}
"""

_SOURCE_EVOLVE_INSIDE_WITHIN = """
package t
pub fn main() -> Unit {
    dynamic qpu within coherent_window {
        State psi = |0>
        Operator H = X
        State psi = Evolve { psi under H for 1.0.s }.run()
        Measure psi
    }
    State<Int> observed = Coin()
    Measure observed
}
"""

_SOURCE_TWO_WITHIN_ONE_MAIN = """
package t
pub fn main() -> Unit {
    dynamic qpu within coherent_window {
        State<Int> flag = Coin()
        Measure flag
    }
    dynamic qpu within idle_window {
        State<Int> other = Coin()
        Measure other
    }
    State<Int> observed = Coin()
    Measure observed
}
"""

_SOURCE_WITHIN_LITERAL = """
package t
pub fn main() -> Unit {
    dynamic qpu within 1 {
        State<Int> flag = Coin()
        Measure flag
    }
    State<Int> observed = Coin()
    Measure observed
}
"""

_SOURCE_WITHIN_CALL = """
package t
pub fn main() -> Unit {
    dynamic qpu within foo(bar) {
        State<Int> flag = Coin()
        Measure flag
    }
    State<Int> observed = Coin()
    Measure observed
}
"""

_SOURCE_WITHIN_AS_IDENTIFIER = """
package t
pub fn main() -> Unit {
    State<Int> within = Coin()
    Measure within
}
"""

_SOURCE_ADJACENT_STATIC_AND_DYNAMIC = """
package t
pub fn main() -> Unit {
    State psi = |0>
    Operator H = X
    State psi = Evolve { psi under H for 1.0.s }.run()
    dynamic qpu within coherent_window {
        State<Int> flag = Coin()
        Measure flag
    }
    Measure psi
}
"""


def test_optional_within_clause_is_accepted_on_dynamic_qpu() -> None:
    """Scenario: optional within clause is accepted on dynamic qpu."""
    compiled = compile_source(_SOURCE_WITHIN_COHERENT)
    stmts = _dynamic_stmts(compiled)
    codes = _codes(compiled.diagnostics)

    assert len(stmts) == 1
    assert stmts[0].timing_intent == "coherent_window"
    assert DynamicQpuStmt in get_args(Stmt)
    assert "DYNAMIC_CAPABILITY_REQUIRED_ERROR" in codes
    assert "DYNAMIC_UNSUPPORTED_FEATURE_ERROR" in codes


def test_dynamic_qpu_without_within_remains_valid_and_unchanged() -> None:
    """Scenario: dynamic qpu without within remains valid and unchanged."""
    compiled = compile_source(_SOURCE_NO_WITHIN)
    stmts = _dynamic_stmts(compiled)
    codes = _codes(compiled.diagnostics)

    assert len(stmts) == 1
    assert stmts[0].timing_intent is None
    assert _timing_regions(compiled) == []
    assert "DYNAMIC_CAPABILITY_REQUIRED_ERROR" in codes
    assert "DYNAMIC_UNSUPPORTED_FEATURE_ERROR" in codes


def test_timing_region_carries_source_derived_timing_intent() -> None:
    """Scenario: TimingRegion carries the source-derived timing intent."""
    compiled = compile_source(_SOURCE_WITHIN_COHERENT)
    regions = _timing_regions(compiled)

    assert len(regions) == 1
    assert getattr(regions[0], "timing_intent") == "coherent_window"
    assert getattr(regions[0], "timing_intent") != "S02.feasible"
    assert getattr(regions[0], "timing_intent") != "placeholder"


def test_different_timing_names_produce_distinguishable_timing_regions() -> None:
    """Scenario: different timing names produce distinguishable TimingRegions."""
    coherent = compile_source(_SOURCE_WITHIN_COHERENT)
    idle = compile_source(_SOURCE_WITHIN_IDLE)
    coherent_regions = _timing_regions(coherent)
    idle_regions = _timing_regions(idle)

    assert len(coherent_regions) == 1
    assert len(idle_regions) == 1
    assert getattr(coherent_regions[0], "timing_intent") == "coherent_window"
    assert getattr(idle_regions[0], "timing_intent") == "idle_window"
    assert getattr(coherent_regions[0], "timing_intent") != getattr(
        idle_regions[0], "timing_intent"
    )


def test_malformed_within_clause_fails_closed() -> None:
    """Scenario: malformed within clause fails closed."""
    compiled = compile_source(_SOURCE_MALFORMED_WITHIN)
    codes = _codes(compiled.diagnostics)

    assert "DYNAMIC_TIMING_INTENT_MALFORMED" in codes
    assert compiled.unit is None or _dynamic_stmts(compiled) == []


def test_timing_intent_does_not_make_the_lane_executable() -> None:
    """Scenario: timing intent does not make the lane executable."""
    with_within = compile_source(_SOURCE_WITHIN_COHERENT)
    without = compile_source(_SOURCE_NO_WITHIN)

    for compiled in (with_within, without):
        codes = _codes(compiled.diagnostics)
        assert "DYNAMIC_CAPABILITY_REQUIRED_ERROR" in codes
        assert "DYNAMIC_UNSUPPORTED_FEATURE_ERROR" in codes
        assert compiled.ok is False


def test_evolve_under_for_inside_within_keeps_timing_intent() -> None:
    """Scenario: Evolve under/for inside within keeps timing intent."""
    compiled = compile_source(_SOURCE_EVOLVE_INSIDE_WITHIN)
    stmts = _dynamic_stmts(compiled)
    codes = _codes(compiled.diagnostics)
    regions = _timing_regions(compiled)

    assert len(stmts) == 1
    assert stmts[0].timing_intent == "coherent_window"
    assert len(regions) == 1
    assert getattr(regions[0], "timing_intent") == "coherent_window"
    assert "DYNAMIC_CAPABILITY_REQUIRED_ERROR" in codes
    assert "DYNAMIC_UNSUPPORTED_FEATURE_ERROR" in codes


def test_multiple_within_blocks_in_one_program_yield_multiple_timing_regions() -> None:
    """Scenario: multiple within blocks in one program yield multiple TimingRegions."""
    compiled = compile_source(_SOURCE_TWO_WITHIN_ONE_MAIN)
    stmts = _dynamic_stmts(compiled)
    codes = _codes(compiled.diagnostics)

    assert len(stmts) == 2
    assert {stmt.timing_intent for stmt in stmts} == {
        "coherent_window",
        "idle_window",
    }
    assert _timing_intents(compiled) == {"coherent_window", "idle_window"}
    assert len(_timing_regions(compiled)) == 2
    assert "DYNAMIC_CAPABILITY_REQUIRED_ERROR" in codes
    assert "DYNAMIC_UNSUPPORTED_FEATURE_ERROR" in codes


def test_non_identifier_timing_intent_fails_closed() -> None:
    """Scenario: non-identifier timing intent fails closed."""
    for source in (_SOURCE_WITHIN_LITERAL, _SOURCE_WITHIN_CALL):
        compiled = compile_source(source)
        codes = _codes(compiled.diagnostics)
        assert "DYNAMIC_TIMING_INTENT_MALFORMED" in codes
        assert compiled.unit is None or all(
            getattr(stmt, "timing_intent", None) is None
            for stmt in _dynamic_stmts(compiled)
        )


def test_within_remains_usable_as_ordinary_identifier_outside_clause() -> None:
    """Scenario: within remains usable as an ordinary identifier outside the clause."""
    compiled = compile_source(_SOURCE_WITHIN_AS_IDENTIFIER)
    codes = _codes(compiled.diagnostics)

    assert "DYNAMIC_TIMING_INTENT_MALFORMED" not in codes
    assert "PARSE_ERROR" not in codes
    assert compiled.unit is not None
    assert compiled.ok


def test_adjacent_static_evolve_and_dynamic_within_do_not_corrupt_each_other() -> None:
    """Scenario: adjacent Static Evolve and dynamic within do not corrupt each other."""
    compiled = compile_source(_SOURCE_ADJACENT_STATIC_AND_DYNAMIC)
    stmts = _dynamic_stmts(compiled)
    codes = _codes(compiled.diagnostics)
    regions = _timing_regions(compiled)

    assert len(stmts) == 1
    assert stmts[0].timing_intent == "coherent_window"
    assert len(regions) == 1
    assert getattr(regions[0], "timing_intent") == "coherent_window"
    assert "DYNAMIC_CAPABILITY_REQUIRED_ERROR" in codes
    assert "DYNAMIC_UNSUPPORTED_FEATURE_ERROR" in codes
    # Static evolve must remain present in the AST (not dropped for within).
    assert compiled.unit is not None and compiled.unit.main is not None
    assert any(
        type(stmt).__name__ == "StateBind"
        for stmt in compiled.unit.main.body.stmts
    )
