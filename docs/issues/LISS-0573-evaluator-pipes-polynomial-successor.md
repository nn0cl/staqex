# LISS-0573: Evaluator pipes, block expressions, and polynomial fusion successor

## Metadata

- Local issue ID: LISS-0573
- Status: done
- Phase: complete
- Type: Architecture Path structural decomposition
- Planning size: L
- Parent: WP-0167
- Depends on: LISS-0571 / Unit A2 complete; LISS-0572 / Unit B complete
- Blocks: none

## [DESIGN CHECK]

### Scope and expected behavior

Extract the runtime evaluator's cohesive pipe/block/polynomial family into a
new `evaluation/pipes.py` without changing pipe semantics, hole-filling order,
Trace-Out behavior, fusion eligibility, polynomial coefficient order,
non-finite rejection, diagnostics, or fusion evidence exposed on the final
evaluation result. `Evaluator` remains the only mutable state owner.

### Specifications and files inspected

- `docs/architecture/agent-quickstart.md`
- `docs/architecture/implementation-readiness.md`
- `docs/collaboration/project-conventions.md`
- `docs/collaboration/runtime-routing.toml`
- `docs/collaboration/process-lessons-log.md`
- `docs/collaboration/source-code-quality.md`
- `docs/specs/staqex-core-module-decomposition.md`
- `docs/work-plans/WP-0167-evaluator-successor-decomposition.md`
- `compiler/staqex/runtime/evaluator.py`
- `compiler/staqex/runtime/evaluation/binding.py`
- `compiler/staqex/runtime/evaluation/context.py`
- `compiler/staqex/runtime/evaluation/values.py`
- `tests/test_pipeline_operator_fusion_red.py`
- `tests/test_poly2_fusion_red.py`
- `tests/test_algebraic_operator_fusion_red.py`
- `tests/test_bare_block_trace_out_red.py`

### Component boundaries, ports/adapters, and VO/DTO candidates

- Successor: `compiler/staqex/runtime/evaluation/pipes.py`.
- Runtime input: `Joint`, `Pipe`, `BlockExpr`, `FunDecl`, and expression AST
  nodes already owned by the runtime language.
- Context callbacks: `_bind`, `_evaluate_value`, function/object lookup,
  `_joint_coord_names`, `_trace_out_dead_fn_locals`, and a fusion-evidence
  setter. Exact callback signatures are resolved during Red preparation from
  actual consumers; no callback is invented for an unobserved dependency.
- State/DTO ownership: `Evaluator` retains mutable maps, `Joint` lifecycle,
  scalar evaluation, trace-out mutation, and `last_*_fusion` result fields.
- No external port, adapter, provider, QPU, serialization, or new value object
  is needed for this structural slice.

### Applicable constraints

- Architecture Path scope only; no Phase 1 Red or implementation yet.
- No parser, typechecker, Semantic IR, QASM, provider, network, credential,
  Rust, language syntax, or public API changes.
- Do not modify `typecheck.py` pipe lowering; it is a separate compiler-phase
  concern.
- Do not split polynomial helpers into a speculative generic algebra module.
- Preserve the single runtime authority and all existing private compatibility
  names until the final refactor phase.
- Target successor remains below the 500-line local structure budget and the
  repository 1,200-line guardrail.

### Current inventory

Measured from `compiler/staqex/runtime/evaluator.py` at intake:

| Family | Methods | Lines |
|---|---:|---:|
| Block binding | `_bind_block_expr` | 20 |
| Pipe fusion/stage execution | `_try_bind_fused_unary_pipe`, `_resolve_fuse_stage`, `_eval_fused_stage` | 132 |
| Affine/polynomial composition | 10 methods from `_compose_affine_pipe` through `_parse_affine` | 123 |
| Pipe structure/hole handling | `_flatten_pipe`, `_fuse_simple_return`, `_piped_call` | 27 |
| **Total** | **17** | **302** |

### Consumer and compatibility inventory

The actual runtime consumer is `evaluation/binding.py`, which calls the fused
pipe entrypoint, piped-call helper, and block-expression entrypoint through the
context. Direct private helper consumers are the pipeline fusion, polynomial,
affine, and block Trace-Out tests listed above. `execution.py` and result
assembly consume the fusion evidence but do not own its computation. Static
search must be supplemented by runtime import smoke and sequential-vs-fused
characterizations.

### Decisions and ambiguity boundaries

- Decision proposed: one `pipes.py` owns pipe mechanics and polynomial
  composition because the polynomial logic is only used to decide and execute
  safe unary pipe fusion.
- Decision proposed: use an explicit fusion-evidence callback rather than
  assigning `context.last_*` fields from the successor.
- Decision proposed: retain exact static helper compatibility during the
  migration; complete body removal is a later Phase 3 concern.
