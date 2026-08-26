# ADR 0015: Runtime Routing Setup for Review and Implementation

## Status

Accepted

## Context

The template routes work by capability class and keeps commercial model names
out of the shared contract. ADR 0014 records whether a template-sync change
requests a provider-neutral subagent handoff; it does not configure day-to-day
review or implementation routing.

Adopters need a first-run, re-runnable way to choose:

- whether agent-to-agent review happens in a separate context or in the same
  session with a dedicated review prompt;
- whether implementation stays on the host agent or is handed to a subagent;
- optional model identifiers as displayed by the host.

Implicitly invoking a provider, storing secrets, or treating those choices as
Adjudicator approval would couple the template to a vendor and collapse the
approval model.

## Decision

1. Adoption may run `scripts/configure-ai-collaboration.sh`, which writes
   target-owned `docs/collaboration/runtime-routing.toml` from
   `docs/templates/runtime-routing.toml`. The live file is not a template
   distribution artifact and is excluded from copy and later sync overwrite.
2. A TTY collects review isolation, review model, implementation isolation,
   and implementation model. Flags cover the same fields. Without a TTY the
   defaults are review `same_context`, implementation `host`, and empty
   model identifiers.
3. Missing live file means current behavior: capability-class routing on the
   host agent. Agents must not invent model names.
4. Isolation values:

   - review: `separate_context` | `same_context` | `ask`
   - implementation: `host` | `separate_context` | `ask`

   `separate_context` is a host-launch request, not a provider invocation.
   `same_context` review uses `docs/templates/same-context-review.md`.
   `ask` stops for the Adjudicator at that review or implementation.
5. These settings parameterize agent-to-agent review and implementation that
   the process already requires. They do not add a new mandatory review gate
   and do not replace typed Adjudicator approval.
6. Model identifiers are optional free text as displayed by the host. The
   template does not ship commercial model names as defaults. Empty means
   follow `docs/collaboration/model-tool-capability-matrix.md`.
7. ADR 0014 `--subagent` remains the template-update delivery concern. Runtime
   routing is the day-to-day concern.
8. Agent contract files instruct agents to read the live file when present
   and to recommend the configure script after first adoption rather than
   guessing.

## Consequences

Positive:

- Adopters can choose review isolation and models without editing contracts.
- Same-context review is a supported alternative when the host cannot spawn
  a clean-context subagent.
- Template sync cannot clobber adopter routing choices.
- The template stays provider-neutral.

Negative:

- Same-context review is weaker isolation than a separate context.
- A `separate_context` choice still requires the host or a human to launch
  the subagent.
- Agents must distinguish missing settings from an explicit empty model.

## References

- `scripts/configure-ai-collaboration.sh`
- `docs/collaboration/runtime-routing.md`
- `docs/templates/runtime-routing.toml`
- `docs/templates/same-context-review.md`
- `docs/architecture/adr/0014-delivery-and-subagent-selection.md`
- `docs/collaboration/model-tool-capability-matrix.md`
