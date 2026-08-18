# LISS-0437 Phase 3 Green bounded target-boundary review 01

## Result

- Context: fresh independent read-only reviewer.
- Verdict: **READY for the approved bounded slice**.
- Reviewer: agent `01a000fb-a2d6-7f23-9ccd-c25735391ac5`.
- Scope excluded: formal `Limit` execution, S02 numerical migration, live QPU
  deployment, and any later phase approval.

## Findings and evidence

- Mapping validation rejects `q[0..3]` for a finite binder domain `0..7` and
  accepts only an exact `q[start..end]` witness.
  Evidence: `compiler/staqex/backend/qasm/lower.py:726-739`.
- Target preflight runs before the `forEach` allocation loop.
  Evidence: `compiler/staqex/backend/qasm/lower.py:293-302` precedes
  `compiler/staqex/backend/qasm/lower.py:344-360`.
- The Red runner has six tests and reports `1/6` failing; the sole failure is
  the intentionally unimplemented formal-Limit provenance case. All five
  approved target-boundary cases pass.
  Evidence: `tests/test_liss_0437_phase3_red.py:332-353` and deterministic
  execution trace.

## Reusable perspectives

- Validate typed mapping shape and domain coverage, not field presence alone.
- Verify rejection order against allocator control flow, not only empty output.
- Separate expected residual Red failures from failures in the approved Green
  slice.
- Keep READY scoped to the named slice; it is not approval for Limit, S02, or
  deployment.

## Gate status

- Approved implementation completed: typed mapping, mapping/budget separation,
  common rejection provenance, and allocation-before-rejection safety.
- Phase 3 Green bounded slice: READY.
- Formal `Limit`, S02 numerical migration, and live QPU deployment: not
  approved and not implemented.
- Terminal state: `COMPLETE` for this review loop.
