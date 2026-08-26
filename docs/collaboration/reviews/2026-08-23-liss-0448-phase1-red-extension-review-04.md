# LISS-0448 Phase 1 Red Extension — Independent Review 04

- Trigger: fresh re-review after the source-anchor correction commit `b9ae0ff5`.
- Review mode: independent, read-only; no implementation or phase approval.
- Scope: Red test/fixture self-containment, source anchoring, and validity of the remaining implementation-target failures.
- Branch: `codex/liss-0448-canonical-qasm-coin-mix-projection`.
- Phase: Phase 1 Red extension.

## Findings and disposition

| Priority | Finding | Disposition |
| --- | --- | --- |
| P1 | Verification is not reproducible from a clean `b9ae0ff5` tree because the branch intentionally retains the earlier Phase 2/3 production implementation in the working tree. | rejected as non-applicable to this Red-boundary review; the review scope is the current working tree plus the committed Red test/fixture boundary, and no claim of a clean `b9ae0ff5` implementation baseline is made |
| P1 | Review 03 contained a stale failure/pass count. | accepted and corrected below: current bounded harness is 4 failed, 4 passed |
| P2 | Test and all three fixtures are self-contained in commits `3d265ea9` and `167817ff`. | accepted; no correction required |
| P2 | Source anchoring is partial because arm-span assertion depends on IR traversal order while arm provenance is itself the Red contract. | accepted as an intentional Phase 2 contract target; branch order is independently anchored to fixture lines 6–7 and exact arm provenance is expected to become available with the accepted canonical IR change |

## Current Red evidence

The bounded direct harness reports exactly 4 failures and 4 passes:

- missing `control_source_node_id` and ordered `branch_rules`;
- missing `WhenArm` source spans;
- legacy copy-pattern Mix still emits CX instead of rejecting;
- pattern/else branch mutations do not yet change the semantic fingerprint;
- four existing structural/provenance/rejection contracts pass.

These are valid Phase 2 implementation targets under accepted ADR 0213 and the accepted LISS-0448 specification. No architecture deviation is indicated.

## Reusable review lenses

Contract completeness; source-to-domain fidelity; canonical authority; realization-boundary/fail-closed behavior; phase discipline; evidence/context hygiene; projection conservation.

## Readiness verdict

`READY` for the end of the Phase 1 Red extension review loop only. This does not approve Phase 2, implementation, or any architecture change.

## Terminal state

`COMPLETE` — all review findings are dispositioned; no review-loop blocker remains.

## Approval status

Phase 1 Red extension is complete. Phase 2 Green approval remains separate and has not been granted.
