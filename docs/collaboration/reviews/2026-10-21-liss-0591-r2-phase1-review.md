# LISS-0591 R2 Phase1 test review —2026-10-21

## Review packet

- Result:PASS for the bounded test correction;no actionable test finding.
  This is not human test acceptance,implementation permission or product Green.
- Approved scope:Phase1 review execution only. Reviewer role re-read files from
  disk;no production/test/fixture change during review.
- Canonical agreement:[P/B/E specification](../../specs/parser-operator-primary-successor.md),
  [Issue](../../issues/LISS-0591-parser-operator-primary-successor.md),
  [WP0175](../../work-plans/WP-0175-source-responsibility-inventory.md).
- Actually inspected:3 R2 test files,0591 ownership/behavior tests and support,
  0590/0592 real readers/copy callers,actual operators/context/parser Git source,
  immutable manifests;readiness,AT-TDD/testing,verification,source quality,
  routing,same-context template and applicable process lessons.
- Candidate22-artifact cohort:
  `467971d66fb895fc6364d40b8f5580b9c62f715c247fe2832c892885f5030bb9`.
  Reversing only approved3 test deltas recovers exact accepted old cohort
  `68d6eef02b5e18a01ed4e3f4fef22c95ae740c71a57881b56b65708f3f1b5547`.
  Neither historical hash nor immutable evidence regenerated.

## Findings / dispositions

| Scenario inspected | Disposition / evidence |
|---|---|
| E01 export widening hidden by subset comparison | Closed with evidence:current P08 assertion is strict equality for3 modules;new fresh-process wildcard compares exact4 names and original object identities. Existing0592 R04 remains unchanged and fails for the real mismatch |
| E02/E04 missing,wrong,extra or duplicate declaration accepted by inverse | Closed with evidence:exact literal wiring;independent Git-built roots pass normal readers and reject mutations,including wrong variable name and reordered declaration |
| E03 EOF cleanup weakens arbitrary raw preservation | Closed with evidence:exact2-LF historical suffix required before removing1 LF in new serialization only;missing/extra LF,whole/mixed CRLF and CR rejected. Original raw facade inverse equals Git |
| E05 edits outside3 new tests or stale baseline replacement | Closed with evidence:exact inverse test-delta cohort recovery above;6 carriers match original closed substitutions. Candidate fingerprint unchanged during review |
| E06 missing setup mistaken for mutation protection | Closed for new controls:30 persistent guard/R1 nodes pass;independent20 reader positives/120 rejections. Existing40 live-origin guard cases remain setup-blocked Red,not counted as independent protection |
| E06 copied roots collapse to one shape | Closed with scoped evidence:unchanged8 Parser×TypeChecker×repair copy cases and1 distinct-root case pass on independently corrected data-only input. Only fixture input roots/defaults redirected;no guard assertion altered,no proposed runtime imported/executed |
| E07/E08 review pass treated as implementation/full Green | Retained blocker:all actual live failures remain blocking;human exact-cohort acceptance and separate Phase2 approval required. No exclusion or source repair made |

No blocking test-correction finding remains. Coverage is bounded to the named
scenarios,not a proof of every dynamic import,grammar or custom serialization.
The four original exported objects also retain actual identity independently;
the wildcard test's later identity assertions still need post-fix Green execution.

## Fresh verification

SHA `dca93187f50594b0417ae88067154baaf3c0ea7c`,dirty branch
`codex/liss-0591-repaired-baseline`;macOS27.0.1 arm64,CPython3.12.6,pytest9.0.3,
explicit PYTHONPATH=repository. No errors/skips in the pytest runs below.

| Run | Result |
|---|---|
| focused4 modules |202 nodes:157 PASS/45 Red (43 exact wiring,2 actual exports) |
| new22 guards + R1 8 |30 PASS;53 deselected only by this explicitly scoped command |
| existing0592 repair4 modules |114:90 PASS/24 FAIL (23 wiring,1 actual export) |
| extended inherited18 modules |428:422 PASS/6 FAIL (wiring) |
| adjacent6 modules |31 PASS |
| adjacent9 named operator/binder/Dirac modules |42 PASS |
| spec compliance |161/161 PASS |
| independent Git/raw/copy probe |20 reader positives,120 rejections,8 copy shapes+1 distinct case PASS |
| cohort/raw scope audit |PASS;P/B/E rows unchanged |

Focused/repair counts and cause groups reproduce recorded Phase1 results.
Prior temporary artifacts are unavailable,so exact prior JUnit-ID comparison
is unavailable;the current complete failure IDs are retained afresh. Inherited
and adjacent commands are explicitly different/wider selections than historical
293/39 runs;do not label428/42 as the same old suites. No new failure class was
observed beyond the named wiring/export causes;not a whole-root regression claim.
Root/all-sanity/final committed-SHA verification:not_run,not required to prove
this bounded Phase1 test-review gate. Required before later Green completion.
Whole-tree diff whitespace still fails for the uncorrected operators EOF.

## Structure / effective routing / gaps

Review route:same_context,weaker than separate_context;implementation host,
empty model IDs,no enabled large_change section. Tool routing JSON flags dirty
working-tree metrics unknown;its base=head zero committed diff is not a measure
of pending work. No required independent review was silently downgraded.
Measured test modules:guard support264,guard tests287,consumers124 physical
lines;maximum functions27/65/24 lines. Retain direct case/reader tables rather
than speculative abstractions. No configured numeric structure override.
Unchanged Parser3584/class3392 remains WP0175-owned residual responsibility,
not excused by this test review;whole dynamic dependency/cycle proof unassessed.

## Evidence links / next approval

- [Representative trace](../traces/2026-10-16-liss-0591-parser-operator-primary.md).
- Canonical Register:not changed;existing specification remains canonical.
- Fresh exact commands,UTC times,environment,exits,JUnits,per-file cohort hashes,
  failure IDs and independent scripts:
  `/private/tmp/liss-0591-r2-review-20261021.Vlft4I/`.
  These are temporary evidence;canonical decisions/cohort/results are recorded
  here so loss of temporary files never authorizes accepting missing evidence.
- External audit first used the guard-evidence namespace for separately pinned
  behavior.json and failed setup;retry used the actual namespace/cohort checks.
  No production/test fix was made to satisfy that external check.
- Requested:**LISS-0591 R2 Phase1 Red テストレビュー／acceptance承認**.
  Approval type:phase/test acceptance of exact candidate above. Implementation
  allowed:no;post-review required:yes;execution batch:N/A. Human decision pending.
  After acceptance,request separate R2 Phase2 implementation approval.

## Human acceptance receipt —2026-10-21

Received **LISS-0591 R2 Phase1 Red テストレビュー／acceptance承認** for exact
22-artifact467971d66fb895fc6364d40b8f5580b9c62f715c247fe2832c892885f5030bb9.
This supersedes the pending human decision above,not historical verification.
No runtime rerun/source/test edit. Next:separate R2 Phase2 Green/implementation
approval;test acceptance does not grant implementation,commit or delivery.
