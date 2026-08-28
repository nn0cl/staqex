# LISS-0464: Credential and device configuration boundary

| Field | Value |
|---|---|
| Status | **done — Phase 3 refactor complete** |
| Phase | phase-3-refactor |
| Type | security / Host contract |
| Priority | P0 |
| Initial size | L |
| Current size | L |
| Owner | Host delivery boundary |
| Parent | WP-0119; WP-0123 |
| Depends on | LISS-0459, LISS-0463 |
| Blocks | LISS-0465, LISS-0466 |
| Branch | `codex/liss-0464-credential-config-boundary` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0464--credential-and-device-configuration) |
| Implementation permission | None |
| Post-review requirement | Security review and typed Phase 1 approval |

Specify configuration precedence for provider, region, device, shots, timeout,
and cost guard; environment/config separation; secret redaction; error
messages; credential lifetime; and audit fields. Credentials must never enter
source, semantic IR, artifacts, logs, or tests. Missing or invalid credentials
must fail closed before submit.
## Design detail

**In:** provider/region/device/shots/timeout/cost configuration, precedence,
environment versus config files, secret redaction, audit fields, and credential
lifetime. **Out:** secrets in repository/tests/traces, source-level provider
imports, and autonomous submission.

**Acceptance:** missing/invalid credentials and device configuration fail before
submit; precedence is deterministic; logs/errors/artifacts contain no secret;
dry-run/check cannot submit; cost and shot limits are enforced before network
work.

**Phase/evidence:** Phase 0 security contract; Phase 1 Red redaction/preflight
tests; Phase 2 Host configuration implementation; Phase 3 review with injected
fake credentials only. Planning record:
`AIP-LISS-0464-2026-08-27-001` (L; N/A model metrics).

## Phase 1 Red artifact

- Added `tests/test_liss_0464_credential_config_boundary_red.py`.
- The test-only contract covers deterministic precedence, missing/invalid
  credential and device rejection, shots/timeout/cost guards before network
  work, dry-run non-submission, redacted audit output, and conflicting-source
  rejection without exposing configuration values.
- No secret values are present in tests or fixtures. Red is confirmed by the
  intentionally absent `compiler.staqex.host_configuration` module.
- Phase 2 Host configuration implementation, credentials, network access, and
  live submission remain unapproved.

## Phase 2 Green artifact

- Added `compiler/staqex/host_configuration.py` with deterministic
  environment/config/default precedence and provider-neutral preflight results.
- Missing credential state, invalid device/resource limits, and conflicting
  sources reject before network work. Dry-run/check modes never submit, and
  audit fields expose no secret values.
- LISS-0464 contract tests, Python 3.14 `py_compile`, and
  `git diff --check` pass. No real environment, credential, network, or
  provider was accessed. Phase 3 security review remains separately gated.

## Phase 3 closeout

- Extracted configuration diagnostics and redacted audit-field construction
  into focused helpers without changing validation order or outcomes.
- LISS-0464 contract tests, Python 3.14 `py_compile`, and
  `git diff --check` pass. No real environment, credential, network, or
  provider was accessed.
- Same-context security review found no blocker within the provider-neutral
  preflight slice; this isolation is weaker than separate-context review.
- Process review: no operating-contract deviation or operational problem
  found.
- Provider credentials, network access, live submission, and production
  configuration loading remain separately gated.
