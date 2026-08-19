# Independent context review: LISS-0443 Phase 2 Green

| Field | Value |
|---|---|
| Trigger | User requested notification after the independent review completed |
| Independent context | `01a01a03-26ce-7aa2-9af8-0047bec0e784` |
| Branch | `codex/liss-0438-residual-reconciliation` |
| Scope | LISS-0443/WP-0106, Phase 1 trace, Red tests, S02 report, ADR 0210, LISS-0438 regression |
| Verdict | **NOT READY** |
| Phase result | Phase 2 Green evidence is partial; Phase 3 and closeout not ready |
| Approval authority | Reviewer did not approve any phase or implementation |

## Findings

### P1 — Spec approval state is inconsistent

- **Evidence:** `docs/specs/staqex-s02-numerical-migration.md` still says
  `not approved for implementation`, while LISS-0443, WP-0106, and the Phase
  2 trace record Green completion.
- **Lenses:** Phase and approval discipline; Contract completeness.
- **Disposition:** `accepted` as a documentation correction. No architecture
  or implementation change is required.

### P1 — Numeric identity is incomplete

- **Evidence:** The Spec/Issue require input, seed, duration, weights, shots,
  baseline identity, tolerance, and provenance. `source_sha256` and
  `base_seed` are now recorded, but the Host input weights are not included in
  the manifest identity, and the failed report path lacks the successful
  path's manifest/baseline identity.
- **Lenses:** Contract completeness; Migration/regression safety; Evidence and
  context hygiene.
- **Disposition:** `deferred — user decision required`. Completing this would
  expand the approved Phase 2 result contract beyond the typed approval and
  requires deciding the canonical composite identity and failure-path schema.

### P1 — LISS-0403 full regression evidence is unavailable locally

- **Evidence:** LISS-0443 is 3/3, LISS-0438 is 5/5, and `git diff --check`
  passes. `python3 -m pytest tests/test_liss_0403_s02_benchmark_report.py`
  cannot run because pytest is not installed; a direct substitute did not
  provide a complete 20-shot pytest result.
- **Lenses:** Migration/regression safety; Evidence and context hygiene.
- **Disposition:** `accepted` as an evidence limitation. It blocks closeout
  evidence but does not by itself authorize a dependency or code change.

## Positive evidence

- The Phase 2 production diff is limited to adding `source_sha256` and
  `base_seed` to successful and failed report metadata.
- S02 source, baseline JSON, scoring, weights, duration, compiler/QASM code,
  and target submission behavior were not changed.
- Exact local / formal Limit / explicit finite Realize separation and atomic
  `QASM_TROTTER_UNSUPPORTED_H` rejection remain covered by 3/3 and 5/5 direct
  tests.

## Reusable reviewer perspectives

- Numeric identity should combine source hash, Host-input digest, seed
  schedule, shots, baseline identity, and realization policy.
- Success and failure paths require symmetric reproducibility metadata.
- Issue, Spec, WP, and trace phase/approval states must be cross-checked.
- Missing test runners, skipped tests, and interrupted runs must never be
  reported as PASS.

## Loop state

- **Terminal state:** `ABORT`
- **Reason:** the incomplete numeric identity requires a user decision about
  scope/schema, and full LISS-0403 evidence requires a provisioned pytest
  environment or an explicitly accepted alternative.
- **Next condition:** user decides whether to expand LISS-0443's contract and
  how to obtain full regression evidence; only then may correction/re-review
  resume.
