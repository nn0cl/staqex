# LISS-0592 Phase1 Red test review — R1 re-review passed

Review date:2026-10-18 Asia/Tokyo. Derived review entry,not acceptance authority.
Current:R1 test-only correction/re-review explicitly approved and executed.
Agent re-review closes R1;human corrected tests accepted2026-10-18. Production
unchanged. See latest re-review section below;initial review is historical.

## Initial review — historical evidence

Initial authority was review execution only;no tests/production edited then.

## Review packet

- Scope:accepted R01–R07 tests,immutable fixture provenance and exact two-carrier
  migration. Role switched to reviewer;artifacts and outputs re-read from disk.
- Canonical agreement:[repair spec](../../specs/parseerror-serialization-repair.md).
  Live owner:[Issue0592](../../issues/LISS-0592-parseerror-serialization-repair.md),
  [WP0175](../../work-plans/WP-0175-source-responsibility-inventory.md).
- Re-read:accepted spec/Issue/latest trace;all six new0592 Python files;
  consumer-baseline.json;original carrier/Git hashes;0590 reader and ownership
  diff;0585 real copy utility;0590 inherited migration guards;actual ParseError,
  modules._parse_file/access.find_module_info entrypoints;quickstart,conventions,
  readiness,AT-TDD,testing,verification,quality,routing and lesson policies.
- Reviewed artifact cohort SHA256:
  1dc80d45363e2a6f43b77129868be4f45eb3e1cc7cb9e237b22435b922c36c89.
  Six Python files/four fixtures/two existing carrier substitutions unchanged
  throughout review. Original hashes and approved substitutions independently
  verified;no old fixture regeneration or assertion/exclusion change.
- Findings/dispositions:R1 below,apply after bounded human authorization.
  Review outcome:changes required;do not accept this Red contract yet.
- Blockers:R06 raw-byte preservation gap;human repair/re-review gate. Human
  test acceptance,Green approval,R07 final verification and0591 handoff remain.

## R1 [P2] — reject raw newline mutations before normalizing parser evidence

Location:`tests/liss_0592_guard_support.py:66` and missing negative cases in
`tests/test_liss_0592_guard_migration_red.py:67`.

`original_parser_bytes()` calls read_text(),which performs universal-newline
translation. It hashes re-encoded normalized text instead of preserving actual
raw input. A parser.py with LF changed to CRLF or CR is therefore accepted as
the old byte-exact source,although the accepted boundary permits only the two
reviewed reducer/helper additions. This affects both original and proposed
repaired shapes and propagates through the migrated0590 readonly reader.

Independent negative probe constructs distinct AST/raw-only pre/post roots,
then changes all LF→CRLF,one LF→CRLF,or all LF→CR. All6 mutations changed source
bytes yet passed the inverse with the original hash. No temporary source was
compiled/imported/executed. Probe exit0 means successful reproduction of the
guard defect,not passing preservation. Existing comment/AST mutations cannot
detect this normalization blind spot. This is a test-boundary defect,not
evidence of a current runtime grammar regression or source corruption.

Disposition:apply pending approval. Proposed correction only in the two new
test files above:retain original raw bytes through inverse processing (for
example explicit UTF-8 decode without universal-newline translation),and add
byte-written newline negative controls on both pre/post shapes. Keep approved
raw additions/exact AST/hash authority unchanged. Verify authorized originals
and repair proposals still pass,all6 mutation cases reject,and actual inherited
copy/guard consumers remain effective. Do not update baseline hashes or edit
the existing two carriers further. No production fix or repair prototype run.
R1 cannot be waived by72 expected behavioral/structural Red results.

## Fresh deterministic verification

All runs:dirty HEAD22335a5768c17a41eb94682e7dd14d3e6df004bd,
branch codex/liss-0592-parseerror-serialization-phase0,repo cwd,
macOS27.0.1 arm64/CPython3.12.6/pytest9.0.3,explicit repo PYTHONPATH.
Full command,UTC timestamps,exit/environment/tree and stdout/stderr retained
under `/private/tmp/liss-0591-phase0.8hzegU/`:

| Label prefix (suffix -20261018) | Result |
|---|---|
| review592-focused | 108 nodes:72 expected Red/36 pass,0 errors/skips;exit1;04:08:58Z–04:09:14Z |
| review592-inherited | 293 pass,exit0;04:08:59Z–04:09:25Z;14 existing0585–0590 files |
| review592-adjacent | 39 pass,exit0;04:09:00Z–04:09:07Z;9 parser/operator/factory/Dirac/PQN/binder files |
| review592-failure-compare | exact same72 failure IDs as author final run;0 new/resolved IDs;exit0 |
| review592-newline | all6 unapproved raw mutations wrongly accepted;R1 reproduced,exit0 |
| review592-integrity-before-records | 928 protected originals and223 compiler files unchanged;agreements/Git fixture provenance/exact carriers and artifact cohort pass,exit0 |
| review592-routing | same_context/normal;dirty committed-diff metrics unknown,exit0 |

