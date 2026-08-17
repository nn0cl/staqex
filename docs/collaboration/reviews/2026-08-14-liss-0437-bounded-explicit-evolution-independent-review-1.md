# LISS-0437 bounded explicit evolution — independent review 1

## Trigger

- User request: 「独立レビューを実施」
- Date: 2026-08-14
- Scope: bounded explicit evolution design intake (`until`付き明示的発展)
- Issue / ADR / Spec / WorkPlan: LISS-0437 / ADR 0209 / `docs/specs/staqex-explicit-evolution-surface.md` / WP-0100
- Branch: `codex/wp-0100-explicit-evolution-surface`
- Current phase: Phase 3 design intake
- Review mode: five fresh independent read-only contexts
- Explicitly excluded: source implementation, Red test creation, Spec/ADR acceptance, phase approval

## Review lenses

Applied lenses from `docs/collaboration/independent-review-perspectives.md`:

1. Contract and acceptance completeness
2. Architecture and boundary integrity
3. Source-to-domain fidelity
4. Type, dimension, and validity closure
5. State and physics safety
6. Realization and fail-closed behavior
7. Migration and regression safety
8. Phase and approval discipline
9. Evidence and context hygiene

The review specifically tested whether bounded repetition can be added without
collapsing the distinction between one explicit propagator application and a
repeated, predicate-controlled evolution.

## Independent reviewers

All reviewers were instructed to inspect the design intake and related
contracts read-only, report P0/P1/P2 findings, and make no implementation or
approval decision.

| Context | Focus | Result |
|---|---|---|
| Fresh context A | Grammar, AST mode separation, predicate contract, existing `times`/`for`/`until` boundaries | NOT READY |
| Fresh context B | Physical meaning, runtime iteration, State linearity, numerical/approximation semantics | NOT READY |
| Fresh context C | QPU lowering, static/dynamic realization, resource and fail-closed behavior, compatibility | NOT READY |
| Fresh context D | Independent cross-check of QPU, convergence, numerical error, State linearity, and stopping semantics | NOT READY |
| Fresh context E | QPU target boundary, IR resource accounting, legacy compatibility diagnostics, migration regression | NOT READY |

## Findings

### P0 — acceptance grammar and syntax position are not frozen

The candidate form

```staqex
Evolve() { U_t * fuel } until converged(fuel) max 64
```

does not establish whether `until` belongs inside the block, after the block,
or before/after `.run()`. The relation to `times N`, `for dt`, and the legacy
Hamiltonian `under ... for ... until ...` branch is also open.

Required correction:

- Add one exact grammar/EBNF form to the Spec and ADR.
- Freeze `.run()` placement, semicolon/newline boundaries, whether `max` is
  mandatory, and whether `until` is valid only for explicit transform mode.
- Add accepted and rejected examples for `times`, `for`, legacy Hamiltonian,
  and explicit bounded iteration.

Evidence: `docs/collaboration/traces/2026-08-14-liss-0437-bounded-explicit-evolution-design.md`;
`docs/specs/staqex-explicit-evolution-surface.md`; `compiler/staqex/parser.py`.

### P0 — no reviewed acceptance specification authorizes this syntax

The current explicit-evolution Spec accepts one explicit transform followed by
`.run()`. It does not accept bounded explicit repetition. Under `AGENTS.md`'s
Prime Directive, Red tests and implementation cannot start from an intake
example alone.

Required correction: amend the Spec and ADR (or create a companion ADR), then
run another independent review before Red creation.

Evidence: `AGENTS.md` Prime Directive; `docs/specs/staqex-explicit-evolution-surface.md`;
`docs/architecture/adr/0209-explicit-blackboard-evolution-surface.md`.

### P1 — predicate meaning and allowed State observations are incomplete

`converged(state)` is described as pure, but the contract does not define the
comparison metric, tolerance, reference/previous State, basis dependence, or
whether amplitude, norm, marginal, observable, `Inspect`, or user-defined
predicates are allowed. Existing runtime behavior is narrower than the design
language suggests.

Required correction:

- Freeze the first-slice predicate set and its return type (`Bool`).
- Define permitted State observations and explicitly prohibit measurement, RNG,
  collapse, mutation, and external effects.
- Define the physical meaning of `converged` or rename it to a narrower
  predicate with a documented contract.

Evidence: `compiler/staqex/runtime/evaluator.py` predicate handling;
`compiler/staqex/typecheck.py` until contract; existing evolve-until tests.

### P1 — repeated-transform semantics are not fully specified

It is not yet frozen whether the transform expression is evaluated once and
reapplied, how the next State is rebound, whether one linear carrier is
preserved, and whether the initial State is checked before the first
transform. The required semantic distinction is:

```text
one step:       U_t * state
bounded repeat: (U_t)^k applied stepwise, with predicate checked per step
```

Required correction: specify post-step-only predicate evaluation, State
rebinding/ownership, `max=0`, successful step range, and no publication of a
partially evolved State after failure.

