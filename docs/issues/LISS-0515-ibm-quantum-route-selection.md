# LISS-0515: IBM Quantum route selection and adoption record

| Field | Value |
|---|---|
| Status | **in_progress — technology selection approved; Phase 1 Red pending** |
| Phase | phase-0-design |
| Type | provider technology selection |
| Priority | P0 |
| Initial size | M |
| Current size | M |
| Parent | WP-0132 |
| Depends on | LISS-0514 |
| Blocks | IBM adapter Phase 1 Issue and IBM real-QPU pilot |
| Implementation permission | None |
| Post-review requirement | Phase 1 Red approval |

## Review outcome

Recommended route: `qiskit-ibm-runtime` with `QiskitRuntimeService` and
Sampler V2; use OpenQASM 3 as Host input and defer backend/device selection
until account access is verified. See the [provider technology-selection review](../collaboration/reviews/2026-09-10-provider-technology-selection-review.md).

## Objective

Choose the bounded IBM Quantum access, artifact, capability, SDK/API, and first
device contract required before tests can be written.

## Phase 0 scope

- Compare IBM Quantum Platform and IBM Cloud access only as execution routes.
- Decide whether the initial artifact is OpenQASM, QIR, or an explicitly
  bounded provider form.
- Record candidate SDK/API version, optional dependency boundary, device
  capability source, status/result mapping, and cost/credential preflight.
- Select one Bell/GHZ-capable pilot device or record the selection blocker.

## Luna execution packet

- Model: `gpt-5.6-luna`; reasoning: `high`; web research allowed only against
  official IBM documentation.
- Include: this Issue, WP-0132, LISS-0514 output, dependency policy, existing
  QASM/QPU port contracts, and minimal IBM official pages.
- Omit: credentials, account pages, unrelated providers, and implementation.
- Allowed changes: this Issue, WP-0132, one provider-adoption note, and trace.
- Output: dated evidence table, selected/rejected alternatives, compatibility
  state (`verified`, `inferred`, or `unknown`), risks, and approval request.
- Stop before dependency installation, tests, or provider calls.

## Verification

- All technology claims have official source URLs and capture dates.
- `git diff --check` and documentation-link check pass.
