"""AT-TDD Phase 1 Red: LISS-0081 Slice D — formula-family inspection."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def _load_api():
    """Slice D Green must provide the deterministic inspection API."""
    from compiler.staqex.physics_ir import (
        InspectionRecord,
        PhysicsInspection,
        PhysicsModule,
        SourceOrigin,
        inspect_physics_ir,
        verify_physics_inspection,
    )

    return (
        InspectionRecord,
        PhysicsInspection,
        PhysicsModule,
        SourceOrigin,
        inspect_physics_ir,
        verify_physics_inspection,
    )


def _family_module(PhysicsModule, SourceOrigin):
    families = (
        "ising",
        "heisenberg",
        "hubbard",
        "molecular_electronic",
        "oscillator",
        "lindblad",
    )
    nodes = tuple(
        {
            "kind": "Formula",
            "family": family,
            "node_id": f"formula:{family}",
            "structure": ("equation", "operator", "provenance"),
            "origin": SourceOrigin(source_id=f"{family}.staqex", line=1, col=1),
        }
        for family in families
    )
    return PhysicsModule(
        spaces=(),
        nodes=nodes,
        origins=tuple(node["origin"] for node in nodes),
    )


def test_inspection_preserves_all_required_formula_families() -> None:
    _, PhysicsInspection, PhysicsModule, SourceOrigin, Inspect, verify = _load_api()
    module = _family_module(PhysicsModule, SourceOrigin)

    result = Inspect(module)

    assert isinstance(result, PhysicsInspection)
    assert tuple(record.family for record in result.records) == (
        "ising",
        "heisenberg",
        "hubbard",
        "molecular_electronic",
        "oscillator",
        "lindblad",
    )
    assert all(record.source_origin is not None for record in result.records)
    assert verify(result) == []


def test_inspection_is_deterministic_and_read_only() -> None:
    _, _, PhysicsModule, SourceOrigin, Inspect, _ = _load_api()
    module = _family_module(PhysicsModule, SourceOrigin)

    first = Inspect(module)
    second = Inspect(module)

    assert first == second
    assert first.module is module
    assert not hasattr(first, "execute")
    assert not hasattr(first, "expanded_gates")


def test_inspection_record_retains_recognizable_structure_and_identity() -> None:
    InspectionRecord, _, PhysicsModule, SourceOrigin, Inspect, _ = _load_api()
    module = _family_module(PhysicsModule, SourceOrigin)

    result = Inspect(module)
    record = result.records[0]

    assert isinstance(record, InspectionRecord)
    assert record.node_id == "formula:ising"
    assert record.structure == ("equation", "operator", "provenance")
    assert record.source_origin.source_id == "ising.staqex"


def test_inspection_verifier_rejects_missing_family_or_provenance() -> None:
    _, _, PhysicsModule, SourceOrigin, Inspect, verify = _load_api()
    origin = SourceOrigin(source_id="invalid.staqex", line=1, col=1)
    module = PhysicsModule(
        spaces=(),
        nodes=(
            {"kind": "Formula", "family": None, "node_id": "formula:missing"},
            {"kind": "Formula", "family": "ising", "node_id": "formula:no-origin"},
        ),
        origins=(origin,),
    )

    diagnostics = verify(Inspect(module))
    codes = {diagnostic.get("code") for diagnostic in diagnostics}

    assert "PHYSICS_IR_FAMILY_ERROR" in codes
    assert "PHYSICS_IR_PROVENANCE_ERROR" in codes


if __name__ == "__main__":
    for test in (
        test_inspection_preserves_all_required_formula_families,
        test_inspection_is_deterministic_and_read_only,
        test_inspection_record_retains_recognizable_structure_and_identity,
        test_inspection_verifier_rejects_missing_family_or_provenance,
    ):
        test()
    print("OK — LISS-0081 Slice D Phase 1 Red")
