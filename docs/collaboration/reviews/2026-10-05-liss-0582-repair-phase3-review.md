# LISS-0582 public-import repair — Phase 3 review

## Review packet

- Scope: Feature Path / Phase 3, LISS-0582 / WP-0174 / AIP-0582-002 (M), accepted R01–R07. Human `Phase 3 Refactor／review` received 2026-10-05. No final verification, human acceptance, delivery or downstream implementation approval inferred.
- Canonical documents: [repair specification](../../specs/evaluator-public-import-compatibility-repair.md), [eligibility specification](../../specs/evaluator-runtime-plan-eligibility.md), AT-TDD process, runtime execution model, readiness, runtime-routing, source-code-quality, verification-policy, definition-of-done and process-lessons policy/live log.
- Changed files this phase: this packet, representative trace, Issue, both spec status notes, WP and lesson application status. No source, tests, fixture, generator, baseline JSON or lifecycle assertion change.
- Isolation: effective `same_context`, weaker than separate_context; reviewer role switch with artifacts/diffs/tests/output re-read from disk, no implementation performed during review. Model IDs empty, implementation host. Human Adjudicator remains separate.
- Result: bounded code/contract review passed; final-SHA local evidence must pass after this documentation commit before reporting Phase 3 complete. Remote CI and delivery remain pending, not waived.
- Next approval required: final verification / human final review (phase), not push/merge or later feature work. Post-review yes; batch N/A. Source implementation permission remains bounded by accepted import-only repair; no broader change authorized.

## Re-read implementation and named failure scenarios

Inspected production diff against base423c003b, evaluator import surface and actual installer invocation, complete plan_eligibility/orchestration/compatibility bodies, complete 37-case accepted repair tests and five original ownership tests, real capture generator/case TOML, compiler consumer import sites and rational private consumer. Re-read Phase 2 packet and external final-SHA XML/spec/sanity evidence; not merely its summary.

1. A direct import could resolve to a copied/wrapped object: ten `is` assertions require original ast_nodes/dataclasses objects; no alias or direct ast_nodes_legacy route added.
2. Import hygiene could silently shrink wildcard exports: actual `import *` exact baseline manifest and original identity checked; no new __all__, extra public names or manifest rewrite.
3. Capture determinism could pass while the frozen contract drifts: real fresh-process output compared byte-for-byte with unchanged JSON; six module inventories and three complete runtime/QASM/diagnostic payloads/hashes retained.
4. Warm imports could hide a consumer-first cycle: actual cli, host, run, runtime and scientific_semantic.legacy imported first in separate processes; legacy wrong-authority rejection uses original KernelDiagnosticError. Private rational `_apply_op` identity and behavior exercised.
5. A short facade could hide duplicated bodies/state: base-versus-head executable evaluator AST comparison is exact; complete successor/installer/orchestration unchanged and hash-protected. Installer aliases point to successor functions; canonical orchestration calls policy directly. No old bodies or new mutable state owner restored.
6. Red retirement could hide still-failing acceptance: all37 unchanged accepted cases pass; five lifecycle entries retired without test skips/xfails/exclusions. Root suite includes all acceptance files.
7. Repair guards could silently block a legitimate later feature: snapshots explicitly bind R05 to repair base. Later owner changes require reviewed guard disposition and new-SHA/merge-result evidence, not an unapproved hash refresh.

## Findings and dispositions

| Finding | Disposition / evidence |
|---|---|
| Current entry points still said Phase 3 unapproved / post-commit checks pending | apply: synchronize Issue phase/status, WP and both spec status notes; preserve Phase 2 evidence as historical, link its actual 93c1c86a final-SHA results |
| Internally unused imports are reachable public compatibility surface | already closed: explicit original-route imports/comments; actual wildcard/direct identity contracts and frozen capture agree; no removal proposed |
| Evaluator remains1149 lines, installer317, successor181, orchestration154 | retain bounded structure: this repair adds import surface only, no executable bodies. No numeric source_structure settings exist; qualitative review covers underlying bodies, not facade count alone. Further decomposition/legacy retirement would violate import-only R05 and needs separate scope |
| Future full-file/AST guards need lifecycle disposition | out of scope for changing assertions now: accepted tests immutable; downstream approval/verification still required under R07; live lesson reapplied |
| Dynamic/out-of-tree consumers, full resolved cycles and semantic module metrics unknown | explicit gap: cold actual consumers and original-route identity cover discoverable compatibility; no claim of global audit or metric zero |
| Remote CI / original PR head / downstream merge results unverified at repaired head | delivery blocker, not silently satisfied by local success; no push/merge authorized or performed |

