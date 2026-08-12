"""AT-TDD LISS-0227: local Operator P/Q/N shadows Fock atoms."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import run_source  # noqa: E402


def _method_return_named(name: str) -> str:
    return f"""
package t
class Lat {{
  fn init() {{}}
  pub fn corridor() -> Operator {{
    Operator {name} = Pi (i In Index<0..1>) {{ 1.0545718e-19 * Z[i] }}
    return {name}
  }}
}}
pub fn main() -> Unit {{
  Lat L = Lat()
  Operator H = L.corridor()
  State a = |+>
  State b = |0>
  State (a, b) = Evolve {{ (a, b) under H for 0.1.fs using Suzuki(order = 2, steps = 2) }}.run()
  State b = |0>
  Measure a
}}
"""


def _unbound_xp() -> str:
    return """
package t
pub fn main() -> Unit {
  Operator H = 5.272859e-20 * (P * P + Q * Q)
  State psi = Dirac(0)
  State psi = Evolve { psi under H for 0.5.fs using Suzuki(order = 2, steps = 4) }.run()
  Measure psi
}
"""


def test_method_return_p_product_evolves() -> None:
    result = run_source(
        _method_return_named("P"),
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics
    msgs = " ".join(str(d.get("message", "")) for d in result.diagnostics)
    assert "Fock Hamiltonian Evolve requires a single bind name" not in msgs


def test_method_return_q_product_evolves() -> None:
    result = run_source(
        _method_return_named("Q"),
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics


def test_method_return_n_product_evolves() -> None:
    result = run_source(
        _method_return_named("N"),
        settings={"seed": 0},
        stdout=io.StringIO(),
    )
    assert result.status == "succeeded", result.diagnostics


def test_unbound_pq_fock_ho_still_works() -> None:
    result = run_source(_unbound_xp(), settings={"seed": 0}, stdout=io.StringIO())
    assert result.status == "succeeded", result.diagnostics


if __name__ == "__main__":
    test_method_return_p_product_evolves()
    test_method_return_q_product_evolves()
    test_method_return_n_product_evolves()
    test_unbound_pq_fock_ho_still_works()
    print("PASS LISS-0227")
