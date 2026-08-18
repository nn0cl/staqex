# Independent Context Review — LISS-0438 design review 01

## Trigger

- User request: proceed to LISS-0438 design/spec/independent review after
  LISS-0437 completion.
- Date: 2026-08-18
- Review scope: residual S02 explicit-evolution reconciliation design only.
- Issue / ADR / Spec / WorkPlan: LISS-0438 / ADR 0210 / residual Spec /
  WP-0104.
- Branch: `codex/liss-0438-residual-reconciliation`
- Current phase: Architecture Path design intake; no AT-TDD phase.
- Allowed paths: LISS-0438 design artifacts and directly referenced S02
  documentation; no compiler or test implementation.
- Explicitly excluded: S02 numerical migration/retuning, live QPU, provider
  SDK, credentials, network, broad corpus migration, and phase approval.

## Review lenses

- Applicable lenses: contract and acceptance completeness; architecture and
  boundary integrity; source-to-domain fidelity; type/dimension/validity
  closure; state and physics safety; realization/fail-closed behavior;
  migration/regression safety; phase/approval discipline; evidence/context
  hygiene.
- Why: the design separates formal blackboard meaning, exact local execution,
  finite target realization, and reproducible S02 evidence.
- Prior records consulted: LISS-0437 independent review records and the
  independent review perspectives ledger.

## Independent reviewer

- Context mode: fresh independent context
- Reviewer task: read-only review of LISS-0438 design artifacts and S02
  source/document correspondence.
- Read-only: yes
- Implementation permission: no
- Approval authority: none

## Iteration log

### Iteration 1

- State entered: `REVIEW` → `DISPOSITION` → `CORRECT`
- Artifacts inspected: residual Spec, WP-0104, LISS-0438 Issue, design trace,
  ADR 0210, accepted explicit evolution Spec, S02 source/README, S02
  regression and objective-fidelity tests.
- Findings, prioritized:
  - **F1 P1:** rejection provenance wording conflicted with ADR 0210.
  - **F2 P1:** S02 README described retired `feasible(...)` syntax rather than
    the source's literal `F`/`P_F` construction.
  - **F3 P1:** exact-local versus finite-target lane was not operationally
    frozen.
  - **F4 P1:** S02 dimensional, acting-space, unitary, and projector-leakage
    safety evidence was not explicit.
  - **F5 P2:** reproducibility inputs lacked source/compiler/profile/settings
    identity.
  - **F6 P2:** bounded corpus inventory had no reviewable file list or rule.
  - **F7 P2:** the proposed branch did not match the active branch.
- Finding dispositions:
  - F1: `accepted`; primary-agent under delegated policy; ADR 0210 requires
    rejection provenance while forbidding executable allocation. No design
    deviation.
  - F2: `accepted`; primary-agent under delegated policy; documentation-only
    correction restores source-to-blackboard fidelity. No design deviation.
  - F3: `accepted`; primary-agent under delegated policy; freeze separate
    `U_t` exact-local and `U_qpu` finite-target-plan lanes for this slice. No
    ADR change; implementation still requires approval.
  - F4: `accepted`; primary-agent under delegated policy; add observable
    dimensional, acting-space, unitary, and leakage evidence requirements.
    No design deviation.
  - F5: `accepted`; primary-agent under delegated policy; bind source hash,
    compiler/profile, settings, Host inputs, and seeds in later evidence.
  - F6: `accepted`; primary-agent under delegated policy; remove broad corpus
    inventory from this slice and defer it to a separate Issue if needed.
  - F7: `accepted`; primary-agent under delegated policy; move uncommitted
    design work to the dedicated LISS-0438 branch before further mutation.
- Lens mapping: F1/F3/F4 → realization, type/physics, architecture; F2 →
  source fidelity; F5/F6 → evidence and migration safety; F7 → approval
  discipline.
- Readiness verdict: `READY for design review; NOT READY for Phase 1 approval`.
- Corrections applied: provenance wording, lane decision, S02 safety/evidence
  requirements, reproducibility identity, corpus boundary, README mapping,
  and branch metadata.
- Files changed: residual Spec, WP-0104, LISS-0438 design trace, S02 README;
  no compiler, test, or runtime files.
- Remaining blockers: fresh independent re-review; authoritative Phase 1
  seed/metric selection; separate Phase 1 and implementation approvals.
- Reviewer perspective to retain: source documentation must be checked against
  the actual current source, not only against historical acceptance prose.
- New recurring perspective to add: none; existing ledger lenses cover all
  findings.
- Next review condition: rerun a fresh read-only review against corrected
  artifacts.

### Terminal decision