- Ambiguity to resolve during scope/Red preparation: whether live-coordinate
  trace-out helpers should be context callbacks or a small pure helper local to
  `pipes.py`, based on the actual consumer inventory. No implementation is
  authorized until this is resolved.

### Included and omitted AI context

- Included: Unit A/B successor boundaries, evaluator pipe/block/polynomial
  bodies, binding dispatch, context protocol, direct helper tests, runtime
  result assembly, project conventions, and applicable process lessons.
- Omitted: parser/typechecker implementation, provider/QPU code, historical
  documents, unrelated state algebra/evolution bodies, and private data not
  required for this boundary.

### Task routing

- Phase 0 design: host agent with deterministic AST, import, and call-site
  measurements.
- Phase 1–3: host agent after typed per-phase approvals.
- Review: `same_context` under the current live routing, explicitly weaker
  than `separate_context`.

### Verification plan

- Phase 0: method inventory, actual consumer manifest, state/evidence owner
  map, exact allowed paths, and callback ambiguity list.
- Phase 1 Red: structural failures plus positive block, unary/affine/poly
  fusion, non-finite rejection, and hole-filling characterizations.
- Phase 2 Green: minimum `pipes.py` extraction, compatibility wiring, import
  smoke, focused suites, adjacent regression, and full blocking suite.
- Phase 3: remove duplicate Evaluator bodies, preserve private helper surface,
  run structure checks, lifecycle/coverage/diff checks, and same-context review.

## Phase 0 acceptance boundary

This document is a design intake only. It requests:

`WP-0167 / Unit C pipe・block・polynomial Architecture Path scope approval`

No Phase 1 Red, implementation, or compatibility rewrite is authorized by
this document.

## Architecture Path scope approval

- Approval: `WP-0167 / Unit C pipe・block・polynomial Architecture Path scope
  approval` (2026-09-22).
- Scope is accepted for investigation and design refinement only. No Phase 1
  Red, production implementation, compatibility rewrite, or test lifecycle
  entry is authorized.
- The callback ambiguity was narrowed by the actual consumer inventory:
  `pipes.py` will use the existing `_joint_coord_names` and
  `_trace_out_dead_fn_locals` behavior through explicit context declarations;
  it will not duplicate trace-out policy. Fusion observations will use a new
  narrow `_set_fusion_evidence` callback, while the observable fields remain
  owned by Evaluator.
- The proposed successor remains one module (`pipes.py`) because stage
  eligibility, piped-call hole filling, and polynomial composition form one
  runtime fusion decision. `typecheck.py` remains excluded.
- Next approval:
  `WP-0167 / LISS-0573 Phase 0 acceptance 承認`.

## Phase 0 acceptance

- Approval: `WP-0167 / LISS-0573 Phase 0 acceptance 承認` (2026-09-22).
- Accepted scope: runtime-only extraction of the pipe/block/polynomial family
  into `evaluation/pipes.py`, with no parser, typechecker, Semantic IR, QASM,
  provider, QPU, syntax, or public API changes.
- Accepted state boundary: Evaluator owns mutable maps, `Joint` lifecycle,
  function/object environments, trace-out policy, and fusion evidence fields.
  The successor receives explicit callbacks and must not import or instantiate
  Evaluator.
- Accepted callback contract for Red preparation: existing live-coordinate and
  trace-out behavior is exposed through context declarations; fusion evidence
  is updated through one narrow setter callback. No duplicate policy or copied
  state is permitted.
- Accepted compatibility contract: private helper names remain available
  until Phase 3 body retirement; direct helper tests and runtime binding smoke
  remain blocking consumers.
- Accepted structure budget: `pipes.py` target below 500 lines and repository
  guardrail below 1,200 lines.
- Phase 1 Red may add only the bounded structural/characterization suite and
  its active-Red ledger entry.
- Next approval:
  `WP-0167 / LISS-0573 Phase 1 Red 承認`.

## Phase 1 Red

- Approval: `WP-0167 / LISS-0573 Phase 1 Red 承認` (2026-09-22).
- Added only `tests/test_liss_0573_pipes_successor_red.py` and the issue-owned
  active-Red manifest entry. No production module or compatibility wiring was
  added.
- Structural contract: five intended failures for successor existence,
  Evaluator body retirement, compatibility wiring, narrow context callbacks,
  and public-facade dependency.
- Passing characterizations: bare-block Trace-Out, affine fusion, polynomial
  fusion, non-finite polynomial rejection, multi-hole pipe filling, and affine
  parser behavior.
- Exact bounded run: **5 failed, 6 passed**. The five failures are the
  declared successor-file, facade-retirement, compatibility-wiring,
  context-callback, and no-facade-dependency gaps. The six passing nodes are
  the approved positive characterizations. The first run exposed a test
  fixture API mismatch; only the test import/assertion contract was corrected
  and the exact suite was rerun.
