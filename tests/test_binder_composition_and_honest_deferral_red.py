"""Acceptance checks for LISS-0053 binder composition.

These tests capture the accepted ADR 0096 boundary: ordinary operator
composition, named scalar coefficients, and the implemented ``product``
operator must reach the existing execution paths without silent loss.
"""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402
from compiler.staqex.host import run_source  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _run(source: str, *, seed: int = 7):
    return run_source(
        source,
        settings={"target": "local", "seed": seed},
        stdout=io.StringIO(),
    )


def _emit(source: str):
    compiled = compile_source(source)
    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None
    return QASM3Emitter(route=False).emit_unit(compiled.unit)


_COMPOSED_SUMS = """
package t
pub fn main() -> Unit {
    QubitRegister<4> register = system()
    Operator H = sum (i in Index<0..2>) {
        -1.0545718e-19 * Z[i] * Z[next(i)]
    } + sum (i in Index<0..3>) {
        -1.0545718e-19 * X[i]
    }
    State a = |+>
    State b = |0>
    State c = |0>
    State d = |0>
    State (a, b, c, d) = Evolve { (a, b, c, d) under H for 0.1.fs using Suzuki(order = 2, steps = 4) }.run()
    State b = |0>
    State c = |0>
    State d = |0>
    Measure a
}
"""


_HAND_WRITTEN_TFIM = """
package t
pub fn main() -> Unit {
    QubitRegister<4> register = system()
    Operator H = -1.0545718e-19 * (Z[0] * Z[1] + Z[1] * Z[2] + Z[2] * Z[3])
        + -1.0545718e-19 * (X[0] + X[1] + X[2] + X[3])
    State a = |+>
    State b = |0>
    State c = |0>
    State d = |0>
    State (a, b, c, d) = Evolve { (a, b, c, d) under H for 0.1.fs using Suzuki(order = 2, steps = 4) }.run()
    State b = |0>
    State c = |0>
    State d = |0>
    Measure a
}
"""


_NAMED_COEFFICIENT = """
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
    State c = |0>
    State d = |0>
    Measure a
}
"""


_PRODUCT = """
package t
pub fn main() -> Unit {
    QubitRegister<4> register = system()
    Operator parity = product (i in Index<0..3>) { Z[i] }
    State a = |+>
    Measure a
}
"""


def test_composed_sums_run_and_match_hand_written_tfim() -> None:
    composed = _run(_COMPOSED_SUMS)
    hand_written = _run(_HAND_WRITTEN_TFIM)

    assert composed.status == "succeeded", composed.diagnostics
    assert (
        composed.measurements[0].marginal
        == hand_written.measurements[0].marginal
    )


def test_composed_sums_emit_qasm() -> None:
    assert _emit(_COMPOSED_SUMS).ok


def test_named_scalar_coefficient_in_binder_matches_literal_coefficient() -> None:
    named = _run(_NAMED_COEFFICIENT)
    literal = _run(_COMPOSED_SUMS.replace(" + sum (i in Index<0..3>) {\n        -1.0545718e-19 * X[i]\n    }", ""))

    assert named.status == "succeeded", named.diagnostics
    assert named.measurements[0].marginal == literal.measurements[0].marginal


def test_product_lowers_as_an_operator_expression() -> None:
    compiled = compile_source(_PRODUCT)

    assert compiled.ok, compiled.diagnostics
    assert compiled.unit is not None


if __name__ == "__main__":
    tests = [
        test_composed_sums_run_and_match_hand_written_tfim,
        test_composed_sums_emit_qasm,
        test_named_scalar_coefficient_in_binder_matches_literal_coefficient,
        test_product_lowers_as_an_operator_expression,
    ]
    passed, failed = 0, 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as exc:  # noqa: BLE001 -- Red run report only
            failed += 1
            print(f"RED (expected): {test.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{passed} passed, {failed} failed (Phase 2 Green verification)")
