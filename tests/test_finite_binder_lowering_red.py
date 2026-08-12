"""Acceptance tests for LISS-0043 finite binder lowering."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def _main(operator: str):
    return f"""
    package t
    pub fn main() -> Unit {{
        QubitRegister<4> register = system()
        Operator H = {operator}
        State<Int> observed = Coin()
        Measure observed
    }}
    """


def test_inclusive_range_resolves_open_chain_to_concrete_pauli_terms() -> None:
    compiled = compile_source(
        _main(
            """
            sum (i in Index<0..2>) {
                1.0 * Z[i] * Z[next(i)]
            }
            """
        )
    )

    assert compiled.ok, compiled.diagnostics
    lowering = compiled.qpu_ir["binder_lowering"]["H"]
    assert lowering["domain"] == {"start": 0, "end": 2, "inclusive": True}
    assert lowering["expanded_terms"] == 3
    assert lowering["resource_check"] == "passed"
    assert lowering["operator_tree"]["kind"] == "Sum"
    assert len(lowering["operator_tree"]["terms"]) == 3
    assert lowering["provenance"]["binder_variable"] == "i"
    assert lowering["provenance"]["expanded_terms"] == 3


def test_open_boundary_rejects_next_of_the_last_index() -> None:
    codes = _codes(
        _main(
            """
            sum (i in Index<0..3>) {
                1.0 * Z[i] * Z[next(i)]
            }
            """
        )
    )

    assert "BINDER_INDEX_OUT_OF_BOUNDS" in codes


def test_reversed_or_empty_inclusive_range_is_a_warning() -> None:
    codes = _codes(
        _main(
            """
            sum (i in Index<2..1>) {
                1.0 * Z[i]
            }
            """
        )
    )

    assert "EMPTY_BINDER_DOMAIN_WARNING" in codes
    assert "BINDER_DOMAIN_ERROR" not in codes


def test_range_beyond_register_shape_is_a_domain_error() -> None:
    codes = _codes(
        _main(
            """
            sum (i in Index<0..4>) {
                1.0 * Z[i]
            }
            """
        )
    )

    assert "BINDER_DOMAIN_ERROR" in codes


def test_expansion_budget_is_hard_error_without_truncation() -> None:
    codes = _codes(
        _main(
            """
            sum (i in Index<0..1000000000>) {
                1.0 * Z[i]
            }
            """
        )
    )

    assert "BINDER_RESOURCE_ERROR" in codes


if __name__ == "__main__":
    for test in (
        test_inclusive_range_resolves_open_chain_to_concrete_pauli_terms,
        test_open_boundary_rejects_next_of_the_last_index,
        test_reversed_or_empty_inclusive_range_is_a_warning,
        test_range_beyond_register_shape_is_a_domain_error,
        test_expansion_budget_is_hard_error_without_truncation,
    ):
        test()
    print("OK — finite binder lowering tests")
