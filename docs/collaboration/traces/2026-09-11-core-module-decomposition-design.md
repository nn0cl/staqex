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
- `LISS-0543 Phase 1 Red 承認` received 2026-09-11.
- `LISS-0543 Phase 2 Green / Implementation 承認` received 2026-09-11.
- `LISS-0543 Phase 3 Refactor 承認` received 2026-09-11.
- `LISS-0543 Phase 3 最終レビュー 承認` received 2026-09-11.

## Verification

- Phase 0: document lifecycle, coverage-ledger consistency, unresolved
  placeholders, duplicate LISS/WP IDs, and `git diff --check` passed.
- Phase 1 Red: 12 tests collected and intentionally failed because both
  expected production scripts are absent; test `py_compile` and diff check
  passed.
- Phase 2 attempt 1: focused Red contracts passed, but direct baseline capture
  failed because execution from `scripts/` did not place repository root on
  `sys.path`. The correction explicitly adds the selected root before imports;
  planning size remains L because it was already multi-file and multi-attempt.
- Phase 2 Green: lifecycle checking, exact-node pytest selection, deterministic
  baseline generation, and CI baseline comparison implemented without compiler
  or runtime behavior changes. Focused tests pass 12/12 and Spec Verification
  passes 161/161; the full blocking-suite result is recorded after completion.
- Phase 2 contract review found that the first public-symbol filter was narrower
  than Python's actual no-`__all__` export behavior. It now records every
  non-underscore name. Final Green evidence is 2,043 passed with 19 exact-node
  deselections, 12/12 focused tests, and 161/161 Spec Verification checks.
- Because LISS-0543 is size L and review routing is `same_context`, the
  same-model review cannot claim independent approval. A deterministic human
  acceptance packet was produced for the next phase gate.
- Final Phase 2 checks also passed baseline byte comparison, active-Red
  lifecycle validation (19 entries), script compilation, document lifecycle,
  coverage-ledger consistency, and `git diff --check`.
- Phase 3 Refactor separated lifecycle validation concerns and baseline case
  orchestration without changing assertions, CLI contracts, selection output,
  or committed baseline bytes. Focused checks passed before the final full
  verification run.
- Final Phase 3 evidence: 2,043 blocking tests passed with the same 19 exact
  active-Red nodes deselected; Spec Verification passed 161/161.
- Completion review found an ownership cycle: all 19 active-Red exclusions
  name LISS-0543, while the lifecycle checker correctly rejects any exclusion
  whose owner issue is done. Final review is approved, but status remains open
  until accepted successor remediation issues own those nodes.

## Changed Files

- Phase 0: accepted spec, WP-0160, LISS-0543–0550, and this trace.
- Phase 1: two Red test files, two test fixtures, LISS/WP synchronization, and
  the Phase 1 review packet.
- Phase 2: two repository scripts, active-Red metadata, generated baseline,
  CI selection and reproducibility checks, and Phase 2 status synchronization.
- Phase 3: readability-only script extraction, final-review packet, and phase
  metadata synchronization.

## Next Safe Action

Obtain Adjudicator disposition for a separate remediation work plan and
successor ownership of the 19 active-Red nodes; then close LISS-0543.
