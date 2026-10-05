# Evaluator runtime-plan eligibility and projection successor

## Status

Original extraction accepted/implemented; public-import repair reopened
2026-10-05; repair R01–R07 and Phase 0 accepted, Red accepted;
Phase 3 checks passed; final local review approved, final status-commit checks and CI/delivery pending. See the canonical
[repair supplement](evaluator-public-import-compatibility-repair.md).
Earlier phase/completion entries below are historical; extraction ownership
remains accepted, but current failed CI baseline is not waived.

## [DESIGN CHECK]

- **Scope and expected behavior:** identify a cohesive, stateless successor for
  runtime-plan eligibility, first-family checks, Operator-attribute inspection,
  and the small `CompilationUnit` projections used by canonical/legacy
  fallback routing. Preserve the selected `RuntimeExecutionPlan` family,
  compile-owned semantic authority, runtime results, diagnostics, ordering, and
  the existing fallback behavior.
- **Specifications and files inspected:** WP-0174, the core module
  decomposition specification, ADR 0211, ADR 0225, ADR 0227, the completed
  LISS-0493–0498 runtime-plan family slices, LISS-0544/LISS-0560 orchestration
  boundaries, `runtime/evaluator.py`, `runtime/evaluation/orchestration.py`,
  `runtime/evaluation/observation.py`, `runtime/evaluation/context.py`,
  `runtime/evaluation/execution.py`, the runtime-plan builder/model, and the
  existing runtime-plan characterization suites.
- **Component boundaries, ports/adapters, and VO/DTO candidates:** proposed
  pure module at `compiler/staqex/runtime/evaluation/plan_eligibility.py` receiving AST
  payloads and immutable runtime-plan data. No external port, adapter, new
  persistence shape, or new VO/DTO is indicated. `Evaluator` remains the sole
  mutable runtime-state owner and retains compatibility hooks as thin
  delegates if required.
- **Applicable constraints:** no language-semantic change, no new runtime-plan
  family, no change to Scientific Semantic IR authority, no implicit
  realization, no provider/QPU/Rust work, no public import retirement, and no
  widening of the legacy fallback boundary. Existing private consumers and
  hook identities must be inventoried before any body removal.
- **Decisions, assumptions, and unresolved ambiguities:** the accepted Phase 0
  successor candidate is `runtime/evaluation/plan_eligibility.py`. The likely family is
  runtime execution policy, not the canonical semantic projection builder.
  `scientific_semantic/legacy.py` may remain outside this slice because it
  projects source-derived meaning, while evaluator eligibility decides which
  already-built plan can use bounded runtime mechanics. The exact successor
  module name and whether `_main_deferred_eligible` joins this family require
  Phase 0 consumer/authority review. Empty or unsupported plan shapes must
  continue to fail closed or use the established legacy path.
- **Included and omitted AI context:** included only the listed runtime-plan
  contracts, direct consumers, private hook manifests, and relevant process
  lessons. Omitted unrelated compiler phases, provider integrations, full
  historical backlog, secrets, and private user data.
- **Task routing (model/assistant/tool):** strong reasoning analysis for the
  cross-module boundary; deterministic `rg`/AST/import checks for consumer
  inventory and later verification. Live routing is review `same_context`,
  implementation `host`; no model identifier is configured.
- **Input/output evidence contract when AI output is involved:** design output
  is reviewable Markdown only; no AI-generated runtime data is trusted as
  application input. Phase 1 must map each accepted clause to a named test;
  Phase 2/3 must report focused, consumer, adjacent, and all-blocking results
  against the final SHA.
- **Verification plan:** Phase 0 records the consumer and authority matrix.
  After Phase 0 acceptance, Phase 1 adds failing structural/behavior
  characterization tests only. Later phases require separate typed approval,
  compatibility identity checks, consumer smoke, adjacent regression, and the
  declared all-blocking suites.

## Candidate responsibility inventory

