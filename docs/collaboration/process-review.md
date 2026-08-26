# Completion Process Review

This policy is the Canonical document for the development-process review that
runs when a local issue or work plan is marked `done`. It does not replace
typed Adjudicator approval or product review.

## When

In the **same context** that is closing the issue or work plan, after
deterministic verification and issue-status synchronization, before reporting
completion.

Do not spawn a subagent solely for this review unless
`docs/collaboration/runtime-routing.toml` already requires `separate_context`
for agent review. The default is same-context.

## What to inspect

Ask only process questions:

- Did the work follow the operating contract (path, phase, approvals, ports,
  payload limits, branch/PR discipline)?
- Did an operational problem appear (status drift, unfilled placeholders
  treated as facts, missing traces on contract changes, review isolation
  ignored)?
- Is there a reusable meta-level lesson for
  `docs/collaboration/process-lessons-log.md`?

Do not turn this into a second product-code review. Do not replay the session
as an incident log.

## Outcomes

### No deviation

Record in the issue or work plan:

```text
Process review: no operating-contract deviation or operational problem found.
```

### Deviation or operational problem

1. Stop and describe the class of problem to the Adjudicator.
2. Agree the disposition (fix now, lesson only, template feedback, or
   `wont_do` with reason).
3. Write a meta-level lesson when the pattern should affect later work.
4. When the Adjudicator agrees the finding should be fed back to this
   collaboration template, write a record from
   `docs/templates/template-feedback.md` under
   `docs/collaboration/template-feedback/`.

Do not send network mail or open an upstream PR unless the Adjudicator asks.
The record in the adopting repository is the durable artifact.

## Template feedback ownership

Files under `docs/collaboration/template-feedback/` are target-owned. Copy and
update scripts must not overwrite them. They are optional until the first
agreed finding.