### P1 — QPU realization can silently erase repetition

An explicit-transform lowering path could allocate and emit one `U_t` while
dropping `until` and early termination. Finite `max` does not make a
predicate-dependent stopping condition statically equivalent to a fixed circuit.

Required correction:

- Guard before allocation and fail closed for dynamic predicate termination.
- Define whether any target may statically unroll exactly `max` steps, and what
  semantic result that represents.
- Require zero partial target artifacts on rejection.
- Define approximation error/resource budgets over all possible iterations and
  provenance for actual stop reason and iteration count.

Evidence: `compiler/staqex/backend/qasm/lower.py`; `compiler/staqex/qpu_ir.py`;
bounded runtime review record.

The additional QPU review also found that the current legacy-evolution
diagnostic is hard-failing only under `strict_evolution=True`; the default
compatibility path must not be described as an unconditional rejection. The
Spec must distinguish migration diagnostics from fail-closed target lowering.

### P1 — State linearity and non-collapse are not acceptance-tested

Tuple/entangled States, duplicate carrier prevention, phase preservation, and
non-collapsing predicate reads are not covered by the current bounded design
intake.

Required correction: add acceptance scenarios for tuple/entangled State over
multiple iterations, predicate reads that preserve amplitudes/phases, HIR
linear-use, and failed-bound behavior.

### P2 — `max` syntax and exhaustion result are incomplete

The accepted form for `max` (literal only versus compile-time constant), zero,
negative values, upper bounds, overflow, diagnostic identity, and simulator/QPU
failure result are not frozen.

Required correction: define the complete value/type/diagnostic contract before
Red tests.

## Cross-review synthesis

The reviewers agree on the central architectural point: a blackboard-explicit
propagator must remain visible as the source meaning, while bounded repetition
is a separate semantic construct. The disagreement in severity (P0 versus P1
for grammar) does not change the gate: every reviewer marked the design
**NOT READY**.

The recurring meta-perspective to retain is:

> Before extending a physicist-facing equation surface, freeze the exact source
> grammar, the denotation of one step versus repeated steps, the State/predicate
> observation contract, and the target rejection boundary. Do not let a target
> lowering path define or erase the physics.

## Verdict and gate status

- Readiness verdict: **NOT READY**
- Red test creation: not authorized by this review
- Implementation: not authorized
- ADR status: bounded explicit iteration amendment not accepted
- Specification status: design intake only; acceptance contract incomplete
- Phase approval: not granted by reviewers
- Required next step: amend Spec/ADR with the exact grammar and semantic/QPU
  contracts, then trigger a fresh independent review
- User/Adjudicator decision still required: acceptance of the amended bounded
  explicit evolution scope and subsequent Red phase approval

## Review evidence

- Design intake: `docs/collaboration/traces/2026-08-14-liss-0437-bounded-explicit-evolution-design.md`
- Runtime/physics review: `docs/collaboration/reviews/2026-08-14-liss-0437-bounded-explicit-evolution-runtime-review.md`
- Reusable perspective ledger: `docs/collaboration/independent-review-perspectives.md`
- No source, test, Spec, or ADR files were changed by the independent reviewers.

## Iteration 2 — delegated disposition and fresh re-review

- Review state: `REVIEW` → `DISPOSITION` → `ABORT`
- Fresh reviewer: Aquinas (`019fffb7-c80b-7961-be7d-379158e12c90`)
- Review mode: read-only independent context
- Files changed by reviewer: none
- Deterministic check reported: `git diff --check` passed

### Finding dispositions

| Finding IDs | Disposition | Authority | Rationale |
|---|---|---|---|
| BE-03, BE-04, BE-09, BE-10, BE-12 | `accepted` as correction requirements | Primary agent under delegated review policy | These preserve the current blackboard-first boundary and can be specified without choosing a new user-facing design. They remain unapplied until the user-facing contract is authorized. |
| BE-01, BE-02, BE-05, BE-06, BE-07, BE-08, BE-11 | `deferred` | Primary agent under delegated review policy | Each changes or completes the accepted language contract: grammar position, predicate meaning, max/result semantics, mode boundaries, or realization policy. They cannot be inferred without choosing among materially different designs. |

No finding was rejected. The deferred findings are review blockers, not
accepted implementation work.

### Terminal decision

- Terminal state: **`ABORT`**
- Reason: the bounded explicit-evolution contract requires user/Adjudicator
  decisions before Spec/ADR amendment.
- User decision required:
  1. exact `until`/`.run()` grammar;
  2. physical meaning and observation contract of `converged`;
  3. `max` syntax and exhaustion/State result;
  4. simulator, fixed-unroll, dynamic-stop, and QPU rejection boundary;
  5. whether `until` is explicit-only or also applies to `times`/`for`.
- Next condition: after those decisions, amend Spec/ADR/WP, then trigger a
  fresh independent re-review. Do not create Red tests or implement before
  that re-review returns `READY` and the typed phase approval is recorded.

