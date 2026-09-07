"""Phase 1 Red contract for moving the current S02 boundary sample to Basics."""

from __future__ import annotations

from pathlib import Path


_REPO = Path(__file__).resolve().parents[1]
_BASIC = _REPO / "examples/basics/B19_constrained_selection"
_SOURCE = _BASIC / "constrained_selection.sqx"
_README = _BASIC / "README.md"


def test_basic_boundary_sample_has_canonical_artifacts() -> None:
    assert _SOURCE.is_file()
    assert _README.is_file()
    assert (_BASIC / "host").is_dir()


def test_basic_source_preserves_boundary_constructs_without_drug_claims() -> None:
    source = _SOURCE.read_text(encoding="utf-8")
    lowered = source.lower()

    assert "state" in lowered
    assert "project" in lowered
    assert "evolve" in lowered
    assert "measure" in lowered
    assert "drug" not in lowered
    assert "candidate" not in lowered
    assert "activity" not in lowered
    assert "selectivity" not in lowered


def test_basic_readme_describes_language_boundary_not_drug_discovery() -> None:
    readme = _README.read_text(encoding="utf-8").lower()

    assert "language boundary" in readme
    assert "terminal" in readme
    assert "measure" in readme
    assert "drug discovery" not in readme
    assert "qpu" in readme
