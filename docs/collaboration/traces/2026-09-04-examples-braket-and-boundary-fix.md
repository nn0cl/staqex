# AI Work Trace: examples, lane boundaries, and AWS Braket delivery

## Request

- Date: 2026-09-04
- User request: Review and fix official examples, then implement the user-facing AWS Braket deployment path without running a real-device test.
- Current phase: Feature implementation and refactor/verification under the accepted AWS Braket adapter ADRs.
- Canonical issue or work plan: ADR 0202/0203; `staqex-real-qpu-readiness-acceptance.md`; no new issue created because the requested scope is an explicit continuation of the accepted adapter boundary.
- AI planning record: Design intake in the session commentary; existing ADR design records are authoritative.

## Context Ledger

- Included: official `.sqx` examples, example READMEs, `aws_braket` Host adapter, live-QPU CLI, provider-neutral QPU ports, accepted AWS Braket/QPU specifications, offline tests.
- Omitted: AWS credentials, provider account data, real QPU submission, unrelated legacy test failures, Rust implementation.
- Assumptions: AWS Braket remains the explicitly selected provider; `amazon-braket-sdk` remains optional and lazy-loaded.
- Open decisions: Dynamic OpenQASM3 support remains device/profile dependent and was not exercised against AWS.

## Routing

- Model/assistant/tool: Host agent with deterministic shell, pytest, spec verification, and official AWS documentation lookup.
- Reason: provider boundary and example correctness require repository evidence; no AI-generated runtime data is involved.
- Privacy constraints: no credentials or provider payloads were accessed or recorded.

## AI Execution Records

### Attempt 1

- Agent: host agent
- Environment: local repository `/Users/nn0cl/Documents/git/qpex`
- Model as displayed: N/A
- Reasoning setting as displayed: N/A
- Estimated token range: N/A
- Estimated token midpoint: N/A
- Actual tokens: N/A
- Token metric: N/A
- Token source: N/A
- Token attribution boundary: N/A
- Actual token unavailable reason: host telemetry is not exposed to the repository trace.
- Estimate variance: N/A
- Variance reason: N/A
- Scope: example review, offline Braket adapter compatibility, A04 repair, lane/documentation alignment.
- Result: completed; no real AWS call made.
- Attempt boundary: one cohesive implementation and verification run.
- Notes: initial spec verification was 98.73%; after the A04 and boundary corrections it was 100.00% (161/161).

## Cost / Reasoning Control

- Operating path: Architecture/Feature Path with same-context review constraints.
- Files read: quickstart, readiness, project conventions, language/QPU specifications, ADR 0202/0203, touched adapter/CLI/examples/tests.
- Context intentionally omitted: secrets, account configuration, real provider state, unrelated historical records.
- Deterministic checks used: targeted pytest, all spec verification, all example entrypoint checks, QASM emission, CLI help, diff check.
- Escalation reason: none; real provider execution was explicitly omitted.
- Avoided LLM work: no generated code was accepted without local tests and source inspection.
- Rework caused by AI output: none.

## Adjudicator Decisions

- AWS Braket is the selected deployment provider under ADR 0202.
- Real-device tests are not required for this task and were not run.

## Verification

- `pytest` targeted Braket/A04 tests: 19 passed.
- `tests/spec_verification/run_all.py`: 161/161, 100.00%, Gate PASS.
- All 31 example `main_*.sqx` entrypoints: check passed.
- Bell-pair `emit-qasm`: OpenQASM3 with `h`, `cx`, and terminal measure.
- `git diff --check`: passed.
- Full pytest: interrupted after existing unrelated migration/runtime failures; 842 passed before interruption, with 13 pre-existing failures observed outside this change's targeted scope.

## Changed Files

- `compiler/staqex/adapters/aws_braket.py`
- `examples/README.md`
- `examples/applied/A04_hp_protein_folding/main_hp_protein_folding.sqx`
- `examples/applied/A10_mission_observatory/main_mission_observatory.sqx`
- `examples/basics/B18_finiteize/README.md`
- `examples/host/live_qpu_braket_demo/README.md`
- `examples/showcase/S02_drug_discovery/main_selection.sqx`
- `tests/test_liss_0392_aws_braket_adapter_red.py`

## Next Safe Action

User may install `amazon-braket-sdk>=1.117.0`, configure AWS credentials through the standard SDK chain, and run the documented commands manually. The agent must not perform the real submission.

## Notes

The live path remains separated from the local synchronous `submit_source` path. Provider-specific behavior is confined to the Host adapter; the Kernel and QASM remain provider-neutral.
