# Independent Context Review — LISS-0444 Scientific Semantic Core

## Trigger

- User request: 「続けて」 after architecture approval; continue with the required independent design review.
- Date: 2026-08-19
- Review scope: Architecture Path design for a source-derived Scientific Semantic IR and authority migration.
- Issue / ADR / Spec / WorkPlan: LISS-0444 / ADR 0211 / `staqex-scientific-semantic-core` / WP-0107
- Branch: `codex/liss-0438-residual-reconciliation`
- Current phase: design review before Phase 1 Red
- Allowed paths: the four design artifacts, review records/traces, and the reusable perspectives ledger
- Explicitly excluded: source implementation, tests/Red, Phase 1 approval, provider SDK, live QPU, S02 numeric migration

## Review lenses

- Applicable lenses: physicist-first source fidelity; semantic boundary and State safety; explicit realization/fail-closed; canonical authority and implementation reality; contract completeness; migration/regression safety.
- Why these lenses apply: this design changes language meaning ownership and must prevent a second “beautiful equation → broken DSL → QPU port” split while replacing several existing semantic paths.
- Prior review records consulted: `docs/collaboration/independent-review-perspectives.md` and the LISS-0444 design-intake trace.

## Independent reviewer

- Context mode: fresh independent contexts; three read-only reviewers with separate implementation-reality, physicist-fidelity, and migration-verification prompts
- Reviewer task: inspect current repository implementation and LISS-0444 design artifacts; return evidence-backed findings, readiness, and reusable perspectives
- Read-only: yes
- Implementation permission: no
- Approval authority: none

## Iteration log

### Iteration 1

- State entered: `REVIEW`
- Artifacts inspected: LISS-0444, ADR 0211, Spec, WP-0107, `compiler/staqex/pipeline.py`, `parser.py`, `typecheck.py`, `hir.py`, `physics_ir.py`, `physics_equation.py`, `physics_ir_lower.py`, `symbolic_ir.py`, `quantum_semantic_ir.py`, `algorithm_plan_ir.py`, `algorithm_planner.py`, `runtime/evaluator.py`, QASM lowering/emitter, H1 authoring, ADR 0210, language vision, perspectives ledger.
- Findings, prioritized:
  - P0: no implemented Scientific Semantic IR exists yet and current evaluator/QASM/algorithm paths bypass the proposed authority. This is a phase-readiness fact, not a request to implement now.
  - P0/P1: the migrate/replace/retire matrix is required but not yet enumerated per representation, owner, exit condition, compatibility window, and retirement proof.
  - P1: the source → AST/HIR → Scientific IR → simulator → Realize → finite-plan chain lacks a closed node/invariant and projection-preservation contract.
  - P1: simulator semantics versus finite `Realize` semantics are not explicit enough; ADR 0210 must remain the finite-boundary authority.
  - P1: Equation DTOs are caller-injected/stringly typed; H1 authoring and AST-pattern backend/evaluator paths are additional authority candidates requiring disposition.
  - P1/P2: soft diagnostics and incomplete DTOs may appear successful; canonical semantic errors need explicit no-consumer-artifact behavior.
  - P1/P2: provenance, type, dimensions, exactness, role, intent, state safety, and terminal-measure invariants need deterministic acceptance cases.
  - P1: migration needs corpus, unchanged-neighbor regression, rollback/deprecation, and deletion/unreachability conditions.
  - P2: semantic roles must be explicitly internal IR/type distinctions, not user-facing `Classical`/`Quantum` namespace or class containers.
  - P2: `physics_ir.py` documentation contradicts current soft pipeline wiring and must be treated as evidence of inventory drift.
- Finding dispositions:
  - All findings: `accepted` as design-document corrections within the already approved LISS-0444 architecture scope.
  - Disposition authority: `primary-agent under delegated policy`; no finding changes the accepted architecture, technology, Issue, or requested phase.
  - Rationale and evidence: the reviewers independently identified the same authority and migration gaps in current source paths; the corrections make those gaps reviewable without preserving the existing paths by default.
  - Design-deviation check: `no` for documentation corrections; implementation absence remains a deliberate Phase 1 boundary.
