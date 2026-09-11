# Architecture Review: LISS-0514 multi-provider QPU contract

| Field | Value |
|---|---|
| Review status | **accepted — Architecture approved; Phase 2 Green complete; review pending** |
| Scope | `staqex-multi-provider-qpu-execution-contract.md`, LISS-0514, WP-0131 |
| Operating path | Architecture Path |
| Review isolation | same_context; weaker than separate-context review |
| Current phase | Phase 2 Green complete |
| Implementation permission | None |
| Requested approval | Review of Phase 2 Green implementation |

## Canonical documents re-read

- `docs/specs/staqex-multi-provider-qpu-execution-contract.md`
- `docs/specs/staqex-real-qpu-readiness-acceptance.md`
- `docs/specs/staqex-hybrid-workflow.md`
- `docs/architecture/decision-themes/dec-0006-host-qpu-and-external-ports.md`
- `docs/architecture/implementation-readiness.md`
- `compiler/staqex/qpu_submit.py`
- `compiler/staqex/job_lifecycle.py`
- `compiler/staqex/qpu_observation.py`
- `docs/architecture/open-work-register.md`
- `docs/work-plans/WP-0131-multi-provider-real-qpu-connectivity.md`
- `docs/issues/LISS-0514-multi-provider-qpu-contract-readiness.md`

## Findings

### F-01 — Existing port vocabulary must stay exact

- Severity: resolved
- Disposition: applied
- The WP design note named a nonexistent `QpuResultPort`. The current accepted
  boundary uses `QpuJobPort.result`; the WP now names `QpuJobPort` only.

### F-02 — Human authorization placement

- Severity: resolved by Adjudicator direction
- Disposition: applied
- AWS/provider credentials remain in the Host execution environment's normal
  config/credential chain. Per-run human approval is represented by a separate
  non-secret `HostSubmissionApproval` record bound to artifact, target, shots,
  and cost ceiling; only its reference may appear in evidence or a request.
- Remaining implementation detail: decide whether the reference is carried in
  an additive request field or only in the Host evidence envelope.

### F-03 — Timeout and unknown state mapping needs a closed rule

- Severity: resolved in proposed contract
- Disposition: applied; typed Architecture approval received 2026-09-10
- The current `ProviderJobState` has queued/running/succeeded/failed/cancelled;
  the proposal adds `timed_out` and `unknown`. Define whether these are
  provider-neutral lifecycle from Host observation. `timed_out` is non-terminal
  observation data; `unknown` is non-success and non-terminal. Raw provider
  states remain preserved.

### F-04 — Capability source and freshness need an invariant

- Severity: resolved in proposed contract
- Disposition: applied; typed Architecture approval received 2026-09-10
- `CapabilityProfile.source` distinguishes declared and observed, but the
  contract now makes the profile a time-bounded Host snapshot. Live preflight
  uses a fresh, identity-matched profile and re-checks dynamic availability;
  stale, unverifiable, retired, or unavailable profiles fail closed.

### F-05 — Artifact format decision is correctly deferred

- Severity: accepted deferral
- Disposition: already closed with evidence
- The common contract does not choose OpenQASM 3 versus QIR. That decision
  belongs to provider-specific Phase 0 adoption Issues; Phase 1 may test only
  the provider-neutral artifact boundary.

### F-06 — AWS scope correctly reuses completed work

- Severity: resolved
- Disposition: already closed with evidence
- The current register records AWS adapter, submit CLI, job-port CLI, and demo
  as complete. WP-0133 is correctly limited to gap analysis and target-profile
  extension.

## Acceptance disposition

The architecture is consistent with DEC-0006 and the real-QPU readiness
specification. F-02 is resolved by the Adjudicator direction. F-03 and F-04
are resolved in the contract and accepted ADR 0217. Typed Architecture
approval was received on 2026-09-10. This review still grants no Phase 1 or
implementation permission. Phase 1 requires separate typed approval.

## Deterministic verification

- `git diff --check`: required after remediation.
- `python3 scripts/check-document-lifecycle.py`: required after remediation.
- `rg` confirms all provider boundaries use `QpuSubmitPort`/`QpuJobPort` and no
  `QpuResultPort` remains in the WP design note.
- No runtime tests run; this is an architecture review.

## Next safe action

Review `compiler/staqex/qpu_contract.py` against the unchanged Phase 1 Red
tests. This review does not grant Phase 3 permission or provider integration
permission.
