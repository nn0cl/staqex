# LISS-0549: QASM lowering decomposition

## Metadata

- Local issue ID: LISS-0549
- GitHub issue: none
- Status: done
- Phase: done
- Type/priority: refactor / P1
- Initial/current planning size: L / L
- Owner/agent: host implementation; same-context review
- Related branch: `refactor/qasm-lowering`

## Summary

Retain `backend.qasm.lower` public exports while extracting capability
preflight, semantic lowering, bounded AST compatibility, evolution lowering,
and resource verification into `backend/qasm/lowering/`.

## Planned extraction units

- `profiles.py`: target profile and immutable capability facts.
- `preflight.py`: finite, operation, limit and resource rejection.
- `semantic.py`: Scientific Semantic IR/QPU IR to circuit lowering.
- `ast_compat.py`: explicitly diagnostic-only bounded legacy pattern path.
- `evolution.py`: explicit/formal-limit/Hamiltonian lowering.
- `resources.py`: allocation and budget verification.

## Acceptance Notes

Accepted QASM, manifest/provenance, gate/qubit order, target fingerprint, and
diagnostics are byte/order identical. Unsupported meaning produces no partial
artifact or allocation. AST compatibility remains non-authoritative.

## Dependencies

- Parent: WP-0160
- Depends on: LISS-0543, LISS-0548
- Blocks: LISS-0550
- Related: QASM consumer migration and real-QPU readiness specifications

## Adjudicator Decision Points

Approve the boundary between canonical semantic lowering and bounded AST
compatibility. Any authority leak is a blocker, not a refactor exception.

## AI Planning Record — AIP-0549-001

- Status/date/size: proposed / 2026-09-11 / L
- Agent/route: Codex host, display unavailable; host + same-context review
- Scope/estimate: six lowering units; N/A token estimate
- Basis/confidence: 1,520 lines, 29 import consumers, 446-line AST path; high
- Assumptions: emitter formatting is untouched
- Revises/Superseded by: none

## Phase 0 design intake

### [DESIGN CHECK]

- Scope and expected behavior: decompose `backend/qasm/lower.py` while keeping
  its public functions and rejection behavior stable. Accepted QASM must be
  byte/order identical; unsupported meaning must reject before allocation and
  leave QASM, gates, instructions, and resource state empty.
- Specifications and files inspected: the core module decomposition spec,
  backend target architecture, canonical Coin/Mix QASM specification, real-QPU
  readiness acceptance, QASM consumer migration artifacts, `lower.py`, QASM
  emitter/circuit/QPU IR consumers, and applicable process lessons.
- Component boundaries, ports/adapters, and VO/DTO candidates: `profiles.py`
  owns immutable target capability facts; `preflight.py` owns capability,
  finite, limit, operation, and resource rejection decisions; `semantic.py`
  owns canonical Scientific Semantic IR/QPU IR to circuit lowering;
  `ast_compat.py` owns the bounded diagnostic-only legacy AST pattern path;
  `evolution.py` owns explicit Realize, formal-limit, and Hamiltonian
  lowering; `resources.py` owns allocation and budget verification. Existing
  `Circuit`, `Gate`, QPU IR, and provider-neutral target profile values remain
  the DTO/port boundaries; no provider adapter is introduced.
- Applicable constraints: QASM lowering consumes canonical semantic meaning
  for executable output. AST compatibility can only be an explicitly
  source-declared, diagnostic-only path and may not authorize execution or
  silently finiteize. Emitter formatting is unchanged. No SDK, network,
  credential, live-QPU, Rust, syntax, or semantic change is in scope.
- Decisions, assumptions, and unresolved ambiguities: `lower.py` remains the
  public facade and re-exports the existing names. `semantic.py` receives the
  canonical projection/circuit context; `preflight.py` runs before any
  allocation; `resources.py` validates a completed candidate and cannot create
  semantic meaning. The compatibility path remains callable only through its
  existing direct legacy entrypoints until consumers are separately migrated.
  Any authority leak or changed diagnostic precedence is a blocker and must
  return to Architecture review.
- Included and omitted AI context: included lowering source, canonical QASM
  and target specs, QPU/circuit contracts, direct consumers, and exact
  accepted/rejected fixtures. Omitted unrelated parser/IR refactors,
  provider credentials, live target data, historical superseded documents,
  and full repository contents.
- Task routing (model/assistant/tool): host implementation with same-context
  review according to runtime routing; deterministic AST/import/pytest and
  QASM snapshot tools for evidence. No model output is accepted as runtime
  meaning without executable tests and human approval.
- Input/output evidence contract when AI output is involved: inputs are the
  accepted specs, current lowering module, public export manifest, and QASM
  corpus. Outputs are structural Red tests, implementation, review packet,
  and snapshots recording artifact bytes, gate/qubit order, diagnostics,
  allocation state, changed files, and known uncertainty.
