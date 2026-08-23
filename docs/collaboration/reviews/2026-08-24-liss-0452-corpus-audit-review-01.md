# LISS-0452 Phase 0 Corpus Audit — Independent Review 01

## Review scope and boundary

- Trigger: continuation after the Phase 0 corpus audit.
- Independent context: fresh read-only reviewer; no worktree edits, approval,
  implementation, merge, or push.
- Branch under review: `docs/liss-0452-corpus-audit`.
- Inspected artifacts: the LISS-0452 Issue, WP-0115, proposed specification,
  audit trace, S02 README/source, host benchmark report, and focused regression.

## Findings and disposition

1. **P1 — README/source state-name mismatch — accepted, deferred for Phase 1.**
   README sections 2–4 use `psi_sel`/`psi_sel(t)`, while
   `main_selection.sqx` distinguishes `psi_0`, `psi_sel`, and terminal
   `psi_final`. The audit now records the mismatch. Editing the example or
   README is deferred because WP-0115 requires source changes to have a
   separately reviewed specification and phase approval.
2. **P1 — incomplete corpus classification — accepted and corrected.** The
   audit now enumerates the only `.sqx` source in the S02 directory and
   classifies `main_selection.sqx` as partial, with README/host files recorded
   as supporting documentation artifacts.
3. **P1 — finite rejection evidence not precise — accepted and corrected.**
   The audit records `capability-rejected`, `QASM_TROTTER_UNSUPPORTED_H`,
   `submitted=False`, `partial_program=None`, and no target-plan provenance;
   it also records that no provider/QPU was contacted.
4. **P2 — stale branch metadata — accepted and corrected.** WP-0115 now names
   `docs/liss-0452-corpus-audit` for the Phase 0 audit.

## Review lenses

- Source-to-domain fidelity and physicist readability.
- Exact simulator versus finite realization and provider submission.
- Fail-closed capability rejection and artifact absence.
- Corpus inventory, per-example classification, and deterministic evidence.
- Phase, branch, and approval-boundary discipline.

## Readiness verdict

**NOT READY for Phase 1 Red.** The design-preserving documentation corrections
are applied, but the README/source terminology mismatch remains deferred until
the required Phase 1 approval. A fresh independent review must inspect the
current audit after these corrections. The reviewer cannot grant Phase 1,
implementation, architecture, or merge approval.

## Next review condition

Re-run an independent read-only review against the current branch and audit
record. If no blocker remains, request a separate typed Adjudicator approval
for Phase 1 Red boundary tests only.
