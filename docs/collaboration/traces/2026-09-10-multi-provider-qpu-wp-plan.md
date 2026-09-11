# AI Work Trace

## Request

- Date: 2026-09-10
- User request: Create work plans for IBM Quantum, AWS Braket, Azure Quantum,
  Google Quantum Computing Service, and direct provider routes.
- Current phase: Architecture Path design planning and Luna-readiness refinement
- Canonical issue or work plan: WP-0119; new WP-0131–WP-0136
- AI planning record: AIP-WP-0131-2026-09-10-001

## Context Ledger

- Included: project conventions, quickstart, design-intake, process lessons,
  real-QPU readiness specification, hybrid workflow, QPU/external-port
  decision, testing strategy, and existing WP-0119–0126.
- Omitted: secrets, provider accounts, raw logs, and unrelated source.
- Assumptions: user requested planning artifacts only; no provider or device is
  selected yet; existing AWS hardening is not reopened.
- Open decisions: first device, SDK/API route, cost ceiling, and live-pilot
  authorization per platform; no repository-wide model routing change.

## Routing

- Model/assistant/tool: host agent plus deterministic repository inspection.
- Reason: cross-provider architecture and technology boundary.
- Privacy constraints: no credentials or private provider data included.

## AI Execution Records

### Attempt 1

- Agent: Codex host agent
- Environment: local repository
- Model as displayed: unavailable
- Reasoning setting as displayed: unavailable
- Estimated token range: 2,000–4,000
- Actual tokens: unavailable
- Scope: inspect existing work plans and create provider-route planning records.
- Result: WP-0131–WP-0136 created; implementation not authorized.
- Attempt boundary: documentation-only planning.
- Notes: Existing WP-0123–0126 remain canonical for common readiness and pilot
  controls.

### Attempt 2

- Agent: Codex host agent
- Environment: local repository
- Model as displayed: unavailable
- Reasoning setting as displayed: unavailable
- Estimated token range: 4,000–7,000
- Actual tokens: unavailable
- Scope: review WP-0131–WP-0136 and make each executable by Luna as a bounded
  one-Issue, one-phase task.
- Result: review findings recorded; LISS-0514–LISS-0519 and Luna execution
  packets added; implementation and provider calls remain gated.
- Attempt boundary: documentation-only planning and readiness review.
- Notes: Luna is named per task; `runtime-routing.toml` was intentionally not
  changed because a global implementation-model decision was not requested.

### Attempt 3

- Agent: Codex host agent
- Environment: local repository
- Model as displayed: unavailable
- Reasoning setting as displayed: unavailable
- Estimated token range: 3,000–5,000
- Actual tokens: unavailable
- Scope: execute LISS-0514 Phase 0 common QPU contract design.
- Result: proposed common execution-contract specification created; no code,
  tests, SDK installation, network, credentials, or real-QPU calls.
- Attempt boundary: Phase 0 design only.
- Notes: current register confirms AWS adapter, submit CLI, job-port CLI, and
  demo are complete; AWS work remains gap analysis only.

### Attempt 4

- Agent: Codex host agent
- Environment: local repository
- Model as displayed: unavailable
- Reasoning setting as displayed: unavailable
- Scope: apply the approved separation between provider credentials and
  per-run human approval.
- Result: added the proposed `HostSubmissionApproval` record, kept credentials
  in Host config/credential chain, and resolved review finding F-02.
- Attempt boundary: architecture document update only; no implementation,
  credentials, SDK, network, or real-QPU call.

## Cost / Reasoning Control

- Operating path: Architecture Path
- Files read: listed in Context Ledger
- Context intentionally omitted: credentials, private accounts, raw provider
  payloads, and unrelated source.
- Deterministic checks used: ID inventory and existing WP inspection.
- Escalation reason: provider and route choices affect architecture.
- Avoided LLM work: no provider SDK code or implementation was generated.
- Rework caused by AI output: none.

## Verification

- Commands/checks: `rg` inventory of WP IDs and inspection of WP-0119–0126.
- Result: no duplicate WP IDs detected before creation; no runtime tests run.

## Changed Files