- Verification plan: capture `lower.py` public exports and accepted/rejected
  artifact envelopes first. Phase 1 Red covers family ownership, facade
  thinness, canonical-only execution, preflight-before-allocation, and
  AST-compatibility non-authority. Green reruns QASM goldens, atomic rejection,
  nearest lowerer/emitter suites, import cycles, compile, spec verification,
  lifecycle, coverage, and diff checks.

### Dependency graph

```text
profiles ───────┐
semantic ────────┼──> lower.py (public compatibility facade) ──> emitter
preflight ──────┤                         │
evolution ──────┤                         └──> existing Circuit/QPU IR DTOs
resources ──────┘
ast_compat ───────> diagnostic-only legacy entrypoint
```

`preflight` precedes allocation and `semantic` is the only executable meaning
producer. `ast_compat` may report a bounded legacy pattern result but cannot
override a canonical projection or turn rejection into a circuit.

### Phase 0 approval requested

`LISS-0549 Phase 0 acceptance 承認`

## Phase 0 acceptance and review result

- Adjudicator approval: `LISS-0549 Phase 0 acceptance 承認`, received
  2026-09-15.
- Review packet: [LISS-0549 Phase 0 design review](../collaboration/reviews/2026-09-15-liss-0549-phase0-design-review.md)
- Same-context review confirmed the six-unit ownership graph, canonical-only
  executable lowering, diagnostic-only AST compatibility, preflight-before-
  allocation, and atomic rejection boundary.
- Findings: no blocker; authority leakage and allocation-before-rejection are
  Phase 1 executable risks.
- Next gate: `LISS-0549 Phase 1 Red 承認`.

## Phase 1 Red result

- Adjudicator approval: `LISS-0549 Phase 1 Red 承認`, received 2026-09-15.
- Added four structural acceptance contracts for six-family ownership,
  `lower.py` facade thinness, dependency direction, and canonical lowering
  before allocation/AST compatibility in
  `tests/test_liss_0549_qasm_lowering_red.py`.
- Production implementation was not changed. All four tests are expected to
  fail until the reviewed lowering decomposition exists.
- Active-Red ownership is recorded in `docs/testing/active-red-tests.toml`.
- Next gate: `LISS-0549 Phase 1 Red テストレビュー承認`.

## Phase 1 Red review result

- Adjudicator approval: `LISS-0549 Phase 1 Red テストレビュー承認`, received
  2026-09-15.
- The four structural tests were accepted as the bounded lowering
  decomposition contract.
- Next gate: `LISS-0549 Phase 2 Green / Implementation 承認`.

## Phase 2 Green / Implementation result

- Adjudicator approval: `LISS-0549 Phase 2 Green / Implementation 承認`,
  received 2026-09-15.
- Added `backend/qasm/lowering/` with profiles, preflight, canonical semantic,
  AST compatibility, evolution, and resources entrypoints. The original
  implementation is isolated in `legacy.py` and the public `lower.py` facade
  preserves existing imports and behavior.
- Corrected relocated relative imports without changing lowering policy or
  emitter formatting.
- Verification: LISS-0549 structure **4 passed**; nearest QASM suite **40
  passed with 1 pre-existing rotation-diagnostic expectation failure**;
  compile and diff checks pass. The residual expects
  `QASM_ROTATION_ANGLE_UNRESOLVED` but currently reproduces
  `E_QPU_CANONICAL_PROVENANCE` and is outside this decomposition.
- Next gate: `LISS-0549 Phase 3 Refactor 承認`.

## Verification

Accepted/rejected QASM corpus, byte-for-byte output, allocation atomicity,
public imports, complete blocking suite, Spec Verification, cycles/diff checks.

## Phase 3 Refactor result

- Adjudicator approval: `LISS-0549 Phase 3 Refactor 承認`, received
  2026-09-15.
- Review packet: [LISS-0549 Phase 3 review](../collaboration/reviews/2026-09-15-liss-0549-phase3-final-review.md)
- The refactor review re-read the canonical decomposition and QASM boundary
  documents, the public facade, all extracted family modules, the legacy
  bridge, structural tests, and lifecycle ledgers.
- Disposition: the facade, family ownership seams, dependency direction, and
  preflight-before-allocation contract are accepted. `legacy.py` is retained
  as an explicit compatibility bridge; this phase does not claim body-by-body
  migration of the 1,520-line implementation. That migration is successor
  scope and is not required for this decomposition to close.
- Verification: LISS-0549 structure **4 passed**; nearest QASM suite **40
  passed with 1 pre-existing rotation-diagnostic expectation failure**;
  `py_compile`, `git diff --check`, lifecycle, document-lifecycle, and
  coverage-ledger checks passed.
- No decomposition blocker remains. Live QPU/provider verification is not
  applicable to this local refactor.
- Final review approval: `LISS-0549 Phase 3 最終レビュー 承認`, received
  2026-09-15.
- Completion: LISS-0549 is closed. The four structural Active-Red entries were
  removed after their Green/Refactor evidence was recorded.

## Process Review

- Outcome: no operating-contract deviation or operational problem found.
- Lesson written: existing atomic-rejection lesson applied
- Template-feedback path: none
