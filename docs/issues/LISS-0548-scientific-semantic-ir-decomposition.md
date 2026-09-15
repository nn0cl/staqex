# LISS-0548: Scientific Semantic IR decomposition

## Metadata

- Local issue ID: LISS-0548
- GitHub issue: none
- Status: done
- Phase: done
- Type/priority: refactor / P0
- Initial/current planning size: L / L
- Owner/agent: host implementation; same-context review
- Related branch: `refactor/scientific-semantic-ir`

## Summary

Keep `scientific_semantic_ir.py` as the canonical public facade while moving
model, fingerprint, runtime-plan, QPU-projection, finite-realization, and
algorithm-plan implementation into `scientific_semantic/`.

## Planned extraction units

- `model.py`: immutable semantic DTOs only.
- `fingerprint.py`: canonical serialization and identity.
- `builder.py`: source-derived semantic graph construction.
- `runtime_plan.py`: runtime execution projection.
- `qpu_projection.py`: finite QPU projection and rejection evidence.
- `realization.py`: explicit finite/evolution/algorithm records.

## Acceptance Notes

Scientific Semantic IR remains the sole compile-owned authority. Fingerprints,
node/source IDs, provenance, approximation and finite evidence, runtime plans,
QPU projections, and rejection ordering are exact. No compatibility DTO gains
execution authority.

## Dependencies

- Parent: WP-0160
- Depends on: LISS-0543
- Blocks: LISS-0549, LISS-0550
- Related: ADR 0211 and consumer-migration specification

## Adjudicator Decision Points

Architecture approval is required for DTO ownership and acyclic dependency
direction. Each consumer is audited before moving exports.

## AI Planning Record — AIP-0548-001

- Status/date/size: proposed / 2026-09-11 / L
- Agent/route: Codex host, display unavailable; host + same-context review
- Scope/estimate: six semantic units; N/A token estimate
- Basis/confidence: 2,008 lines and 14 direct import consumers; high
- Assumptions: facade owns backwards-compatible imports
- Revises/Superseded by: none

## Phase 0 design intake

### [DESIGN CHECK]

- Scope and expected behavior: split the implementation families of the
  source-derived Scientific Semantic IR while keeping
  `scientific_semantic_ir.py` as the stable public facade. Preserve semantic
  node identity, source provenance, fingerprints, runtime-plan projections,
  finite-realization records, QPU projection/rejection ordering, and all
  existing public imports.
- Specifications and files inspected: the core module decomposition spec, the
  Scientific Semantic Core spec, the semantic consumer migration spec, ADR
  0211, `scientific_semantic_ir.py`, its direct import consumers, the existing
  semantic-core and consumer tests, implementation readiness, and the current
  process-lessons log.
- Component boundaries, ports/adapters, and VO/DTO candidates: `model.py`
  owns frozen semantic DTOs and stable value records; `fingerprint.py` owns
  canonical serialization/digest only; `builder.py` owns source-AST to
  canonical-IR construction and read-only inspection/rejection views;
  `runtime_plan.py` owns runtime projection DTO construction;
  `qpu_projection.py` owns finite QPU projection, Suzuki lowering policy,
  binder provenance, and ordered projection errors; `realization.py` owns
  explicit `Realize` records, algorithm-plan projection, and realization
  provenance. No provider port or adapter is introduced; target/provider
  transport remains outside the Kernel.
- Applicable constraints: Scientific Semantic IR remains the only
  compile-owned semantic authority. No AST/DTO fallback may gain execution
  authority; `Realize` remains the explicit finite boundary; no live QPU,
  SDK, network, filesystem, Rust, or language-semantics change; no second
  mutable semantic state owner; no new dependency or import cycle.
- Decisions, assumptions, and unresolved ambiguities: the facade will
  re-export the current symbols and delegate only through internal modules.
  Internal modules may depend on `model.py` and narrowly on existing AST,
  finite-binder, and Trotter helpers, but never import the facade. Builder
  orchestration must call each projection builder once, making canonical
  build/fingerprint/finiteization ownership machine-checkable. The exact
  placement of observation dictionaries and inspection/rejection DTOs is
  resolved as model data plus builder-produced views; no new observation
  algebra is designed here. Any consumer needing a new public symbol is a
  separate migration issue.
- Included and omitted AI context: included source module structure, public
  import manifest, accepted semantic authority/provenance specs, relevant
  tests, and process lessons. Omitted unrelated evaluator/parser changes,
  historical superseded ADRs, provider credentials, private data, and full
  repository contents.
- Task routing (model/assistant/tool): host implementation with same-context
  review, as required by `runtime-routing.toml`; deterministic shell/pytest
  checks for verification. No model-generated runtime behavior is accepted
  without tests and human approval.
- Input/output evidence contract when AI output is involved: inputs are the
  accepted specs, source module, public-import manifest, and approved test
  corpus. Outputs are a design review packet, Phase 1 Red tests, and later
  source changes; each records changed files, findings, exact verification,
  uncertainty, and approval type. No AI output is a semantic authority.
- Verification plan: first capture public exports/imports and semantic
  fingerprint/QPU/realization snapshots; then add structural Red tests for
  module ownership, facade thinness, acyclic imports, and single projection
  ownership. Green runs the exact accepted semantic-core and nearest consumer
  suites plus import-cycle, compile, spec-verification, lifecycle, coverage,
  and diff checks. Refactor repeats snapshots and the full blocking baseline.

### Accepted extraction graph

```text
model
  ^       ^          ^             ^
  |       |          |             |
fingerprint  builder  runtime_plan  qpu_projection  realization
      \       |          |             |             /
       \      +----------+-------------+------------/
        scientific_semantic_ir.py (public compatibility facade)
```