- `docs/work-plans/WP-0131-multi-provider-real-qpu-connectivity.md`
- `docs/work-plans/WP-0132-ibm-quantum-real-qpu.md`
- `docs/work-plans/WP-0133-aws-braket-provider-fanout.md`
- `docs/work-plans/WP-0134-azure-quantum-provider-fanout.md`
- `docs/work-plans/WP-0135-google-quantum-computing-service.md`
- `docs/work-plans/WP-0136-direct-provider-parity.md`
- `docs/issues/LISS-0514-multi-provider-qpu-contract-readiness.md`
- `docs/issues/LISS-0515-ibm-quantum-route-selection.md`
- `docs/issues/LISS-0516-aws-braket-fanout-gap-analysis.md`
- `docs/issues/LISS-0517-azure-quantum-route-selection.md`
- `docs/issues/LISS-0518-google-qcs-access-and-route-selection.md`
- `docs/issues/LISS-0519-direct-provider-parity-decision.md`
- `docs/collaboration/reviews/2026-09-10-wp-0131-0136-luna-readiness-review.md`
- `docs/specs/staqex-multi-provider-qpu-execution-contract.md`
- `docs/collaboration/reviews/2026-09-10-liss-0514-architecture-review.md`
- `docs/collaboration/traces/2026-09-10-multi-provider-qpu-wp-plan.md`

### Attempt 5

- Agent: Codex host agent
- Environment: local repository
- Scope: formalize lifecycle observation and capability freshness decisions.
- Result: updated the proposed execution contract, added proposed ADR 0217,
  and synchronized LISS-0514's architecture review. No code, tests, SDK,
  credentials, network, or real-QPU call.
- Attempt boundary: Architecture document formalization only.

## Next Safe Action

### Attempt 6

- Agent: Codex host agent
- Environment: local repository
- Scope: record typed Architecture approval and synchronize Phase 0 status.
- Result: ADR 0217 and the execution contract were marked accepted; LISS-0514
  and the review now await separate Phase 1 Red approval. No implementation.

## Next Safe Action

### Attempt 7

- Agent: Codex host agent
- Environment: local repository
- Scope: execute approved LISS-0514 Phase 1 Red.
- Result: added five fake/provider-neutral contract tests. The test script
  failed at the intentionally absent `compiler.staqex.qpu_contract` module,
  confirming Red. No production code or provider access.
- Attempt boundary: Phase 1 Red only.

### Attempt 8

- Agent: Codex host agent
- Environment: local repository
- Scope: execute approved LISS-0514 Phase 2 Green.
- Result: added the minimum provider-neutral lifecycle/capability contract
  module. The unchanged five-test suite passes through its direct script
  runner. No provider SDK, credentials, network, or real-QPU call.
- Attempt boundary: Phase 2 Green only.

## Next Safe Action

Adjudicator reviews the Green implementation. Phase 3 refactoring and provider
integration remain separately gated.

### Attempt 9

- Agent: Codex host agent in reviewer role
- Environment: local repository; same_context isolation
- Scope: Phase 2 Green review after re-reading the spec, ADR, implementation,
  tests, and deterministic output.
- Result: review packet recorded blockers F1 (spec status drift) and F2
  (capability identity/required-capability enforcement incomplete). No
  implementation changes were made during review.
- Verification: direct test runner, `py_compile`, `git diff --check`, and
  document lifecycle check passed; pytest unavailable.

## Next Safe Action

Correct F1–F2, rerun the scoped tests, and request a fresh Phase 2 Green
review. Phase 3 remains gated.

### Attempt 10

- Agent: Codex host agent in reviewer role
- Environment: local repository; same_context isolation
- Scope: re-review the F1–F2 correction.
- Result: F1 status synchronization and F2 capability identity/requirement
  checks are resolved. Found F3: the two new correction tests are omitted from
  the direct-runner list, so complete Green evidence is not yet available. No
  implementation changes were made during review.
- Next safe action: add the two tests to the runner, rerun the full scoped
  suite, and repeat Phase 2 Green review.

### Attempt 11

- Agent: Codex host agent in reviewer role
- Environment: local repository; same_context isolation
- Scope: re-review after the F3 test-runner correction.
- Result: all seven scoped tests are now executed and pass. F1–F3 are
  resolved; no blockers remain within Phase 2. No provider access.
