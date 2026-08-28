# Real-QPU readiness design review — 2026-08-27

## Review packet

- **Scope:** agent review of the approved WP-0119 roadmap, child WP-0120–0125,
  and LISS-0456–0470. LISS-0455 is already closed as the Phase 0 ledger
  reconciliation.
- **Review mode:** same-context read-only design review.
- **Canonical documents:** `open-work-register.md`, WP-0118–0125, ADR 0083,
  0103, 0104, 0127, 0161, 0202–0203, 0210–0213, and the related Issue files.
- **Changed files:** none during the review pass; status updates follow this
  packet as a separate synchronization action.

## Review lenses

1. Scope and acceptance completeness.
2. Parent WP / Issue dependency integrity.
3. Canonical Semantic IR and source-meaning preservation.
4. Realization, provenance, and no-artifact safety.
5. Clean Architecture and provider-port boundaries.
6. Credential, privacy, cost, retry, and lifecycle safety.
7. Phase and human-approval separation.
8. Evidence and reproducibility sufficient for a real-device claim.

## Findings and dispositions

| Finding | Severity | Disposition |
|---|---|---|
| Completed bounded semantic/realization/QASM/Host slices could be reopened by a broad real-QPU plan | P1 | Closed by LISS-0455 matrix and WP-0119 non-reopen rule |
| Public QASM facades and parallel AST/`symbolic_ir` paths lack one authority | P1 | Accepted as LISS-0456 design scope; Phase 1 remains gated |
| Coin/Mix contract must not be generalized to product/tensor, continuous/open-system, or measurement | P1 | Accepted as LISS-0457 family-by-family scope |
| Artifact, target, provider, result, and evidence boundaries were previously cross-cutting | P1 | Split into WP-0121–0124 with explicit dependencies |
| Provider/credential work could accidentally authorize real submission | P0 | Closed by explicit fake-first and human-only pilot gates |
| Deployment/persistence topology is not selected | P1 | Correctly conditional in WP-0125; separate ADR required |
| LISS-0458 had a duplicated design section in the draft | P2 | Removed during review; final Issue has one design section |
| LISS-0458 omitted its direct dependency on the LISS-0457 family disposition | P2 | Added during review; Issue graph now matches WP-0120/WP-0121 ordering |

## Verdict

**READY — design baseline approved for continued Issue-level acceptance review.**

WP-0120–0125 and LISS-0456–0470 are internally coherent enough to proceed to
their individual acceptance-spec reviews. No Issue is approved for Phase 1 Red,
Phase 2 implementation, provider installation, credential use, network access,
or real-QPU submission by this review.

## Acceptance-spec follow-up

The review found that the Issue-level design notes were not yet collected in
one formal EARS/Gherkin acceptance authority. The proposed
`docs/specs/staqex-real-qpu-readiness-acceptance.md` now maps one observable
scenario and exit-evidence row to every LISS-0456–0470 Issue. Each Issue and
WP-0120–0125 links to that specification. This closes the documentation gap
for the next review gate, but does not accept the specification or authorize
Phase 1 Red.

## Acceptance-spec review findings

| Finding | Severity | Disposition |
|---|---|---|
| All 15 Issues map to an observable scenario and exit-evidence row | — | Already closed with evidence in the acceptance specification and link audit |
| LISS-0457's family scenario should make the three research lanes explicit before Red | P1 | Apply: add a family-by-family research matrix; retain reject/defer as the default until a family-specific contract is accepted |
| LISS-0463–0466 could be read as authorizing provider work because AWS Braket is already selected | P0 | Already closed with evidence: the specification keeps SDK, credentials, network, and real submission behind separate technology/security/human gates |
| LISS-0470 could introduce deployment topology by implication | P1 | Already closed with evidence: it is conditional and requires a new ADR and technology approval |

The acceptance specification is therefore **READY as a proposed design
authority**, subject to the LISS-0457 matrix clarification below. It is not a
Phase 1 Red approval or implementation authorization.

## Required next gates

- LISS-0456: accept the canonical consumer migration scenarios, then request
  typed Phase 1 Red approval.
- LISS-0457: select one meaning family for a bounded specification, or record
  its deferral; do not implement all families together.
- LISS-0458–0462: accept artifact/target/QASM contracts before tests or code.
- LISS-0463–0466: complete technology/security review and fake-provider Red
  approval before any optional dependency or credential path is changed.
- LISS-0467–0469: accept the evidence and human-pilot protocol before a human
  performs any real run.
- LISS-0470: decide after the pilot whether delivery/operations is needed.

## Verification

- All LISS-0455–0470 have unique IDs and required planning metadata.
- Every LISS-0456–0470 has a linked acceptance-spec scenario and exit row.
- New WP/Issue relative links resolve.
- `git diff --check` passes.
- No production source, tests, dependency manifest, credentials, or provider
  calls were changed or executed.

## Approval boundary

This is an agent design-readiness verdict, not a replacement for the
Adjudicator's typed phase, technology, implementation, or real-run approval.

## LISS-0456 Phase 1 Red review

- User approval: Phase 1 Red for LISS-0456, 2026-08-27, interpreted from the
  immediate approval after the stated next gate.
- Branch: `codex/liss-0456-phase1-red`.
- Test-only artifact: `tests/test_liss_0456_semantic_consumer_qasm_red.py`.
- Red evidence: the canonical measure-only path currently calls
  `lower_unit_to_circuit`; the pytest-independent harness observed the intended
  assertion failure. Terminal Measure semantic role/provenance assertions
  pass independently.
- Deterministic checks: `py_compile` and `git diff --check` pass. Local pytest
  is unavailable because the environment has no pytest installation; CI/venv
  execution remains required.
