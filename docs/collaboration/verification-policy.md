# Verification Evidence and Consumer Compatibility

Canonical policy for verification in Phase 2/3 and final review. Project suite
commands, environments and layout belong in target-owned project conventions.

## Declared scope and states

Declare the blocking suites before implementation, with commands, cwd,
required environment and approved exclusions. Record focused, consumer import
smoke, adjacent regression and all-blocking results separately. A focused
success is not full Green. States are `passed`, `failed`, `not_run`,
`environment_blocked`, `excluded`; expected Phase 1 Red is reported as Red.
Only all declared blocking suites passing establishes full Green. Exclusions
need an explicit scope and human disposition; a follow-up Issue is not a waiver.

For each run record tested commit SHA, tree/dirty status, baseline SHA,
command, cwd, OS/runtime/dependency versions, start/end time, exit code,
test/check total, failures, errors, skipped/excluded counts and evidence path.
Unknown counts remain unknown; collection failure is not zero successful tests.
Do not log secrets or complete environment-variable dumps.

Compare failure IDs against the baseline in a comparable environment. Separate
new/resolved failures, root causes and affected suites/cases. An import error
may stop many suites; uncollected cases remain unassessed, not fabricated failures.
If baseline cannot run, say comparison unavailable instead of “no new failures”.
Report pre-existing blocking failures; do not turn them into full Green.

## Final commit

After the final commit, run every blocking suite against that SHA. Preserve
evidence in CI logs/artifacts tied to the SHA or outside the working tree.
Evidence from an earlier commit is not current completion evidence. A later
evidence/documentation commit creates a new HEAD requiring another run.
Rebase, merge and dependency/environment changes invalidate applicability;
branch-head and merge-result verification are separate claims.
Uncommitted runs are provisional and must identify dirty state.

## Splitting and existing consumers

Before splitting, inventory all discoverable consumers, import paths and used
symbols, including private/underscore names, re-exports, CLI entry points,
registrations and dynamic/plugin loading. Record limitations of static search.
Compare before/after paths and symbols and run imports through the actual
consumer entry points, not only the new facade. Wildcard exports need explicit
attention to private symbols. Run adjacent regression and final all-blocking
suites, including spec-compliance checks if the project declares them.
Review serialization, diagnostics, error boundaries, ordering and cycles as
applicable. Mechanical import counts do not prove semantic compatibility.

## Review evidence

Map acceptance clauses to changes and tests. Identify new behavior, weakened
assertions, changed fixtures, exclusions, moved failures and implicit error or
ordering changes. Each needs a stated specification basis or human disposition.
Moving implementation to a legacy/helper file is not evidence of separated
responsibilities. Use `docs/templates/verification-record.md` for the record.

## Template tooling

`python3 scripts/run-regression-tests.py` emits scoped JSON evidence for the
template regression suite. It is not the whole blocking suite. The repository
CI also checks required documents, ADRs, syntax, records, conflicts, copy smoke
and PR traceability. Python tools require Python 3.11+; adopters define their
own application test suites. CI logs retain execution evidence at the job SHA.
