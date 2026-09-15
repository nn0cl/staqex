# LISS-0548 Phase 3 Refactor Review

## Review packet

- Scope: Phase 3 review of the Scientific Semantic IR decomposition boundary.
- Canonical documents: core module decomposition spec, Scientific Semantic
  Core spec, consumer migration spec, ADR 0211, LISS-0548 Issue, and its
  trace.
- Changed files re-read: public facade, all six internal family modules and
  `legacy.py`, structural tests, Active-Red ledger, and Phase 0/2 review
  packets.

## Findings and dispositions

1. Public DTO and function names are exposed through the stable facade, while
   the family package owns named entrypoints. **Already closed with evidence:**
   the four structural tests pass.
2. The internal package does not import the public facade; the legacy bridge
   imports the model through the internal package and corrects its relative
   dependency level. **Already closed with evidence:** import collection,
   compile, and dependency-direction checks pass.
3. The bridge preserves the existing `source_id` keyword and object identity
   by delegating to the retained implementation. **Already closed with
   evidence:** semantic consumer tests execute through the facade.
4. The legacy implementation bodies remain in `legacy.py`. **Accepted bounded
   disposition:** this slice establishes the ownership and compatibility seam;
   moving each large body is successor work requiring its own exact snapshots.
   No claim of full body migration is made here.

## Blockers and known failures

- No Phase 3 decomposition blocker found.
- Two existing QASM expectation tests remain failed with
  `E_QPU_CANONICAL_PROVENANCE` instead of the expected
  `E_QPU_CANONICAL_PROJECTION_UNAVAILABLE`; no decomposition code was added to
  alter that unrelated diagnostic behavior.
- Live QPU/provider tests are not applicable.

## Deterministic verification

- LISS-0548 structural suite: 4 passed.
- Semantic-core/consumer suite: 50 passed, 2 pre-existing failures.
- `py_compile`: passed.
- `git diff --check`: passed.
- Document, coverage-ledger, and Active-Red lifecycle checks: passed.
- Isolation: `same_context`, weaker than `separate_context`.

## Reviewer empathy summary

The public entrypoint is now easy to locate, DTO ownership is explicit, and
the bridge makes the compatibility tradeoff visible. The remaining large
implementation body is named as successor scope rather than obscured by a
false completion claim.

## Final disposition

Adjudicator approval received: `LISS-0548 Phase 3 最終レビュー 承認`,
2026-09-15. The review is accepted and LISS-0548 may be marked done.
