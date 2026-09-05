# LISS-0480: Scientific lexicon and alias contract

| Field | Value |
|---|---|
| Status | **done — Phase 3 refactor and review complete** |
| Phase | phase-3-refactor-complete |
| Parent | WP-0092 |
| Design authority | [Quantum mental-model follow-up specification](../specs/staqex-v1-quantum-mental-model-follow-up.md#detailed-follow-up-issue-design) |
| Depends on | ADR 0189/0190 |
| Implementation permission | Granted only for the bounded lexicon metadata slice |
| Next approval | None for this Issue; broader lexicon changes require a new Issue/phase approval |

## Scope

Define canonical ASCII spellings, display aliases, token classes, contexts,
shadowing, versioning, and actionable diagnostics for the scientific lexicon.

## Acceptance scenarios

- Aliases map to one AST/semantic meaning and preserve written-form provenance.
- Shadowing and declaration-context collisions are deterministic.
- Unsupported spelling fails with an actionable diagnostic.
- No alias introduces a second semantic dialect.

## Exclusions and stop conditions

No mandatory Unicode migration, broad syntax rewrite, provider, or runtime
behavior. Stop for ADR review if grammar ownership or compatibility policy
changes.

## Phase 1 candidate files

Lexicon matrix, source fixtures, lexer/parser Red tests, and diagnostics only.

## Phase 1 Red execution record

- Typed approval: user message `LISS-0480 Phase 1 Red 承認`, 2026-09-04.
- Added `tests/fixtures/scientific_lexicon/aliases_and_contexts.sqx`,
  `tests/fixtures/scientific_lexicon/shadowing.sqx`, and
  `tests/test_liss_0480_scientific_lexicon_contract_red.py`.
- The packet covers canonical ASCII/display identity, written-form
  provenance, token class/context, deterministic shadowing, actionable
  unsupported-spelling diagnostics, and the no-second-dialect rule.
- Red verification: **5 failed**, with no collection errors. The failures are
  expected because the Phase 2 lexicon inspection API is not implemented.
- Existing alias implementation was not modified; mandatory Unicode
  migration and broad syntax changes remain excluded.
- `git diff --check` passed.

Phase 2 Green requires a separate approval and remains limited to the reviewed
lexicon contract. Provider, runtime, and broad syntax work remain excluded.

## Phase 2 Green execution record

- Typed approval: user message `承認`, 2026-09-04.
- Added `compiler/staqex/scientific_lexicon_contract.py`.
- The read-only inspection API records canonical ASCII identity, display
  symbol, written-form provenance, token class, typed context, shadowing
  policy, and `cm` → commutator meaning without introducing a second dialect.
- Existing lexer/parser behavior remains authoritative. Unicode source remains
  rejected with an actionable ASCII fix-it; no mandatory Unicode migration or
  broad syntax rewrite was added.
- Verification: LISS-0480 and existing scientific-alias tests **8/8 passed**;
  `py_compile` and `git diff --check` passed.

Phase 3 requires a separate approval and is limited to readability/refactor,
review evidence, and status synchronization.

## Phase 3 closeout

- Typed approval: user message `LISS-0480 Phase 3 承認`, 2026-09-04.
- Refactor: the accepted display-symbol inventory is immutable and shared
  constants make scientific versus ordinary context explicit. Existing
  lexer/parser behavior and all contract values are unchanged.
- Verification after refactor: LISS-0480 and existing alias tests **8/8
  passed**; `py_compile` and `git diff --check` passed.
- Same-context review: `COMPLETE` / `READY`; no blocking finding. Review
  packet: `docs/collaboration/reviews/2026-09-04-liss-0480-phase3-review.md`.
- Process review: no operating-contract deviation or operational problem found.

The bounded lexicon metadata contract is complete. Further aliases,
mandatory migrations, grammar changes, and runtime/provider behavior require a
new specification or Issue with its own typed approval.
