"""S02 Host-side classical domain records (LISS-0321).

These are Host classical values — see
docs/specs/staqex-v1-s02-drug-discovery-benchmark.md "Value model" §"Classical
records". None of them are quantum values, and none of this module depends on
the Kernel. A `Candidate`'s optional canonical chemical string is evidence
only; it is never interpreted as an amplitude here or downstream.
"""

from __future__ import annotations

from dataclasses import dataclass, field

CandidateId = str


@dataclass(frozen=True)
class Score:
    """A named, normalized finite score component with provenance."""

    name: str
    value: float
    direction: str  # "maximize" | "minimize"
    weight: float
    provenance: str = ""


@dataclass(frozen=True)
class Candidate:
    """An immutable molecule/fragment record. Classical input data only."""

    candidate_id: CandidateId
    descriptor_ref: str
    score_components: tuple[Score, ...] = ()
    tags: tuple[str, ...] = ()
    provenance: str = ""
    canonical_string: str | None = None


@dataclass(frozen=True)
class TargetProfile:
    """Abstract target binding / property profile. No disease name required."""

    profile_id: str
    description: str = ""


@dataclass(frozen=True)
class Constraint:
    """A named hard selection rule and its domain."""

    name: str
    domain: str


@dataclass(frozen=True)
class SelectionProblem:
    """The finite candidate-selection problem handed to the Kernel boundary."""

    candidates: tuple[Candidate, ...]
    target_profile: TargetProfile
    hard_constraints: tuple[Constraint, ...] = ()
    soft_objective_terms: tuple[Score, ...] = field(default_factory=tuple)
    selection_size: tuple[int, int] = (2, 4)
    seed: int = 0
    encoding_profile: str = "one-hot-per-candidate"
    resource_profile: str = "synthetic"
