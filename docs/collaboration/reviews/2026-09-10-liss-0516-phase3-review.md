# Review Summary: LISS-0516 AWS Braket Phase 3 — Re-review 3

## Review packet

- Scope: Phase 3 readability, boundary, compatibility, and deterministic
  verification review for the AWS Braket fan-out implementation.
- Canonical documents: LISS-0516, WP-0133, the accepted multi-provider QPU
  contract, ADR 0217, and the Phase 2 Green review.
- Changed implementation re-read: `compiler/staqex/adapters/aws_braket.py`.
- Isolation: `same_context`; weaker than `separate_context`.

## Initial findings and correction

- **F1 — resolved:** The initial review found that `AwsBraketAdapter.status()`
  mapped
  every unmapped provider state to `ProviderJobState.RUNNING`. The same legacy
  projection is used by `wait()` and `cancel()`. This violates ADR 0217's
  fail-closed rule that an unknown state must never be guessed as queued,
  running, or failed. `status_observation()` is correct, but existing
  `QpuJobPort` consumers can still reach the unsafe projection.
- The correction adds `BraketUnknownJobStateError`, makes the legacy projection
  fail closed, and adds a regression assertion through `status()`.
- **F2 — resolved:** `RealAwsBraketClient` now implements
  `device_capabilities()` through the lazy `AwsDevice` boundary. It maps
  provider name, device status, ARN, and the OpenQASM action's supported
  operations into the adapter's snapshot shape. A concrete-client surface
  regression assertion was added without installing the SDK.
- The implementation is otherwise readable and keeps SDK access lazy,
  credentials in the existing Host credential port, and provider conversion
  outside Kernel code.

## Verification

- Fan-out Phase 2 Green runner — passed.
- Existing AWS adapter runner — passed.
- Provider-neutral contract runner — passed.
- `py_compile` — passed.
- Document lifecycle check — passed.
- `git diff --check` — passed.
- No SDK installation, credentials, network call, or real-QPU submission.

## Disposition

- **Phase 3 accepted after correction.** F1 and F2 are resolved. The adapter
  now has a complete fake and concrete-client method surface while retaining
  lazy SDK loading and no live call in verification.
- Live AWS integration remains separately gated.

## Evidence links

- Canonical Register: `docs/architecture/open-work-register.md`
- Representative Trace: `docs/collaboration/traces/2026-09-10-multi-provider-qpu-wp-plan.md`
- Implementation: `compiler/staqex/adapters/aws_braket.py`
- Tests: `tests/test_liss_0516_aws_braket_fanout_red.py`
