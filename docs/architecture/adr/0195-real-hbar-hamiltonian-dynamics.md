# ADR 0195: real ℏ and dimensioned Hamiltonian time-evolution

## Status

**Accepted** (2026-08-05) — Architecture Path decision, approved by the
Adjudicator. This is one of the largest changes considered this
session: it redefines the numeric meaning of every `evolve ... under H for
t` construct in the shipping Kernel and requires migrating the example
base. Acceptance approves the physics/semantics decision and the phased
rollout shape below; it does not by itself authorize any single migration
Issue — each still needs its own Plan approval, per CLAUDE.md's Issue-Level
Autonomy.

## Design check

- **Scope and expected behavior:** Staqex currently computes
  `evolve ψ under H for t` as `U = exp(-i H t)` — natural units, ℏ
  implicitly `1`, hardcoded directly in the matrix-exponential primitive.
  This ADR proposes replacing that with real, dimensioned time evolution
  `U = exp(-i H t / ℏ)` using ℏ's real SI value, so a physicist can supply
  a Hamiltonian in real energy units (`eV`, `J`) and a duration in real
  time units (`s`, `ps`, …) and get physically meaningful dynamics —
  matching the user's stated goal: "used for physics research," not only
  pedagogical toy examples.
- **Specifications and files inspected:** `compiler/staqex/runtime/matrix.py::expm_ih`
  (confirmed: `a = mat_scale(h, -1j * float(t))` — no `/ℏ` division
  anywhere; this is the sole primitive every `evolve` call path uses,
  confirmed via all three call sites in `runtime/evaluator.py:1614/1644/1752`
  plus the sparse-Pauli path `sparse_pauli.py::expm_ih_apply`);
  `compiler/staqex/runtime/hamiltonian.py` (module docstring: *"Compile
  Operator AST → dense Hamiltonian matrix (ℏ = 1)"* — confirms this is a
  named, deliberate existing convention, not an oversight);
  `compiler/staqex/dimensions.py` (confirmed real, shipped infrastructure
  already exists to build on: `Energy` dimension `Dim(L=2, M=1, T=-2)`
  with `J`/`eV` unit conversion (`eV → J`, factor `1.602176634e-19`,
  already exact per 2019 SI redefinition); `Time` dimension `Dim(T=1)`
  with `s`/`ms`/`us`/`ps` conversions — **no `ns` or `fs`**, a gap this
  ADR's rollout will likely need to fill, consistent with the existing
  one-unit-at-a-time ADR lineage (0124–0151)); a live probe of
  `evolve.md`, `Operator G = adjoint(H)` (also confirmed broken at
  runtime independent of this ADR — `hamiltonian.py` has no `Call`-node
  handling at all, `RUNTIME_ERROR: cannot compile operator node Call` —
  tracked as a separate, unrelated existing bug, not caused by or blocking
  this ADR); `grep` count: 19 example `.sqx` files and 77 total
  files (examples + tests) reference `evolve ... under ... for`.
- **Component boundaries, ports/adapters, and VO/DTO candidates:** Kernel
  runtime only (`runtime/matrix.py`, `runtime/hamiltonian.py`,
  `runtime/evaluator.py`, `runtime/sparse_pauli.py`). No new port — ℏ is a
  mathematical/physical constant, not an external resource. Builds on the
  already-shipped `dimensions.py` Type-First `Energy`/`Time` machinery;
  does not introduce a new dimension system.
- **Applicable constraints:** No silent unit stripping (the project's
  established Type-First discipline, ADR 0121–0155). No compatibility
  shim that silently reinterprets old natural-units source with new
  meaning — per the user's explicit "samples must be updated, do the
  proper implementation" (2026-08-05), migration is a real rewrite of
  affected examples' Hamiltonian/time magnitudes to physically sensible
  SI values, not a flag or dual-mode toggle. Fail-closed: an `evolve`
  whose `H`/`t` cannot be resolved to real Energy/Time dimensions must
  reject explicitly, not silently assume natural units.
- **Decisions, assumptions, unresolved ambiguities:** ℏ's numeric value
  (§Decision 1) — CODATA 2018 exact value via the 2019 SI redefinition,
  `1.054571817...e-34 J*s`, matching the same "already-exact defining
  constant" treatment `eV`'s conversion factor already receives. Rollout
  order (§Decision 3) — this ADR recommends starting with the Kernel
  primitive plus one reference example (`A03_h2_vqe`, already a real
  molecule) before the remaining 18, given each example's real energy/time
  scale requires physics-domain judgment per system, not a mechanical
  find-replace; the Adjudicator may prefer a different first example or
  ordering.
