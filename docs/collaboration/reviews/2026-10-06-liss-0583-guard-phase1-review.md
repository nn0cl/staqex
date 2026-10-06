# LISS-0583 guard migration: Phase 1 Red test review

## Review Target

- Artifact: [new acceptance tests](../../../tests/test_liss_0583_repair_boundary_migration_red.py),
  accepted [G01–G07](../../specs/evaluator-static-foreach-repair-guard-migration.md).
- Current phase: Feature Path / phase-1-red, supplemental AIP-0583-003 size M;
  original Feature Phase 2 source parked unchanged.
- Received execution approval: human `ISS-0583 guard移行 Phase 1 Red実行承認`;
  existing LISS-0583 is the uniquely identified target, not a new Issue.
- Received test acceptance: human **LISS-0583 guard移行 Phase 1 Red テストレビュー／acceptance承認**,2026-10-06; new27 cases/review unchanged.
- Next requested approval: **LISS-0583 guard移行 Phase 2 Green／implementation承認**.
- Approval type: phase / test acceptance.
- Approved scope: new real-guard acceptance/mutation tests only.
- Implementation allowed: **no** for guard migration. Post-review required: yes.
- Execution batch ID: N/A. Commit/push/merge and Phase 3 not authorized here.

## What Changed / Why It Matters

Only new test file,196 physical lines /27 parameterized cases, plus phase
records. Existing0584 guard/function identity, fixture, numeric tests, F08
support/tests, parked runtime source and lifecycle unchanged this phase.
Tests copy eight dependencies to pytest temporary storage and patch the real
guard's ROOT, never its function. Baseline reconstruction changes only temporary
copies, validates original foreach AST against the frozen F08 baseline, and
is executable-AST evidence, not a reconstructed historical byte snapshot.

| Requirement | Executable evidence / disposition |
|---|---|
| G01 | Actual fixture digest, explicit base/owner/adopted-node assertions; three metadata mutations and one altered temporary fixture rejected. Original fixture unchanged. |
| G02 | Real guard checks both extracted and baseline-AST positive shapes (2 expected Red); each of five persistent byte-protected dependencies mutated separately and rejected. Exact eight-path set asserted. |
| G03 | Real-entrypoint spies demand existing evaluator import/full-AST, compatibility and context projections (1 expected Red). Existing F08 helper unchanged. |
| G04 | Twelve source mutations, duplicate installer and changed retained foreach rejected; paired real positive tests prevent reject-all guards passing Phase 2. |
| G05 | Original0583/0582 focused94, numeric repair38, remaining boundary5 and consumer/adjacent77 pass. Original F05 unchanged. |
| G06 | New test-only change; old0584 readonly guard remains unchanged and failing. Runtime/fixture/helper hashes/diffs checked. |
| G07 | Lifecycle0entries, no skips/exclusions. Root/spec/sanity and actual-commit final verification deliberately not_run in Red; remain mandatory later. |

## Agent review / findings

Same-context reviewer reread new tests from disk and accepted requirements,
original guard/support and projection boundaries; reran focused suite without
author/test/implementation edits. Agent verdict: **passed for human Red test
acceptance**, not Green or completed guard protection.

Important limitation:24 new passing negatives can currently reject because the
old byte guard rejects the clean extracted shape before reaching each mutation.
This is expected in Red, not proof the new mutation protections work. Phase 2
must pass both legitimate positives and all negatives at the same real entrypoint;
the projection delegation assertion also must pass. No waiver of G04.
No fixture/precondition errors observed; baseline foreach AST and unique mutation
replacement preconditions pass. No requirement changes made to fit results.

## Deterministic evidence

Tested HEAD/base `6d1b851bff292ae496145b71e7a15a9be757cfd1` **plus dirty parked
source, records and new tests**, branch `codex/liss-0583-phase1-rereview`.
Not committed-SHA evidence. cwd `/Users/nn0cl/Documents/git/qpex`;
macOS27.0.1 arm64, `/usr/local/bin/python3.12`3.12.6, pytest9.0.3.
All runs2026-10-06 JST. Errors/skips/exclusions0 in each run.

| Run | Result / exit | Start; duration | Evidence |
|---|---|---|---|
| Focused165 | 161pass /4fail, exit1 | 17:08:01.308599;1.828s | `/private/tmp/liss0583-guard-phase1-focused.xml` |
| Same-context focused rerun165 | 161pass /same4fail, exit1 | 17:09:08.902297;1.888s | `/private/tmp/liss0583-guard-phase1-review.xml` |
| Consumer/adjacent77 | 77pass, exit0 | 17:08:30.206361;24.841s | `/private/tmp/liss0583-guard-phase1-consumer-adjacent.xml` |
| Root/spec/local sanity | not_run this phase | N/A | Prior Phase 2 evidence is historical, not fresh success. |

