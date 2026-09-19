# WP-0164: Evaluator classical/value and frame successor

| Field | Value |
|---|---|
| Status | done — Phase 3 final review accepted 2026-09-19 |
| Size | XL |
| Parent | WP-0163 / completed evaluator successor |
| Scope approval | accepted 2026-09-19 — Architecture Path Phase 0 |
| Implementation permission | approved for bounded Phase 2 Green and Phase 3 Refactor |
| Canonical specification | [Core module decomposition](../specs/staqex-core-module-decomposition.md) |
| Candidate issues | LISS-0567 |

## Goal

Continue the evaluator decomposition after WP-0163 without creating a second
runtime state owner or hiding cross-family dispatch in a generic helper. The
bounded successor separates classical value semantics from invocation-frame
mechanics while preserving the public `runtime.evaluator` facade.

## Current evidence

`compiler/staqex/runtime/evaluator.py` is **4,005 lines** with **112 class
methods**. The largest remaining bodies are:

| Method | Lines | Proposed responsibility |
|---|---:|---|
| `_run_legacy_ast_body` | 414 | retained cross-family dispatcher; excluded from first extraction |
| `_bind_method` | 171 | method receiver/frame execution |
| `_bind_user_fun` | 145 | measure-free user-function frame execution |
| `_bind` | 143 | retained cross-family bind dispatcher; excluded from first extraction |
| `_legacy_evaluate_value` | 134 | classical value compatibility entrypoint |
| `_eval_classical_user_fun_value` | 124 | classical function frame evaluation |
| `_bind_names` | 111 | retained binding dispatcher; excluded from first extraction |

Existing static consumer inventory and private compatibility evidence from
WP-0163 remain applicable. The current `evaluation/calls.py` already delegates
to `_bind_method`, `_bind_user_fun`, constructors, and classical evaluation;
this WP makes those callbacks cohesive without changing their authority.

## Proposed decomposition boundary

| Candidate module | Owns | Must not own |
|---|---|---|
| `runtime/evaluation/frames.py` | method/function invocation frames, receiver restoration, frame units, local-map lifetime, dead-coordinate trace-out | global state copies, AST-wide dispatch, semantic IR, QASM policy |
| `runtime/evaluation/classical.py` | classical call/method value evaluation, class/struct construction, attributes, unit-aware scalar evaluation | quantum `Joint` policy, terminal measurement, provider behavior |
| `runtime/evaluation/calls.py` | call classification and quantum binding entrypoints already extracted | implementation copies of frame/value bodies |
| `runtime/evaluator.py` | mutable maps, ports, cross-family `_bind_names`/`_bind`/AST dispatch, compatibility facade | duplicate family implementation bodies |

The exact split between `frames.py` and `classical.py` remains subject to the
Phase 0 call-graph inventory. A single `classical.py` larger than the 1,200-line
guardrail is not an acceptable shortcut.

## Invariants

- `Evaluator` remains the only mutable runtime-state owner.
- `_this`, `_frame_units`, local classical maps, and trace-out cleanup are
  restored on every success and failure path.
- Existing private aliases remain available until a separate consumer decision.
- Public imports, diagnostics, source spans, ordering, local fixed-seed output,
  QASM output, and semantic authority remain unchanged.
- No provider SDK, network, credential, filesystem, or Rust boundary is added.
- `_run_legacy_ast_body`, `_bind`, and `_bind_names` are not moved wholesale.

## Phase gates

1. Phase 0: call graph, state ownership map, consumer manifest, exact allowed
   paths, and design acceptance.
2. Phase 1 Red: structural contracts and characterization tests only.
3. Phase 2 Green: minimum frame/classical extraction for the approved slice.
4. Phase 3 Refactor: import cleanup, compatibility audit, and reviewer packet.
5. Final review: full verification, process review, and status synchronization.

## Verification plan