- Verification: direct test runner, `py_compile`, `git diff --check`, and
  document lifecycle check passed; pytest unavailable.

## Next Safe Action

Request typed Phase 3 approval. Provider integration and live execution remain
separately gated.

### Attempt 12

- Agent: Codex host agent in reviewer role
- Environment: local repository; same_context isolation
- Scope: Phase 3 refactor and review.
- Result: extracted named helpers for state normalization, terminal detection,
  and identity matching. Seven scoped tests remained Green; Phase 3 review
  found no blockers within LISS-0514.
- Verification: direct test runner, `py_compile`, `git diff --check`, and
  document lifecycle check passed; pytest unavailable.

## Next Safe Action

Begin provider-specific Phase 0/technology review. No provider SDK or live QPU
submission is authorized by this slice.

### Attempt 13

- Agent: Codex host agent
- Environment: local repository
- Scope: provider Phase 0 / technology-selection review for WP-0132–0136.
- Result: reviewed official IBM, AWS, Azure, Google, IonQ, Rigetti, and QuEra
  documentation. Recommended IBM Runtime, AWS Braket reuse, Azure QIR v1,
  Google offline Cirq/Engine, and defer all direct routes pending a demonstrated
  gap. No SDK installation, credentials, network call, or provider selection
  was performed.
- Verification: source URLs and capture date recorded in the review packet;
  no runtime tests applicable.

## Next Safe Action

Request typed technology-selection approval for the recommended route set.

### Attempt 14

- Agent: Codex host agent
- Environment: local repository
- Scope: record typed technology-selection approval.
- Result: approved AWS Braket reuse/OpenQASM 3, IBM Runtime, Azure Quantum
  Job API/QIR v1, and Google Cirq/Engine offline route. Direct Quantinuum,
  IonQ, Rigetti, and QuEra routes remain deferred. SDK installation and live
  execution remain separately gated.
- Verification: status synchronization and document lifecycle checks.

## Next Safe Action

Request provider-specific Phase 1 Red approval, starting with the AWS Braket
fan-out gap analysis or IBM route adapter contract. No SDK installation or live
provider call is authorized yet.

### Attempt 15

- Agent: Codex host agent
- Environment: local repository
- Scope: execute approved LISS-0516 AWS Braket fan-out Phase 1 Red.
- Result: added three fake-client gap tests for raw lifecycle preservation and
  route/provider/device capability separation. The direct runner fails at the
  intentionally absent `status_observation` method, confirming Red.
- Verification: test-only `py_compile` and `git diff --check` passed; no SDK,
  credentials, network, or real submission.

## Next Safe Action

Adjudicator reviews the AWS fan-out Red tests. Phase 2 implementation requires
a separate typed approval.

### Attempt 16

- Agent: Codex host agent in reviewer role
- Environment: local repository; same_context isolation
- Scope: review LISS-0516 AWS Braket Phase 1 Red.
- Result: fake-client scope and genuine adapter gaps are valid, but F1 blocks
  acceptance because the direct runner stops at the first missing method and
  does not prove all three tests fail.
- Verification: `py_compile` and `git diff --check` passed; no provider access.

## Next Safe Action

Correct the direct test runner to report all three failures, rerun it, and
repeat the Phase 1 Red review.

### Attempt 17

- Agent: Codex host agent in implementation and reviewer role
- Environment: local repository; same_context isolation
- Scope: correct the LISS-0516 Phase 1 Red direct runner and repeat review.
- Result: runner now aggregates all failures. All three approved fake-client
  tests fail for the intended missing `status_observation` or
  `capability_profile` adapter methods. Phase 1 Red review accepted.
- Verification: `py_compile`, direct runner, document lifecycle check, and
  `git diff --check` passed; no SDK, credentials, network, or provider call.

## Next Safe Action

Request separate typed Phase 2 approval for the minimum AWS Braket adapter
implementation. Do not install SDKs or connect to a real provider.

### Attempt 18

- Agent: Codex host agent in implementation role
- Environment: local repository; host implementation isolation
- Scope: execute the explicitly authorized LISS-0516 Phase 2 minimum
  implementation.