- Reviewer disposition: **READY FOR ADJUDICATOR TEST REVIEW**. No production
  code, Phase 2 Green, or provider action is authorized by this review.

## LISS-0456 Phase 2 Green review

- User approval: Phase 2 Green for the reviewed LISS-0456 Red slice,
  2026-08-27.
- Production change is limited to `compiler/staqex/backend/qasm/emitter.py`:
  non-empty canonical projections containing only Measure instructions now use
  `emit_qpu_program` and do not fall through to `lower_unit_to_circuit`.
  Canonical output preserves the existing `terminal measure` comment.
- The Phase 1 test file remains unchanged. The targeted harness passes after
  the change; `py_compile` and `git diff --check` pass. Full pytest remains
  unavailable locally because pytest is not installed.
- Same-context reviewer disposition: **READY FOR ADJUDICATOR PHASE 2
  REVIEW**. Phase 3 refactor, issue closure, and all provider/real-QPU work
  remain unapproved.

## LISS-0456 Phase 3 closeout review

The user approved the Phase 3 review. The bounded change was re-read from
disk, and no additional refactor was warranted: the canonical Measure-only
branch is explicit, the Phase 1 test remains unchanged, and the adapter does
not acquire provider or semantic policy. The canonical regression,
`py_compile`, `compileall`, and `git diff --check` passed. Local pytest is not
available and is a CI merge gate. Same-context process review found no
operating-contract deviation or operational problem. LISS-0456 is therefore
closed for this bounded slice; LISS-0457 is the next safe action.

### 変更の要約 (PR Summary)

- **何を目的として何を変更したか**: canonical semantic QPU projections
  containing only terminal Measure instructions now use the canonical QPU
  emitter path instead of rebuilding through AST/DAG lowering; existing QASM
  output spelling remains stable.

### 残存リスク・検証の溝 (Verification Gap)

- **AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
  local pytest was unavailable, so the full suite result is not claimed.
- **人間がコードレビューで重点的に見るべきポイント**: ensure future
  canonical instruction-only paths cannot silently reintroduce AST fallback;
  run the LISS-0446 and full CI suites before merge.

## LISS-0457 acceptance-spec review

The product/tensor, continuous/open-system, and measurement lanes were
reviewed against the existing fixtures, specifications, and ADR boundaries.
The resulting disposition matrix is recorded in LISS-0457 and in the
acceptance specification. Product/tensor remains limited to accepted finite
projections; continuous/open-system QPU realization remains deferred without
hidden discretization; and terminal measurement remains distinct from
dynamic measurement, with general POVM/tomography deferred.

Same-context review disposition: **READY FOR PHASE 1 RED SCOPE REVIEW**.
This is an acceptance-spec/design verdict only. No Phase 1 tests, production
implementation, new public type, numerical method, provider, credential,
network, or live-QPU action is approved.

## LISS-0457 Phase 1 Red review

- User approval: Phase 1 Red for LISS-0457, 2026-08-27.
- Branch: `codex/liss-0457-meaning-family-qpu-readiness`.
- Test-only artifact: `tests/test_liss_0457_meaning_family_readiness_red.py`.
- Red evidence: the three family tests reach the intentionally absent
  `compiler.staqex.meaning_family_readiness` module under a
  pytest-independent harness and fail with the expected
  `ModuleNotFoundError`. The fourth test fixes the future fail-closed API
  shape and is likewise not executable until that reviewed contract exists.
- Deterministic checks: Python 3.14 `py_compile` and `git diff --check` pass.
  Local pytest is unavailable because pytest is not installed.
- Reviewer disposition: **READY FOR ADJUDICATOR TEST REVIEW**. Phase 2 Green,
  provider work, credentials, network access, and real-QPU execution remain
  unapproved.

## LISS-0465 Phase 3 closeout review

- User approved Phase 3 on 2026-08-28.
- Extracted provider-failure classification into a focused helper; reviewed
  idempotency, preflight rejection, dry-run, and retry behavior remain unchanged.
- Contract tests, Python 3.14 `py_compile`, and `git diff --check` pass.
- Same-context fake fault-injection reviewer disposition: **DONE for the
  bounded provider-neutral submit hardening slice**. Real provider, credential,
  network, and physical submission remain gated.

## LISS-0465 Phase 1 Red test review

- User approved the LISS-0465 Phase 1 Red gate on 2026-08-28.
- Added fake-port tests for request/artifact identity, idempotency,
  dry-run non-submission, pre-network payload/target rejection, and typed
  provider failures.
- Red is confirmed by the absent `compiler.staqex.submit_integration` module.
  Python 3.14 `py_compile` and `git diff --check` pass; pytest is unavailable
  locally. Provider SDK, credentials, network, and real-device calls remain
  excluded. Next gate is provider/security test review and Phase 2 approval.

## LISS-0465 Phase 2 Green review

- User approved provider/security review and Phase 2 Green on 2026-08-28.
- Added provider-neutral submit orchestration with pre-invocation payload and
  target validation, idempotency deduplication, dry-run/check zero-submit,
  and typed transient/permanent failure mapping.
- LISS-0465 contract tests, Python 3.14 `py_compile`, and
  `git diff --check` pass. No implicit retry, SDK, credential, network, or
  real-device behavior was introduced. Phase 3 fault-injection review is next.

## LISS-0466 Phase 1 Red test review

- User approved the LISS-0466 Phase 1 Red gate on 2026-08-28.
- Added fake-job lifecycle tests for status/result integrity, partial payload
  rejection, timeout/cancel/failure/unknown distinction, metadata and attempt
  preservation, and no resubmit during polling.
- Red is confirmed by the absent `compiler.staqex.job_lifecycle` module.
  Python 3.14 `py_compile` and `git diff --check` pass; pytest is unavailable
  locally. Provider SDK, credentials, network, and real-device calls remain
  excluded. Next gate is test review and Phase 2 approval.