Focused exact command (review rerun substitutes `review` for `focused` XML):

```sh
/usr/local/bin/python3.12 -m pytest tests/test_liss_0583_repair_boundary_migration_red.py tests/test_liss_0584_repair_boundary_red.py tests/test_liss_0584_opaque_wire_arithmetic_red.py tests/test_liss_0583_static_foreach_behavior_red.py tests/test_liss_0583_static_foreach_successor_red.py tests/test_liss_0583_guard_migration_red.py tests/test_liss_0582_public_import_repair_red.py -q --junitxml=/private/tmp/liss0583-guard-phase1-focused.xml
```

Consumer/adjacent exact command:

```sh
/usr/local/bin/python3.12 -m pytest tests/test_kernel_classical_boundary_red.py tests/test_static_hilbert_migration_red.py tests/test_qpu_ir_lowering_red.py tests/test_parametric_circuit_runtime_red.py tests/test_liss_0416_dedicated_in_keyword_red.py tests/test_liss_0582_runtime_plan_eligibility_red.py tests/test_scientific_semantic_core_red.py tests/test_conformance_slice_c_red.py tests/test_linear_hardening_slice_e_red.py tests/test_classical_rational_red.py tests/test_liss_0543_refactor_baseline_red.py -q --junitxml=/private/tmp/liss0583-guard-phase1-consumer-adjacent.xml
```

Exact failures in both focused runs:

- `tests/test_liss_0583_repair_boundary_migration_red.py::test_real_guard_accepts_only_reviewed_positive_shapes[extracted]`
- `tests/test_liss_0583_repair_boundary_migration_red.py::test_real_guard_accepts_only_reviewed_positive_shapes[baseline-ast]`
- `tests/test_liss_0583_repair_boundary_migration_red.py::test_real_guard_delegates_to_existing_f08_projections`
- `tests/test_liss_0584_repair_boundary_red.py::test_existing_f05_owner_and_readonly_dependencies_are_preserved`

Comparison: Phase 0 scoped baseline had the last existing failure only; current
new tests add3 expected Red. Original bounded runtime/numeric/consumer sets show
no new observed regression; whole-suite comparison not_run. All-blocking remains
open with historical readonly-guard and source-clean copy-smoke failures.
No full Green or Phase 2/3 completion claimed; actual final commit rerun required.

Additional checks: `git diff --check`; lifecycle `--as-of 2026-10-06`0entries;
empty diff for original guard/numeric tests/fixture/F08 helper/original F08 tests;
all four parked source SHA256 values match the Phase 2 trace.

Routing evidence `/private/tmp/liss0583-guard-phase1-routing.json`:
`review-change.py --root . --base 6d1b851b --head HEAD` reports normal
same_context, empty model, no reasons/large-change override. Working-tree metrics
unknown because dirty changes are not represented by committed diff; not used
as permission to downgrade. Host execution / same-context review (weaker),
no separate-context review claimed. New196-line test owns one guard contract;
no facade implementation body or numeric structure-budget waiver introduced.
Global dynamic/out-of-tree consumer graph remains unassessed.

Existing bounded-repair-guard lesson applied: real entrypoint, immutable
provenance, positive/negative coupling and honest partial verification. Included
accepted specs, actual guard/projections, selected policies and adjacent consumers;
omitted other ranks, Rust/providers/secrets and unrelated history. No AI runtime
payload or external/private data. No new ADR/technology/operating rule.

## Adjudicator Checklist / Decision

- [x] Current phase, included/omitted context, assumptions and scope explicit.
- [x] Deterministic Red evidence adequate for test review; limitations visible.
- [x] Implementation forbidden; post-review and non-batch route recorded.
- [x] Human test acceptance received2026-10-06; unchanged tests/specification.
- [x] Approved — Phase 1 test acceptance only, not implementation.
- [ ] Approved with comments
- [ ] Rejected
- [ ] Needs ADR

Next safe action: obtain bounded guard Phase 2 Green/implementation approval.
Allowed implementation after that approval: only the existing0584 readonly
guard's exact three-path AST/five-path byte dispatch using existing F08 helpers,
retaining guard identity and metadata assertions. Existing fixture, other guards,
accepted tests, source and lifecycle remain unchanged for this supplement.
Post-review required; batch N/A. Local commit/all-blocking actual-SHA rerun and
Phase 3/final/delivery remain separately gated. No guard modification or rehash
while implementation permission is absent.

Acceptance synchronization changed records only; historical test counts above
are not new execution evidence. Implementation permission remains no.