- Next approval:
  `WP-0167 / LISS-0573 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

- Approval: `WP-0167 / LISS-0573 Phase 1 Red テストレビュー承認`
  (2026-09-22).
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0573-phase1-red-review.md`.
- Same-context review reproduced **5 failed, 6 passed**. The five failures
  are the declared structural gaps; the six passing nodes are the approved
  behavior characterizations.
- The fixture API mismatch found before review was corrected in the test only
  and the exact bounded suite was rerun.
- Active-Red lifecycle, document lifecycle, coverage-ledger consistency, and
  `git diff --check` passed. No production implementation was added.
- Result: Phase 1 Red test review accepted. Next approval:
  `WP-0167 / LISS-0573 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0573 Phase 2 Green / Implementation 承認`
  (2026-09-22).
- Added `compiler/staqex/runtime/evaluation/pipes.py` with the pipe/block/
  polynomial successor implementation and installed its compatibility entry
  points through `evaluation/compatibility.py`.
- Evaluator remains the state/evidence owner. The retained original bodies
  were renamed to explicit `*_body` callbacks for the reversible Phase 2
  boundary; complete body removal is reserved for Phase 3.
- Added narrow context declarations for live-coordinate tracing,
  dead-coordinate trace-out, and fusion-evidence recording. No duplicate
  mutable state or public-facade dependency was introduced.
- Red contract: **11 passed**. Focused consumer/adjacent regression:
  **71 passed**. All-blocking suite: **2,216 passed in 318.41s**.
- Measurements: `evaluator.py` **2,596 lines**; `pipes.py` **346 lines**;
  `context.py` **244 lines**. The successor remains below the 500-line
  target and 1,200-line repository guardrail.
- Compile check, active-Red lifecycle, document lifecycle,
  coverage-ledger consistency, and `git diff --check` passed. The LISS-0573
  active-Red entry was retired after all eleven approved nodes passed.
- Tested SHA: `39e995f900574bf63db546a5cee4b89aa872cb39`; dirty worktree,
  macOS, repository virtualenv, Python 3.14. Commit-specific verification is
  pending because no commit was requested or created.
- Next approval:
  `WP-0167 / LISS-0573 Phase 3 Refactor 承認`.

## Phase 3 Refactor

- Approval: `WP-0167 / LISS-0573 Phase 3 Refactor 承認` (2026-09-22).
- Removed the retained pipe/block/polynomial implementation bodies from
  `evaluator.py`. `evaluation/pipes.py` is now the sole implementation owner;
  compatibility names are installed as thin directional bindings.
- Evaluator remains the owner of mutable maps, `Joint` lifecycle, trace-out
  policy, and fusion evidence. `pipes.py` uses explicit context callbacks and
  has no Evaluator import or construction dependency.
- Verification: focused consumer/adjacent **71 passed**; all-blocking
  **2,216 passed in 315.13s**. Active-Red lifecycle, document lifecycle,
  coverage-ledger consistency, `git diff --check`, and compile checks passed.
- Measurements after body retirement: `evaluator.py` **2,246 lines**;
  `pipes.py` **346 lines**; `context.py` **244 lines**. The successor remains
  below the accepted 500-line target and 1,200-line guardrail.
- Structural confirmation: no Unit C `*_body` definitions remain in
  `evaluator.py`.
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0573-phase3-review.md`.
- Tested SHA: `39e995f900574bf63db546a5cee4b89aa872cb39`; dirty worktree,
  macOS, repository virtualenv, Python 3.14. `review-change.py` reported the
  committed diff as zero and flagged the dirty worktree as unknown, so no
  commit-specific structural metric is claimed.
- Result: implementation review is ready; final human review remains.
- Next approval:
  `WP-0167 / LISS-0573 Phase 3 最終レビュー 承認`.

## Phase 3 Final Review

- Approval: `WP-0167 / LISS-0573 Phase 3 最終レビュー 承認` (2026-09-22).
- Re-read the accepted design, implementation files, private-consumer tests,
  Phase 3 review packet, and deterministic verification from disk.
- Findings: no blocker. Successor ownership, context callbacks, facade body
  retirement, private helper compatibility, and excluded boundaries match the
  accepted scope.
- Evidence: focused/adjacent **71 passed**; all-blocking **2,216 passed in
  315.13s**; compile, lifecycle, document, coverage-ledger, and diff checks
  passed.
- Review isolation: `same_context`, weaker than `separate_context`.
- Result: LISS-0573 is complete. Unit D and commit/PR operations remain out of
  scope for this approval.

Process review: no operating-contract deviation or operational problem found.
