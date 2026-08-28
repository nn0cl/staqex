# LISS-0470: Provider-neutral delivery and operations boundary

| Field | Value |
|---|---|
| Status | **deferred — local Host operation is sufficient; no Phase 1 required** |
| Phase | phase-0-deferred |
| Type | architecture / operations |
| Priority | P1 |
| Initial size | XL |
| Current size | XL |
| Owner | Host/delivery boundary |
| Parent | WP-0119; WP-0125 |
| Depends on | LISS-0469 |
| Blocks | none |
| Branch | `codex/liss-0470-provider-neutral-delivery-operations` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0470--delivery-and-operations-boundary) |
| Implementation permission | None |
| Post-review requirement | Post-pilot need decision; ADR and Phase 1 approval if unblocked |

Only if the pilot demonstrates a need, define provider-neutral delivery,
retention, monitoring, audit, incident response, cancellation, and cost
controls. Keep deployment outside the Kernel. Selecting cloud topology,
persistence, or a service provider requires a separate ADR and technology
approval; this Issue may close as deferred if local Host operation is enough.
## Design detail

**In:** only demonstrated post-pilot needs: provider-neutral delivery,
retention/deletion, monitoring, audit, incident response, cancellation, cost,
and privacy controls. **Out:** default cloud migration, datastore selection,
public service API, and provider-specific deployment without a new ADR.

**Acceptance:** delivery exposes only approved Job/Result evidence; retention,
deletion, audit, and incident behavior are explicit or the Issue closes as
deferred; operational failure cannot mutate source meaning or silently
resubmit a job.

**Phase/evidence:** Phase 0 decides needed/deferred after WP-0124; if needed,
new ADR and Phase 1 Red contract tests precede implementation. Planning record:
`AIP-LISS-0470-2026-08-27-001` (XL; N/A model metrics).

## Deferred disposition

- User confirmed on 2026-08-28 that delivery/operations should remain
  conditional and deferred until a demonstrated post-pilot need exists.
- Current local Host operation is sufficient. No delivery ADR, datastore,
  cloud topology, public API, retention, monitoring, or deployment boundary
  was introduced.
- Reopening requires an evidenced need, a new ADR, technology approval, and
  Phase 1 Red contract tests.
- Process review: no operating-contract deviation or operational problem
  found.
