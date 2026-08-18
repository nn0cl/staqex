# LISS-0437 bounded explicit evolution — independent runtime/physics review

## Trigger

- User request: 「独立レビュー：物理意味・ランタイム。bounded explicit evolution design intake を読み、単一U_tとuntil反復の非同値性、停止時点、max、State線形性、数値/近似意味、既存runtime契約をレビューしてください。P0/P1/P2の指摘と具体的修正案を報告。読み取り専用。」
- Date: 2026-08-14
- Review scope: `docs/collaboration/traces/2026-08-14-liss-0437-bounded-explicit-evolution-design.md`
- Issue / ADR / Spec / WorkPlan: LISS-0437 / ADR 0209 / `docs/specs/staqex-explicit-evolution-surface.md` / WP-0100
- Branch: `codex/wp-0100-explicit-evolution-surface`
- Current phase: Phase 3 design intake; no Red or implementation approval for bounded explicit syntax
- Allowed paths: read-only inspection of the intake, acceptance spec, existing `until` contract, parser/typechecker/runtime/QPU lowering, and tests
- Explicitly excluded: source edits, compiler edits, test edits, phase approval, architecture approval

## Review lenses

- Source-to-domain fidelity: one `U_t` and repeated `U_t` are different denotations.
- State and physics safety: iteration must preserve one linear State carrier and must not collapse during predicate evaluation.
- Realization and fail-closed behavior: QPU lowering must not erase repetition or termination.
- Contract and acceptance completeness: stopping point, bound, failure, and numeric tolerance must be observable.
- Type, dimension, and validity closure: the explicit form must remain distinct from legacy Hamiltonian syntax.

## Independent reviewer

- Context mode: independent read-only review requested; app-side fresh-context dispatch was unavailable during this turn, so the findings below are limited to deterministic repository inspection and are not presented as delegated-agent approval.
- Reviewer task: inspect the requested design intake and current contracts; report prioritized findings and concrete corrections.
- Read-only: yes
- Implementation permission: no
- Approval authority: none

## Findings

### P0 — explicit `until` can become a silent single-step QPU realization

Evidence:

- The intake proposes `Evolve() { U_t * fuel } until converged(fuel) max 64`, while the current parser only attaches `until` to the legacy Hamiltonian block (`compiler/staqex/parser.py::_evolve_hamiltonian_block`).
- The explicit QPU branch in `compiler/staqex/backend/qasm/lower.py` handles `explicit_transform` before the legacy Hamiltonian branch and does not reject or consume `until_predicate`.
- The current QPU diagnostic in `compiler/staqex/qpu_ir.py` recognizes `until` on a State binding, but direct lowering and future AST combinations must not rely on that diagnostic as semantic enforcement.

Risk: once the syntax is added to the explicit AST, a target profile could emit gates for one `U_t` and silently drop both the repeated application and predicate-dependent stopping. That violates source-to-physics fidelity and is worse than a visible unsupported diagnostic.

Required correction:

1. Add an acceptance rule that an explicit transform carrying `until` is rejected before allocation unless a dedicated finite/static realization is accepted.
2. Make the QPU lowering guard run before any explicit evolution allocation and return zero gates on rejection.
3. Add a regression with a preceding `apply` or allocated state proving the rejected result contains no partial circuit.
4. Keep dynamic predicate termination rejected even when `max` is finite; finite `max` alone does not make predicate-dependent control statically equivalent.

### P1 — `converged(state)` has no physics-level convergence meaning yet

Evidence:

- `compiler/staqex/runtime/evaluator.py::_eval_until_predicate` currently treats `converged(state)` as `len(joint.amplitude_marginal(coord)) == 1`.
- That is a computational-basis support/cardinality test, not a numerical convergence test between successive States, and it is not generally invariant under basis choice.
- The intake states that the predicate is pure but does not specify a norm, tolerance, reference state, prior-step value, or whether convergence means fixed point, observable convergence, or basis support.

Risk: a unitary evolution can be physically valid while never satisfying this predicate, or can satisfy it for a basis-dependent reason unrelated to convergence. The fuel example's behavior therefore cannot be used as the general semantic contract.

Required correction:

