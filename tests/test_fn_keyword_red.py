"""AT-TDD Phase 1 Red: LISS-0023 / ADR-0066."""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def test_fn_function_is_accepted() -> None:
    result = compile_source(
        """
        package t
        fn advance() -> State<Int> {
            return Dirac(1)
        }
        pub fn main() -> Unit {
            State<Int> value = advance()
            Measure value
        }
        """
    )
    assert result.ok, result.diagnostics


def test_fun_function_is_rejected() -> None:
    result = compile_source(
        """
        package t
        fun advance() -> State<Int> {
            return Dirac(1)
        }
        pub fn main() -> Unit {
            State<Int> value = advance()
            Measure value
        }
        """
    )
    assert not result.ok, result.diagnostics


def test_official_examples_have_no_fun_declarations() -> None:
    declaration = re.compile(r"^\s*(?:(?:public|pub)\s+)?fun\s+")
    offenders = []
    for path in sorted((_REPO / "examples").rglob("*.sqx")):
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if declaration.match(line):
                offenders.append(f"{path}:{line_no}")
    assert not offenders, "legacy fun declarations:\n" + "\n".join(offenders)


if __name__ == "__main__":
    test_fn_function_is_accepted()
    test_fun_function_is_rejected()
    test_official_examples_have_no_fun_declarations()
    print("OK — fn keyword Red tests")
