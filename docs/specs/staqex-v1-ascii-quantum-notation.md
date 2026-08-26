# Staqex v1 ASCII quantum notation acceptance specification

| Field | Value |
|---|---|
| Status | **Accepted — PR #339 merged 2026-08-04** |
| ADR | [ADR 0191](../architecture/adr/0191-ascii-quantum-notation-and-lexical-boundary.md) |
| Work plan | [WP-0094](../work-plans/WP-0094-ascii-quantum-notation.md) |

## Acceptance boundary

The source language must be keyboard-friendly while preserving compact quantum
notation. Unicode mathematical identifiers and punctuation are presentation
only, not source forms.

## EARS scenarios
```gherkin
Feature: ASCII quantum notation

  Scenario: ASCII ket is accepted
    Given a primary expression position
    When the source contains |psi>
    Then the lexer emits one ket literal

  Scenario: ASCII bra is accepted
    Given a primary expression position
    When the source contains <psi|
    Then the lexer emits one bra literal

  Scenario: ASCII tensor is accepted
    Given two quantum expressions
    When the source contains left *|* right
    Then the lexer emits one tensor operator

  Scenario: Tensor association preserves factor order
    Given three compatible quantum expressions
    When the source contains a *|* b *|* c
    Then it is equivalent to (a *|* b) *|* c
    And the product dimensions retain the order a, b, c

  Scenario: Tensor alias is semantically identical
    Given two compatible quantum expressions
    When the source contains tensor(a, b)
    Then it lowers to the same tensor operation as a *|* b
    And it is not a classical collection constructor

  Scenario: Tensor alias requires explicit arity
    Given three quantum expressions
    When the source contains tensor(a, b, c)
    Then compilation fails with an arity diagnostic
    And tensor(tensor(a, b), c) remains the explicit three-factor form

  Scenario: Tensor punctuation is exact
    Given source contains * | * with spaces
    When the source is tokenized
    Then it is not recognized as the tensor operator

  Scenario: Tensor and arithmetic require grouping
    Given a tensor expression mixed with ordinary multiplication or division
    When the source omits explicit parentheses
    Then compilation fails with a grouping diagnostic

  Scenario: Logical OR wins over a ket prefix
    Given the condition 100 == a || 10 == b
    When the source is tokenized
    Then || is one OR token
    And no ket literal is created

  Scenario: Spaced comparison is not a bra
    Given a comparison expression
    When the source contains a < psi
    Then < remains a comparison operator

  Scenario: Function aliases remain available
    Given keyboard-only source
    When the source contains ket(psi), bra(psi), or tensor(a, b)
    Then each form resolves to the corresponding quantum operation

  Scenario: Unicode source forms are rejected
    Given source contains ψ, ⟨, ⟩, ⊗, or †
    When the source is lexed
    Then compilation fails with a stable ASCII-source diagnostic

  Scenario: Full-width and unlisted mathematical source forms are rejected
    Given source contains full-width ASCII or an unlisted Unicode mathematical
      symbol
    When the source is lexed
    Then compilation fails with a stable ASCII-source diagnostic
```

## Required invariants

- Longest-match tokenization must recognize `||` before single `|`.
- No source identifier may depend on a Unicode keyboard.
- Ambiguous `<psi|` forms must fail closed or use the function alias; they must
  not be silently parsed as comparison expressions.
- Formatter output must be accepted again by the ASCII lexer.
- `*|*` is binary and left-associative; factor order is observable in the
  product type and lowering output.
- `tensor(a, b)` and `a *|* b` are one semantic operation, with the same type
  checks, arity rules, and diagnostics.
- Tensor construction is distinct from classical arrays and coefficient
  tensors.
- Unicode `⊗` is rejected as source, not silently rewritten during lexing.
- Full-width ASCII and unlisted Unicode mathematical symbols are rejected as
  source, not silently normalized by the lexer.
