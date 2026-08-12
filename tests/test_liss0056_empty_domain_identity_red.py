"""Phase 1 Red tests for LISS-0056 empty-domain identities.

These tests define only observable behavior: an empty range is a warning, an
acting-space-free identity cannot reach execution, and an explicit register
allows the identity to materialize.  The symbolic IR representation remains
an implementation detail for Phase 2.
"""

from __future__ import annotations

import io
import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import OpIdentity  # noqa: E402
from compiler.staqex.codegen_qasm import StaqexCompiler  # noqa: E402
from compiler.staqex.finite_binder import lower_finite_binder_operators  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402
from compiler.staqex.runtime.hamiltonian import compile_hamiltonian  # noqa: E402


def _program(operator: str, *, register: int | None = None) -> str:
    register_decl = (
        f"    QubitRegister<{register}> register = system()\n"
        if register is not None
        else ""
    )
    return f"""
package t
pub fn main() -> Unit {{
{register_decl}    Operator H = {operator}
    State psi = |0>
    State psi = |0>
    State out = Evolve {{ psi under H for 0.1 using Suzuki(order = 2, steps = 1) }}.run()
    Measure out
}}
"""


def test_empty_sum_is_a_warning_and_not_a_hard_compile_error() -> None:
    compiled = compile_source(_program("sum (i in Index<3..1>) { Z[i] }"))

    codes = [diagnostic.get("code") for diagnostic in compiled.diagnostics]
    assert "EMPTY_BINDER_DOMAIN_WARNING" in codes
    assert compiled.ok


def test_empty_product_is_a_warning_and_not_a_hard_compile_error() -> None:
    compiled = compile_source(_program("product (i in Index<3..1>) { Z[i] }"))

    codes = [diagnostic.get("code") for diagnostic in compiled.diagnostics]
    assert "EMPTY_BINDER_DOMAIN_WARNING" in codes
    assert compiled.ok


def test_identity_without_acting_space_is_rejected_before_simulation() -> None:
    result = run_source(
        _program("sum (i in Index<3..1>) { Z[i] }"),
        seed=0,
        stdout=io.StringIO(),
    )

    codes = [diagnostic.get("code") for diagnostic in result.diagnostics]
    assert not result.compile_ok
    assert "IDENTITY_ACTING_SPACE_UNDETERMINED" in codes


def test_identity_with_explicit_register_runs_at_that_register_shape() -> None:
    compiled = compile_source(
        _program("sum (i in Index<3..1>) { Z[i] }", register=4)
    )
    assert compiled.ok, compiled.diagnostics
    lowered, _ = lower_finite_binder_operators(compiled.unit)
    identity = lowered["H"]
    assert isinstance(identity, OpIdentity)
    assert identity.acting_space == 4
    matrix = compile_hamiltonian(identity, env={}, n_qubits=4)
    assert len(matrix) == 16
    assert len(matrix[0]) == 16


def test_identity_without_acting_space_cannot_emit_qasm() -> None:
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "empty_identity.sqx"
        source.write_text(
            _program("sum (i in Index<3..1>) { Z[i] }"), encoding="utf-8"
        )
        try:
            StaqexCompiler().compile_to_qasm3(str(source))
        except ValueError as error:
            assert "IDENTITY_ACTING_SPACE_UNDETERMINED" in str(error)
        else:
            raise AssertionError("QASM emission must reject an unshaped identity")


if __name__ == "__main__":
    tests = (
        test_empty_sum_is_a_warning_and_not_a_hard_compile_error,
        test_empty_product_is_a_warning_and_not_a_hard_compile_error,
        test_identity_without_acting_space_is_rejected_before_simulation,
        test_identity_with_explicit_register_runs_at_that_register_shape,
        test_identity_without_acting_space_cannot_emit_qasm,
    )
    failures: list[str] = []
    for test in tests:
        try:
            test()
        except Exception as error:  # noqa: BLE001 - aggregate Red evidence
            failures.append(f"{test.__name__}: {error}")
    if failures:
        raise AssertionError("\n".join(failures))
    print("OK - LISS-0056 empty-domain identity tests")
