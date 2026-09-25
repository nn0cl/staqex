# WP-0171 / LISS-0578 Phase 1 Red Review

## Review packet

- Scope: review the accepted Phase 1 Red structural contract and its
  characterization boundary. No production extraction or Phase 2 work was
  reviewed or authorized.
- Approval reviewed: `WP-0171 / LISS-0578 Phase 1 Red テストレビュー承認`
  (2026-09-24).
- Canonical documents and files re-read: LISS-0578 specification, issue,
  WP-0171, Phase 0 handoff, LISS-0578 structural test, active-Red manifest,
  process lessons, verification policy, runtime routing, evaluator/classical
  dispatch, binding dispatch, operator set-comprehension lookup, and the
  LISS-0424/0427/0428/0429 characterization suites.
- Findings:
  1. **Blocker — compatibility assertion is only a substring search.** The
     assertions at `tests/test_liss_0578_classical_operator_eval_red.py:61-65`
     check that import/function/attribute strings occur somewhere in
     `compatibility.py`. They do not prove that the installer assigns each
     evaluator hook to the intended successor function, that the installer is
     invoked during evaluator setup, or that the live class attributes have
     successor identity. A dead comment or unrelated function can satisfy the
     current assertions. This repeats the already-recorded
     `decomposition-source-ownership` lesson and the LISS-0575 Phase 1 review
     finding about string-search compatibility contracts.
  2. **Blocker — consumer inventory omits a real direct consumer.**
     `runtime/evaluation/classical.py` dispatches classical operator binders
     through `context._evaluate_classical_op_binder` (currently line 136), in
     addition to `binding.py`. The Phase 0 specification's inventory and the
     review payload do not name this path. The LISS-0424 suite exercises
     classical Sigma through this value-evaluation route, but that linkage is
     not recorded in the accepted consumer inventory.
  3. **Blocker — Operator-resolution consumer is not characterized.** The
     accepted Phase 1 scenario calls for both set-comprehension evaluation and
     Operator resolution to keep working. The selected LISS-0429 suite tests
     set construction/measurement but does not exercise
     `operators.py::lookup_set_comprehension_value`. The existing
     `test_liss_0430_sigma_over_set_projector_red.py` does exercise that
     Operator-resolution consumer and passed when rerun; include it as an
     adjacent positive characterization, while keeping projection
     implementation explicitly out of scope.
- Dispositions:
  - Compatibility test strength: **not accepted**; revise to inspect actual
    installer mappings (AST or equivalent) and assert the runtime Evaluator
    hooks are identical to the successor functions once the successor exists.
  - Consumer inventory: **not accepted as complete**; add
    `evaluation/classical.py` to the canonical inventory and link it to the
    existing LISS-0424 behavioral cases.
  - Operator-resolution characterization: **not accepted as complete**; add
    the LISS-0430 consumer suite to the explicitly named verification set.
  - The three current structural failures remain credible intentional Red
    gaps. The existing 17 behavior tests remain passing evidence, but do not
    close the consumer omissions above.
- Remaining blockers: Phase 1 Red test review is **not accepted** until the
  above test/specification corrections are made and rerun. Phase 2 remains
  unauthorized.
- Verification re-run:
  - Focused LISS-0578 suite: **3 failed, 0 passed**. Failures are the intended
    missing successor, duplicate facade bodies, and compatibility wiring.
  - Existing LISS-0424/0427/0428/0429 characterization: **17 passed**.
  - LISS-0430 operator-resolution/set-comprehension consumer: **5 passed**.
  - Active-Red lifecycle, document lifecycle, coverage-ledger consistency,
    and `git diff --check`: passed.
- Tested SHA/environment: base SHA
  `0e32937f4bf90f7541f146feaa7c95670437acb2`, with uncommitted Phase 0/1
  artifacts; macOS Darwin 27.0.0 arm64, Python 3.14.6, pytest 9.1.1.
  These are focused Phase 1 Red results, not all-blocking Green evidence.
- New/resolved/unassessed failures: three intentional structural Red failures;
  22 existing characterizations passed across the 0424/0427/0428/0429/0430
  suites. No unrelated or all-blocking suites were run; they remain
  unassessed, not failed.
- Spec-to-test mapping and assertion changes: no existing assertions were
  weakened. The compatibility assertion is weaker than the accepted active
  hook identity contract; the two omitted consumers leave accepted scenarios
  without direct named characterization coverage.
- Consumer compatibility and structure: static inventory confirms calls from
  `evaluation/classical.py` and `evaluation/binding.py`; Operator resolution
  reaches set-comprehension evaluation through `evaluation/operators.py`.
  No post-extraction compatibility claim can be made before Green.
- Applied process lessons: `private-consumer-inventory` and
  `decomposition-callback-boundary` require the missing consumer to be added;
  `red-contract-scope` requires distinct passing characterizations for the
  real consumers; `decomposition-source-ownership` requires a structural
  compatibility mapping and successor/hook identity check. The last lesson
  was not honored by the current substring assertions and is reinforced in the
  process-lessons log.
- Effective review route: `same_context` per live routing; this is weaker than
  `separate_context`. Artifacts and test outputs were re-read/rerun in reviewer
  role. The large-change override is absent/disabled; no separate-context
  review was required by routing.
- Disposition: **Phase 1 Red test review not accepted**. No production
  implementation is authorized.

## Next gate

Request `WP-0171 / LISS-0578 Phase 1 Red contract correction 承認` before
revising the test contract and consumer inventory. After correction and rerun,
resubmit `WP-0171 / LISS-0578 Phase 1 Red テストレビュー承認`.

## Evidence links

- Specification: `docs/specs/evaluator-classical-operator-evaluation.md`
- Issue: `docs/issues/LISS-0578-classical-operator-evaluation.md`
- Work plan: `docs/work-plans/WP-0171-classical-operator-evaluation-decomposition.md`
- Trace: `docs/collaboration/traces/2026-09-24-liss-0578-phase0.md`
- Test: `tests/test_liss_0578_classical_operator_eval_red.py`
