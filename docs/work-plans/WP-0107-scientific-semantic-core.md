# WP-0107: Scientific Semantic Core and IR authority

| Field | Value |
|---|---|
| Status | **Phase 2 Green bounded consumer migration complete — consumer-wide migration pending** |
| Issue | [LISS-0444](../issues/LISS-0444-scientific-semantic-core.md) |
| Follow-up Issues | [LISS-0476](../issues/LISS-0476-symbolic-ir-consumer-migration.md), [LISS-0477](../issues/LISS-0477-ast-dto-authority-retirement.md) |
| Specification | [Scientific Semantic Core](../specs/staqex-scientific-semantic-core.md) |
| ADR | [ADR 0211](../architecture/adr/0211-scientific-semantic-core-and-ir-authority.md) |
| Detailed follow-up design | [Scientific Semantic Core](../specs/staqex-scientific-semantic-core.md#consumer-wide-follow-up-design) |
| Architecture approval | User approved 2026-08-19 |
| Phase 1 Red approval | User approved 2026-08-19 |
| Phase 2 Green approval | User approved 2026-08-20 |
| Phase 3 representative-slice approval | User approved 2026-08-20 |
| Implementation approval | Granted for the representative QPU IR/QASM projection slice only |

## [DESIGN CHECK]

- **Scope and expected behavior:** Replace the assumption that existing IR/DTO
  artifacts are authoritative with a source-derived, typed Scientific Semantic
  IR design and reviewed migration plan.
- **Specifications and files inspected:** LISS-0440–0443, ADR 0209–0210,
  language vision, AST/parser/typecheck/HIR, Physics/Symbolic/Equation IR,
  Quantum Semantic IR, Algorithm Plan IR, evaluator, continuous lowering,
  examples, tests, and open-work register.
- **Component boundaries:** language front end owns source meaning; semantic IR
  owns typed scientific structure; simulator/QPU/Algorithm Plan consume typed
  projections; adapters and providers remain ports.
- **Applicable constraints:** no hidden classicalization or finiteization,
  source must preserve blackboard physics, `State<T>` remains state-first,
  terminal measurement remains explicit, and no provider SDK/live QPU.
- **Decisions, assumptions, ambiguities:** the current parallel models are not
  presumed salvageable; each must pass authority, reachability, structure, and
  consumer-wiring tests or be migrated/replaced/retired. No technology choice
  is introduced.
- **Included context:** minimal implementation slices proving source → semantic
  IR → consumer wiring and the retirement boundary.
- **Omitted context:** provider credentials, network, S02 numerical migration,
  and broad example conversion before the semantic contract is accepted.
- **Task routing:** architecture reviewer plus deterministic compiler tests;
  no implementation before approval.
- **Input/output evidence contract:** review outputs are prioritized findings,
  file/section evidence, readiness verdict, disposition, and reusable lenses;
  hidden reasoning is excluded.
- **Independent review lenses:** canonical-authority/implementation-reality;
  source fidelity; boundary integrity; type/dimension closure; state/physics
  safety; realization honesty; migration safety; evidence hygiene; phase gates.
- **Verification:** source reachability, structurality, type validity,
  provenance, consumer wiring, no-soft-authority checks, and full regression.

## Work units

### Phase 0 — Architecture design

- inventory every semantic representation and its actual consumers;
- define the canonical Scientific Semantic IR and structural node taxonomy;
- freeze the structural/provenance/type/dimension/exactness/role invariants
  and simulator-versus-`Realize` boundary in the Spec;
- complete the per-path migrate/replace/retire matrix, naming owner,
  migration order, compatibility window, retirement condition, rollback
  trigger, and deletion/unreachability proof;
- define a representative source corpus and positive/negative semantic
  snapshots, including state safety and terminal `measure` cases;
- freeze the migration matrix baseline and its owner/order/exit evidence;
- define the `ssc-semantic-v1` snapshot schema and atomic no-artifact rule for
  unresolved canonical semantics;
- define `SemanticInspectionResult`, legal role/lane transitions, and the
  proof-ID-to-test mapping without creating the Phase 1 fixtures yet;
- treat existing dynamic-lane execution as an unchanged downstream consumer;
  this WP adds no new dynamic execution or provider behavior;
- define source syntax ownership and the migration/deprecation matrix;
- define the first Red tests and explicit non-goals;
- request independent review and Architecture approval.

### Phase 1 — Red (later approval required)

- bounded test/fixture batch only: create the named SSC fixtures, snapshot
  contract checks, and `tests/test_scientific_semantic_core_red.py`; do not
  implement the Scientific Semantic IR, migrate production consumers, or
  delete/rewire legacy paths in this phase;
- tests proving source reachability of accepted relations;
- tests rejecting caller-only/string-only equation evidence;
- tests for role, type, dimension, provenance, and exactness closure;
- tests proving simulator and finite-plan projections consume the canonical IR;
- tests proving superseded paths cannot silently remain authoritative.
- tests proving projections conserve canonical node identity and semantic
  fields, or reject lossy conversion;
- tests proving unresolved canonical semantics emit no consumer artifact and
  that exact/symbolic simulation cannot bypass explicit finite `Realize`.
- no provider SDK, live-QPU submission, S02 numerical migration, solver
  implementation, or production migration is permitted in Phase 1.

### Phase 2 — Green (later approval required)

Implement only the minimum accepted semantic core. Do not add solver families,
provider integrations, or compatibility shims that preserve an obsolete
authority model.

### Phase 3 — Refactor and migration (later approval required)

Migrate the smallest representative physics slice, remove or retire duplicate
paths with evidence, split evaluator responsibilities, and verify examples can
recover the blackboard equation from source.
Use the Phase 0 corpus for unchanged-neighbor regression, record any temporary
compatibility window and deprecation diagnostic, and stop or rollback when a
semantic snapshot or fail-closed invariant diverges.

#### Phase 3 representative slice completed

- QPU IR and the QASM emitter now construct their entry projection from the
  source-derived `ScientificSemanticIR`, and QPU IR retains canonical
  `source_node_ids` and top-level provenance.
- This slice does not claim full consumer migration. AST-derived instruction,
  shape, routing, and finite-lowering helpers remain migration candidates;
  `symbolic_ir` remains a compatibility projection until a separately bounded
  consumer migration proves retirement safety.
- The next migration table must treat `lowering_policy`,
  `explicit_evolution`, and `binder_lowering` as separate AST-derived
  consumers, each with an owner, retirement condition, and acceptance test.
- Provider SDKs, live QPU submission, S02 numerical migration, and solver
  expansion remain excluded.

#### Phase 3 policy/evolution/binder projection batch completed

- `lowering_policy`, `explicit_evolution`, and `binder_lowering` are now
  source-derived fields on `ScientificSemanticIR` and are projected into QPU
  IR. Each projection retains source identity/provenance.
- The complete semantic fingerprint includes these fields, and QPU instruction
  mutations are rejected by an executable-projection fingerprint.
- Evidence: 45 targeted tests and 1636 full-regression tests passed; the
  independent review is `READY` for this bounded batch.
- Old AST helpers, diagnostic-time binder re-lowering, QASM AST fallback, and
  parallel `symbolic_ir` creation remain consumer-wide migration work.

| Consumer | Owner | Current state | Retirement condition | Acceptance evidence |
|---|---|---|---|---|
| `lowering_policy` | Scientific Semantic IR / QPU projection | canonical field consumed | remove old helper after policy migration and fallback proof | Suzuki policy provenance/fingerprint tests |
| `explicit_evolution` | Scientific Semantic IR / target projection | canonical field consumed; target lowering deferred | remove AST fallback after explicit target-capability batch | explicit evolution provenance/fingerprint tests |
| `binder_lowering` | Scientific Semantic IR / finite binder projection | canonical field and provenance consumed | retire duplicate diagnostic lowering after consumer migration | binder provenance/fingerprint tests |
| QASM fallback / `symbolic_ir` | backend and simulator owners | deferred compatibility/diagnostic path | separate reviewed consumer-wide phase | future Issue/Phase approval |

#### Consumer-wide migration Phase 1 Red (approved and created)

- Added `tests/test_liss_0444_consumer_migration_red.py` with six acceptance
  acceptance tests for fallback suppression, legacy helper retirement,
  diagnostic binder authority, `symbolic_ir` retirement, and AST dependency
  removal.
- Red verification: **4 failed, 2 structural assertions passed** with no collection errors. No production
  implementation, helper deletion, fallback change, or migration was performed.
- Phase 2 Green remains separately gated and requires review acceptance of
  these failures.

#### Consumer-wide migration Phase 2 Green (bounded slice completed)

- Explicit evolution no longer enters QASM AST fallback; it rejects with an
  empty artifact when no canonical executable projection is available.
- The two obsolete QPU projection helpers were removed, and
  `qpu_ir_diagnostics()` no longer directly re-lowers binders from the AST.
- Explicit-evolution compilation no longer exposes `symbolic_ir` as a parallel
  live projection. Non-explicit symbolic consumers retain a documented
  compatibility projection until their own migration.
- Finite Suzuki/binder lowering remains a temporary compatibility boundary so
  existing resolved finite behavior and diagnostic codes remain stable.
- Verification: bounded target suites **98 passed**; full regression
  **1642 passed**; `git diff --check` passed.
- Independent review: bounded Green slice `READY`; WP-0107 consumer-wide
  migration remains open.

#### Finite Suzuki/binder canonical instruction projection — Phase 1 Red

- Added `tests/test_liss_0444_finite_instruction_projection_red.py`.
- The contract covers canonical QPU instructions, per-instruction provenance,
  and the prohibition on `lower_unit_to_circuit()` compatibility fallback for
  the already accepted explicit `using Suzuki(...)` finite surface and finite
  binder inputs. This phase does not introduce an implicit finiteization path;
  source-visible `Realize` remains the formal-limit conversion boundary.
- Red verification: **4 failed**, with no collection errors. The failures
  cover both missing canonical gate instructions and both compatibility-fallback
  calls.
- Phase 2 Green requires a separate approval after independent review.

#### Finite Suzuki/binder canonical instruction projection — Phase 2 Green

- The accepted finite `using Suzuki(...)` surface now projects source-derived
  finite gates into canonical QPU instructions. The QPU consumer does not
  re-read the AST on this path.
- Gate opcode, wires, parameters, Suzuki order/steps comments, source node,
  and provenance are preserved through QPU IR and QASM. Canonical Measure
  provenance is also validated.
- Invalid or statically unresolved Suzuki order fails closed: no lowering
  policy fallback, QPU instructions, partial artifact, or QASM is produced.
- Recomputed instruction fingerprints cannot authorize mutation of canonical
  finite gates or terminal Measure instructions.
- The existing AST compatibility fallback remains only for non-finite or
  not-yet-migrated consumers; it is not reachable for valid finite
  Suzuki/binder canonical projection.
- Verification: finite/consumer target suites **26 passed**; full regression
  **1650 passed**; `git diff --check` passed.
- Independent review loop: final bounded review **READY / COMPLETE**. P3
  follow-up: add a dedicated mixed Suzuki+ordinary-gate regression if that
  mixed surface is admitted; current source-filtered validation prevents the
  observed false rejection.
- This completes the bounded Phase 2 Green slice only. WP-0107 consumer-wide
  migration, provider/live QPU, S02 numerical migration, and solver work
  remain outside this phase.

#### LISS-0476 — non-explicit `symbolic_ir` consumer migration — complete

- Phase 1 Red, Phase 2 Green, and Phase 3 refactor/review are complete.
- Ordinary simulator/inspection compilation now uses the canonical Scientific
  Semantic IR without constructing a parallel `symbolic_ir` projection.
- The legacy projection remains only at the named operator/discretization
  compatibility boundary; LISS-0477 and other consumer migrations remain
  separate work.
- Evidence: 49 related tests passed, Python compilation passed, and the
  same-context review is recorded in
  `docs/collaboration/reviews/2026-08-30-liss-0476-phase3-review.md`.

#### LISS-0477 — AST/DTO semantic-authority retirement — bounded QASM slice complete

- Phase 1 Red, Phase 2 Green, and Phase 3 review are complete for the QASM
  missing-canonical-projection boundary.
- Compiled units provide the canonical Scientific Semantic IR to QASM; raw
  units without that projection fail closed before artifact creation.
- Remaining evaluator, Equation/Physics DTO, H1, and Algorithm Plan reads are
  explicitly separate follow-up work and are not claimed complete here.
- Evidence: 4 LISS-0477 tests passed and the same-context review is recorded
  in `docs/collaboration/reviews/2026-08-30-liss-0477-phase3-review.md`.

## Independent review request

> Review LISS-0444 / WP-0107 / ADR 0211 as an Architecture Path design. Do not
> treat existing DTOs, golden fixtures, soft diagnostics, or importable modules
> as proof that a language capability exists. For every claimed capability,
> verify: (1) a real `.sqx` source form can express it; (2) parser, AST,
> typecheck, and HIR retain its structure; (3) the canonical semantic IR owns
> the meaning; (4) a real consumer uses that IR; (5) provenance, type,
> dimensions, exactness, and role boundaries survive; and (6) obsolete or
> parallel paths have an explicit migrate/replace/retire disposition. Review
> whether the proposed architecture will create debt at maturity, even if a
> smaller compatibility patch would be easier now. Check physicist-first
> source fidelity, Never Leave the State, explicit `Realize`, fail-closed
> target behavior, and the exclusion of provider SDK/live QPU/S02 migration.
> Return prioritized findings, evidence paths, readiness verdict, and reusable
> review perspectives. Do not edit files, approve architecture, or request
> hidden chain-of-thought.

## Exit conditions

- ADR and Spec independently reviewed and dispositioned;
- canonical authority and migration/deprecation matrix accepted;
- Phase 1 Red paths and acceptance criteria approved separately;
- implementation remains blocked until typed Phase 1 and implementation
  approvals are recorded.
