# WP-0165: Evaluator value and continuous body successor

| Field | Value |
|---|---|
| Status | done — Phase 3 final review accepted 2026-09-19 |
| Size | XL |
| Parent | WP-0164 / completed LISS-0567 successor |
| Scope approval | accepted 2026-09-19 — Architecture Path scope |
| Implementation permission | none |
| Canonical specification | [Core module decomposition](../specs/staqex-core-module-decomposition.md) |
| Candidate issues | LISS-0568 |

## [DESIGN CHECK]

### Scope and expected behavior

Move the remaining classical value-evaluation and continuous/finiteization
implementation bodies behind the already accepted `classical.py` successor
and a new `continuous.py` successor. Preserve source meaning, fixed-seed
results, diagnostics, units, provenance, Joint behavior, public imports, and
the single `Evaluator` mutable-state owner. This is structural extraction only;
it adds no syntax or language semantics.

### Current evidence

- `compiler/staqex/runtime/evaluator.py`: **4,026 lines / 114 class methods**.
- `_legacy_evaluate_value` is the remaining broad classical expression body;
  it covers literals, variables, attributes, `when`, constructors, calls,
  binders, units, and recursive value evaluation.
- `_eval_value_with_unit`, `_eval_unit_convert`, attribute/receiver helpers,
  and `_exec_assign` form the unit-aware classical frame support.
- `_bind_finiteize`, `_bind_finiteize_continuous`,
  `_bind_field_from_host`, and `_bind_continuous_compose` form the continuous
  host/finiteization family; they own provenance assembly but not the host
  implementation.
- `_bind_inner` and `_materialize_outer` are state-algebra operations and are
  excluded from this successor.

### Proposed component boundaries

| Candidate module | Owns | Must not own |
|---|---|---|
| `runtime/evaluation/classical.py` | value dispatch, unit-aware value evaluation, unit conversion, attribute/receiver reads, classical assignment support | mutable evaluator maps, Joint policy, continuous host calls, provider/QPU behavior |
| `runtime/evaluation/continuous.py` | `finiteize`, continuous `finiteize`, `field_from_host`, `weight`, `mask`, provenance assembly, port calls | continuous pointwise evaluation, provider SDKs, semantic authority, copied state |
| `runtime/evaluator.py` | mutable state, DTO definitions, cross-family `_bind`/`_run_unit_body`, compatibility facade | duplicate extracted bodies |
| `runtime/evaluation/context.py` | narrow callbacks for maps, DTO predicates, units, value recursion, ports, and provenance storage | a second runtime state object |

### State ownership and ports

- `Evaluator` remains the only owner of `objects`, `scalars`, units,
  receiver/frame state, `Joint`, seed, and injected ports.
- `ContinuousFieldPort` remains an external port; the successor calls it only
  through the existing context callback/owner.
- The extracted modules must not import `runtime.evaluator` or construct an
  `Evaluator`.
- Runtime DTO identity (`ClassInstance`, `StructValue`, `EnumValue`) remains
  evaluator-owned unless Phase 0 dependency evidence justifies a separate
  pure DTO move. Such a move is outside this scope by default.

### Applicable constraints

- No implementation before reviewed Red contracts and explicit Phase 2
  approval.
- No parser, typechecker, Semantic IR, QASM, provider, network, credential,
  Rust, or public API retirement changes.
- No change to continuous-host semantics, finiteization approximation,
  provenance shape, seed handling, diagnostic text/order, or unit policy.
- New `continuous.py` and the expanded `classical.py` should each remain below
  the 1,200-line guardrail.
- Existing private aliases remain available until a separate consumer decision.

### Decisions, assumptions, and unresolved ambiguities

- Decision: complete the body migration into the existing `classical.py`
  boundary rather than create another generic value utility module.
- Decision: isolate continuous/finiteization mechanics in `continuous.py`
  because the port/provenance boundary is distinct from classical value
  recursion.
- Assumption: `_bind_inner` and `_materialize_outer` remain in the facade until
  a separate state-algebra scope is accepted.
- Ambiguity: exact DTO predicates and callback names must be fixed by the
  Phase 0 call-graph/mutation inventory; no facade import workaround is
  permitted.
- Ambiguity: `_apply_op`, `_pat_match`, and dimension helpers may remain pure
  evaluator helpers or move only if dependency evidence proves the move is
  mechanical and within the allowed paths.

### Included and omitted AI context

