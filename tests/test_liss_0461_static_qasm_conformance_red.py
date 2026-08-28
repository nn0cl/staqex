"""AT-TDD Phase 1 Red: LISS-0461 static OpenQASM conformance."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

FIXTURES = REPO / "tests/fixtures/qasm_static"


def _api():
    from compiler.staqex.qasm_conformance import (  # noqa: PLC0415
        StaticQasmSubset,
        validate_static_qasm,
    )

    return StaticQasmSubset, validate_static_qasm


def _metadata():
    return {
        "source_fingerprint": "sha256:source",
        "semantic_fingerprint": "sha256:semantic",
        "artifact_fingerprint": "sha256:artifact",
        "measurement_id": "measurement.terminal.0",
    }


def test_bell_fixture_is_accepted_by_declared_static_subset() -> None:
    StaticQasmSubset, validate_static_qasm = _api()
    subset = StaticQasmSubset(
        version="staqex-static-qasm-v1",
        gates=("h", "cx", "rz"),
        supports_terminal_measurement=True,
        supports_dynamic_control=False,
    )
    result = validate_static_qasm(
        (FIXTURES / "bell.qasm").read_text(encoding="utf-8"),
        subset=subset,
        metadata=_metadata(),
    )

    assert result.status == "accepted"
    assert result.parse_ok is True
    assert result.subset_version == "staqex-static-qasm-v1"
    assert result.metadata == _metadata()
    assert result.physical_execution_claimed is False


def test_parameterized_static_gate_and_terminal_measurement_are_preserved() -> None:
    StaticQasmSubset, validate_static_qasm = _api()
    subset = StaticQasmSubset(
        version="staqex-static-qasm-v1",
        gates=("h", "cx", "rz"),
        supports_terminal_measurement=True,
        supports_dynamic_control=False,
    )
    result = validate_static_qasm(
        (FIXTURES / "parameterized.qasm").read_text(encoding="utf-8"),
        subset=subset,
        metadata=_metadata(),
    )

    assert result.status == "accepted"
    assert result.measurement_mode == "terminal"
    assert result.parameters == ("0.5",)
    assert result.metadata["artifact_fingerprint"] == "sha256:artifact"


def test_dynamic_control_is_rejected_without_qasm_fallback_or_artifact() -> None:
    StaticQasmSubset, validate_static_qasm = _api()
    subset = StaticQasmSubset(
        version="staqex-static-qasm-v1",
        gates=("h", "cx", "rz"),
        supports_terminal_measurement=True,
        supports_dynamic_control=False,
    )
    result = validate_static_qasm(
        (FIXTURES / "dynamic_rejected.qasm").read_text(encoding="utf-8"),
        subset=subset,
        metadata=_metadata(),
    )

    assert result.status == "rejected"
    assert "QASM_STATIC_DYNAMIC_UNSUPPORTED" in result.diagnostic_codes
    assert result.qasm == ""
    assert result.artifact is None
    assert result.allocation is None
    assert result.physical_execution_claimed is False


def test_empty_static_program_is_rejected_without_success_fallback() -> None:
    StaticQasmSubset, validate_static_qasm = _api()
    subset = StaticQasmSubset(
        version="staqex-static-qasm-v1",
        gates=("h", "cx", "rz"),
        supports_terminal_measurement=True,
        supports_dynamic_control=False,
    )
    result = validate_static_qasm(
        (FIXTURES / "empty_rejected.qasm").read_text(encoding="utf-8"),
        subset=subset,
        metadata=_metadata(),
    )

    assert result.status == "rejected"
    assert "QASM_STATIC_EMPTY_PROGRAM" in result.diagnostic_codes
    assert result.qasm == ""
    assert result.artifact is None


if __name__ == "__main__":
    tests = [
        test_bell_fixture_is_accepted_by_declared_static_subset,
        test_parameterized_static_gate_and_terminal_measurement_are_preserved,
        test_dynamic_control_is_rejected_without_qasm_fallback_or_artifact,
        test_empty_static_program_is_rejected_without_success_fallback,
    ]
    for test in tests:
        test()
    print("OK — LISS-0461 Red contract")