| Current responsibility | Current owner | Direct consumers | Phase 0 disposition |
|---|---|---|---|
| `_is_deferred_callable_eligible` | `Evaluator` | `orchestration.py`, callable-plan path, callable characterization | Candidate for pure policy successor; preserve private hook identity |
| `_operator_expr_contains_attr` | `Evaluator` | callable eligibility | Candidate helper; preserve recursive traversal semantics and order |
| `_is_minimal_local_evolution` | `Evaluator` | `orchestration.py`, evolution-plan path | Candidate policy helper; no evolution semantics change |
| `_is_first_runtime_family` | `Evaluator` | `orchestration.py`, first-family fallback | Candidate plan/unit eligibility helper; plan authority remains canonical |
| `_unit_without_operator_declarations` and unit shapers | `Evaluator` | evolution/binder orchestration | Candidate pure payload projection; retain source declarations where binder mechanics require them |
| `_main_deferred_eligible` | `evaluation/observation.py` | deferred execution, `Evaluator` compatibility hook, tests | Boundary decision required; likely related but currently coupled to deferred observation mechanics |
| `build_runtime_execution_plan` | `scientific_semantic/legacy.py` | `evaluation/orchestration.py`, public facade | Exclude unless authority review proves this is the same family; it remains source-derived semantic projection |

Static search is a discoverability lower bound. Private imports, runtime hook
installation, dynamic callers, and out-of-tree consumers require explicit
review evidence before body removal.

## Proposed acceptance scenarios

1. Given each currently characterized runtime-plan family, when eligibility is
   evaluated, then the same family selects the same dedicated executor or
   established legacy fallback.
2. Given a callable plan containing an Operator attribute, when eligibility is
   evaluated, then the existing conservative fallback decision is preserved.
3. Given a minimal local evolution plan, when its runtime unit is projected,
   then compile-time Operator declarations are handled exactly as today and
   no implicit realization is introduced.
4. Given a first-family plan, when its unit and node kinds are checked, then
   the existing State/Measure route remains eligible only for the same bounded
   statement shape.
5. Given an invalid family, missing payload, unresolved authority, or
   unsupported shape, when routing occurs, then the existing diagnostic or
   legacy fallback boundary is preserved without partial execution.
6. Given existing private evaluator hooks and compatibility imports, when the
   successor is installed, then import availability and callable identity stay
   compatible while implementation ownership moves to the successor.

## Phase boundary

Phase 0 authorized the boundary and Phase 1 Red test-only work. Phase 2 Green
implementation is now authorized after the accepted Red review. Phase 3
refactor, public API retirement, and completion remain separately gated.

## Applied process lessons

- **Evaluator state ownership:** keep every mutable runtime map and semantic
  authority observation in `Evaluator`; the successor is stateless.
- **Private-consumer inventory / decomposition callback boundary:** inspect
  private hooks, compatibility installers, `context.py`, and actual runtime
  callers before moving any body.
- **Compatibility-hook identity:** verify the installer and runtime callable
  identity, not only source-name presence.
- **Acceptance-inventory reconciliation:** map each proposed scenario to an
  exact test before Phase 1 review.
- **Status synchronization:** update this spec, the Issue, WP-0174, and the
  representative trace together at each approval transition.

## Phase 0 acceptance

The human Adjudicator accepted this Phase 0 boundary on 2026-09-29. The
acceptance authorizes preparation of the Phase 1 Red test-only contract. It does
not authorize production edits, active-Red registry changes, Phase 2 Green,
Phase 3 Refactor, or implementation.

Review record: [LISS-0582 Phase 0 acceptance](../collaboration/reviews/2026-09-29-liss-0582-phase0-acceptance.md).

## Phase 1 Red acceptance

The human Adjudicator accepted the reviewed Phase 1 Red contract on 2026-09-29.
The five structural Red tests and Active-Red registration are now the accepted
test boundary.

## Phase 2 Green result

The successor implementation is complete on the feature branch. The accepted
Red tests remain unchanged. Eligibility and projection policy now lives in
`runtime/evaluation/plan_eligibility.py`; orchestration calls the pure policy
functions directly, while the Evaluator retains only compatibility aliases.
The first-family observation boundary remains in `observation.py` and is
provided to the successor as an explicit callback, preserving its ownership.

Verification is recorded in [the Phase 2 Green review packet](../collaboration/reviews/2026-09-29-liss-0582-phase2-green-review.md).

## Historical final verification and completion

Phase 3 review passed for the bounded import-hygiene refactor. Final
verification was approved on 2026-09-29 and passed on final commit
`7620eb8c7b6843de4d821f4100c1d029e0a8b572`: all-blocking suite 2,285 passed,
lifecycle validation passed, and the tree was clean. Process review found no
operating-contract deviation. LISS-0582 is done; further residual candidates
require separate design intake.
