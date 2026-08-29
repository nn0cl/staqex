# LISS-0455: Real-QPU scope reconciliation

| Field | Value |
|---|---|
| Status | **done — Phase 0 reconciliation complete** |
| Phase | phase-0-design |
| Type | architecture / planning |
| Priority | P0 |
| Initial size | M |
| Current size | M |
| Owner | Adjudicator + host agent |
| Parent | WP-0119 / WP-0120 |
| Depends on | none |
| Blocks | LISS-0456–0470 |
| Branch | `codex/liss-0455-qpu-scope-reconciliation` |

| Scope approval | User approved this next safe action, 2026-08-27 |
| Implementation permission | None; documentation/ledger reconciliation only |
| Post-review requirement | Process review recorded below |

Reconcile the canonical register, WP-0118, WP-0116/0117, and completed QPU
assets. Produce the authoritative supported-subset matrix, close status drift,
and record which work is complete, deferred, or genuinely open. No code,
provider install, branch deletion, or phase approval is included.

Decision points: scope of the first real-device pilot, accepted provider/device
boundary, and whether deployment operations are in scope. Exit: approved
matrix and synchronized register/WP/Issue statuses.

## Design detail

**In:** reconcile WP-0118/0119, `open-work-register`, WP-0106/0108/0116/0117,
completed QPU assets, and the first-device pilot boundary. **Out:** source or
runtime changes, provider installation, branch deletion, credentials, and
downstream Phase 1 approval.

**Acceptance:** every roadmap item is mapped to `complete`, `deferred`,
`proposed`, or `blocked` with evidence; completed slices are not reopened; each
proposed item names owner, dependency, approval type, and next artifact.

**Phase/evidence:** Phase 0 inventory and decision log only. Deliverables are
the synchronized register, status matrix, dependency graph, and Adjudicator
decision record. Verify with unique-ID scan, link check, `git diff --check`,
and canonical ADR/spec cross-check. Planning record:
`AIP-LISS-0455-2026-08-27-001` (M; host agent; N/A model metrics).

**Decision points:** first pilot program/device, provider scope, and whether
WP-0125 is needed. Unresolved decisions keep downstream work `proposed`.

## Phase 0 result and disposition matrix

| Area | Disposition | Evidence / next owner |
|---|---|---|
| Scientific Semantic IR bounded projection | complete baseline; not reopened | ADR 0211, WP-0107/0108; continuation is LISS-0456 |
| Coin/Mix meaning and QPU rejection | complete bounded baseline; not generalized | ADR 0212/0213, WP-0111–0114; family review is LISS-0457 |
| Explicit finite `Realize`/Suzuki and S02 migration | complete recorded slices; new numerical work requires a new plan | ADR 0210, WP-0100/0105/0106 |
| Static/dynamic QASM emitters and provider-neutral ports | existing baseline; hardening only | ADR 0083/0103/0104/0201; WP-0122/0123 |
| AWS Braket adapter/CLI walkthrough | existing adapter baseline; integration verification only | ADR 0202/0203; LISS-0463–0466 |
| Public QASM facade / old AST / non-explicit `symbolic_ir` | open, design-gated | LISS-0456 / WP-0120 |
| Product/tensor, continuous/open-system, measurement | open, family-specific contract required | LISS-0457 / WP-0120 |
| Artifact, capability, routing, QASM conformance | open roadmap work | LISS-0458–0462 / WP-0121–0122 |
| Provider packaging, credentials, lifecycle | open roadmap work | LISS-0463–0466 / WP-0123 |
| Real run, validation, operations | human/conditional future work | LISS-0475 / WP-0126; operations LISS-0470 / WP-0125 |

### Phase 0 closeout

- All LISS-0455–0470 have a unique owner, dependency, parent WP, and next
  artifact; none is promoted to implementation by this reconciliation.
- WP-0120 is now the active child WP, with LISS-0456 and LISS-0457 remaining
  proposed design work.
- The first real-device program, device, and deployment need remain unresolved
  decisions; they are not silently selected here.
- Verification: unique LISS ID scan, link scan, `git diff --check`, and manual
  cross-check against the canonical register/ADR/spec records.

Process review: no operating-contract deviation or operational problem found.