JUnit:`/private/tmp/liss-0592-review-20261018.Dd2UJo/focused.xml`.
Independent probe/comparison scripts in that directory. Selected regression
commands repeat author r592-inherited/adjacent metadata verbatim;no exclusions.
Root/spec/all CI-sanity NOT_RUN in Phase1;no all-blocking/clean-SHA Green claim.
Full dynamic graph,external blobs/subclass-specific serialization unassessed.

## Clause reconciliation / named failure scenarios

- R01:56 actual default+protocol0–5/message/code/coordinate round-trips fail
  reconstruction,not a test-only replacement or expected-failure assertion.
- R02:6 real _expect/bracket/brace errors fail fresh-interpreter restoration;
  both requested module import orders execute before load failure. Public class
  catch and field checks remain required after repair;not claimed passing now.
- R03:7 extra-state/notes/independent-args/alias/self-reference round-trips and
  shallow/deep copy2 fail reconstruction. Positive preservation assertions are
  present but not reached until real repair;cyclic constructor args excluded.
- R04:7 constructor/signature/invalid-call/export/class/AST checks pass.
- R05:9 actual consumer snapshots+1 evidence-tamper rejection pass. Full ordered
  diagnostics include prefixes,coordinates and advisory records. Corpus label
  cardinality produces an invalid declaration/block diagnostic here;direct
  cardinality exceptions are separately covered by R02,not falsely counted.
- R06:17 migration/mutation and2 preservation positives pass;missing actual
  reducer/helper is1 intended structural Red. Real Parser×TypeChecker pre/post
  copies are distinct. However R1 exposes missing raw negative coverage,so
  those passing guards are insufficient for acceptance.
- R07:outside-scope bytes/exports and provisional regressions assessed. Final
  actual clean SHA/all blocking and repaired0591 baseline not yet satisfied.

No functional clause weakening,old hash update,active-Red exclusion or source
edit. No current consumer mismatch found in assessed scope;no claim that this
proves repaired serialization or future full integration.

## Structure / effective isolation / lessons

Live TOML:review.same_context,implementation.host,empty model IDs;large_change
and source_structure sections absent. No enabled conditional override;use
same-context skill,explicitly weaker than separate-context. Committed routing
measurement compares22335a57→same HEAD and reports0 committed files/lines plus
dirty-tree unknown;NOT a measurement of zero working-tree change. Re-run
committed evidence later at real SHA. No required external reviewer unavailable.

Qualitative test structure:six new Python files523 physical lines;largest154,
guard support123,migration113. Behavior/consumer/boundary/guard concerns separate.
No production-size reduction asserted. Large Parser remains unchanged under
accepted repair scope;WP0175/0591 own subsequent family migration gates. Missing
structure thresholds/dynamic graph stay unmeasured,not fabricated compliance.

Applied lessons:acceptance-inventory-reconciliation (matrix),migration-test-
shape-invariance (real distinct copied roots),bounded-repair-guard-lifecycle
(exact original evidence/no waivers),compatibility-baseline/private-consumer
inventory (actual exports/entrypoints),external-verification-import-environment
(explicit PYTHONPATH),status-drift and quantitative-traceability. R1 adds the
meta lesson raw-byte-guard-normalization to the target-owned lesson log.

## Next adjudicator decision

- Requested:**LISS-0592 Phase 1 Red R1テスト限定修正／再レビュー承認**.
- Type:phase execution for test-only repair/re-review;not test acceptance.
- Approved current scope:review only. Implementation allowed:no.
- Proposed allowed edits:only the two new test files named in R1,plus review/
  Issue/spec/status/trace evidence;no production/carrier/hash/policy broadening.
- Post-review required:yes,rerun failure comparison and guard/adjacent checks,
  close R1 in review,then separate human corrected-test acceptance and Green
  implementation approval. Batch:N/A. Decision pending;0591 remains blocked.

## Evidence links

- [Representative trace/handoff](../traces/2026-10-17-liss-0592-parseerror-repair.md)
- Canonical Register:N/A for a new agreement;accepted authority remains the
  linked Issue/spec/WP. This packet adds review evidence only.
- [Process lessons](../process-lessons-log.md)

## R1 correction / current re-review —2026-10-18

Explicit **LISS-0592 Phase 1 Red R1テスト限定修正／再レビュー承認** received.
Allowed correction executed in exactly two new files:

- tests/liss_0592_guard_support.py:one read_text() expression replaced with
  read_bytes().decode("utf-8"). No universal-newline translation;UTF-8 decode/
  encode preserves original bytes. All exact AST/raw additions and hashes stay.
- tests/test_liss_0592_guard_migration_red.py:one parametrized6-node test added.
  Original/proposed shapes × wholeCRLF/singleCRLF/wholeCR. Mutations written as
  bytes,assert changed raw bytes/equal AST,then require both the direct inverse
  and actual inherited readonly reader to reject them with boundary errors.
  Before each mutation,the authorized shape must restore original bytes.

