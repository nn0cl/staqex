# LISS-0522 / WP-0139 Phase 3 最終レビュー

- Date: 2026-09-11
- Scope: D04 S02 classical closed-loop assay batch
- Approval received: `LISS-0522 Phase 3 最終レビュー 承認`
- Isolation: `same_context`; this is weaker than a separate-context review.
- Reviewer posture: reviewer role; implementation was not continued during review.

## Canonical artifacts re-read

- [WP-0139](../../work-plans/WP-0139-s02-assay-batch-cycle.md)
- [LISS-0522](../../issues/LISS-0522-s02-assay-batch-cycle.md)
- [Scientific Workflow acceptance specification](../../specs/staqex-scientific-workflow-acceptance.md)
- `compiler/staqex/s02_assay_batch_cycle.py`
- `tests/test_s02_assay_batch_cycle_red.py`
- `docs/architecture/open-work-register.md`
- Applicable process lessons: status-drift, coverage-authority-boundary,
  acceptance-boundary, phase-acceptance-boundary.

## Findings

### Blocker B1 — D04 acceptance is not fully implemented

The accepted D04 profile requires proposal-level snapshot/model/policy identity,
approval hash and deadline, uncertainty, provenance, and fail-closed handling
for changed approval state, duplicate replay, and missing provenance. The
current `BatchProposal` omits policy identity, approval hash, deadline,
uncertainty, and provenance. `_validate_proposal_inputs` checks only future
labels, snapshot identity, and stock state; approval expiry, model/policy
mismatch, duplicate rounds, and missing provenance are not rejected.

Disposition: apply before completion. This is not a refactor-only finding;
Phase 1 Red coverage and a bounded Phase 2 implementation are required.

### Blocker B2 — Red evidence does not cover the accepted negative boundary

The five tests in `tests/test_s02_assay_batch_cycle_red.py` cover the positive
proposal, future labels, stale snapshot, stock change, and revision increment,
but do not fix the accepted scenarios for approval expiry, policy/model
identity, duplicate round, missing uncertainty/provenance, or approval-bound
hash/deadline. The current phase record therefore overstates the acceptance
coverage.

Disposition: apply by adding only the missing Red tests in a new Phase 1 gate;
do not modify the existing tests to make the implementation pass.

### Finding F1 — deterministic local verification is partial

Python 3.14 `py_compile`, `git diff --check`, and a direct D04 smoke check pass.
`python3 -m pytest ...` cannot run because pytest is unavailable in this
environment. CI or a provisioned pytest environment remains required for the
full suite.

Disposition: already honestly recorded as an environment limitation; CI must
run after the follow-up implementation.

### Finding F2 — status/register drift remains open

WP-0151 records completion while LISS-0534 and the scientific register retain
older review/phase text. LISS-0522 itself is correctly still review-pending.
No completion status is synchronized while B1/B2 remain unresolved.

Disposition: apply after the bounded follow-up reviews, in the same status
update unit.

## Verification re-run

- `python3 -m py_compile compiler/staqex/s02_assay_batch_cycle.py tests/test_s02_assay_batch_cycle_red.py`: pass
- Direct positive D04 proposal smoke check: pass
- `git diff --check`: pass
- Focused pytest command: not run successfully; pytest is not installed

## Decision

`LISS-0522 Phase 3 最終レビュー` is **not approved**. The issue remains
`phase-3-refactor` / final-review-pending. Do not mark WP-0139 or LISS-0522
done, and do not advance to LISS-0541 until the missing D04 acceptance boundary
is implemented and reviewed.

## Next requested approval

After the design correction updates WP-0139/LISS-0522 and readiness is checked,
request:

`LISS-0522 Phase 1 Red 承認`

## Follow-up final review (2026-09-11)

The Phase 1 fixture correction and Phase 2/3 implementation were re-read and
verified. The focused test command was run with the repository import path:

- `PYTHONPATH=. .venv/bin/pytest -q tests/test_s02_assay_batch_cycle_red.py`
- Result: **8 passed, 1 failed**

The failure is in the existing positive follow-up test: `_snapshot(...,
round_id="round:002")` leaves `revision=1`, while the test asserts that the
new snapshot has revision 2. The implementation correctly requires the next
snapshot revision to advance exactly once, so this is a test-fixture defect,
not a production failure.

Disposition: blocker. Correct the follow-up fixture to explicitly use
`revision=2` in a new bounded Phase 1 Red correction, then rerun the focused
suite. Do not mark LISS-0522/WP-0139 done or advance to LISS-0541 until that
correction and the final review are complete.

The earlier environment note stating that pytest was unavailable is superseded
by this verified `.venv` result; the required invocation includes `PYTHONPATH=.`.

## Fixture-correction verification (2026-09-11)

After the approved Phase 1 Red fixture correction, the follow-up snapshot now
uses `revision=2`. The focused command passes completely:

- `PYTHONPATH=. .venv/bin/pytest -q tests/test_s02_assay_batch_cycle_red.py`: **9 passed**
- `python3 -m py_compile compiler/staqex/s02_assay_batch_cycle.py tests/test_s02_assay_batch_cycle_red.py`: pass
- `git diff --check`: pass

The fixture blocker is resolved. The remaining gate is the typed Adjudicator
approval for the Phase 3 final review; this record does not infer completion
from the passing automated checks.

## Final review decision (2026-09-11)

The typed final-review approval was received after the fixture correction.
D04 focused verification is **9 passed**. The related S02 command is **23
passed / 3 failed**; all three failures are in the unchanged LISS-0517
assay-profile DTO surface and are tracked outside LISS-0522. They do not
regress the D04 implementation or its tests.

`py_compile` and `git diff --check` pass. The D04 acceptance boundary,
fail-closed diagnostics, provider-neutral scope, and status synchronization
are accepted. LISS-0522/WP-0139 is complete.

Process review: no operating-contract deviation or operational problem found.
Next planned work is WP-0158/LISS-0541 Phase 0 acceptance/profile review.