- Result: added Braket raw lifecycle observation and TTL-bound capability
  profile translation using provider-neutral Host contracts. The fan-out
  tests and existing AWS fake-adapter tests are Green.
- Verification: direct runners, `py_compile`, document lifecycle check, and
  `git diff --check` passed; no SDK, credentials, network, or provider call.

## Next Safe Action

Perform the separate Phase 2 Green review. Do not begin Phase 3 refactoring or
live AWS integration before its approval.

### Attempt 19

- Agent: Codex host agent in reviewer role
- Environment: local repository; same_context isolation
- Scope: review LISS-0516 AWS Braket Phase 2 Green implementation.
- Result: no blockers. Lifecycle observation, capability-profile separation,
  existing AWS behavior, and provider-neutral contract compatibility all
  passed review.
- Verification: fan-out, existing AWS, and common contract direct runners;
  `py_compile`, document lifecycle check, and `git diff --check` passed. No
  SDK, credentials, network, or provider call.

## Next Safe Action

Request typed Phase 3 approval for the AWS adapter readability/import-boundary
review. Keep live AWS integration separately gated.

### Attempt 20

- Agent: Codex host agent in reviewer role
- Environment: local repository; same_context isolation
- Scope: review LISS-0516 AWS Braket Phase 3.
- Result: F1 blocks acceptance. The legacy `status()`/`wait()`/`cancel()` path
  still guesses an unmapped provider state as `RUNNING`, contrary to ADR 0217,
  although the new `status_observation()` path is correct.
- Verification: fan-out, existing AWS, and common contract runners; compile,
  lifecycle, and diff checks passed. No provider access.

## Next Safe Action

Correct the legacy unknown-state projection, add its regression assertion, and
repeat the Phase 3 review. Do not start live AWS integration.

### Attempt 21

- Agent: Codex host agent in implementation and reviewer role
- Environment: local repository; same_context isolation
- Scope: correct the LISS-0516 Phase 3 F1 and repeat the review.
- Result: legacy `status()` now raises a typed fail-closed exception for an
  unmapped state; a regression test covers the legacy entry point. Phase 3
  re-review accepted the implementation.
- Verification: fan-out, existing AWS, and common contract runners; compile,
  lifecycle, and diff checks passed. No provider access.

### Attempt 22

- Agent: Codex host agent in audit/reviewer role
- Environment: local repository; same_context isolation
- Scope: independent recheck of the LISS-0516 Phase 3 acceptance.
- Result: F2 blocks acceptance. The new `BraketClientPort.device_capabilities`
  requirement is implemented by the fake only; `RealAwsBraketClient` lacks
  the method, so the real capability-profile path is incomplete.
- Verification: source inventory and all local direct runners/compile,
  lifecycle, and diff checks; no SDK or provider access.

## Next Safe Action

Resolve the concrete-client capability boundary under the approved SDK/live
access constraints, add a concrete-surface regression check, and repeat the
Phase 3 review. Do not start a real-QPU pilot.

### Attempt 23

- Agent: Codex host agent in implementation and reviewer role
- Environment: local repository; same_context isolation
- Scope: resolve LISS-0516 F2 and repeat Phase 3 review.
- Result: implemented `RealAwsBraketClient.device_capabilities()` through the
  lazy SDK boundary, added a concrete method-surface regression assertion, and
  accepted Phase 3 after re-review.
- Verification: fan-out, existing AWS, and common contract runners; compile,
  lifecycle, and diff checks passed. No SDK installation or provider call.

## Next Safe Action

Prepare a bounded real-QPU pilot review. Require explicit human target,
shots, cost ceiling, credential, and submission approval before any live call.

### Attempt 24

- Agent: Codex host agent in architecture/implementation role
- Environment: local repository; Host CLI boundary
- Scope: move AWS live-submit settings into runtime config and add interactive
  pre-submit approval.
- Result: added non-secret TOML loading with CLI override support, positive
  shots/cost validation, and `y`/`yes` confirmation immediately before
  adapter construction/submission. Added config, denial, and acceptance tests.
- Verification: LISS-0396, LISS-0516, LISS-0392 direct runners;
  `py_compile`, lifecycle, and diff checks passed. No SDK, credentials,
  network, or provider call.

