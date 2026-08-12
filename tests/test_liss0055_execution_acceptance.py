"""Acceptance coverage for the executable LISS-0055 binder slice."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.backend.qasm.emitter import QASM3Emitter  # noqa: E402
from compiler.staqex.finite_binder import lower_finite_binder_operators  # noqa: E402
from compiler.staqex.host import run_source  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.ast_nodes import OpBin, OpPauli  # noqa: E402


def _source(operator: str, register: int = 3) -> str:
    names_list = list("abc"[:register])
    wires = "\n".join(
        f"    State {name} = |{'+' if name == 'a' else '0'}>" for name in names_list
    )
    names = ", ".join(names_list)
    uncompute = "\n".join(
        f"    State {name} = |0>" for name in names_list if name != "a"
    )
    return f"""
package t
pub fn main() -> Unit {{
    QubitRegister<{register}> register = system()
    Operator H = {operator}
{wires}
    State ({names}) = Evolve {{ ({names}) under H for 0.1.fs using Suzuki(order = 2, steps = 2) }}.run()
{uncompute}
    Measure a
}}
"""


def test_where_filters_index_tuples_before_execution() -> None:
    compiled = compile_source(
        _source(
            "Sigma (i In Index<0..2>, j In Index<0..2>) "
            "where i < j { 1.0545718e-19 * (Z[i] * Z[j]) }"
        )
    )
    assert compiled.ok, compiled.diagnostics
    provenance = compiled.qpu_ir["binder_lowering"]["H"]["provenance"]
    assert provenance["binder_variables"] == ["i", "j"]
    assert provenance["desugared"] is True
    assert provenance["retained_terms"] == 3
    assert run_source(_source("Sigma (i In Index<0..2>, j In Index<0..2>) where i < j { 1.0545718e-19 * (Z[i] * Z[j]) }"), stdout=io.StringIO()).status == "succeeded"


def test_nested_sum_runs_and_emits_qasm() -> None:
    source = _source(
        "Sigma (i In Index<0..1>) { Sigma (j In Index<0..1>) "
        "{ 1.0545718e-19 * (Z[i] * Z[j]) } }"
    )
    result = run_source(source, stdout=io.StringIO())
    assert result.status == "succeeded", result.diagnostics
    compiled = compile_source(source)
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)
    assert emitted.ok


def test_product_preserves_ascending_factor_order() -> None:
    source = _source("Pi (i In Index<0..2>) { Z[i] }")
    compiled = compile_source(source)
    lowered, diagnostics = lower_finite_binder_operators(compiled.unit)
    assert not diagnostics

    sites: list[int] = []

    def visit(node):
        if isinstance(node, OpPauli):
            sites.append(node.site)
        elif isinstance(node, OpBin):
            visit(node.lhs)
            visit(node.rhs)

    visit(lowered["H"])
    assert sites == [0, 1, 2]


def test_second_quantized_binder_runs_and_emits_qasm() -> None:
    source = _source(
        "Sigma (i In Index<0..1>) { 1.0545718e-19 * (create[i] * annihilate[i]) }"
    )
    result = run_source(source, stdout=io.StringIO())
    assert result.status == "succeeded", result.diagnostics
    compiled = compile_source(source)
    emitted = QASM3Emitter(route=False).emit_unit(compiled.unit)
    assert emitted.ok


if __name__ == "__main__":
    tests = [
        test_where_filters_index_tuples_before_execution,
        test_nested_sum_runs_and_emits_qasm,
        test_product_preserves_ascending_factor_order,
        test_second_quantized_binder_runs_and_emits_qasm,
    ]
    for test in tests:
        test()
    print("OK - LISS-0055 execution acceptance tests")