- Lens mapping: P0/P1 authority and implementation reality; P1 source fidelity/projection conservation; P1/P2 explicit realization and fail-closed; P1 migration/regression; P2 surface-role clarity.
- Readiness verdict: `NOT READY` for Phase 1 and for terminal review completion until the design contracts and migration matrix are documented and independently re-reviewed.
- Corrections applied: accepted documentation corrections were applied after
  the review: ADR 0211 now defines internal role classifications, simulator
  versus `Realize`, source-node identity, and authority closure; the Spec now
  contains the structural/projection contract, negative corpus, and competing
  path matrix; WP-0107 now makes those artifacts and rollback/corpus evidence
  Phase 0 deliverables; lens 11 records projection conservation and authority
  reachability.
- Files changed: ADR 0211, the Scientific Semantic Core Spec, WP-0107, and
  `docs/collaboration/independent-review-perspectives.md`.
- Remaining blockers: fresh independent review is required; implementation,
  Red, and Phase 1 approval remain outside this loop.
- Reviewer perspectives to retain: parser reachability is not semantic capability; DTO/fixture/importability/soft diagnostics are not authority; projection conservation; authority reachability; explicit Realize; state safety.
- New recurring perspective to add: projection conservation and authority reachability (added to the ledger in the correction batch).
- Next review condition: after the ADR/Spec/WP and ledger corrections are applied, run a fresh independent review against current artifacts.

### Iteration 2

- State entered: `RE_REVIEW`
- Artifacts inspected: current ADR 0211, Scientific Semantic Core Spec,
  WP-0107, LISS-0444, perspectives ledger, and the same implementation paths
  listed in Iteration 1.
- Findings, prioritized:
  - P0: the migration matrix remains an unpopulated requirement; it lacks
    actual dispositions, owners, order, compatibility/rollback, retirement,
    and deletion proof.
  - P0: no checked-in LISS-0444 source corpus or semantic snapshot contract
    exists yet.
  - P1: projection preservation and fail-closed artifact rules are not mapped
    per consumer, and the current soft paths remain live by design.
  - P1: exact/symbolic simulator output and its non-finiteization contract are
    still ambiguous.
  - P1: static terminal measurement versus the existing dynamic-lane
    mid-circuit measurement model is not classified in the canonical IR.
  - P1: role transitions, consumer-wide no-hidden-Limit enforcement, and
    positive terminal-measure coverage need explicit acceptance cases.
  - P2: compatibility APIs such as `lower_physics_ir` need a named
    disposition.
- Finding dispositions:
  - Matrix, corpus, projection, fail-closed, compatibility, and acceptance
    coverage findings: `accepted` as documentation/Phase 0 corrections.
  - Simulator result contract and static-versus-dynamic measurement boundary:
    `deferred` pending user/Architecture decision because existing ADRs do not
    determine a unique contract.
  - Disposition authority: primary agent under delegated policy for accepted
    in-scope corrections; user/Adjudicator required for deferred findings.
  - Design-deviation check: `yes — escalated` for the two deferred boundaries.
- Readiness verdict: `NOT READY` for terminal review completion and Phase 1.
- Corrections applied: none in Iteration 2; the unresolved semantic choices
  determine the acceptance contract, so further correction would risk inventing
  architecture.
- Files changed: none by reviewers.
- Remaining blockers: pending fresh review; Phase 1 and implementation gates
  remain separate.
- Reviewer perspective to retain: projection conservation and authority
  reachability are now required lenses.
- Next review condition: record decisions for the simulator contract and
  measurement boundary, apply accepted documentation fixes, then run a fresh
  independent review.

## Terminal decision

- Terminal state: `ABORT`
- Completion basis or abort reason: the loop exits at the required decision
  boundary; the current design cannot determine the simulator result contract
  or static terminal-measure versus dynamic-lane classification safely.
- User/Adjudicator decision required: yes — decide those two semantic
  boundaries before further correction or Phase 1 review.
- Evidence path: this record and the three independent reviewer outputs received in the task trace.

## Gate status

- Requested approval type: independent design review, not implementation or phase approval
- Approved scope: architecture/design of LISS-0444 and WP-0107
- Approval authority / approver: user, 2026-08-19
- ADR status: architecture-approved; review correction required
- Specification status: architecture-approved; review correction required
- Phase approval: not granted
- Implementation approval: not granted
- Post-review requirement: fresh independent review after accepted corrections

## Evidence

- Deterministic checks before correction: `git diff --check` passed; repository inspection confirmed parallel source and DTO paths described above.
- Related trace: `docs/collaboration/traces/2026-08-19-liss-0444-design-intake.md`
- User/Adjudicator decision still required: simulator result/non-finiteization
  contract and static terminal-measure versus dynamic-lane classification.
