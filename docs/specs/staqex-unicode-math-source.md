# Staqex Unicode mathematical source (LISS-0069 historical)

> Superseded for source syntax by [ADR 0191](../architecture/adr/0191-ascii-quantum-notation-and-lexical-boundary.md).
> This document is retained only as migration history; Unicode forms are no
> longer accepted by the lexer.

| Field | Value |
|---|---|
| Status | **Slice A complete**; Slice B migrator plan in [`staqex-unicode-math-migrator.md`](staqex-unicode-math-migrator.md) |
| Authority | ADR 0106 Unicode scope; ADR 0095; [`staqex-language-specification.md`](staqex-language-specification.md) v1.0 §2 |
| Migration | [`staqex-v1-migration-matrix.md`](staqex-v1-migration-matrix.md) M-P02–M-P04 |
| Last updated | 2026-07-28 |

This companion freezes the **Slice A** surface contract for dual-accept Unicode
math tokens. It does not authorize Green implementation until LISS-0069 plan
approval and Phase 1 Red review.

## 1. Goals

1. One **canonical emitted** spelling (formatter/migrator): Unicode Dirac /
   dagger / tensor.
2. **Dual-accept** at parse time during the transition window.
3. No collision between pipeline `|>` and ket close `⟩`.
4. Same semantic IR nodes as today’s ASCII spellings.

## 2. Token mapping (Slice A)

| Form | Code points (informative) | Shipping ASCII | AST / IR target |
|---|---|---|---|
| Ket | `\|` … `⟩` (U+27E9) | `\|label>` | existing `KetLit` (label = interior) |
| Bra | `⟨` (U+27E8) … `\|` | — | **Slice A:** lexer `BRA` token only; matrix-element / `inner` desugar → Slice A.1 / LISS-0073 |
| Tensor | `⊗` (U+2297) | `*|*` | existing `TENSOR_OP` / tensor bind |
| Adjoint | postfix `†` (U+2020) | `adjoint(expr)` | desugar to same call/node as `adjoint` |
| Pipeline | `\|` `>` | `\|>` | existing `PIPE_OP` — **unchanged** |

### Lexer ordering rule (Normative)

When scanning `|`:

1. If next char is `>`, emit `PIPE_OP` (`|>`).
2. Else scan a ket label until either ASCII `>` or Unicode `⟩`.
3. Never treat `⟩` as the second character of a pipeline.

`⊗` is a single-character operator token alternate for `TENSOR_OP`.
Postfix `†` binds tighter than pipeline and attaches to a primary/call
expression (exact precedence table locked in Red assertions).

## 3. Normalization

- Source files are read as UTF-8.
- Slice A: apply **NFC** before lexing identifiers and math tokens, or document
  an equivalent boundary if the stdlib path differs — Red tests must pin the
  chosen contract.
- Confusable-identifier diagnostics: stub or hard code TBD in Red; must not
  silently merge distinct NFC forms.

## 4. Diagnostics (proposed)

| Code | When |
|---|---|
| `LEX_ERROR` | Unterminated ket/bra (missing `>` / `⟩` / `⟨` pair) |
| `UNICODE_MATH_CONFUSABLE` (TBD) | Identifier confusable pair (may be warn-only in Slice A) |
| existing codes | Semantic errors unchanged |

Public codes require catalog sync on Green (Appendix K).

## 5. Dual-accept policy

- Valid: ASCII ket **or** Unicode ket in the same program.
- Migrator (Slice B) prefers Unicode output for M-P02–M-P04.
- **No** deprecate/remove diagnostics in Slice A.
- Pauli ASCII atoms remain fully valid (M-P01 not activated).

## 6. Acceptance envelopes (Slice A)

### EARS

When a program contains a Unicode ket `|label⟩`, the system shall accept it
whenever the ASCII ket `|label>` would be accepted for the same label.

When a program contains `⊗` between tensor operands, the system shall accept
it whenever `*|*` would be accepted.

When a program contains postfix `†` on an operator or state primary, the
system shall treat it as `adjoint(...)` of that primary.

When the lexer sees `|>`, the system shall emit pipeline, not a ket.

### Gherkin (representative)

```gherkin
Feature: Unicode math dual-accept

  Scenario: Unicode ket parses like ASCII ket
    Given source with "state psi = |0⟩"
    When the program typechecks
    Then compilation succeeds
    And the bound ket label is "0"

  Scenario: Pipeline does not steal ket close
    Given source using both "|>" and "|+⟩"
    When the lexer runs
    Then "|>" is PIPE_OP
    And "|+⟩" is a ket with label "+"

  Scenario: Tensor Unicode matches ASCII
    Given a valid ASCII "*|*" tensor program
    When "*|*" is replaced by "⊗"
    Then the program remains Valid with the same semantics
```

## 7. Verification plan

- Phase 1 Red: new tests under `tests/` (lexer-focused module name TBD).
- After Green: `python3 tests/spec_verification/run_all.py` remains 160/160+.
- No forced rewrite of `examples/` in Slice A.

## 8. Out of scope

See LISS-0069 Issue non-goals. Formatter-owned emit and CLI migrate are
Slices B/C.
