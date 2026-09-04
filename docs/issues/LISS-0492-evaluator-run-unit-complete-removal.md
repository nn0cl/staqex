# LISS-0492: Complete removal of evaluator `run_unit()`

| Field | Value |
|---|---|
| Status | **done — public evaluator legacy entry removed** |
| Phase | phase-3-refactor-complete |
| Parent | [WP-0107](../work-plans/WP-0107-scientific-semantic-core.md) |
| Predecessor | [LISS-0491](LISS-0491-evaluator-legacy-run-unit-retirement.md) |
| Design authority | [Scientific Semantic Consumer Migration](../specs/staqex-scientific-semantic-consumer-migration.md#liss-0492-evaluator-run-unit-complete-removal) |
| Scope approval | Named target received from Adjudicator 2026-09-01 |
| Architecture approval | Approved by Adjudicator 2026-09-01 for the bounded migration and removal gates |
| Implementation permission | No |
| Next approval | None for this bounded Issue; AST mechanics remain separate |

## [DESIGN CHECK]

- **Scope and expected behavior:** remove the public
  `Evaluator.run_unit(CompilationUnit)` API and its compatibility/deprecation
  metadata after every runtime, verification, and regression caller has moved
  to `run_canonical_unit(..., semantic_ir=...)` or an approved test helper
  that obtains the compile-owned semantic IR.
- **Specifications and files inspected:** LISS-0491, its Phase 3 review,
  evaluator, pipeline, host, run, CLI, project conventions, WP-0107, the
  consumer-migration Spec, and the repository-wide call-site inventory.
- **Component boundaries, ports/adapters, and VO/DTO candidates:** pipeline
  owns the canonical IR; evaluator exposes only the canonical execution
  boundary; delivery callers pass the compile-owned IR; test helpers must not
  fabricate authority. `RngPort`, `MeasureSinkPort`, and host-input ports stay
  injected. No new DTO or external adapter is required.
- **Applicable constraints:** no second semantic authority, no early State
  collapse, terminal Measure remains the sink boundary, no provider/QPU/AWS,
  Rust, solver, release technology, or persistence changes.
- **Decisions, assumptions, and unresolved ambiguities:** the current test
  suite contains many direct legacy calls, including specification-verification
  suites. Complete removal therefore needs bounded test-family migrations and
  cannot be a one-file deletion. The final public compatibility policy and
  whether a private test-only helper is permitted require Architecture
  approval.
- **Included and omitted AI context:** included all evaluator callers,
  canonical compile result, provenance/authority fields, and local test
  families. Omitted unrelated language features, provider credentials, and
  future Rust/runtime implementation.
- **Task routing:** host-agent inventory and deterministic test migration;
  same-context review under current routing; no external AI/provider output.
- **Input/output evidence contract:** every execution input must carry a
  compile-owned `ScientificSemanticIR`; every result exposes canonical
  authority and source identity; unsupported or missing canonical meaning
  fails before mutation or artifact publication.
- **Verification plan:** freeze caller inventory; migrate production tests by
  bounded families; add a removal Red test; remove the method and compatibility
  fields; run full local regression and static no-reference checks; review
  public import/API surface and documentation.

## Observed removal surface

LISS-0491 eliminated direct production delivery callers and separated the
authority-neutral `_execute_unit()` mechanics. The remaining references are
primarily tests and specification-verification suites. They are not allowed
to keep the public API alive accidentally: each must either migrate to the
canonical entry with the exact compiled IR or be explicitly classified as a
test of an unrelated internal mechanic and given an approved helper.

The removal inventory must classify:

| Class | Required action | Evidence |
|---|---|---|
| `tests/test_*` feature/regression files | migrate in semantic-family batches | batch test pass and no direct call scan |
| `tests/spec_verification/suites/*` | migrate shared execution helpers first, then suites | suite pass and canonical source identity assertions |
| docs/examples/comments | update references or mark historical evidence | documentation reference scan |
| evaluator API tests | replace legacy metadata assertions with canonical/absence assertions | removal Red/Green tests |
| private `_execute_unit()` | retain only while it serves both public removal and canonical execution | Phase 3 review; no public fallback |

## Work breakdown and sequence

The complete removal is one architectural objective but several bounded
development units:

1. **LISS-0492-A — test execution helper migration:** introduce one local
   helper that compiles and calls the canonical entry, then migrate the
   `tests/spec_verification` shared patterns. No production behavior change.
2. **LISS-0492-B — feature-family migration:** migrate direct evaluator tests
   in bounded families (runtime/ports, arithmetic/units, dynamic lanes,
   structured operators, and examples). Preserve assertions; each batch gets
   its own focused regression.
3. **LISS-0492-C — removal guard Red/Green:** add a test proving the public
   `run_unit` attribute is absent and no source reference remains outside
   explicitly historical documentation. Then remove the public method and
   compatibility-only `execution_deprecation` field/behavior.
4. **LISS-0492-D — closure and API audit:** run full local regression, inspect
   exports/imports/docs, verify canonical authority/source identity and
   State/Measure/port behavior, and record the final no-reference evidence.

Each unit requires its own Issue/phase approval if it changes production code;
the breakdown is not implementation authorization.

## Acceptance criteria

- No callable public `Evaluator.run_unit` remains.
- No production or test execution path invokes `.run_unit(`; historical
  documentation may mention the migration only when clearly non-executable.
- All local execution enters through a canonical semantic IR carrying valid
  authority and source identity.
- No test fabricates a semantic IR solely to satisfy the signature; fixtures
  derive it from the same compile result as the executed unit.
- Canonical results retain source identity and `execution_authority` while no
  longer exposing compatibility-only deprecation metadata.
- State remains non-collapsed before terminal Measure; `RngPort` and
  `MeasureSinkPort` effects remain unchanged.
- No hidden finiteization, provider call, network access, QPU claim, AWS
  credential, Rust code, or release-policy choice is introduced.
- Targeted batches and the full local regression pass, with the final
  no-reference scan recorded in the closure review.

## Stop conditions and rollback

Stop and retain the compatibility implementation if a caller cannot receive
the compile-owned semantic IR without changing language meaning, if source
provenance diverges, if State/Measure or port behavior changes, or if a test
requires an unapproved new provider/release boundary. Stop for a new ADR if
public versioning, packaging, concurrency, persistence, or external execution
contracts become necessary.

## Architecture approval request

Approve or reject the bounded migration sequence, the canonical-only test
helper rule, the public API removal gate, and the listed stop conditions.
Approval does not authorize any Phase 1 Red test creation or implementation.

## Architecture approval result

- The bounded sequence LISS-0492-A through D is accepted.
- Test and verification callers must derive the executed unit and canonical
  semantic IR from the same compile result; fabricated authority is forbidden.
- The public API removal gate, canonical-only helper rule, no-reference scan,
  State/Measure and injected-port invariants, and rollback/stop conditions are
  accepted.
- No release/version policy, provider boundary, Rust implementation, or
  implementation permission is created by this approval.

## Phase 1 Red readiness

The fixed Phase 1 Red batch is:

- `tests/test_liss_0492_evaluator_run_unit_complete_removal_red.py`;
- this Issue, the linked migration Spec, WP-0107, and the Phase 1 review
  record;
- no production implementation changes and no broad test migration in Red.

The tests will establish the removal contract: a canonical test helper must
pass the compile-owned semantic IR; all current direct test/spec-verification
callers must be inventoried and classified; the public `run_unit` attribute
must be absent after the removal phase; executable references must be
detectable; canonical results must retain authority/source identity; and
State/Measure plus injected-port behavior must remain unchanged.

Phase 1 Red requires separate explicit approval before the test file is
created.

## Phase 1 Red result

- Added `tests/test_liss_0492_evaluator_run_unit_complete_removal_red.py`.
- Verification: **2 failed, 2 passed**, with no collection errors.
- The failures expose the two removal blockers: public `Evaluator.run_unit`
  still exists, and 131 executable references remain across existing feature
  tests and specification-verification suites.
- The canonical test helper and terminal Measure/authority/source contract
  pass.
- No production implementation, broad test migration, or API removal was
  performed.

Phase 1 Red is complete; Phase 2 must migrate callers in bounded families
before the removal guard can become Green.

## Phase 2 Green — LISS-0492-A result

- Added `tests/spec_verification/harness/canonical_execution.py`, which
  requires the unit and compile-owned semantic IR from one compile result.
- Migrated SV-07 and SV-08, removing nine direct `run_unit()` calls without
  changing their semantic assertions.
- Full Spec Verification: **161/161 passed, 100%**. `git diff --check` passed.
- Complete-removal Red guard remains intentionally failing because the other
  feature/regression and specification-verification families still contain
  direct references.
- Review: `docs/collaboration/reviews/2026-09-01-liss-0492-phase2a-review.md`.

LISS-0492-B through D remain separate bounded migration and removal work; the
public API is not removed by this batch.

## Phase 2 Green — LISS-0492-B result

- Migrated the remaining 15 specification-verification suites and 17 direct
  calls to the shared canonical helper.
- `tests/spec_verification/suites` now contains zero direct `run_unit()`
  references.
- Full Spec Verification: **161/161 passed, 100%**; migrated files compile and
  `git diff --check` passed.
- The remaining inventory is 103 feature/regression test references; the
  public API remains until LISS-0492-C and the final removal gate.
- Review: `docs/collaboration/reviews/2026-09-01-liss-0492-phase2b-review.md`.

## Phase 2 Green — LISS-0492-C unit/runtime batch result

- Added `tests/canonical_execution.py` for local regression tests.
- Migrated 48 calls across unit-conversion, runtime-port, and display-unit
  tests to canonical execution.
- Targeted family verification: **48 passed**; helper compilation and
  `git diff --check` passed.
- Remaining executable feature references: **73**, limited to operator,
  dynamic, structured, and other feature families.
- Review: `docs/collaboration/reviews/2026-09-01-liss-0492-phase2c-review.md`.

## Phase 2 Green — operator/expression batch result

- Migrated 42 operator/expression evaluator calls across 12 feature test
  modules to `tests/canonical_execution.py`.
- Targeted verification: **56 passed**; helper compilation and
  `git diff --check` passed.
- Remaining executable references: **31**, in ports, dynamic execution,
  evolve/binder, and example tests.
- Review: `docs/collaboration/reviews/2026-09-01-liss-0492-phase2d-review.md`.

## Phase 2 Green — final feature batch result

- Migrated the remaining 31 calls across ports, dynamic/evolve, binder, and
  example tests to the canonical helper.
- Non-contract executable `run_unit()` references: **0**.
- Targeted final feature batch: **65 passed**.
- LISS-0492 removal guard: **3 passed, 1 failed**; the sole failure is the
  expected remaining public `Evaluator.run_unit` attribute.
- `git diff --check` passed.
- Review: `docs/collaboration/reviews/2026-09-01-liss-0492-phase2e-review.md`.

All caller migration is complete. LISS-0492-D may now remove the public method
and compatibility-only result field, subject to explicit implementation
approval and final full-regression verification.

## LISS-0492-D result

- Removed public `Evaluator.run_unit()` and `EvalResult.execution_deprecation`.
- Updated the LISS-0491 regression contract, S02 benchmark, and resource
  wiring patch target to the canonical API.
- API-related regression: **19 passed**. Spec Verification: **161/161 passed**.
  Full pytest: **1823 passed, 10 unrelated existing Red failures** in
  QASM/meaning-family owners.
- `py_compile` and `git diff --check` passed.
- Review: `docs/collaboration/reviews/2026-09-01-liss-0492-phase3-review.md`.
- Process review: no operating-contract deviation or operational problem found.

The remaining evaluator `_execute_unit()` AST mechanics are intentionally not
retired by this Issue and require separate scope/approval.
