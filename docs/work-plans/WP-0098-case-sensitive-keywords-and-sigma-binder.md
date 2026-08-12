# WP-0098: case-sensitive blackboard keyword convention + Sigma/Pi binder unification

| Field | Value |
|---|---|
| Status | **approved_for_execution** (2026-08-12) — Adjudicator「承認」 |
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
| 1 | LISS-0415 | classical `sqrt`/`^` builtins | none |
| 2 | LISS-0416 | dedicated `In` keyword (distinct from lowercase `in`) | none |
| 3 | LISS-0417 | `{0,1}^n` set-literal domain expression | none |
| 4 | LISS-0418 | retire lowercase `state` → `State` (hard cutover, freed identifier) | none |
| 5 | LISS-0419 | capitalize remaining ten verb keywords (`Evolve`/`Measure`/`Mix`/`Coin`/`Dirac`/`Inspect`/`Vacuum`/`Snapshot`/`Superpose`/`ForEach`) | none |
| 6 | LISS-0420 | unify `sum`/`product` → `Sigma`/`Pi`; State-typed ket-sum body support | 0415, 0416, 0417 (own Red tests use final target spelling); benefits from 0418/0419 landing first too |

Execution order: **0415, 0416, 0417 (any order) → 0418, 0419 (any order) → 0420 last.**

## What this WP does not include

`main_selection.sqx` itself is not rewritten by this WP — a follow-on Issue
once LISS-0420 ships. Category-B builtin-function renames (`apply`,
`project`, `prepare_selection`, …) are explicitly declined for this round.

## Verification

Full regression sweep (`.venv/bin/python -m pytest -q`) and
`python3 tests/spec_verification/run_all.py` after **each** Issue. Every
scripted corpus migration (LISS-0418/0419) dry-run reviewed and swept with
`staqex check` across every touched `.sqx` file, matching LISS-0414's own
established discipline (that migration's f-string-corruption bug is the
reason this step is non-negotiable). LISS-0420's final check: a throwaway
snippet using `Sigma (x In {0,1}^n) { (1.0/sqrt(2.0^n)) * |x> }` produces the
same terminal distribution as `prepare_selection(8)` for `n=8`.
