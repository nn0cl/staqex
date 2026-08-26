# Independent Context Review Record

Use this record whenever the user triggers the independent review/correction
loop. One record may contain multiple iterations, or a new record may be made
for a separate trigger.

## Trigger

- User request:
- Date:
- Review scope:
- Issue / ADR / Spec / WorkPlan:
- Branch:
- Current phase:
- Allowed paths:
- Explicitly excluded paths/actions:

## Review lenses

- Applicable lenses from the perspectives ledger:
- Why these lenses apply:
- Prior review records consulted:

## Independent reviewer

- Context mode: fresh independent context
- Reviewer task:
- Read-only: yes
- Implementation permission: no
- Approval authority: none

## Iteration log

### Iteration <N>

- State entered: `REVIEW` / `DISPOSITION` / `CORRECT` / `RE_REVIEW`
- Artifacts inspected:
- Findings, prioritized:
- Finding dispositions:
  - Finding ID:
  - Disposition: `accepted` / `rejected` / `deferred`
  - Disposition authority: `primary-agent under delegated policy` /
    `Adjudicator` / `user`
  - Rationale and evidence:
  - Design-deviation check: `no` / `yes — escalated`
- Lens mapping for findings:
- Readiness verdict:
- Corrections applied:
- Files changed:
- Remaining blockers:
- Reviewer perspective to retain:
- New recurring perspective to add to the ledger:
- Next review condition:

### Terminal decision

- Terminal state: `COMPLETE` / `ABORT` / not terminal
- Completion basis or abort reason:
- User/Adjudicator decision required:
- Evidence path:

## Gate status

- Requested approval type:
- Approved scope:
- Approval authority / approver:
- ADR status:
- Specification status:
- Phase approval:
- Implementation approval:
- Post-review requirement:
- Gate evidence path:

## Evidence

- Finding evidence: each finding must include file path, line or section, and
  the deterministic or document evidence used to verify it.
- Deterministic checks:
- Related trace:
- User/Adjudicator decision still required:
