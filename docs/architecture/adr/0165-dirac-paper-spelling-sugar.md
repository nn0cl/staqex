# ADR 0165: Dirac paper spelling as surface sugar over `inner` / `outer`

## Status

**Proposed** (2026-08-01). Design candidate for
[LISS-0217](../../issues/LISS-0217-dirac-paper-spelling-sugar.md).

This ADR **does not authorize implementation**. It records the design question
and the constraints any accepted answer must satisfy. Red requires a separate
ship ADR and Adjudicator approval.

## Context

`CLAUDE.md` §Language Design Priority makes the physicist mental model primary
and prefers blackboard spelling on conflict (ADR 0095, `physicist-dx-harmony.md`).

ADR 0087 deliberately chose function calls for the Dirac algebra:

- Paper: ⟨φ|ψ⟩ and |ψ⟩⟨φ|
- Kernel: `inner(phi, psi)` and `outer(psi, phi)`

[`physicist-source-friction-ledger.md`](../physicist-source-friction-ledger.md)
records this as F-04, Class B, **an accepted trade rather than a defect** — the
reason was parser safety — and states the follow-up condition explicitly:
"sugar later must lower to Calls". The ledger's §5 asks that remaining Class B
items be promoted to ADRs once the Adjudicator picks design options, rather
than being patched silently inside showcases.

The parser pressure is real. `|` and `>` already carry meaning:

- ket literals `|0>`, `|+>`, and the Unicode ket forms
- comparison `>` / `>=`
- pipeline `|>` (ADR 0080 / 0122)

so `⟨φ|ψ⟩` and especially a named ket `|psi>` sit close to existing tokens.
F-04 records that a named ket `|psi>` is **not accepted** today.

## Dependency Adoption Evidence

Not applicable. No library, framework, SDK, datastore client, build tool, or
test helper is selected by this ADR.

## Decision (candidate — not accepted)

The question this ADR opens, and the constraints any accepted answer must meet:

1. **Sugar only.** Any accepted spelling lowers to `inner` / `outer` Calls
   during parse or a desugaring pass. Semantics stay exactly as ADR 0087
   defines them; the evaluator does not change.
2. **Grammar must stay unambiguous.** The accepted answer states the
   disambiguation rule against ket literals, comparison, and pipeline `|>`, and
   names the alternatives it rejects and why. Parser safety was ADR 0087's
   stated reason; a sugar that erodes it is not an improvement.
3. **Named kets are a separate decision.** If the spelling requires accepting
   `|psi>`, that reopens an F-04 line item and needs its own ruling — it is not
   carried implicitly by accepting the inner-product sugar.
4. **Round-trip obligations are in scope.** `format.py` / the CST must
   round-trip the sugar, and `migrate_unicode_math.py` must be considered.
   (Note the migrator today re-implements the lexer's Dirac character classes
   instead of importing them — see
   [LISS-0210](../../issues/LISS-0210-duplicated-kernel-constants.md).)
5. **Scope is stated as a first slice.** Inner product alone, or inner and
   outer together, decided explicitly rather than left open.

## Consequences

Positive:

- A many-body or quantum-information source file can be read against the paper
  it came from without transliterating every bracket into a call.
- Discharges an explicitly-deferred ledger item through an ADR, which is what
  the ledger asks for, instead of ad-hoc patches inside showcases.

Negative:

- Grammar risk in the most contested corner of the lexer. A mistake here is
  paid by every program, not only by the ones using the sugar.
- Two spellings for one meaning. Teaching material, the formatter, and the
  migrator must all pick a canonical form.
- If named kets are pulled in, the surface change is materially larger than
  "sugar".

## Enforcement

Code review should reject:

- A Dirac spelling that does not lower to `inner` / `outer` Calls.
- Any evaluator or typechecker change justified by this ADR.
- Kernel Red started against this ADR — it is `Proposed` and authorizes nothing.
- A grammar change that does not state its disambiguation rule against ket
  literals, comparison, and `|>`.