## LISS-0467 Phase 2 Green review

- User approved Phase 2 Green on 2026-08-28 after evidence-protocol test
  review.
- Added a local/fake versioned evidence envelope carrying source-to-result
  identity, runtime metadata, baseline/tolerance/drift, and explicit
  non-fidelity claims for simulator/fake evidence.
- Missing links and unexplained drift remain incomplete/inconclusive, with no
  invented calibration. Contract tests, Python 3.14 `py_compile`, and
  `git diff --check` pass. Phase 3 review is next.

## LISS-0469 Phase 1 Red test review

- User approved the LISS-0469 Phase 1 Red gate on 2026-08-28.
- Added offline validation tests for predeclared criteria, raw/derived
  separation, explicit valid/inconclusive/rejected dispositions, drift,
  failed shots, provider anomalies, deviation, and identity preservation.
- Red is confirmed by the absent `compiler.staqex.result_validation` module.
  Python 3.14 `py_compile` and `git diff --check` pass; pytest is unavailable
  locally. No real result or provider data was used. Next gate is validation
  test review and Phase 2 approval.

## LISS-0469 Phase 2 Green review

- User approved Phase 2 Green on 2026-08-28 after validation test review.
- Added offline result analysis with raw/derived separation, predeclared
  criteria enforcement, explicit drift/anomaly/deviation dispositions, and
  unchanged source/artifact identity.
- Contract tests, Python 3.14 `py_compile`, and `git diff --check` pass. No
  real result, provider data, credential, or network was used. Phase 3 review
  is next.

## LISS-0469 Phase 3 closeout review

- User approved Phase 3 on 2026-08-28.
- Extracted disposition and derived-statistics construction; reviewed raw/
  derived separation, criteria, deviations, and identity remain unchanged.
- Contract tests, Python 3.14 `py_compile`, and `git diff --check` pass.
- Same-context validation reviewer disposition: **DONE for the bounded result
  validation/disposition slice**. Real-result analysis and physical-fidelity
  claims remain gated.

## LISS-0467 Phase 3 closeout review

- User approved Phase 3 on 2026-08-28.
- Extracted envelope status and fidelity-claim decisions into focused helpers;
  reviewed complete/incomplete/inconclusive behavior remains unchanged.
- Contract tests, Python 3.14 `py_compile`, and `git diff --check` pass.
- Same-context complete-envelope reviewer disposition: **DONE for the bounded
  reproducibility evidence slice**. Provider data, secrets, and physical
  fidelity claims remain gated.

## LISS-0470 deferred disposition review

- User confirmed on 2026-08-28 to follow the conditional operations policy.
- Local Host operation is sufficient for the current scope; no delivery ADR,
  deployment topology, datastore, public API, retention, monitoring, or
  provider operations were introduced.
- Same-context process review: **DONE as deferred**. Reopening requires a
  demonstrated post-pilot need, a new ADR, and typed architecture/technology
  approval.

## LISS-0468 Phase 1 Red test review

- User approved the LISS-0468 Phase 1 Red gate on 2026-08-28.
- Added offline pilot-checklist tests for dry-run review, safety/cost guards,
  credential state, cancellation/evidence plans, required real-time human
  approval, redaction, and execution labeling.
- Red is confirmed by the absent `compiler.staqex.pilot_checklist` module.
  Python 3.14 `py_compile` and `git diff --check` pass; pytest is unavailable
  locally. No real credential, network, provider, device, or submission was
  used. Next gate is pilot-protocol test review and Phase 2 approval.

## LISS-0468 Phase 2 Green review

- User approved Phase 2 Green on 2026-08-28 after pilot-protocol test review.
- Added offline/fake checklist evaluation with fail-closed safety and guard
  checks. It distinguishes `ready-for-human-approval` from `authorized`,
  while keeping physical execution false until observed evidence exists.
- Contract tests, Python 3.14 `py_compile`, and `git diff --check` pass. No
  real credential, network, device, or submission occurred. Phase 3 review is
  next.

## LISS-0468 Phase 3 closeout review

- User approved Phase 3 on 2026-08-28.
- Extracted checklist diagnostics and audit-field construction; approval
  states, redaction, physical-claim, and non-submit behavior remain unchanged.
- Contract tests, Python 3.14 `py_compile`, and `git diff --check` pass.
- Same-context pilot-protocol reviewer disposition: **DONE for the bounded
  human-authorization checklist slice**. Any real action remains separately
  human-authorized.

## LISS-0466 Phase 2 Green review

- User approved Phase 2 Green on 2026-08-28 after lifecycle test review.
- Added provider-neutral job observation with deterministic state mapping,
  complete metadata requirements, exact measurement ordering, and fail-closed
  partial-result handling. Observation never resubmits or retries.
- LISS-0466 contract tests, Python 3.14 `py_compile`, and
  `git diff --check` pass. No provider SDK, credentials, network, or device
  access occurred. Phase 3 fault-matrix review is next.

## LISS-0466 Phase 3 closeout review

- User approved Phase 3 on 2026-08-28.
- Extracted attempt normalization and common failed-result construction;
  reviewed lifecycle/fault behavior remains unchanged.
- Contract tests, Python 3.14 `py_compile`, and `git diff --check` pass.
- Same-context fault-matrix reviewer disposition: **DONE for the bounded job
  lifecycle/result-integrity slice**. Provider and live-QPU work remain gated.

## LISS-0467 Phase 1 Red test review

- User approved the LISS-0467 Phase 1 Red gate on 2026-08-28.
- Added the test-only reproducibility envelope contract for source-to-result
  identity, target/job metadata, baseline/tolerance/drift evidence, and
  physical-fidelity claim separation.
