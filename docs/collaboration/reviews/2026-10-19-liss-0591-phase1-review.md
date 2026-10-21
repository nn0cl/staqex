# LISS-0591 Phase1 Red review — R1 closed;human corrected-test acceptance received

Current2026-10-19:authorized R1 correction/re-review completed;R1 closed in
agent review and human corrected-test acceptance received. Corrected179 nodes:
4 expected structural Red/175 PASS. Initial
requires-changes findings below are retained as history;latest disposition at end.

## Review target / authority

- Date:2026-10-19;Feature Path,Phase1 test review execution explicitly approved.
- Canonical:[P01–P10/B01–B10 and6-carrier policy](../../specs/parser-operator-primary-successor.md),
  [Issue0591](../../issues/LISS-0591-parser-operator-primary-successor.md),
  [WP0175](../../work-plans/WP-0175-source-responsibility-inventory.md).
- Reviewed actual dirty HEAD:`dca93187f50594b0417ae88067154baaf3c0ea7c`,branch
  `codex/liss-0591-repaired-baseline`. No clean review-commit SHA exists yet.
- Reviewed22-artifact cohort SHA256:
  `82458c74523978e6ea16cf7dcd32c3bdc4c2e2b15926a470aa1c171c72ed414d`.
- Isolation:same_context,explicitly weaker than separate_context. Role switched
  to reviewer;disk artifacts/probes,not author reasoning,are evidence. ModelIDs
  empty;no enabled large-change override. No test/source edit during review.
- Implementation allowed:no;post-review required:yes;batch:N/A. Human test
  acceptance and Phase2 implementation remain separate from this review.

## Findings / disposition

### R1 [P2] Named readonly operators read synthesizes bytes for a deleted file

