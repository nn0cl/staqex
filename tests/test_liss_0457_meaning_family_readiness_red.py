"""AT-TDD Phase 1 Red: LISS-0457 meaning-family readiness contract.

These tests intentionally describe the smallest family-specific classification
boundary required by the reviewed acceptance specification.  The production
classifier does not exist yet, so this file is expected to remain Red in this
phase.  No provider, credential, network, or numerical implementation is
allowed here.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

FIXTURES = REPO / "tests" / "fixtures"


def _classify(source_fixture: str):
    """Load the future contract without coupling Red tests to an adapter."""

    from compiler.staqex.meaning_family_readiness import classify_for_qpu

    fixture_path = REPO / source_fixture if source_fixture.startswith("examples/") else FIXTURES / source_fixture
    source = fixture_path.read_text(encoding="utf-8")
    return classify_for_qpu(source, source_id=source_fixture)


def test_product_family_rejects_non_unitary_meaning_without_artifact() -> None:
    decision = _classify("capability_rejection/non_unitary_product.sqx")

    assert decision.family == "product/tensor"
    assert decision.semantic_role == "product/tensor"
    assert decision.status == "rejected"
    assert decision.code == "E_QPU_UNSUPPORTED_CAPABILITY"
    assert decision.reason == "non_unitary_target"
    assert decision.source_id == "capability_rejection/non_unitary_product.sqx"
    assert decision.artifact is None
    assert decision.rewritten_as_unitary is False


def test_continuous_open_system_defers_without_hidden_discretization() -> None:
    decision = _classify("examples/basics/B12_open_systems/main_open_systems.sqx")

    assert decision.family == "continuous/open-system"
    assert decision.semantic_role == "density/channel/evolution"
    assert decision.status == "deferred"
    assert decision.reason == "discretization_required"
    assert decision.source_id == "examples/basics/B12_open_systems/main_open_systems.sqx"
    assert decision.artifact is None
    assert decision.numerical_method is None
    assert decision.provider_mapping is None


def test_dynamic_measurement_rejects_unsupported_target_without_qasm() -> None:
    decision = _classify("semantic_core/dynamic_measurement.sqx")

    assert decision.family == "measurement"
    assert decision.semantic_role == "dynamic_measurement_feedback"
    assert decision.status == "rejected"
    assert decision.code == "E_QPU_UNSUPPORTED_CAPABILITY"
    assert decision.reason == "dynamic_measurement_unsupported"
    assert decision.artifact is None
    assert decision.qasm is None
    assert decision.terminal_measurement_is_not_dynamic is True


def test_classifier_rejects_unknown_family_without_partial_artifact() -> None:
    with pytest.raises(ValueError, match="unsupported meaning family"):
        from compiler.staqex.meaning_family_readiness import classify_for_qpu

        classify_for_qpu("unknown-family", source_id="synthetic.unknown")