- Red is confirmed by the absent `compiler.staqex.evidence_envelope` module.
  Python 3.14 `py_compile` and `git diff --check` pass; pytest is unavailable
  locally. Missing links and unexplained drift remain non-success statuses.
  Next gate is evidence-protocol test review and Phase 2 approval.

## LISS-0463 Phase 1 Red test review

- User approved the LISS-0463 Phase 1 Red gate on 2026-08-28.
- Added the test-only provider dependency policy contract. It covers optional
  local importability, actionable missing-SDK failure, security-floor
  rejection before SDK import, and Host-adapter boundary ownership.
- Red is confirmed by the absent
  `compiler.staqex.provider_dependency_policy` module. Python 3.14
  `py_compile` and `git diff --check` pass; pytest is unavailable locally.
- Dependency manifest changes and technology/range decisions remain outside
  this phase. Next gate is technology/security test review and Phase 2
  approval.

## LISS-0463 Phase 2 Green review

- User approved the technology/security review and Phase 2 Green with no
  manifest change on 2026-08-28.
- Added a provider-neutral dependency policy inspector. It checks optional
  absence, the approved security floor, and Host-adapter-only ownership
  without importing or installing the SDK.
- LISS-0463 and existing AWS Braket adapter contract tests pass; Python 3.14
  `py_compile` and `git diff --check` pass. No credentials, network call, or
  live submission occurred. Phase 3 security/CI review is next.

## LISS-0463 Phase 3 closeout review

- User approved Phase 3 on 2026-08-28.
- Extracted boundary validation and dependency diagnostic construction into
  focused helpers; reviewed policy behavior remains unchanged.
- Contract and existing adapter tests pass; Python 3.14 `py_compile` and
  `git diff --check` pass. No SDK or manifest was added, so external package
  installation/audit was not applicable.
- Same-context reviewer disposition: **DONE for the bounded dependency
  policy/security isolation slice**. Provider adoption, pinning, credentials,
  and live submission remain gated.

## LISS-0464 Phase 1 Red test review

- User approved the LISS-0464 Phase 1 Red gate on 2026-08-28.
- Added the test-only Host configuration contract for precedence,
  fail-closed validation, pre-network cost/shot/timeout guards, dry-run
  behavior, redacted audit fields, and conflict handling.
- No secret values were added. Red is confirmed by the absent
  `compiler.staqex.host_configuration` module. Python 3.14 `py_compile` and
  `git diff --check` pass; pytest is unavailable locally.
- Next gate is security test review and Phase 2 approval. Credentials,
  network access, and live submission remain out of scope.

## LISS-0464 Phase 2 Green review

- User approved the LISS-0464 security review and Phase 2 Green on 2026-08-28.
- Added the provider-neutral Host configuration preflight. It applies
  deterministic precedence, rejects invalid/conflicting inputs before network
  work, keeps dry-run/check non-submitting, and redacts audit values.
- LISS-0464 contract tests, Python 3.14 `py_compile`, and
  `git diff --check` pass. No real credentials, environment, network, or
  provider was accessed. Phase 3 security review is next.

## LISS-0464 Phase 3 closeout review

- User approved Phase 3 on 2026-08-28.
- Extracted configuration diagnostics and redacted audit construction into
  focused helpers; reviewed validation behavior remains unchanged.
- Contract tests, Python 3.14 `py_compile`, and `git diff --check` pass. No
  real credentials, environment, network, or provider was accessed.
- Same-context reviewer disposition: **DONE for the bounded credential/config
  preflight slice**. Provider credentials, production configuration loading,
  and live submission remain gated.

## LISS-0462 Phase 1 Red test review

- User approved the LISS-0462 Phase 1 Red gate on 2026-08-28.
- Added dynamic QASM fixtures and the test-only conformance contract. The
  packet covers explicit dynamic measurement/feed-forward metadata,
  reset/reuse accounting, branch outcomes and wire mapping, static-only
  target rejection, unsupported-branch rejection, and required reuse
  metadata.
- Red is confirmed by the absent
  `compiler.staqex.dynamic_qasm_conformance` module. Python 3.14
  `py_compile` and `git diff --check` pass; pytest is unavailable locally.
  Next gate is Adjudicator test review before Phase 2 Green.

## LISS-0462 Phase 2 Green review

- User approved Phase 2 Green after the LISS-0462 Red test review on
  2026-08-28.
- Added the minimum provider-neutral dynamic QASM conformance validator. It
  exposes explicit control/outcome metadata, wire mapping, branch outcomes,
  reset/reuse evidence, and atomic rejection for unsupported dynamic behavior.
- The LISS-0462 contract test and existing dynamic QPU integration test pass;
  Python 3.14 `py_compile` and `git diff --check` pass. Pytest remains
  unavailable locally.
- No provider SDK, credentials, network access, QASM submission, or physical
  execution claim was introduced. Phase 3 is the next approval gate.

## LISS-0462 Phase 3 closeout review

- User approved Phase 3 on 2026-08-28.
- Refactored diagnostic de-duplication and target-capability checks into
  focused helpers; reviewed assertions and behavior remain unchanged.
- LISS-0462 contract tests, existing dynamic emission/integration tests,
  Python 3.14 `py_compile`, and `git diff --check` pass. Pytest remains
  unavailable locally.
- Same-context reviewer disposition: **DONE for the bounded dynamic QASM
  conformance slice**. Same-context isolation is weaker than separate-context
  review. Provider, credential, submission, and live-QPU work remain gated.

## LISS-0461 Phase 3 closeout review

- User approved Phase 3 for LISS-0461 on 2026-08-28.
- Extracted shared rejection construction and static-header validation.
  Reviewed tests and observable conformance behavior remain unchanged.
