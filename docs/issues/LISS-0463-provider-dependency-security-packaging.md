# LISS-0463: Provider SDK dependency and security packaging

| Field | Value |
|---|---|
| Status | **done — Phase 3 refactor complete** |
| Phase | phase-3-refactor |
| Type | technology / dependency |
| Priority | P0 |
| Initial size | M |
| Current size | M |
| Owner | Host adapter |
| Parent | WP-0119; WP-0123; ADR 0202 |
| Depends on | LISS-0461, LISS-0462 |
| Blocks | LISS-0464, LISS-0465 |
| Branch | `codex/liss-0463-provider-dependency-packaging` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0463--dependency-and-packaging-isolation) |
| Implementation permission | None |
| Post-review requirement | Technology/security review and typed Phase 1 approval |

For the already selected AWS Braket path, verify the approved SDK range,
vulnerability posture, optional/lazy import behavior, installation and
troubleshooting path, and minimal real-file smoke test. Reconfirm technology
scope with the Adjudicator before changing dependency manifests. No automatic
installation or live submission is included.
## Design detail

**In:** approved AWS Braket SDK range, vulnerability posture, optional/lazy
import, install/troubleshooting path, lock/update policy, and minimal real-file
smoke test. **Out:** new provider selection, automatic install, credentials,
and live submission.

**Acceptance:** local paths work without the SDK; supported installation is
version/security checked; import failure is actionable and fail-closed; no
provider package is imported by Domain/UseCase; the dependency policy record is
reviewable.

**Phase/evidence:** Phase 0 technology/dependency review; Phase 1 Red isolated
import tests; Phase 2 approved packaging change only; Phase 3 security and CI
review. Planning record: `AIP-LISS-0463-2026-08-27-001` (M; N/A model metrics).
Changing provider/range requires typed technology approval.

## Phase 1 Red artifact

- Added `tests/test_liss_0463_dependency_security_packaging_red.py`.
- The test-only contract covers provider-optional local operation, actionable
  missing-SDK failure, rejection below the approved security floor, no SDK
  import during inspection, and Host-adapter-only import boundaries.
- Red is confirmed by the intentionally absent
  `compiler.staqex.provider_dependency_policy` module. No dependency
  manifest, SDK installation, credentials, network access, or provider
  selection was changed.
- Phase 2 Green requires technology/security review and remains unapproved.

## Phase 2 Green artifact

- Added `compiler/staqex/provider_dependency_policy.py`, a standard-library
  policy inspector that reads version metadata supplied by the Host boundary
  and never imports or installs the provider SDK.
- Missing SDKs remain provider-optional for local paths and fail closed with
  an actionable diagnostic; versions below the approved floor are rejected;
  imports outside the Host adapter are rejected.
- LISS-0463 and the existing AWS Braket adapter contract tests pass. Python
  3.14 `py_compile` and `git diff --check` pass. No dependency manifest,
  credentials, network access, or live submission was introduced.
- Phase 3 security/CI review remains separately gated.

## Phase 3 closeout

- Extracted boundary validation and dependency diagnostic message creation
  into focused helpers without changing the reviewed policy behavior.
- LISS-0463 and existing AWS Braket adapter contract tests pass; Python 3.14
  `py_compile` and `git diff --check` pass. Because no SDK or manifest was
  added, live package installation and external vulnerability scanning were
  not performed.
- Same-context security/CI review found no blocker within the approved,
  manifest-free slice; this isolation is weaker than separate-context review.
- Process review: no operating-contract deviation or operational problem
  found.
- Actual SDK adoption, dependency pinning, credentials, network access, and
  live submission remain separately gated.
