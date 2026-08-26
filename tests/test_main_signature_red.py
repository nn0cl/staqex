"""AT-TDD Phase 1 Red: ADR 0064 explicit `main -> Unit` entry point."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402


def test_main_requires_explicit_unit_result() -> None:
    src = """
package t
pub fn main() -> Unit {
    State<Int> value = Coin()
    Measure value
}
"""
    result = run_source(src, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None


def test_bare_main_signature_is_rejected() -> None:
    src = """
package t
pub fn main() {
    State<Int> value = Coin()
    Measure value
}
"""
    compiled = compile_source(src)
    assert not compiled.ok, compiled.diagnostics


def test_main_cannot_return_a_quantum_state() -> None:
    src = """
package t
pub fn main() -> State<Int> {
    State<Int> value = Coin()
    Measure value
}
"""
    compiled = compile_source(src)
    assert not compiled.ok, compiled.diagnostics


def test_official_examples_declare_unit_main() -> None:
    example_files = sorted((_REPO / "examples").glob("**/*.sqx"))
    bare = []
    for path in example_files:
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if "pub fn main" in line and "-> Unit" not in line:
                bare.append(f"{path}:{line_no}")
    assert not bare, "bare main signatures remain:\n" + "\n".join(bare)


if __name__ == "__main__":
    for test in (
        test_main_requires_explicit_unit_result,
        test_bare_main_signature_is_rejected,
        test_main_cannot_return_a_quantum_state,
        test_official_examples_declare_unit_main,
    ):
        test()
    print("OK — explicit main signature Red tests")
