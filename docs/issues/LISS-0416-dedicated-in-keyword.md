# LISS-0416: dedicated `In` keyword

## Metadata

- Local issue ID: LISS-0416
- Status: complete
- Type: Feature Path (`compiler/staqex/tokens.py` only)
- Priority: P2
- Planning size: S
- Owner / agent: Claude Code
- Parent: WP-0098 (batch `case-sensitive-keywords-and-sigma-binder`)
- Branch: `batch/case-sensitive-keywords-and-sigma-binder` (batch-level)
- GitHub Issue / PR: (opened at batch completion)

## Intent

ADR 0191's amendment (this batch) makes `In` the sole binder-domain
membership keyword for the future `Sigma`/`Pi` binder (LISS-0420) — a
genuinely separate, non-interchangeable reserved word from lowercase `in`,
which stays reserved for `forEach`'s classical collection iteration (a
different relation: "iterate over," not "is an element of"). This Issue
reserves the token; LISS-0420 is the actual grammar consumer.

## Scope

1. `tokens.py`: new `TokenKind.IN_SET` enum value.
2. `tokens.py`: register `"In": TokenKind.IN_SET` in `ACTIVE`, distinct from
   the existing `"in": TokenKind.IN` entry — plain dict-key case-sensitivity
   (confirmed exact-match lookup, `lexer.py:274` `if lexeme in ACTIVE`) means
   these are two independent, non-colliding table entries.

## Explicitly out of scope

- Any grammar production consuming `TokenKind.IN_SET` — that's LISS-0420's
  `Sigma`/`Pi` binder domain, once it exists. Until then, `In` is a reserved
  word usable nowhere (parses as an error wherever it appears), which is the
  correct and expected state for a keyword reserved ahead of its consumer.

## Design verification performed

1. Confirmed `In` and `in` lex to distinct token kinds (`IN_SET` vs. `IN`).
2. Confirmed `In` is rejected wherever it appears (no grammar production
   accepts it yet) — expected, not a bug, since LISS-0420 is the consumer.
3. Regression guard: `forEach x in collection { ... }` and the existing
   Operator-DSL `sum (i in Index<0..7>) { ... }`/`product (i in
   Index<0..1>) { ... }` binder domains are completely unaffected — still
   use lowercase `in`, unchanged (LISS-0420 is the Issue that migrates
   `sum`/`product`'s own domain keyword to `In`, not this one).

## Exit criteria

- [x] `In` lexes as a distinct token from `in`.
- [x] `forEach`'s `in` and the existing Operator-DSL `sum`/`product`
  binders' `in` are unaffected.
- [x] Full regression sweep passes; spec verification 100.00%.
