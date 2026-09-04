# LISS-0491: Evaluator legacy `run_unit()` retirement design

| Field | Value |
|---|---|
| Status | **done — canonical execution no longer bypasses through legacy entry** |
| Phase | phase-3-refactor-complete |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Related Issues | [LISS-0489](LISS-0489-symbolic-ir-canonical-inspection.md), [LISS-0490](LISS-0490-evaluator-canonical-execution-boundary.md), [LISS-0447](LISS-0447-residual-semantic-consumer-reconciliation.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0491-evaluator-legacy-run-unit-retirement) |
| Existing authority | [Scientific Semantic Core](../specs/staqex-scientific-semantic-core.md), ADR 0211 |
| Scope approval | Adjudicator approved `run_unit` retirement design 2026-08-31 |
| Architecture approval | Approved by Adjudicator 2026-08-31 for the staged retirement boundary |
| Implementation permission | No |
| Next approval | None for this bounded Issue; API removal remains separate |

## [DESIGN CHECK]

- **Scope and expected behavior:** design staged retirement of public legacy
  `Evaluator.run_unit(CompilationUnit)` after canonical
  `run_canonical_unit(..., semantic_ir=...)` is proven across local callers.
- **Specifications and files inspected:** `evaluator.py`, `host.py`, `run.py`,
  `cli.py`, LISS-0489, LISS-0490, WP-0107, the consumer-migration Spec, ADR
  0211, project conventions, readiness checklist, and call-site inventory.
- **Component boundaries, ports/adapters, and VO/DTO candidates:** the
  pipeline owns `ScientificSemanticIR`; evaluator owns execution mechanics;
  host/run/CLI are delivery callers. Existing `RngPort`, `MeasureSinkPort`,
  and host-input ports remain injected. A retirement disposition record is a
  candidate contract, not an approved DTO.
- **Applicable constraints:** canonical IR is the only execution authority;
  AST is mechanics only; `State<T>` collapses only at terminal `Measure`; no
  provider SDK, QPU, AWS, Rust, solver, or deployment work.
- **Decisions, assumptions, and unresolved ambiguities:** direct callers exist
  in delivery code, tests, and verification suites, so migration is staged.
  The deprecation mechanism and final removal release require Architecture
  approval. No blanket rejection is proposed in this design phase.
- **Included and omitted AI context:** included evaluator boundary,
  compilation result, caller classes, authority metadata, and ports. Omitted
  unrelated language features, provider credentials, numerical solver design,
  and historical issue narratives.
- **Task routing:** host-agent inventory plus same-context architecture review;
  deterministic tests only after Phase 1 approval; no external AI/provider.
- **Input/output evidence contract:** inputs are a compiled unit, matching
  canonical IR, source identity/fingerprint, and injected ports. Outputs expose
  execution authority, provenance, diagnostics, and unchanged runtime results.
- **Verification plan:** complete caller inventory; Red tests for no-bypass,
  migration coverage, deprecation observability, and State/Measure/port
  behavior; migrate bounded caller families; prove zero production callers
  before removal; run targeted and full local regression.

## Problem statement and observed inventory

`run_canonical_unit()` validates canonical type, authority, and source identity,
then delegates to existing evaluator mechanics. `run_unit()` remains directly
callable and labels its result `legacy_ast_compatibility`, so it is an explicit
compatibility lane but still permits execution without a compile-owned semantic
snapshot.

Current caller classes are:

| Caller class | Examples | Migration treatment |
|---|---|---|
| Delivery/runtime | `compiler/staqex/host.py`, `run.py`, `cli.py` | migrate first; preserve output/error contracts |
| Specification verification | `tests/spec_verification/suites/sv*.py` | migrate after delivery lanes |
| Feature/regression tests | many `tests/test_*` files | migrate by bounded semantic families; isolate legacy tests |
| Internal mechanics/tests | evaluator helpers and doubles | classify individually before API removal |

The inventory is acceptance evidence. A grep count alone is insufficient because
wrappers and monkeypatches must be classified.

## Proposed staged retirement boundary

```text
compile(source) -> CompileResult.scientific_semantic_ir
             -> canonical execution request
             -> Evaluator.run_canonical_unit(...)
             -> existing mechanics (temporary implementation detail)

Evaluator.run_unit(...) -> compatibility-only lane
                         -> observable deprecation + removal gate
```

1. Classify all direct and indirect callers and freeze the canonical invocation
   adapter plus unchanged result/port behavior.
2. Migrate `host.py`, `run.py`, and CLI to pass the compile-owned semantic IR.
   Keep `cmd_inspect` non-destructive and document its measure-filtering policy
   separately from execution.
3. Migrate spec-verification helpers and feature-test families in bounded
   batches. Keep only explicitly named compatibility tests on `run_unit()`.
4. Keep `run_unit()` callable during a bounded window, with a stable,
   machine-readable compatibility/deprecation classification that includes
   caller lane and source identity when available, but no secrets/provider data.
5. Remove it only after production caller inventory is empty, compatibility
   tests are migrated or intentionally isolated, no-bypass tests pass, runtime
   port/state regressions remain green, and full local regression is green.
   Any canonical/source-provenance divergence rolls back to the compatibility
   lane.

## Acceptance design for next phases

