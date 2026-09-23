# LISS-0572: Evaluator frames, constructors, and assignments successor

## Metadata

- Local issue ID: LISS-0572
- Status: done
- Phase: complete
- Type: Architecture Path structural decomposition
- Planning size: XL
- Parent: WP-0167
- Depends on: LISS-0571 / Unit A2 complete
- Blocks: none

## [DESIGN CHECK]

### Scope and expected behavior

Extract the evaluator's invocation-frame, object-constructor, and field-
assignment implementation families into cohesive modules without changing
language behavior, diagnostics, mutation order, receiver/frame restoration,
private consumer compatibility, DTO identity, or the single mutable
`Evaluator` state owner.

### Specifications and files inspected

- Canonical specification: `docs/specs/staqex-core-module-decomposition.md`.
- Parent plan: `docs/work-plans/WP-0167-evaluator-successor-decomposition.md`.
- `compiler/staqex/runtime/evaluator.py`: six target bodies and their helper
  calls.
- Existing boundaries: `runtime/evaluation/frames.py`,
  `runtime/evaluation/classical.py`, `runtime/evaluation/calls.py`,
  `runtime/evaluation/execution.py`, `runtime/evaluation/context.py`, and
  `runtime/evaluation/compatibility.py`.
- Direct and structural consumers: LISS-0567, LISS-0566-C/D,
  LISS-0413, class/struct/value tests, execution tests, call-binding tests,
  evolution tests, and operator assignment tests.

### Current inventory

| Family | Current body | Size | Proposed owner |
|---|---|---:|---|
| Class method frame binding | `_legacy_bind_method` | 173 lines | `evaluation/frames.py` |
| Free-function frame binding | `_legacy_bind_user_fun` | 145 lines | `evaluation/frames.py` |
| Class construction and init | `_legacy_construct_instance`, `_run_init` | 106 lines | new `evaluation/constructors.py` |
| Struct construction | `_legacy_construct_struct` | 65 lines | new `evaluation/constructors.py` |
| Field assignment | `_exec_assign` | 36 lines | new `evaluation/assignments.py` |

The current evaluator is **3,117 lines** after Unit A2. These six bodies total
**525 lines** before helper extraction decisions. `frames.py` currently acts
as a compatibility wrapper and must not become a second implementation copy.

### Component boundaries and state ownership

- `frames.py` owns method and free-function invocation-frame control flow,
  including local argument binding, receiver setup, frame-unit capture, return
  handling, and restoration.
- `constructors.py` owns class/struct construction and class `init` execution.
- `assignments.py` owns object-field assignment and its mutation/diagnostic
  ordering.
- `Evaluator` remains the only owner of mutable maps, receiver/frame state,
  DTO classes (`ClassInstance`, `StructValue`, `PartialValue`), `Joint`
  lifecycle, scalar/unit stores, and injected ports.
- Successors receive `EvaluatorContext` callbacks and must not import or
  instantiate `runtime.evaluator`.
- No new dependency, provider, network, filesystem, QASM, Semantic IR, parser,
  typechecker, or public API change is included.

### Consumer and compatibility inventory

Actual consumers identified:

- `evaluation/calls.py` calls `_bind_method`, `_bind_user_fun`,
  `_construct_instance`, and `_construct_struct`.
- `evaluation/execution.py` constructs class/struct values and calls
  `_exec_assign` during main execution.
- `evaluation/classical.py` resolves constructor calls and currently retains
  the legacy constructor bridge.
- `evaluation/evolution.py` binds function results through `_bind_user_fun`.
- `evaluation/operators.py` calls `_execute_assignment`.
- Direct tests exercise private constructor, frame, and assignment names;
  structural tests also inspect compatibility installation and facade method
  retirement.

Static search also finds comments, historical issue text, parser/typechecker
symbols, and test helper names. These are not runtime consumers unless import
or execution evidence confirms them.

### Proposed compatibility contract

- Add `install_constructor_compatibility` and
  `install_assignment_compatibility` without changing public imports.