The arrows denote implementation dependency toward `model`; the public
facade is the only compatibility entrypoint and is not imported by any
internal package. `builder` owns the single source-derived construction
sequence. `qpu_projection` and `realization` consume the already-built core
and return projections/records; they do not rebuild the semantic graph or
invoke a second finite-binder lowering.

### Consumer audit boundary

The initial direct-import audit covers `pipeline.py`, `qpu_ir.py`,
`backend/qasm/lower.py`, `backend/qasm/emitter.py`, `codegen_qasm.py`,
`codegen/openqasm.py`, `physics_ir_lower.py`, `realization_artifact.py`,
`symbolic_ir.py`, and `runtime/evaluator.py`. Their import paths remain
unchanged in this issue; each moved symbol is checked against the pre-change
manifest before any import is redirected.

### Applied process lessons

- `compatibility-authority-boundary`: preserve the facade while making
  canonical authority and diagnostic-only compatibility explicit.
- `coverage-authority-boundary`: distinguish source-derived execution meaning,
  metadata, target capability, and scientific validation; do not claim module
  decomposition as broader workflow coverage.
- `quantitative-traceability`: label counts as source lines, direct consumers,
  test nodes, or artifacts; do not conflate them in review evidence.
- `boundary-completeness`: audit every concrete consumer and producer surface,
  not only the new internal package tests.

### Phase 0 approval requested

`LISS-0548 Phase 0 acceptance 承認`

## Phase 0 acceptance and review result

- Adjudicator approval: `LISS-0548 Phase 0 acceptance 承認`, received
  2026-09-15.
- Review packet: [LISS-0548 Phase 0 design review](../collaboration/reviews/2026-09-15-liss-0548-phase0-design-review.md)
- Same-context review confirmed the six-unit ownership graph, stable facade,
  one-time canonical build boundary, consumer audit scope, and explicit
  exclusion of richer observation semantics and provider work.
- Findings: no blocker; circular imports and duplicate projection construction
  are Phase 1 acceptance risks to be made executable.
- Next gate: `LISS-0548 Phase 1 Red 承認`.

## Phase 1 Red result

- Adjudicator approval: `LISS-0548 Phase 1 Red 承認`, received 2026-09-15.
- Added four structural acceptance contracts for family ownership, facade
  thinness, dependency direction, and one-time canonical build/projection
  ownership in `tests/test_liss_0548_scientific_semantic_ir_red.py`.
- Production implementation was not changed. The four tests fail as expected
  because the `scientific_semantic/` package and facade extraction do not yet
  exist.
- Active-Red ownership is recorded in `docs/testing/active-red-tests.toml`.
- Next gate: `LISS-0548 Phase 1 Red テストレビュー承認`.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0548 Phase 1 Red テストレビュー承認`, received
  2026-09-15.
- The four structural tests were accepted as the bounded decomposition
  contract; no test assertion was broadened during implementation.
- Next gate: `LISS-0548 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0548 Phase 2 Green / Implementation 承認`,
  received 2026-09-15.
- Added `scientific_semantic/` with immutable model ownership, canonical
  fingerprint/builder/runtime/QPU/realization entrypoints, and a stable public
  facade. The existing implementation is isolated behind an internal
  compatibility bridge until each body can be moved safely.
- All existing public imports and `source_id` call signatures remain intact.
- Verification: LISS-0548 structure **4 passed**; semantic-core/consumer
  suite **50 passed, 2 pre-existing QASM expectation failures**; compile and
  diff checks pass. The two failures expect
  `E_QPU_CANONICAL_PROJECTION_UNAVAILABLE` but currently reproduce
  `E_QPU_CANONICAL_PROVENANCE` and are outside this decomposition.
- Next gate: `LISS-0548 Phase 3 Refactor 承認`.

## Phase 3 Refactor result

- Adjudicator approval: `LISS-0548 Phase 3 Refactor 承認`, received 2026-09-15.
- Review packet: [LISS-0548 Phase 3 review](../collaboration/reviews/2026-09-15-liss-0548-phase3-final-review.md)
- The review confirms stable public exports, explicit DTO/function ownership,
  acyclic internal-to-facade direction, and preservation of the `source_id`
  compatibility contract.
- The `legacy.py` bridge is an intentional bounded disposition. It preserves
  runtime identity and behavior while future body migrations proceed one
  family at a time; this issue does not claim that all bodies have moved.
- Verification: structure **4 passed**; semantic-core/consumer suite **50
  passed with 2 pre-existing QASM expectation failures**; compile, lifecycle,
  coverage, and diff checks passed.
- Next gate: none; LISS-0548 is complete.

## Final review and completion

- Adjudicator approval: `LISS-0548 Phase 3 最終レビュー 承認`, received
  2026-09-15.
- Final review packet: [LISS-0548 Phase 3 review](../collaboration/reviews/2026-09-15-liss-0548-phase3-final-review.md)
- The four LISS-0548 Active-Red nodes were removed after their accepted
  contracts passed and the phase sequence completed.
- The `legacy.py` bridge and one-family-at-a-time body migration are explicit
  successor scope; no full body migration is claimed by this issue.
- Process review: no operating-contract deviation or operational problem
  found.
- Lesson written: no new lesson; existing semantic-authority and boundary
  lessons were applied.

## Verification

Semantic serialization/fingerprint snapshots, every known consumer, positive
and unsupported projection cases, full suite, Spec Verification, cycles and
diff checks.

## Process Review

- Outcome: not yet
- Lesson written: existing semantic-authority lessons applied
- Template-feedback path: none
