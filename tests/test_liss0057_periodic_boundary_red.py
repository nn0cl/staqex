"""Phase 1 Red tests for the explicit periodic binder accessor."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402
from compiler.staqex.ast_nodes import OpBin, OpPauli  # noqa: E402
from compiler.staqex.finite_binder import lower_finite_binder_operators  # noqa: E402
from compiler.staqex.host import run_source  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402


def _ring_source(domain: str = "0..3", register: int = 4) -> str:
    return f"""
package t
pub fn main() -> Unit {{
    QubitRegister<{register}> register = system()
    Operator H = Sigma (i In {domain}) {{
        -1.0545718e-19 * Z[i] * Z[wrap(i)]
    }}
    State<Qubit> a = |0>
    State<Qubit> b = |0>
    State b = |0>
    State<Qubit> c = |0>
    State c = |0>
    State<Qubit> d = |0>
    State d = |0>
    State (a, b, c, d) = Evolve {{ (a, b, c, d) under H for 0.1.fs using Suzuki(order = 2, steps = 1) }}.run()
    Measure a
}}
"""


def test_wrap_is_accepted_as_periodic_index_accessor() -> None:
    compiled = compile_source(_ring_source())

    assert compiled.ok, compiled.diagnostics
    lowering = compiled.qpu_ir["binder_lowering"]["H"]
    assert lowering["expanded_terms"] == 4
    assert lowering["provenance"]["accessors"] == ["wrap"]


def test_periodic_ring_runs_and_emits_qasm() -> None:
    source = _ring_source()
    result = run_source(source, stdout=io.StringIO())
    assert result.status == "succeeded", result.diagnostics

    compiled = compile_source(source)
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)
    assert emitted.ok, emitted.diagnostics


def test_wrap_keeps_the_closing_bond() -> None:
    compiled = compile_source(_ring_source())
    lowered, diagnostics = lower_finite_binder_operators(compiled.unit)
    assert not diagnostics

    def sum_terms(node):
        if isinstance(node, OpBin) and node.op == "+":
            return sum_terms(node.lhs) + sum_terms(node.rhs)
        return [node]

    def pauli_sites(node):
        if isinstance(node, OpPauli):
            return [node.site]
        if isinstance(node, OpBin):
            return pauli_sites(node.lhs) + pauli_sites(node.rhs)
        return []

    terms = sum_terms(lowered["H"])

    assert {tuple(pauli_sites(term)) for term in terms} == {
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
    }


def test_wrap_does_not_silently_leave_the_static_register() -> None:
    compiled = compile_source(_ring_source(domain="0..4", register=4))
    codes = {diagnostic.get("code") for diagnostic in compiled.diagnostics}

    assert "BINDER_DOMAIN_ERROR" in codes


def test_next_remains_an_open_boundary_accessor() -> None:
    source = _ring_source().replace("wrap(i)", "next(i)")
    compiled = compile_source(source)
    codes = {diagnostic.get("code") for diagnostic in compiled.diagnostics}

    assert "BINDER_INDEX_OUT_OF_BOUNDS" in codes


if __name__ == "__main__":
    tests = (
        test_wrap_is_accepted_as_periodic_index_accessor,
        test_periodic_ring_runs_and_emits_qasm,
        test_wrap_keeps_the_closing_bond,
        test_wrap_does_not_silently_leave_the_static_register,
        test_next_remains_an_open_boundary_accessor,
    )
    failures: list[str] = []
    for test in tests:
        try:
            test()
        except Exception as error:  # noqa: BLE001 - aggregate Red evidence
            failures.append(f"{test.__name__}: {error}")
    if failures:
        raise AssertionError("\n".join(failures))
    print("OK - LISS-0057 periodic boundary tests")
