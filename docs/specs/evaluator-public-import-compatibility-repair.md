# Evaluator public-import compatibility repair

Status: accepted — R01–R07 and Phase 0 accepted 2026-10-05 by
`修復仕様 R01–R07 と Phase 0 acceptance`. Scope/design start previously
approved by `互換性修復の Scope／Phase 0 設計開始`. Phase 1 Red execution
approved by `Phase 1 Red（受入テスト作成）承認`; same-context Red review
passed; human test acceptance approved by `Phase 1 Red acceptance を承認`
on 2026-10-05, reviewed tests unchanged.
Phase 2 Green execution/implementation approved by `Phase 2 Green／implementation`
2026-10-05; import-only repair passed all local blocking checks at93c1c86a.
Phase 3 approved by `Phase 3 Refactor／review` 2026-10-05; code review passed,
no source/test refactor required; all local blocking checks passed atc2112a4f.
Final local verification/review approved by `final verification／最終レビュー`
2026-10-05; final status-commit checks passed at d6f7e917. Separate delivery
approval received; PR #604 merged at 458fcbe6 with all PR/main CI checks and
actual merge-result local checks passed. Documentation-only closeout approved
by subsequent `続けて`; no downstream implementation authorization inferred.
Planning owner: [LISS-0582](../issues/LISS-0582-evaluator-runtime-plan-eligibility.md),
AIP-0582-002 / [WP-0174](../work-plans/WP-0174-evaluator-residual-responsibility-successors.md).
This supplements the accepted [eligibility boundary](evaluator-runtime-plan-eligibility.md).

## Evidence / accepted boundary

