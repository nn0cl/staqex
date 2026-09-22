# LISS-0573 Phase 1 Red test review

## Review boundary

- Scope: WP-0167 Unit C — evaluator pipes, block expressions, and polynomial
  fusion successor.
- Phase: Phase 1 Red test review.
- Review isolation: `same_context`; weaker than `separate_context`.
- Tested SHA: `39e995f900574bf63db546a5cee4b89aa872cb39` with a dirty
  worktree; no commit-specific result is claimed.
- Environment: macOS, repository virtualenv, Python 3.14.

## Artifacts re-read

- LISS-0573 design issue and Phase 0 acceptance.
- WP-0167 Unit C design section.
- Unit C work trace.
- `tests/test_liss_0573_pipes_successor_red.py`.
- `docs/testing/active-red-tests.toml`.
- Current `evaluator.py`, `binding.py`, `context.py`, and compatibility wiring.

## Findings and dispositions

1. Five structural nodes fail for the declared migration gaps: successor
   absence, facade body retention, compatibility wiring, context callbacks,
   and facade-dependency boundary. Disposition: already closed with evidence
   as intentional Red contract; no implementation is inferred.
2. Six positive characterizations pass for block Trace-Out, affine fusion,
   polynomial fusion, non-finite rejection, multi-hole pipe filling, and
   affine parsing. Disposition: accepted as the behavior baseline for Green.
3. The first test run used the wrong result API in the fixture. Disposition:
   already closed with evidence; only the test fixture import/assertion was
   corrected, then the exact bounded suite was rerun.
4. No parser, typechecker, provider, QASM, or unrelated state-family change
   appears in the Red contract. Disposition: out of scope by accepted design.

## Deterministic verification

- Exact bounded rerun: **5 failed, 6 passed**.
- Active-Red lifecycle: `entries=1`.
- Document lifecycle: passed.
- Coverage-ledger consistency: passed.
- `git diff --check`: passed.
- No production implementation was added by this phase.

## Review result

The Phase 1 Red contract is accepted for the declared scope. The five
structural failures are intentional and the six passing characterizations are
adequate Green baselines. No blocker was found.

Next approval:
`WP-0167 / LISS-0573 Phase 2 Green / Implementation 承認`.
