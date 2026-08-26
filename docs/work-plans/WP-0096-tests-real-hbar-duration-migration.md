# WP-0096: migrate `tests/` fixtures off the pre-ADR-0195 dimensionless `evolve` duration convention

| Field | Value |
|---|---|
| Status | **complete — all 8 work units merged (2026-08-08). `pytest tests/ -q` returns to a fully green suite (1308 passed, 0 failed) for the first time since ADR 0195's real-ℏ migration began (2026-08-05). Every EVOLVE_UNRESOLVED_UNIT_ERROR failure tracked in open-work-register.md since LISS-0330 is now closed.** |
| Parent ADR | [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md) (Accepted 2026-08-05) — this WP applies an already-accepted decision to a backlog WP-0095 deliberately left open |
| Scope | Every `tests/*.py` fixture still using a bare/dimensionless `evolve ... for <expr>` duration, currently rejected by ADR 0195's fail-closed unit check (`EVOLVE_UNRESOLVED_UNIT_ERROR`) |
| Not in scope | Any change to Kernel source (`compiler/staqex/`) — this WP is test-fixture-only; `examples/` (already fully migrated by WP-0095); any new architecture decision (none needed — see below) |

## Goal

`main` currently carries **52 known, tracked, ADR-0195-approved test
failures** (confirmed unchanged since WP-0095 closed, most recently
re-verified 2026-08-08 across LISS-0357/0358) — every one traced to
`EVOLVE_UNRESOLVED_UNIT_ERROR` on a bare/dimensionless `evolve ... for
<expr>` duration written before ADR 0195. Unlike WP-0095 (which
migrated shipped, physics-narrative `examples/` and required literature
research or an explicit "arbitrary unit" honesty judgment per example),
these are **mechanical Kernel-behavior tests** (binder lowering, JW
mapping structure, operator-factory dispatch, Suzuki policy, acting-
space typing, etc.) — the duration/Hamiltonian magnitude is incidental
to what each test actually verifies, not a physics claim.

This WP's goal is to migrate every one of these fixtures to a real,
ADR-0195-compliant `Energy`/`Time` unit **without changing any test's
existing numeric assertions or observable behavior** — i.e., a pure
unit-compliance migration, not a re-derivation of each test's physics.

## The conversion identity (no new ADR needed)