- Extend `install_frame_compatibility` so `_bind_method` and `_bind_user_fun`
  resolve to `frames.py` implementation functions, not legacy Evaluator bodies.
- Keep compatibility aliases only at the facade boundary; do not retain a
  second implementation body in `Evaluator` after Phase 3.
- Preserve keyword arguments `logs` and `inspect_out`, receiver identity,
  `_this`/`_frame_units` restoration, local unit propagation, and exact error
  text/order.

### Phase plan and acceptance

- Phase 0: this inventory, callback ownership map, exact allowed paths, and
  design decisions.
- Phase 1 Red: structural gaps for successor modules, compatibility wiring,
  context callbacks, body retirement, and no-facade dependency; positive
  characterizations for method, free-function, class/struct, init, and field
  assignment behavior.
- Phase 2 Green: minimum extraction with actual consumer import/runtime smoke
  and nearest frame/constructor/assignment regressions.
- Phase 3 Refactor: remove legacy bodies, simplify callback contracts, verify
  structure budget, compileall, import cycles, lifecycle, and full blocking.
- Final review: same-context under current routing; separate-context is not
  configured.

### Allowed and excluded paths

Allowed: `evaluator.py`, existing `evaluation/frames.py`, new
`evaluation/constructors.py`, new `evaluation/assignments.py`,
`evaluation/context.py`, `evaluation/compatibility.py`, a new LISS-0572 Red
test, active-Red ledger, and linked WP/Issue/Trace/review records.

Excluded: `parser.py`, `typecheck.py`, Semantic IR, QASM, providers, network,
credentials, Rust, syntax changes, public API retirement, Units C/D, and
unrelated changes to `classical.py`, `calls.py`, or `evolution.py` beyond
compatibility imports required by the accepted extraction.

### Decisions and ambiguity boundaries

- Decision: use the existing `frames.py` as the frame successor; do not create
  a second frame module.
- Decision: create separate `constructors.py` and `assignments.py`; these
  responsibilities must not be combined into a generic utility module.
- Decision: `_run_init` belongs to `constructors.py` because it is part of
  class construction and receiver/frame initialization.
- Decision: `_execute_assignment` remains a thin compatibility name while the
  mutation body moves to `assignments.py`.
- Ambiguity to resolve during Red: exact callback names for class/struct DTO
  construction and assignment target mutation, based on the full body-level
  consumer inventory. No implementation is authorized by this intake.

### Next approval

`WP-0167 / LISS-0572 Phase 1 Red 承認`

## Phase 0 acceptance

- Approval: `WP-0167 / Unit B frames・constructors・assignments Architecture Path scope approval`
  (2026-09-22).
- Scope is accepted for design and bounded Red preparation only. Phase 1 Red,
  implementation, and later refactor require separate typed approvals.

## Phase 1 Red

- Approval: `WP-0167 / LISS-0572 Phase 1 Red 承認` (2026-09-22).
- Added `tests/test_liss_0572_frames_constructors_assignments_red.py` and its
  issue-owned active-Red entry.
- Contract: six structural failures for constructor/assignment successor
  existence, facade body retirement, frame bridge retirement, compatibility
  wiring, and narrow context callbacks; four passing characterizations for
  free-function frames, method receivers, class init/assignment, and struct
  construction.
- No production module or compatibility implementation was added.
- Next approval:
  `WP-0167 / LISS-0572 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

- Approval: `WP-0167 / LISS-0572 Phase 1 Red テストレビュー承認`
  (2026-09-22).
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0572-phase1-red-review.md`.
- Result: accepted. The focused suite reproduced **6 failed, 4 passed**;
  the six failures are the declared structural gaps and the four passing
  tests are approved frame/constructor/assignment characterizations.
- Active-Red lifecycle, document lifecycle, coverage-ledger consistency, and
  `git diff --check` passed. No production implementation was added.
- Review isolation was `same_context`, weaker than `separate_context`.
  LISS-0572 remains issue-owned in active Red until Green implementation.