## Next Safe Action

Obtain human pilot inputs and typed real-run approval. The agent must not
invoke the live command or provider itself.

### Attempt 25

- Agent: Codex host agent in architecture/design role
- Environment: local repository; same_context routing
- Scope: review Runtime/provider credential boundary and artifact naming after
  adopting `.sqxa` as the only artifact extension.
- Finding: ADR 0218 already covers Host config, provider credential chains,
  and interactive approval. Existing WP-0121/0122 cover in-memory and
  target-neutral contracts but do not define serialized portable versus
  target-resolved `.sqxa` variants.
- Result: did not reopen completed WPs. Added proposed ADR 0219, LISS-0542,
  and WP-0159 for the `.sqxa` packaging/target-build boundary; the associated
  Issue is LISS-0542.
- Verification: document/link inventory and `git diff --check`; no
  implementation, SDK installation, credentials, network, or live provider
  call.

## Next Safe Action

Request typed Architecture approval for ADR 0219, then typed Phase 1 approval
for LISS-0542 before writing artifact serialization or Runtime loader code.

### Attempt 26

- Agent: Codex host agent in Host-runtime smoke-test role
- Environment: isolated `/private/tmp/staqex-aws-sdk-smoke-20260910` venv
- Scope: install the approved AWS Braket SDK range and verify the execution
  path up to, but not including, provider submission.
- Result: installed `amazon-braket-sdk==1.127.0`; `AwsDevice`,
  `AwsQuantumTask`, and `RealAwsBraketClient` imported/constructed; CLI reached
  the resolved target/shots/cost prompt and cancelled on `n` before adapter
  submission. `pip check` reported no broken requirements.
- Safety: no repository/global Python dependency was changed; no credentials,
  provider API, device capability request, S3 operation, or billed task was
  performed.

### Attempt 28

- Agent: Codex host agent in Phase 1 Red role
- Scope: execute the `.sqxa`-only Phase 1 Red boundary after Architecture
  approval.
- Result: added `tests/test_liss_0542_sqxa_target_build_red.py`. The direct
  runner fails at the intentionally absent `compiler.staqex.sqxa` module;
  the test file itself passes `py_compile`.
- Verification: `git diff --check` and document lifecycle check passed. No
  production implementation, SDK, credentials, provider network, or live
  submission was used.

## Next Safe Action

Request typed Phase 1 Red review/approval for LISS-0542. Do not implement the
`.sqxa` writer/reader or Runtime loader until that approval is received.

### Attempt 29

- Agent: Codex host agent in same-context reviewer role
- Scope: review LISS-0542 Phase 1 Red tests after human review/approval request.
- Result: changes requested. The test packet lacks target metadata assertions,
  capability-expiry rejection, and observable provider non-contact before
  Runtime acceptance; the direct runner also uses a shared temporary path.
- Verification: re-read ADR 0217/0218, ADR 0219, LISS-0542, WP-0159, and the
  Red test; `py_compile`, `git diff --check`, and document lifecycle checks
  passed. No implementation or provider access.
- Next gate: correct only the Phase 1 tests, repeat review, then request typed
  Phase 1 Red approval. Phase 2 remains unauthorized.

### Attempt 30

- Agent: Codex host agent in same-context reviewer role
- Scope: re-review corrected LISS-0542 Phase 1 Red tests.
- Result: F1–F4 resolved; Phase 1 Red accepted. Issue/WP/review packet status
  synchronized. Phase 2 remains separately gated.
- Verification: `py_compile`, `git diff --check`, and document lifecycle check
  passed; direct runner remains intentionally Red at the absent production
  `compiler.staqex.sqxa` module. No provider access.

### Attempt 27

- Agent: Codex host agent in Phase 1 Red role
- Scope: apply the approved `.sqxa`-only architecture and define the first
  offline serialization/target-build contract tests.
- Result: ADR 0219 marked accepted; added LISS-0542 Phase 1 Red tests and
  synchronized WP-0159/LISS-0542 statuses. `.qpa` remains retired.
- Verification: Phase 1 direct runner is expected Red because the production
  `compiler.staqex.sqxa` module is intentionally absent; no SDK, credentials,
  provider network, or live submission used.
