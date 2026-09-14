# LISS-0544 Phase 0 acceptance / Architecture review packet

## Review packet

- Scope: decompose the Evaluator orchestration family while preserving the
  public facade and one mutable runtime-state owner.
- Canonical documents: WP-0160, the core module decomposition spec, LISS-0544,
  the runtime execution model, and project conventions.
- Files re-read: `compiler/staqex/runtime/evaluator.py`, the evaluator-related
  test corpus, public import references, and the implementation-readiness
  checklist.
- Changed files: Phase 0 documentation only; no production or test
  implementation changed.

## Findings and dispositions

- `Evaluator` concentrates plan dispatch, deferred execution, measurement, and
  dynamic lanes in one class — **apply: five bounded extraction units**.
- The evaluator owns RNG, scalar/function/object/state maps and mutable runtime
  state — **already closed with evidence: retain ownership in the facade**.
- Extracted modules could silently copy mutable state or import the facade —
  **apply: narrow context protocol and import-direction checks**.
- Evolution, operators, classical calls, and value evaluation — **out of
  scope: LISS-0545**.
- Provider/QPU/AWS, Rust, syntax, semantic authority, and behavior changes —
  **out of scope**.

## Architecture decision

WP-0160 and its accepted decomposition spec are sufficient authority. No new
dependency, port, provider, or semantic authority is introduced. The public
`runtime.evaluator` module remains a compatibility facade; internal
`runtime/evaluation/` services receive explicit context and do not import the
facade.

## Verification

Deterministic audit identified `Evaluator` at approximately 6,669 lines,
`_bind_call()` at approximately 492 lines,
`_run_legacy_ast_body()` at approximately 416 lines, and
`_hamiltonian_evolve_one_step()` at approximately 327 lines. Public import
fan-out and the existing fixed-seed/QASM baseline requirements were confirmed
from the canonical spec. No implementation phase was executed.

Same-context review was used because runtime routing specifies
`same_context`; it is weaker than `separate_context` and does not replace
Adjudicator approval.

## Approval result

Approval received: `LISS-0544 Phase 0 acceptance 承認`, 2026-09-14.

## Next approval required

`LISS-0544 Phase 1 Red 承認`

## Evidence links

- Issue: `docs/issues/LISS-0544-evaluator-orchestration-decomposition.md`
- Work plan: `docs/work-plans/WP-0160-core-module-decomposition.md`
- Specification: `docs/specs/staqex-core-module-decomposition.md`