- Location:[readonly_bytes](../../../tests/liss_0591_guard_support.py#L141),
  supporting optional old-owner check at lines130–133;negative inventory in
  [post-only missing-owner test](../../../tests/test_liss_0591_guard_migration_red.py#L68).
- In a valid unextracted Parser root,delete `compiler/staqex/parsing/operators.py`.
  The0591 `readonly_bytes(root, OPERATORS)` calls `parser_bytes`,whose historical
  parser-only allowance does not require operators to exist,then returns the
  immutable original-operators fixture. Thus an explicit named-file read
  succeeds even though that file is absent. It masks the very deletion that
  readonly boundary checks should reject.
- Independent probe builds raw roots directly from actual Git22335 and repaired
  Gitdca93187,not `guard.make_shape`. Four intact-file reader positives succeed.
  After deletion,new0591 reader wrongly accepts both repaired/unrepaired roots
  and returns the exact original operators digest. Existing0590 reader rejects
  both with FileNotFoundError because it reads the requested path first.
- Existing production-path projection alone does not detect the deletion when
  given a cached Git path list;tracked deleted files remain named in that list.
  Do not claim all guards/CI accept the deletion:the inherited0590 reader and
  fresh cold imports can still reject it. The defect is the new0591 reader's
  protection and the missing pre-shape control,not a proven product regression.
- Requirement:P09/B08/B09,missing-artifact rejection in real pre/post shapes.
  Current14 mutation nodes cover missing-owner only on extracted shape;they
  do not test deletion of the original operators module on the pre shape.
- Disposition:apply,OPEN. Requires test-only correction/re-review authorization.
  Preserve parser-only historical raw-root support where needed,but require
  the explicitly requested operators path to exist before any projection.
  Add persistent positive/deletion controls for unextracted repaired/unrepaired
  roots and retain extracted missing-owner controls. Keep original fixture
  hashes,accepted clauses and6 existing carrier substitutions unchanged.
- Proposed edit boundary:only new `tests/liss_0591_guard_support.py` and
  `tests/test_liss_0591_guard_migration_red.py`,plus related review/status records.
  No implementation,existing fixture regeneration or seventh carrier.

## Deterministic verification / comparison

Environment:macOS27.0.1 arm64/CPython3.12.6/pytest9.0.3,repository cwd,explicit
PYTHONPATH,dirty HEAD dca93187 throughout. External per-command metadata includes
SHA/dirty before/after,command/start/end UTC/duration/exit/full output:
`/private/tmp/liss-0591-phase0.8hzegU/review591-*-20261019.{json,out,err}`.

- Focused171 nodes:4 expected structural Red/167 PASS,0 errors/skips,exit1.
  Exact same failure node IDs/outcomes as authored suite;new/resolved suite
  failures0/0. Reviewed cases do not cover R1;passing counts do not close it.
- Existing repair114 PASS,inherited293 PASS,adjacent39 PASS,spec161/161 PASS.
  No failure/exclusion/accepted-assertion changes. Consumer/cold import/pickle
  nodes run on actual current production,not a runnable extraction proposal.
- Reviewer probe:4 positive controls;2 new-reader false acceptances and2 old-
  reader correct rejections. Evidence `review591-probe-retry-20261019.out`;
  script `/private/tmp/liss-0591-review-20261019.bTBhjH/probe.py`.
  Initial probe over-assumed both readers would accept;it failed its own outcome
  assertion. Corrected that external expectation only;initial logs retained.
- Independent Git/cohort audit PASS:all223 tracked production files,all original
  tests/fixtures outside6 carriers unchanged;exact6-carrier substitutions and
  original22-artifact hashes unchanged;closed new16-path inventory retained.
- Root/all CI sanity/final-clean-SHA evidence:not_run this Phase1 review.
  Expected Red is not full Green;no waived failure or whole-graph coverage claim.

## Mapping, structure / routing limitations

Re-read all4 new tests,2 helpers,6 existing carrier deltas,accepted P/B clauses,
immutable provenance and prior JUnit evidence. Canonical clause mapping remains
the spec's Phase1 section. P02–P07 cover direct primary/callbacks/conversion/
cursor and neighboring pipeline programs;factory runtime controls are authored
but gated by the missing-factory Red until real implementation. R1 leaves P09/
B08/B09 incomplete regardless of the current passing AST-only guard matrix.

Official `review-change.py --base dca93187 --head HEAD` reports normal
same_context with dirty-tree unknown;its committed0-file diff is NOT the actual
reviewed scope. Independent dirty-tree supplement before these review records:
26 files/4389 added+deleted lines (includes immutable data/docs),12 Python
source/test files measured,max250 physical lines. Source ownership mapping,
whole dynamic graph/cycles are unknown. Final dirty metrics are retained in
review591-final-audit-20261019.out after record edits.

No source_structure numeric settings/large_change override are enabled. Normal
same_context therefore remains effective,not an inferred stronger review.
Keep fixed Git evidence for recoverability rather than shortening it to hide
diff size;no runtime body split/line reduction is claimed. Parser3694/class3504
and the future117-line move remain subject to the accepted WP0175 follow-up.
Missing full graph/committed metrics are disclosed,not waived by this review.

## Next approval / handoff

Review result:requires changes,R1 open. No human acceptance/reviewer pass or
implementation permission is inferred. Current test/source cohort preserved.

Request **LISS-0591 Phase 1 Red R1テスト限定修正／再レビュー承認**.
Approval type:phase/test correction + re-review;implementation allowed:no;
post-review:yes;batch:N/A. Then rerun unchanged reviewer probe and focused/
repair/inherited/adjacent evidence;request exact corrected-test acceptance only
after R1 is closed by evidence. Do not start Green from this packet.

Representative [trace/handoff](../traces/2026-10-16-liss-0591-parser-operator-primary.md).

## Authorized R1 correction / re-review —2026-10-19

Received **LISS-0591 Phase 1 Red R1テスト限定修正／再レビュー承認**.
Feature Path,only2 new0591 test files plus records. Repair implementation,
fixture/hash regeneration and6 existing carrier changes remain out of scope.

Correction:`readonly_bytes` now requires the explicitly requested operators
path to be a file before projection. Historical parser-only raw-root allowance
is untouched. Appended `test_r1_named_operators_read_requires_actual_file_on_all_shapes`:
2 readers×2 repair states×2 extraction states =8 persistent nodes. Each proves
intact positive,then deletion rejection;unextracted cases also prove parser-only
normalization still works. Source roots start from actual Git22335/dca93187.

After authoring,switched back to reviewer and re-read both corrected files,
the original finding/accepted scope and deterministic outputs. Same-context
isolation remains weaker;no separate-agent review/model override is claimed.
R1 disposition:already closed with evidence. No further blocking finding found
within this correction/re-review scope. Human acceptance remains separate.

Fresh dirtyHEAD dca93187/macOS27.0.1 arm64/CPython3.12.6/pytest9.0.3,explicit
PYTHONPATH,per-command metadata/full output under
`/private/tmp/liss-0591-phase0.8hzegU/r1-591-*-20261019.{json,out,err}`:

- Focused179 nodes:4 same expected structural Red/175 PASS,0 errors/skips.
  Original171 source nodes/outcomes unchanged;all8 new controls pass. No new
  collected failures or weakened old assertions. Factory implementation still
  absent by design;this is test acceptance readiness,not full Green.
- Repair114/inherited293/adjacent39/spec161/161 PASS.
- Exact original reviewer probe script is unchanged and was rerun. Its
  defect-reproduction oracle now fails because the wrong acceptances disappeared;
  this is not a product/test regression. Companion r1-probe.py executes the
  exact unchanged input/setup/deletion/read operations with corrected outcome
  assertions:4 intact positives and4 deletion rejections PASS. Input script
  SHA256 `f3471d2c13ff94feb1643607717d89a7c185229ef6e4b948b5d6268036e889c8`.
- Bounded audit PASS:only one added helper assertion plus8 appended test nodes;
  remove just those additions and the2 files match prior raw cohort hashes.
  Other20 artifacts,all old fixtures,6 existing carrier substitutions and223
  production Git files are unchanged. Closed new path manifest unchanged.
- Corrected22-artifact cohort SHA256:
  `68d6eef02b5e18a01ed4e3f4fef22c95ae740c71a57881b56b65708f3f1b5547`.
  Per-file hashes:r1-591-audit-20261019.out. Helper251 physical lines;new guard
  test214. No configured numeric budget/large-change override changed. Logical
  owner mapping/full dynamic graph/committed-diff applicability remain gaps.
- Root/all CI sanity/final-clean-SHA:not_run;expected Phase1 Red not waived.
  Final records/lifecycle/Git/cohort audit:r1-591-final-audit-20261019.out and
  r1-591-lifecycle-20261019.out (actual outcomes checked before handoff).

Next requested:**LISS-0591 Phase 1 Red 修正済みテストレビュー／acceptance承認**.
Type:phase/test acceptance of corrected22-artifact cohort. Approved scope:R1
test-only correction/re-review;implementation allowed:no;post-review required:
yes;batch:N/A. Green implementation,commit and remote delivery need separate
explicit approvals. Do not reuse earlier scope/review execution permission.

## Human receipt —2026-10-19

Received **LISS-0591 Phase 1 Red 修正済みテストレビュー／acceptance承認** for
corrected22-artifact cohort `68d6eef02b5e18a01ed4e3f4fef22c95ae740c71a57881b56b65708f3f1b5547`.
This records human test acceptance,not another agent review/runtime run or
Phase2 permission. Current next gate:explicit Phase2 Green/implementation
approval;implementation allowed:no;post-review required:yes;batch:N/A.
