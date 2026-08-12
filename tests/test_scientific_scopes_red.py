"""AT-TDD Phase 1 Red: LISS-0034 scientific scope separation."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_scope_blocks_resolve_independently_of_source_order() -> None:
    compiled = compile_source(
        """
        package t
        execution StudyRun {
            experiment = CriticalPoint
            shots = 1000
        }
        theory Ising {
            Operator H = X + Z
        }
        experiment CriticalPoint {
            theory = Ising
            observable = H
        }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert compiled.scope_contracts is not None
    assert tuple(compiled.scope_contracts) == (
        "StudyRun",
        "Ising",
        "CriticalPoint",
    )
    assert compiled.scope_contracts["Ising"].kind == "theory"
    assert compiled.scope_contracts["CriticalPoint"].references == ("Ising",)
    assert compiled.scope_contracts["CriticalPoint"].sealed is True
    ising = next(scope for scope in compiled.unit.decls if scope.name == "Ising")
    assert len(ising.body_declarations) == 1
    assert ising.body_declarations[0].names == ["H"]


def test_scope_contracts_are_immutable() -> None:
    compiled = compile_source(
        """
        package t
        theory Ising { Operator H = X + Z }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert compiled.scope_contracts is not None
    try:
        compiled.scope_contracts["Ising"].name = "Changed"
        compiled.scope_contracts["Other"] = compiled.scope_contracts["Ising"]
    except (AttributeError, TypeError):
        pass
    else:
        raise AssertionError("scope contracts must be immutable")


def test_invalid_scope_direction_is_rejected() -> None:
    codes = _codes(
        """
        package t
        theory Invalid { uses = Run }
        execution Run { shots = 1000 }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "PHASE_SCOPE_DIRECTION_ERROR" in codes


def test_execution_symbols_are_invisible_to_theory() -> None:
    codes = _codes(
        """
        package t
        theory Invalid {
            Operator H = shots * X
        }
        execution Run { shots = 1000 }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "PHASE_SCOPE_DEPENDENCY_ERROR" in codes


def test_scope_cycle_is_rejected_before_lowering() -> None:
    codes = _codes(
        """
        package t
        theory A { uses = B }
        experiment B { theory = A }
        pub fn main() -> Unit {
            State<Int> observed = Coin()
            Measure observed
        }
        """
    )

    assert "PHASE_SCOPE_CYCLE_ERROR" in codes


if __name__ == "__main__":
    for test in (
        test_scope_blocks_resolve_independently_of_source_order,
        test_scope_contracts_are_immutable,
        test_invalid_scope_direction_is_rejected,
        test_execution_symbols_are_invisible_to_theory,
        test_scope_cycle_is_rejected_before_lowering,
    ):
        test()
    print("OK — scientific scope tests")