- Included: WP-0164/LISS-0567 final artifacts, core decomposition spec,
  `evaluator.py` value/continuous methods, `calls.py`, `values.py`,
  `context.py`, `compatibility.py`, existing continuous/classical fixtures,
  and private-consumer inventory.
- Omitted: provider credentials, live QPU/network, parser/typechecker
  internals, Semantic IR implementation, historical WP-0162 records, and
  unrelated scientific profiles.

### Task routing

- Phase 0 design and dependency inventory: host agent with deterministic
  source/import/AST/search tools.
- Phase 1–3 implementation: host agent only after typed phase approval.
- Review: `same_context` under current runtime routing.

### Input/output evidence contract

No external AI or provider output is part of this task. Design evidence is
repository Markdown containing measured method/line counts, state ownership,
consumer paths, allowed files, ambiguity boundaries, and deterministic test
commands/results.

### Verification plan

- Phase 0: call graph, mutation ownership, consumer/import manifest, DTO
  predicate inventory, port/provenance map, exact allowed paths.
- Phase 1 Red: structural module/callback/no-facade/state-owner contracts and
  existing classical/unit/continuous characterization tests.
- Phase 2 Green: minimum body migration with focused classical and continuous
  suites, fixed-seed finiteization/provenance checks, and nearest evaluator
  regressions.
- Phase 3: import cleanup, compatibility audit, full pytest, compileall,
  Spec Verification, lifecycle, coverage-ledger, and diff checks.

## Phase 0 gate

This design intake records the approved Architecture Path scope only. It does
not authorize Phase 1 Red tests, production extraction, or public API changes.
Next approval:
`WP-0165 / LISS-0568 Architecture Path Phase 0 acceptance 承認`.

## Phase 0 evidence

### Call graph and mutation inventory

- `evaluation/values.py` delegates value evaluation to the evaluator legacy
  entrypoint and is a compatibility consumer that must be updated or wired
  explicitly during Green.
- `evaluation/calls.py` routes `finiteize`, `field_from_host`, `weight`, and
  `mask` through the existing context callbacks; its call classification is
  retained and is not moved by this WP.
- `evaluation/evolution.py` consumes `_eval_value_with_unit` for duration and
  unit-aware expressions; this consumer must continue to resolve through the
  context contract.
- Classical reads use `objects`, `scalars`, `scalar_units`, `_this`, classes,
  structs, and enums. Assignment and provenance writes mutate evaluator-owned
  maps and remain owner callbacks, not extracted state.
- Continuous operations read the existing seed/port and write only the
  evaluator-owned opaque handle/provenance entries; the extracted module must
  receive these through explicit callbacks.
- `_bind`, `_run_unit_body`, `_bind_inner`, and `_materialize_outer` remain
  retained cross-family/state-algebra responsibilities.

### Consumer and dependency inventory

- Static consumers: `values.py`, `calls.py`, `evolution.py`, evaluator
  orchestration, classical/unit tests, continuous-field tests, and private
  Unit C/D contract tests.
- No `runtime/evaluation/*.py` module imports the public evaluator facade.
- Existing private names `_eval_value`, `_evaluate_value`,
  `_eval_value_with_unit`, and continuous bind hooks remain compatibility
  surfaces until a separate consumer decision.
- External boundary: `ContinuousFieldPort` only. No provider SDK, network,
  credential, filesystem, or new port is introduced.

### Exact Phase 1 allowed paths

- `compiler/staqex/runtime/evaluator.py`
- `compiler/staqex/runtime/evaluation/classical.py`
- `compiler/staqex/runtime/evaluation/continuous.py` (new)
- `compiler/staqex/runtime/evaluation/context.py`
- `compiler/staqex/runtime/evaluation/compatibility.py`
- `compiler/staqex/runtime/evaluation/values.py`
- `tests/test_liss_0568_value_continuous_red.py` (new)
- `docs/testing/active-red-tests.toml`
- this WP, LISS-0568, the design trace, and the Phase 1 review packet

Parser, typechecker, Semantic IR, QASM, provider, network, historical WP-0162,
and unrelated scientific-profile files are excluded.

### Phase 1 Red acceptance contract

1. `classical.py` contains the explicit value/unit entrypoint and
   `continuous.py` contains finiteize/field/compose entrypoints without a
   public facade import.
2. The context declares narrow callbacks for value recursion, DTO predicates,
   unit conversion, continuous port access, seed, and evaluator-owned writes.
