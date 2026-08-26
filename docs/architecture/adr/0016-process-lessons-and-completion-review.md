# ADR 0016: Process Lessons, Completion Review, and Adopter-Safe Identifiers

## Status

Accepted

## Context

Agents that load operating context will follow any ISSUE or work-plan ID they
see. Those files are work-management history, not current rules. Decided
content belongs in ADRs and specifications, which may cite ISSUES and work
plans as evidence. Context files that justify their own edits by linking out
to an ADR or ISSUE invert that graph.

Unfilled angle-bracket placeholders are easy to treat as domain or technology
facts. Review write-ups that replay a single incident do not transfer to the
next task. Completing an issue or work plan without checking operating-contract
deviations hides process debt until the next adoption round.

`CLAUDE.md` is a full effective-content mirror. Canonical contract-change
text that still describes an `@AGENTS.md` import contradicts that decision.

## Decision

1. Citation direction:

   - Agents do not open ISSUE or work-plan files as the source of current
     rules. They read current policy documents, ADRs, and specifications.
   - ADRs and specifications may reference ISSUES and work plans as evidence.
   - Context files (agent contracts, current collaboration policy, quickstart)
     do not link to an ADR or ISSUE as the reason that context file changed.
     The reverse is required: the ADR or ISSUE lists the context files it
     changed.
   - Copy and update still exclude this template's `LISS-*.md`, `WP-*.md`,
     traces, and reviews so adopting repositories do not receive this
     template's planning ledger. Naming-format examples (`LISS-0000`) remain.
2. If a relied-on contract or architecture file still contains an unfilled
   `<...>` placeholder, agents stop after design intake and ask the
   Adjudicator to set the value. Placeholder text is not a fact.
3. `CLAUDE.md` remains a full mirror. It does not import `@AGENTS.md`.
   Contract-change checks compare effective content across the five agent
   surfaces.
4. Review outcomes that should change later work are recorded as meta-level
   lessons: recurring process risks, contract-deviation classes, and
   operating-path failures. Do not record a blow-by-blow of a specific
   session. Read the lessons log at the next design intake and before
   implementation. Policy: `docs/collaboration/process-lessons.md`.
5. When a local issue or work plan is marked `done`, the same context runs a
   development-process review against the operating contract. If no
   deviation or operational problem is found, record that. If one is found,
   agree the disposition with the Adjudicator and write a template-feedback
   record from `docs/templates/template-feedback.md` under
   `docs/collaboration/template-feedback/` so it can be sent upstream.
   Policy: `docs/collaboration/process-review.md`.

## Consequences

Positive:

- Agents follow current policy, ADRs, and specs instead of old ISSUES/WPs.
- Context-file edits are explained from the ADR or ISSUE, not the reverse.
- Placeholders cannot silently become stack or domain choices.
- Later design and implementation can reuse process patterns.
- Template feedback is captured in the adopting repo with Adjudicator
  agreement, not only in chat.

Negative:

- Completion takes an extra same-context review step.
- Meta lessons still need human judgment to stay non-anecdotal.
- Historical traces in this template repository keep issue IDs; they are
  not copied.

## Changed context files

- `AGENTS.md`
- `CLAUDE.md`
- `.github/copilot-instructions.md`
- `.grok/rules/*.md`
- `.cursor/rules/*.mdc`
- `docs/architecture/agent-quickstart.md`
- `docs/collaboration/document-lifecycle.md`
- `docs/collaboration/prompt-instruction-change-control.md`
- `docs/collaboration/adoption-guide.md`
- `docs/collaboration/local-issue-planning.md`
- `docs/collaboration/runtime-routing.md`
- `docs/collaboration/process-gap-register.md`
- `docs/collaboration/process-lessons.md`
- `docs/collaboration/process-review.md`
- `scripts/lib/collaboration-template-paths.sh`

## References

- `docs/issues/LISS-0021-adopter-hygiene-and-process-review.md`
- `docs/collaboration/process-lessons.md`
- `docs/collaboration/process-review.md`
- `docs/collaboration/document-lifecycle.md`