- Next approval:
  `WP-0167 / LISS-0572 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

- Approval: `WP-0167 / LISS-0572 Phase 2 Green / Implementation 承認`
  (2026-09-22).
- Added `evaluation/constructors.py` and `evaluation/assignments.py`, and
  converted `evaluation/frames.py` from legacy-name wrappers to explicit
  successor entrypoints.
- Added constructor and assignment compatibility installers. The existing
  Evaluator implementation bodies are now explicitly named context callbacks
  (`_bind_method_body`, `_bind_user_function_body`,
  `_construct_instance_body`, `_run_init_body`, `_construct_struct_body`, and
  `_execute_assignment_body`) so the public private-hook names resolve through
  successor modules without changing state ownership.
- Evaluator remains the sole owner of mutable maps, receiver/frame state,
  DTO identity, `Joint` lifecycle, and scalar/unit stores. Complete body
  retirement is reserved for Phase 3; no duplicate public dispatcher names or
  legacy-named frame bridge remains.
- Red contract: **10 passed**. Focused consumer and adjacent regression:
  **61 passed**. All-blocking suite: **2,205 passed in 314.28s**.
- Compileall, active-Red lifecycle, document lifecycle, coverage-ledger
  consistency, and `git diff --check` passed.
- Measurements: `evaluator.py` **3,121 lines**, `frames.py` **58 lines**,
  `constructors.py` **24 lines**, `assignments.py` **16 lines**, and
  `context.py` **219 lines**.
- Tested SHA: `39e995f900574bf63db546a5cee4b89aa872cb39`; dirty worktree,
  macOS, repository virtualenv, Python 3.14. Commit-specific verification is
  pending because no commit was requested or created.
- Next approval:
  `WP-0167 / LISS-0572 Phase 3 Refactor 承認`.

## Phase 3 Refactor

- Approval: `WP-0167 / LISS-0572 Phase 3 Refactor 承認` (2026-09-22).
- Moved the frame, constructor/init, and assignment bodies completely into
  `evaluation/frames.py`, `evaluation/constructors.py`, and
  `evaluation/assignments.py`. Evaluator no longer retains the extracted
  implementation bodies; compatibility names are thin successor bindings.
- Added only the context callbacks required by the moved bodies. Evaluator
  remains the owner of mutable environments, receiver/frame state, DTO
  identity, `Joint` lifecycle, and scalar/unit stores.
- Restored the successor `restore_frame` entrypoint and wired operator
  resolution through the explicit context callback for private consumers.
- Verification: focused consumer and adjacent regression **61 passed**;
  all-blocking suite **2,205 passed in 317.73s**. Active-Red lifecycle,
  document lifecycle, coverage-ledger consistency, and `git diff --check`
  passed.
- Measurements: `evaluator.py` **2,586 lines**; `frames.py` **364**;
  `constructors.py` **188**; `assignments.py` **52**; `context.py` **234**.
- Tested SHA: `39e995f900574bf63db546a5cee4b89aa872cb39`; dirty worktree,
  macOS, repository virtualenv, Python 3.14. No commit-specific result is
  claimed because no commit was requested or created.
- Review packet:
  `docs/collaboration/reviews/2026-09-22-liss-0572-phase3-review.md`.
- Result: implementation review is ready; final human review remains.
- Next approval:
  `WP-0167 / LISS-0572 Phase 3 最終レビュー 承認`.

## Phase 3 Final Review

- Approval: `WP-0167 / LISS-0572 Phase 3 最終レビュー 承認` (2026-09-22).
- Re-read the accepted design, implementation files, actual private-consumer
  tests, and the Phase 3 review packet from disk.
- Findings: no blocker. Successor ownership, explicit context callbacks,
  facade retirement, diagnostics, and private consumer compatibility are
  consistent with the accepted scope.
- Deterministic evidence: focused/adjacent **61 passed** and all-blocking
  **2,205 passed in 317.73s** on the recorded SHA/environment. Lifecycle,
  document, coverage-ledger, and diff checks passed.
- Review isolation: `same_context`, weaker than `separate_context`.
- Result: LISS-0572 is complete. Unit C/D and commit/PR operations remain
  outside this approval.

Process review: no operating-contract deviation or operational problem found.
