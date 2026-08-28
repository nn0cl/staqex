# LISS-0468: Human-authorized first real-QPU pilot

| Field | Value |
|---|---|
| Status | **done — Phase 3 refactor complete** |
| Phase | phase-3-refactor |
| Type | human operations |
| Priority | P0 |
| Initial size | M |
| Current size | M |
| Owner | Adjudicator / human operator |
| Parent | WP-0119; WP-0124 |
| Depends on | LISS-0464, LISS-0466, LISS-0467 |
| Blocks | LISS-0469 |
| Branch | none for real run; preparation uses a dedicated feature branch |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0468--human-authorized-real-qpu-pilot) |
| Implementation permission | None; no autonomous real-QPU submission |
| Post-review requirement | Human pilot-protocol review and separate real-run approval |

Write the dry-run and approval checklist for one small supported program,
including target selection, cost/shots guard, cancellation, credential check,
artifact review, explicit real-time human confirmation, and evidence capture.
The agent may prepare commands and inspect results, but must not submit to a
real device autonomously.
## Design detail

**In:** one minimal supported program, one selected device, dry-run output,
artifact review, cost/shot guard, human confirmation, cancellation, and
evidence capture. **Out:** unattended scheduling, production claims, agent
credential use, broad benchmarking, and provider expansion.

**Acceptance:** the human operator reviews artifact, target, cost, and safety
checks before explicit real-time approval; the path is auditable; the run is
labeled real/non-mock; cancellation and failure instructions exist before
submission.

**Phase/evidence:** Phase 0 pilot protocol; Phase 1 offline checklist tests;
Phase 2 dry-run/fake execution only; Phase 3 human-gated real action and
evidence handoff. Planning record:
`AIP-LISS-0468-2026-08-27-001` (M; N/A model metrics).

## Phase 1 Red artifact

- Added `tests/test_liss_0468_human_authorized_pilot_red.py`.
- The test-only checklist covers dry-run artifact review, target/device,
  shots/cost guards, credential check, cancellation/evidence plans, explicit
  real-time human approval, redacted audit fields, and real/non-mock labeling.
- Red is confirmed by the intentionally absent
  `compiler.staqex.pilot_checklist` module. No real credential, network,
  provider, device, or submission was used.
- Phase 2 fake/dry-run implementation and any real-run authorization remain
  unapproved.

## Phase 2 Green artifact

- Added `compiler/staqex/pilot_checklist.py` for offline/fake checklist
  evaluation.
- Missing safety steps, invalid guards, or failed credential checks reject
  before any action. A complete dry-run is only `ready-for-human-approval`;
  explicit approval becomes `authorized` but still carries no physical claim
  and no observed execution.
- Contract tests, Python 3.14 `py_compile`, and `git diff --check` pass. No
  real credential, network, device, or submission was used. Phase 3 review
  remains gated.

## Phase 3 closeout

- Extracted checklist diagnostic and audit-field construction into focused
  helpers without changing approval states, redaction, or non-submit behavior.
- Contract tests, Python 3.14 `py_compile`, and `git diff --check` pass.
- Same-context pilot-protocol review found no blocker; this isolation is
  weaker than separate-context review.
- Process review: no operating-contract deviation or operational problem
  found.
- Any real-QPU action still requires separate real-time human authorization.