Repair base: PR [#604](https://github.com/nn0cl/staqex/pull/604) head
`423c003b0b39c292731f6a8c7456a0b40cbd03f2`.
[CI run 37038460927](https://github.com/nn0cl/staqex/actions/runs/37038460927):
Repository sanity failed capture-baseline/cmp; root 2285 passed and spec job
passed. Commit `7620eb8c` removed ten imports as unused. Without `__all__`,
these were public names; earlier import-hygiene review missed the export contract.

Fresh capture at base: all six module manifests differ only by ten missing
evaluator names; all three runtime/QASM/diagnostic payloads and hashes match.
cmp exit 1, byte 9065 / line 362; no added names.

| Restored names | Original object / import route |
|---|---|
| EvolveExpr, Measure | compiler.staqex.ast_nodes facade |
| OpAttr, OpBin, OpBinder, OpCall, OpIndexed, OpPauli, OpPow | same AST facade |
| replace | dataclasses.replace |

Nine class objects are defined in ast_nodes_legacy but re-exported by ast_nodes.
Retain that existing facade route; do not introduce direct legacy dependencies,
copies, wrappers or new types. Restore explicit compatibility imports/comments
only in production. plan_eligibility retains execution policy, orchestration
retains routing, Evaluator retains state/private hooks. No old bodies restored.
No VO/DTO, port/provider, dependency, export installer, `__all__` restriction,
legacy retirement, language-semantic change or new ADR proposed.

## Accepted requirements R01–R07

| ID | Required behavior / test evidence |
|---|---|
| R01 | All ten names directly import from runtime.evaluator and are identical (`is`) to ast_nodes/dataclasses objects. Ten explicit parameterized identity cases; missing entrypoint resolution outside exception assertions. |
| R02 | Wildcard import exposes every baseline evaluator public name, including the ten, with original identity. Exact manifest comparison; no removed/accidentally added public names or new restrictive `__all__`. |
| R03 | Real capture script succeeds then generated baseline is byte-identical to unchanged checked-in JSON: six module inventories and three complete payloads/hashes. Use fresh processes, not cached imports. Existing CI cmp is original evidence; add pytest equality regression because existing generator tests only check determinism/schema, not frozen-baseline equality. |
| R04 | Existing Evaluator, EvalResult, MeasureResult, KernelError, KernelDiagnosticError, ClassInstance, EnumValue and private `_apply_op` remain available. Smoke actual cli/host/run/runtime facade/scientific_semantic.legacy consumers and rational private consumer; no import cycle introduced. |
| R05 | Only compatibility imports/comments change in production; executable evaluator AST and successor/installer/orchestration unchanged. Existing five ownership tests, baseline JSON/generator/case TOML and accepted tests unchanged. No duplicated implementation/state owner. |
| R06 | Focused repair, consumer and adjacent evidence reported separately. Root pytest, spec runner, capture/cmp and all applicable CI jobs pass at final SHA after final commit; no skipped/red bypass or weakened assertions/exclusions. |
| R07 | PR #604 delivery resumes only at green repaired head. Carry compatibility through later dependency branches with explicit new-SHA/merge-result evidence; no force push/history rewriting or later implementation copied into repair. A different downstream manifest mismatch requires separate diagnosis/disposition. |

EARS: When a consumer imports an established evaluator name, the facade shall
return the original object. When the baseline is captured, it shall equal the
frozen contract. Republishing symbols shall not move execution policy back.

## Actual consumers / limits

AST inventory at base: 116 direct evaluator import statements in compiler/tests/scripts.
Compiler consumers: cli, host, run, runtime/__init__, scientific_semantic/legacy.
Private import: tests/test_classical_rational_red.py `_apply_op`.
Hook consumers: 0544/0560/0561/0581 and 0493–0499 suites. Static inventory does
not exhaust dynamic/out-of-tree callers; lack of in-tree callers for the ten
is not permission to remove public names. Global cycles unassessed.

Frozen JSON SHA256:
`1dcc3848030fdf48f3c44ebbe8951853b1698cce2ffd75c713d213e22dc99692`.
Do not regenerate this expected contract or modify its generator/case TOML to
make CI pass. Numeric structure/large-change settings absent; qualitative
ownership review remains required. Routing host/same_context, empty model IDs.

## Historical phase verification and gates

Fresh existing focused/consumer/adjacent 52 passed, 0 failures/errors/skips,
exit 0, 0.543s; 2026-10-05 10:31:27.839192–10:31:28.382192 JST.
Environment macOS 27.0.1 arm64 / Python3.12.6 / pytest9.0.3; source base above.
No new source/tests. Full local root/spec not_run this phase; remote root/spec
successes do not clear the failed baseline or establish full Green.
Counts/cause recorded durably here; exact commands/hash evidence in
[representative trace](../collaboration/traces/2026-09-29-liss-0582-runtime-plan-eligibility.md).

Human acceptance received for unchanged R01–R07 and the Phase 0 evidence.
Separate Phase 1 Red execution approval received 2026-10-05; the new repair
suite has 14 expected failures and 23 passes. Consumer regression 8 pass;
adjacent/ownership 52 pass. See the [test mapping and review request](../collaboration/reviews/2026-10-05-liss-0582-repair-red-acceptance.md).
Fresh same-context review reproduces14 expected failures/23 passes, consumer8
and adjacent52 pass; tests unchanged. Human review request
`Phase 1 Red テストレビュー／acceptance` is not an implementation decision.
Human `Phase 1 Red acceptance を承認` accepts this unchanged reviewed test set.
Separate `Phase 2 Green／implementation` approval received; restored nine AST
facade exports and dataclasses.replace without altering execution bodies.
Fresh focused37, consumer8, adjacent52 and spec161 pass; frozen capture/cmp
matches. Active-Red entries retired, accepted tests unchanged. Full root2322
passed; these are provisional dirty-tree results.
Phase 2 post-commit local root2322/spec161/sanity11 and all scoped checks passed
at93c1c86a; evidence independently read during approved Phase 3. The
[Phase 3 review](../collaboration/reviews/2026-10-05-liss-0582-repair-phase3-review.md)
passed with source/tests unchanged; post-commit local checks passed atc2112a4f.
Human final local verification/review approved 2026-10-05; see the
[final record](../collaboration/reviews/2026-10-05-liss-0582-repair-final-verification.md).
Final status-commit local checks required. Next gate: separate delivery
authorization. R06/R07 remote CI and delivery evidence not yet satisfied;
no delivery or later implementation approval inferred. Issue not done.
Delivery approval does not waive these gates or authorize baseline weakening.

## Current delivery status — 2026-10-05

The historical final gate above has been satisfied for PR #604, not waived.
LISS-0582 is done; WP-0174 remains active. See the representative trace's
current closeout section for exact head/merge SHAs, focused versus all-blocking
results, environments and PR/main CI links. R01–R07 remain unchanged.
R07 downstream propagation and R05 guard disposition require separately
approved later feature work; this repair does not claim those branches cleared.