3. Compatibility wiring preserves `_eval_value`, `_evaluate_value`,
   `_eval_value_with_unit`, and all four continuous private hooks.
4. Extracted modules do not define a second mutable state owner or directly
   mutate copied evaluator maps.
5. Existing classical literals/attributes/constructors/units and continuous
   finiteize/field/provenance behavior remain the characterization contract.

The Phase 0 inventory and boundaries are accepted. This acceptance authorizes
Phase 1 Red test work only; it does not authorize body migration or public API
retirement.

Next approval:
`WP-0165 / LISS-0568 Phase 1 Red 承認`.

## Phase 1 Red

Approved on 2026-09-19:
`WP-0165 / LISS-0568 Phase 1 Red 承認`.

Added `tests/test_liss_0568_value_continuous_red.py` with eight bounded
contracts: five expected structural gaps for the successor modules, callback
contracts, and compatibility wiring; plus three existing classical and
continuous characterization cases. Active-Red ownership is registered for
LISS-0568. The exact Red run produced **5 failed, 3 passed**. The five
failures are limited to the absent `continuous.py`, callback declarations, and
compatibility installers; all three characterization cases pass. The initial
classical fixture setup was corrected from a nonexistent `Evaluator.run()` API
to the repository's `run_source()` host entrypoint before this final Red run.
No production source or reviewed assertion was changed.

Next approval:
`WP-0165 / LISS-0568 Phase 1 Red テストレビュー承認`.

## Phase 1 Red test review

Accepted on 2026-09-19:
`WP-0165 / LISS-0568 Phase 1 Red テストレビュー承認`.

Review packet:
`docs/collaboration/reviews/2026-09-19-liss-0568-phase1-red-review.md`.
All eight contracts were reviewed. The exact focused run produced
**5 failed, 3 passed**: five intended structural gaps and three passing
classical/continuous characterization cases. Lifecycle, document,
coverage-ledger, and diff checks passed. No production implementation started.

Next approval:
`WP-0165 / LISS-0568 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation

Approved and implemented on 2026-09-19:
`WP-0165 / LISS-0568 Phase 2 Green / Implementation 承認`.

Implemented the approved continuous successor body in
`evaluation/continuous.py`: interval finiteization, Continuous-field
finiteization, host field creation, composition, and provenance storage. The
existing `classical.py` now exposes explicit value/unit/attribute successor
entrypoints while preserving the legacy evaluator behavior boundary. Context
callbacks expose the evaluator-owned object map, seed, port, nested value
evaluation, and runtime-object writes without copying mutable state.

Verification:

- LISS-0568 Red plus continuous/classical adjacent suites: **24 passed**.
- The Active-Red entry was retired after all eight LISS-0568 contracts passed.
- Runtime compileall, test lifecycle, document lifecycle, coverage-ledger
  consistency, and `git diff --check`: passed.

No parser, Semantic IR, QASM, provider, public API, or language behavior
change was introduced. Next step is Phase 3 Refactor and compatibility audit.

Next approval:
`WP-0165 / LISS-0568 Phase 3 Refactor 承認`.

## Phase 3 Refactor

Approved and completed on 2026-09-19:
`WP-0165 / LISS-0568 Phase 3 Refactor 承認`.

Refactor-only cleanup factored shared seed/port validation in
`continuous.py`, improved line-level readability, and kept compatibility
installers grouped by family. No runtime behavior, assertion, fixture,
provenance shape, or public API changed. The remaining legacy classical value
body is explicitly retained as a future bounded migration scope.

Verification after refactor: focused/adjacent suites **24 passed**, full
pytest **2,171 passed**, and compileall, lifecycle, document, coverage-ledger,
and diff checks passed.

Next approval:
`WP-0165 / LISS-0568 Phase 3 最終レビュー 承認`.

## Phase 3 final review

Accepted on 2026-09-19:
`WP-0165 / LISS-0568 Phase 3 最終レビュー 承認`.

Review packet:
`docs/collaboration/reviews/2026-09-19-liss-0568-phase3-final-review.md`.
The continuous successor boundary, compatibility wiring, single mutable-state
owner, and structural budget were re-read and verified. Focused/adjacent
tests passed (**24**), full pytest passed (**2,171**), and compileall,
lifecycle, document, coverage-ledger, and diff checks passed.

Process review: no operating-contract deviation or operational problem found.

WP-0165 and LISS-0568 are complete. Further migration of the remaining
classical legacy value body requires a new approved scope.