- Re-read the acceptance spec, WP-0122, LISS-0461, validator, fixtures,
  emitter/facade, and related tests. No blocker was found within the bounded
  static subset.
- The contract test, Python 3.14 `py_compile`, and `git diff --check` pass.
  Existing pytest QASM tests are unavailable locally; SV11 requires its suite
  runner.
- Isolation: `same_context`, weaker than `separate_context`.
- Process review found no operating-contract deviation or operational problem.
- Reviewer disposition: **DONE for the bounded static QASM conformance slice**.
  Dynamic QASM, provider, credential, and live-QPU work remain gated.

## LISS-0461 Phase 1 Red review

- User approved Phase 1 Red for LISS-0461 on 2026-08-28.
- Added static QASM fixtures for Bell, parameterized terminal measurement,
  dynamic-control rejection, and empty-program rejection, plus
  `tests/test_liss_0461_static_qasm_conformance_red.py`.
- The packet covers declared subset acceptance, metadata retention, unsupported
  dynamic rejection, and empty/no-artifact/no-allocation behavior.
- Red evidence: the intentionally absent
  `compiler.staqex.qasm_conformance` module is confirmed absent. Python 3.14
  `py_compile` and `git diff --check` pass; pytest is unavailable locally.
- Reviewer disposition: **READY FOR ADJUDICATOR TEST REVIEW**. Phase 2 Green,
  provider extensions, SDKs, credentials, network access, and live-QPU
  execution remain unapproved.

## LISS-0461 Phase 2 Green review

- User approved Phase 2 Green for LISS-0461 on 2026-08-28.
- Added the standard-library-only static QASM subset validator. Accepted
  inputs retain QASM and source/semantic/artifact/measurement metadata;
  dynamic, empty, and unsupported inputs fail closed without artifact or
  allocation fallback.
- The reviewed tests and fixtures are unchanged. The LISS-0461 contract test,
  Python 3.14 `py_compile`, and `git diff --check` pass. Existing QASM pytest
  tests are unavailable locally; SV11 cannot run standalone because its
  `harness` import requires the suite runner.
- Reviewer disposition: **GREEN REVIEWED; READY FOR PHASE 3 REVIEW APPROVAL**.

## LISS-0471 Phase 2 Green review

- User approval: Phase 2 Green for the Measurement slice, 2026-08-27.
- Production artifact: `compiler/staqex/measurement_family_readiness.py`.
- The classifier consumes canonical Scientific Semantic IR. It classifies
  terminal `Measure` as `terminal_classical`, rejects dynamic measurement with
  the existing capability diagnostics, preserves source identity, and emits
  no artifact or QASM. Unspecified measurement realizations are explicitly
  deferred.
- The Red tests were not changed. Static terminal, dynamic rejection, and
  POVM/Tomography deferral direct checks pass; `py_compile` and
  `git diff --check` pass. Local pytest is unavailable.
- Same-context reviewer disposition: **READY FOR ADJUDICATOR PHASE 2 REVIEW**.
  Phase 3, provider work, and real-QPU execution remain unapproved.

## LISS-0471 Phase 3 closeout review

The approved refactor separates dynamic diagnostic extraction, terminal
measurement detection, and decision construction into focused helpers. The
classifier still consumes canonical Scientific Semantic IR; reviewed
assertions and behavior are unchanged. Static terminal, dynamic rejection, and
explicit deferral checks pass, as do `py_compile` and `git diff --check`.

Same-context reviewer disposition: **DONE for the bounded Measurement slice**.
Process review found no operating-contract deviation or operational problem.
POVM/Tomography, provider, and real-QPU work remain separately gated.

### 変更の要約 (PR Summary)

- **何を目的として何を変更したか**: improve Measurement readiness
  classifier readability while preserving canonical lane semantics and
  artifact-free rejection.

### 残存リスク・検証の溝 (Verification Gap)

- **AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
  full pytest remains a CI-only check because pytest is unavailable locally.
- **人間がコードレビューで重点的に見るべきポイント**: ensure future
  measurement capabilities continue to preserve terminal/dynamic separation
  and do not turn deferred POVM/Tomography into implicit support.

## LISS-0471 Phase 2 Green review

The Measurement classifier was re-read against the reviewed Red tests and the
existing Semantic/Dynamic Lane contracts. It consumes canonical IR, uses
`DynamicMeasurementRegion` for dynamic classification and terminal `Measure`
nodes for static classification, preserves source identity, and returns no
artifact or QASM for unsupported/deferred cases. The Red tests are unchanged.

Direct static, dynamic, and deferral checks pass; Python 3.14 `py_compile` and
`git diff --check` pass. Same-context reviewer disposition: **GREEN REVIEWED;
READY FOR PHASE 3 REVIEW APPROVAL**. Phase 3 and provider/real-QPU work remain
unapproved.

## LISS-0471 Phase 1 Red test review

The test-only packet was re-read against the canonical measurement-family
scenario and the existing dynamic-lane specifications. It cleanly separates
terminal collapse from dynamic measurement, preserves source identity, checks
the existing pair of dynamic capability diagnostics and empty artifacts, and
keeps POVM/Tomography as an explicit deferral. It does not duplicate the
already-shipped low-level Dynamic Lane assertions or introduce provider
dependencies.

Same-context reviewer disposition: **TESTS REVIEWED; READY FOR PHASE 2 GREEN
APPROVAL**. The reviewed tests must remain unchanged during Green. Phase 2 is
limited to the Measurement classifier contract; provider and real-QPU work
remain unapproved.

## LISS-0457 Phase 1 Red test review

The test-only Red packet was re-read from disk against the LISS-0457 matrix
and the canonical acceptance scenarios. Each family assertion preserves the
semantic family boundary, requires an explicit rejection or deferral, and
checks that no finite artifact or QASM is produced. The tests use local source
fixtures only and contain no provider, credential, network, or numerical
method dependency. The unknown-family case also fixes the fail-closed error
shape for the future classifier.

