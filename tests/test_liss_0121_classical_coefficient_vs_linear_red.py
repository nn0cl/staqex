"""AT-TDD Phase 1 Red: LISS-0121 / ADR 0114 classical coefficient vs LINEAR.

Physicist-first: ``Float J`` (and struct fields) used only as Operator /
binder coefficients must not be treated as linear quantum resources.
True ``state`` values remain LINEAR. Fail-closed when coefficients are
misused as Measure/when subjects or depend on unmeasured quantum state.
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


def _codes(source: str) -> set[str]:
    return {d.get("code", "") for d in (compile_source(source).diagnostics or [])}


def _linear_codes(source: str) -> set[str]:
    return {
        c
        for c in _codes(source)
        if c in {"LINEAR_IMPLICIT_DISCARD", "LINEAR_DUPLICATE_USE"}
    }


def _run(source: str, *, seed: int = 7):
    return run_source(source, seed=seed, stdout=io.StringIO())


# --- EARS 1 / D2: named coefficient in binder + outside binder ---------------

_NAMED_IN_BINDER = """
package t
pub fn main() -> Unit {
    QubitRegister<4> register = system()
    Float J = 1.0545718e-19
    Operator H = sum (i in Index<0..2>) {
        J * Z[i] * Z[next(i)]
    }
    State a = |+>
    State b = |0>
    State c = |0>
    State d = |0>
    State (a, b, c, d) = Evolve { (a, b, c, d) under H for 0.1.fs using Suzuki(order = 2, steps = 4) }.run()
    State b = |0>
        State b = |0>
    State c = |0>
    State d = |0>
Measure a
}
"""

_LITERAL_IN_BINDER = """
package t
pub fn main() -> Unit {
    QubitRegister<4> register = system()
    Operator H = sum (i in Index<0..2>) {
        1.0545718e-19 * Z[i] * Z[next(i)]
    }
    State a = |+>
    State b = |0>
    State c = |0>
    State d = |0>
    State (a, b, c, d) = Evolve { (a, b, c, d) under H for 0.1.fs using Suzuki(order = 2, steps = 4) }.run()
    State b = |0>
        State b = |0>
    State c = |0>
    State d = |0>
Measure a
}
"""

_NAMED_OUTSIDE_BINDER = """
package t
pub fn main() -> Unit {
    Float hx = 2.6364295e-20
    Operator H = hx * X
    State psi = |+>
    State psi = Evolve { psi under H for 0.1.fs }.run()
    Measure psi
}
"""

_LITERAL_OUTSIDE_BINDER = """
package t
pub fn main() -> Unit {
    Operator H = 2.6364295e-20 * X
    State psi = |+>
    State psi = Evolve { psi under H for 0.1.fs }.run()
    Measure psi
}
"""

_STRUCT_FIELD_COEFF = """
package t
namespace Dom {
    pub struct Couplings {
        val h_x: Float
    }
}
pub fn main() -> Unit {
    Dom.Couplings c = Dom.Couplings(2.6364295e-20)
    Operator H = c.h_x * X
    State psi = |+>
    State psi = Evolve { psi under H for 0.1.fs }.run()
    Measure psi
}
"""


def test_named_float_coefficient_in_binder_has_no_linear_discard() -> None:
    compiled = compile_source(_NAMED_IN_BINDER)
    on_j = [
        d.get("message", "")
        for d in (compiled.diagnostics or [])
        if d.get("code") in {"LINEAR_IMPLICIT_DISCARD", "LINEAR_DUPLICATE_USE"}
        and "`J`" in d.get("message", "")
    ]
    assert on_j == [], on_j


def test_named_float_coefficient_outside_binder_has_no_linear_discard() -> None:
    compiled = compile_source(_NAMED_OUTSIDE_BINDER)
    on_hx = [
        d.get("message", "")
        for d in (compiled.diagnostics or [])
        if d.get("code") in {"LINEAR_IMPLICIT_DISCARD", "LINEAR_DUPLICATE_USE"}
        and "`hx`" in d.get("message", "")
    ]
    assert on_hx == [], on_hx


def test_named_coefficient_run_matches_literal_binder() -> None:
    named = _run(_NAMED_IN_BINDER)
    literal = _run(_LITERAL_IN_BINDER)
    # Green must not leave LINEAR on J even if runtime currently evaluates.
    named_linear_on_j = [
        d
        for d in (compile_source(_NAMED_IN_BINDER).diagnostics or [])
        if d.get("code") == "LINEAR_IMPLICIT_DISCARD" and "`J`" in d.get("message", "")
    ]
    assert not named_linear_on_j, named_linear_on_j
    assert named.ok, named
    assert literal.ok, literal
    assert named.eval is not None and literal.eval is not None
    assert named.eval.measure.marginal == literal.eval.measure.marginal


def test_named_coefficient_run_matches_literal_outside_binder() -> None:
    named_linear_on_hx = [
        d
        for d in (compile_source(_NAMED_OUTSIDE_BINDER).diagnostics or [])
        if d.get("code") == "LINEAR_IMPLICIT_DISCARD" and "`hx`" in d.get("message", "")
    ]
    assert not named_linear_on_hx, named_linear_on_hx
    named = _run(_NAMED_OUTSIDE_BINDER)
    literal = _run(_LITERAL_OUTSIDE_BINDER)
    assert named.ok, named
    assert literal.ok, literal
    assert named.eval is not None and literal.eval is not None
    assert named.eval.measure.marginal == literal.eval.measure.marginal


def test_struct_field_coefficient_in_operator_compiles_and_runs() -> None:
    codes = _codes(_STRUCT_FIELD_COEFF)
    assert "PARSE_ERROR" not in codes, codes
    assert "LINEAR_IMPLICIT_DISCARD" not in codes, codes
    result = _run(_STRUCT_FIELD_COEFF)
    assert result.ok, result


# --- EARS 2: true quantum state still LINEAR ---------------------------------

_DISCARDED_STATE = """
package t
pub fn main() -> Unit {
    State q = |+>
    State viewed = Inspect(|0>)
    Measure viewed
}
"""


def test_unconsumed_quantum_state_still_linear_implicit_discard() -> None:
    assert "LINEAR_IMPLICIT_DISCARD" in _codes(_DISCARDED_STATE)


# --- EARS 3: open coefficient depending on unmeasured quantum — fail-closed --

_QUANTUM_DEPENDENT_COEFF = """
package t
pub fn main() -> Unit {
    State amp = |+>
    Operator H = amp * X
    State psi = |0>
    State psi = Evolve { psi under H for 0.1 }.run()
    Measure psi
}
"""


def test_quantum_dependent_coefficient_is_explicitly_rejected() -> None:
    compiled = compile_source(_QUANTUM_DEPENDENT_COEFF)
    assert compiled.ok is False
    assert compiled.diagnostics, "expected an explicit diagnostic, not silence"


# --- EARS 4: misuse as Measure / when subject -------------------------------

_MEASURE_COEFFICIENT = """
package t
pub fn main() -> Unit {
    Float J = 1.0
    Measure J
}
"""

_WHEN_ON_COEFFICIENT = """
package t
pub fn main() -> Unit {
    Float J = 1.0
    State label = Mix (J) {
      0 -> 0,
      else -> 1,
    }
    Measure label
}
"""


def test_measure_of_elaboration_coefficient_fail_closed() -> None:
    compiled = compile_source(_MEASURE_COEFFICIENT)
    assert compiled.ok is False
    blob = " ".join(
        f"{d.get('code', '')} {d.get('message', '')}".lower()
        for d in (compiled.diagnostics or [])
    )
    assert (
        "coefficient" in blob
        or "classical" in blob
        or "cannot_measure" in blob
    ), blob


def test_when_control_on_elaboration_coefficient_fail_closed() -> None:
    compiled = compile_source(_WHEN_ON_COEFFICIENT)
    assert compiled.ok is False
    blob = " ".join(
        f"{d.get('code', '')} {d.get('message', '')}".lower()
        for d in (compiled.diagnostics or [])
    )
    assert "coefficient" in blob or "classical" in blob or "when" in blob, blob


# --- EARS 5: fold invariant (named vs literal diagnostics parity) -----------

def test_named_and_literal_coefficient_share_linear_diagnostic_shape() -> None:
    """Named J must not add LINEAR on the coefficient that literal lacks."""

    def linear_on_coeff(source: str, name: str) -> list[str]:
        return [
            d.get("message", "")
            for d in (compile_source(source).diagnostics or [])
            if d.get("code") == "LINEAR_IMPLICIT_DISCARD"
            and f"`{name}`" in d.get("message", "")
        ]

    assert linear_on_coeff(_LITERAL_IN_BINDER, "J") == []
    assert linear_on_coeff(_NAMED_IN_BINDER, "J") == [], linear_on_coeff(
        _NAMED_IN_BINDER, "J"
    )


if __name__ == "__main__":
    tests = [
        test_named_float_coefficient_in_binder_has_no_linear_discard,
        test_named_float_coefficient_outside_binder_has_no_linear_discard,
        test_named_coefficient_run_matches_literal_binder,
        test_named_coefficient_run_matches_literal_outside_binder,
        test_struct_field_coefficient_in_operator_compiles_and_runs,
        test_unconsumed_quantum_state_still_linear_implicit_discard,
        test_quantum_dependent_coefficient_is_explicitly_rejected,
        test_measure_of_elaboration_coefficient_fail_closed,
        test_when_control_on_elaboration_coefficient_fail_closed,
        test_named_and_literal_coefficient_share_linear_diagnostic_shape,
    ]
    passed = failed = 0
    for test in tests:
        try:
            test()
            passed += 1
            print(f"PASS: {test.__name__}")
        except Exception as exc:  # noqa: BLE001 -- suite report
            failed += 1
            print(f"FAIL: {test.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{passed} passed, {failed} failed (LISS-0121)")
    raise SystemExit(0 if failed == 0 else 1)
