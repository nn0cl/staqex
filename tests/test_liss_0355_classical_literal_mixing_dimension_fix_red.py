"""AT-TDD: LISS-0355 -- fix Classical-operand-vs-bare-literal mixing
discarding payload and dimension in typecheck.py.

Design decision: docs/issues/LISS-0355-classical-literal-mixing-dimension-fix.md
"""

from __future__ import annotations

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


def _run(src: str) -> None:
    compiled = compile_source(src)
    hard = _hard(compiled.diagnostics)
    assert compiled.ok and not hard, hard
    result = run_source(src, settings={"target": "local", "seed": 0})
    hard_run = _hard(result.diagnostics)
    assert result.status == "succeeded" and not hard_run, (result.status, hard_run)


def test_relational_against_literal_produces_bool() -> None:
    _run(
        """
        pub fn main() -> Unit {
            Float x = 3.0
            Bool ok = x == 3.0
            State s = Dirac(ok)
            Measure s
        }
        """
    )


def test_int_times_literal_preserves_int_payload() -> None:
    _run(
        """
        fn double_it(x: Int) -> Int {
            return x * 2
        }
        pub fn main() -> Unit {
            Int x = 5
            Int y = double_it(x)
            State s = |0>
            Measure s
        }
        """
    )


def test_energy_times_literal_preserves_energy_dimension() -> None:
    _run(
        """
        fn scale(e: Energy) -> Energy {
            return e * 2.0
        }
        pub fn main() -> Unit {
            Energy e = 1.0.eV to J
            Energy e2 = scale(e)
            State s = |0>
            Measure s
        }
        """
    )


def test_literal_on_the_left_side_is_handled_symmetrically() -> None:
    _run(
        """
        fn lit_lt(x: Float) -> Bool {
            return 3.0 < x
        }
        pub fn main() -> Unit {
            Float x = 5.0
            Bool ok = lit_lt(x)
            State s = |0>
            Measure s
        }
        """
    )
