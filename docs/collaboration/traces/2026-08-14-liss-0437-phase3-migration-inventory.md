# LISS-0437 Phase 3 migration inventory

## Current inventory

The authoritative source-corpus inventory is the `.sqx` scan below. It finds
15 official/example files and 20 legacy `Evolve { ... }` expressions. A raw
repository-wide occurrence count is intentionally not used as a migration
metric: tests, specifications, review records, and compatibility fixtures
repeat the spelling for different acceptance purposes.

The compiler implementation contains no legacy source examples.

### Classification of official `.sqx` sources

- **Hamiltonian evolution, explicit generator and duration:** 14 files, 19
  expressions. These are valid candidates for mechanical surface migration to
  `Operator U_t = exp(-i * H * t / hbar)` followed by
  `Evolve() { U_t * state }.run()`, subject to each file's fixed-seed check.
- **Convergence-bounded evolution:** 1 file, 1 expression
  (`S01/main_fuel_search.sqx`). Its `until ... max ...` contract is not a
  plain canonical propagator and must remain until a separate bounded-target
  design is accepted.
- **Discrete `times N`:** none in the official `.sqx` corpus. Existing
  `times N` compatibility tests remain a separate semantic family.
- **Grid/Fock or other unsupported symbolic evolution:** none detected in the
  official `.sqx` corpus by the legacy `Evolve {` scan.

## Migration policy

Official examples are migration candidates because they teach the physicist
source surface. Tests are not bulk-rewritten: legacy syntax tests retain
compatibility and retirement diagnostics until their acceptance intent is
explicitly reclassified. This prevents a source migration from silently
removing regression coverage for the old mode.

## Ordered next slice

1. Classify the 15 `.sqx` examples into Hamiltonian, discrete `times N`, grid/Fock,
   and unsupported symbolic forms.
2. Migrate only Hamiltonian examples whose generator and duration are explicit
   and whose simulator baseline can be fixed-seed verified.
3. Leave `times N` examples unchanged and record why they are not Hamiltonian
   evolution.
4. Run the full 161-case specification gate after each example family.
5. Migrate tests only with a dedicated acceptance decision per test family.

The next safe implementation batch is one Hamiltonian example family at a
time, beginning with sources whose runtime baseline already has a fixed-seed
regression. The convergence-bounded S01 source is excluded from that batch.

## First candidate probe: B08

B08 has a fixed-seed regression and its written Hamiltonian/duration are
explicit. The probe exposed two implementation boundaries before source
mutation:

1. `H_chain` must be declared as `Operator` for the explicit exponent's
   `H * dur / hbar` dimension check to see the physical `Energy` dimension.
2. B08's tuple state is evolved and then measured with `tracing_out`. The
   current explicit tuple output path does not yet preserve a live linear
   carrier when the evolved tuple is renamed; keeping the original names also
   reports a duplicate linear use. The legacy B08 source still compiles and
   runs, so this is a compiler boundary rather than an example regression.

The tuple-state output/linear-carrier boundary was then specified by a Red
test, implemented, and verified. B08 is now migrated to:

```staqex
Operator U_dur = exp(-i * H_chain * dur / hbar)
State (s0, s1) = Evolve() { U_dur * (s0, s1) }.run()
```

The B08 fixed-seed example regression, the LISS-0437 explicit-surface suite,
and the 161-case specification gate all pass.

The next probe, B07, exposed a separate boundary: `H` is returned from
`ising_hamiltonian(...)`, and the type environment did not preserve the
returned operator's physical `Energy` dimension for explicit exponent
checking. A Red/Green slice now preserves `OpAttr` field dimensions through
an `Operator` function return. B07 was migrated successfully without
flattening its namespace/struct/function teaching surface. B16, whose
Hamiltonian is local to the source file, was also migrated successfully with
the same explicit propagator and tuple-carrier path. Its effect-marking and
terminal measurement behavior remain intact.

The nine migrated examples (A03, A05, A06, A10, A11, B07, B08, B16, and
`quantum_matter_discovery`), their dedicated regressions, the LISS-0437
explicit-surface suite, and the full 161-case gate pass.
The first S01 Showcase slice, `main_morning_collect.sqx`, is now also
migrated. Its `phase`, Host-computed Energy scale, Inspect peek, and terminal
trace-out remain unchanged; the dedicated LISS-0346 regression passes. The
four-zone lattice file is also migrated with separate propagators for the
four-state Hamiltonian and the two-state basis Hamiltonian; its LISS-0345
regression passes. The day-two recovery file is also migrated; its former
Suzuki order is retained as showcase metadata while the source now exposes
the exact propagator. Its LISS-0347 regression passes. The four-stage
disaster-response file is also migrated; its dedicated LISS-0348 regression
passes. The remaining source corpus is one S01 file plus B04. B04 remains
intentionally in the legacy bare-Pauli teaching family because its duration
is a rotation angle, not a real-time propagator input. The S01 files are kept
as a separate showcase batch: one has convergence-bounded `until`, while the
other four require preserving the showcase's multi-stage protocol semantics.

The remaining S01 file, `main_fuel_search.sqx`, is not migration-ready. Its
`until converged(fuel) max 64` is a bounded repeated evolution contract, not
a single propagator application. The current legacy Hamiltonian spelling is
already rejected by the migration diagnostic, while `Evolve() { U_t * fuel }`
has no accepted `until` form. Do not replace it with one `U_t` application;
that would erase the convergence semantics. A separate acceptance
specification is required for explicit bounded repetition and its target
capability boundary.

A03 H₂ required and now includes a Red/Green rule for identity-operator sums:
adding an explicitly dimensioned identity offset to a dimensionless
QubitOperator preserves the Hamiltonian's Energy dimension. Its dedicated
real-unit regression and Jordan–Wigner literature cross-check pass. A06 also
verified that function-local Operator dimensions survive multi-file import
linking. A11 then verified the same dimension and tuple-carrier behavior for
a three-sensor state in a larger imported module graph; its full-module and
structural regressions pass.

Formal `Limit` remains a separate target-realization design because replacing
it with Suzuki would change the written finite-product semantics.
