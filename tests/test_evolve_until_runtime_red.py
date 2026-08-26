"""AT-TDD: LISS-0012 bounded Evolve-until runtime (Joint evaluator)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host import run_source  # noqa: E402


def _run(source: str, *, seed: int = 7) -> tuple[str, tuple[dict, ...]]:
    result = run_source(
        source,
        settings={"target": "local", "seed": seed},
        stdout=io.StringIO(),
    )
    codes = tuple(d.get("code", "") for d in result.diagnostics)
    return result.status, codes


def test_explicit_evolve_until_stops_when_predicate_holds() -> None:
    status, codes = _run(
        """
        package t
        pub fn main() -> Unit {
            Energy scale = 0.0.eV to J
            Operator H = scale * X
            Time dt = 0.1.fs
            State psi = Dirac(0)
            Operator U_dt = exp(-i * H * dt / hbar)
            State psi = Evolve() { U_dt * psi until converged(psi) max 64 }.run()
            Measure psi
        }
        """
    )

    assert status == "succeeded", codes
    assert "EVOLVE_UNTIL_MAX_STEPS_ERROR" not in codes


def test_explicit_evolve_until_reports_max_steps_error() -> None:
    status, codes = _run(
        """
        package t
        pub fn main() -> Unit {
            Energy scale = 1.0.eV to J
            Operator H = scale * X
            Time dt = 1.0.fs
            State psi = |+>
            Operator U_dt = exp(-i * H * dt / hbar)
            State psi = Evolve() { U_dt * psi until false max 2 }.run()
            Measure psi
        }
        """
    )

    assert status == "failed"
    assert "EVOLVE_UNTIL_MAX_STEPS_ERROR" in codes


def test_evolve_until_predicate_does_not_consume_rng() -> None:
    with_until, _ = _run(
        """
        package t
        pub fn main() -> Unit {
            Energy scale = 0.0.eV to J
            Operator H = scale * X
            Time dt = 0.1.fs
            State psi = Dirac(0)
            Operator U_dt = exp(-i * H * dt / hbar)
            State psi = Evolve() { U_dt * psi until converged(psi) max 64 }.run()
            Measure psi
        }
        """,
        seed=11,
    )
    without_until, _ = _run(
        """
        package t
        pub fn main() -> Unit {
            State psi = Dirac(0)
            State psi = Evolve { psi under X for 1.5707963267948966.s }.run()
            Measure psi
        }
        """,
        seed=11,
    )

    assert with_until == "succeeded"
    assert without_until == "succeeded"


if __name__ == "__main__":
    for test in (
        test_explicit_evolve_until_stops_when_predicate_holds,
        test_explicit_evolve_until_reports_max_steps_error,
        test_evolve_until_predicate_does_not_consume_rng,
    ):
        test()
    print("OK — Evolve until runtime tests")
