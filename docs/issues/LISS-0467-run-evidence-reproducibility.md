# LISS-0467: Run evidence and reproducibility envelope

| Field | Value |
|---|---|
| Status | **done — Phase 3 refactor complete** |
| Phase | phase-3-refactor |
| Type | experiment / evidence |
| Priority | P0 |
| Initial size | L |
| Current size | L |
| Owner | Host experiment boundary |
| Parent | WP-0119; WP-0124 |
| Depends on | LISS-0458, LISS-0466 |
| Blocks | LISS-0468, LISS-0469 |
| Branch | `codex/liss-0467-run-evidence-reproducibility` |
| Acceptance spec | [Real-QPU readiness acceptance](../specs/staqex-real-qpu-readiness-acceptance.md#liss-0467--reproducibility-evidence) |
| Implementation permission | None |
| Post-review requirement | Evidence-protocol review and typed Phase 1 approval |

Define the run envelope: source and semantic fingerprints, artifact hash,
provider/device/job IDs, compiler and SDK versions, shots, seeds, calibration
snapshot, noise metadata, timestamps, cost, and capability profile. Define
statistical tolerances, drift handling, and prohibited claims. Separate
reproducibility evidence from physical fidelity claims.
## Design detail

**In:** source/semantic/artifact/provider/device/job identities, compiler/SDK
versions, shots, seeds, calibration/noise, timestamps, cost, capability
profile, baseline, tolerances, and drift policy. **Out:** secrets, raw private
provider exports, invented calibration, or unsupported fidelity claims.

**Acceptance:** a run envelope traces source to measured result; required fields
are immutable or versioned; simulator baseline and statistical criteria are
named; missing evidence yields incomplete/inconclusive status.

**Phase/evidence:** Phase 0 schema and evidence contract; Phase 1 Red
schema/baseline tests; Phase 2 local/fake evidence generation; Phase 3 review
of one complete envelope. Planning record:
`AIP-LISS-0467-2026-08-27-001` (L; N/A model metrics).

## Phase 1 Red artifact

- Added `tests/test_liss_0467_run_evidence_reproducibility_red.py`.
- The test-only contract covers versioned source-to-result linkage, identity
  fingerprints, target/provider/device/job metadata, compiler/SDK/shots/seed,
  baseline/tolerance/drift fields, and simulator evidence without physical
  fidelity claims.
- Missing identity links must be `incomplete`; unexplained drift must be
  `inconclusive`; calibration must not be invented. No secret or raw private
  provider export is included.
- Red is confirmed by the intentionally absent
  `compiler.staqex.evidence_envelope` module. Phase 2 evidence generation
  remains unapproved.

## Phase 2 Green artifact

- Added `compiler/staqex/evidence_envelope.py` for local/fake versioned
  evidence generation.
- The envelope carries source/semantic/artifact and job identity, runtime
  metadata, baseline/tolerance/drift fields, and explicit non-fidelity claims
  for simulator/fake evidence.
- Missing links are `incomplete`; unexplained drift is `inconclusive` without
  invented calibration. Contract tests, Python 3.14 `py_compile`, and
  `git diff --check` pass. Phase 3 review remains gated.

## Phase 3 closeout

- Extracted envelope status and fidelity-claim decisions into focused helpers
  without changing complete/incomplete/inconclusive outcomes.
- Contract tests, Python 3.14 `py_compile`, and `git diff --check` pass.
- Same-context complete-envelope review found no blocker; this isolation is
  weaker than separate-context review.
- Process review: no operating-contract deviation or operational problem
  found. Provider data, secrets, and physical-fidelity claims remain gated.
