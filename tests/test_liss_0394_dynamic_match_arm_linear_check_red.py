"""AT-TDD Phase 1 Red: LISS-0394 linear-use checking inside dynamic-lane
`match` arms.

Target: docs/issues/LISS-0394-dynamic-match-arm-linear-check.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(diagnostics) -> set[str]:
    return {str(d.get("code", "")) for d in diagnostics}


def test_reset_of_unknown_wire_inside_match_arm_fails_closed() -> None:
    """Scenario 1: reset of an unknown wire inside a match arm now fails
    closed with DYN_RESET_UNKNOWN_WIRE (previously silently unchecked --
    MatchStmt arm bodies were never visited by the linear-use checker).
    """
    source = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        State q = |0>
        Controller<Bit> bit = measure q
        match bit {
            0 => { reset ghost }
            1 => { }
        }
    }
    State<Int> observed = coin()
    measure observed
}
"""
    compiled = compile_source(source)
    codes = _codes(compiled.diagnostics)

    assert "DYN_RESET_UNKNOWN_WIRE" in codes


def test_reset_of_wire_known_from_before_the_match_does_not_false_positive() -> None:
    """Scenario 2: reset of a wire already known (Controller-measured)
    before the match, used inside an arm, must NOT false-positive as
    unknown -- the shared-state design's core claim.
    """
    source = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        State q = |0>
        Controller<Bit> bit = measure q
        match bit {
            0 => { reset q }
            1 => { }
        }
    }
    State<Int> observed = coin()
    measure observed
}
"""
    compiled = compile_source(source)
    codes = _codes(compiled.diagnostics)

    assert "DYN_RESET_UNKNOWN_WIRE" not in codes


def test_measure_only_fixture_still_produces_no_implicit_discard() -> None:
    """Scenario 3 (regression guard): LISS-0387's measure-only fixture
    (measure, then arms with no reset) must still produce NO
    LINEAR_IMPLICIT_DISCARD. This is exactly the false-positive the
    rejected "seeded nested _analyze_block per arm" design would have
    caused (q consumed before the match would appear undischarged inside
    each arm's own fresh state) -- proves the shared-state design avoids
    it.
    """
    source = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        State q = |0>
        Controller<Bit> bit = measure q
        match bit {
            0 => { }
            1 => { }
        }
    }
    State<Int> observed = coin()
    measure observed
}
"""
    compiled = compile_source(source)
    codes = _codes(compiled.diagnostics)

    assert "LINEAR_IMPLICIT_DISCARD" not in codes


def test_nested_match_inside_arm_unknown_reset_is_still_caught() -> None:
    """Scenario 4: a match nested inside a match arm's body still gets its
    own arm bodies checked (recursion works).
    """
    source = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        State q = |0>
        Controller<Bit> bit = measure q
        match bit {
            0 => {
                match bit {
                    0 => { reset ghost_nested }
                    1 => { }
                }
            }
            1 => { }
        }
    }
    State<Int> observed = coin()
    measure observed
}
"""
    compiled = compile_source(source)
    codes = _codes(compiled.diagnostics)

    assert "DYN_RESET_UNKNOWN_WIRE" in codes


def test_top_level_reset_behavior_is_unaffected() -> None:
    """Regression guard: top-level (non-arm) reset diagnostics are
    unchanged by the _check_reset_stmt extraction (pure code motion).
    """
    source = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        State q = |0>
        Controller<Bit> bit = measure q
        reset ghost_top_level
    }
    State<Int> observed = coin()
    measure observed
}
"""
    compiled = compile_source(source)
    codes = _codes(compiled.diagnostics)

    assert "DYN_RESET_UNKNOWN_WIRE" in codes