Phase 1 Red must cover: delivery callers pass the exact canonical object and
fingerprint; legacy calls are compatibility-only; canonical and migrated
neighbors preserve State/Measure, ports, diagnostics, and provenance; missing
or mismatched canonical input fails closed before mutation/allocation/measurement;
new production direct callers fail an inventory guard; deprecation metadata is
observable separately from scientific output; inspection is not execution; and
no provider/QPU/AWS/Rust behavior is introduced.

Phase 2 Green is limited to one bounded caller family per approval. Phase 3 may
simplify the compatibility adapter and update the removal ledger, but may not
silently remove the legacy entry without removal-gate evidence.

## Explicit non-goals and stop conditions

This design does not remove `run_unit()`, rewrite `_run_unit_body`, change
language semantics, define a release/version policy, select a deprecation
framework, migrate QASM/QPU/provider paths, or begin Rust work. Stop for a new
ADR if removal changes public runtime compatibility, introduces release policy,
changes port contracts, or requires concurrency/persistence decisions.

## Architecture approval request

Approve or reject the staged retirement boundary, delivery-before-test order,
observable compatibility lane, zero-production-caller removal gate, and
fail-closed rollback trigger. Approval does not authorize Phase 1 tests, Phase 2
implementation, or removal of `run_unit()`.

## Architecture approval result

- The staged retirement boundary is accepted: canonical execution is the
  required destination and `run_unit()` remains compatibility-only until the
  removal gate is evidenced.
- The delivery-before-test migration order, observable compatibility signal,
  production-caller inventory guard, zero-production-caller removal gate, and
  fail-closed rollback trigger are accepted.
- The exact deprecation mechanism and final release policy remain deferred;
  this approval introduces no release technology or new port.
- No Phase 1 test creation, Phase 2 implementation, or API removal is
  authorized by this result.

## Phase 1 Red readiness

The fixed Phase 1 Red batch is:

- `tests/test_liss_0491_evaluator_legacy_run_unit_retirement_red.py`;
- `tests/fixtures/semantic_core/evaluator_legacy_retirement.sqx` only if the
  existing fixture corpus cannot express the caller/provenance cases without
  duplication;
- this Issue, the linked migration Spec, WP-0107, and the Phase 1 review
  record.

The Red tests will cover canonical object/fingerprint propagation through
`host.py`, `run.py`, and CLI; legacy compatibility classification; missing or
mismatched canonical input; State/Measure and injected-port preservation;
observable caller/source deprecation evidence; and a production direct-caller
inventory guard. They will not modify evaluator production code or remove
`run_unit()`.

Phase 1 Red requires separate explicit approval before test files are created.

## Phase 1 Red result

- Added `tests/test_liss_0491_evaluator_legacy_run_unit_retirement_red.py`.
- No fixture was added; the existing minimal source shape is sufficient for
  the caller and provenance contracts.
- Verification: **5 failed**, with no collection errors.
- The failures expose the current gaps: `host.py` and `run.py` still invoke
  `run_unit()`; `EvalResult` has no observable deprecation record; four direct
  production callers remain in `host.py`, `run.py`, and `cli.py`; and canonical
  execution does not yet publish source provenance on its result.
- No evaluator production code, delivery code, API removal, provider, or
  external integration was changed.

The fixed Red batch is now complete. Phase 2 requires a separate approval and
must be limited to the smallest implementation that makes these assertions
green while preserving the compatibility lane.

## Phase 1 review result

Same-context review completed on 2026-09-01. The review found no Phase 1 scope
deviation. Three implementation findings are accepted for Phase 2: migrate the
delivery callers, add observable deprecation/source provenance, and enforce the
production caller inventory. Review record:
`docs/collaboration/reviews/2026-09-01-liss-0491-phase1-review.md`.

The review is weaker than a separate-context review and does not grant Phase 2
implementation permission.

## Phase 2 Green result

- Migrated `host.py`, `run.py`, and CLI inspection to
  `run_canonical_unit(..., semantic_ir=...)`.
- Added `EvalResult.source_id` and structured legacy deprecation metadata;
  canonical execution exposes its compile-owned source identity and clears
  the compatibility signal.
- The production caller inventory guard now passes with no direct
  `.run_unit()` callers outside `evaluator.py`.
- Verification: LISS-0491, LISS-0490, MeasureSinkPort, SourcePort, and host
  orchestration suites **27 passed**; `py_compile` and `git diff --check`
  passed.
- Phase 2 review: `docs/collaboration/reviews/2026-09-01-liss-0491-phase2-review.md`.

`run_canonical_unit()` still delegates to existing evaluator mechanics by
design. Phase 3 must decide whether and how those mechanics can be retired;
this result does not authorize removing `run_unit()`.

## Phase 3 result

- Extracted `_execute_unit()` as the authority-neutral internal mechanics
  runner. Canonical execution calls it directly and no longer traverses the
  public legacy `run_unit()` entry.
- Preserved the legacy entry's explicit `legacy_ast_compatibility` authority
  and deprecation metadata for the compatibility window.
- Production inventory remains free of direct `.run_unit()` callers outside
  `evaluator.py`.
- Same-context review: `docs/collaboration/reviews/2026-09-01-liss-0491-phase3-review.md`.
- Process review: no operating-contract deviation or operational problem found.

Complete removal of `run_unit()` and retirement of the underlying AST
mechanics remain separate future scope requiring a new approval.

Process note: authority-boundary evidence is explicit in `execution_authority`;
review observability requires classification, reason, and source/caller
evidence; status must be synchronized when this slice closes.
