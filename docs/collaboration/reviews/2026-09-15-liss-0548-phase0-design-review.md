# LISS-0548 Phase 0 Design Review

## Review packet

- Scope: Scientific Semantic IR decomposition design before Phase 1 Red.
- Canonical documents: `docs/specs/staqex-core-module-decomposition.md`,
  `docs/specs/staqex-scientific-semantic-core.md`,
  `docs/specs/staqex-scientific-semantic-consumer-migration.md`, ADR 0211,
  `docs/issues/LISS-0548-scientific-semantic-ir-decomposition.md`, and the
  LISS-0548 trace.
- Files re-read: `compiler/staqex/scientific_semantic_ir.py`, its 10 direct
  production import consumers, relevant semantic tests, and readiness/policy
  documents.

## Findings and dispositions

1. The proposed six-unit graph preserves one canonical semantic authority and
   keeps the public facade stable. **Already closed with evidence:** the
   ownership and dependency decisions match the accepted decomposition and
   semantic-core specifications.
2. DTO ownership is separated from fingerprinting, source construction,
   runtime projection, target projection, and explicit realization.
   **Already closed with evidence:** each responsibility has a named module
   and no provider boundary is introduced.
3. The builder/projection one-time boundary is explicit. **Already closed with
   evidence:** the design forbids rebuilding the core or invoking finite-binder
   lowering a second time from a consumer.
4. Consumer compatibility is bounded to the current 10 direct production
   imports and an export-manifest audit. **Already closed with evidence:** no
   import redirection or public retirement is included in this issue.
5. Observation dictionaries and inspection/rejection views remain in the
   canonical model/builder surface without inventing a second observation
   algebra. **Accepted as scope boundary:** any richer observation semantics
   is a separate issue.

## Blockers and risks

- No Phase 0 design blocker found.
- Main implementation risk is circular dependency between builder,
  qpu-projection, and realization. Phase 1 must make the import graph and
  single-build ownership executable tests.
- Full blocking baseline and live provider tests are Phase 2/3 verification;
  live QPU execution is out of scope.

## Verification

- `git diff --check`: passed.
- Document lifecycle check: passed.
- Coverage-ledger consistency check: passed.
- Runtime routing: `same_context`; this is weaker than `separate_context`.

## Reviewer empathy summary

A maintainer can begin at the stable facade, follow the dependency graph down
to immutable model data, and distinguish source construction from each
consumer projection. The design records the one-time canonical build rule and
the exact successor boundary instead of hiding unresolved ownership in a
generic utility module.

## Next approval

Request: `LISS-0548 Phase 1 Red 承認`.
