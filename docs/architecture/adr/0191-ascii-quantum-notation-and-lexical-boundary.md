# ADR 0191: ASCII quantum notation and lexical boundary

| Field | Value |
|---|---|
| Status | **Accepted — PR #339 merged 2026-08-04.** Amended 2026-08-12 (case-sensitive keyword spelling) — Adjudicator approval via WP-0098 batch record. |
| Date | 2026-08-04 |
| Scope | Ket, bra, tensor notation, and Unicode input policy |
| Related | ADR 0189, ADR 0190, WP-0094, WP-0098 |

## Context

Staqex should retain compact physics-facing notation without requiring a
Unicode-capable keyboard. The ASCII sequence `||` is already the logical OR
operator, so a lexer that treats every single `|` as the start of a ket can
misread expressions such as:

```text
100 || psi > 10
```

The language also currently accepts Unicode mathematical punctuation and
Unicode identifiers. That is inconsistent with the decision that `psi`,
`phi`, and `rho` are the canonical source spellings.

## Proposed decision

1. Canonical source spellings are ASCII:

   ```text
   |psi>       // ket literal
   <psi|       // bra literal
   a *|* b     // tensor product
   ```

2. ASCII aliases remain available for unambiguous and machine-generated
   source:

   ```text
   ket(psi)
   bra(psi)
   tensor(a, b)
   ```

3. Unicode identifiers and Unicode quantum punctuation are not source syntax.
   This includes `ψ`, `φ`, `ρ`, `⟨`, `⟩`, `⊗`, and `†`.
   Full-width Latin letters, full-width ASCII punctuation, and other Unicode
   mathematical symbols are also not alternate source spellings. They must be
   rejected or handled by an explicit source-normalization tool outside the
   lexer; the lexer must not silently normalize them.

4. Lexical precedence is explicit:

   - `||` is recognized before a single `|`.
   - `|identifier>` is a ket only when the complete ASCII delimiter is
     present.
   - `<identifier|` is a bra only in a primary-expression position and only
     when the delimiters are adjacent; `< psi |` remains ordinary comparison /
     operator syntax.
   - `*|*` is a dedicated ASCII tensor operator, recognized as one token before
     `*` is considered independently.

   Tensor-specific rules are also explicit:

   - `*|*` is a binary, left-associative quantum product. Thus
     `a *|* b *|* c` means `(a *|* b) *|* c` and preserves factor order.
   - `tensor(a, b)` is a semantic alias for the same binary operation, not a
     classical array or coefficient-tensor constructor. Three or more factors
     must be written with explicit nesting; variadic folding is not implicit.
   - Mixing tensor product with ordinary arithmetic multiplication or division
     requires parentheses. This prevents a scalar product from silently
     becoming a tensor factor and makes lowering boundaries reviewable.
   - The exact token `*|*` is required. `* | *` is not a tensor operator and
     must not be normalized into one.

6. Tensor operands are checked at the quantum semantic boundary:

   - Operands must be compatible quantum states or quantum operators; a
     classical collection or numeric coefficient is not accepted merely because
     it is passed to `tensor(...)`.
   - The result retains ordered factor identity and product dimensions. No
     silent dimension coercion or factor reordering is permitted.
   - The infix and alias forms must lower to the same AST/IR operation and have
     identical diagnostics and runtime behavior.

7. When an ASCII notation is ambiguous, the compiler emits a diagnostic that
   points to `ket(...)`, `bra(...)`, or `tensor(...)`; it must not guess.

8. Formatter and documentation may render Unicode chalk as presentation, but
   formatted source must remain ASCII-reproducible.

## Consequences

Positive:

- International users can write all quantum expressions with ordinary
  keyboards.
- Conditions such as `100 == a || 10 == b` remain ordinary Boolean syntax.
- Physicist-facing short notation is retained where delimiters make its
  meaning deterministic.

Costs:

- `<psi|` needs a dedicated ASCII bra lexing rule because `<` is also a
  comparison operator.
- Existing Unicode notation tests and grammar productions must be migrated.
- The formatter becomes responsible for any optional Unicode presentation.
- Tensor alias lowering and its arity/grouping boundaries are implemented;
  focused acceptance evidence is recorded in WP-0094. Completion is recorded
  by PR #339.

## Non-goals

- Changing the meaning of `mix`, `controlled`, `project`, or `measure`.
- Adding implicit multiplication or a new Boolean expression model.
- Accepting full-width Latin characters as ASCII identifiers.

## Gate

