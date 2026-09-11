# LISS-0541 / WP-0158 Phase 3 最終レビュー

- Date: 2026-09-11
- Scope: D05 S02 quantum projection and classical baseline comparison
- Approval received: `LISS-0541 Phase 3 最終レビュー 承認`
- Isolation: `same_context`; this is weaker than a separate-context review.
- Reviewer posture: reviewer role; no implementation was continued during review.

## Canonical artifacts re-read

- [WP-0158](../../work-plans/WP-0158-s02-quantum-baseline-comparison.md)
- [LISS-0541](../../issues/LISS-0541-s02-quantum-baseline-comparison.md)
- [Scientific Workflow acceptance specification](../../specs/staqex-scientific-workflow-acceptance.md)
- `compiler/staqex/s02_quantum_baseline_comparison.py`
- `tests/test_s02_quantum_baseline_comparison_red.py`
- `compiler/staqex/s02_classical_batch_baseline.py`
- `compiler/staqex/quantum_artifact.py`
- Applicable process lessons: coverage-authority-boundary,
  acceptance-boundary, phase-acceptance-boundary.

## Verification re-run

- `PYTHONPATH=. .venv/bin/pytest -q tests/test_s02_quantum_baseline_comparison_red.py tests/test_s02_classical_batch_baseline_red.py tests/test_liss_0520_sqxa_runtime_loader_red.py`: **14 passed**
- `python3 -m py_compile compiler/staqex/s02_quantum_baseline_comparison.py tests/test_s02_quantum_baseline_comparison_red.py`: pass
- `git diff --check`: pass

## Finding B1 — comparison lineage is not machine-checked

The accepted Phase 0 contract requires identical snapshot/cutoff, candidate
set, profile revision, baseline/artifact identity, encoding, and manifest
identity before a comparison is accepted. `ComparisonInput` stores these
identities only once at the outer boundary, while `LaneResult` carries none of
them. `compare_baseline_and_quantum` validates only selected candidate IDs,
feasibility, objective, and cost. It therefore cannot detect or report a lane
produced from a different snapshot, profile, artifact, encoding, or manifest;
the caller could supply a shared outer identity even when the lanes came from
different inputs.

Disposition: blocker. Add a bounded Phase 1 Red contract for lane lineage and
artifact identity, then implement fail-closed
`QUANTUM_CANDIDATE_SET_MISMATCH`/`QUANTUM_BASELINE_MISMATCH` handling in the
next Phase 2. Do not mark LISS-0541/WP-0158 done.

## Finding F1 — current passing scope is intentionally narrower

The implementation is a provider-neutral comparison kernel. It does not run a
QUBO, invoke the Q01 artifact loader, or submit to a finite target. Those
responsibilities remain separate by the accepted boundary and live QPU/provider
work remains out of scope. This is acceptable for the current bounded slice,
but the next Red contract must make the artifact/manifest lineage explicit.

## Decision

`LISS-0541 Phase 3 最終レビュー` is **not approved**. The issue remains
`phase-3-refactor` / final-review-pending. The focused behavior is green, but
the accepted identity boundary is incomplete.

## Next requested approval

After the bounded Red contract correction and readiness record were updated:

`LISS-0541 Phase 2 Green / Implementation 再承認`

## Phase 1 Red lineage-contract correction verification

The approved correction added only lane-lineage fixture fields and two
contracts: snapshot/artifact mismatch quarantine and lineage preservation in
a matched result. The focused suite now collects 7 intentional failures,
because the current `LaneResult` and `ComparisonResult` production DTOs do
not yet accept or validate the new fields. `py_compile` and `git diff --check`
pass; no production, provider, network, credential, or live-QPU code changed.

Disposition: Red correction complete. The next gate is
`LISS-0541 Phase 2 Green / Implementation 再承認`.

## Phase 2 Green lineage-contract correction verification

The implementation now carries the approved lineage identities on each lane,
checks lane-to-lane and quantum-to-input identity equality before comparison,
and preserves the evidence on matched results. The focused D05 suite reports
7 passed; `py_compile` and `git diff --check` pass. Provider, network,
credential, and live-QPU behavior remain out of scope.

Disposition: Phase 2 Green complete. The next gate is
`LISS-0541 Phase 3 Refactor 承認`.

## Phase 3 Refactor verification

The lineage field list and diagnostic mapping were consolidated into private
helpers/constants. Public DTOs, assertions, diagnostic codes, precedence,
and fallback behavior were preserved. The focused D05 and related S02 suites
report 16 passed; `py_compile` and `git diff --check` pass.

Disposition: Phase 3 Refactor complete. Final review remains pending:
`LISS-0541 Phase 3 最終レビュー 承認`.

## Final review disposition

The accepted D05 lineage and comparison boundaries are implemented and
verified. No blocker was found. D05 plus related S02 verification reports 16
passed; `py_compile` and `git diff --check` pass. The bounded
provider-neutral comparison kernel is approved as complete. Broader scientific
profiles and provider delivery remain separate work.

Process review: no operating-contract deviation or operational problem found.