- Terminal state: `ABORT`
- Completion basis or abort reason: user/Adjudicator decision is required to
  reconcile the already Accepted explicit-evolution Spec P8/P10 with ADR 0210.
- User/Adjudicator decision required: decide whether overflow rejection keeps a
  diagnostic-only record while retaining no target-plan provenance, or whether
  the Accepted Spec/ADR contract should be amended. No Phase 1 or
  implementation approval is implied.
- Evidence path: this record and the corrected artifacts.

## Gate status

- Requested approval type: design/spec/review scope only.
- Approved scope: LISS-0438 design intake, Spec/WP creation, and independent
  review; approved by user 2026-08-18.
- Approval authority / approver: user/Adjudicator.
- ADR status: ADR 0210 unchanged and accepted.
- Specification status: residual Spec corrected; loop ABORTED on an existing
  Accepted Spec contradiction.
- Phase approval: none.
- Implementation approval: none.
- Post-review requirement: fresh independent review before Phase 1 request.
- Gate evidence path: LISS-0438 Issue and this record.

## Evidence

- Finding evidence: reviewer paths/sections recorded above; deterministic
  source/document inspection confirmed the README/source mismatch and branch
  mismatch.
- Deterministic checks: `git diff --check`; required design files exist and
  links resolve by path inventory.
- Related trace: `docs/collaboration/traces/2026-08-18-liss-0438-design-intake.md`.
- User/Adjudicator decision still required: Phase 1 Red approval and later
  implementation approval.

### Iteration 2

- State entered: `RE_REVIEW` → `DISPOSITION` → `CORRECT`
- Artifacts inspected: corrected residual Spec and WP, S02 README/source,
  ADR 0210, and this review record.
- Findings, prioritized:
  - **F8 P1:** rejection diagnostic evidence and target-plan provenance were
    still conflated; ADR 0210 requires missing-policy evidence but forbids
    provenance on resource-budget overflow.
  - **F9 P1:** README still contained retired `feasible(...)` wording and an
    outdated objective factory signature/body.
- Finding dispositions:
  - F8: `accepted`; primary-agent under delegated policy; clarify three
    distinct outcomes: diagnostic/rejection evidence for missing/invalid
    policy, no executable allocation for all rejection, and no target-plan
    provenance specifically for budget overflow. This preserves ADR 0210.
  - F9: `accepted`; primary-agent under delegated policy; update all README
    equation/code/operation references to match the current source. No design
    deviation.
- Lens mapping: F8 → realization/fail-closed behavior and contract
  completeness; F9 → source-to-domain fidelity and migration safety.
- Readiness verdict: `NOT READY for design closure`.
- Corrections applied: residual Spec rejection taxonomy and S02 README
  objective/operation wording.
- Files changed: residual Spec and S02 README.
- Remaining blockers: fresh independent re-review; Phase 1 seed/metric
  authority and typed Phase 1/implementation approvals.
- Reviewer perspective to retain: distinguish diagnostic evidence from
  successful target-plan provenance, especially for budget overflow.
- New recurring perspective to add: none.
- Next review condition: fresh read-only review of the corrected artifacts.

### Iteration 3

- State entered: `RE_REVIEW` → `DISPOSITION` → `ABORT`
- Artifacts inspected: corrected residual Spec/README/WP, accepted explicit
  evolution Spec P8/P10, ADR 0210, and prior iterations.
- Findings, prioritized:
  - **F10 P1:** the accepted explicit-evolution Spec is internally ambiguous:
    P8 permits a rejected provenance envelope, while P10 describes resource
    budget rejection with `realization_kind`, resource estimate, and requested
    budget without explicitly excluding provenance. The same Spec also says
    budget rejection leaves no provenance envelope, and ADR 0210 requires no
    provenance on overflow.
- Finding disposition:
  - F10: `deferred`; resolution requires changing an already Accepted Spec
    and possibly reconciling its authority with ADR 0210. The primary agent
    must not decide this by assumption.
- Lens mapping: contract completeness; realization/fail-closed behavior;
  phase and approval discipline.
- Readiness verdict: `NOT READY for design closure`.
- Corrections applied: none; the blocker is outside the approved design-only
  correction authority.
- Files changed: none in this iteration.
- Remaining blockers: user/Adjudicator decision on the Accepted Spec's
  rejection-provenance contract; then a fresh independent review.
- Reviewer perspective to retain: specify diagnostic evidence versus target-
  plan provenance and resource-overflow behavior in one authoritative
  contract.
- New recurring perspective to add: none; existing lenses cover the issue.
- Next review condition: only after the user/Adjudicator resolves F10.
