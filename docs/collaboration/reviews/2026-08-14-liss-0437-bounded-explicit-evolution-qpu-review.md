# LISS-0437 bounded explicit evolution — QPU/target-boundary review

## Trigger and scope

- Trigger: user requested an independent read-only review of the bounded
  explicit evolution design intake.
- Date: 2026-08-14
- Scope: QPU/target boundary, compatibility, QPU IR, static/dynamic
  termination, resource estimation, fail-closed behavior, legacy shorthand
  retirement, and the `main_fuel_search.sqx` migration plan.
- Issue / ADR / Spec / WorkPlan: LISS-0437 / ADR 0209 /
  `docs/specs/staqex-explicit-evolution-surface.md` / WP-0100
- Branch: `codex/wp-0100-explicit-evolution-surface`
- Current phase: Phase 3 design intake for bounded explicit evolution; no Red,
  implementation, architecture, or target-technology approval for this slice.
- Review mode: read-only. No source, test, specification, or implementation
  correction was applied.

## Independent-context evidence

- A fresh read-only reviewer dispatch was requested with the bounded-design
  scope and a prohibition on edits, implementation, and approval. The
  app-side response was not available during this review turn, so the findings
  below are deterministic repository findings and are not presented as a
  delegated-agent approval or as phase approval.
- The findings were checked against the current repository artifacts listed
  below; they must receive a fresh independent-context re-review before the
  design is treated as ready.

## Inspected artifacts

- `docs/collaboration/traces/2026-08-14-liss-0437-bounded-explicit-evolution-design.md`
- `docs/specs/staqex-explicit-evolution-surface.md`
- `docs/architecture/adr/0209-explicit-blackboard-evolution-surface.md`
- `docs/work-plans/WP-0100-explicit-evolution-surface.md`
- `compiler/staqex/qpu_ir.py`
- `compiler/staqex/backend/qasm/lower.py`
- `compiler/staqex/pipeline.py`
- `compiler/staqex/parser.py`
- `examples/showcase/S01_quantum_disaster_response/main_fuel_search.sqx`

## Review lenses

- Realization and fail-closed behavior: target lowering must never erase
  repetition or predicate-dependent termination.
- Source-to-domain fidelity: `U_t` repeated `k` times is not one `U_t`, and a
  predicate-selected `k` is not a statically known loop count.
- Contract completeness: QPU IR, resource estimates, approximation/error
  policy, and termination outcome must be observable.
- Migration/compatibility safety: legacy shorthand retirement must have one
  explicit compatibility policy and a verifiable removal gate.
- Phase and approval discipline: this intake must freeze target semantics
  before Red tests or implementation.

## Findings

### P0 — the target-profile escape hatch can authorize semantic loss

Evidence:

- The intake says QPU lowering may reject dynamic convergence unless a target
  profile supplies a “finite static realization”
  (`docs/collaboration/traces/2026-08-14-liss-0437-bounded-explicit-evolution-design.md:13-18`).
- The same intake says the predicate-dependent stopping realization is
  deferred and fail-closed, but it does not define what a finite realization
  is or how it preserves the runtime-selected iteration count
  (`...bounded-explicit-evolution-design.md:23-29`).
- The current QPU IR rejects dynamic `until` unconditionally and has no
  bounded-explicit iteration or termination projection
  (`compiler/staqex/qpu_ir.py:468-488`, `545-602`).
- Current QASM lowering has a profile-based explicit-evolution path that
  synthesizes a single target-owned Suzuki application, while the bounded
  syntax is not yet represented there (`compiler/staqex/backend/qasm/lower.py:360-398`).

Risk: a future implementation could interpret finite `max` as sufficient and
emit one or a fixed number of `U_t` applications, silently dropping the
predicate or changing the number of transformations. That would violate the
blackboard denotation and the fail-closed rule.

Required correction:

1. Remove “target profile supplies a finite static realization” as an
   unqualified escape hatch. Define a separate accepted target contract that
   proves either predicate-independent fixed iteration or an equivalent
   target control-flow realization.
2. State explicitly that finite `max` alone never authorizes static QPU
   lowering of predicate-dependent termination.
3. Require the QPU IR to preserve termination kind, written `max`, predicate
   provenance, and the relation between each iteration and `U_t`.
4. Add a negative acceptance case with a preceding `apply` proving that any
   unsupported bounded realization returns zero executable gates.

### P1 — resource and approximation accounting is incomplete for repeated steps

Evidence:

- The intake requests QPU rejection without a finite profile but does not
  specify a resource formula or an error-accumulation rule for up to `max`
  repetitions (`...bounded-explicit-evolution-design.md:38-42`).
