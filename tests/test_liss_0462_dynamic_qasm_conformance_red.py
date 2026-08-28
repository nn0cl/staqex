"""AT-TDD Phase 1 Red: LISS-0462 dynamic OpenQASM conformance."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

FIXTURES = REPO / "tests/fixtures/qasm_dynamic"


def _api():
    from compiler.staqex.dynamic_qasm_conformance import (  # noqa: PLC0415
        DynamicQasmSubset,
        validate_dynamic_qasm,
    )

    return DynamicQasmSubset, validate_dynamic_qasm


def _metadata():
    return {
        "source_fingerprint": "sha256:source",
        "semantic_fingerprint": "sha256:semantic",
        "artifact_fingerprint": "sha256:artifact",
        "dynamic_request_id": "dynamic.0",
    }


def _subset(**overrides):
    DynamicQasmSubset, _ = _api()
    values = {
        "version": "staqex-dynamic-qasm-v1",
        "gates": ("h", "x", "z"),
        "supports_dynamic_measurement": True,
        "supports_classical_conditions": True,
        "supports_reset": True,
        "supports_reuse": True,
    }
    values.update(overrides)
    return DynamicQasmSubset(**values)


def test_measure_feedforward_reset_and_reuse_preserve_explicit_control_metadata() -> None:
    _, validate_dynamic_qasm = _api()
    result = validate_dynamic_qasm(
        (FIXTURES / "measure_feedforward_reset_reuse.qasm").read_text(encoding="utf-8"),
        subset=_subset(),
        metadata=_metadata(),
    )

    assert result.status == "accepted"
    assert result.parse_ok is True
    assert result.subset_version == "staqex-dynamic-qasm-v1"
    assert result.metadata == _metadata()
    assert result.measurement_mode == "dynamic"
    assert result.outcome_dependencies == (("outcome[0]", "if", "outcome[0] == 1"),)
    assert result.reset_wires == ("q[0]",)
    assert result.reused_wires == ("q[0]",)
    assert result.physical_execution_claimed is False


def test_branch_outcomes_and_wire_mapping_are_explicit() -> None:
    _, validate_dynamic_qasm = _api()
    result = validate_dynamic_qasm(
        (FIXTURES / "branch_outcomes.qasm").read_text(encoding="utf-8"),
        subset=_subset(),
        metadata=_metadata(),
    )

    assert result.status == "accepted"
    assert result.wire_mapping == {"branch": "branch", "q": "q"}
    assert result.branch_outcomes == (("branch", "0", "then"), ("branch", "else", "else"))
    assert result.unsupported_branches == ()


def test_dynamic_program_is_rejected_by_static_only_target_without_fallback() -> None:
    _, validate_dynamic_qasm = _api()
    result = validate_dynamic_qasm(
        (FIXTURES / "dynamic_on_static_target.qasm").read_text(encoding="utf-8"),
        subset=_subset(
            supports_dynamic_measurement=False,
            supports_classical_conditions=False,
            supports_reset=False,
            supports_reuse=False,
        ),
        metadata=_metadata(),
    )

    assert result.status == "rejected"
    assert "QASM_DYNAMIC_TARGET_UNSUPPORTED" in result.diagnostic_codes
    assert result.qasm == ""
    assert result.artifact is None
    assert result.allocation is None
    assert result.physical_execution_claimed is False


def test_unsupported_branch_is_rejected_without_silent_drop_or_static_fallback() -> None:
    _, validate_dynamic_qasm = _api()
    result = validate_dynamic_qasm(
        (FIXTURES / "unsupported_branch.qasm").read_text(encoding="utf-8"),
        subset=_subset(),
        metadata=_metadata(),
    )

    assert result.status == "rejected"
    assert "QASM_DYNAMIC_UNSUPPORTED_BRANCH" in result.diagnostic_codes
    assert result.unsupported_branches == (("result", "1"),)
    assert result.qasm == ""
    assert result.artifact is None


def test_reuse_requires_explicit_metadata_and_cannot_be_inferred_from_text_only() -> None:
    _, validate_dynamic_qasm = _api()
    result = validate_dynamic_qasm(
        (FIXTURES / "missing_reuse_metadata.qasm").read_text(encoding="utf-8"),
        subset=_subset(),
        metadata={**_metadata(), "reused_wires": ()},
    )

    assert result.status == "rejected"
    assert "QASM_DYNAMIC_REUSE_METADATA_REQUIRED" in result.diagnostic_codes
    assert result.qasm == ""
    assert result.artifact is None


if __name__ == "__main__":
    tests = [
        test_measure_feedforward_reset_and_reuse_preserve_explicit_control_metadata,
        test_branch_outcomes_and_wire_mapping_are_explicit,
        test_dynamic_program_is_rejected_by_static_only_target_without_fallback,
        test_unsupported_branch_is_rejected_without_silent_drop_or_static_fallback,
        test_reuse_requires_explicit_metadata_and_cannot_be_inferred_from_text_only,
    ]
    for test in tests:
        test()
    print("OK — LISS-0462 Red contract")
