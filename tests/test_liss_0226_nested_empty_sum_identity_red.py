"""AT-TDD LISS-0226: nested empty sum must not inject undetermined identity."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import OpIdentity  # noqa: E402
from compiler.staqex.finite_binder import lower_finite_binder_operators  # noqa: E402
from compiler.staqex.host import run_source  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source as run_source_eval  # noqa: E402


def _where_sum_program() -> str:
    return """
package t
pub fn main() -> Unit {
  Operator H = Sigma (i In 0..1, j In 0..1) where i < j {
      1.0545718e-19 * (Z[i] * Z[j])
  }
  State a = |+>
  State b = |0>
  State (a, b) = Evolve { (a, b) under H for 0.1.fs using Suzuki(order = 2, steps = 2) }.run()
  State b = |0>
  Measure a
}
"""


def _walk_has_undetermined_sum_identity(expr) -> bool:
    if isinstance(expr, OpIdentity):
        return expr.kind == "sum" and expr.acting_space is None
    if hasattr(expr, "lhs"):
        return _walk_has_undetermined_sum_identity(expr.lhs) or _walk_has_undetermined_sum_identity(
            expr.rhs
        )
    return False


def test_where_sum_evolves_without_qubit_register() -> None:
    result = run_source(
        _where_sum_program(),
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics
    msgs = " ".join(str(d.get("message", "")) for d in result.diagnostics)
    assert "IDENTITY_ACTING_SPACE_UNDETERMINED" not in msgs


def test_lowered_where_sum_omits_undetermined_identity() -> None:
    compiled = compile_source(_where_sum_program())
    assert compiled.ok, compiled.diagnostics
    lowered, _ = lower_finite_binder_operators(compiled.unit)
    assert "H" in lowered
    assert not _walk_has_undetermined_sum_identity(lowered["H"]), lowered["H"]


def test_empty_outer_sum_still_rejected_without_register() -> None:
    result = run_source_eval(
        """
package t
pub fn main() -> Unit {
  Operator H = Sigma (i In 3..1) { Z[i] }
  State psi = |0>
  State out = Evolve { psi under H for 0.1 using Suzuki(order = 2, steps = 1) }.run()
  Measure out
}
""",
        seed=0,
        stdout=io.StringIO(),
    )
    codes = [d.get("code") for d in result.diagnostics]
    assert not result.compile_ok
    assert "IDENTITY_ACTING_SPACE_UNDETERMINED" in codes


if __name__ == "__main__":
    test_where_sum_evolves_without_qubit_register()
    test_lowered_where_sum_omits_undetermined_identity()
    test_empty_outer_sum_still_rejected_without_register()
    print("PASS LISS-0226")
