# Review Summary: WP-0171 / LISS-0578 Phase 3 Refactor

## Review packet

- Scope: behavior-preserving Phase 3 review of the classical Operator
  expression/binder successor, compatibility facade, actual consumers, and
  structure. No scope expansion or new source implementation.
- Canonical documents: `docs/specs/evaluator-classical-operator-evaluation.md`,
  `docs/specs/staqex-core-module-decomposition.md`, LISS-0578 Issue,
  WP-0171, `docs/collaboration/verification-policy.md`, and
  `docs/collaboration/source-code-quality.md`.
- Files re-read: `compiler/staqex/runtime/evaluation/classical_operator_eval.py`,
  `compiler/staqex/runtime/evaluation/compatibility.py`,
  `compiler/staqex/runtime/evaluator.py`,
  `tests/test_liss_0578_classical_operator_eval_red.py`, and
  `docs/testing/refactor-baseline.json`.
- Findings: no actionable behavior, ownership, or compatibility defects found.
  The successor remains a focused 147-line module with two direct algorithms
  and a narrow read-only context protocol. Evaluator remains the state owner;
  the extracted code does not import or instantiate it. The compatibility
  installer retains the old private entrypoints and maps them directly to the
  successor functions. No further helper layer or file split would reduce
  review cost, so source refactoring was not warranted.
- Dispositions:
  - Applied: issue/WP/spec/trace/handoff statuses synchronized to Phase 3
    reviewed, with Adjudicator final review still pending.
  - Already closed with evidence: snapshot now reflects the actual public
    export; generated capture compares byte-for-byte.
  - Out of scope: general Operator projection, parser/typechecker, QPU/provider
    work, and changes to accepted expression semantics.
- Blockers: GitHub-hosted CI and verification after the final commit SHA have
  not run. The current worktree is dirty and uncommitted; all results below
  are provisional for base SHA `0e32937f4bf90f7541f146feaa7c95670437acb2`.
- Verification result:
  - Focused structural and consumer run: **31 passed**, 0 failed/errors,
    0 skipped. Command: `PYTHONPATH=compiler:.
    /Users/nn0cl/Documents/git/qpex/.venv/bin/python -m pytest
    tests/test_liss_0578_classical_operator_eval_red.py
    tests/test_liss_0424_classical_numeric_sigma_red.py
    tests/test_liss_0427_forall_binder_red.py
    tests/test_liss_0428_min_binder_red.py
    tests/test_liss_0429_set_comprehension_red.py
    tests/test_liss_0430_sigma_over_set_projector_red.py
    tests/test_liss_0431_project_no_implicit_renorm_red.py -q`.
  - All-root pytest: **2,260 passed**, 0 failed/errors, 0 skipped, 315.29s.
    Command: `PYTHONPATH=compiler:.
    /Users/nn0cl/Documents/git/qpex/.venv/bin/python -m pytest tests/ -q
    -p no:cacheprovider`.
  - Spec compliance: **161/161**, 100%, gate PASS; run from `/private/tmp`
    because SV-17 writes a relative sink file.
  - Refactor baseline: 3 cases generated; `cmp` passed.
  - Other blocking local checks: document lifecycle passed (1 register),
    coverage consistency passed, active-Red lifecycle passed (0 active
    entries), execution-batch review validation passed (20 records), baseline
    JSON parse passed, and `git diff --check` passed.
  - Environment: macOS Darwin 27.0.0 arm64; Python 3.14.6; pytest 9.1.1.
    Test start/end timestamps were not captured; elapsed duration is available
    for the all-root run only. Pytest cache plugin was disabled for the root
    run to avoid managed-worktree write restrictions. GitHub CI: not run.
- Tested SHA/environment: tested working tree based on
  `0e32937f4bf90f7541f146feaa7c95670437acb2`; dirty; no final commit exists.
- New/resolved failures: none observed; all suites completed successfully.
  The Phase 2 root result was also 2,260 passed. No comparable failing
  baseline is known. No tests were collected as failures or left unassessed in
  the completed commands.
- Spec-to-change mapping: successor ownership and duplicate-body retirement
  are asserted by the five LISS-0578 structural checks; value, binder,
  short-circuit, set-comprehension, and Operator-resolution consumers are
  covered by the named LISS-0424/0427/0428/0429/0430 suites. Compatibility
  wiring and runtime hook identity are checked against the actual installer.
  No assertions, fixtures, exclusions, behavior, ordering, or diagnostics
  changed during Phase 3.
- Consumer compatibility: static private/dynamic hook inventory found
  `Evaluator._bind`, `evaluation/classical.py::evaluate_value`,
  `evaluation/binding.py`, `evaluation/operators.py`, and the compatibility
  installer/setup path. Named characterization suites exercised the real
  routes; dynamic class-hook identity was asserted. Static search cannot
  discover arbitrary runtime monkey-patching outside this repository.
- Structure-budget disposition: runtime routing does not define a
  `[source_structure]` section, so no numeric enforcement budget is active.
  The target successor is 147 physical lines; `evaluator.py` is 1,477 lines
  after extraction (1,620 at the recorded pre-extraction baseline). The
  `review-change.py --base HEAD` aggregate reports `unknown` because changes
  are dirty/untracked; target file sizes and source diff were measured
  directly. No enabled large-change override applies; configured review
  isolation is `same_context`.
- Effective review route: same-context role switch, weaker isolation than a
  separate-context reviewer. Reviewer re-read canonical artifacts and source
  from disk; author reasoning was not used as evidence. No model switch was
  configured or available. This review packet does not replace Adjudicator
  review.
- Adjudicator accepted this review on 2026-09-24 as
  `WP-0171 / LISS-0578 Phase 3 最終レビュー 承認`. Next: final commit and
  blocking-suite verification, followed by process review before closure.

## Evidence links

- Canonical Register: not applicable to this bounded implementation review.
- Representative Trace: `docs/collaboration/traces/2026-09-24-liss-0578-phase0.md`.
- Detailed Evidence: this review packet and the deterministic command outputs
  recorded in the trace; baseline capture file is `/tmp/liss-0578-p3-baseline.json`,
  spec output is `/tmp/liss-0578-p3-spec.log`.