Role switched from test author to reviewer after correction;all six modules,
spec/R1/diff and deterministic outputs re-read. No further test edits during
review. Independent reviewer probe builds raw roots directly from Git rather
than using make_shape;4 authorized reader checks pass and all6 mutations are
rejected by both readers(12 negative reader checks). No proposed source import,
compile or execution. R1 disposition:**already closed with evidence**. No new
blocking finding in bounded re-review;this is not human test acceptance or
implementation approval.

### Fresh results / comparison

Environment and dirty HEAD22335a5768c17a41eb94682e7dd14d3e6df004bd unchanged.
Full command/UTC timestamps/exits/tree/stdout/stderr under
`/private/tmp/liss-0591-phase0.8hzegU/`,labels below use suffix -20261018:

| Label prefix | Result |
|---|---|
| r1-592-newline-before | new6 nodes all fail(DID NOT RAISE);17 deselected;old reader,exit1 |
| r1-592-newline-after | same6 nodes pass;17 deselected,exit0;selection only for this diagnostic run |
| r1-592-focused | 114 nodes:72 expected Red/42 pass,0 errors/skips/exclusions;exit1;10:10:47Z–10:11:02Z |
| r1-592-inherited | 293 pass,exit0;10:10:49Z–10:11:14Z;same14 existing files |
| r1-592-adjacent | 39 pass,exit0;10:10:50Z–10:10:56Z;same9 adjacent files |
| r1-592-old-probe | original reviewer reproducer unchanged now stops at first raw mutation with unapproved parser byte change,exit1(expected rejection,not suite regression) |
| r1-592-reviewer-probe | independent Git-root positives4/mutations6/readers12 all correct,exit0 |
| r1-592-failure-compare | all original108 IDs/outcomes identical,only6 new passing nodes;new/resolved failure IDs both0,exit0 |
| r1-592-integrity | exact approved2-file delta;other10 artifacts/928 originals/223 compiler files and agreements unchanged,exit0 |
| r1-592-routing | same_context/normal;dirty committed-diff metrics unknown,exit0 |

External scripts/JUnit:`/private/tmp/liss-0592-r1-20261018.gTq1Nx/`.
No unexpected setup failure,no xfail/skip/waiver. Focused114 run includes all
nodes,unlike selected6-node diagnosis. Root/spec/all CI-sanity NOT_RUN;no clean
SHA or all-blocking Green. Original71 behavioral reconstruction failures and
1 missing-repair structural failure remain,not weakened to pass.

### Corrected artifacts / acceptance boundary

Current12-artifact cohort SHA256(sorted path:hash lines,no final newline):
3d77b2159acb72ad9aae73f347e3f85c20492098706bbca58f20618fb765029e.
The only changed hashes versus initial cohort are:

- tests/liss_0592_guard_support.py:
  9b29db09e2c1ee6965512666c78b7d84c5e334143ab71e0df3861f746e71cf16
- tests/test_liss_0592_guard_migration_red.py:
  0bf776b8e456ab126b66a0596877cb5bde62dae728d04f44ce74c429faa30266

Independent inverse-diff check reconstructs both old files exactly (one reader
expression substitution and removal of only the new test block). No existing
assertion removed/relaxed,no old fixture/hash/carrier edit. R06 gains6 passing
negative nodes (migration module now23 nodes);R01–R05 unchanged,R07 final SHA/
blocking/repaired0591 handoff remains future work. Original agreement unchanged.
Six new Python files548 physical lines,largest154,migration138,guard123;
responsibility grouping unchanged. No configured structure thresholds or
large-change override;dirty measurement remains unknown. Same-context review
is still weaker than separate-context;no unavailable required review hidden.
Raw-byte lesson applied with persistent negatives;no new duplicate lesson.

Received2026-10-18:**LISS-0592 Phase 1 Red 修正済みテストレビュー／acceptance承認**.
Type:phase/test acceptance. Approved scope:test-only R1 correction and re-review.
Implementation allowed:no. Post-review required:yes,separate Green implementation
approval after human exact corrected-artifact acceptance;then Phase3/final/
delivery and0591 repaired-baseline gates. Batch:N/A. Human decision:accepted
exact corrected cohort3d77b215…65029e above. No test/assertion/fixture/source
change or new agent review in this metadata-only record;runtime evidence is
historical R1 verification,not rerun/all-blocking Green.
Current next approval:**LISS-0592 Phase 2 Green／implementation承認**.

Subsequent Phase2 approval received2026-10-18;exact repair written with accepted
tests unchanged. This remains a Phase1 review/acceptance artifact,not Phase3
review or full-Green evidence. Current gate:local commit/actual-SHA all-blocking
approval;live implementation results owned by Issue/spec/representative trace.

Local commit/actual-SHA all-blocking gate subsequently authorized2026-10-18.
Exact postcommit results are external to this target commit (sha592 evidence
paths in Issue/trace);do not treat this Phase1 packet as a Phase3 review or
pre-claim clean-SHA Green. No reviewed test change;no remote authority.
