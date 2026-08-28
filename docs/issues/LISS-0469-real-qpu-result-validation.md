# LISS-0469: Real-QPU result validation and disposition

| Field | Value |
|---|---|
| Status | **done — Phase 3 refactor complete** |
| Phase | phase-3-refactor |
| Type | experiment validation |
| Priority | P0 |
| Initial size | L |
| Current size | L |
| Owner | Adjudicator + experiment reviewer |
| Parent | WP-0119; WP-0124 |
| Depends on | LISS-0467, LISS-0468 |
| Blocks | LISS-0470 |
| Branch | `codex/liss-0469-real-qpu-result-validation` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0469--result-validation-and-disposition) |
| Implementation permission | None |
| Post-review requirement | Validation-protocol review and typed Phase 1 approval |

Compare the real result with the CPU/simulator baseline using declared
statistical and physics checks. Record calibration drift, noise, failed shots,
provider anomalies, and limitations. Classify the outcome as valid evidence,
inconclusive, or rejected; never silently tune the source or claim hardware
support from a single passing sample.
## Design detail

**In:** declared CPU/simulator baseline, expected observable, shot statistics,
calibration/noise context, drift, provider anomalies, and valid/inconclusive/
rejected disposition. **Out:** changing source/compiler after seeing data,
unbounded claims, and replacing physics review with a single threshold.

**Acceptance:** validation uses criteria declared before the run; raw and
derived evidence remain distinguishable; anomalies produce explicit
disposition; source/artifact identity is unchanged by analysis.

**Phase/evidence:** Phase 0 validation protocol; Phase 1 Red baseline/statistics
tests; Phase 2 offline analysis; Phase 3 independent review of the pilot.
Planning record: `AIP-LISS-0469-2026-08-27-001` (L; N/A model metrics).

## Phase 1 Red artifact

- Added `tests/test_liss_0469_result_validation_red.py`.
- The test-only contract covers predeclared criteria, raw/derived evidence
  separation, valid/inconclusive/rejected disposition, calibration drift,
  failed shots, provider anomalies, statistical deviation, and immutable
  source/semantic/artifact identity.
- Red is confirmed by the intentionally absent
  `compiler.staqex.result_validation` module. No real-QPU result, provider
  data, credential, or network call was used.
- Phase 2 offline analysis remains unapproved.

## Phase 2 Green artifact

- Added `compiler/staqex/result_validation.py` for offline result analysis.
- Raw results and derived statistics remain distinct; predeclared criteria,
  drift, failed shots, anomalies, and statistical deviation produce explicit
  dispositions without source or identity rewrite.
- LISS-0469 contract tests, Python 3.14 `py_compile`, and
  `git diff --check` pass. No real result, provider data, credential, or
  network was used. Phase 3 review remains gated.

## Phase 3 closeout

- Extracted disposition and derived-statistics construction into focused
  helpers without changing raw/derived separation, criteria, or identity.
- Contract tests, Python 3.14 `py_compile`, and `git diff --check` pass.
- Same-context validation review found no blocker; this isolation is weaker
  than separate-context review.
- Process review: no operating-contract deviation or operational problem
  found. Real-result analysis and physical-fidelity claims remain gated.