No blocking code finding in the approved repair. No speculative source refactor: explicit imports/comments already readable, and additional reshuffling offers no necessary reduction in review cost while risking the frozen compatibility contract.

## Specification reconciliation

| Clause | Change / evidence / remaining boundary |
|---|---|
| R01 | ten explicit imports, original route and object identity; ten parameterized tests |
| R02 | original wildcard surface, identity and no __all__; exact accepted manifest test |
| R03 | unchanged generator/cases/JSON; actual capture equality, six inventories and three complete payloads |
| R04 | retained public/private hooks; five consumer-first cold imports, legacy error identity, rational regression; adjacent suites |
| R05 | only imports/comments in production; exact executable AST and protected owner/file hashes; no assertions changed |
| R06 | focused/consumer/adjacent separately reported; full local blocking checks rerun after review-record commit; remote applicable CI remains not_run until separately authorized delivery |
| R07 | no push/merge/rewrite or later code propagation; downstream guard/new-SHA/merge gates explicitly retained |

## Verification and routing

Reviewed SHA `93c1c86a56a80a14ff13e2cfd51700b95e789f24`, clean at review entry; baseline `423c003b0b39c292731f6a8c7456a0b40cbd03f2`. Environment macOS27.0.1 arm64 / Python3.12.6 / pytest9.0.3, cwd `/Users/nn0cl/Documents/git/qpex`.

Fresh reviewer scoped reruns at reviewed SHA: focused37, consumer8, adjacent52 pass, exit0, failures/errors/skips0, no exclusions. Evidence `/private/tmp/liss0582-repair-phase3-{focused,consumers,adjacent}.xml`; XML holds exact start/duration and end=start+duration. Exact file selections remain in the representative trace. Executable AST comparison against actual git base passed; `git diff c7c72697..HEAD --name-only tests scripts docs/testing/refactor-baseline.json` empty.

Phase 2 all-blocking evidence independently read: root2322, spec161, sanity11 and capture/cmp passed after commit93c1c86a; external `/private/tmp/liss0582-repair-phase2-final-handoff.md` maps SHA/environment/commands/times/XML/logs. These results are not transferred to a later documentation SHA without rerunning.

`review-change.py --root . --base BASE --head HEAD` JSON stored `/private/tmp/liss0582-repair-phase3-routing.json`: normal same_context, no enabled large-change override or exclusions. At inspected SHA:1111 changed lines /12 files, production12 changed lines, max implementation1149. Missing/ambiguous logical ownership for evaluator/test and unresolved cycles remain explicit gaps; missing large_change section preserves normal routing, not an invented numerical waiver.

Declared blocking commands unchanged from Phase 2: full `pytest tests/ -q`, spec runner, real capture/cmp, all11 inspected local CI sanity run blocks and all three scoped selections. After this documentation commit rerun all of them, preserve evidence outside the tree as `/private/tmp/liss0582-repair-phase3-committed-*.xml`, spec.log and final-handoff.md plus unique sanity results directory. Do not add an evidence commit afterward without another all-blocking run.

Failure comparison: fourteen original focused failures resolved with passing23 retained; consumer/adjacent still green. Comparable local pre-repair root baseline not run; full-root new/resolved comparison unavailable. Existing Ubuntu CI2285 is not same-environment evidence. No new assertions, fixture edits, moved failures, exceptions, expected-baseline regeneration or hidden diagnostic/order change.

## Reviewer empathy / handoff

### 変更の要約 (PR Summary)

公開名10件を元のオブジェクト・経路のまま復元した修復をレビューした。Phase 3でソース変更は不要と判断し、承認・検証・残存ゲートの文書を同期する。実行ポリシーは successor、ルーティングは orchestration、状態所有は Evaluator のまま。

### 残存リスク・検証の溝 (Verification Gap)

動的／外部consumerと全依存グラフを網羅したという主張はしない。GitHub CIと後続ブランチ・merge-resultは未検証。人間の重点確認は「未使用import＝削除可能」ではない公開契約、R05修復snapshotの有効範囲、Phase 3 agent passと最終承認／deliveryの区別。

Next safe action: once post-commit checks pass, request final verification approval. No issue marked done, no completion process review claimed. Use representative trace/spec and external final-SHA evidence to resume; do not rely on chat memory.

## Evidence links

- Representative trace: [LISS-0582](../traces/2026-09-29-liss-0582-runtime-plan-eligibility.md).
- Detailed implementation evidence: [Phase 2](2026-10-05-liss-0582-repair-phase2-verification.md).
- Accepted tests/review: [Red acceptance](2026-10-05-liss-0582-repair-red-acceptance.md).