Same-context reviewer disposition: **TESTS REVIEWED; READY FOR PHASE 2 GREEN
APPROVAL**. The reviewed tests must remain unchanged during Green. Phase 2 is
restricted to one family slice and its minimum classifier contract; no
family-wide implementation or provider/QPU action is approved.

## LISS-0457 Phase 2 Green review

- User approval: Phase 2 Green for the Product/Tensor slice, 2026-08-27.
- Production artifact: `compiler/staqex/meaning_family_readiness.py`.
- The implementation is provider-neutral and returns an immutable decision for
  the reviewed scalar non-unitary product boundary. It preserves source
  identity, returns the accepted rejection code/reason, emits no artifact or
  QASM, and never rewrites the meaning as a unitary.
- The Red tests were not changed. Direct Product/Tensor and unknown-family
  fail-closed harness checks pass; `py_compile` and `git diff --check` pass.
  Local pytest remains unavailable.
- Same-context reviewer disposition: **READY FOR ADJUDICATOR PHASE 2 REVIEW**.
  Continuous/open-system and Measurement remain intentionally unimplemented;
  Phase 3 and provider/real-QPU actions remain unapproved.

## LISS-0457 Phase 2 Green review finding

The Product/Tensor result shape and rejection envelope are bounded, and the
direct harness confirms the expected code, reason, source identity, and empty
artifact/QASM. However, the implementation classifies the program with a raw
source regular expression. It does not consume the source-derived Scientific
Semantic IR, so it violates the canonical semantic-authority invariant and can
classify text rather than meaning.

Disposition: **PHASE 2 REVIEW BLOCKED**. Phase 3 is not approved. The Green
slice must be corrected to consume the canonical Scientific Semantic IR and
then receive a repeat Phase 2 review. Continuous/open-system, Measurement,
provider, and real-QPU work remain out of scope.

## LISS-0457 corrected Phase 2 Green review

The source-text classifier was corrected in the same bounded Product/Tensor
slice. The implementation now calls the existing compiler pipeline and bases
classification on `scientific_semantic_ir` `meaning_kind` and child node kinds
(`OpLit` plus `OpPauli`). The reviewed Red tests remain unchanged, and no
provider, numerical method, artifact emission, or QPU operation was added.

Direct Product/Tensor verification passes, as do Python 3.14 `py_compile` and
`git diff --check`. Same-context reviewer disposition: **CORRECTED AND
REVIEWED; READY FOR PHASE 3 REVIEW APPROVAL**. Phase 3 has not been executed.

## LISS-0457 Phase 3 closeout review

The approved Phase 3 refactor extracts the Product/Tensor rejection decision
construction into a dedicated helper and formats the canonical IR traversal
for readability. The reviewed assertions and behavior are unchanged. Direct
Product verification, `py_compile`, and `git diff --check` pass; local pytest
remains unavailable.

Same-context reviewer disposition: **DONE for the bounded Product/Tensor
slice**. Continuous/open-system and Measurement remain deferred, and no
provider or real-QPU operation was performed.

### 変更の要約 (PR Summary)

- **何を目的として何を変更したか**: keep the reviewed Product/Tensor
  rejection contract readable while preserving canonical Scientific Semantic
  IR authority and artifact-free failure.

### 残存リスク・検証の溝 (Verification Gap)

- **AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
  full pytest remains a CI-only verification because pytest is unavailable
  locally.
- **人間がコードレビューで重点的に見るべきポイント**: confirm future
  family classifiers continue to consume canonical IR and do not broaden this
  bounded rejection slice into provider or numerical policy.

## LISS-0471 Measurement-family Phase 0 design review

The next family slice is split into LISS-0471 rather than reopening the done
Product/Tensor slice. Its scope is limited to source-derived terminal versus
dynamic measurement classification, existing dynamic capability rejection, and
no-artifact/no-QASM behavior. POVM/tomography, provider selection, numerical
methods, and live QPU execution are explicitly deferred.

Same-context design disposition: **READY FOR PHASE 1 RED SCOPE REVIEW**. No
Phase 1 tests or implementation have started.

## LISS-0458 Phase 1 Red review

- User approval: Phase 1 Red for LISS-0458, 2026-08-27.
- Test-only artifact: `tests/test_liss_0458_realization_artifact_contract_red.py`.
- The packet covers symbolic no-artifact rejection, explicit finite policy
  metadata/provenance, ordered duplicate instructions, invalid-policy atomic
  rejection, and stable canonical serialization/fingerprints.
- Red evidence: the intentionally absent
  `compiler.staqex.realization_artifact` module is confirmed absent. Python
  3.14 `py_compile` and `git diff --check` pass; pytest is unavailable
  locally.
- Reviewer disposition: **READY FOR ADJUDICATOR TEST REVIEW**. Phase 2 Green,
  new DTO acceptance, provider work, credentials, network access, and live
  QPU execution remain unapproved.

## LISS-0458 Phase 2 Green review

- User approved Phase 2 Green for LISS-0458 on 2026-08-27.
- Added the minimal provider-neutral realization/artifact contract and source
  identity propagation through Scientific Semantic IR. No provider SDK,
  allocation, payload, credentials, routing, or live-QPU behavior was added.
- The implementation validates finite plan fields, preserves canonical
  provenance and policy metadata, emits stable canonical bytes/fingerprints,
  and rejects without partial artifacts.
- The reviewed Red tests are unchanged. Plain Python Red contract execution,
  Python 3.14 `py_compile`, and `git diff --check` pass; pytest is unavailable
  locally.
- Reviewer disposition: **GREEN REVIEWED; READY FOR PHASE 3 REVIEW APPROVAL**.

