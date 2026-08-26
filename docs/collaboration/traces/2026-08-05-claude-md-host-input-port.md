# AI Work Trace

## Request

- Date: 2026-08-05
- User request: Adjudicator directed working through an agreed follow-up
  order ("4, 1, 3, 2") after LISS-0327/LISS-0328 shipped ADR 0194's
  `HostInputPort`; item "1" in that order is ADR 0194's own Follow-up item
  3 — add `HostInputPort` to `CLAUDE.md`'s "External Resources Must Be
  Ports" list.
- Current phase: documentation-only change to an agent operating contract
  file (`CLAUDE.md`), governed by
  `docs/collaboration/prompt-instruction-change-control.md`, not an AT-TDD
  Red/Green/Refactor phase.
- Canonical issue or work plan: [ADR 0194](../../architecture/adr/0194-host-input-port-and-selection-predicate-semantics.md)
  Follow-up item 3; ports shipped in
  [LISS-0327](../../issues/LISS-0327-host-input-port-foundation.md) (PR
  #366, merged) and consumed by
  [LISS-0328](../../issues/LISS-0328-selection-projector-predicate-execution.md)
  (PR #368, merged).
- AI planning record: none separate — this is a one-line addition to an
  existing bulleted list, following the exact wording pattern already used
  for `RngPort`/`SourcePort`/`MeasureSinkPort` in the same list.

## Context Ledger

- Included: `CLAUDE.md`'s "External Resources Must Be Ports" section (the
  list this change extends); ADR 0194's own text (which already states
  this as a required follow-up, not a new decision); the shipped
  `compiler/staqex/host_input_port.py` (confirms the port's real shape:
  `HostInputPort` Protocol + `MappingHostInputAdapter`, matching
  `MeasureSinkPort`'s existing pattern).
- Omitted: no other CLAUDE.md section was reviewed for unrelated changes —
  this trace covers only the one list addition ADR 0194 named.
- Assumptions: the port's already-Accepted ADR text is sufficient
  justification; this trace does not re-litigate ADR 0194's own design
  reasoning, only records that its Follow-up item 3 is being executed.
- Open decisions: none — the wording is a direct, low-ambiguity summary of
  what ADR 0194 already decided and what LISS-0327 already shipped.

## Routing

- Model/assistant/tool: Claude Code (Sonnet 5), this session, direct edit.
- Reason: single-sentence documentation addition; no external AI/model call
  warranted.
- Privacy constraints: none — no private data involved.

## AI Execution Records

### Attempt 1

- Agent: Claude Code (Sonnet 5)
- Environment: this session, local repository
- Model as displayed: Claude Sonnet 5
- Reasoning setting as displayed: N/A (not exposed to this environment)
- Estimated token range: N/A
- Estimated token midpoint: N/A
- Actual tokens: N/A — no token/time budget tracked for this environment
  (consistent with every other AI planning record filed this session,
  e.g. LISS-0322/0324's own "Estimate: N/A" notes)
- Token metric: N/A
- Token source: N/A
- Token attribution boundary: N/A
- Actual token unavailable reason: environment does not expose per-request
  token accounting to the agent
- Estimate variance: N/A
- Variance reason: N/A
- Scope: add one bullet to `CLAUDE.md`'s "External Resources Must Be
  Ports" list, naming `HostInputPort` and its ADR 0194 origin.
- Result: complete, one edit.
- Attempt boundary: single attempt, no retries needed.
- Notes: wording deliberately restates the port's actual constraint (never
  candidate/entity identity, slot-indexed structural data only) so the
  contract line stands on its own without requiring a reader to open ADR
  0194 to understand the boundary.

## Optional Reference Total

- Value: N/A
- Metric: N/A
- Source: N/A
- Compatibility statement: N/A

## Cost / Reasoning Control

- Operating path: Fast Path (mechanical, local, documentation-only; does
  not change behavior, architecture, tests, or agent instructions beyond
  recording an already-Accepted ADR's own required follow-up).
- Files read: `CLAUDE.md`, `docs/collaboration/prompt-instruction-change-control.md`,
  `docs/templates/ai-work-trace.md`, ADR 0194, `compiler/staqex/host_input_port.py`.
- Context intentionally omitted: unrelated `CLAUDE.md` sections.
- Deterministic checks used: `git diff --check`.
- Escalation reason: none — no ambiguity requiring escalation.
- Avoided LLM work: none applicable.
- Rework caused by AI output: none.

## Adjudicator Decisions

- Granted: explicit review and approval of the `CLAUDE.md` wording itself,
  per `docs/collaboration/prompt-instruction-change-control.md`'s Review
  Rule.
- Granted: push + PR authorization; PR #372 opened.
- Granted: merge confirmation. PR #372 merged, commit `eba7fd8`.

## Verification

- Commands/checks: `git diff --check` (clean). No test suite or spec
  verification run — this change touches only `CLAUDE.md` prose and this
  trace file; no compiler, grammar, or example code changed.
- Result: clean.

## Changed Files

- `CLAUDE.md` (one bullet added to "External Resources Must Be Ports")
- `docs/collaboration/traces/2026-08-05-claude-md-host-input-port.md` (this file)

## Next Safe Action

Complete. ADR 0194's Follow-up item 3 is now fully closed — both Issues
(LISS-0327, LISS-0328) and this contract update are merged. Next work
follows the Adjudicator's stated order ("4, 1, 3, 2"): item 3 (WP-0092's
remaining work units) or item 2 (WP-0093 work unit E's remaining scope).

## Notes

- `CLAUDE.md` is excluded from the cross-agent-file consistency check
  (ADR 0112) — this change does not need to be ported to `AGENTS.md`,
  `.github/copilot-instructions.md`, `.grok/rules/*.md`, or
  `.cursor/rules/*.mdc`, and their silence on `HostInputPort` is not a
  defect.