- function, method, class/struct, partial-value, attribute, and unit fixtures;
- nested frame/shadowing and receiver restoration characterization;
- private consumer/import smoke and no-facade dependency checks;
- focused and adjacent runtime regressions;
- fixed-seed local execution and diagnostic ordering;
- `tests/spec_verification/run_all.py`;
- full blocking pytest, compileall, lifecycle, coverage-ledger, and diff checks.

## Explicit exclusions

- parser/typechecker changes;
- new language semantics or syntax;
- scientific/continuous-family implementation;
- moving the cross-family AST dispatcher;
- public API retirement;
- provider/QPU/network work;
- opportunistic bug fixes discovered during characterization.

## Current decision

Architecture Path Phase 0, Phase 1 Red, Phase 2 Green / Implementation, and
Phase 3 Refactor have been approved and executed for LISS-0567. Final review
remains pending; no further implementation is authorized before that review.

## Phase 0 evidence

### Call-graph and mutation inventory

- Frame entrypoints: `_bind_method`, `_bind_user_fun`, and
  `_eval_classical_user_fun_value` each create local parameter maps and use
  `_frame_units`; `_exec_assign` mutates receiver/object fields and unit maps.
- Classical entrypoints: `_eval_classical_call`,
  `_eval_classical_method_call`, `_construct_instance`, `_construct_struct`,
  `_eval_value_with_unit`, `_legacy_evaluate_value`, and
  `_resolve_receiver_instance`.
- Retained dispatchers: `_run_legacy_ast_body`, `_bind`, and `_bind_names`
  call across quantum, classical, observation, and scientific families and are
  not eligible for wholesale movement in this successor.
- Mutable state remains in `Evaluator`: `objects`, `classes`, `structs`,
  `funs`, `scalars`, `scalar_units`, `operators`, `_this`, `_frame_units`,
  `_call_local_units`, and injected ports. `Joint` is passed through and is not
  copied into an extracted service.

### Consumer and dependency inventory

- Runtime consumers include `evaluation/calls.py`, `evolution.py`,
  `operators.py`, `values.py`, `dynamic_lane.py`, and `observation.py`.
- Direct test consumers include method/function frame, struct-return,
  classical rational/unit, continuous binding, and existing Unit D contract
  suites. Private evaluator aliases remain compatibility surfaces.
- `evaluation/calls.py` and other extracted modules do not import the public
  `runtime.evaluator` facade. The new modules must preserve this direction.
- No provider, filesystem, network, credential, or external port is added.

### Exact Phase 1 allowed paths

- `compiler/staqex/runtime/evaluator.py`
- `compiler/staqex/runtime/evaluation/frames.py` (new)
- `compiler/staqex/runtime/evaluation/classical.py` (new)
- `compiler/staqex/runtime/evaluation/context.py`
- `compiler/staqex/runtime/evaluation/compatibility.py`
- `tests/test_liss_0567_classical_frame_red.py` (new)
- `docs/issues/LISS-0567-evaluator-classical-frame-successor.md`
- `docs/work-plans/WP-0164-evaluator-classical-frame-successor.md`
- the linked design trace and review packet only

No parser, typechecker, semantic IR, QASM, provider, or historical WP-0162
file is in the Phase 1 allowed set.

### Phase 1 Red contract proposal

1. `frames.py` and `classical.py` expose explicit entrypoints without
   importing `runtime.evaluator`.
2. The reviewed context declares frame, receiver, environment, constructor,
   unit, and value callbacks required by the extracted functions.
3. The facade retains one compatibility mapping per private consumer hook.
4. Receiver/frame state is restored on both success and error paths.
5. Existing method/function/struct/partial/unit characterization tests remain
   the behavior contract; no new language behavior is introduced.

## Phase 0 acceptance request

The call graph, mutation ownership, consumer inventory, candidate module
boundary, and Phase 1 allowed paths are ready for review. Next approval:
`WP-0164 / LISS-0567 Architecture Path Phase 0 acceptance 承認`.

## Phase 0 acceptance

Accepted on 2026-09-19:
`WP-0164 / LISS-0567 Architecture Path Phase 0 acceptance 承認`.

