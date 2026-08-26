# WP-0098: case-sensitive blackboard keyword convention + Sigma/Pi binder unification

| Field | Value |
|---|---|
| Status | **complete** (2026-08-13) — LISS-0415–0420 all Green/Refactor complete; full regression 1511 passed; spec verification 100.00% (161/161) |
| Purpose | Extend ADR 0191's ASCII-spelling rule with a case axis: capitalized spellings for tokens standing in for a blackboard symbol/operator (`Sigma`, `Pi`, `State`, and the existing `X`/`Y`/`Z`/`Suzuki`/`Index` precedent); lowercase stays for connective/procedural keywords. Unify the Operator-DSL `sum`/`product` binder with a new State-typed ket-sum capability under one `Sigma`/`Pi` keyword pair. |
| Parent | Design-review session re-examining S02's `main_selection.sqx` against the actual blackboard physics (see [S02 README's Physics ↔ program section](../../examples/showcase/S02_drug_discovery/README.md)) — found Staqex has no way to write a State as a literal sum over basis kets |
| Investigation | Plan file content folded into this WP + the batch record below; two of the investigating agent's own technical claims were wrong and corrected after actually running the parser (see "Corrections" in the batch proposal notes) |
| Execution branch | `batch/case-sensitive-keywords-and-sigma-binder` |
| Batch record | [execution-batch-case-sensitive-keywords-and-sigma-binder.json](../collaboration/reviews/execution-batch-case-sensitive-keywords-and-sigma-binder.json) — **`status: approved_for_execution`** |

## Confirmed decisions

1. Retire lowercase `state` (hard cutover, no alias); freed as an ordinary identifier.
2. `product` → `Pi`. No collision with the reserved constant `pi` — verified: `pi`/`Pi` are resolved via a case-sensitive exact-string membership check (`evaluator.py:5198`/`5422`, `typecheck.py:3114`), so `"Pi" in {"pi", ...}` is `False`.
3. Category-A scope only: reserved *keywords* (`tokens.py` `ACTIVE`/binder names). Built-in *functions* resolved by string-name dispatch (`apply`, `capply`, `project`, `prepare_selection`, …) are explicitly out of scope.
4. Amends ADR 0191 (same lexical-boundary topic), not a new ADR number.
5. Broad scope: every Category-A keyword, not just `Sigma`/`In`.
6. `In` (capitalized) is the sole binder-domain membership keyword for `Sigma`/`Pi` (including the domain that today reads `sum (i in Index<0..7>)`); lowercase `in` stays reserved for `forEach`'s classical collection iteration only.

## Issue rows

| Order | ID | Title | Depends |
|---|---|---|---|
| 1 | [LISS-0415](../issues/LISS-0415-classical-float-power.md) | classical `sqrt`/`^` builtins (scope reduced to `^` only — `sqrt` was already shipped by LISS-0356) | none | **complete** |
| 2 | [LISS-0416](../issues/LISS-0416-dedicated-in-keyword.md) | dedicated `In` keyword (distinct from lowercase `in`) | none | **complete** |
| 3 | [LISS-0417](../issues/LISS-0417-set-power-domain-literal.md) | `{0,1}^n` set-literal domain expression | none | **complete** |
| 4 | [LISS-0418](../issues/LISS-0418-retire-lowercase-state.md) | retire lowercase `state` → `State` (hard cutover, freed identifier) | none | **complete** |
| 5 | [LISS-0419](../issues/LISS-0419-capitalize-verb-keywords.md) | capitalize remaining ten verb keywords (`Evolve`/`Measure`/`Mix`/`Coin`/`Dirac`/`Inspect`/`Vacuum`/`Snapshot`/`Superpose`/`ForEach`) | none | **complete** |
| 6 | [LISS-0420](../issues/LISS-0420-sigma-pi-unification.md) | unify `sum`/`product` → `Sigma`/`Pi`; State-typed ket-sum body support | 0415, 0416, 0417, 0418, 0419 | **complete** |

Execution order: **0415, 0416, 0417 (any order) → 0418, 0419 (any order) → 0420 last.**

## What this WP does not include

`main_selection.sqx` itself is not rewritten by this WP — a follow-on Issue
once LISS-0420 ships. Category-B builtin-function renames (`apply`,
`project`, `prepare_selection`, …) are explicitly declined for this round.

## Completion summary

All six Issues shipped, in order, each self-verified (full regression +
spec verification) before the next began. Two Hard Stops during LISS-0420
were escalated to the Adjudicator rather than resolved unilaterally: how
`|x>` binds to a Sigma-loop variable's runtime value (KetLit's scope was
extended, narrowly — see LISS-0420's own doc), and how the external
normalization coefficient applies at runtime (literal application,
verified to produce an honest unnormalized result when redundant,
matching this codebase's own no-silent-normalization precedent). Several
real, pre-existing bugs were found and fixed along the way — most
notably LISS-0418's five gaps in bare `State` Type-First handling
(exposed only because the corpus migration made that combination common
for the first time) and LISS-0420's regression against LISS-0273's
classical/State boundary (found and narrowed before merge). Final state:
1511 tests passed (up from the pre-batch 1476 baseline), spec
verification 100.00% (161/161), full `.sqx` corpus `staqex check` clean.

## Verification

Full regression sweep (`.venv/bin/python -m pytest -q`) and
`python3 tests/spec_verification/run_all.py` after **each** Issue. Every
scripted corpus migration (LISS-0418/0419) dry-run reviewed and swept with
`staqex check` across every touched `.sqx` file, matching LISS-0414's own
established discipline (that migration's f-string-corruption bug is the
reason this step is non-negotiable). LISS-0420's final check: a throwaway
snippet using `Sigma (x In {0,1}^n) { (1.0/sqrt(2.0^n)) * |x> }` produces the
same terminal distribution as `prepare_selection(8)` for `n=8`.
