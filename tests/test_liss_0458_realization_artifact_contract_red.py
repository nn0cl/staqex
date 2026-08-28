"""AT-TDD Phase 1 Red: LISS-0458 finite realization/artifact boundary.

This packet contains acceptance tests only.  The realization/artifact
contract is intentionally not implemented until the reviewed Red tests are
accepted for Phase 2.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.pipeline import compile_path  # noqa: E402


EXPLICIT = REPO / "tests/fixtures/ideal_realization/explicit_realize.sqx"
IDEAL = REPO / "tests/fixtures/ideal_realization/ideal_limit.sqx"


def _contract():
    from compiler.staqex.realization_artifact import (  # noqa: PLC0415
        RealizePlan,
        build_execution_artifact,
    )

    return RealizePlan, build_execution_artifact


def test_symbolic_inspection_does_not_create_a_finite_artifact() -> None:
    _, build_execution_artifact = _contract()
    compiled = compile_path(IDEAL)
    assert compiled.scientific_semantic_ir is not None

    decision = build_execution_artifact(compiled.scientific_semantic_ir)

    assert decision.artifact is None
    assert decision.allocation is None
    assert decision.provider_payload is None
    assert decision.diagnostics[0].code == "FINITE_REALIZATION_REQUIRED"
    assert decision.provenance["source_id"] == "tests/fixtures/ideal_realization/ideal_limit.sqx"


def test_explicit_realize_preserves_policy_fingerprints_and_provenance() -> None:
    RealizePlan, build_execution_artifact = _contract()
    compiled = compile_path(EXPLICIT)
    assert compiled.scientific_semantic_ir is not None
    plan = RealizePlan(
        method="suzuki",
        order=2,
        steps=8,
        error_budget=1e-6,
        dimensions=(2,),
        basis_order=("0", "1"),
    )

    decision = build_execution_artifact(compiled.scientific_semantic_ir, plan)

    assert decision.artifact is not None
    assert decision.artifact.source_fingerprint
    assert decision.artifact.semantic_fingerprint
    assert decision.artifact.provenance["source_node_id"]
    assert decision.artifact.policy == plan
    assert decision.artifact.approximation["method"] == "suzuki"
    assert decision.artifact.approximation["order"] == 2
    assert decision.artifact.approximation["steps"] == 8
    assert decision.artifact.approximation["error_budget"] == 1e-6


def test_artifact_keeps_instruction_order_and_duplicate_entries() -> None:
    RealizePlan, build_execution_artifact = _contract()
    compiled = compile_path(EXPLICIT)
    assert compiled.scientific_semantic_ir is not None
    plan = RealizePlan(
        method="product",
        order=1,
        steps=2,
        error_budget=1e-4,
        dimensions=(2,),
        basis_order=("0", "1"),
    )

    decision = build_execution_artifact(
        compiled.scientific_semantic_ir,
        plan,
        instructions=("h q[0]", "h q[0]", "measure q[0]"),
    )

    assert decision.artifact is not None
    assert decision.artifact.instructions == (
        "h q[0]",
        "h q[0]",
        "measure q[0]",
    )


def test_invalid_finite_policy_rejects_atomically() -> None:
    RealizePlan, build_execution_artifact = _contract()
    compiled = compile_path(EXPLICIT)
    assert compiled.scientific_semantic_ir is not None
    for overrides in (
        {"dimensions": (0,)},
        {"dimensions": (2,), "error_budget": float("nan")},
        {"dimensions": (2,), "steps": 0},
    ):
        values: dict[str, object] = {
            "method": "suzuki",
            "order": 2,
            "steps": 8,
            "error_budget": 1e-6,
            "dimensions": (2,),
            "basis_order": ("0", "1"),
        }
        values.update(overrides)
        decision = build_execution_artifact(
            compiled.scientific_semantic_ir,
            RealizePlan(**values),
        )

        assert decision.artifact is None
        assert decision.allocation is None
        assert decision.provider_payload is None
        assert decision.diagnostics


def test_equivalent_artifacts_have_stable_canonical_serialization() -> None:
    RealizePlan, build_execution_artifact = _contract()
    plan = RealizePlan(
        method="suzuki",
        order=2,
        steps=8,
        error_budget=1e-6,
        dimensions=(2,),
        basis_order=("0", "1"),
    )
    first = compile_path(EXPLICIT)
    second = compile_path(EXPLICIT)
    assert first.scientific_semantic_ir is not None
    assert second.scientific_semantic_ir is not None

    first_artifact = build_execution_artifact(first.scientific_semantic_ir, plan).artifact
    second_artifact = build_execution_artifact(second.scientific_semantic_ir, plan).artifact

    assert first_artifact is not None
    assert second_artifact is not None
    assert first_artifact.canonical_bytes == second_artifact.canonical_bytes
    assert first_artifact.fingerprint == second_artifact.fingerprint


if __name__ == "__main__":
    tests = [
        test_symbolic_inspection_does_not_create_a_finite_artifact,
        test_explicit_realize_preserves_policy_fingerprints_and_provenance,
        test_artifact_keeps_instruction_order_and_duplicate_entries,
        test_invalid_finite_policy_rejects_atomically,
        test_equivalent_artifacts_have_stable_canonical_serialization,
    ]
    for test in tests:
        test()
    print("OK — LISS-0458 Red contract")