This ADR is accepted as the source-language boundary. Implementation evidence
and the remaining final-review gate are recorded in WP-0094; no compatibility
fallback or alternate Unicode source semantics are implied.

## Amendment (2026-08-12): case-sensitive keyword spelling for blackboard symbols

Approved by the Adjudicator as part of the WP-0098 batch record
(`docs/collaboration/reviews/execution-batch-case-sensitive-keywords-and-sigma-binder.json`).
Originated from a design-review session finding Staqex had no way to write a
State as a literal sum over basis kets, and generalizing the fix into a
language-wide convention.

### Amended decision

1. **Case is a semantic axis, not decoration.** Extending this ADR's existing
   "canonical ASCII spelling" rule (§1–3 above): a capitalized ASCII spelling
   is reserved for a keyword that stands in for one specific blackboard
   symbol or operator. A lowercase spelling stays reserved for a connective
   or procedural keyword with no single blackboard glyph. This is the same
   underlying principle as `psi`/`phi`/`rho` (§1) — canonical ASCII spelling
   of the symbol's read-aloud name — with case added as a second, orthogonal
   signal. It does not relax §3's Unicode ban; `Σ`/`Π`/`∈` remain rejected
   exactly as `ψ`/`⟨`/`⟩` already are.
2. **`state` is retired**, hard cutover (no back-compat alias, matching this
   project's own `fun`→`fn`/`public`→`pub`/`evolve{}.run()` precedent).
   `State` (already an existing, shipped Type-First spelling — see
   `TYPE_HEADS` in `compiler/staqex/dimensions.py`) becomes the sole
   canonical declaration spelling. Once retired as a keyword, `state`
   becomes an ordinary available identifier.
3. **Ten further verb keywords are capitalized**, hard cutover: `evolve`→
   `Evolve`, `measure`→`Measure`, `mix`→`Mix`, `coin`→`Coin`, `dirac`→
   `Dirac`, `inspect`→`Inspect`, `vacuum`→`Vacuum`, `snapshot`→`Snapshot`,
   `superpose`→`Superpose`, `forEach`→`ForEach`.
4. **`sum`/`product` are retired in favor of `Sigma`/`Pi`** (Σ/Π), which also
   gain a State-typed body (a literal sum over basis kets, previously
   inexpressible in Staqex source at all — see LISS-0420) alongside the
   existing Operator-typed body. Every `Sigma`/`Pi` binder domain uses a new
   dedicated `In` keyword (∈) — including the domain that previously read
   `sum (i in Index<0..7>)`.
5. **`In` and lowercase `in` are two separate, non-interchangeable reserved
   words**, not a case-insensitive alias. `In` denotes set/domain membership
   inside a `Sigma`/`Pi` binder only. Lowercase `in` remains reserved for
   `forEach`'s classical collection iteration — a different relation
   ("iterate over," not "is an element of").
6. **Explicitly out of scope**: built-in *functions* resolved by string-name
   dispatch rather than a reserved keyword (`apply`, `capply`, `ocapply`,
   `project`, `controlled`, `toffoli`, `prepare_selection`, `feasible`,
   `expect`, `host`, `finiteize`, `map`, …) are not renamed by this
   amendment. Everything else in `tokens.py`'s `ACTIVE`/`CONTEXTUAL` tables
   not listed above (`class`, `struct`, `fn`, `let`, `return`, `package`,
   `import`, `namespace`, `enum`, `this`, `val`, `var`, `module`, `exports`,
   `requires`, `private`, `else`, `pub`, `true`, `false`, `to`, `times`,
   `for`, `under`, `in`, `until`, `max`, `onto`) is scaffolding/connective,
   not a blackboard-symbol verb, and stays lowercase.

### Non-goals (amendment)

- Renaming Category-B built-in functions (see Decision 6 above) — a
  separate, larger, and more invasive change (touches evaluator.py/
  typecheck.py string-name dispatch at many sites, not one lexer table),
  explicitly declined for this round.
- Retroactively re-litigating already-capitalized tokens that predate this
  amendment (Pauli `X`/`Y`/`Z`, `Suzuki`, `Index`) — they were already
  consistent with the convention this amendment formalizes.

### Gate (amendment)

Tracked under WP-0098 (`docs/work-plans/WP-0098-case-sensitive-keywords-and-sigma-binder.md`),
Issues LISS-0415 through LISS-0420. `main_selection.sqx` itself is not
touched by this amendment or WP-0098; rewriting it to the new syntax is a
separate follow-on Issue.
