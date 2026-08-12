"""AT-TDD Phase 1 Red: explicit returns and lexical function scope."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _codes(source: str) -> set[str]:
    return {diagnostic.get("code", "") for diagnostic in compile_source(source).diagnostics}


def test_terminal_return_is_accepted_for_ordinary_function() -> None:
    codes = _codes(
        """
        pub fn build_observatory_coin() -> Operator {
            Operator walk_coin = (X + Z) * inv_sqrt2
            return walk_coin
        }

        pub fn main() -> Unit {
            State<Int> answer = Coin()
            Measure answer
        }
        """
    )

    assert "FORBIDDEN_KEYWORD" not in codes
    assert "PARSE_ERROR" not in codes


def test_implicit_final_expression_is_rejected() -> None:
    codes = _codes(
        """
        pub fn build_observatory_coin() -> Operator {
            Operator walk_coin = (X + Z) * inv_sqrt2
            walk_coin
        }

        pub fn main() -> Unit {
            State<Int> answer = Coin()
            Measure answer
        }
        """
    )

    assert "MISSING_RETURN_STATEMENT" in codes


def test_return_is_not_an_entry_point_escape() -> None:
    codes = _codes(
        """
        pub fn main() -> Unit {
            State<Int> answer = Coin()
            return answer
        }
        """
    )

    assert "MAIN_RETURN_ERROR" in codes


def test_function_local_operator_cannot_leak_to_sibling_function() -> None:
    codes = _codes(
        """
        pub fn build_observatory_coin() -> Operator {
            Operator walk_coin = (X + Z) * inv_sqrt2
            return walk_coin
        }

        pub fn walk_observatory_step(c: State<Qubit>) -> State<Qubit> {
            State<Qubit> next_c = apply(walk_coin, c)
            return next_c
        }

        pub fn main() -> Unit {
            State<Int> answer = Coin()
            Measure answer
        }
        """
    )

    assert "LEXICAL_SCOPE_ERROR" in codes


def test_init_cannot_return_a_value() -> None:
    codes = _codes(
        """
        class CoinBox {
            val operator: Operator

            fn init(value: Operator) {
                this.operator = value
                return value
            }
        }

        pub fn main() -> Unit {
            State<Int> answer = Coin()
            Measure answer
        }
        """
    )

    assert "INIT_RETURN_ERROR" in codes


if __name__ == "__main__":
    tests = [
        test_terminal_return_is_accepted_for_ordinary_function,
        test_implicit_final_expression_is_rejected,
        test_return_is_not_an_entry_point_escape,
        test_function_local_operator_cannot_leak_to_sibling_function,
        test_init_cannot_return_a_value,
    ]
    for test in tests:
        test()
    print("OK — explicit return and lexical scope Red tests")