- The provider-neutral explicit projection records `realization`,
  `approximation_policy`, and a capability decision, but no iteration bound,
  per-step cost, total worst-case cost, or error budget
  (`compiler/staqex/qpu_ir.py:592-600`).
- The current profile lowering note estimates gates for one synthesized
  explicit application (`compiler/staqex/backend/qasm/lower.py:376-381`),
  which is insufficient for a predicate-controlled loop.

Required correction:

- Freeze whether the resource estimate is worst-case over `max`, exact for a
  fixed count, or unavailable for dynamic termination.
- Record per-step realization, maximum iteration count, worst-case gate/depth/
  qubit estimates, and total approximation/error budget. Do not claim simulator
  and QPU equivalence without a declared accumulation policy.

### P1 — static versus dynamic termination is named but not a closed contract

Evidence:

- The intake calls for a “pure convergence predicate” and a positive
  compile-time bound, but does not define a target-visible classification of
  predicates or how purity is established at the QPU boundary
  (`...bounded-explicit-evolution-design.md:13-21`).
- Existing QPU diagnostics treat dynamic `until` as unsupported, without a
  distinct diagnostic for “finite bound but predicate-dependent termination”
  (`compiler/staqex/qpu_ir.py:473-480`).

Required correction:

- Define three cases: fixed-count static repetition, finite-but-dynamic
  termination, and unbounded/dynamic termination. Only the first is in the
  current static QPU lane.
- Keep the second rejected even when `max` is present, unless a future target
  control-flow contract is explicitly accepted.
- Specify that predicate purity is a simulator/source contract and is not by
  itself evidence that a QPU can execute the predicate.

### P1 — legacy shorthand retirement is inconsistent with the intake’s wording

Evidence:

- The design intake says the existing legacy source is “currently rejected by
  the migration diagnostic” (`...bounded-explicit-evolution-design.md:27-30`).
- The normative Spec says the diagnostic is migration-only and that a future
  strict profile must promote it to a hard rejection
  (`docs/specs/staqex-explicit-evolution-surface.md:136-143`).
- `CompileResult.ok` only treats the migration diagnostic as hard when
  `strict_evolution=True` (`compiler/staqex/pipeline.py:221-229`), so the
  default compatibility path is not equivalent to retirement.

Required correction:

- Replace “currently rejected” with the exact default/strict behavior.
- Define the retirement gate: which corpus must be migrated, which command or
  profile enables strict mode, and the evidence required before the default
  changes.
- State that legacy shorthand cannot be accepted as an alias for bounded
  explicit syntax and cannot be used to infer a target realization.

### P2 — fuel migration is sequenced after design, but its target outcome is
not explicit enough

Evidence:

- `main_fuel_search.sqx` still uses the legacy Hamiltonian `until` form
  (`examples/showcase/S01_quantum_disaster_response/main_fuel_search.sqx:8-13`).
- The intake says to add tests and then migrate the example, but does not state
  whether the migrated example must remain simulator-only, whether its QPU
  lane must fail with a named diagnostic, or what exact terminal behavior is
  preserved (`...bounded-explicit-evolution-design.md:38-42`).

Required correction:

- Make the fuel example’s acceptance packet explicit: simulator regression,
  post-step predicate semantics, `max` exhaustion behavior, terminal measure,
  and a QPU negative test with no circuit allocation.
- Keep migration separate from acceptance-spec/grammar approval; do not change
  the example until the bounded syntax and target rejection contract are
  accepted.

## Readiness verdict

**NOT READY** for acceptance-spec amendment, Red tests, or implementation.

The high-level boundary is correct, but the P0 target-profile escape hatch can
permit a semantics-losing realization unless it is closed. The P1 findings
also leave resource/error accounting, static/dynamic termination, and legacy
retirement behavior insufficiently specified.

## Corrections applied

- None. This review was read-only; this document records the findings only.

## Remaining blockers and next review condition

- Freeze the P0 target realization rule and explicitly prohibit fixed-count
  substitution for predicate-dependent termination.
- Add the QPU IR termination/resource/error fields or explicitly defer the
  entire bounded QPU lane with a hard rejection contract.
- Correct the legacy compatibility wording and define the strict retirement
  gate.
- Expand the fuel migration acceptance packet.
- Re-run a fresh independent read-only review after those documentation
  corrections. Reviewer readiness is not phase, architecture, technology, or
  implementation approval.

## Gate status

- Requested approval type: none; review only
- Approved scope: read-only inspection and review recording
- Reviewer approval authority: none
- Phase approval: not granted
- Implementation approval: not granted
- Post-review: required after documentation correction