Confirmed live (2026-08-08, this WP's own investigation) that the
`evolve` step depends only on the product `H·t/ℏ`. Two distinct cases
exist in the current failing set:

1. **Legacy single-Pauli-letter `evolve ψ under X for t`**
   (`runtime/quantum_ops.py::pauli_u`) uses the *canonical-seconds*
   magnitude directly as the rotation angle — it does **not**
   reference `ℏ` at all. The suffix must specifically be **`.s`**
   (seconds is the canonical `Time` unit, scale factor 1), **not**
   `.fs`/`.ps`/`.ns` — those canonicalize to a much smaller magnitude
   (`.fs` = ×1e-15) before reaching `pauli_u`, silently producing a
   near-zero rotation instead of the intended angle. **Correction
   (2026-08-08, caught during this WP's own work unit 1 before any
   test was edited)**: an earlier draft of this document said `.s`/`.fs`
   were interchangeable for this case — live-verified they are **not**:
   `evolve psi under X for 1.5707963267948966.s` reproduces the
   original `for pi / 2.0` measurement (`1`) exactly; the same value
   with `.fs` instead produces a different measurement (`0`), confirming
   the canonicalization-factor mistake. With `.s`, the numeral is
   otherwise unchanged and reproduces the identical rotation angle.

2. **General composed Hamiltonian `Operator H = ...` (sums, `hop()`,
   JW-mapped operators, factory-returned operators)** goes through
   `expm_ih`/the sparse-Pauli evolution path, which real-ℏ ADR 0195
   changed to `U = exp(-iHt/ℏ)`. Appending a unit suffix alone
   overflows the sparse-evolution step budget (confirmed live:
   `Z[0]*Z[1]` + `0.1.s` → `|H·t/ℏ| ~= 2**110`, rejected). However,
   **scaling the whole Hamiltonian by a fixed constant `k = ℏ / 1fs ≈
   1.0545718e-19`, while keeping the duration's existing numeral
   unchanged and appending `.fs`, exactly reproduces the original
   `H·t` product** (since real-ℏ evolution then computes `(k·H_old) ·
   (t_old · 1fs) / ℏ = H_old · t_old · (ℏ/1fs) · (1fs) / ℏ = H_old ·
   t_old`, the pre-ADR-0195 value). Confirmed live: `Operator H =
   1.0545718e-19 * (Z[0] * Z[1])` with `evolve ... for 0.1.fs`
   succeeds and reproduces the same measurement as the pre-migration
   intent.

Both cases are **behavior-preserving by construction** — no per-test
physics judgment is required, unlike WP-0095's `examples/` migration.
This is why this WP is scoped as a mechanical migration and does not
require a new ADR: it applies ADR 0195 exactly as already decided,
using an algebraic identity to guarantee no observable change.

The one place per-file judgment remains: the Operator-DSL requires
explicit parentheses when a scalar multiplies a tensor product
(`TENSOR_GROUPING_ERROR`), so each general-Hamiltonian expression needs
correct `k * (...)` grouping — a mechanical but not fully
find-and-replace edit, hence still worth per-file review at Red/Green
time rather than a blind sweep.

## Granularity rationale

52 failing test functions span 26 files. Unlike WP-0095 (one shipped,
narratively-distinct example per work unit, each needing its own
literature/honesty judgment), these are internal Kernel-behavior tests
with no such distinction — grouping by *file count* alone would produce
either 26 near-trivial single-file Issues (high PR/review overhead for
a mechanical change) or one enormous Issue (hard to review, hard to
bisect if something regresses). This WP instead groups by **shared
Hamiltonian-construction pattern**, since that is what determines the
exact conversion mechanics each work unit's Red/Green phase must get
right — a reviewer looking at one work unit's diff sees one consistent
transformation applied uniformly, not a grab-bag.

Work units deliberately left as multi-file groups (not split further)
where the files already share a `LISS-*`-prefixed name lineage (e.g.
the four binder/sum-lowering files), since those already represent a
single coherent feature area in the codebase's own naming.

## Execution order

No cross-unit dependencies exist (each work unit touches disjoint test
files and does not depend on another unit's changes) — order below is
by ascending risk/complexity, not a hard requirement, so a stall on one
unit does not block the others.

### 1 — Legacy single-Pauli-letter evolve (trivial, zero-numeral-change) — **complete**

Status: **complete**, PR [#437](https://github.com/nn0cl/staqex/pull/437)
merged (`9eacfc8`), [LISS-0359](../issues/LISS-0359-legacy-pauli-evolve-duration-migration.md).
Caught and corrected an error in this document's own case-1 claim
before any test was edited (see LISS-0359's design decision): the
suffix must be `.s` specifically, not `.fs`. `pytest tests/ -q` → 1260
passed, 48 failed (exactly -4 vs. the 52-failure baseline, confirmed
via full failure-list diff); `spec_verification` unchanged (161/161).


Files: `test_evolve_until_runtime_red.py` (3 cases),
`test_qudit_d3_sv_slice_b_red.py` (1 case).
Conversion: append **`.s`** (not `.fs`) unchanged to each existing bare
numeral. The `pi / 2.0`/other non-literal-expression cases cannot take
a unit suffix directly (the suffix grammar only attaches to a literal)
— pre-compute the equivalent decimal value (e.g. `math.pi / 2` in
Python, which is bit-for-bit `PRELUDE_CONSTANTS["pi"]`) and write it as
a `<value>.s` literal. Lowest risk: confirmed behavior-preserving by
construction (case 1 above), no Hamiltonian edits needed at all.

### 2 — Binder / sum-lowering execution wiring — **complete**

Status: **complete**, PR [#439](https://github.com/nn0cl/staqex/pull/439)
merged (`80c0353`), [LISS-0360](../issues/LISS-0360-binder-sum-lowering-duration-migration.md).
Corrected this document's own case count during Red (14 cases, not
13). Found and fixed one genuine, previously-undiscovered Kernel bug
during Green: `backend/qasm/trotter.py::_eval_float` had a local,
independently-hardcoded Time-unit-scale table that predated ADR 0195's
`ps`/`fs` additions and had gone stale — confirmed with the Adjudicator
before including the fix in this work unit. Also found that wrapping a
binder expression's *whole* top-level RHS in the `K` scale (as this
document originally proposed) breaks `qpu_ir["binder_lowering"]`
provenance tracking for two files; corrected to inject `K` inside each
binder body instead (mathematically identical, since scalar
multiplication distributes over the sum). `pytest tests/ -q` → 1274
passed, 34 failed (exactly -14 vs. the 48-failure baseline, confirmed
via full failure-list diff); `spec_verification` unchanged (161/161).

Files: `test_binder_composition_and_honest_deferral_red.py`,
`test_binder_lowering_execution_wiring_red.py`,
`test_liss0055_execution_acceptance.py`,
`test_liss_0224_method_returned_binder_evolve_red.py`,
`test_liss_0226_nested_empty_sum_identity_red.py`,
`test_liss_0227_operator_pqn_shadow_red.py` (14 cases total).
Conversion: case 2 above (scale Hamiltonian by `k`, append `.fs`
unchanged to duration numeral). All use `Z[i]*Z[j]`-style composed
sums via the Operator-DSL `sum(...)`/binder machinery.

### 3 — Periodic boundary / acting-space typing — **complete**

Status: **complete**, PR [#441](https://github.com/nn0cl/staqex/pull/441)
merged (`8e44252`), [LISS-0361](../issues/LISS-0361-periodic-boundary-acting-space-duration-migration.md).
No surprises this time — case 2's pattern (established in work unit 2)
applied cleanly. `pytest tests/ -q` → 1278 passed, 30 failed (exactly
-4 vs. the 34-failure baseline, confirmed via full failure-list diff);
`spec_verification` unchanged (161/161).

Files: `test_liss0057_periodic_boundary_red.py`,
`test_liss0058_acting_space_typing_red.py` (4 cases total).
Conversion: case 2. Grouped together as both concern how `evolve`
infers/retains the acting Hilbert-space shape, a related structural
concern.

### 4 — Operator factory / method-return / struct-field coefficients — **complete**

Status: **complete**, PR [#443](https://github.com/nn0cl/staqex/pull/443)
merged (`bead530`), [LISS-0362](../issues/LISS-0362-operator-factory-duration-migration.md).
Corrected this document's own case count during Red (19 cases, not
18). Kept as one Issue rather than splitting, per Adjudicator
direction, after reading all 10 files and confirming the conversion
pattern was fully uniform (no unresolved surprises this time — every
edit, including one Time-typed-declaration nuance for a method-returned
duration, was live-verified during design intake before Red). `pytest
tests/ -q` → 1297 passed, 11 failed (exactly -19 vs. the 30-failure
baseline, confirmed via full failure-list diff); `spec_verification`
unchanged (161/161).

Files: `test_liss0051_operator_factory_runtime_red.py`,
`test_liss0107_examples_linker_runtime_red.py`,
`test_operator_method_call_return_red.py`,
`test_sparse_pauli_operator_return_red.py`,
`test_liss_0297_operator_freefn_struct_coeffs_red.py`,
`test_liss_0305_classical_multi_bind_red.py`,
`test_liss_0306_nested_opattr_and_effects_red.py`,
`test_liss_0309_multi_ket_multi_bind_red.py`,
`test_classical_float_operator_evolve_binding_red.py`,
`test_liss_0121_classical_coefficient_vs_linear_red.py` (19 cases
total — the largest work unit; kept as one Issue, LISS-0362, per
Adjudicator direction after full-file review found no unresolved
surprises).
Conversion: case 2, plus care where the Hamiltonian's scalar
coefficient is itself a classical variable/struct-field/method-return
(not a bare literal) — the `k` scale multiplies that existing
expression, not a hardcoded literal.

### 5 — Suzuki/Trotter explicit policy — **complete**

Status: **complete**, PR [#445](https://github.com/nn0cl/staqex/pull/445)
merged (`77c177f`), [LISS-0363](../issues/LISS-0363-suzuki-trotter-duration-migration.md).
Case 2's pattern applied cleanly, including a larger duration numeral
(100.0) verified not to overflow the sparse-evolution step-budget
check. `pytest tests/ -q` → 1300 passed, 8 failed (exactly -3 vs. the
11-failure baseline, confirmed via full failure-list diff);
`spec_verification` unchanged (161/161).

Files: `test_explicit_trotter_steps_red.py`,
`test_liss_0270_experiment_surface_profile_red.py`,
`test_liss_0280_0288_sugar_red.py` (3 cases total).
Conversion: case 2. Explicit `using Suzuki(order=..., steps=...)`
clauses are untouched — only the Hamiltonian/duration values change.

### 6 — Jordan-Wigner mapping — **complete**

Status: **complete**, PR [#447](https://github.com/nn0cl/staqex/pull/447)
merged (`800584b`), [LISS-0364](../issues/LISS-0364-jordan-wigner-duration-migration.md).
Confirmed this document's own advance concern (both sides of each
equivalence check need the identical `k`); also found the
`FermionOperator` side has no top-level-paren-wrap form that parses
(`K * (create[0] * annihilate[0])` fails, as does scaling the
already-mapped `QubitOperator`) — resolved with a per-term `K *`
prefix instead, live-verified end-to-end including the marginal-
equality comparisons before Red. `pytest tests/ -q` → 1304 passed, 4
failed (exactly -4 vs. the 8-failure baseline, confirmed via full
failure-list diff); `spec_verification` unchanged (161/161).

Files: `test_jordan_wigner_mapping_red.py` (4 cases).
Conversion: case 2, for both the JW-`mapped` operator and its
hand-written-Pauli comparison counterpart in each test (both sides of
each equivalence check must use the identical `k`/duration so the
comparison itself remains meaningful).

### 7 — Continuous/grid Hamiltonian bridge — **complete**

Status: **complete**, PR [#449](https://github.com/nn0cl/staqex/pull/449)
merged (`bbb5a18`), [LISS-0365](../issues/LISS-0365-continuous-grid-duration-migration.md).
Resolved this document's own flagged open question: the grid
Hamiltonian path uses the same `expm_ih` primitive as the sparse-Pauli
path (WP-0095 work unit 1 updated both together), so the identical `k`
constant applies — confirmed live via Born-rule norm preservation and
bridge-vs-direct marginal equality before Red. `pytest tests/ -q` →
1306 passed, 2 failed (exactly -2 vs. the 4-failure baseline,
confirmed via full failure-list diff); `spec_verification` unchanged
(161/161).

Files: `test_continuous_lowering_red.py` (2 cases).
Conversion: case 2, applied to the grid/continuous-coordinate
Hamiltonian bridge path specifically — confirm this path's magnitude
budget behaves the same as the sparse-Pauli path before assuming
identical `k`.

### 8 — Remaining misc — **complete (final work unit)**

Status: **complete**, PR [#451](https://github.com/nn0cl/staqex/pull/451)
merged (`31a9bd5`), [LISS-0366](../issues/LISS-0366-misc-duration-migration.md).
`pytest tests/ -q` → **1308 passed, 0 failed** — `main` is fully green
for the first time since the ADR 0195 real-ℏ migration began
(2026-08-05); `spec_verification` unchanged (161/161). **This closes
WP-0096 in its entirety.**

Files: `test_operator_pauli_atom_call_parse_red.py`,
`test_when_ket_prepare_arms_red.py` (2 cases).
Conversion: case 2.

## Verification plan (applies to every work unit)

Each work unit follows the same AT-TDD discipline as every other Issue
this session: Red confirms the existing failures still fail for the
documented `EVOLVE_UNRESOLVED_UNIT_ERROR` reason (already true on
`main`, so Red is "these tests already fail, for this reason" rather
than a new test being added), Green applies the conversion, and the
regression sweep must show the fixed tests moving from FAIL to PASS
**with no change to any other test's outcome** — confirmed via full
failure-list diff (not just count), matching this session's established
rigor. `spec_verification` expected unchanged throughout (161/161 — none
of these 52 tests are `spec_verification` suites).

## Draft batch record (not yet approved)

This WP proposes following WP-0095's own actually-used operating
pattern: **per-work-unit Plan/Completion approval**, not a single
upfront batch grant. No `execution-batch-*.json` record is proposed:
each of the 8 work units above becomes its own LISS Issue, drafted and
Plan-approved individually immediately before its own Phase 1 Red,
exactly as WP-0095's 16 work units were run. This avoids granting a
broad, hard-to-revoke batch authorization for 52 individually-small
edits where the main risk (getting the `k`/parenthesization conversion
wrong for one file) is best caught by the existing per-Issue regression
gate, not a batch-wide one.

## Open questions

- ~~Work unit 4 (18 cases) may be too large for a single reviewable
  PR~~ — resolved: 19 cases, kept as one Issue (LISS-0362) after full
  review found the pattern fully uniform.
- ~~Work unit 7's grid/continuous path was not live-verified against
  the `k`-scaling identity~~ — resolved: confirmed live (LISS-0365) the
  grid path shares `expm_ih` with the sparse-Pauli path, so the
  identical constant applies.
