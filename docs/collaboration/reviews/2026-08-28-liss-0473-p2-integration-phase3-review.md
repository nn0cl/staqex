# LISS-0473 P2 integration Phase 3 review

| Field | Value |
|---|---|
| Issue | [LISS-0473](../../issues/LISS-0473-documentation-compression-classifier.md) |
| Work plan | [WP-0090](../../work-plans/WP-0090-documentation-canonicalization.md) |
| Phase | Phase 3 refactor/review |
| Isolation | same_context (runtime routing file absent; weaker than separate-context) |
| Reviewer | Codex host agent, reviewer role |
| Date | 2026-08-28 |

## Canonical documents and files re-read

- `docs/architecture/implementation-readiness.md`
- `docs/architecture/documentation-canonicalization-policy.md`
- `docs/issues/LISS-0473-documentation-compression-classifier.md`
- `docs/work-plans/WP-0090-documentation-canonicalization.md`
- `scripts/documentation_compression.py`
- `tests/test_liss_0473_documentation_compression_classifier_red.py`
- `docs/collaboration/process-lessons-log.md`

No prior author reasoning was treated as review evidence. No provider, network,
or deletion operation was used.

## Findings and dispositions

### P1 — classification is not observable at the command boundary

`candidates()` converts only `candidate=True` results into `Candidate` values,
which do not carry the classification. The CLI then prints only those
candidate rows. As a result, the required dispositions
`retain-canonical`, `retain-evidence`, `index-pointer`, and
`unresolved-review` are available only through the internal pure API, not in
the candidate-generation output that a reviewer would inspect.

Disposition: blocker; add a reviewed output/report boundary that preserves the
classification, reason, and source path for every scanned record. Do not make
this a deletion operation.

### P2 — no end-to-end positive candidate fixture

The current filesystem scan produces `candidate_count=0`. That is fail-closed,
but the integration tests prove only protected exclusions and delegation. The
genuinely safe completed-record case is tested against `classify_records`
directly, not through `candidates()` and the filesystem record builder.

Disposition: follow-up test/implementation slice; add an isolated deterministic
filesystem fixture or injectable record source that proves one safe candidate
flows through the integrated boundary without touching the current document
tree.

### P2 — obsolete and brittle integration code remains

`historical_candidate` is no longer called, but remains as a second legacy
classification path. `_record_has_review_evidence` also detects review paths by
searching for an absolute-path substring, which is host-layout dependent.

Disposition: bounded Phase 3 refactor in the next approved slice: remove the
dead path and use repository-relative path classification, then rerun the
existing deterministic checks.

## Positive observations

- The pure classifier is deterministic and protects referenced, reviewed, and
  unresolved records.
- `incomplete` and `not complete` no longer pass as completed statuses.
- The filesystem scan is read-only and currently fails closed with zero
  candidates.
- Compression-map recovery rows and baseline pointers were not rewritten.

## Deterministic verification

- `python3 tests/test_liss_0473_documentation_compression_classifier_red.py` — passed.
- `python3 -m py_compile scripts/documentation_compression.py` — passed.
- `python3 scripts/documentation_compression.py` — passed; `candidate_count=0`.
- `git diff --check` — passed.

## Blockers

The P1 command-boundary classification gap blocks acceptance of LISS-0473.
No deletion batch is authorized.

## Reviewer empathy summary

The implementation is conservative, but a maintainer inspecting the command
output cannot tell whether a file was retained as canonical, retained as
evidence, already indexed, or left unresolved. The next slice should make
those dispositions explicit and demonstrate one safe positive candidate at the
same boundary before any deletion decision is considered.

## Next requested approval

Adjudicator approval for **LISS-0473 follow-up Phase 1 Red** covering the
command-boundary disposition report, an end-to-end safe-candidate fixture, and
the bounded cleanup of the obsolete/brittle integration path.
