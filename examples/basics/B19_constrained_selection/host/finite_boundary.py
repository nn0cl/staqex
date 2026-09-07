"""S02 finite-manifest witness and Host input hygiene (LISS-0321).

Proves a candidate manifest is finite, bounded, and ID-unique before it may
reach the Kernel boundary — see
docs/specs/staqex-v1-s02-drug-discovery-benchmark.md "Fixture limits" and
"Required boundary contracts" §"Host → Kernel". Selection-specific quantum
constraints stay in the Kernel boundary (work unit C); this module only
covers Host input hygiene (ADR 0190 item 5).

This does not reuse or modify the Kernel's `finiteize` op
(`compiler/staqex/typecheck.py`): that is a general numeric finiteization
primitive, not a candidate-manifest witness.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from domain import Candidate

MIN_CANDIDATES = 8
MAX_CANDIDATES = 16
MIN_SELECTION = 2
MAX_SELECTION = 4


class ManifestValidationError(ValueError):
    """Raised when a candidate manifest fails Host input hygiene. Fail-closed:
    no manifest that raises this may reach the Kernel boundary."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class FiniteManifestWitness:
    """Evidence that a candidate manifest is finite, bounded, and ID-unique."""

    candidate_count: int
    selection_size: tuple[int, int]
    candidate_ids: tuple[str, ...]


def validate_manifest(
    candidates: list[Candidate], selection_size: tuple[int, int]
) -> FiniteManifestWitness:
    """Validate a candidate manifest and return its finite-encoding witness.

    Raises ManifestValidationError with a distinct code for each rejected
    condition; never silently drops or repairs a malformed record.
    """

    if not candidates:
        raise ManifestValidationError(
            "S02_MANIFEST_EMPTY", "candidate manifest is empty"
        )

    for candidate in candidates:
        if not candidate.candidate_id or not candidate.candidate_id.strip():
            raise ManifestValidationError(
                "S02_MANIFEST_MISSING_ID", "candidate missing a stable id"
            )

    ids = [candidate.candidate_id for candidate in candidates]
    if len(ids) != len(set(ids)):
        duplicates = sorted({i for i in ids if ids.count(i) > 1})
        raise ManifestValidationError(
            "S02_MANIFEST_DUPLICATE_ID",
            f"duplicate candidate ids: {duplicates}",
        )

    for candidate in candidates:
        for score in candidate.score_components:
            if not math.isfinite(score.value):
                raise ManifestValidationError(
                    "S02_MANIFEST_NON_FINITE_SCORE",
                    f"non-finite score on candidate {candidate.candidate_id}: "
                    f"{score.name}",
                )

    if not (MIN_CANDIDATES <= len(candidates) <= MAX_CANDIDATES):
        raise ManifestValidationError(
            "S02_MANIFEST_OVERSIZED",
            f"candidate count {len(candidates)} outside fixture bounds "
            f"[{MIN_CANDIDATES}, {MAX_CANDIDATES}]",
        )

    lo, hi = selection_size
    if not (MIN_SELECTION <= lo <= hi <= MAX_SELECTION):
        raise ManifestValidationError(
            "S02_SELECTION_SIZE_UNPROVEN",
            f"selection size {selection_size} outside fixture bounds "
            f"[{MIN_SELECTION}, {MAX_SELECTION}]",
        )

    return FiniteManifestWitness(
        candidate_count=len(candidates),
        selection_size=selection_size,
        candidate_ids=tuple(ids),
    )
