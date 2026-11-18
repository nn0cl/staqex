# Review Summary — LISS-0594 GU compatibility supplement Phase 3

## Review packet

- **Scope:** GU01–GU09 compatibility supplement only. The main
  `unitarity_check.py` decomposition remains in Phase 1 Red and is not
  implemented by this review.
- **Approval:** Adjudicator approved Phase 3 Refactor/review on 2026-10-28.
- **Canonical documents:**
  [LISS-0594](../../issues/LISS-0594-unitarity-check-family-separation.md),
  [unitarity spec](../../specs/unitarity-check-family-separation.md),
  [GU design/trace](../traces/2026-10-26-liss-0594-guard-path-compatibility-design.md),
  [WP-0175](../../work-plans/WP-0175-source-responsibility-inventory.md),
  `docs/collaboration/verification-policy.md`,
  `docs/collaboration/source-code-quality.md`,
  `docs/collaboration/runtime-routing.toml`.
- **Changed files reviewed:** `tests/liss_0593_guard_support.py`,
  `tests/test_liss_0591_guard_migration_red.py`,
  `tests/test_liss_0593_guard_composition_red.py`,
  `tests/test_liss_0594_unitarity_family_red.py`,
  `docs/testing/active-red-tests.toml`, LISS-0594 Issue/spec, WP-0175,
  representative traces, and the process-lessons log.
- **Findings and dispositions:**
  1. The missing-artifact diagnostic in `new_test_paths()` named only LISS-0593
     although the exact LISS-0594 follow-on path is included. **Applied:** use
     the neutral composed-inventory wording. No assertion or path contract
     changed.
  2. No blocking compatibility or consumer finding remains for GU01–GU09.
     The exact singleton remains separate from the frozen 26-path cohort;
     P10/R06/F09/G07 copied-root and inherited consumers pass.
  3. The still-failing structural assertion is the intended LISS-0594 main
     source Red. It is out of scope for this GU supplement and remains active.
- **Assertion/exclusion changes:** no accepted assertion was removed or
  weakened. The LISS-0591 B08 synthetic inventory now includes only the exact
  accepted singleton. The LISS-0593 copied-root setup copies the same file and
  restores the real Git inventory runner before consumer execution. The
  lifecycle manifest excludes the LISS-0594 module from ordinary blocking
  pytest because its main-source structural Red remains; the whole module was
  separately exercised in the focused run. No inherited test exclusion or
  skip was added.
- **Review isolation:** `same_context`, as configured. This is weaker than
  separate-context review; the reviewer re-read the specification, change and
  deterministic outputs from disk. No separate-context review was available
  or required by the configured route.
- **Structure disposition:** no production implementation body changed.
  Manual worktree accounting from HEAD found 1,363 inserted/deleted lines
  across tracked and untracked files; 392 Python lines are added, all in
  test/support code, with zero production-source additions.
  `tests/test_liss_0594_unitarity_family_red.py` is 344 lines; it stays one
  path because GU08 requires the exact singleton follow-on artifact and a
  second module would expand the accepted path inventory. The pre-existing
  668-line LISS-0593 composition module received only bounded consumer setup
  and expected-inventory updates. No `[source_structure]` budget is configured.
  `review-change.py` reports structured metrics unknown because the working
  tree is dirty; the manual counts above cover change size, while a clean
  committed revision is still needed for its implementation-size report.
  `[review.large_change]` is not enabled, so normal same-context routing
  remains effective.