## LISS-0460 Phase 3 closeout review

- User approved Phase 3 for LISS-0460 on 2026-08-28.
- Extracted shared measurement-aware artifact evidence construction for
  success/rejection paths. Reviewed tests and observable behavior remain
  unchanged.
- Re-read the acceptance spec, WP-0122, LISS-0460, target routing/capability
  contracts, and reviewed tests. No blocker was found within the bounded
  slice.
- LISS-0460 and existing target-routing integration tests pass (11 tests);
  Python 3.14 `py_compile` and `git diff --check` pass. Pytest remains
  unavailable locally.
- Isolation: `same_context`, weaker than `separate_context`.
- Process review found no operating-contract deviation or operational problem.
- Reviewer disposition: **DONE for the bounded target-neutral route/schedule
  evidence slice**. QASM, provider, credential, and live-QPU work remain
  separately gated.

## LISS-0459 Phase 3 closeout review

- User approved Phase 3 for LISS-0459 on 2026-08-28.
- Refactored the preflight implementation into capability/resource helpers and
  a shared append rule. Reviewed tests and observable behavior are unchanged.
- Re-read the acceptance spec, WP-0122, LISS-0459, target preflight and
  capability modules, and the reviewed tests. No blocker was found within the
  bounded slice.
- LISS-0459 and existing target-capability integration tests pass; Python 3.14
  `py_compile` and `git diff --check` pass. Pytest remains unavailable locally.
- Isolation: `same_context`, weaker than `separate_context`.
- Process review found no operating-contract deviation or operational problem.
- Reviewer disposition: **DONE for the bounded target capability preflight
  slice**. Routing, QASM, provider, credential, and live-QPU work remain
  separately gated.

## LISS-0460 Phase 1 Red review

- User approved Phase 1 Red for LISS-0460 on 2026-08-28.
- Test-only artifact: `tests/test_liss_0460_transpile_route_schedule_red.py`.
- The packet covers deterministic route/SWAP evidence, cost, measurement
  mapping, schedule depth/timing, logical identity, provenance, and atomic
  no-partial-artifact rejection.
- Red evidence: the existing `TargetPipelineResult` lacks the intentionally
  unimplemented `cost` field. Python 3.14 `py_compile` and `git diff --check`
  pass; pytest is unavailable locally.
- Reviewer disposition: **READY FOR ADJUDICATOR TEST REVIEW**. Phase 2 Green,
  provider-specific transpilers, calibration optimization, SDKs, credentials,
  network access, and live-QPU execution remain unapproved.

## LISS-0460 Phase 2 Green review

- User approved Phase 2 Green for LISS-0460 on 2026-08-28.
- Extended the target-neutral pipeline with cost evidence, measurement
  mapping, schedule depth/duration, and explicit atomic artifact safety fields.
  Legacy stage provenance remains compatible; no provider transpiler,
  calibration, SDK, credential, network, or live-QPU behavior was added.
- LISS-0460 and existing target-routing integration tests pass (11 tests);
  Python 3.14 `py_compile` and `git diff --check` pass. Pytest is unavailable
  locally.
- Reviewer disposition: **GREEN REVIEWED; READY FOR PHASE 3 REVIEW APPROVAL**.

## LISS-0458 Phase 3 closeout review

- User approved Phase 3 for LISS-0458 on 2026-08-28.
- Refactor separated semantic fingerprint from filesystem source identity and
  centralized rejection construction. Reviewed tests and behavior remain
  unchanged.
- Re-read canonical acceptance, WP-0121, LISS-0458, realization/artifact,
  Scientific Semantic IR, pipeline, and tests. No blocker was found within
  the bounded slice.
- LISS-0458, LISS-0449, and Scientific Semantic IR integration tests pass;
  Python 3.14 `py_compile` and `git diff --check` pass. Pytest remains
  unavailable locally.
- Isolation: `same_context`; weaker than `separate_context`.
- Reviewer disposition: **DONE for the bounded finite realization/artifact
  contract slice**. Provider, routing, credentials, and live-QPU work remain
  separately gated.

## LISS-0459 Phase 1 Red review

- User approved Phase 1 Red for LISS-0459 on 2026-08-28.
- Test-only artifact: `tests/test_liss_0459_target_capability_profile_red.py`.
- The packet covers synthetic profile version/provenance, declared-only
  calibration, all named target/resource dimensions, fail-closed
  allocation/artifact behavior, and the absence of physical execution claims.
- Red evidence: the intentionally absent `compiler.staqex.target_preflight`
  module is confirmed absent. Python 3.14 `py_compile` and `git diff --check`
  pass; pytest is unavailable locally.
- Reviewer disposition: **READY FOR ADJUDICATOR TEST REVIEW**. Phase 2 Green,
  provider queries, SDKs, credentials, network access, and live-QPU execution
  remain unapproved.

## LISS-0459 Phase 2 Green review

- User approved Phase 2 Green for LISS-0459 on 2026-08-28.
- Added `compiler/staqex/target_preflight.py` with provider-neutral synthetic
  capability profiles, resource demands, and pre-allocation decisions.
- The implementation preserves profile version/provenance, rejects all
  reviewed dimensions without allocation/artifact/provider payload, and
  keeps physical execution claims false. Provider queries, SDKs, credentials,
  network access, and live QPU execution were not added.
- LISS-0459 and existing target-capability integration tests pass; Python 3.14
  `py_compile` and `git diff --check` pass. Pytest is unavailable locally.
- Reviewer disposition: **GREEN REVIEWED; READY FOR PHASE 3 REVIEW APPROVAL**.

## LISS-0472 Phase 1 Red review

