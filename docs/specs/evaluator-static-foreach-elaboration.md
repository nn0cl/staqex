# Evaluator static `forEach` elaboration successor

Status: accepted — current-main Phase 0 acceptance, 2026-10-05.
Current implementation/review locally complete; actual79d038b2 all-blocking and
human final acceptance passed. [PR #607 delivery](../collaboration/reviews/2026-10-06-liss-0583-delivery.md)
authorized, gated on actual final-head local/CI success; merge not claimed here.
F01–F08 unchanged. Earlier final/delivery pending wording below historical.
Final review/verification explicitly approved2026-10-06; [final record gate](../collaboration/reviews/2026-10-06-liss-0583-final-verification.md)
requires actual finalSHA all-blocking evidence. F01–F08 unchanged; delivery still
separate. Older pending final-approval wording below historical.
Current Phase 3 explicitly approved2026-10-06; [review passed](../collaboration/reviews/2026-10-06-liss-0583-phase3-review.md),
F01–F08 unchanged, no source/test edits. Fresh clean9165d6d1 all-blocking passes;
review-record commit/actual-final-SHA rerun and human final review still pending.
Older pending Phase 3 wording below historical; no delivery permission.
Local commit/actual-SHA all-blocking rerun explicitly authorized2026-10-06;
current gate and external evidence location in the linked guard Phase 2 packet.
Prior uncommitted results below historical; no Phase 3/delivery permission.
Current supplementary design: Scope / Phase 0 start approved2026-10-06 for
the0584 readonly guard disposition. [G01–G07 supplement](evaluator-static-foreach-repair-guard-migration.md)
is accepted via human `LISS-0583 guard移行仕様 G01–G07 と Phase 0 acceptance承認`;
original F01–F08 unchanged. Supplement Phase 1 tests accepted by human2026-10-06;
guard Phase 2 explicitly approved and implemented, committed all-blocking
verification pending ([evidence](../collaboration/reviews/2026-10-06-liss-0583-guard-phase2-verification.md)). Existing Phase 2
source is parked unchanged. No test/hash/source/lifecycle edit authorized by
this supplementary design approval. Implementation permission for it is no.

Current Phase 2 approved2026-10-06 by human
`LISS-0583 Phase 2 Green／implementation承認`. Minimal split implemented;
focused94/consumer77/spec161 pass with accepted tests unchanged. Four structural
Red exclusions retired. Root2422pass/1fail:0584 readonly source guard is outside
the accepted F08 migration scope and needs separate reviewed disposition.
Copy smoke rejects the uncommitted spec,
so no all-blocking Green/completion claim. [Current verification](../collaboration/reviews/2026-10-06-liss-0583-phase2-verification.md).
F01–F08 unchanged; Phase 3/final review/delivery remain separate.
All previous implementation-pending wording below is historical.

Current review2026-10-06: Phase 1 agent re-review passed at clean main6d1b851b,
90passed/4expected structural Red; consumer/adjacent77passed. Merged0584 resolves
the original F05 arithmetic node unchanged. [Current review](../collaboration/reviews/2026-10-05-liss-0583-phase1-review.md)
has human acceptance on2026-10-06 via
`LISS-0583 Phase 1 Red テストレビュー／acceptance承認`.
The existing F01–F08 tests, immutable fixture and bounded three-guard mapping
are accepted unchanged; Phase 2 implementation permission remains no.
F01–F08 and guard disposition unchanged. Earlier pending-repair statements below
are historical; no full blocking Green or new phase approval inferred.

Owner: [LISS-0583](../issues/LISS-0583-evaluator-static-foreach-successor.md),
WP-0174 rank 3. Scope/design start and Phase 0 acceptance are approved in this
attempt. Human `Phase 0 acceptance」の承認` accepts the immediately preceding
dedicated Issue/spec F01–F08 and bounded guard-disposition target without
changes. Phase 1 test execution / bounded guard migration approved on2026-10-05;
test acceptance received2026-10-06 as recorded above; implementation is not approved.
Historical design/implementation exists at local branch
`feature/liss-0583-static-foreach-successor`, tip `b09e3e06`; it is not merged
into current main and is not delivery clearance for this specification.
Recovery: `git show b09e3e06:docs/specs/evaluator-static-foreach-elaboration.md`.

## [DESIGN CHECK]

- Scope and expected behavior: Architecture Path / Phase 0 revalidation of
  static collection sizing, wire expansion and body validation. Preserve
  behavior while moving the 51-line `Evaluator._run_foreach` body.
- Specifications and files inspected: Static Hilbert Kernel, v1 E-05 acceptance
  envelopes, DEC-0005, evaluator/execution/context/calls/compatibility/pipes;
  historical LISS-0583 artifacts and current LISS-0582 repair requirements/tests.
- Component boundaries, ports/adapters, and VO/DTO candidates: proposed
  `runtime/evaluation/static_foreach.py`, context-first
  `execute_static_foreach(context, joint, stmt)`; live state remains Evaluator
  owned. No new port, adapter, VO/DTO, dependency, provider or ADR required.
- Applicable constraints: source-derived semantic authority, public import
  identity, private hook identity, established diagnostics and order; no
  dynamic circuits, new semantics, rollback feature or legacy retirement.
- Decisions, assumptions, and unresolved ambiguities: reuse historical
  successor shape, not old branch wholesale. Bounded repair-guard disposition
  below is accepted for later reviewed Red preparation, not immediate editing.
  Historical five tests are insufficient
  evidence for every behavior clause. Dynamic/out-of-tree overrides unassessed.
- Included and omitted AI context: relevant source/tests/contracts only;
  rank 4–6, Rust, providers, secrets and unrelated backlog omitted.
- Task routing: host analysis / deterministic rg, AST and pytest; normal
  same_context review, empty model IDs, optional large-change settings absent.
- Input/output evidence contract: reviewed Markdown design only; no AI runtime
  payload. Future test assertions must map to the numbered requirements.
- Verification plan: current baseline and consumers below; separate acceptance,
  Red, test review, implementation, Refactor and final delivery gates.

## Authority and consumer inventory

Current normative sources:
[Static Hilbert Kernel](staqex-static-hilbert-kernel.md),
[v1 E-05 envelope](staqex-v1-acceptance-envelopes.md#e-05--static-hilbert-register-surface),
[quantum/runtime decision theme](../architecture/decision-themes/dec-0005-quantum-operations-and-runtime.md).
The classical-boundary slice and ADR 0069 are historical evidence, not the
current source spelling authority. `register(N)` remains rejected by compilation
with STATIC_HILBERT_SURFACE_ERROR even though direct runtime AST supports it.

| Owner / discoverable consumer | Required boundary |
|---|---|
| evaluator.py `_run_foreach` | current expansion body; reads live static_register_sizes; calls `_bind_names` and bind_call |
| evaluation/execution.py:189–191 | actual statement dispatcher calls context._run_foreach; preserve statement order |
| evaluation/context.py | `_bind_names` and other bind_call callbacks already declared; propose typing the existing static_register_sizes reference and hook, not new state |
| evaluation/calls.py | bind_call retains operator resolution and transformation ownership |
| evaluation/pipes.py | ForEachStmt exclusion remains unchanged |
| parser.py, typecheck.py | syntax, opaque Wire typing, bound and body diagnostics remain compile owned |
| hir_legacy.py, scientific_semantic/legacy.py, pipeline_legacy.py | source-derived/projection consumers; no migration or removal in this scope |
| backend/qasm/lowering/legacy.py, qpu_ir.py | backend emission consumers; preserve gate order and authority |
| cli/host/run/runtime facade/private rational consumer | actual evaluator import consumers; preserve complete public manifest |

In-tree `_run_foreach` search finds its definition and execution dispatch.
Static inventory is a lower bound, not proof that the private hook is unused.
Dynamic/out-of-tree consumers and global cycle resolution remain review gaps.

## Accepted requirements F01–F08

| ID | Behavior and minimum executable evidence for Red review |
|---|---|
| F01 | A declared positive register expands in member order, then body statement order. Recording callbacks verify 1 and multiple members, two different operations, wire names `__foreach_<element>_<index>`, zero-ket/span, call span/operator identity, logs=[]/inspect_out=None, Joint result threading and empty body. |
| F02 | Missing/non-register/dynamic, zero and negative bounds retain exact FOR_EACH_DYNAMIC_BOUND_ERROR message and invoke neither binding nor operation callbacks. Cover named map and direct AST forms, register wrong arity/nonliteral argument; source measurement-dependent bounds retain compile diagnostics. |
| F03 | Bound 1024 is admitted; 1025 fails with exact STATIC_HILBERT_RESOURCE_ERROR before callbacks, without truncation. Test the limit with lightweight recording callbacks, not a 2^1024 state allocation. |
| F04 | Unsupported ExprStmt/non-Call body has the existing first message; non-Var/non-apply callee, wrong arity, non-Var/wrong element target have the existing second message. Preserve current order: each member is bound before its body validation; an earlier valid operation can precede a later body error. No new prevalidation, atomicity or rollback promise. Bound rejection in F02/F03 is distinct from body rejection. |
| F05 | Direct runtime AST `register(positive literal)` remains supported as current characterization only; compiled historical spelling remains rejected. Opaque element index/arithmetic and Measure/Snapshot rejection remain compile owned. Existing Kernel, Hilbert, parametric and semantic/QASM suites remain blocking. |
| F06 | Dedicated successor owns the only expansion body; Evaluator has no `_run_foreach` body and its installed hook is the identical successor function. Inspect real installer mapping/setup, invoke actual execution entrypoint, prove live state/reference use and absence of a second state owner. New module has no runtime evaluator import/cycle. No algorithm copied into execution.py. |
| F07 | Complete frozen wildcard/direct import manifest and original identities remain unchanged, including repaired ten names plus ForEachStmt and MVP_MAX_LOGICAL_QUBITS. Keep these evaluator re-exports even when internally unused. No restrictive __all__, public successor import or manifest regeneration. Cold actual-consumer imports and real capture/cmp remain blocking. |
| F08 | Only the authorized expansion body/wiring/context declarations move; every unrelated body and accepted plan-eligibility behavior remains unchanged. Repair-base guard transition below is reviewed and tested before implementation, never adjusted opportunistically after failure. |

EARS: When a static loop executes, the runtime shall preserve member/body order
and original binding semantics. When a bound is invalid or exceeds the accepted
budget, it shall reject before wire binding. When the body is invalid, it shall
preserve the existing error and the point in the execution sequence at which it
is raised. When callers import existing evaluator names, objects shall retain
their original identity.

## Accepted successor and structure disposition

Successor owns sizing/validation/expansion only; calls existing bind_call and
live context._bind_names. Use the current live static_register_sizes reference
with an explicit context annotation, not a copied dict. Switching to an
overridable getter could change private override behavior and is not proposed.
Type-only context/Joint imports avoid runtime cycles. Keep compatibility wiring
small and underscore-imported on evaluator so no public name is added.

Current physical lines: evaluator1149, execution463, context275,
compatibility317, calls532. Historical successor80 lines is evidence, not a
new-source budget or an exact implementation prescription. Qualitative
disposition: add a dedicated responsibility module instead of enlarging the
already broad execution/calls bodies; leave their unrelated bodies intact.
Numeric structure settings are absent; resolved logical ownership/cycle and
dynamic graph metrics remain unknown, not zero.

## Accepted disposition of LISS-0582 repair-base guards

Repair R05 used base423c003b to prove an import-only repair. Current base is
`a287be51da358eed195f836afa21b07286128940` (PR #605). Two evaluator snapshot
tests and the compatibility.py file-hash case in
`tests/test_liss_0582_public_import_repair_red.py` would reject a legitimate
body move. They may not be silently rehashed, skipped or deleted.

F08 disposition is accepted; after separate Phase 1 execution approval,
Phase 1 may propose a reviewed guard migration:
freeze audit evidence of the old snapshot scope/base; replace whole-file
freezing for those three bounded guards with structural preservation of all
unaffected imports/declarations/bodies and explicit tests of the only allowed
delta (one successor, installer import/function/setup, hook and context typing).
Use provenance-stamped immutable baseline fixtures if needed, not git availability
as a production/test runtime prerequisite. Inspect the migration diff and map
each old protection to a successor assertion at Red review; absence of an
equivalent assertion is a blocker. No blanket exemption for future refactors.

R01–R04 persistent compatibility, remaining protected plan_eligibility,
orchestration, accepted ownership test, frozen JSON/generator/cases and byte
comparison remain unchanged and blocking. Phase 0 changes none of these tests.
Later rank4–6 migrations need their own reviewed guard disposition.

## Historical branch / current evidence and gates

Historical tip b09e3e06 descends from423c003b, not the repaired main. Its five
focused tests cover structure/identity and one QASM example, not all F01–F08.
Static import comparison identifies twelve dropped public bindings: EvolveExpr,
ForEachStmt, MVP_MAX_LOGICAL_QUBITS, Measure, OpAttr, OpBin, OpBinder, OpCall,
OpIndexed, OpPauli, OpPow, replace. Do not merge/cherry-pick old implementation
or copy stale done/approval wording as current acceptance. No matching remote
branch or PR was found on2026-10-05; local historical branch is retained.

Fresh Phase 0 evidence at clean a287be51: baseline65 and adjacent41 pass,
exit0/failures0/errors0/skips0. Exact selectors/environment/times in the trace.
These are scoped design evidence, not whole-repository Green. Root/spec/sanity
not_run in this Phase 0; earlier merged-main verification is historical.

Human acceptance of this current dedicated Issue/spec, F01–F08 and bounded
guard disposition / Phase 0 is recorded on2026-10-05. Phase 1 execution was
separately approved; current tests give four structural Red nodes and one F05
compile mismatch (opaque element arithmetic unexpectedly accepted). This is
not behavior-preserving extraction work and needs human disposition before
Green; do not relax F05 or hide the failure. See the
[Phase 1 packet](../collaboration/reviews/2026-10-05-liss-0583-phase1-review.md).
Next: separate test review/acceptance and the F05 scope decision,
Phase 2 implementation, Phase 3, final review and push/merge approval follow.
No next-phase or delivery permission inferred from historical approvals.

Update2026-10-05: human `修復の設計開始承認` selects separate repair
[LISS-0584 R01–R07 design](opaque-foreach-wire-arithmetic-repair.md), not expansion
of this extraction. F05 remains unchanged. Human
`専用Issue/spec R01–R07 と Phase 0 acceptance` subsequently accepts0584 design
unchanged on2026-10-05; repair Phase 1 execution subsequently approved and tests
prepared. [0584 test acceptance](../collaboration/reviews/2026-10-05-liss-0584-phase1-review.md)
received2026-10-06;584 implementation separately approved and guard implemented.
[584 verification](../collaboration/reviews/2026-10-06-liss-0584-phase2-verification.md)
has focused Green but unresolved all-blocking sanity;0583 test acceptance remains pending,
and Green/delivery require the repair. Prior scope-decision request above is
historical to the Phase 1 packet, not an unresolved choice of repair ownership.

Human `はい。` on2026-10-06 approves the named0583 test carrier and three F08
guard transitions for local dependency commits under the
[split record](../collaboration/reviews/2026-10-06-liss-0584-commit-scope.md).
No assertion change, blanket0583 acceptance or0583 implementation authorized.
