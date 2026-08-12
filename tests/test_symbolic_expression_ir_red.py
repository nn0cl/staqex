"""AT-TDD Phase 1 Red: LISS-0033 symbolic IR and provenance."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source  # noqa: E402


def test_symbolic_ir_retains_binder_and_source_span() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Dimension sites = 4
            Operator H = sum (i in sites) { Z[i] * Z[next(i)] }
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    ir = compiled.symbolic_ir
    assert ir["kind"] == "SymbolicProgram"
    assert ir["operators"]["H"]["kind"] == "Binder"
    assert ir["operators"]["H"]["source_span"]["line"] == 5


def test_symbolic_ir_has_no_provider_sdk_objects() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator H = commutator(X, Z)
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    assert "provider" not in repr(compiled.symbolic_ir).lower()


def test_lowering_provenance_records_approximation_metadata() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator H = X + Z
            State<Qubit> q = |0>
            state q = |0>
            state out = evolve { q under H for 0.5 }.run()
            measure out
        }
        """
    )

    assert compiled.ok, compiled.diagnostics
    provenance = compiled.symbolic_ir["provenance"]
    assert any(record["pass"] == "source" for record in provenance)


def test_symbolic_nodes_have_stable_ids_and_resolved_links() -> None:
    source = """
        package t
        pub fn main() -> Unit {
            Operator H = X + Z
            State<Int> observed = coin()
            measure observed
        }
        """
    first = compile_source(source).symbolic_ir
    second = compile_source(source).symbolic_ir

    assert first["operators"]["H"]["node_id"] == "operator:H"
    assert first["operators"]["H"]["node_id"] == second["operators"]["H"]["node_id"]
    assert first["resolved"]["source_node_ids"] == ["operator:H"]
    assert first["resolved"]["status"] == "unresolved"


def test_provenance_has_explicit_approximation_and_mapping_slots() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            Operator H = X
            State<Int> observed = coin()
            measure observed
        }
        """
    )

    metadata = compiled.symbolic_ir["provenance"][0]["metadata"]
    assert metadata == {"approximation": None, "mapping": None}
    assert compiled.symbolic_ir["resolved"]["approximations"] == []


if __name__ == "__main__":
    for test in (
        test_symbolic_ir_retains_binder_and_source_span,
        test_symbolic_ir_has_no_provider_sdk_objects,
        test_lowering_provenance_records_approximation_metadata,
        test_symbolic_nodes_have_stable_ids_and_resolved_links,
        test_provenance_has_explicit_approximation_and_mapping_slots,
    ):
        test()
    print("OK — symbolic IR tests")
