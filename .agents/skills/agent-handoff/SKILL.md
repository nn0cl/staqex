---
name: agent-handoff
description: Write a resumable handoff when pausing, stopping before completion, or transferring work to another agent. Use when the session ends mid-task or another agent must continue.
---

# Agent handoff

Canonical template: `docs/templates/agent-handoff.md`. Fill that shape.

State at least:

- current phase and remaining user request
- completed artifacts and verification
- changed files
- included, omitted, assumptions, and open decisions
- review and implementation isolation (or that routing is missing)
- next safe action and blockers

Recover later from this handoff, a trace, spec or ADR, branch, and changed
files — not from chat memory.
