# WP-0094: ASCII quantum notation and Unicode input removal

| Field | Value |
|---|---|
| Status | **Complete — PR #339 merged 2026-08-04** |
| ADR | [ADR 0191](../architecture/adr/0191-ascii-quantum-notation-and-lexical-boundary.md) |
| Specification | [ASCII notation acceptance](../specs/staqex-v1-ascii-quantum-notation.md) |
| Parent direction | [Physicist × DX harmony](../architecture/physicist-dx-harmony.md) |

## Objective

Retain compact ket, bra, and tensor notation while making every source
expression writable on an ordinary ASCII keyboard.

## Planned sequence

### Phase 0 — Design

- [x] Select ASCII canonical forms: `|psi>`, `<psi|`, `*|*`.
- [x] Retain `ket(...)`, `bra(...)`, and `tensor(...)` aliases.
- [x] Define `||` longest-match precedence.
- [x] Reject Unicode identifiers and quantum punctuation as source syntax.
- [x] Define tensor factor order, binary arity, and exact `*|*` spelling.
- [x] Define explicit grouping for tensor/arithmetic mixtures.
- [x] Confirm and implement `tensor(...)` prelude/AST lowering parity.
- [x] Obtain ADR and specification approval.

### Phase 1 — Red

- [x] Add lexer tests for ASCII ket, bra, tensor, and Boolean OR.
- [x] Add rejection tests for Unicode identifiers and punctuation.
- [x] Add parser tests for primary-position bra disambiguation.
- [x] Add tensor associativity, alias parity, arity, factor-order, and grouping
      tests.

### Phase 2 — Green

- [x] Implement ASCII bra lexing without changing comparison semantics.
- [x] Remove Unicode tensor, bra, ket-close, and dagger source paths.
- [x] Preserve function aliases and formatter round-tripping.
- [x] Register `tensor` as the canonical alias or record an explicit decision
      to remove it; do not leave a documentation-only alias.

### Phase 3 — Refactor

- [x] Migrate grammar, examples, and documentation.
- [x] Verify all condition expressions and existing `*|*` tensor programs.
- [x] Record remaining display-only Unicode policy.

## Phase 3 evidence

- Implementation commit: `773661f` on `codex/wp0094-tensor-hardening`.
- Focused Tensor parity suite: PASS.
- ASCII notation, Dirac AST, and Unicode rejection regression suites: PASS.
- Spec verification: 161/161 PASS.
- Completion PR: #339 (merged 2026-08-04).
- Post-merge verification: PR checks passed; main contains the implementation
  and acceptance evidence.
## Explicit non-goals

- No new quantum semantics.
- No change to `mix`, `controlled`, `project`, or terminal `measure`.
- No implicit conversion of full-width Latin characters to ASCII names.
