# ADR 0217: QPU observation states and capability freshness

## Status

**Accepted** (2026-09-10) — typed Adjudicator Architecture approval received.
This does not authorize implementation or live provider submission.

## Context

Provider SDKs expose provider-specific lifecycle states, while polling and API
failures are Host observations. AWS Braket, Azure Quantum, IBM Qiskit, and
Google QCS do not provide one portable `timed_out` terminal state. Device
capabilities, availability, and calibration are also time-varying snapshots.
Treating these as permanent or collapsing them into `failed` can cause lost
jobs, duplicate submissions, or execution against stale hardware assumptions.

## Dependency Adoption Evidence

Not applicable. This ADR selects no SDK, provider, or dependency.

## Decision

1. Preserve the raw provider lifecycle value in `provider_state`.
2. Represent provider-neutral lifecycle and Host observation separately:
   `normalized_state` contains queued/running/succeeded/failed/cancelled/
   unknown, while `observation_state` contains observed/timed_out/unreachable/
   stale.
3. `timed_out`, `unreachable`, and `stale` are non-terminal observations.
   `unknown` is non-success and non-terminal unless a later provider
   observation establishes a terminal state. No unknown state may be guessed as
   queued, running, or failed.
4. Only an observed provider success permits result projection. A timed-out or
   unknown observation never authorizes automatic resubmission.
5. `CapabilityProfile` is a time-bounded Host snapshot with provider/device
   identity, fingerprint, capture/expiry timestamps, availability, and an
   optional calibration reference.
6. Live preflight must use a fresh, identity-matched profile and re-check
   dynamic availability immediately before submission. Expired, stale,
   unverifiable, retired, or unavailable profiles fail closed. Stale data may
   be used for offline planning only.
7. Provider-specific TTL and calibration cadence are adapter metadata. They may
   refine freshness, but may not change Staqex semantics or authorize stale
   execution silently.

## Consequences

Positive:

- Provider differences remain observable without weakening the common contract.
- Polling timeouts cannot be mistaken for job failure or successful completion.
- Capability and calibration assumptions become auditable and reproducible.

Negative:

- Host adapters must maintain an observation envelope and freshness policy.
- Live submission may be rejected when a provider capability endpoint is
  unavailable.

## Enforcement

Code review should reject:

- Mapping Host polling timeout to provider `failed` or `cancelled`.
- Projecting results from `timed_out`, `unknown`, stale, or unverifiable state.
- Live submission using an expired or identity-mismatched capability profile.
- Automatic resubmission without an explicit idempotency-aware Host policy.
