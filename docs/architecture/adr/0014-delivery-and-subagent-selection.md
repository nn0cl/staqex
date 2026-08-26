# ADR 0014: Delivery Route and Subagent Selection

## Status

Accepted

## Context

The template sync script already creates a branch and can open a pull request,
while `--no-pr` supports local-only work. Operators need an explicit choice
between those routes, a way to select the local base branch, and a way to
record whether another agent should be involved. Implicit publication or a
provider-specific subagent command would create unintended external effects or
technology coupling.

## Decision

`scripts/update-ai-collaboration-files.sh` supports two delivery routes:

- `github`: push the branch and open a PR. `--merge-pr` is an explicit opt-in
  that requests GitHub auto-merge after required checks pass.
- `local`: create and commit the branch locally without pushing or opening a
  PR. `--base-branch` or an interactive menu selects the branch from which it
  is created.

When a route or base branch is omitted, an interactive terminal may ask. In a
non-interactive invocation, the safe defaults are local delivery and the
current branch. `--no-pr` remains an alias for local delivery.

`--subagent ask|yes|no` records a provider-neutral handoff request. `yes`
does not invoke a model, create a provider account, or choose an agent runtime;
the host environment remains responsible for launching an actual subagent.

The existing Issue, specification, ADR, Work Plan, and Adjudicator approval
boundaries remain the agreement units. Delivery and subagent choices only
control execution routing and are recorded in the output/PR metadata.

## Consequences

Positive:

- Publication is explicit and local review remains safe by default.
- Operators can choose a local base branch without editing the script.
- The template stays provider-neutral while making subagent intent visible.

Negative:

- GitHub auto-merge depends on repository settings and required checks.
- Local review does not automatically publish or merge a branch.
- A `yes` subagent choice still requires a host agent or human to launch it.

## References

- `scripts/update-ai-collaboration-files.sh`
- `docs/collaboration/branch-commit-pr-discipline.md`
- `docs/architecture/adr/0007-trunk-oriented-branching.md`
- `docs/architecture/adr/0008-template-update-propagation.md`
