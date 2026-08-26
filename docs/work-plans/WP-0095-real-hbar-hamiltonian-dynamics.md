# WP-0095: real ℏ and dimensioned Hamiltonian dynamics

| Field | Value |
|---|---|
| Status | **complete — all 16 work units merged. Every ADR 0195-affected `.sqx` example (`examples/basics`, `examples/applied`, `examples/showcase/quantum_matter_discovery`, `examples/showcase/S01_quantum_disaster_response`) is confirmed migrated to real ℏ / real Energy-Time units. `main` no longer carries any ADR-approved real-unit regression** |
| Parent ADR | [ADR 0195](../architecture/adr/0195-real-hbar-hamiltonian-dynamics.md) (Accepted 2026-08-05) |
| Scope | Replace `evolve`'s hardcoded natural-units (ℏ = 1) time evolution with real, dimensioned SI-unit dynamics; migrate every example that uses `evolve` |
| Not in scope | Live QPU/pulse-level hardware timing (ADR 0193's separate concern); the unrelated `Operator G = adjoint(H)` runtime bug (tracked separately, see "Related, not blocking" below) |

## Goal

Make `evolve ψ under H for t` physically real: a physicist supplies a
Hamiltonian in real energy units (`eV`, `J`) and a duration in real time
units (`s`, `ps`, …) and gets the physically correct phase evolution,
using ℏ's real SI value — not a natural-units convention silently baked
into the simulator. Per ADR 0195, this is a real, one-time migration: the
old `U = exp(-iHt)` formula is deleted outright, not kept behind a flag.

## Decisions to preserve (from ADR 0195)

- ℏ = `1.054571817e-34` J·s (CODATA 2018 exact), one source of truth
  shared by `evolve`'s formula and the `hbar` prelude constant.
- No permanent natural-units dual-mode. An unmigrated program must fail
  closed (explicit diagnostic), never silently keep running under the old
  formula.
- Real energy/time values for each example are sourced from public
  references (NIST/CODATA, or the system's known literature values), not
  invented or auto-rescaled from the old numbers.
- Builds on the already-shipped `Energy`/`Time` Type-First dimensions
  (`compiler/staqex/dimensions.py`) — no new dimension system.

## Work units

### 1 — Kernel primitive (this Issue: LISS-0330) — **complete**

Status: **complete**, PR #376 merged (`29f2ee8`).
`HBAR_SI` lives in `stdlib/prelude.py`, not `dimensions.py` as first
sketched (that module is compile-time-only; refinement found during
Green). Two unanticipated numerical-robustness bugs in `expm_ih`/
`expm_ih_apply` were found and fixed within this Issue (both exposed only
by this Issue's own formula change). Confirmed regression, as intended:
`pytest tests/ -q` → 66 failed / 1188 passed; `spec_verification` →
132/145 (91.03%), Gate: FAIL. `main` now carries this expected,
ADR-approved regression until work unit 2+ migrates each affected
example/test. See LISS-0330 for full evidence.

1. Add `HBAR_SI` to `compiler/staqex/dimensions.py` as the single source
   of truth.
2. Change `runtime/matrix.py::expm_ih` (and the sparse-Pauli equivalent,
   `runtime/sparse_pauli.py::expm_ih_apply`) from `U = exp(-iHt)` to
   `U = exp(-iHt/hbar)`.
3. Add a fail-closed diagnostic when `H`/`t` cannot be resolved to real
   `Energy`/`Time` dimensions by the time they reach the primitive.
4. Add `hbar` to `compiler/staqex/stdlib/prelude.py`'s `PRELUDE_CONSTANTS`,
   referencing the same `HBAR_SI` value.
5. Add a hand-verified reference test case (a two-level system with a
   known real energy gap and a known real Rabi period, computed
   independently, not by running the Kernel and trusting its own output).
6. Add `ns`/`fs` time units to `dimensions.py` if the reference case or
   early migration needs them (gap confirmed during ADR 0195's design
   check: only `s`/`ms`/`us`/`ps` exist today).

No example migration in this work unit — every existing example continues
to use the old formula until this Issue lands, at which point they all
start failing closed (by design, per the "no silent old-formula survival"
decision) until migrated.

**Sequencing implication:** because work unit 1 makes every unmigrated
`evolve` fail closed, work unit 2 (first example migration) should follow
immediately — the gap between work units 1 and 2 is a period where no
`evolve`-using example runs, tracked openly rather than hidden.

### 2 — First reference migration: `A03_h2_vqe` — **complete**

Status: **complete**, PR [#381](https://github.com/nn0cl/staqex/pull/381)
merged (`510e860`),
[LISS-0332](../issues/LISS-0332-a03-h2-real-unit-migration.md). Migrated
`examples/applied/A03_h2_vqe/main_h2_vqe.sqx` to real energy/time values
derived from H₂ literature data — full derivation and provenance caveats:
[docs/research/2026-08-05-h2-two-orbital-jordan-wigner-cross-validation.md](../research/2026-08-05-h2-two-orbital-jordan-wigner-cross-validation.md).
Found and fixed an unrelated, previously-undiscovered gap during Green:
`second_quantization.py`'s Jordan-Wigner mapping never handled a scalar
coefficient on a fermionic term (only unweighted products) — no example
had ever attached one before. Confirmed: A03 no longer appears in
`test_applied_catalog_health_red.py`'s failure list; only A05/A06/A10/A11
remain (work unit 3+).

### 3 — `A05_qaoa_portfolio` — **complete**

Status: **complete**, PR [#383](https://github.com/nn0cl/staqex/pull/383)
merged (`8d36278`),
[LISS-0333](../issues/LISS-0333-a05-qaoa-arbitrary-unit-migration.md).
Unlike `A03_h2_vqe`, `A05` models an abstract QUBO portfolio-selection
cost function, not a real physical system — a Hard Stop design question
(no literature-traceable physical energy exists for QAOA cost weights)
was raised and resolved with the Adjudicator before Plan approval: give
`H_cost`/`H_mixer` real `Energy`/`Time` dimensions (`eV`/`fs`, satisfying
the Kernel's fail-closed requirement) but honestly document the
magnitudes as arbitrary problem-defined cost units, not physical
constants — see LISS-0333's "Design decision carried into this Issue"
section for the full record. Found and fixed live during design intake
(not a shipped-code bug, a design-intake finding): the mixer term's
originally-implicit coefficient `1` overflows the `hbar`-divided phase
magnitude and must also be given an explicit `Energy` value. Confirmed:
A05 no longer appears in `test_applied_catalog_health_red.py`'s failure
list; only A06/A10/A11 remain (work unit 4+).

### 4 — `A06_topological_edge_memory` — **complete**

Status: **complete**, PR [#385](https://github.com/nn0cl/staqex/pull/385)
merged (`780707a`),
[LISS-0334](../issues/LISS-0334-a06-ssh-real-unit-migration.md). Unlike
A05, `A06` models a real physical system class (the SSH tight-binding
chain, Su-Schrieffer-Heeger 1979) — its hopping amplitudes are a genuine
`Energy` quantity, unlike A05's abstract QUBO weights, but the specific
values are not traced to a cited measurement (the README already
describes the example as "pedagogical"). Resolved with the Adjudicator
as a third honesty category, distinct from both A03 (literature-traced)
and A05 (arbitrary units): real `eV`-scale magnitudes, ratio preserved
from the original code, documented as physically plausible but not a
reproduction of a specific paper's numeric SSH parameters. Bonus,
unanticipated fix during Green: three other tests exercising A06's
legacy "example10" source also flipped from failing to passing (same
root cause). Confirmed: A06 no longer appears in
`test_applied_catalog_health_red.py`'s failure list; only A10/A11
remain (work unit 5+).

### 5 — `A10_mission_observatory` — **complete**

Status: **complete**, PR [#387](https://github.com/nn0cl/staqex/pull/387)
merged (`556d459`),
[LISS-0335](../issues/LISS-0335-a10-mission-observatory-real-unit-migration.md).
Same SSH tight-binding pattern and honesty category as A06; reused
without re-litigating. New finding during design intake: the fail-closed
`evolve` duration check only recognizes a bare `Var`, not a dimensioned
struct-field `Attr` expression (`config.duration`), even though the
field genuinely carries a resolvable unit via ADR 0174's field-unit
tracking — worked around with a local `Time` variable, not fixed (noted
in "Related, not blocking" below). Bonus, unanticipated fix during
Green: three more tests exercising A10's legacy multi-file/capstone
source also flipped from failing to passing. Confirmed: A10 no longer
appears in `test_applied_catalog_health_red.py`'s failure list; only A11
remains (work unit 6+).

### Urgent interleaved fix — evolve real-unit canonicalization bugs — **complete**

Status: **complete**, PR [#389](https://github.com/nn0cl/staqex/pull/389)
merged (`bbd7c06`),
[LISS-0336](../issues/LISS-0336-evolve-real-unit-canonicalization-bugs.md).
Found live during work unit 6 (A11 rewrite) design intake, not itself an
example migration: two independent Kernel bugs in ADR 0195's `evolve`
glue code — `sparse_pauli.py::_coalesce`'s absolute `1e-15` epsilon
silently zeroed real Joule-scale coefficients (confirmed to have broken
already-merged A05's `H_mixer`/`H_cost` entirely); `evolve`'s duration
was never canonicalized from its declared Time unit (`fs`/`ps`/`ns`) to
seconds (affected all four merged examples, A03/A05/A06/A10). Both
fixed; A05/A06/A10 re-verified to now show real, non-trivial evolution.
A03 re-verification surfaced a **third, separate, pre-existing bug**
(`op_n_qubits` undercounts qubits for Jordan-Wigner-mapped Operators,
silently dropping a qubit) — deferred to its own new Issue, not fixed
here. Work unit 6 (A11) resumes now that this fix has landed.

### 6 — `A11_noether_forge` — **complete**

Status: **complete**, PR [#392](https://github.com/nn0cl/staqex/pull/392)
merged (`42ca5ed`),
[LISS-0338](../issues/LISS-0338-a11-structural-monitoring-magnetometer.md).
Rethemed all 14 module files plus `main_static.sqx`
from the rejected/deferred Noether Forge quantum-matter-discovery theme
(LISS-0120, "optional salvage only — not authoritative") to a
structural-monitoring quantum magnetometer, per the Adjudicator's
explicit direction: a 3-sensor NV-center-like array detects a
stress/defect signature via a real D≈2.87GHz zero-field-splitting-based
rotating-frame model (Doherty et al. 2013), all 14 modules genuinely
wired (no unwired scaffolding remains). Found and fixed a real,
previously-undiscovered Kernel bug during Green: struct constructor
calls from within an imported function's own body failed at runtime
(`evaluator.py::_bind_call` never checked `self.structs`/`self.classes`
for a bare-`Var` callee). Found, documented, and deliberately not
fixed (design avoided instead): three further classical-language gaps —
no execution path for free functions *returning* a struct type; `&&`
unsupported in expressions; Float relational comparisons between two
classical operands mistyped as `Classical<Float>` instead of
`Classical<Bool>`; `abs()` has no classical-scalar implementation — see
LISS-0338's "Related, not blocking". Confirmed: A11 no longer appears in
`test_applied_catalog_health_red.py`'s failure list (that test's
failure list is now empty).

### 7 — `B04_evolve_not_loops` — **complete**

Status: **complete**, PR [#394](https://github.com/nn0cl/staqex/pull/394)
merged (`084feb4`),
[LISS-0339](../issues/LISS-0339-b04-evolve-not-loops-real-unit-migration.md).
Reused the `sv17` fix pattern from LISS-0337: the
legacy bare-Pauli-letter evolve form (`evolve psi under Z for t`) routes
through `quantum_ops.py::pauli_u`, which is not ℏ-divided — its duration
is a rotation angle, not physical time. Declared the existing `pi / 2.0`
value as `Time dur = 1.5707963267948966.s` (canonical seconds, passes
through unchanged) with a comment distinguishing this from real-time
physics. No new findings.

### 8 — `B07_structure_visibility` — **complete**

Status: **complete**, PR [#396](https://github.com/nn0cl/staqex/pull/396)
merged (`f385df8`),
[LISS-0340](../issues/LISS-0340-b07-structure-visibility-real-unit-migration.md).
`IsingParams.J`/`.h` (bare `Float`) became real
`Energy` (ratio preserved), routed through the qubit-Pauli sparse path
(the same path LISS-0336 fixed a coalescing-epsilon bug for — genuinely
needed real, appropriately-scaled values, unlike B04's non-ℏ legacy
path). The evolve duration (`scale * 0.25`, struct-field-derived) could
no longer directly become `Time`-typed (unit suffixes only attach to
literals, not expressions) — replaced with an independent `Time`
literal; `Float scale = seg.length` kept as its own standalone
struct-field-read demonstration (this example's actual teaching point:
`namespace`/`enum`/`struct`/`pub` visibility), no longer wired to the
duration.

### 9 — `B08_operators_hamiltonians` — **complete**

Status: **complete**, PR [#398](https://github.com/nn0cl/staqex/pull/398)
merged (`45fe41d`),
[LISS-0341](../issues/LISS-0341-b08-operators-hamiltonians-real-unit-migration.md).
`J`/`h` became explicit `Energy`-typed (`H_chain`
stays inferred, confirmed ADR 0180 ty-fill still applies); duration
became explicit `Time`. **Found and fixed a real Kernel bug**:
`backend/qasm/trotter.py`'s Suzuki gate-angle computation was never
updated for ADR 0195's real-ℏ formula (`theta = coeff * delta_t`,
missing `/hbar`), and had its own absolute-coefficient epsilon
predating LISS-0336's `sparse_pauli.py` fix — together these silently
collapsed B08's QASM3 Trotter emission into an "idle" no-op circuit
(`test_qasm3_codegen.py::test_trotter_ising_evolve_qasm` caught this).
Fixed by dividing by real ℏ and removing the redundant pre-division
filter. Confirmed this bug is not B08-specific — it affects any future
QASM3-emitted example with a real-`Time`-typed evolve duration.
`spec_verification` reached **161/161 (100%, Gate: PASS)** — but this
is only every case that suite's own 161 cases exercise, **not** a
complete repository audit: `examples/basics/B16_effect_marking` is
confirmed still unmigrated (`EVOLVE_UNRESOLVED_UNIT_ERROR`) and simply
isn't referenced by any `spec_verification` suite, so it was never
counted. See work unit 10 below.

### 10 — `B16_effect_marking` — **complete**

Status: **complete**, PR [#400](https://github.com/nn0cl/staqex/pull/400)
merged (`adf63b4`),
[LISS-0342](../issues/LISS-0342-b16-effect-marking-real-unit-migration.md).
Found unmigrated during LISS-0341's honest
correction (not exercised by any `spec_verification` suite, hence
absent from the 161/161 figure). Identical fix pattern to B08
(LISS-0341): `J`/`h` become explicit `Energy`-typed, `H` stays inferred,
duration becomes explicit `Time`. Bonus: a pre-existing test
(`test_liss_0306_nested_opattr_and_effects_red.py::test_b16_effect_marking_sample`)
also flipped from failing to passing. No new findings.

### 11 — `quantum_matter_discovery` — **complete**

Status: **complete**, PR
[#402](https://github.com/nn0cl/staqex/pull/402) merged (`fbf0f58`),
[LISS-0343](../issues/LISS-0343-typecheck-classical-payload-and-quantum-matter-discovery-migration.md).
Chosen over the 5 locked S01 files (Adjudicator selection, 2026-08-06).
Same qubit-Pauli sparse-path pattern as B07/B08/B16: `IsingCouplings.J`/
`.h` (`Float` → `Energy`) and `QuenchSchedule.duration` (`Float` →
`Time`), with the struct-field type changes propagated through
`field_scale`/`named_coeff_sum`/`schedule_duration`'s return types
(multi-file showcase slice, unlike the single-file B04/B07/B08/B16
migrations). **Found and fixed a fifth instance of the same systemic
category**: `typecheck.py::_infer_binop`'s Classical `+`/`-` branch
hardcoded its result payload to `"Float"` regardless of operand payload
(dimension itself was tracked correctly), so `Energy + Energy`
type-checked as `Classical<Float>` with an `Energy` dimension — a
function declared `-> Energy` returning such a sum failed
`RETURN_TYPE_MISMATCH`. Fixed with a payload check that preserves a
non-bare-numeric operand's payload and otherwise falls back to the
existing `Int + Int -> Float` legacy convention (confirmed this
convention is relied upon by an existing passing test — using the
shared `_promote()` helper as-is would have broken it, caught during
this Issue's own verification before it shipped). **Bonus fix**: the
locked S01 disaster-response spine
(`test_showcase_s1_thin_slice_red.py::test_s1_spine_compiles_and_runs`)
independently hit the same bug and now passes — S01's own real-unit
migration (work unit 12+) is still not done.

### 12 — S01 real-unit migration survey + `main_fuel_search` — **complete**

Status: **complete**, PR
[#404](https://github.com/nn0cl/staqex/pull/404) merged (`2c62100`),
[LISS-0344](../issues/LISS-0344-s01-fuel-search-real-unit-migration.md).
Before any of the 5 locked S01 files, confirmed the lock-boundary check
WP-0095 itself flagged: these migrations change only a value's internal
unit representation (retype/rescale), not the locked mission's scope,
story, or coverage — no lock-boundary conflict for any of the 5.

Live investigation of all 5 files found this program is genuinely more
involved than any prior WP-0095 example: 3 of the 5 (`main_lattice_four`,
`main_morning_collect`, and 3 of `main_disaster_response`'s 4
Hamiltonians) reference Hamiltonians with an *implicit* coefficient of
exactly `1` (built via `sum(...)`/`product(...)` combinators, or a bare
`Operator H = Z`, with no scalar multiplier). Evolving these under real
ℏ with any human-scale duration produces a numerically meaningless
rotation angle — confirmed live: `RUNTIME_ERROR: evolve magnitude
|H*t/hbar| ~= 2**61 exceeds the sparse evolution step budget (2**16) --
H and/or t are not physically plausible real-unit values`. Simply
retyping the duration (every prior WP-0095 fix) is not sufficient here.

**Adopted design** (Adjudicator-confirmed): a single new shared
function, `pub fn ops_energy_scale() -> Energy { return 1.0.eV to J }`,
in a new file
`examples/showcase/S01_quantum_disaster_response/physics/ops_energy_scale.sqx`,
with a disclosure comment adapted from A05_qaoa_portfolio's own honesty
wording (arbitrary problem-defined units satisfying the Kernel's
fail-closed evolve requirement, not physical energies or
literature-traced constants). Each affected `main_*.sqx` binds `Energy
scale = ops_energy_scale()` once and wraps every `Operator H =
<factory call>` as `Operator H = scale * <factory call>` at the call
site. Confirmed live this requires **no changes** to the existing
`physics/constraint_h.sqx` or `grid/block_costs.sqx` factory functions'
internals — `ConstraintCoeffs.congestion`/`.fairness` stay `Float`,
preserving `main_disaster_response.sqx`'s existing classical
causal-map chain (its own header comment calls this out as a design
property) untouched. Verified: `1eV × 1fs / ℏ ≈ 1.5 rad`, producing a
real, non-degenerate measurement distribution, not the earlier
`RUNTIME_ERROR` or a trivial near-identity rotation. Since no shared
file's internals change (only a new, purely-additive file), the 5 S01
files can proceed as independent Issues, in increasing-complexity
order: `main_fuel_search` (this Issue — no energy-scale question,
bare-Pauli-letter fast path, identical to LISS-0339/B04) →
`main_lattice_four` (introduces `ops_energy_scale.sqx`) →
`main_morning_collect` → `main_day2_recovery` →
`main_disaster_response` (flagship "tonight spine", most complex: 4
Hamiltonians, 4 durations — done last, once the pattern is proven four
times over).

### 13 — `main_lattice_four` — **complete**

Status: **complete**, PR
[#406](https://github.com/nn0cl/staqex/pull/406) merged (`1c1b2c6`),
[LISS-0345](../issues/LISS-0345-s01-lattice-four-real-unit-migration.md).
First file to add `physics/ops_energy_scale.sqx` (per work unit 12's
adopted design: `pub fn ops_energy_scale() -> Energy { return 1.0.eV to
J }`, A05-style arbitrary-unit honesty category). Wraps both of the
file's coefficient-1 Hamiltonians (`damage_hamiltonian_four()`,
`basis_zone_sum()`) with `scale * <factory result>`. No changes to
`grid/block_costs.sqx` itself. **Found and corrected two implementation
wrinkles during Green** (both already flagged as open questions in the
Issue's own design decision, resolved by testing directly — not new
Kernel bugs): (1) `scale * <factory call>()` written inline fails
`RUNTIME_ERROR: cannot compile sparse Pauli for OpCall` — the
Operator-compiler's scalar multiplication only recognizes a `Var`
operand, not a direct `Call`; the factory's result must be pre-bound to
its own local `Operator` variable first. (2) an inline unit-suffixed
literal directly in the `for` clause (`for 0.15.fs`) does not satisfy
the fail-closed duration check either — `_hamiltonian_evolve_one_step`
only resolves `duration_unit` when `expr.duration` is a bare `Var`; the
duration must be declared as its own `Time`-typed variable and
referenced by name, matching every prior WP-0095 example. **Both
constraints apply to every remaining S01 Hamiltonian-wrapping migration
below** — flagged here so work units 14+ don't rediscover them.

### 14 — `main_morning_collect` — **complete**

Status: **complete**, PR
[#408](https://github.com/nn0cl/staqex/pull/408) merged (`c1ab33f`),
[LISS-0346](../issues/LISS-0346-s01-morning-collect-real-unit-migration.md).
`Operator H = Z` (bare Pauli letter assigned to an intermediate `Var`,
confirmed not on the legacy fast path) wrapped with `ops_energy_scale()`
using work unit 13's confirmed pattern (pre-bind `H_raw` before
`scale *`, duration as its own `Time` variable). No new findings —
Green passed on the first attempt.

### 15 — `main_day2_recovery` — **complete**

Status: **complete**, PR
[#410](https://github.com/nn0cl/staqex/pull/410) merged (`cde5191`),
[LISS-0347](../issues/LISS-0347-s01-day2-recovery-real-unit-migration.md).
First of the two `ConstraintCoeffs`-based files (shared with
`main_disaster_response`). `ConstraintCoeffs` itself stays `Float`
(per work unit 12's confirmed design); `Operator H =
recovery_hamiltonian(coeffs)` wrapped with the same
`ops_energy_scale()` pattern work unit 13 confirmed for coefficient-1
Hamiltonians — no new findings, confirming the pattern holds equally
for a computed-`Float`-weighted Hamiltonian. Green passed on the first
attempt.

### 16 — `main_disaster_response` — **complete** (final work unit)

Status: **complete**, PR
[#412](https://github.com/nn0cl/staqex/pull/412) merged (`f22d78a`),
[LISS-0348](../issues/LISS-0348-s01-disaster-response-real-unit-migration.md).
The flagship "tonight spine" — 4 Hamiltonians (`H_drive`,
`ConstraintCoeffs`-based, sharing `physics/constraint_h.sqx` with work
unit 15; `H_damage`/`H_flood`/`H_corridor`, coefficient-1, sharing
`grid/block_costs.sqx` with work unit 13) all wrapped with
`ops_energy_scale()`'s pre-bind + `scale *` pattern — including its
first use on a `product(...)`-built Hamiltonian (`corridor_product()`),
confirmed the scale applies once to the whole assembled result, not
distributed into individual factors. 4 evolve durations (3 computed
classical expressions — `t_drive`, `t_damage`, `t_corridor` — needing
B07's independent-`Time`-literal workaround, confirmed live a computed
dimensionless `Float` cannot be `to`-converted to `Time` either; 1
already a literal, `t_flood`). No new Kernel findings — every
constituent pattern was already proven by prior work units; this Issue
combined them in one file for the first time. **Bonus fix**: all 3
cases in `test_s01_tonight_ticket_export.py` (depend on this file
running end-to-end) flipped from failing to passing.

**This closes WP-0095.** Every ADR 0195-affected `.sqx` example across
`examples/basics`, `examples/applied`,
`examples/showcase/quantum_matter_discovery`, and
`examples/showcase/S01_quantum_disaster_response` is confirmed
migrated.

## Related, not blocking

`Operator G = adjoint(H)` fails at runtime (`RUNTIME_ERROR: cannot compile
operator node Call`, `hamiltonian.py` has no `Call`-node handling) —
discovered during ADR 0195's design check, confirmed unrelated to ℏ or
`evolve`'s formula. Tracked as its own Local Issue under WP-0092 (found
during that Work Plan's `dag`/`adjoint` scientific-lexicon investigation),
not this Work Plan.

`evolve`'s fail-closed duration check
(`_hamiltonian_evolve_one_step` in `compiler/staqex/runtime/evaluator.py`)
only recognizes a bare `Var` duration, not a dimensioned struct-field
`Attr` expression, even when the field genuinely carries a resolvable
unit via ADR 0174's field-unit tracking — discovered during LISS-0335's
design intake, worked around there with a local variable, not fixed.
Flagged for a future Kernel-side Issue if this pattern recurs often
enough across the remaining migrations to be worth generalizing.

`hamiltonian.py::op_n_qubits` undercounts the qubit register for
`Operator`s containing a Jordan-Wigner-mapped runtime value (opaque to
its AST site-scanning `walk()`) — discovered re-verifying A03 during
LISS-0336, confirmed pre-existing and unrelated to either bug LISS-0336
fixed. Not fixed there; deferred to its own new, separate Issue (not yet
filed) per Adjudicator direction.

LISS-0338 (A11 rewrite) found and fixed one real Kernel bug (struct
constructor calls from within an imported function's own body failed at
runtime — `evaluator.py::_bind_call` never checked `self.structs`/
`self.classes` for a bare-`Var` callee) and found, documented, but
**deliberately did not fix** three further classical-language gaps
(design avoided them instead): no execution path for free functions
*returning* a struct type (`_bind_user_fun` vs. `_eval_classical_call`'s
`classical_heads` mismatch); `&&` unsupported in expression position;
Float relational comparisons (`>`,`<`,`>=`,`<=`) between two classical
operands mistyped as `Classical<Float>` instead of `Classical<Bool>`
(`typecheck.py::_infer_binop`'s classical-arithmetic branch has no
relational-operator case); `abs()` has no classical-scalar
implementation (only a quantum `map_coord` one). See LISS-0338's own
"Related, not blocking" for full detail. Flagged for a future Kernel-side
Issue if any of these recur across the remaining migrations.

LISS-0341 (B08) found and fixed a third instance of the same systemic
category: `backend/qasm/trotter.py`'s Suzuki gate-angle computation
(`theta = coeff * delta_t`) was never updated for ADR 0195's real-ℏ
formula, and its own `_suzuki_term_gates` absolute-coefficient epsilon
predated LISS-0336's `sparse_pauli.py` fix — together these silently
turned any real Joule-scale Hamiltonian's QASM3 Trotter emission into an
"idle" no-op circuit. Fixed (divide by real ℏ; drop the redundant
pre-division filter). Confirmed general — affects any future
QASM3-emitted example with a real-`Time`-typed duration, not just B08.

[LISS-0337](../issues/LISS-0337-spec-verification-suite-real-unit-fixtures.md)
(2026-08-05, bundled into the LISS-0336 post-merge-sync PR) migrated 5
`spec_verification` suites' own internal test fixtures (`sv17`/`sv19`/
`sv27`/`sv28`/`sv29`, plus 4 shared `tests/fixtures/staqex/*.sqx` files)
to real units — these are Kernel spec_verification fixtures, not `.sqx`
catalog examples, so not itself a WP-0095 work unit, but directly
relevant: it restored `spec_verification`'s full 161-case reporting
(156/161, only the 4 already-tracked WP-0095 examples still failing) and
fixed a QASM3 Trotter-backend gap (`Energy`/`Time`-typed locals were
never recognized by `backend/qasm/lower.py`'s scalar collection) found
as a drive-by regression while doing so.

LISS-0343 (`quantum_matter_discovery`) found and fixed a fifth instance
of the same systemic category: `typecheck.py::_infer_binop`'s Classical
`+`/`-` branch hardcoded its result payload to `"Float"` (see work unit
11 above). The sibling Classical `*`/`/` branches in the same function
(same file, ~lines 3322-3326) are suspected to have the identical
hardcoded-payload issue but were **not** fixed — no live repro currently
forces that path. Flagged for a future Kernel-side Issue if a
multiplication/division of two same-dimensioned physical quantities
returning a dimensioned type is needed by a later migration. The
Float-relational-comparison mistyping documented under LISS-0338 above
remains separately unfixed and is architecturally adjacent but distinct
(a different operator-kind branch in the same function).

## Approval gates

- **Architecture approval:** ADR 0195 — complete.
- **Work-plan investigation:** this document, plus LISS-0330's own design
  intake, precede any batch-approval request. No batch approval is being
  requested — each work unit proceeds through ordinary Issue-Level Plan/
  Completion approval, one Issue at a time, matching this session's
  established pattern for every other Work Plan so far.
- **Per-Issue Plan approval:** required before each work unit's Phase 1
  Red, per CLAUDE.md's Issue-Level Autonomy.

## Verification

Each work unit's own Issue carries its own verification evidence
(`pytest`, `tests/spec_verification/run_all.py`, `git diff --check`).
Work unit 1 additionally requires a hand-computed reference value,
independent of the Kernel's own output, before it can be trusted.
