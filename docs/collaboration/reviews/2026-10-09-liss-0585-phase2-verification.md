# LISS-0585 Phase 2 implementation / provisional verification

## Review target and authority

- Artifact: this packet, accepted spec and implementation on the named branch
- Current phase: Phase2 Green implementation, all-blocking verification pending
- Approved scope: accepted T01–T09 and corrected Phase1 tests/guard mapping
- Human implementation approval: `LISS-0585 Phase 2 Green／implementation承認`
- Local commit/rerun authority: human `LISS-0585 ローカルコミット／実SHAで全blocking再検証`
- Next requested approval: Phase3 only after successful actual-SHA all-blocking rerun
- Approval type: phase/process verification only; not Phase3 or delivery
- Implementation permission: yes for the completed minimal approved move only;
  no additional semantic or test changes proposed
- Post-review required: actual committed-head verification, separate Phase3
  review, human final acceptance and delivery approval
- Execution batch: none

## What changed / why it matters

1. New `compiler/staqex/runtime/evaluation/tensor_binding.py` owns
   `bind_tensor(context, joint, names, expr)`,61physical lines. Algorithm
   unchanged apart from self→context and relative Joint import/typed ownership.
2. Evaluator removes its only `_bind_tensor` body, preserves all public imports,
   adds one private installer import and one setup.1099→1055physical lines.
3. Compatibility adds one successor import and exact `_bind_tensor` mapping;
   323→329physical lines. Binding/context remain unchanged; no new state owner.

T01–T06 behavior, T07 real hook identity/setup and no duplicate body, T08 frozen
manifest/actual cold consumers, T09 real shared/readonly guards and original
algorithm conservation all pass. No retired `_red.py` blanket exclusions or
new lifecycle exclusions; active-Red entries0 before/after.
Structure disposition: dedicated stateless responsibility, compatibility wiring
only. Total physical lines across the three affected production owners grow
1422→1445 despite a44-line facade reduction; this improves responsibility
ownership, not a claim of total code-size reduction. Numeric structure policy
absent; resolved dynamic graph/cycles and external consumers unassessed.

## Accepted test bytes unchanged

Pre/post implementation SHA256 equality, measured with `shasum -a 256`:

```text
47e0b9886cd83b0d4c4bff7262ed7590713afd65b97890332dc1c489d5e471a7  tests/test_liss_0585_tensor_behavior_red.py
85fbd6958f3c667682ee43146cdb4cdbbd106451a23c68113ca0e3721081a54e  tests/test_liss_0585_tensor_ownership_red.py
72552beca3ec015dfbf8d6d5068e4bf32fcaef518e15818f8bc81cac31fb2809  tests/test_liss_0585_tensor_guard_migration_red.py
68d9718e168407bfec05a6f2ac60ae3140dbdfe44c2cea5b3a32663a34f6192d  tests/liss_0585_guard_support.py
d846669d13eee74e980b0fb97794e615289225d3683597e6f56680327ea22eb5  tests/liss_0583_guard_support.py
8fc41a4cfb69c3dfca1c6f5b29a9eef8f764dc862d65ed32f74173a9ade0cb0f  tests/fixtures/liss_0585/original-tensor-method.txt
```

Original0583/0584 immutable fixtures, adopted tests/assertions, TypeChecker,
runtime-plan eligibility, public export capture/generator and byte dependencies
unchanged. Exact contract and test mapping in
[Phase1 review](2026-10-09-liss-0585-phase1-review.md).

## Historical provisional verification states

HEAD/baseline a349a5b720c59f3a0e288c4751dd012c25514843; dirty source/test/docs tree.
cwd `/Users/nn0cl/Documents/git/qpex`; macOS27.0.1 arm64, Python3.12.6
`/usr/local/bin/python3.12`, pytest9.0.3. This is provisional evidence, not
final-SHA completion. No commit or push/PR performed. Raw task tool outputs;
precise root/focused start/end timestamps unavailable in this attempt.

| Suite | Result |
|---|---|
| Focused12-suite command from Phase1 packet |172passed in4.33s, exit0; prior four structural Red resolved, other168 unchanged |
| Actual consumer smoke/public-import repair suite |37passed in1.10s, exit0; real cold CLI/runtime/compiler/scientific and private rational consumers |
| Adjacent ASCII/Joint/qudit/nested-Mix/semantic tensor suites |22passed in0.32s, exit0 |
| Root `python3.12 -m pytest tests/ -q` |2513passed in324.26s, exit0; failures/errors/skips/exclusions0 |
| Spec `python3.12 tests/spec_verification/run_all.py` |161/161passed, exit0 |
| Non-PR Repository sanity |9passed/1failed, exit1: distributed-copy source-clean rejects uncommitted dedicated spec |

Focused/consumer/adjacent/spec errors/skips/exclusions0. Overlapping suite totals
are not additive. Root completed without exclusions or failures.
Root clean-main baseline not rerun this attempt; root failure comparison remains
unavailable. Comparable focused Phase1→Phase2 resolves exactly four named Red
failures and introduces none in that selector set.

Sanity executed every non-PR `run` step from `.github/workflows/ci.yml` under
Bash with `python3` replaced by the same Python3.12 executable; no skipped
non-PR steps, PR-only traceability check not applicable without a PR.
UTC start2026-10-09T01:15:31.248722Z/end01:15:32.431983Z.
Required docs/ADRs/script syntax/batch/document lifecycle/coverage/test lifecycle/
refactor baseline capture+cmp/conflict markers pass. Copy smoke fails with:

```text
Uncommitted distributed source: docs/specs/evaluator-tensor-binding-successor.md. Commit it before distribution.
```

This is an applicable blocking failure, not waived as a documentation nuisance.
It needs clean committed-source evidence. Prior-phase uncommitted design records
already had the same source-clean limitation; no fresh pre-implementation full
sanity baseline run claimed. `git diff --check` passes.

## Approved bounded local commit / post-commit gate

Commit only the current LISS-0585 artifacts on
`codex/liss-0585-tensor-binding-phase0`, keeping planning/accepted tests and
implementation as separate reviewable commits where practical. Include matched
Issue/spec/WP/trace/review and applicable process lesson synchronization; no
unrelated files, assertions, fixture/hash edits, exclusions or instruction edits.
Then rerun focused/consumer/adjacent/root/spec/all10 applicable sanity steps
against the resulting actual SHA, preserve evidence outside the tree to avoid
an evidence-only commit invalidating it. If any blocking fails, report it before
requesting Phase3; no Phase3/push/PR/merge permission inferred.

Post-commit evidence directory: `/private/tmp/liss-0585-sha-verification.cFxPdj`.
`result.md` will identify the exact tested SHA, clean-tree status and suite
outcomes; per-suite logs retain commands, UTC start/end and exit codes.
At this record's commit the rerun is pending, not claimed passed. No later
repository edit/commit will be made merely to embed that result. Follow the
external result alongside this packet for the current Phase2 gate.

## Adjudicator checklist

- [ ] Phase2 verification scope and bounded commit paths are correct.
- [ ] Included context, omissions and visible assumptions are acceptable.
- [ ] Source-clean failure and provisional evidence are not treated as full Green.
- [ ] Local commit/rerun approval is distinct from Phase3 and delivery.
- [ ] Post-commit all-blocking verification is required; no execution batch.

## Decision

- [x] Approved — bounded local commits and actual-SHA rerun only, human2026-10-09
- [ ] Approved with comments
- [ ] Rejected
- [ ] Needs ADR