## Iteration 3 — post-correction verification

- Review state: `CORRECT` → `RE_REVIEW` → `DISPOSITION` → `COMPLETE`
- Fresh reviewer: Mill (`019fffd8-af22-7752-90cc-0921fe367150`)
- Review mode: read-only independent context
- Files changed by reviewer: none
- Verdict: **READY**

### Verification result

- P0 findings: none
- P1 findings: none
- QPU boundary: consistent — bounded predicate-dependent iteration is
  simulator-only and QPU lowering fails closed before allocation.
- WP historical implementation notes: explicitly marked as baseline history.
- Approval status: consistent — bounded design amendment is accepted for
  Spec/WP design; Red, implementation, and phase transition remain separate
  approvals.

### Remaining P2 follow-up

The reviewer identified documentation-strengthening work before Red creation:

- add formal EBNF or equivalent grammar notation;
- state concrete norm/tolerance/numeric-type and provenance details;
- define the minimum convergence-contract assertions for Red.

These are accepted as design-preserving P2 follow-ups and do not reopen the
architecture decision. They must be completed before requesting Red phase
approval, but they do not change the terminal review result.

### Terminal decision

- Terminal state: **`COMPLETE`**
- Completion basis: all P0/P1 blockers were corrected and independently
  verified; no user decision remains for the accepted bounded design.
- Phase approval: not granted by this review.
- Implementation approval: not granted.
- Next safe action: complete the P2 documentation follow-up, then request the
  separately typed Red phase approval.

## Iteration 4 — final contract verification

- Review state: `CORRECT` → `RE_REVIEW` → `DISPOSITION` → `COMPLETE`
- Fresh reviewer: Poincare (`019fffe3-109c-7b21-91bb-fd9f442ce319`)
- Review mode: read-only independent context
- Files changed by reviewer: none
- Verdict: **READY**
- P0/P1 findings: none

The reviewer confirmed consistent mode-specific approval boundaries, grammar
position, `times`/`for` separation, Float64 full-State L2 tolerance `1e-9`,
provenance fields, simulator-only execution, QPU fail-closed behavior, and
the absence of Red/implementation/phase approval.

Remaining P2 notes are non-blocking: the EBNF refers to the existing language
grammar for primitive nonterminals, and the design trace's next-review wording
was updated after this final review.

### Final terminal decision

- Terminal state: **`COMPLETE`**
- Review result: ready for a typed Red phase approval request
- Red phase approval: not yet granted
- Implementation approval: not granted
- Next safe action: request Red phase approval; do not begin tests until it is
  explicitly approved.

## Iteration 5 — acceptance-matrix review

- Review state: `REVIEW` → `DISPOSITION` → `COMPLETE`
- Fresh reviewer: Ptolemy (`019fffe8-5b7e-76e1-bb01-5e9ba7fa4a0b`)
- Review mode: read-only independent context
- Files changed by reviewer: none
- Verdict: **READY**
- P0/P1 findings: none

### Finding dispositions

All findings R-01 through R-07 were `accepted` by the primary agent under the
delegated review policy. They confirm blackboard/source fidelity, State
linearity and non-collapse, atomic max exhaustion, QPU fail-closed behavior,
`times`/`for` isolation, approval boundaries, and coverage of the acceptance
matrix. No user decision or design deviation is required.

The only remaining optional follow-up is to specify how much failure
provenance is externally visible when `max` is exhausted. It is non-blocking
and does not prevent the Red approval request.

### Terminal decision

- Terminal state: **`COMPLETE`**
- Review result: ready for a typed bounded Red phase approval request
- Red phase approval: not granted
- Implementation approval: not granted
- Next safe action: request Red phase approval; do not create tests before
  explicit approval.

## Iteration 6 — failure-provenance closure

- Review state: `CORRECT` → `RE_REVIEW` → `DISPOSITION` → `COMPLETE`
- Fresh reviewer: Heisenberg (`019ffff4-44a1-7900-a9b5-69a3448bf547`)
- Review mode: read-only independent context
- Files changed by reviewer: none
- Verdict: **READY**
- P0/P1 findings: none

The nine required `max_exhausted` provenance fields now match across Spec,
ADR, and WP: `source_transform`, `predicate`, `metric`, `numeric_type`,
`tolerance`, `iteration_count`, `max_steps`, `stop_reason`, and
`realization`. The same documents consistently prohibit publishing,
rebinding, measuring, or resuming any State, State amplitudes, intermediate
State, or resumable handle. QPU fail-closed and approval boundaries remain
consistent.

The terminology difference between “resumable intermediate value” and
“resumable handle” is P2 only and does not block readiness.

### Final terminal decision

- Terminal state: **`COMPLETE`**
- Review result: ready for a typed bounded Red phase approval request
- Red phase approval: not granted
- Implementation approval: not granted
- Next safe action: request explicit bounded Red phase approval.
