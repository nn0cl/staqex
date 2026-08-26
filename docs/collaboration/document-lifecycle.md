# Document Lifecycle and Source-of-Truth Policy

This policy keeps reusable collaboration rules separate from target-owned
specifications while preserving decisions and evidence.

## Ownership

`Template-owned` documents define common paths, phases, approvals, reviews,
sync behavior, logging rules, and on-demand procedures
(`.agents/skills/*/SKILL.md`). They may be updated by this template and are
not a place to add a target project's domain decisions. Skills are procedure
Entry documents; they point at Canonical policy and templates rather than
replacing them.

`Target-owned` documents define the adopted project's specifications, domain
model, ADR choices, implementation boundaries, technology selections,
runtime routing choices (`docs/collaboration/runtime-routing.toml`),
project conventions (`docs/collaboration/project-conventions.md`), and
deprecated-term mappings. They are authoritative for that project and should
be linked from the template entry documents rather than copied into them.

When synchronizing agent contracts, record template changes, target changes,
intentional differences, and each decision as accepted, rejected, or pending.
Literal equality is not required when a target has an approved customization.

## Four document layers

| Layer | Purpose | Normal status |
| --- | --- | --- |
| Entry | First document a developer or agent reads | Current |
| Canonical | The one current source for a topic | Current |
| Evidence | ADRs, issues, work plans, traces, tests, and review records supporting a decision | Current or Historical |
| Archive | Completed, superseded, or historical material retained for recovery | Historical |

Every topic should have one Canonical document. Entry documents point to the
Canonical Register and current Canonical documents. They do not begin from an
Archive document or present Historical material as current guidance.

The Register is a navigation and consistency aid, not a new agreement unit.
It does not approve requirements, replace an accepted specification or ADR,
change Issue or Work Plan ownership, or authorize implementation. The existing
Issue, specification, ADR, Work Plan, and Adjudicator approval boundaries
remain unchanged.

## Current and Historical

Use `Current` for material that can affect today's implementation or review.
Use `Historical` for superseded or completed material. Historical records keep
their original decision context; they are not silently rewritten to match the
current rule.

The Canonical document states the current rule briefly and links to its source
evidence. Do not copy the same current status into an ADR, Issue, Work Plan,
and Trace merely for convenience.

## Consolidation and recovery

Consolidate documents when a decision is accepted, an Issue or Work Plan is
complete with no next action, duplicate Canonical documents exist, or review
records repeat the same conclusion. Preserve the evidence needed to explain
the decision and keep the original file historical when it has audit value.

Before moving or compressing a document, record:

```text
source_path
source_commit
source_tag
canonical_destination
classification
reason
```

Git history remains the recovery mechanism. Do not delete historical material
just to reduce the current reading set.

## Standard read order

1. Entry document and the Canonical Register.
2. The relevant current Canonical document.
3. For decided content, the relevant ADR or specification.
4. Only the Evidence needed to verify that decision (ISSUE, work plan, trace)
   when the ADR or specification cites it, or when resuming that work.
5. Archive material only when the Register or a Canonical document points to it
   for historical context.

Do not open ISSUE or work-plan files as the source of current rules.

## Citation direction

- ADRs and specifications may reference ISSUES and work plans.
- ISSUES and work plans list the context files, ADRs, and specifications they
  changed.
- Context files (agent contracts, current collaboration policy, quickstart)
  state the current rule. They do not link to an ADR or ISSUE as the reason
  that context file was edited.
- Agents looking up why a context file changed start from the ADR or ISSUE,
  not from a reverse link in the context file.

The register and review summary are navigation aids, not substitutes for the
underlying evidence or for the existing agreement artifacts. A Review Summary
may point to an approval record, but cannot create or widen that approval.

## Deterministic checks

`scripts/check-document-lifecycle.py` validates the explicit Register entries:

- Canonical keys are unique.
- Entry and Canonical paths exist and are not under an Archive path.
- Status and layer values are valid.
- Current Canonical entries include existing source references.

The check intentionally does not infer project-specific vocabulary or decide
whether a document should be archived. Those decisions require target-owned
review.
