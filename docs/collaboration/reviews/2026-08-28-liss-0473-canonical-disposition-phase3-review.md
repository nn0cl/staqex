# LISS-0473 canonical disposition Phase 3 review

| Field | Value |
|---|---|
| Issue | [LISS-0473](../../issues/LISS-0473-documentation-compression-classifier.md) |
| Work plan | [WP-0090](../../work-plans/WP-0090-documentation-canonicalization.md) |
| Phase | Canonical disposition Phase 3 refactor/review |
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

### P1 — Canonical paths are not part of the filesystem scan

`CANONICAL_PATHS` contains current canonical pages, but `_classification_records`
only scans `SOURCE_ROOTS` (`docs/issues`, `docs/work-plans`, and traces). The
normal CLI therefore never creates records with `canonical=True`; it cannot
emit `retain-canonical` for the pages the new signal is intended to protect.
The direct unit test proves only the pure classifier branch.

Disposition: blocker; make the Canonical input signal observable at the
filesystem/report boundary and add an integration assertion for it. No
deletion is authorized.

### P2 — report test does not include the Canonical disposition

The report test checks the three classifications represented in its fixture,
while the Canonical test calls `classify_records` directly. The complete
four-disposition report contract is therefore not tested at one boundary.

Disposition: follow-up Red coverage; include a canonical fixture in the report
test after the scan boundary is defined.

### P2 — prior cleanup findings remain

The dead `historical_candidate` helper and absolute-path review detection from
the earlier review remain unchanged.

Disposition: retain as bounded follow-up refactor; not a deletion authorization.

## Positive observations

- Explicit Canonical classification is deterministic and fail-closed in the
  pure API.
- Canonical records cannot become candidates once the signal is supplied.
- Existing tests, syntax compilation, CLI execution, and diff checks pass.

## Deterministic verification

- `python3 tests/test_liss_0473_documentation_compression_classifier_red.py` — passed.
- `python3 -m py_compile scripts/documentation_compression.py` — passed.
- `python3 scripts/documentation_compression.py` — passed; no
  `retain-canonical` rows were emitted by the normal scan.
- `git diff --check` — passed.

## Blockers

The normal filesystem/report path does not exercise the new Canonical signal,
so the acceptance boundary remains incomplete. No deletion batch is
authorized.

## Reviewer empathy summary

The pure classifier appears complete in isolation, but the actual command
cannot observe the new input because its scan excludes the canonical pages.
Making the source discovery and report fixture share the same boundary will
prevent a future maintainer from trusting a branch that production scanning
never reaches.

## Next requested approval

Adjudicator approval for **LISS-0473 canonical disposition follow-up Phase 1
Red**, covering filesystem inclusion of Canonical records and a complete
four-disposition report fixture.
