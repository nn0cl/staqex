"""AT-TDD Phase 1 Red: LISS-0472 continuous/open-system readiness.

Existing tests cover CPU discretization and Lindblad execution.  This packet
adds only the missing QPU-readiness boundary: canonical meaning identity,
explicit finiteization, and honest evidence classification.  The classifier
is intentionally absent until Phase 2 Green.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _classify(source: str, *, source_id: str):
    from compiler.staqex.continuous_open_system_readiness import classify_for_qpu

    return classify_for_qpu(source, source_id=source_id)


def test_b12_preserves_continuous_open_system_meaning_and_provenance() -> None:
    source_id = "examples/basics/B12_open_systems/main_open_systems.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")

    decision = _classify(source, source_id=source_id)

    assert decision.family == "continuous/open-system"
    assert decision.semantic_role == "density/channel/evolution"
    assert decision.source_id == source_id
    assert decision.meaning_authority == "scientific_semantic_ir"


def test_qpu_readiness_requires_explicit_finite_discretization() -> None:
    source_id = "examples/basics/B12_open_systems/main_open_systems.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")

    decision = _classify(source, source_id=source_id)

    assert decision.status == "deferred"
    assert decision.reason == "discretization_required"
    assert decision.discretization_inferred is False
    assert decision.numerical_method is None
    assert decision.error_tolerance is None


def test_deferred_continuous_qpu_request_emits_no_artifact_or_provider_mapping() -> None:
    source_id = "examples/basics/B12_open_systems/main_open_systems.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")

    decision = _classify(source, source_id=source_id)

    assert decision.artifact is None
    assert decision.qasm is None
    assert decision.allocation is None
    assert decision.provider_mapping is None


def test_simulator_evidence_does_not_claim_physical_qpu_execution() -> None:
    source_id = "examples/basics/B12_open_systems/main_open_systems.sqx"
    source = (REPO / source_id).read_text(encoding="utf-8")

    decision = _classify(source, source_id=source_id)

    assert decision.evidence_kind == "cpu_or_simulator"
    assert decision.physical_execution_claimed is False


def test_unknown_continuous_realization_is_explicitly_deferred() -> None:
    with pytest.raises(ValueError, match="continuous realization deferred"):
        _classify(
            "continuous unknown realization",
            source_id="synthetic.continuous_unknown.sqx",
        )
