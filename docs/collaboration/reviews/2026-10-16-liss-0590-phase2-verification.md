# LISS-0590 Phase2 verification (provisional dirty tree)

Current local commit/actual-SHA revalidation authorized2026-10-16. The dirty-tree
results below are historical baseline evidence. Actual commit,clean state and
fresh per-suite results live in `/private/tmp/liss-0590-sha.v0SnLA/verification.json`
and its command logs,not an evidence-only commit that changes the tested SHA.
Until that actual record reports every required PASS,no full Green is implied.

- Scope:Phase2 minimum implementation of accepted O01–O10;not Phase3 review.
- Status:focused/consumer/adjacent passed;all-blocking failed(copy-smoke).
- Full Green established:**no**. No commit or remote delivery authorized.
- Canonical [spec](../../specs/typechecker-operator-body-successor.md),
  [Issue](../../issues/LISS-0590-typechecker-operator-body-successor.md),
  [trace](../traces/2026-10-15-liss-0590-typechecker-operator-body.md).

## Change / accepted-byte boundary

Only three production files:move the sole281-line operator walk into existing
`typechecking/operators.py`,add declaration-only `operator_context.py`,replace
the old method by ordinary alias plus fresh-Ty static factory in `typecheck.py`.
Public variadic forwarder and bottom private alias remain. Ty/state ownership
stays on the same TypeChecker. No duplicate body or reverse facade import.
Keep receiver/private name,callback recursion,diagnostic order and exceptional
env/depth behavior. Exactly2Ty constructor expressions become factory calls.

Accepted16-test-artifact digest unchanged:
`12426ae6b89a222a40eb0cf25f66cdbe018cc786d7ae75c1b5477d168dfbed3b`.
No test/helper/carrier/fixture/assertion/hash/exclusion change during Phase2.
No dimension/Parser callback repair,additional feature or dependency introduced.

## Tested SHA / environment / commands

Actual HEAD/base:`b5c96f7e4c2a846f41ac8ad5d882f0cb987cd420`,**dirty** production,
accepted uncommitted tests and inherited metadata. Branch:
`codex/liss-0590-typechecker-operator-phase0`. Not a new final committed SHA.
cwd/PYTHONPATH:`/Users/nn0cl/Documents/git/qpex`;macOS27.0.1 arm64,
CPython3.12.6,pytest9.0.3,NumPy2.4.6,PyYAML6.0.3.

External `/private/tmp/liss-0590-green.tQpTBG/` stores per-label exact command,
start/end UTC,exit,SHA/dirty/cwd/env and stdout/stderr (run.py). Root/spec/sanity
declared before implementation in spec;no exclusions. Current source hashes:

| Production file | SHA256 |
|---|---|
| typecheck.py | 2f3f76f79bdbdb54d367397e9474677566801adf0ffaec20642df3b134ed9d7a |
| typechecking/operators.py | dd772d9ea6082191f228ae28d770dbfbabfc7086e64f3fee292677f71c400e9d |
| typechecking/operator_context.py | 24019e0b8a2d7dd6e2f2da329d45db2e1271d43ccba70b66e79d2f0bfc90d487 |

- final-focused:four0590suites,**117PASS8.62s**,exit0,no errors/skips/exclusions.
  Four previous structural Reds resolved without changing accepted tests.
- inherited:nine0583/84/87/88/89guard/ownership/migration suites,
  **162PASS12.80s**,exit0. Real pre/post shape/copy guards and original negative
  mutations remain effective after actual extraction.
- adjacent-consumers:12family/binder/register/Set/numeric/newconsumer suites,
  **90PASS1.04s**,exit0,including real cold import/pickle/pipeline/HIR checks.
- spec:`python3.12 tests/spec_verification/run_all.py`,**161/161PASS**,exit0;
  harness does not report aggregate skip count. Includes actual linked modules.
- root:`python3.12 -m pytest tests/ -q --tb=short`,**2938PASS362.93s**,exit0;
  failures/errors/skips/exclusions0. All4previous structural failures resolved.
  Start2026-10-16T03:57:04.743691Z,end04:03:08.094119Z;command wall363.35s.
