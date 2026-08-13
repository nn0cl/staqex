# WP-0099: S02 step 2 literal Σ/∀/min/projector transcription

| Field | Value |
|---|---|
| Status | investigation complete, ADR 0207 **Accepted** (2026-08-13) — awaiting batch approval before Red |
| Purpose | Make S02 `main_selection.sqx` step 2 ($\lvert\psi_{sel}\rangle=P_F\lvert\psi_0\rangle/\lVert P_F\lvert\psi_0\rangle\rVert$, $P_F=\sum_{x\in F}\lvert x\rangle\langle x\rvert$) a literal, term-by-term transcription of its own equation, matching what LISS-0421/0422 already did for step 1's `Sigma`. |
| Parent | Direct continuation of WP-0098 / LISS-0421/0422's design-review session — re-reading step 2 against the actual equation, symbol by symbol, with the Adjudicator |
| Investigation | Plan file: `/Users/nn0cl/.claude/plans/zany-juggling-hejlsberg.md` — the full term-by-term equation/program comparison that produced this design is recorded in the session transcript, not reproduced in the plan file |
| ADR | [0207](../architecture/adr/0207-literal-set-builder-projector-transcription.md) — **Accepted**, supersedes ADR 0192/0194 |
| Execution branch | `batch/s02-step2-literal-transcription` (once batch-approved) |
| Batch record | [execution-batch-s02-step2-literal-transcription.json](../collaboration/reviews/execution-batch-s02-step2-literal-transcription.json) — **draft, not yet `approved_for_execution`** |

## Confirmed final equation (step 2)

$$n\in\mathbb{N},\quad n=8$$
$$x\in\{0,1\}^n,\quad i,j\in\{0,\ldots,n-1\}$$
$$C\in\{0,1\}^{n\times n},\quad D\in\mathbb{R}^{n\times n},\quad \theta=0.3$$
$$\lvert\psi_0\rangle=\dfrac{1}{\sqrt{2^n}}\sum_{x\in\{0,1\}^n}\lvert x\rangle$$
$$F=\left\{x\in\{0,1\}^n \;\middle|\; \sum_{i=0}^{n-1}x_i=3,\ \ \forall\,i,j\in\{0,\ldots,n-1\},\,i<j:\ x_ix_j=1\Rightarrow C_{ij}=1,\ \ \min_{i<j:\,x_ix_j=1}D_{ij}\ge\theta\right\}$$
$$P_F=\sum_{x\in F}\lvert x\rangle\langle x\rvert$$
$$\lvert\psi_{sel}\rangle=\dfrac{P_F\lvert\psi_0\rangle}{\lVert P_F\lvert\psi_0\rangle\rVert}$$

## Confirmed final program (step 2)

```staqex
Int n = 8

State psi_0 = (1.0 / sqrt(2.0 ^ n)) * Sigma (x In {0,1}^n) { |x> }

Bool[8][8] C = host("pairwise_compatible")
Float[8][8] D = host("diversity")
Float theta = 0.3

Set F = {
    x In {0,1}^n :
        Sigma (i In 0..n-1) { x[i] } == 3,
        ForAll (i In 0..n-1, j In 0..n-1) where i < j {
            (x[i] * x[j] == 1) Implies (C[i][j] == 1)
        },
        Min (i In 0..n-1, j In 0..n-1) where i < j, x[i] * x[j] == 1 {
            D[i][j]
        } >= theta
}

Operator P_F = Sigma (x In F) { |x><x| }

State psi_sel = (project psi_0 onto P_F) / ||project psi_0 onto P_F||
```

## Issue rows

| Order | ID | Title | Depends | Status |
|---|---|---|---|---|
| 1 | [LISS-0423](../issues/LISS-0423-bare-range-binder-domains.md) | bare-range binder domains (`i In 0..n-1`), retire `Index<...>` (hard cutover; corpus impact turned out to be ~35 files, not just `objective_hamiltonian` — escalated per the batch record's own invalidating trigger, Adjudicator confirmed proceeding) | none | **complete** |
| 2 | [LISS-0424](../issues/LISS-0424-classical-numeric-sigma.md) | classical numeric `Sigma` (Int/Float array-element sum) | none | **complete** |
| 3 | [LISS-0425](../issues/LISS-0425-implies-operator.md) | `Implies` keyword operator | none | **complete** |
| 4 | [LISS-0426](../issues/LISS-0426-norm-and-state-division.md) | `\|\|State\|\|` norm notation + `State / Float` division | none | **complete** |
| 5 | [LISS-0427](../issues/LISS-0427-forall-binder.md) | `ForAll` binder, comma-separated guard | S1 | **complete** |
| 6 | [LISS-0428](../issues/LISS-0428-min-binder.md) | `Min` binder, comma-separated guard | S1 | **complete** |
| 7 | [LISS-0429](../issues/LISS-0429-set-comprehension.md) | `Set F = { x In D : cond1, cond2, ... }` comprehension | S1, S2, S5, S6 | **complete** |
| 8 | [LISS-0430](../issues/LISS-0430-sigma-over-set-projector.md) | `Sigma (x In F)` over general `Set` domain + bound-variable `\|x><x\|` (Pauli-Z decomposition) | S7 | **complete** |
| 9 | [LISS-0431](../issues/LISS-0431-project-explicit-renorm.md) | `project` drops implicit renormalization entirely; accepts general multi-term `Operator` | S8 | **complete** |
| 10 | LISS-TBD-S10 | retire `feasible(...)`; migrate to plain `host(...)`-bound arrays | S8 | pending |
| 11 | LISS-TBD-S11 | rewrite `main_selection.sqx` step 2 to the confirmed final form; byte-identical terminal output | S1-S10 | pending |

Execution order: **S1, S2, S3, S4 (any order) → S5, S6 (any order, after S1) → S7 → S8 → S9, S10 (any order, after S8) → S11.**

## What this WP does not include

Steps 1, 3, 4, 5 of `main_selection.sqx` (already literal per LISS-0421/0422,
or not yet reviewed with the same rigor) are out of scope — this WP is step 2
only. `Min`'s empty-guard-match behavior is not decided here; it is Red-phase
work for LISS-0428.

## Verification

Per-Issue Red→Green→Refactor, full regression sweep and
`tests/spec_verification/run_all.py` after each Issue; S1's `Index<...>`
retirement swept across the full `.sqx` corpus before being called complete;
S8's Pauli-Z decomposition cross-checked numerically at small `n` before
trusting it at `n=8`; S11's byte-identical terminal-distribution check
against the current `feasible(...)`-based baseline.
