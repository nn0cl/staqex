"""AT-TDD Phase 1 Red: LISS-0321 S02 Host domain records and finite boundary.

Target behavior is the accepted docs/specs/staqex-v1-s02-drug-discovery-benchmark.md
acceptance scenarios "candidate data stays classical" and "finite encoding is
explicit", plus the Host input hygiene sub-cases from WP-0093 work unit B
item 4 (missing / duplicate / non-finite / oversized / unproven-finite
input). Host-side Python only; no Kernel/.sqx change.

These tests intentionally describe the not-yet-implemented module. They must
fail (ImportError / AttributeError) against the current repo, which has no
`examples/showcase/S02_drug_discovery/host` package yet.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_HOST = _REPO / "examples/showcase/S02_drug_discovery/host"
if str(_HOST) not in sys.path:
    sys.path.insert(0, str(_HOST))

from domain import (  # noqa: E402
    Candidate,
    Constraint,
    Score,
    SelectionProblem,
    TargetProfile,
)
from finite_boundary import ManifestValidationError, validate_manifest  # noqa: E402


def _candidate(candidate_id: str, *, value: float = 0.5) -> Candidate:
    return Candidate(
        candidate_id=candidate_id,
        descriptor_ref=f"descriptor:{candidate_id}",
        score_components=(
            Score(
                name="activity",
                value=value,
                direction="maximize",
                weight=0.5,
                provenance="synthetic-fixture",
            ),
        ),
    )


def _valid_manifest(count: int = 8) -> list[Candidate]:
    return [_candidate(f"C{i:02d}") for i in range(count)]


def test_candidate_data_stays_classical() -> None:
    """Spec scenario: candidate data stays classical.

    Given a valid synthetic candidate manifest, when the Host constructs a
    SelectionProblem, candidate records and scores remain plain classical
    Python values -- no implicit amplitude/State encoding is introduced.
    """

    candidates = _valid_manifest(8)
    witness = validate_manifest(candidates, selection_size=(2, 4))

    problem = SelectionProblem(
        candidates=tuple(candidates),
        target_profile=TargetProfile(profile_id="synthetic-target"),
        hard_constraints=(Constraint(name="max_selected", domain="exactly_selected<=4"),),
        soft_objective_terms=(),
        selection_size=(2, 4),
        seed=0,
        encoding_profile="one-hot-per-candidate",
        resource_profile="synthetic",
    )

    assert witness.candidate_count == 8
    assert isinstance(problem.candidates, tuple)
    for candidate in problem.candidates:
        assert isinstance(candidate, Candidate)
        assert isinstance(candidate.candidate_id, str)
        for score in candidate.score_components:
            assert isinstance(score.value, float)
    # No amplitude, State, or Kernel type appears anywhere in the DTO graph.
    assert not hasattr(problem, "amplitude")
    assert not hasattr(problem, "state")


def test_finite_encoding_is_explicit_missing_evidence_fails_closed() -> None:
    """Spec scenario: finite encoding is explicit.

    Given a candidate set without finite encoding evidence (empty manifest),
    preparation fails with a finite-evidence diagnostic rather than silently
    proceeding.
    """

    with pytest.raises(ManifestValidationError) as excinfo:
        validate_manifest([], selection_size=(2, 4))

    assert excinfo.value.code == "S02_MANIFEST_EMPTY"


def test_missing_candidate_id_fails_closed() -> None:
    candidates = _valid_manifest(8)
    candidates[3] = Candidate(
        candidate_id="",
        descriptor_ref="descriptor:missing",
        score_components=(),
    )

    with pytest.raises(ManifestValidationError) as excinfo:
        validate_manifest(candidates, selection_size=(2, 4))

    assert excinfo.value.code == "S02_MANIFEST_MISSING_ID"


def test_duplicate_candidate_id_fails_closed() -> None:
    candidates = _valid_manifest(8)
    candidates[1] = _candidate("C00")  # duplicates candidates[0]

    with pytest.raises(ManifestValidationError) as excinfo:
        validate_manifest(candidates, selection_size=(2, 4))

    assert excinfo.value.code == "S02_MANIFEST_DUPLICATE_ID"


def test_non_finite_score_fails_closed() -> None:
    candidates = _valid_manifest(8)
    candidates[2] = _candidate("C02", value=math.nan)

    with pytest.raises(ManifestValidationError) as excinfo:
        validate_manifest(candidates, selection_size=(2, 4))

    assert excinfo.value.code == "S02_MANIFEST_NON_FINITE_SCORE"


def test_oversized_manifest_fails_closed() -> None:
    candidates = _valid_manifest(17)  # fixture cap is 16

    with pytest.raises(ManifestValidationError) as excinfo:
        validate_manifest(candidates, selection_size=(2, 4))

    assert excinfo.value.code == "S02_MANIFEST_OVERSIZED"


def test_undersized_manifest_fails_closed() -> None:
    candidates = _valid_manifest(7)  # fixture floor is 8

    with pytest.raises(ManifestValidationError) as excinfo:
        validate_manifest(candidates, selection_size=(2, 4))

    assert excinfo.value.code == "S02_MANIFEST_OVERSIZED"


def test_unproven_selection_size_fails_closed() -> None:
    candidates = _valid_manifest(8)

    with pytest.raises(ManifestValidationError) as excinfo:
        validate_manifest(candidates, selection_size=(1, 5))  # outside 2..4

    assert excinfo.value.code == "S02_SELECTION_SIZE_UNPROVEN"


def test_valid_manifest_witness_is_reproducible() -> None:
    candidates = _valid_manifest(8)

    witness_a = validate_manifest(candidates, selection_size=(2, 4))
    witness_b = validate_manifest(candidates, selection_size=(2, 4))

    assert witness_a == witness_b
    assert witness_a.candidate_ids == tuple(c.candidate_id for c in candidates)


if __name__ == "__main__":
    import traceback

    tests = [
        test_candidate_data_stays_classical,
        test_finite_encoding_is_explicit_missing_evidence_fails_closed,
        test_missing_candidate_id_fails_closed,
        test_duplicate_candidate_id_fails_closed,
        test_non_finite_score_fails_closed,
        test_oversized_manifest_fails_closed,
        test_undersized_manifest_fails_closed,
        test_unproven_selection_size_fails_closed,
        test_valid_manifest_witness_is_reproducible,
    ]
    failures = 0
    for test in tests:
        try:
            test()
        except Exception:  # noqa: BLE001
            failures += 1
            traceback.print_exc()
    if failures:
        print(f"RED — {failures}/{len(tests)} failed")
    else:
        print("GREEN — S02 Host domain and finite boundary")
