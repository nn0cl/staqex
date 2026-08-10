# AI Work Trace

## Request

- Date: 2026-08-10
- User request: Continue a handoff on Dynamic QPU follow-ups
  (post LISS-0383/0385), then a long "続けて" (continue) sequence across
  root-cause work, reset keyword design, OpenQASM emission, and a live
  QPU provider adapter, ending with a request to sync `CLAUDE.md`'s
  "Current Open Topics" section to reflect what this session shipped.
- Current phase: Feature Path, Issue-Level Autonomy (multiple Issues,
  each with its own Plan + Completion approval per CLAUDE.md §Claude Code
  Issue-Level and Work-Plan Autonomy); this trace itself is Architecture
  Path docs-only (CLAUDE.md sync).
- Canonical issue or work plan: LISS-0387, LISS-0388, LISS-0389,
  LISS-0390, LISS-0391, LISS-0392, LISS-0393 (all **complete**, each with
  its own PR). No work-plan batch record — every Issue used the
  Issue-level two-gate model (Plan approval, Completion approval), not a
  bounded execution batch.
- AI planning record: N/A for this trace (docs-only, size S). Each
  Feature Issue above carries its own AI planning record in its Issue
  file.

## Context Ledger

- Included: ADR 0197–0203 (0198/0199 Amendments), LISS-0383–0393, the
  Adjudicator language vision (§1 audience/priority, §2.2 blackboard↔source
  sameness) for the `reset`-keyword decision, `dependency-policy.md`'s
  Dependency Adoption Checklist for the AWS Braket selection, and direct
  reads of the touched Kernel/Host source files at each step (evaluator,
  hir.py, dynamic_capability.py, dynamic_qpu.py, parser.py, ast_nodes.py,
  qpu_submit.py, credentials.py, backend/qasm/*).
- Omitted: live provider result-schema deep mapping, CLI/REPL surfaces,
  OpenQASM emission for any lane beyond Dynamic, cost/budget controls —
  all explicitly named out-of-scope in their respective ADRs/Issues.
- Assumptions: each root-cause discovery (LISS-0387's block-end trace-out
  erasing evidence, LISS-0390's linear-checker consumed-vs-fresh
  distinction, ADR 0203's async/sync mismatch) was investigated against
  actual source before being presented as a finding, not inferred from
  documentation alone — cited by file:line at each step in this session's
  own transcript.
- Open decisions: none outstanding at trace time. Two standing
  constraints carry forward past this session (not decisions to revisit):
  this agent never handles AWS credentials and never performs a real
  (non-mock) Braket submission autonomously, regardless of any
  "proceed without stopping" direction given for unrelated, zero-cost
  Kernel work earlier in the same session (ADR 0202 Decisions 3 and 5).

## Routing

- Model/assistant/tool: Claude Code (Sonnet 5), interactive session
- Reason: Feature Path implementation across nine Issues plus four new
  ADRs and two ADR Amendments; docs-only trace + `CLAUDE.md` sync as the
  final step
- Privacy constraints: repository docs and source only; no secrets;
  AWS Braket security research (CVE-2026-9291) used public web search/
  fetch against public advisory sources only, no account-specific data

## AI Execution Records

### Attempt 1

- Agent: Claude Code
- Environment: Claude Agent SDK, macOS
- Model as displayed: Sonnet 5
- Reasoning setting as displayed: N/A (harness default)
- Estimated token range: N/A
- Estimated token midpoint: N/A
- Actual tokens: N/A
- Token metric: N/A
- Token source: N/A
- Token attribution boundary: N/A
- Actual token unavailable reason: interactive session; no token meter
  surfaced to the agent
- Estimate variance: N/A
- Variance reason: N/A
- Scope: ADR 0200 (root-cause real Kernel execution) / LISS-0387; LISS-0388
  (reuse capability repurposing); ADR 0198 Amendment (outcome confirmation)
  / LISS-0389; ADR 0199 Amendment (`reset` keyword) / LISS-0390; ADR 0201
  (OpenQASM dynamic emission) / LISS-0391; ADR 0202 (AWS Braket adapter
  selection) / LISS-0392; ADR 0203 (live submit entrypoint) / LISS-0393;
  this trace + `CLAUDE.md` Current Open Topics sync.
- Result: completed — all nine Issues merged to `main`; full regression
  1402 passed as of LISS-0393; `CLAUDE.md` sync is this trace's own
  remaining step.
- Attempt boundary: single continuous session, Issue-by-Issue Plan/Red/
  Green/Refactor/Completion per CLAUDE.md's Issue-Level Autonomy model;
  no batch record used.
- Notes: Self-verification performed per Issue (Red failed for the
  stated reason before Green; Green passed without editing a test to
  force it; Refactor changed no behavior; full regression ran after each
  Refactor) — recorded individually in each Issue's own Exit Criteria
  section rather than repeated here.

## Optional Reference Total

- Value: N/A
- Metric: N/A
- Source: N/A
- Compatibility statement: N/A

## Cost / Reasoning Control

- Operating path: Feature Path (nine Issues) + Architecture Path (four
  ADRs: 0200, 0201, 0202, 0203; two Amendments: ADR 0198, ADR 0199) +
  this Architecture Path docs-only trace
- Files read: see each Issue's own Plan-locked decisions section for the
  specific files inspected before that Issue's implementation; this
  trace additionally read `CLAUDE.md`'s own "Current Open Topics" section
  to locate the stale bullets being corrected here
- Context intentionally omitted: live provider account/credential state
  (never inspected, never held); vendor-specific QASM dialect extensions
- Deterministic checks used: full regression suite re-run after every
  Green/Refactor (final count 1402 passed); direct source reads (not
  inference) grounded every root-cause finding this session surfaced
  (e.g. `Joint.project_coord` already shipped, `Circuit`/`Gate` IR has no
  reset/conditional representation, `submit_source` is local-only by
  contract)
- Escalation reason: three Hard Stops during this session, each resolved
  by presenting findings and options rather than deciding unilaterally —
  (1) LISS-0387's Verification-boundary discovery (block-end trace-out
  erases direct evidence), (2) the `reset`-keyword surface-spelling
  choice (Adjudicator explicitly rejected reusing existing syntax), (3)
  the `submit_source` sync/async mismatch discovered while wiring ADR
  0202's adapter (led to ADR 0203)
- Avoided LLM work: real AWS Braket SDK import/execution was never
  attempted — `RealAwsBraketClient`'s real-SDK method calls are written
  from public documentation knowledge and are explicitly flagged
  (LISS-0392 AI planning record) as unverified against a live import,
  isolated behind a lazy-import + version-gate boundary
- Rework caused by AI output: two amendments to already-"complete"
  Issues within this same session (LISS-0383's success-fixture Gherkin
  amended by LISS-0386 and again by LISS-0388; LISS-0385's reject-on-demand
  consequence superseded by LISS-0388/0390) — each was a disclosed,
  Adjudicator-approved consequence of an accepted root-cause fix, not a
  defect discovered after the fact; recorded in each amended Issue's own
  Addendum/Amendment note at the time
