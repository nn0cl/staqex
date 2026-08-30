# LISS-0480: Scientific lexicon and alias contract

| Field | Value |
|---|---|
| Status | **Phase 1 Red complete; Phase 2 Green approval required** |
| Phase | phase-1-red |
| Parent | WP-0092 |
| Design authority | [Quantum mental-model follow-up specification](../specs/staqex-v1-quantum-mental-model-follow-up.md#detailed-follow-up-issue-design) |
| Depends on | ADR 0189/0190 |
| Implementation permission | None; production lexicon implementation remains prohibited until Phase 2 Green approval |
| Next approval | Typed Phase 2 Green approval |

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

## Phase 1 Red result

- Added the v1 scientific lexicon matrix to the authoritative follow-up
  specification, including accepted aliases, contexts, collision rules,
  versioning, and actionable diagnostics.
- Added `tests/test_liss_0480_scientific_lexicon_contract_red.py` covering the
  matrix, canonical identity/provenance, deterministic alias collision, and
  unsupported spelling diagnostics.
- No production code, runtime behavior, provider integration, or Unicode
  migration was changed. The suite is intentionally Red until Phase 2.

## Phase 2 Green result

- Implemented the minimum lexer support for `psi`/`ψ`, `phi`/`φ`, and
  `rho`/`ρ`, retaining `canonical_spelling` and `written_spelling` metadata.
- Added actionable `LEXICON_UNSUPPORTED_SPELLING` for the unlisted uppercase
  `Ψ` spelling and deterministic `LEXICON_COLLISION` for the tested duplicate
  state-name declaration slice.
- LISS-0480 suite and the existing Unicode punctuation regression suite pass:
  `13 passed`.
- Full repository pytest still contains compatibility failures outside this
  slice: the older ASCII-only test expects `ψ`/`φ`/`ρ` rejection, and existing
  semantic/QASM Red suites remain failing. These are recorded as follow-up
  migration work; they were not suppressed or changed here.

## Unicode alias adoption decision

The Adjudicator approved formal adoption of `ψ`/`φ`/`ρ` as v1 scientific-name
display aliases. The existing ASCII-only acceptance test was narrowed so that
these scientific names are accepted with provenance, while Unicode quantum
punctuation and operators remain ASCII-only. This resolves the specification
conflict identified in the Phase 3 review.

The lexer collision ownership finding remains open: scope-sensitive duplicate
declaration analysis must move to the parser/symbol-table layer in a follow-up
slice before this Issue can be marked done.
