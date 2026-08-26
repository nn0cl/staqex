# WP-0093 S02 Phase 1 — work-plan investigation

## Current State

- Current phase: investigation only (docs/design intake). No test, no
  implementation, no status promotion, no ADR acceptance, no batch approved
  for execution.
- User request: after tracing S02 history and confirming the language-surface
  prerequisite (work unit A / `superpose` grammar) was complete, the
  Adjudicator asked to investigate how to start S02 Phase 1 implementation
  before approving any batch.
- Canonical work plan: [WP-0093](../../work-plans/WP-0093-s02-language-expressiveness-and-selection.md).
- Draft Issue: [LISS-0321](../../issues/LISS-0321-s02-host-domain-and-finite-boundary.md).
- Draft batch record: [execution-batch-wp-0093-liss-0321.json](../reviews/execution-batch-wp-0093-liss-0321.json).

## Included context

- ADR 0190 (Accepted), the S02 acceptance specification (Accepted, same
  commit as ADR 0190), the S02 design draft (just synced in PR #347),
  WP-0093.
- `tests/test_s02_selection_surface_red.py` (existing, green) — read in full
  to determine what it actually proves.
- `compiler/staqex/unitarity_check.py` (`_QUANTUM_OPS` whitelist),
  `compiler/staqex/typecheck.py` (`finiteize` op), grepped for `Selection`
  type and `feasible` stdlib registration (none found).
- `examples/showcase/S01_quantum_disaster_response/` directory layout as
  Host/domain precedent.

## Omitted context

- Real S02 domain data (chemistry, real compound sets) — synthetic fixture
  only, per spec.
- Provider SDKs, live QPU.
- `controlled`'s formal ordinary-surface grammar (separate, unstarted future
  Issue per LISS-0320's boundary note).

## Investigation finding

The S02 acceptance specification
(`docs/specs/staqex-v1-s02-drug-discovery-benchmark.md`) is **already
Accepted** — it was authored in the same commit as ADR 0190 (`321de3a`, PR
#337), and ADR 0190's own text says "This ADR established the S02
specification and conformance boundary." So WP-0093 work unit B's stated
deliverable ("S02 target specification with schema and fail-closed
scenarios") is already satisfied at the design level; the real gap is
implementation.

Re-reading `tests/test_s02_selection_surface_red.py` closely (it was
mentioned as evidence of S02 progress earlier in this session) shows its
4th test, `test_projector_is_explicitly_lowered_from_selection_constraints`,
does **not** prove S02 domain/Projector semantics exist:

- `prepare_selection` is only a name in `unitarity_check.py`'s
  `_QUANTUM_OPS` whitelist (marks a call as producing a quantum-lineage
  value for the unitarity checker; no actual implementation).
- `feasible` is not a registered stdlib function anywhere.
- No `Candidate`/`Constraint`/`Score`/`SelectionProblem`/`Selection<T>` type
  exists in `compiler/staqex/` or anywhere in the repo.
- The test passes because the **general** `project X onto <call-expr>`
  syntax (an existing, S02-independent language feature) already produces a
  `ProjectorRegion` regardless of what the callee means — it happens to
  tolerate S02-shaped names, which is not the same as implementing S02.

This reframes the actual remaining scope: essentially all of WP-0093 work
units B (domain/finite boundary), C (constraint/objective/Projector
semantics — which still needs its own ADR per WP-0093's own deliverable
list), D (observation/result contract), and E (conformance) are
unimplemented, not just "some grammar pieces."

## Granularity rationale

Considered splitting options:

1. **One Issue for all of S02 Phase 1** (all 9 Gherkin scenarios at once).
   Rejected: work unit C explicitly requires its own ADR before
   implementation (WP-0093: "Deliverable: ADR proposal covering
   `Projector<Selection>` semantics..."); bundling Host-side domain work
   with an unresolved architecture decision would either stall the whole
   Issue on the ADR or tempt skipping the ADR gate. Also far too large for
   one reviewable unit (`XL`, spanning Host records, Kernel semantics, and
   an architecture decision).
2. **Split strictly by work unit (B, C, D, E), file all four now.**
   Rejected for filing all four now: C, D, and E all depend on decisions or
   artifacts (the Projector ADR; B's fixture) that do not exist yet. Filing
   Issues whose scope can't be bounded without those artifacts would produce
   Issues that immediately need rework once the ADR lands.
3. **File only the Issue that has no blocking dependency now (work unit B),
   and treat work unit C as its own future Architecture Path track rather
   than a Feature-Path Issue.** **Selected.** Work unit B is Host-side only
   (Python DTOs, finite-manifest witness, Host input hygiene) — it touches
   no Kernel code, needs no ADR, and its acceptance scenarios ("candidate
   data stays classical", "finite encoding is explicit") are already
   accepted and self-contained. It is a clean, independently reviewable
   `L`-size unit. Work unit C's Projector ADR is called out explicitly as
   the next investigation/Architecture Path step rather than being drafted
   as a Feature-Path Issue prematurely.

Reviewable unit for LISS-0321: one Host-side domain module (records +
finite-witness validation) plus its own test suite, provable independently
of any Kernel or Projector decision.

## Execution order

1. **LISS-0321** (this batch) — no dependency, Host-side only. First because
   it is the only work-unit-B/C/D/E slice that can be fully specified and
   bounded today without a new ADR.
2. **Work unit C ADR** (Projector<Selection> semantics) — not filed as an
   Issue in this investigation; recommended as the next Architecture Path
   step after LISS-0321, or in parallel if the Adjudicator prefers, since it
   does not depend on LISS-0321's code (only on the already-accepted spec).
3. **Work unit D** (observation/result contract) — depends on both LISS-0321
   (fixture) and the work-unit-C ADR (what a selection State actually looks
   like after projection).
4. **Work unit E** (conformance: reproducibility, capability rejection) —
   depends on B, C, and D all existing; last.

## Draft batch record

[`execution-batch-wp-0093-liss-0321.json`](../reviews/execution-batch-wp-0093-liss-0321.json),
`status: "proposed"` — not `approved_for_execution`. Names only LISS-0321.
`compiler/staqex/**` and the accepted spec/ADR are explicitly listed as
disallowed paths so this batch cannot quietly grow into work unit C.

## Recommendation

Approve the LISS-0321 batch (Host domain + finite boundary) now; treat work
unit C's `Projector<Selection>` ADR as a separate, subsequent
investigation/Architecture Path request rather than bundling it here.

## Open questions for the Adjudicator

1. Does the Host-side domain module belong under
   `examples/showcase/S02_drug_discovery/` (mirroring S01's `domain/`/`host/`
   layout), or somewhere else (e.g. a shared `compiler/staqex/stdlib`-level
   Host DTO if S02 is meant to be reusable beyond one showcase)?
2. Should classical baselines (greedy / exact small-instance) be pulled into
   LISS-0321, or stay deferred to work unit E as drafted?
3. Timing preference for the work-unit-C Projector ADR: right after
   LISS-0321, or in parallel?

## Adjudicator decisions

- Granted: Investigation approval.
- Granted: Plan approval for LISS-0321.
- Decided: Host domain module under `examples/showcase/S02_drug_discovery/domain/`
  and `.../host/` (S01 layout) — refined during Green to `host/` only, once
  it was confirmed S01's `domain/` means `.sqx` Kernel source, which this
  Host-only Issue does not have.
- Decided: classical baselines (greedy/exact) stay out of LISS-0321, deferred
  to work unit E.
- Decided: work unit C's `Projector<Selection>` ADR is filed as its own,
  separate Issue right after LISS-0321 closes — not in parallel.
- Pending: Completion approval (Phase 3 is done).

## Execution record — Red, Green, Refactor

- **Phase 1 Red** (commit `f722c13`): added
  `tests/test_liss_0321_s02_host_domain_red.py` covering the two target
  spec scenarios plus six Host-input-hygiene sub-cases. Red is a compile
  failure (`ModuleNotFoundError`), confirmed as the expected/documented
  reason. Confirmed baseline unaffected via `pytest tests/ -q
  --ignore=tests/test_liss_0321_s02_host_domain_red.py` → 1209 passed
  (pytest aborts the whole run on a collection error by default, so this
  targeted check was needed instead of the usual full-suite run for this
  one verification step).
- **Phase 2 Green** (commit `8ff74da`): implemented
  `examples/showcase/S02_drug_discovery/host/domain.py` (frozen dataclasses
  matching the accepted spec's Value Model exactly) and
  `.../finite_boundary.py` (`FiniteManifestWitness` + `validate_manifest()`
  with one distinct `ManifestValidationError` code per rejected condition).
  Discovered mid-implementation that the Red test's dotted-package import
  (`examples.showcase.S02_drug_discovery.host.domain`) would not match this
  repo's convention — grepped for `__init__.py` under `examples/` (none
  exist) and found the established pattern in
  `tests/test_s01_tonight_ticket_export.py` (insert the specific `host/`
  directory into `sys.path`, import bare module names). Corrected the Red
  test to match; no assertion was weakened. Also discovered the planned
  `domain/` subdirectory (from the Plan-approval decision) doesn't fit this
  Host-only Issue, since S01's `domain/` holds `.sqx` — placed both new
  modules under `host/` only instead; this is an implementation-detail
  refinement within the already-approved Host-only boundary, not a new
  scope decision.
- **Phase 3 Refactor**: reviewed both new modules for readability; already
  minimal and consistent with S01's `host/` style (`ManifestValidationError`
  mirrors `ticket_dto.py`'s `IncompleteMeasurementError` pattern). No
  changes needed.
- **Doc sync** (this commit): LISS-0321 exit criteria checked off, status →
  `final-review-ready`; WP-0093 header and work unit B row updated to match;
  this trace updated. `open-work-register.md` and the batch record's
  `post_review_*` fields deliberately **not** updated yet — both wait for
  Completion approval + merge, matching the LISS-0320 precedent.

## Next safe action

Report Phase 3 completion to the Adjudicator with this trace, LISS-0321's
reviewer empathy summary, and full verification results; request Completion
approval. Do not push the branch or open a PR without separate explicit
authorization.
