# LISS-0587 Phase2 provisional verification

Current continuation2026-10-12:human separately approved local commit and
actual-SHA all-blocking rerun. Result pending at this record commit; current
tested SHA/status/commands/UTC boundaries are saved externally in
`/private/tmp/liss-0587-sha-verification.fYIOBG/result.md` and per-scope JSON/logs.
No result or Phase3 approval inferred. All dirty-run results below are historical,
not current completion evidence. No production or accepted test changes in this continuation.

## Scope and authority

Feature Path / phase-2-green. Human separately approved P01–P09/Phase0,
Phase1 execution, Red test acceptance, then Phase2 Green/implementation2026-10-12.
Implementation allowed:yes, accepted partial-filling slice only. Post-review
required:yes, separate Phase3 and final review. No batch or delivery approval.
Local commit/revalidation now approved; no authority for additional implementation.

## Changes and acceptance mapping

- P01–P04:original fill algorithm moved unchanged to evaluation/partial_calls.py.
  Reviewed behavior14 cases retain ordering, identity, spans, error and mutation contracts.
- P05/P08:calls/context/binding/pipes and22-file readonly manifest unchanged;
  seven adjacent suites retain one-hole/stepwise/multi-hole/fusion/move diagnostics.
- P06:exact evaluator class re-export and static function mapping, old class
  module metadata retained; real class/instance/cold-order/pickle tests pass.
- P07:unique successor class and algorithm; old bodies removed, no evaluator
  import, mutable-state owner, wrapper, lazy factory or new abstraction.
- P09:accepted exact projection/mutation guards unchanged; actual live successor
  and real pre/post copied consumers pass. No tests, old fixtures or exclusions edited.
- Independent smoke verifies whole class/method AST against Git b5ad7402,
  real six consumer/package imports and both cold import orders with identity,
  annotation resolution and serialization. Static inventory limitations remain.

## Verification

Tested HEAD and baseline:b5ad7402c184a3a79440271e02dd423c53d8bc36,
dirty uncommitted implementation/tests/docs; cwd /Users/nn0cl/Documents/git/qpex.
macOS27.0.1 arm64 / CPython3.12.6 / pytest9.0.3. All commands use
/usr/local/bin/python3.12. UTC boundaries/commands/environment/exit recorded
in /private/tmp/liss-0587-green.2uQ7ei/<scope>.json; output in matching logs.

| Scope | Result | Evidence |
| --- | --- | --- |
| Focused, three0587 suites | passed48,2.79s,exit0 | focused.json/log |
| Consumer smoke / Git AST provenance | passed six imports and both cold orders,exit0 | smoke.json/log; smoke.py |
| Inherited guards/public imports, six0582–0586 suites | passed143,6.99s,exit0 | inherited.json/log |
| Adjacent, seven readonly partial suites | passed16,0.38s,exit0 | adjacent.json/log |
| Whole root tests/ | passed2621,332.31s,exit0 | root.json/log |
| Spec run_all.py | passed161/161,exit0 | spec.json/log |
| Repository-sanity, actual ci.yml steps | failed:9 checks pass;10th copy-smoke rejects dirty distributed spec,exit1 | sanity.json/log; sanity.py |

PR-only traceability not applicable:PR not created; it is not a local pass claim.
Sanity uses Python3.12 via PATH and exact workflow shell bodies. No override
of source-clean or temporary replacement of distributed spec. No full Green.
Focused/inherited/adjacent have zero failures/errors/skips/exclusions; smoke
counts are checks, not pytest cases. Spec skips unknown (not separately reported).
Root has zero failures/errors/skips/exclusions; totals overlap, do not sum.
Compared with same-environment prior Red focused/root evidence, all four
ownership nodes resolved; no new root failures observed. Pristine base full root
not rerun:baseline root failure comparison unavailable. New failures require
explicit disposition, not test edits or waivers.

After record synchronization, accepted11 artifact hashes, document/test
lifecycle, coverage consistency and git diff --check passed. Runtime source
bytes were unchanged throughout verification/record updates (SHA256):

- evaluator.py:b29b2208f0b017aae3591cf069019955792a493a1042ecc64621a224c8dcccb1
- evaluation/partial_calls.py:b412349081af6a0c84457aea6ec5adff87c2e67ba7743225733a17cd0ae4dca6

## Structure, routing and next gate

Evaluator1014→976 physical lines; successor52, with one class (5 AST-span lines
plus its decorator) and one31-line function. Existing evaluator responsibilities remain owned by WP-0174;
not a claim of complete decomposition or total line reduction. Type and pure
fill operation are cohesive; class mutability/documentation preserved as accepted.
No numeric live budgets. Qualitative responsibility rules applied behind facade.
Review route same_context, implementation host; no enabled large_change section.
review-change.py base/head both b5ad7402 reports dirty-tree unknown; zero
committed metrics do not measure current/untracked work. Complete dynamic
consumer graph and resolved cycles remain unproved, despite both cold orders passing.

Full Green was not established by the dirty run. Local commit and actual-SHA
all-blocking revalidation of this unchanged unit now approved. Commit includes accepted Red
artifacts and phase records already in dirty branch, not hidden new test changes.
Then request Phase3 separately after all blocking pass. No push, PR or merge.
