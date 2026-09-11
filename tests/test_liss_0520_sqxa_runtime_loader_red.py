"""Phase 1 Red contracts for LISS-0520 Q01 artifact loading."""

from __future__ import annotations

import importlib
import json

import pytest


def _artifact_module():
    try:
        return importlib.import_module("compiler.staqex.quantum_artifact")
    except ModuleNotFoundError as error:
        pytest.fail("LISS-0520 .sqxa artifact boundary is not present yet")
        raise AssertionError from error


def _artifact(module):
    return module.SqxaArtifact(
        schema_version="sqxa/1",
        artifact_id="artifact:q01-fixture-v1",
        problem_id="problem:q01-binary-2",
        variables=("x0", "x1"),
        qubo_terms=(("x0", "x0", 1.0), ("x1", "x1", 2.0), ("x0", "x1", 3.0)),
        offset=-1.5,
        encoding={"bit_order": ("x0", "x1"), "scale": 2.0},
        runtime={"kind": "local-simulator", "precision": "float64"},
        source_hash="sha256:q01-source-v1",
    )


def test_sqxa_writer_and_reader_preserve_projection_identity(tmp_path) -> None:
    module = _artifact_module()
    artifact = _artifact(module)
    path = tmp_path / "q01.sqxa"

    module.write_sqxa(artifact, path)
    restored = module.read_sqxa(path)

    assert restored == artifact
    assert restored.schema_version == "sqxa/1"
    assert restored.encoding["bit_order"] == ("x0", "x1")
    assert restored.source_hash == "sha256:q01-source-v1"


def test_sqxa_reader_rejects_tampered_content_without_partial_artifact(tmp_path) -> None:
    module = _artifact_module()
    path = tmp_path / "tampered.sqxa"
    module.write_sqxa(_artifact(module), path)
    document = json.loads(path.read_text())
    document["payload"]["offset"] = 99.0
    path.write_text(json.dumps(document, sort_keys=True))

    with pytest.raises(module.SqxaValidationError, match="content hash"):
        module.read_sqxa(path)


def test_sqxa_reader_rejects_unknown_schema_before_runtime_loading(tmp_path) -> None:
    module = _artifact_module()
    path = tmp_path / "unknown-schema.sqxa"
    module.write_sqxa(_artifact(module), path)
    document = json.loads(path.read_text())
    document["payload"]["schema_version"] = "sqxa/99"
    path.write_text(json.dumps(document, sort_keys=True))

    with pytest.raises(module.SqxaValidationError, match="schema"):
        module.read_sqxa(path)


def test_runtime_loader_exposes_provider_neutral_execution_input(tmp_path) -> None:
    module = _artifact_module()
    path = tmp_path / "q01.sqxa"
    module.write_sqxa(_artifact(module), path)

    loaded = module.load_runtime(path)

    assert loaded.status == "ready"
    assert loaded.artifact.problem_id == "problem:q01-binary-2"
    assert loaded.runtime_kind == "local-simulator"
    assert loaded.capability == "finite-binary-projection"


def test_runtime_loader_rejects_unsupported_provider_without_fallback(tmp_path) -> None:
    module = _artifact_module()
    artifact = _artifact(module)
    unsupported = module.SqxaArtifact(
        **{**artifact.__dict__, "runtime": {"kind": "live-qpu", "precision": "float64"}}
    )
    path = tmp_path / "unsupported.sqxa"
    module.write_sqxa(unsupported, path)

    with pytest.raises(module.RuntimeLoadError, match="unsupported runtime"):
        module.load_runtime(path)