The call graph, mutable-state ownership, consumer inventory, candidate module
boundary, exact allowed paths, and proposed Red contracts are accepted. This
acceptance authorizes Phase 1 Red test work only; it does not authorize
production extraction, compatibility retirement, or public API changes.

Next approval:
`WP-0164 / LISS-0567 Phase 1 Red 承認`.

## Phase 1 Red

Approved on 2026-09-19:
`WP-0164 / LISS-0567 Phase 1 Red 承認`.

Added `tests/test_liss_0567_classical_frame_red.py` with eight bounded
structural and characterization contracts. Five structural gaps are expected
before extraction; three existing function/method/struct-return cases remain
characterization evidence. Active-Red ownership is registered for LISS-0567.

Expected pre-Green result: **5 failed, 3 passed**. No production source or
reviewed assertion was changed.

Next approval:
`WP-0164 / LISS-0567 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

Accepted on 2026-09-19:
`WP-0164 / LISS-0567 Phase 1 Red テストレビュー承認`.

The same-context review packet is
`docs/collaboration/reviews/2026-09-19-liss-0567-phase1-red-review.md`.
All eight bounded contracts were reviewed. The focused run produced the
expected **5 failed, 3 passed** result: five structural gaps are intentionally
Red before extraction, while the function-frame, method-receiver, and
struct-return characterizations pass. Lifecycle, document, coverage-ledger,
and diff checks passed. No production implementation was started.

Next approval:
`WP-0164 / LISS-0567 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

Approved and implemented on 2026-09-19:
`WP-0164 / LISS-0567 Phase 2 Green / Implementation 承認`.

The approved successor boundaries are now wired through explicit
`frames.py` and `classical.py` entrypoints. Legacy evaluator bodies remain
behind `_legacy_*` compatibility callbacks, while `Evaluator` remains the sole
mutable state owner. Frame restoration callbacks and classical construction /
value callbacks are declared in `EvaluatorContext`; no provider, parser,
Semantic IR, QASM, or public API work was added.

Verification:

- LISS-0567 Red suite, adjacent evaluator characterization, and operator
  regression: **15 passed**.
- Full blocking pytest: **2,163 passed**.
- Runtime compileall, test lifecycle, document lifecycle,
  coverage-ledger consistency, and `git diff --check`: passed.

The Active-Red entry was retired after all eight contracts passed. The next
step is readability-only Phase 3 Refactor and compatibility audit; no new
behavior is included in this Green slice.

Next approval:
`WP-0164 / LISS-0567 Phase 3 Refactor 承認`.

## Phase 3 Refactor

Approved and completed on 2026-09-19:
`WP-0164 / LISS-0567 Phase 3 Refactor 承認`.

Refactor-only cleanup made the successor boundary explicit without changing
runtime behavior:

- frame callback signatures now name `logs` and `inspect_out` explicitly;
- `EvaluatorContext` documents the legacy callback contract and frame
  restoration contract;
- compatibility installer imports and descriptions are grouped by family;
- evaluator legacy bodies are documented as compatibility implementations;
- the successor modules remain free of evaluator-owned mutable maps and public
  facade imports.

No assertion, fixture, language semantic, provider, or public API change was
made in this phase. Full pytest and the focused/lifecycle checks pass.

Next approval:
`WP-0164 / LISS-0567 Phase 3 最終レビュー 承認`.

## Phase 3 final review

Accepted on 2026-09-19:
`WP-0164 / LISS-0567 Phase 3 最終レビュー 承認`.

Review packet:
`docs/collaboration/reviews/2026-09-19-liss-0567-phase3-final-review.md`.
The bounded implementation and refactor were re-read and verified with 15
focused/adjacent passes, **2,163 full pytest passes**, compileall, lifecycle,
coverage-ledger, and diff checks. The remaining `evaluator.py` size is
explicitly recorded as future decomposition scope; it is not concealed by the
successor modules.

Process review: no operating-contract deviation or operational problem found.

WP-0164 and LISS-0567 are complete. Future evaluator body migration or
private compatibility retirement requires a new approved scope.
