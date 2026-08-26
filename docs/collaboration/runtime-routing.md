# Runtime Routing for Review and Implementation

This policy is the Canonical document for how an adopting project routes
agent-to-agent review and implementation. It does not replace typed
Adjudicator approval.

Live settings live at:

```text
docs/collaboration/runtime-routing.toml
```

Create or refresh them with:

```bash
scripts/configure-ai-collaboration.sh --target /path/to/repo
scripts/configure-ai-collaboration.sh --target /path/to/repo --non-interactive
scripts/configure-ai-collaboration.sh --target /path/to/repo \
  --review-isolation separate_context \
  --implementation-isolation host \
  --force
```

The blank form is `docs/templates/runtime-routing.toml`. The live file is
target-owned: copy and update scripts must not overwrite it. Re-run with
`--force` only when you intend to replace local choices.

## Who reads it

After selecting an operating path, and before review or implementation work:

1. Read `docs/collaboration/runtime-routing.toml` if present.
2. If it is missing after first adoption, recommend
   `scripts/configure-ai-collaboration.sh` rather than inventing isolation or
   model names. Continue with capability-class routing on the host agent.
3. Honor `[review]` and `[implementation]`. Do not treat these values as
   architecture, phase, or implementation approval.

## Defaults when the file is missing

| Role | Isolation | Model |
| --- | --- | --- |
| Review | `same_context` | empty (capability class) |
| Implementation | `host` | empty (capability class) |

These defaults match pre-ADR-0015 behavior plus the same-context review
template when an agent review packet is already required.

## `[review]`

Applies only when the process already requires an agent review packet
(substantial review, review summary, or Phase 3 reviewer empathy). It does
not add a new mandatory gate and does not replace the human Adjudicator.

| Isolation | Meaning |
| --- | --- |
| `same_context` | The current agent reviews in this session using `.agents/skills/same-context-review/SKILL.md`. |
| `separate_context` | The host launches a subagent in a clean context. Pass artifacts, specifications, contract documents, deterministic output, and a handoff. Do not pass the parent's reasoning as justification. |
| `ask` | Stop and ask the Adjudicator which isolation to use for this review. |

`model` is an optional identifier as displayed by the host. Empty means follow
`docs/collaboration/model-tool-capability-matrix.md`. A different model from
the implementer is recommended to reduce shared bias, but is not required.

The template never invokes a provider. `separate_context` is a launch request
for the host agent or a human.

## `[implementation]`

| Isolation | Meaning |
| --- | --- |
| `host` | The current agent implements. |
| `separate_context` | The host launches an implementer subagent in a clean context with a handoff. |
| `ask` | Stop and ask the Adjudicator which isolation to use for this implementation. |

`model` is an optional host-displayed identifier. Empty means capability-class
routing.

## Relation to template-sync handoff

`scripts/update-ai-collaboration-files.sh --subagent` records whether a
template-sync change requests a provider-neutral handoff. That flag is not
this file. Do not mix the two.

## Secrets

Never store API keys, tokens, or provider credentials in the live file or in
handoffs derived from it.
