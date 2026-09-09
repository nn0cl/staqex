"""Phase 1 Red tests for WP-0151 / LISS-0534 Unit A."""

from __future__ import annotations

import importlib

import pytest


def _evidence_module():
    try:
        return importlib.import_module("compiler.staqex.reproducibility_evidence")
    except ModuleNotFoundError as error:
        pytest.fail("LISS-0534 Unit A implementation is not present yet")
        raise AssertionError from error


def _manifest(module, *, source_hash: str = "sha256:source-001"):
    return module.RunManifest(
        manifest_id="manifest:s02-d03-v1",
        source_hash=source_hash,
        fixture_hash="sha256:fixture-001",
        input_snapshot_id="snapshot:s02-round-001",
        model_revision="model:s02-v1",
        baseline_revision="baseline:greedy-feasible-v1",
        seed=17,
        numeric_precision="f64",
        runtime_version="python:3.14",
        command="s02-d03-replay",
    )


def test_unit_a_accepts_same_manifest_replay_within_declared_numeric_tolerance() -> None:
    module = _evidence_module()
    manifest = _manifest(module)
    original = module.EvidenceRecord(
        manifest=manifest,
        output_ids=("candidate:001", "candidate:002"),
        numeric_value=3.0,
    )
    replay = module.EvidenceRecord(
        manifest=manifest,
        output_ids=("candidate:001", "candidate:002"),
        numeric_value=3.0 + 1e-12,
    )

    result = module.compare_replay(original, replay, absolute_tolerance=1e-9)

    assert result.status == "reproduced"


def test_unit_a_rejects_replay_when_source_or_fixture_hash_changes() -> None:
    module = _evidence_module()
    original_manifest = _manifest(module)
    changed_manifest = _manifest(module, source_hash="sha256:source-002")
    original = module.EvidenceRecord(original_manifest, ("candidate:001",), 1.0)
    replay = module.EvidenceRecord(changed_manifest, ("candidate:001",), 1.0)

    result = module.compare_replay(original, replay, absolute_tolerance=1e-9)

    assert result.status == "rejected"
    assert result.diagnostic.code == "EVIDENCE_HASH_CHANGED"


def test_unit_a_rejects_manifest_identity_changes_even_when_output_matches() -> None:
    module = _evidence_module()
    original = module.EvidenceRecord(_manifest(module), ("candidate:001",), 1.0)
    changed = module.RunManifest(
        manifest_id="manifest:s02-d03-v2",
        source_hash="sha256:source-001",
        fixture_hash="sha256:fixture-001",
        input_snapshot_id="snapshot:s02-round-001",
        model_revision="model:s02-v1",
        baseline_revision="baseline:greedy-feasible-v1",
        seed=17,
        numeric_precision="f64",
        runtime_version="python:3.14",
        command="s02-d03-replay",
    )
    replay = module.EvidenceRecord(changed, ("candidate:001",), 1.0)

    result = module.compare_replay(original, replay, absolute_tolerance=1e-9)

    assert result.status == "rejected"
    assert result.diagnostic.code == "EVIDENCE_MANIFEST_MISMATCH"


def test_unit_a_rejects_numeric_replay_outside_declared_tolerance() -> None:
    module = _evidence_module()
    manifest = _manifest(module)
    original = module.EvidenceRecord(manifest, ("candidate:001",), 1.0)
    replay = module.EvidenceRecord(manifest, ("candidate:001",), 1.1)

    result = module.compare_replay(original, replay, absolute_tolerance=1e-9)

    assert result.status == "inconclusive"
    assert result.diagnostic.code == "EVIDENCE_NUMERIC_MISMATCH"