1. Freeze the meaning of `converged` in the acceptance spec, or narrow the first slice to a named, explicitly documented predicate contract.
2. If numerical convergence is intended, define the metric, tolerance, comparison window, and numeric type; do not infer them from amplitude support.
3. If convergence is domain-specific, expose the domain predicate as a pure Host/Kernel contract with explicit State-read inputs and test it independently of evolution.
4. Add tests for a superposition, a basis change, and a non-converging unitary so the predicate is not accidentally a collapse operation.

### P1 — approximation and error accumulation across repeated steps are underspecified

Evidence:

- The intake correctly says repeated `U_t` is not one `U_t`, but it does not specify the approximation/error contract when a QPU target realizes each step approximately.
- The simulator path calls exact matrix/sparse exponential routines in `_hamiltonian_evolve_one_step`, while QPU lowering uses Suzuki gates and target-profile steps (`compiler/staqex/backend/qasm/lower.py`).
- A per-step Suzuki approximation repeated up to `max` times has accumulated error and resource cost; the current proposed text records a policy but not whether its error budget is per step, total, or worst-case over early stop.

Required correction:

1. State that simulator semantics are exact-to-numeric-tolerance per explicit `U_t` application, not a shortcut to `U_t^k`.
2. For any future static realization, require a total error/resource budget over at most `max` iterations, and record early-stop behavior.
3. Do not claim equivalence between exact simulator and approximate QPU output without a declared tolerance and accumulation rule.
4. Add provenance fields for iteration count, per-step realization, total bound, and whether the result stopped by predicate or by `max`.

### P1 — linear State ownership is asserted but not acceptance-tested for repeated tuple/entangled states

Evidence:

- The intake says the State must remain linear and uncollapsed, but its verification plan only names repeated execution and terminal measurement.
- Existing runtime iteration rebinds the same `names` through `bind_multi` and `_hamiltonian_evolve_one_step`; the existing test file covers single-name Pauli examples but not tuple ownership, entanglement, stale seed axes, or failed-max visibility.
- `converged` reads a marginal from `Joint`, so the contract must explicitly say this is a non-collapsing read-only view.

Required correction:

1. Add Red tests for a tuple/entangled State through at least two iterations, asserting one live carrier and no duplicated seed coordinates.
2. Add a test that predicate evaluation does not call measurement/RNG and preserves amplitudes/phases.
3. Define failure semantics: when `max` is exhausted, no partially evolved State is published to subsequent statements or terminal measurement.
4. Verify HIR linear-use and trace/discard analysis for the new explicit bounded AST shape before implementation.

### P2 — stopping-point and bound semantics need to be frozen before grammar work

Evidence:

- The intake says the predicate is evaluated after each transform, but does not explicitly define whether the initial State is tested before the first transform.
- `max` is described as `k <= max`, while the current runtime requires a positive literal and raises `EVOLVE_UNTIL_MAX_STEPS_ERROR` after exactly `max` unsuccessful transforms.
- The intake leaves `until` placement relative to `.run()` unresolved.

Required correction:

1. Specify post-step-only evaluation, or explicitly support an initial check; add a test for an already-satisfying initial State.
2. Specify whether `max = 0` is invalid or means zero transforms, and whether omission is invalid.
3. Freeze one grammar form before Red tests, including the exact `.run()` placement and whether `until` is inside the Evolve block.

## Readiness verdict

**NOT READY for acceptance-spec amendment, Red tests, or implementation.**

The intake has the correct high-level distinction between one explicit propagator application and bounded repetition, but P0 target fail-closed behavior and P1 predicate/approximation/linearity contracts remain unresolved. A reviewer cannot grant phase or implementation approval.

## Corrections applied

- No source, test, specification, ADR, or runtime files were changed. This was a read-only review. The review record is the only artifact added by the main context.

## Remaining blockers and next review condition

- Resolve the P0 QPU guard and explicit-AST shape in the acceptance specification before implementation.
- Define the physical meaning and numeric contract of `converged`.
- Add explicit bounded-loop scenarios covering stopping point, max exhaustion, tuple State linearity, and approximate error accumulation.
- Re-run a fresh independent read-only review after those documentation corrections. Typed Architecture/Phase/Implementation approval remains separate.

## Gate status

- Requested approval type: none; review only
- Approved scope: read-only review and review-record creation
- ADR status: no amendment accepted
- Specification status: bounded explicit design intake remains unapproved
- Phase approval: not granted by reviewer
- Implementation approval: not granted
- Post-review requirement: correction and fresh independent review before Red