- **Verification result:** provisional pass for the GU supplement on dirty
  worktree HEAD `93a2548ae168a70a3c3340bf79533de95828dc39`, macOS arm64,
  CPython 3.12.6, pytest 9.0.3.

  | Verification | Result |
  |---|---:|
  | Focused LISS-0594 + LISS-0411/0436/0376 | 29 passed; 1 expected structural Red |
  | Inherited LISS-0591 + LISS-0593 suites | 319 passed |
  | Root blocking pytest (`tests/ -q --ignore=tests/test_liss_0594_unitarity_family_red.py`) | 3,589 passed, 0 failed |
  | Spec verification | 161/161 passed |
  | Test/document lifecycle | passed |
  | Coverage/Open Topics consistency | passed |
  | Execution-batch review records | 20 validated |
  | Refactor baseline | 3 cases passed |
  | Repository template-copy smoke | passed in a temporary clean checkout at HEAD |
  | Changed Python syntax / `git diff --check` | passed |

- **Environment comparison:** an initial inherited-suite run with venv
  Python 3.14.8/pytest 9.1.1 had 49 failures in AST baseline comparisons.
  A representative failure passed alone with CI-compatible Python 3.12.6, and
  the complete inherited suite passed 319/319 there. The 3.14 result is
  environment-incompatible evidence, not a code regression. No baseline
  failure remains in the comparable 3.12.6 run.
- **Remaining verification gaps:** final-SHA evidence is unavailable because
  no commit was made; required all-blocking reruns remain after an explicitly
  authorized commit. PR-only contract-traceability is not applicable without
  a PR. The template-copy smoke initially refused the dirty checkout because
  the untracked spec is a distributed source; it passed from a temporary clean
  clone at the same committed HEAD, which does not contain the uncommitted
  LISS-0594 changes.
- **Next approval at this Phase 3 checkpoint:** separate Adjudicator
  final-verification approval. It was received on 2026-10-28; the review
  approval did not authorize commit, push, PR, or merge.

## Final verification — 2026-10-28

- **Approval:** Adjudicator approved final verification on 2026-10-28.
- **Scope:** rerun GU supplement focused/consumer suites, the active-Red-aware
  root suite, spec verification, and lifecycle checks against the latest
  working-tree contents. No production or test source changed after the Phase 3
  review; only review/status documentation changed.
- **Initial dirty-tree results:** HEAD `93a2548ae168a70a3c3340bf79533de95828dc39`,
  dirty working tree; macOS arm64, CPython 3.12.6, pytest 9.0.3. Focused
  LISS-0594 plus LISS-0411/0436/0376: 29 passed and the
  single expected main-source structural Red; inherited LISS-0591/0593:
  319 passed; root pytest with the declared LISS-0594 Active-Red exclusion:
  3,589 passed / 0 failed; spec verification 161/161. Test lifecycle,
  document lifecycle, coverage/Open Topics, execution-batch records (20),
  refactor baseline (3 cases), Python compilation and diff checks passed.
- **Disposition:** GU compatibility supplement local final verification
  passed. No new or unresolved failures appeared in the CI-compatible
  environment. The structural Red remains active for the main decomposition.
- **Committed-SHA revalidation:** after separate approval, commit
  `638c8956f8f1ff2d8808ef2cba68e66bd18a5922` was tested with a clean worktree.
  Focused 29 passed / 1 expected structural Red; inherited 319 passed; root
  blocking pytest 3,589 passed / 0 failed; spec 161/161. Required documents
  and ADRs (99), shell syntax, repository lifecycle/coverage, execution-batch
  (20), baseline (3 cases), Python syntax, diff checks and template-copy smoke
  passed. Environment: macOS arm64, CPython 3.12.6, pytest 9.0.3.
- **Remaining limits:** PR-only contract-traceability is not applicable
  without a PR. The template-copy smoke initially refused the dirty checkout
  because the untracked spec is a distributed source; it passed in a temporary
  clean clone and was repeated at the committed SHA above.

## Evidence links

- Canonical Register: not applicable; the project has no canonical-document
  register for this source-area task.
- Representative Trace:
  [2026-10-26 GU compatibility design](../traces/2026-10-26-liss-0594-guard-path-compatibility-design.md).
- Detailed Evidence: LISS-0594 Issue and the linked specification above.
