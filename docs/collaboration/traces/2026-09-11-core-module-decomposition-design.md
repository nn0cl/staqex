# AI Work Trace — core module decomposition design

## Request

- Date: 2026-09-11
- User request: refactor and split source files that carry too much code.
- Current phase: Architecture Path / Phase 0 design
- Canonical issue or work plan: WP-0160 / LISS-0543–0550
- AI planning record: AIP-WP-0160-001

## Context Ledger

- Included: largest Python modules, method spans, import blast radius, test/CI
  state, runtime/backend/semantic architecture, and source-quality policy.
- Omitted: new language behavior, provider/live-QPU work, credentials, Rust.
- Assumptions: existing public imports and behavior remain compatible.
- Open decisions: architecture/spec approval; active-Red metadata shape;
  evaluator/typechecker/parser context protocols; blocking size thresholds.

## Routing

- Model/assistant/tool: host Codex agent, deterministic AST/import/test inventory
- Reason: implementation route is host; review isolation is same-context
- Privacy constraints: repository-local data only

## AI Execution Record

- Agent/environment: Codex host in local workspace
- Model/reasoning setting: unavailable from repository runtime
- Token estimate/actual/metric: N/A; compatible metric unavailable
- Scope: Phase 0 specification, work plan, and issue decomposition
- Result: one authoritative proposed spec, one umbrella WP, eight bounded issues
- Attempt boundary: repository recovery through Phase 0 document verification

## Cost / Reasoning Control

- Operating path: Architecture Path
- Files read: workflow, readiness, quality, runtime/backend architecture,
  planning templates, largest modules through AST inventory, and import callers
- Context intentionally omitted: unrelated historical issues and provider code
- Deterministic checks used: line counts, AST method spans, import-reference
  inventory, document checks
- Avoided LLM work: inventories were generated mechanically
- Rework caused by AI output: none

## Adjudicator Decisions

- `WP-0160 / Core module decomposition Architecture承認` received 2026-09-11.
- No Phase 1/2/3 implementation permission is inferred from the request.

## Verification

- Required after edits: document lifecycle, coverage-ledger consistency,
  unresolved placeholders, duplicate LISS/WP IDs, and `git diff --check`.

## Changed Files

- Proposed spec, WP-0160, LISS-0543–0550, and this trace.

## Next Safe Action

Request `LISS-0543 Phase 1 Red 承認`; begin only that test/process-contract
phase after its separate approval.