- sanity:every applicable real CI repository-sanity run step,**9PASS/1FAIL**,
  exit1. Failure:`Check template copy smoke test`:uncommitted inventory TSV
  `docs/collaboration/reviews/2026-10-15-source-responsibility-inventory.tsv`.
  Same known failure as Red baseline;not waived or turned into a pass. PR-only
  traceability check N/A locally;must run on eventual PR CI.
- implementation-audit PASS:whole moved AST versus original Git under only
  approved annotation/2constructor normalizations;restored facade raw bytes
  equal original Git;219other production files and16accepted artifacts unchanged.
  Total production222files = prior221+one approved context.

## Acceptance / consumer / comparison

O01/O07:actual sole owner/alias/factory and exact Git AST/raw inverse audits.
O02–O05:unchanged behavioral suite including R1actual-site exceptions,live
maps/prior bindings,ordered diagnostics/recursion. O06:real bound aliases,
variadic custom contexts,instance/subclass overrides,unbound self=,fresh real Ty,
ordinary bound/Ty pickle and cold requested imports. O08:real compile_source,
finite/Set/Basis/reverse/register and SV31 module consumers. O09:real post-shape
strict old guards/mutations and readonly hashes. O10:accepted bytes preserved;
current all-blocking/final-SHA gap retained,not waived by focused success.
Exact named test mapping remains in Phase1 trace/accepted review.

Private callers remain in TypeChecker main/assignment/second-quantized checks
and the moved recursion;pipeline/HIR continue to consume the same facade/Ty.
All previous public exports retained even if locally unused. New AST/Protocol
imports add operator-module attributes;no public retirement or __all__ narrowing.
Two cold requested import orders do not establish a complete dynamic cycle-free
graph. Arbitrary custom pickles,all dynamic receivers and past deletion coverage
remain unassessed;no broad functionality/no-regression claim inferred.

Comparable preimplementation Red at the same source SHA/environment:
focused113PASS/4ownership failures,root2934PASS/4same failures;known TSV sanity
failure. Current focused/root both resolve all4;total root cases remain2938.
No new pytest failure in that comparable run. No immutable-main full baseline
rerun claimed. Any additional
failure must remain blocking,not be excluded or moved into a follow-up waiver.

## Structure / route / remaining authority

Actual file lines:typecheck4690→4416 (−274);operators14→310 with281-line actual
algorithm;context39. This is responsibility relocation,not total code reduction
or completion of the remaining4416-line TypeChecker decomposition.
The cohesive281-line walk exceeds150guideline under the explicit Phase0 human
disposition;preserve ordered equivalence in this mechanical move. Future
internal factoring requires separate scope. No hidden body behind a shorter
facade or second state owner. Live numeric structure settings absent;qualitative
rules apply. review-change.py reports committed0/dirty unknown metrics,not true
pending diff size. Whole dynamic graph/semantic-owner metrics remain gaps.
Implementation route:host;review.same_context/weaker,IDs empty,no enabled
large_change override. No required isolated review silently downgraded. No
Phase3 reviewer pass/human final review claimed by this verification record.

Current implementation approval received and used for O01–O10 only. No later
phase or commit inferred. To satisfy source-clean/final-SHA gates,next request:
**LISS-0590 ローカルコミット／実SHAで全blocking再検証承認**。
Proposed commit cohort:bounded0590production,accepted tests/four carriers and
fixtures,current0590records plus inherited accepted WP0175 inventory/TSV and
navigation/lessons changes already carried on this branch. Confirm actual paths
again before staging;exclude unrelated future edits. This request is local only,
not push/PR/merge or Phase3 approval. Post-review remains required;later Phase3
and final review/verification need separate approval. Stop without committing.

The local-only commit/revalidation request above was subsequently approved.
The exact30-file cohort is rechecked before staging;no code/test/fixture edits.
Phase3 is not included:request **LISS-0590 Phase 3 Refactor／review承認** only
after clean-SHA all applicable blocking checks pass. Otherwise report the failure.