- **Included and omitted AI context:** Included direct reads of every
  `expm_ih` call site, `dimensions.py`'s existing unit tables, and a live
  runtime probe distinguishing this ADR's scope from the unrelated
  `adjoint(H)` bug. Omitted: chemistry-accuracy claims for any specific
  molecule's energy levels (real literature values must be sourced per
  example during migration, not invented here) and any live QPU/hardware
  timing concern (separate, ADR 0193's scope).
- **Task routing:** Architecture review for the physics/semantics
  decision; deterministic source inspection for all current-state claims;
  no external AI/model call for this design intake. Per-example real
  energy/time value sourcing during migration should cite a public
  reference (e.g. NIST/CODATA data) rather than an unsourced AI estimate,
  per `io-reasoning-contracts.md`'s input/output evidence discipline.
- **Verification plan:** After acceptance, a work-plan investigation
  (spec/ADR already this document; Local Issues; granularity rationale;
  execution order; draft batch record) precedes any batch approval, per
  CLAUDE.md's mandatory work-plan investigation rule — this ADR's
  Follow-up section below is the first draft of that shape, not the
  investigation itself.

## Context

The Kernel's `evolve ψ under H for t` is a foundational primitive
exercised by nearly every non-trivial example (19 `.sqx` files, 77
including tests). Its current `U = exp(-iHt)` formula silently assumes
natural units (ℏ = 1) — a common convention in theoretical-physics
pedagogy, but one that makes `H` and `t`'s numeric values physically
meaningless outside that convention: a physicist cannot supply a real
molecule's energy gap in `eV` and a real femtosecond duration and expect
`evolve` to produce the physically correct phase. `hamiltonian.py`'s own
docstring names this convention explicitly, confirming it is a deliberate
existing choice, not an oversight — but WP-0092's scientific-lexicon work
unit's `hbar` candidate alias surfaced the tension: a real ℏ constant is
meaningless if the Kernel's own evolution math never uses it.

Staqex already has the dimensional infrastructure this needs:
`dimensions.py`'s `Energy` and `Time` Type-First dimensions, with real
unit conversions (`eV → J`, `s`/`ms`/`us`/`ps`) already shipped via the
ADR 0121–0155 lineage. This ADR's job is to connect that existing,
real infrastructure to `evolve`'s actual numerics — not to invent a new
one.

## Decision proposal

### 1. ℏ's real value and where it lives

Add `HBAR_SI = 1.054571817e-34` (J*s, CODATA 2018 exact) to
`compiler/staqex/dimensions.py` (or a small dedicated `physical_constants.py`
module, TBD during implementation) as the single source of truth ℏ used
by both `evolve`'s runtime formula and the `hbar` prelude-constant surface
name a physicist can reference directly in source (WP-0092's original
scientific-lexicon candidate). One value, two consumers — never two
separately-maintained numbers that could drift.

### 2. `evolve`'s formula becomes dimensioned

`runtime/matrix.py::expm_ih` (and the sparse-Pauli equivalent) changes
from `U = exp(-i H t)` to `U = exp(-i H t / hbar)`, where `H`'s numeric
value is required to already be in real Joules and `t` in real seconds by
the time it reaches this primitive — the SI-scale conversion (`eV to J`,
`ps to s`, etc.) happens earlier, via the already-shipped `to` operator,
exactly like every other dimensioned quantity in the language today. No
new conversion machinery is invented here. This is an in-place formula
replacement, not an additional mode: the old `U = exp(-i H t)` line is
removed from the codebase, not retained behind a flag or alternate
function (see the strengthened "Rejected alternatives" note below).

### 3. Migration is real, not a compatibility shim

Every existing example's `H`/`t` magnitudes were chosen under the old
ℏ = 1 convention and are not physically meaningful SI values. Per the
Adjudicator's explicit direction, these are rewritten with real energy and
time scales sourced from public references (NIST/CODATA, or the specific
system's known literature values), not silently reinterpreted or run
through an automatic rescaling formula that would hide the fact that the
old numbers were never real to begin with. This is real content-authoring
work per example, not a mechanical patch.

**Recommended rollout order:** Kernel primitive change first (`expm_ih` +
`hbar` constant), verified against a hand-computed reference case (e.g. a
two-level system with a known, real energy gap and a known real Rabi
period). Then migrate examples one at a time, starting with
`A03_h2_vqe` (already targets a real molecule, so its real energy
scale is the least speculative to source), each as its own Local Issue
with its own Plan/Completion approval — not one giant batch that risks
silently wrong physics in 18 examples reviewed too quickly.

### 4. Fail-closed on unresolvable units

If `evolve`'s `H` or `t` cannot be resolved to a real `Energy`/`Time`
dimension by the time it reaches `expm_ih` (e.g. a bare dimensionless
`Float` with no unit annotation), the Kernel must reject with an explicit
diagnostic — never silently assume the value is already in SI units or
silently fall back to the old ℏ = 1 behavior. The exact diagnostic
name/shape is implementation detail for the first Local Issue, not decided
here.

## Consequences

- `evolve` becomes physically real: a physicist can express a genuine
  Hamiltonian in real energy units and a real duration and get a
  physically correct answer, not a natural-units convention they must
  remember and mentally rescale.
- `hbar` becomes a real prelude constant, not a decorative one disconnected
  from actual Kernel dynamics.
- Every existing `evolve`-using example needs real physics content work to
  migrate, not a mechanical patch — this is a genuinely large,
  multi-Issue undertaking, tracked via its own work-plan investigation
  after this ADR's acceptance.
- `ns`/`fs` time units will likely need adding to `dimensions.py` during
  migration (small, same pattern as existing SI-scale ADRs).
- The unrelated `adjoint(H)`/`Call`-node `hamiltonian.py` bug found during
  this investigation is *not* fixed by this ADR — tracked separately.

## Rejected alternatives

### Dual-mode: keep ℏ = 1 as an explicit opt-out alongside real SI dynamics

**Rejected and removed, not merely deprioritized** — explicit Adjudicator
confirmation (2026-08-05): a permanent natural-units path is a real
correctness hazard, not just a style preference. If the Kernel kept a
ℏ = 1 fallback available, a program could silently combine real
SI-sourced `H`/`t` values with the wrong internal formula and produce
gate angles that are wrong by ~34 orders of magnitude once any future
target adapter compiles them to real hardware — the exact failure mode
this ADR exists to prevent. Concretely: after migration, `matrix.py`'s
old `U = exp(-i H t)` line is **deleted**, not kept behind a flag,
setting, or alternate function; there is no code path, default, or
silent-fallback behavior anywhere in the Kernel that reintroduces
ℏ = 1. A phased *rollout* is still necessary (the examples cannot all be
rewritten atomically — see §Decision 3), but during that rollout an
unmigrated example must fail closed (explicit diagnostic) rather than
silently keep running under the old formula.

### Automatic rescaling of existing H/t values

Rejected. Any formula that rescales old ℏ=1-convention numbers into
"equivalent" SI values would produce numbers with no real physical
grounding — solving the wrong problem. The old numbers were never real
energies/times; they must be replaced with real ones sourced from
physics, not algebraically transformed.

## Follow-up work required after acceptance

This ADR's size requires the mandatory work-plan investigation
(`docs/collaboration/local-issue-planning.md`-governed spec/Issues/
granularity/order/draft-batch-record) before any batch approval, per
CLAUDE.md. First draft of that shape:

1. New Work Plan (next free `WP-####`) scoping this whole effort,
   parented to this ADR.
2. Local Issue 1: `hbar` constant + `expm_ih`/sparse-Pauli formula change
   + fail-closed unit-resolution diagnostic + a hand-verified reference
   test case. No example migration in this Issue.
3. Local Issue 2+: one Issue per example (or small, physically-related
   group of examples), each sourcing real energy/time values from a
   public reference, starting with `A03_h2_vqe`.
4. `ns`/`fs` time-unit additions to `dimensions.py`, likely folded into
   whichever Issue first needs them.
5. Separately (not blocking this ADR): file the `adjoint(H)`/`hamiltonian.py`
   `Call`-node bug as its own small Local Issue.

## Acceptance boundary

Acceptance of this ADR approves the physics/semantics decision (real ℏ,
dimensioned `evolve`, real migration not a shim) and the phased rollout
shape above. It does **not** authorize any implementation — the
work-plan investigation and each Local Issue's own Plan approval remain
separately gated, per CLAUDE.md's Issue-Level Autonomy and mandatory
work-plan investigation rule.