- User approval: Phase 1 Red for LISS-0472, 2026-08-27.
- Branch: `codex/liss-0472-continuous-open-system-qpu-readiness`.
- Test-only artifact: `tests/test_liss_0472_continuous_open_system_qpu_readiness_red.py`.
- The packet covers canonical continuous/open-system identity, explicit
  discretization requirement, no artifact/QASM/allocation/provider mapping,
  and non-physical CPU/Simulator evidence. Existing CPU numerical tests are
  not duplicated.
- Red evidence: the intentionally absent
  `compiler.staqex.continuous_open_system_readiness` module is confirmed
  absent. Python 3.14 `py_compile` and `git diff --check` pass; local pytest
  is unavailable.
- Reviewer disposition: **READY FOR ADJUDICATOR TEST REVIEW**. Phase 2 Green,
  numerical methods, provider work, credentials, network access, and
  real-QPU execution remain unapproved.

## LISS-0472 Phase 1 Red test review

The Continuous/Open-system Red packet was re-read against the accepted
discretization, density/CPTP/Lindblad, and real-QPU contracts. It keeps CPU /
Simulator evidence separate from physical-QPU evidence, requires explicit
finiteization, checks no artifact/QASM/allocation/provider mapping, and retains
source identity. Existing numerical-lowering tests are not duplicated.

Same-context reviewer disposition: **TESTS REVIEWED; READY FOR PHASE 2 GREEN
APPROVAL**. The reviewed tests must remain unchanged. Phase 2 is limited to
the canonical deferral classifier; numerical methods, providers, and live QPU
work remain unapproved.

## LISS-0472 Phase 2 Green review

- User approval: Phase 2 Green for the Continuous/Open-system deferral slice,
  2026-08-27.
- Production artifact: `compiler/staqex/continuous_open_system_readiness.py`.
- The classifier consumes compiler-derived Scientific Semantic IR and existing
  mixed-state contracts, preserves density/channel/Lindblad meaning, and
  defers QPU realization without inferred discretization, numerical method,
  error tolerance, artifact, QASM, allocation, or provider mapping.
- The Red tests were not changed. B12 classification, explicit deferral,
  non-physical evidence, and empty-artifact checks pass; `py_compile` and
  `git diff --check` pass. Local pytest is unavailable.
- Same-context reviewer disposition: **READY FOR ADJUDICATOR PHASE 2 REVIEW**.
  Phase 3, numerical methods, provider work, and real-QPU execution remain
  unapproved.

## LISS-0472 Phase 3 closeout review

The approved refactor extracts deferred-decision construction into a focused
helper. Canonical IR classification, simulator evidence labeling, no-artifact
fields, and reviewed behavior remain unchanged. B12 classification and
explicit deferral checks pass, as do `py_compile` and `git diff --check`.

Same-context reviewer disposition: **DONE for the bounded Continuous/Open-
system deferral slice**. Process review found no operating-contract deviation
or operational problem. Numerical methods, finite encoding, Provider, and
real-QPU realization remain separately gated.

### 変更の要約 (PR Summary)

- **何を目的として何を変更したか**: improve deferred-decision generation
  readability while preserving canonical meaning and non-physical evidence.

### 残存リスク・検証の溝 (Verification Gap)

- **AIが推測で補った部分、またはハルシネーションが発生しやすい箇所**:
  full pytest remains a CI-only check because pytest is unavailable locally.
- **人間がコードレビューで重点的に見るべきポイント**: ensure future
  continuous realization requires explicit discretization and never treats
  simulator evidence as physical-QPU evidence.

Human approval record: the Adjudicator approved the reviewed LISS-0472 Phase 2
Green slice on 2026-08-27. Phase 3 remains a separate approval gate.

## LISS-0472 Phase 1 Red test review

The test-only packet was re-read against the continuous discretization,
density/CPTP/Lindblad, and real-QPU acceptance contracts. It separates
CPU/Simulator evidence from QPU evidence, requires explicit finiteization,
checks no artifact/QASM/allocation/provider mapping, and preserves canonical
meaning identity and provenance. Existing CPU numerical tests are not
duplicated.

Same-context reviewer disposition: **TESTS REVIEWED; READY FOR PHASE 2 GREEN
APPROVAL**. The reviewed tests must remain unchanged. Phase 2 is limited to
the canonical continuous/open-system deferral classifier; numerical methods,
providers, and live QPU work remain unapproved.

## LISS-0472 Continuous/Open-system Phase 0 design review

The next family slice is split into LISS-0472. Its scope is limited to
canonical-IR classification of continuous/open-system meaning and fail-closed
QPU readiness when an authorized finite discretization is absent. Existing CPU
RK4/grid evidence is not treated as physical-QPU evidence. Numerical methods,
error bounds, finite encoding, provider mapping, and live QPU execution are
deferred.

Same-context design disposition: **READY FOR PHASE 1 RED SCOPE REVIEW**. No
Phase 1 tests or implementation have started.

## LISS-0471 Phase 1 Red review

- User approval: Phase 1 Red for LISS-0471, 2026-08-27.
- Branch: `codex/liss-0471-measurement-family-qpu-readiness`.
- Test-only artifact: `tests/test_liss_0471_measurement_family_readiness_red.py`.
- The packet covers static terminal versus dynamic measurement lane identity,
  source provenance, existing dynamic capability diagnostics with empty
  artifact/QASM, and explicit POVM/Tomography deferral. Existing low-level
  dynamic-lane tests are reused as evidence rather than duplicated.
- Red evidence: the intentionally absent
  `compiler.staqex.measurement_family_readiness` module is confirmed absent.
  Python 3.14 `py_compile` and `git diff --check` pass; local pytest is not
  installed.
- Reviewer disposition: **READY FOR ADJUDICATOR TEST REVIEW**. Phase 2 Green,
  provider work, credentials, network access, and real-QPU execution remain
  unapproved.
