# LISS-0437 Phase 2 independent implementation review

## Review metadata

- Date: 2026-08-14
- Scope: Phase 2 implementation and its acceptance/regression tests
- Reviewer context: independent subagent, fresh context, read-only
- Lenses: all nine perspectives in
  `docs/collaboration/independent-review-perspectives.md`
- Initial verdict: **Not ready**
- Correction round: completed in the same work session; re-review required

## Initial findings and resolution status

| Lens | Finding | Resolution in this round |
|---|---|---|
| Runtime realization | `Evolve()` used the legacy seed-count path and could not execute. | Added an explicit runtime path for named and inline canonical `exp(-i * H * t / hbar)` propagators. |
| Target boundary | QPU lowering could fall through to a partial/fallback circuit. | Added an early capability rejection before allocation; the returned circuit has no gates. |
| Physics safety | Explicit mode was routed through the opaque `times`-block unitarity rule. | Added a separate explicit branch and retained canonical generator Hermiticity checking. |
| Migration | Legacy Hamiltonian spelling was only a compatibility diagnostic. | Documented the bounded compatibility window and added `strict_evolution=True` compile/profile behavior that makes the diagnostic fail compilation. |
| Type/dimension | Hamiltonian dimension depended on the identifier name. | Operator dimensions now come from the explicit operator expression, including coefficient scaling. |
| Diagnostics | `Limit` and malformed explicit bodies could produce duplicate diagnostics. | Generic operator calls return their inferred type once; shape errors remain typechecker-owned. |
| IR evidence | Explicit mode had only a boolean discriminator. | DAG retains explicit mode, source span, operator-state application, and generator/exponent/propagator/state provenance references. |
| Semantic deferral | Explicit mode suppressed all generic qsem obligations. | Deferral is limited to the case where all emitted qsem diagnostics are the two known target-realization obligations; unrelated diagnostics remain visible. |

## Evidence

- `python3 tests/test_liss_0437_explicit_evolution_surface_red.py`
- `python3 tests/test_liss_0436_evolve_times_block_transparency_red.py`
- `python3 tests/test_evolve_until_runtime_red.py`
- `python3 -m compileall -q compiler/staqex`
- `git diff --check`
- S02 `compile_path` returns `ok=True` with no diagnostics.

## Residual boundaries for the next phase

- QPU realization of explicit evolution remains rejected with
  `EVOLUTION_TARGET_UNSUPPORTED`; no QPU deployment is claimed.
- Formal `Limit` remains source-preserving but requires a finite target
  realization and is not executable in this phase.
- Broad corpus migration and the final strict migration policy remain
  separate work and require their own approval.

## Re-review finding and correction

The fresh re-review found two remaining issues: Hermiticity checking lost
dimensioned coefficient symbols such as `scale`, and malformed `State *
Operator` bodies emitted both the operand-order error and the enclosing
explicit-Evolve error. The checker now supplies neutral witness values only
for static Hermiticity analysis and removes the nested operand-order
diagnostic inside the explicit-Evolve contract. Direct probes now produce one
`NON_UNITARY_TRANSFORM_ERROR` for `scale * (X * Y)` and one
`EVOLVE_REQUIRES_EXPLICIT_TRANSFORM` for `State * Operator`.

## Final independent verification

The final fresh-context verification confirmed inline and named propagator
runtime execution, QPU rejection before allocation, strict migration
rejection, one diagnostic for malformed explicit application,
coefficient-aware non-Hermitian generator rejection, DAG provenance, qsem
preservation, S02 compilation, and regression slices.

The reviewer retained **Not ready** only for work explicitly outside this
Phase 2 minimum slice: QPU realization, formal `Limit` execution, broad
corpus migration, and Phase 3 numerical equivalence. Those remain named
residuals and are not silently promoted to Phase 2 requirements.

## Phase 3 first target-realization review

An independent fresh-context review returned **READY** for the bounded first
slice. It confirmed 161/161 specification checks, preservation of the
`times N` path, profile evidence for approximation/resources/capabilities,
profile-less fail-closed behavior, canonical `-i` Suzuki lowering, invalid
policy and positive-`i` rejection, S02 compilation, and `git diff --check`.
Formal `Limit` execution, broad migration, S02 numerical equivalence, and
real QPU submission remain explicit later boundaries.

## Final Phase 3 first-slice correction

The final independent review found one S02 README mismatch: the terminal
example measured `psi_sel` while the migrated source measures `psi_final`.
The README was corrected. The bounded Phase 3 first target-realization slice
is now READY; the full specification gate remains 161/161 PASS.

## Reviewer perspective to retain

Reviewers should distinguish source acceptance from target realization,
exercise both named and inline blackboard forms, test that unsupported targets
return no partial artifact, verify physical dimensions from expressions rather
than names, and inspect whether provenance survives the AST-to-IR boundary.
