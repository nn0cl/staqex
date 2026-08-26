# LISS-0444 finite instruction projection — Phase 2 Green review 02

| Field | Value |
|---|---|
| Trigger | User-approved Phase 2 Green implementation followed by independent review/correction loop |
| Scope | Finite Suzuki/binder canonical QPU instruction projection and QASM consumer boundary |
| Context boundary | Fresh read-only reviewer; no worktree edits, approval, provider, network, or QPU access |
| Final status | **READY / COMPLETE** for the bounded Phase 2 Green slice |
| Phase status | Implementation and Phase 2 approval were granted before this review; review does not grant a new phase approval |

## Findings and disposition

1. **Accepted, corrected — P1:** invalid or unresolved Suzuki order could
   reach fallback or retain a default order. The canonical projection now
   fails closed, emits no lowering policy/instructions/QASM, and tests cover
   order 3 and an unresolved order name.
2. **Accepted, corrected — P1:** projection errors could leave partial QPU
   instructions, including Measure. Rejected projections now expose an empty
   instruction sequence; the emitter rejects atomically.
3. **Accepted, corrected — P2:** instruction-level evidence was too weak.
   Tests now cover opcode, wires, parameter, both Suzuki steps, Evolve source
   identity, Measure provenance, and recomputed-fingerprint mutation.
4. **Accepted, corrected — P1:** a caller could mutate instructions and
   recompute the instruction fingerprint. The emitter now compares finite
   canonical gate operations and canonical Measure operations, including
   provenance.
5. **Accepted, corrected — P2:** expected/actual finite validation filters
   were asymmetric and could reject QFT or ordinary canonical operations in a
   mixed program. Both sides now use the `Evolve.Suzuki` provenance boundary.
6. **Rejected as out of scope / recorded boundary — P2:** the old AST fallback
   remains in non-finite and not-yet-migrated compatibility paths. WP-0107
   explicitly defers consumer-wide migration; valid finite Suzuki/binder
   paths return through canonical instructions before that fallback.
7. **Deferred, recorded — P3:** a dedicated mixed Suzuki+ordinary-gate test
   can be added if that source surface is admitted. The current symmetric
   source filter removes the observed false rejection.

## Reusable perspectives

Contract completeness; source-to-domain fidelity; canonical authority;
projection conservation; executable projection integrity; realization and
fail-closed behavior; migration/regression safety; phase/approval discipline;
evidence hygiene; symmetric projection validation.

## Verification evidence

- Finite and related consumer suites: **26 passed**.
- Full `.venv/bin/pytest -q`: **1650 passed**.
- `git diff --check`: passed after documentation synchronization.
- No provider SDK, live QPU submission, network, S02 numerical migration, or
  solver implementation was performed.

## Terminal state

`COMPLETE`: all in-scope findings were corrected or dispositioned with
authority, the final independent review was READY, and no review blocker
remains. This does not complete WP-0107 or authorize a subsequent phase.
