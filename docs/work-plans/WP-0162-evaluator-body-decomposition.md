# WP-0162: Evaluator body decomposition successor

| Field | Value |
|---|---|
| Status | historical — superseded by WP-0163; predecessor evidence retained |
| Size | XL |
| Parent | WP-0160 |
| Scope approval | Adjudicator approved 2026-09-18 |
| Implementation permission | historical record only; no new implementation under this WP |
| Canonical specification | [Core module decomposition](../specs/staqex-core-module-decomposition.md) |
| Current source at intake | `compiler/staqex/runtime/evaluator.py` — 6,928 lines / 149 methods |

## Goal

Reduce the cognitive and regression risk of `Evaluator` by extracting cohesive
runtime families while preserving its public API, single mutable-state owner,
diagnostics, deterministic local execution, and canonical Scientific Semantic
IR authority.

## Scope

In: internal extraction of evaluator orchestration, observation/dynamic lanes,
evolution/operators, classical/value evaluation, scientific selection/continuous
families, and the final compatibility facade/budget audit.

Out: language semantics, public API retirement, diagnostic renaming, QASM
format changes, provider SDKs, credentials, network/live QPU, Rust migration,
performance rewrites, and opportunistic bug fixes.

## Issue Graph

| Issue | Status | Size | Depends on | Blocks | Candidate internal package |
|---|---|---:|---|---|---|
| LISS-0560 | done — Phase 3 final review approved 2026-09-18 | M | none | 0561–0565 | `runtime/evaluation/orchestration.py` |
| LISS-0561 | done — Phase 3 final review approved 2026-09-18 | L | 0560 | 0565 | `runtime/evaluation/observation.py`, `dynamic_lane.py` |
| LISS-0562 | superseded by LISS-0566-C | L | 0560 | - | `runtime/evaluation/evolution.py`, `operators.py` |
| LISS-0563 | historical — not started | L | 0560 | - | no implementation; future work requires a new issue |
| LISS-0564 | historical — not started | L | 0560 | - | no implementation; future work requires a new issue |
| LISS-0565 | superseded by LISS-0566-D | M | 0561–0564 | - | facade/structure audit |

The package names are design candidates, not implementation permission. A
Phase 0/Phase 1 review may rename a package when the measured dependency graph
shows a more cohesive boundary.

## Architecture boundary

`Evaluator` remains the only owner of mutable runtime maps, `Joint` state,
stdout/sink routing, and injected ports. Extracted services receive an
explicit immutable context or narrow callbacks. They must not construct a
second `Evaluator`, cache mutable maps, or import a public facade that imports
them.

The public `compiler.staqex.runtime.evaluator` module remains a compatibility
facade and thin orchestration surface. Scientific Semantic IR remains the
compile-owned authority; extracted AST helpers are execution mechanics only.

## Planning record

### AIP-WP-0162-001 (Historical)

- Status: historical — superseded by WP-0163
- Created by: Codex host agent; displayed model/reasoning identifier unavailable
- Created at: 2026-09-18
- Planning size: XL
- Intended route: Architecture Path Phase 0, then Feature Path bounded units;
  host implementation and same-context review under current routing
- Intended scope: evaluator internals only, six Issues above
- Estimate: N/A; repository exposes no compatible token-planning metric
- Basis: 6,976 lines, 166 methods, multiple mutable-state and semantic-family
  boundaries, high runtime import fan-out, and fixed-seed/QASM preservation needs
- Assumptions: no behavior correction is hidden in extraction; public imports stay
- Confidence: medium; Phase 1 dependency manifests may subdivide 0562–0564
- Revises: WP-0160 evaluator successor candidate

## Phase gates

1. Phase 0: accepted inventory, public symbol manifest, mutable-state map,
   dependency graph, characterization corpus, and exact allowed files.
2. Phase 1 Red: failing structural/characterization contracts only.
3. Phase 2 Green: minimum extraction for one approved family.
4. Phase 3 Refactor: import cleanup, naming, facade audit, and full evidence.
5. Final review: process review, status synchronization, and no unresolved
   behavior drift.

No Issue may begin Phase 2 until its Phase 1 contract and allowed file set are
separately approved.

## Acceptance invariants

- Public imports and callable/DTO contracts remain available.
- Fixed source/seed local results, measurement evidence, and stdout remain equal.
- Accepted QASM and artifact identity remain byte-identical.
- Rejection code, source span, ordering, and atomic no-artifact behavior remain equal.
- Scientific Semantic IR identity and provenance remain compile-owned.
- Extracted modules have one declared mutable-state owner and no import cycle.
- No provider SDK, credential, network, filesystem, or UI dependency enters the
  Kernel runtime path.
- `tests/spec_verification/run_all.py` remains `161/161`.

## Recommended order

1. LISS-0560 — orchestration and runtime-plan dispatch.
2. LISS-0561 — observation and dynamic lanes.
3. LISS-0562 — evolution and operator execution.
4. LISS-0563 — classical calls and values.
5. LISS-0564 — scientific selection and continuous families.
6. LISS-0565 — facade, import graph, public symbol, and structure-budget audit.

## Historical successor disposition

WP-0162 was the original decomposition plan. Its completed orchestration and
observation work was carried into the successor plan `WP-0163`, and the
evolution/operator and facade work was completed through
`LISS-0566-A`–`LISS-0566-D`. `LISS-0562` remains as historical evidence of its
bounded predecessor slice. `LISS-0563` and `LISS-0564` were never started, and
`LISS-0565` was replaced by the approved facade audit in `LISS-0566-D`.

Do not reopen these records as current work. Any future classical/value or
scientific-family decomposition must receive a new issue and design intake.

## Completion disposition

Recorded on 2026-09-19:
`WP-0162/LISS-0562〜0565 整合性整理 承認`.

This work plan is Historical and is not a source of current next actions.
`WP-0163` is the canonical successor for the evaluator decomposition work.

## Verification plan

Each Issue must run public-symbol/import manifest comparison, focused
characterization tests, fixed-seed runtime snapshots, nearest semantic-family
tests, compile/import checks, document lifecycle checks, Spec Verification,
blocking pytest, and `git diff --check`. Runtime-moving Issues additionally
require QASM golden comparison and mutable-state ownership review.

## Risks and stop conditions

Stop and return to Architecture review if extraction changes public DTOs,
semantic authority, diagnostic precedence, state ownership, or dependency
direction. Reclassify as a separate Feature Path Issue if characterization
reveals a behavior defect rather than a structural mismatch.

## Process Review

- Outcome: no operating-contract deviation or operational problem found.
- Lesson written: evaluator-state ownership and private-consumer inventory
  lessons were applied; no new deviation recorded.
- Template-feedback path: none
