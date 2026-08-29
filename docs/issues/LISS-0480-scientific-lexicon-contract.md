# LISS-0480: Scientific lexicon and alias contract

| Field | Value |
|---|---|
| Status | **ready — design complete; specification/Phase 1 approval required** |
| Phase | phase-0-design |
| Parent | WP-0092 |
| Design authority | [Quantum mental-model follow-up specification](../specs/staqex-v1-quantum-mental-model-follow-up.md#detailed-follow-up-issue-design) |
| Depends on | ADR 0189/0190 |
| Implementation permission | None |
| Next approval | Architecture/spec review, then typed Phase 1 Red approval |

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
