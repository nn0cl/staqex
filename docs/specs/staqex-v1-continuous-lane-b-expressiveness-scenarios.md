# Continuous / Lane B — expressiveness scenarios (proper-demand seats)

| Field | Value |
|---|---|
| Status | **Scoring baseline frozen** (2026-08-03, LISS-0319) — compose closed as weak+Host/H→E; Ideal §2A remains law for Ideal Y. §7's "Architecture Accept Lane B ship shape" gate is now satisfied: [ADR 0204](../architecture/adr/0204-continuous-lane-b-type-world.md) **Accepted** (2026-08-10). Feature Plan investigation not yet started — seat scoring stays **weak** until Green. |
| Issue | [LISS-0315](../architecture/documentation-compression-map.md) (seats); [LISS-0316](../architecture/documentation-compression-map.md) (Ideal); [LISS-0317](../architecture/documentation-compression-map.md) / [LISS-0318](../architecture/documentation-compression-map.md) (Runtime H); [LISS-0319](../architecture/documentation-compression-map.md) (score sync) |
| Review | [2026-08-03-continuous-lane-b-expressiveness-intake.md](../collaboration/reviews/2026-08-03-continuous-lane-b-expressiveness-intake.md) |
| Ship law | Mid-program `Continuous` **not yet Green** — [ADR 0204](../architecture/adr/0204-continuous-lane-b-type-world.md) Accepted as architecture boundary; Feature Path Red still requires a separate Feature Plan + Issue-level Plan approval before any Kernel code |
| Companions | ADR 0126, 0162, 0163, 0164; Lane A surface LISS-0313; S01 [locked scenario](staqex-v1-s01-locked-scenario.md) §Field continuous |
| Pedagogy | [physicist-minimal-dialect](../architecture/physicist-minimal-dialect.md); Ideal form first (ADR 0095) |

```markdown
[DESIGN CHECK]
- Scope: lock proper-demand scenarios for mid-program Continuous (Lane B) so
  language expressiveness can be scored like S01 A+B seats — Ideal chalk vs
  current Kernel, Class, action.
- Not in scope: Kernel Continuous Red; city-wide continuous QC; CFD/seismic
  waveform sims; amending ADR 0185 to ship Lane B.
- Obligation: each seat names Ideal form, hard gates, Lane A/Host substitute,
  and expressiveness gap (not theatrical coverage).
```

## 0. Product rule (Continuous expressiveness)

> Inventory **proper** continuous demand first; scenario seats grow only where
> multi-step continuous carriers must be first-class mid-program values; spine
> disaster OS stays finite jobs + Host. Ideal form is written before machine
> spelling. Measure / QPU remain finite-only forever under these seats.

**Proper-demand one-liner (Lane B):**

> Finiteize より前に、連続キャリアへの複数の意味ある変換を、Staqex 中盤の
> first-class 値として書き、有限化以降だけを Joint / measure に載せたい。

**Not proper (do not seat as Lane B):**

- 首都圏グリッド / 多セル Host federation alone  
- one-shot demand histogram inject (Lane A `finiteize` / Host MC)  
- magical continuous city-wide optimum QC  

---

## 1. Lane map (honesty)

| Lane | Role in these seats |
|---|---|
| **H** | Sensors, GIS, raw continuous models, MC draw callables |
| **Continuous mid-program (Lane B — future)** | Named continuous carriers; multi-step field algebra; **no** `measure` |
| **finiteize (Lane A — shipped)** | Continuous description / samples → finite `State` |
| **E finite Joint** | Tonight plan / zone assignment after finiteize; terminal `measure` |

```text
[H / Theory continuous world]
        │  (optional: bind as Continuous mid-program — Lane B)
        │  multi-step continuous transforms
        ▼
   finiteize  ──▶  finite State / Joint  ──▶  measure
   (Lane A)         (E-lane disaster plan)
```

---

## 2. Locked seats (expressiveness chapters)

Each seat must remain checkable even while Lane B is unshipped: Ideal chalk is
normative for **review**; Runtime path today is the **Lane A / Host substitute**.

### CH-field-compose — multi-step continuous field algebra → one finiteize

| Field | Value |
|---|---|
| Seat ID | **CH-field-compose** |
| Ops story | K-ku: damage density × flood / fire risk weight × impassable mask → zone priority field → finite bins for tonight shelter / rescue pressure |
| Why Lane B proper | ≥2 continuous transforms before any discrete assignment; Ideal form wants named mid-program continuous carriers, not one opaque Host blob |
| Phase | Pre-tonight Host prep → inject into E plan job |
| Hard gates | No `measure` on continuous; no silent grid; provenance on finiteize |
| **Ideal deep-dive** | **§2A below** (LISS-0316) — normative for expressiveness scoring of this seat |

**Ideal form (compact — full expansion in §2A):**

```text
// Ideal — continuous world (Lane B)  [NOT legal Kernel Continuous today]
Continuous damage = field_from_host(…)
Continuous risk   = weight(damage, flood)
Continuous masked = mask(risk, impassable)
state zone = finiteize(masked, bins = N, interval = …)
// finite E-lane plan (existing disaster dialect)
measure plan tracing_out …
```

**Today (shipped substitute — expressiveness debt for Ideal form):**

```text
// multi-step continuous algebra lives in Python — not typed Staqex mid-program
// Named Host stages + inject: host/field_compose_inject.py (LISS-0317)
// Uniform Lane A only: state zone = finiteize(0.0, 1.0, N, samples, seed)
```

**Host substitute (H-lane, runnable):**
`examples/showcase/S01_quantum_disaster_response/host/field_compose_inject.py`
— Ideal pipeline stages as Host functions; provenance
`continuous_pipeline`; finite Joint via ADR 0163/0164.

**H→E bridge (runnable):**
`host/field_compose_to_tonight_plan.py` (LISS-0318) maps zone masses →
ConstraintCoeffs-shaped feed → thin finite evolve/`measure` sample + JSON
envelope. Full tonight spine desk packs remain separate. Seat remains **weak**
vs Ideal Continuous mid-program, but the causal map Host→coeffs→plan is
auditable.

| Check | Ideal | Today | Gap |
|---|---|---|---|
| Named continuous multi-step | Y | N | **B — needs Lane B ship ADR** |
| Explicit finiteize | Y | partial (uniform histogram MVP) | A — extend finiteize args / Host draw |
| Finite plan + measure | Y | Y | — |
| City-wide continuous QC | forbidden | forbidden | — |

---

## 2A. Ideal deep-dive — CH-field-compose (normative for scoring)

| Field | Value |
|---|---|
| Status | **Ideal form expansion** (2026-08-03) — docs only; not Kernel law |
| Issue | [LISS-0316](../architecture/documentation-compression-map.md) |
| Seat | CH-field-compose |
| Ship Continuous | **forbidden** until a future Lane B ship ADR (ADR 0185 non-goal) |

This section is the **Ideal form first** (ADR 0095) reference for one seat.
Agents score expressiveness against **§2A.3–2A.7**, not against opportunistic
Host Python that hides the multi-step algebra.

### 2A.1 Physicist one-sentence (must stay true)

> Overnight damage and flood/fire risk on the ward plane are combined and
> masked by impassable geometry as **continuous fields**, then **explicitly**
> discretized into zone bins that feed tonight’s finite plan sample — never
> measured while still continuous.

If a proposed surface forces measuring continuous risk, or folds weight+mask
into an opaque Host black box with no named intermediate fields, it **fails**
this seat’s Ideal form.

### 2A.2 Narrative placement (K-ku, not 首都圏 mega-job)

| Beat | Who | What |
|---|---|---|
| T−30 min … T−5 | Host / sensors | Damage proxy, inundation, fire index, road graph |
| T−5 … T0 | **CH-field-compose Ideal** | Continuous compose → finiteize → zone State |
| T0 tonight | E-lane spine | Constraint H, `when`, `measure plan0 tracing_out …` |
| After measure | Host ticket | Tonight handoff; continuous fields do not re-enter measure |

**Not this seat:** G01–G80 federation, rolling replan orchestration, CFD fire
spread, continuous seismic waveforms (S0 out).

### 2A.3 Type worlds (Ideal)

| World | Carrier (Ideal spelling) | May enter `measure`? | May enter QPU/QASM? |
|---|---|---|---|
| Continuous | `Continuous<Field>` / `Continuous` (payload TBD in ship ADR) | **No** | **No** |
| Finite | `State<…>` / Joint | **Yes** (terminal) | Only if placeable finite IR |
| Classical Host | Float packs, graphs, tickets | N/A (Host) | N/A |

**Crossing continuous → finite** is only via **explicit finiteize** (0162).
There is no silent grid, no “Continuous that acts like State.”

LINEAR (Ideal expectation when Continuous ships): continuous binds are
**linear or affine-use** under a future rule — at minimum, no implicit discard
of a named continuous root without finiteize / explicit drop. Exact LINEAR
row is ship-ADR material; for Ideal scoring, require **every named Continuous
to be consumed by finiteize or an explicit continuous discard form**.

### 2A.4 Field dictionary (Ideal physics reading)

Coordinates: ward plane \(x \in \Omega\) (abstract continuous domain — not a
Kernel grid until finiteize).

| Name | Ideal type | Physics reading | Source |
|---|---|---|---|
| `damage` | `Continuous` | Damage / collapse density proxy on \(\Omega\) | Host sensor / model inject |
| `flood` | `Continuous` | Inundation / liquefaction pressure field | Host |
| `fire` | `Continuous` (optional arm) | Fire / firestorm pressure | Host |
| `impassable` | `Continuous` or classical mask field | Geometry where units cannot go | Host road graph → field |
| `risk` | `Continuous` | Combined operational risk weight | **Derived** continuous |
| `masked` | `Continuous` | Risk after impassable suppression | **Derived** continuous |
| `zone` | `State` (finite labels) | Discrete zone / bin pressure after finiteize | finiteize result |

Dim / units (Ideal): prefer Type-First **density-like** tags where meaningful
(e.g. people/area, dimensionless risk index). Exact Dim algebra for Continuous
is ship-ADR; Ideal scoring requires **no silent SI strip** of known Host units
at the continuous boundary without provenance.

### 2A.5 Continuous algebra (Ideal operators — multi-step)

Ideal requires **≥2 named continuous transforms** before finiteize. Minimum
ops for this seat (names are Ideal chalk, not shipped keywords):

| Op (Ideal) | Sort | Reading |
|---|---|---|
| `field_from_host(…)` / inject | Continuous | Bring Host continuous description into mid-program |
| `weight(damage, flood[, fire])` | Continuous → Continuous | Pointwise risk composition (not discrete zone yet) |
| `mask(risk, impassable)` | Continuous → Continuous | Suppress support / set risk 0 on impassable |
| `finiteize(masked, …)` | Continuous → State | **Only** legal exit to measure world |

**Forbidden Ideal shortcuts for this seat:**

- `state zone = host_blackbox_compose_and_bin(…)` with no named `risk`/`masked`
- `measure risk` while `risk` is continuous
- weight+mask folded inside finiteize args only (collapses multi-step Ideal)

**Optional later Ideal (not required for seat pass):**

- `clip`, `normalize_field`, `support_restrict` as additional continuous maps
- Dual-output continuous still single finiteize (fork is CH-field-fork)

### 2A.6 Full Ideal program (blackboard transcript)

Spelling is **Ideal**. Tokens marked `(ship)` do not exist as Continuous mid-
program law today. Lane A `finiteize` positional form is real only for uniform
samples, not for Continuous-valued args.

```text
// ============================================================
// CH-field-compose — Ideal form (Lane B + finiteize)
// Expressiveness reference — NOT Runtime Continuous
// ============================================================

// --- Host boundary: continuous descriptions enter with provenance ---
Continuous damage = field_from_host(
  source = "damage_proxy_v1",
  domain = Omega_Kku,              // abstract continuous domain
  provenance = { sensor_window = "T-30..T-5" }
)
Continuous flood = field_from_host(source = "inundation_v1", domain = Omega_Kku)
Continuous fire  = field_from_host(source = "fire_index_v1", domain = Omega_Kku)
Continuous impassable = field_from_host(source = "road_block_field", domain = Omega_Kku)

// --- Mid-program continuous algebra (≥2 steps; named roots) ---
Continuous risk = weight(damage, flood, fire)
// reading: pointwise operational pressure on the plane
Continuous masked = mask(risk, impassable)
// reading: zero / drop support where units cannot operate

// --- Explicit finiteization (only bridge to State) ---
state zone = finiteize(
  masked,
  approximation = EqualWidthHistogram,   // or declared grid contract
  bins = N_zone,                         // e.g. district / block index
  interval = support_of(masked),         // or declared [lo,hi)
  label_mode = bin_index,                // ADR 0164 vocabulary
  provenance = {
    discretization = { basis = "EqualWidthHistogram", resolution = N_zone, … },
    continuous_pipeline = ["weight", "mask"],
    note = "finite approximation of masked risk; not the continuous field"
  }
)

// --- Finite E-lane (existing disaster dialect; spine-compatible) ---
// zone feeds constraint coeffs / when arms / plan superposition
state plan0 = … // ket / when / evolve under H_constraint for t  (finite)
// …
measure plan0 tracing_out …              // NEVER measure masked / risk / damage
```

**Reading order for a physicist:** continuous fields → combine → mask →
**then** discretize → only then plan sample.

### 2A.7 Finiteize boundary (Ideal contract)

Finiteize is the **type gate**, not a style preference.

| Rule | Ideal requirement |
|---|---|
| Input | Continuous (or Host continuous description explicitly lifted) |
| Output | Finite `State` / Joint only |
| Approximation | Named (`EqualWidthHistogram`, UniformGrid, …) — never silent |
| Provenance | ADR 0074-style `discretization` block + continuous pipeline list |
| Errors | Empty support / invalid bins / missing domain → fail closed |
| After | Ordinary NLTS / LINEAR / `tracing_out` on finite carriers only |

**Lane A today (LISS-0313)** implements only:

```text
finiteize(lo, hi, n_bins, n_samples[, seed])  // uniform draw on [lo,hi)
```

So Ideal `finiteize(masked, …)` is a **gap**: Continuous-valued first argument
and non-uniform field density are not Lane A MVP.

### 2A.8 Connection to tonight spine (honesty)

| Spine (`main_disaster_response.sqx`) | CH-field-compose Ideal | Host Runtime (LISS-0317/0318) |
|---|---|---|
| Finite plan sample | Consumes **outputs** of finiteize (`zone` → coeffs / arms) | Thin E-lane with Host-mapped congestion/fairness |
| No Continuous mid-program | Compose seat is **pre-spine** constellation / Host-prep chapter | Compose + map stay on H |
| `measure plan0` | Never replaced by measuring continuous risk | Thin plan `measure plan0 tracing_out plan1` |

Ideal does **not** rewrite the spine into Continuous. Full OS spine desk packs
remain authoritative for constellation tonight; LISS-0318 is the **auditable
H→E link** for this seat, not a spine replacement.

Expressiveness scoring asks: can the **prep chapter** speak Ideal form without
Host-only multi-step? (Host substitute is allowed; Ideal Y still needs Lane B.)

### 2A.9 Ideal vs today — expanded gap matrix

| Concern | Ideal | Today (shipped) | Class | Action |
|---|---|---|---|---|
| Named `damage`/`risk`/`masked` continuous binds | Y | N (Python vars) | **B** | Lane B ship ADR |
| `weight` / `mask` as typed continuous ops | Y | N | **B** | ship ADR op list ≤ MVP |
| `finiteize(Continuous, …)` | Y | N | **B**+**A** | Continuous arg + finiteize extend |
| Uniform `finiteize(lo,hi,…)` | optional demo | Y (B18) | — | keep as teaching MVP |
| Host field prep entirely outside Staqex | allowed H | **LISS-0317 named stages** | **E** | weak seat honest; Ideal still needs B |
| Provenance continuous_pipeline | Y | **Y (Host inject)** LISS-0317 | — | keep |
| H→E zone→coeffs→plan sample | optional Ideal | **Y (Host)** LISS-0318 | — | keep (not Lane B) |
| `measure` continuous | forbidden | N/A | **A** | keep-forbidden |
| Spine absorbs Continuous | forbidden | N | **A** | keep-forbidden |
| City-wide continuous QC | forbidden | forbidden | **A** | keep-forbidden |

### 2A.10 Expressiveness scorecard for this seat only

Score when reviewing language design / samples for CH-field-compose:

| Criterion | Pass if |
|---|---|
| **Ideal form first** | §2A.6-shaped multi-step continuous visible in design, not only Host |
| **≥2 continuous steps** | weight and mask (or equivalents) named before finiteize |
| **Type gate** | No measure / QPU on continuous; finiteize sole exit |
| **Provenance** | Discretization + pipeline list in Ideal or Host substitute honesty |
| **Spine purity** | Tonight main remains finite dialect |
| **Substitute honesty** | If only Host/Python multi-step, seat marked **weak** not Y |
| **No granularity lie** | Not sold as “continuous city OS on one QPU” |
| **H→E auditable** | Zone masses map to finite plan feed without claiming Continuous Runtime |

**Seat status today (baseline freeze LISS-0319):** **weak**

| Layer | Path | Status |
|---|---|---|
| Ideal | §2A blackboard | **Y** (docs law for Ideal scoring) |
| Host multi-step | `host/field_compose_inject.py` (LISS-0317) | **Y** (H substitute) |
| H→E bridge | `host/field_compose_to_tonight_plan.py` (LISS-0318) | **Y** (auditable link) |
| Mid-program Continuous Runtime | — | **N** (deferred; needs-ADR) |
| **Aggregate seat today** | Ideal Y + Runtime H only | **weak** — do **not** mark Y until Lane B ships |

**Do not reopen compose Host demos** unless Ideal or honesty breaks. Next language
investment is optional Lane A extend or other P3 — not more compose packaging.

### 2A.11 Ship ADR checklist (when Adjudicator opens Lane B)

Not authorized now. Minimum contents if Ideal is to become law:

1. `Continuous` type world + hard gates (measure/QPU/Joint mix)  
2. MVP continuous ops for this seat: inject, weight, mask (or smaller set that still yields ≥2 steps)  
3. `finiteize` accepts Continuous + 0074 provenance  
4. LINEAR / discard story for Continuous roots  
5. Constellation sample path (not spine rewrite)  
6. Explicit non-goals: CFD, continuous seismic, city-wide continuous optimum  

### 2A.12 Worked numeric micro-Ideal (for review intuition)

Abstract 1-D domain \(\Omega=[0,1)\) (toy, not production GIS):

| \(x\) band | damage | flood | impassable | risk (Ideal weight) | masked |
|---|---:|---:|---:|---:|---:|
| [0,0.3) | high | med | 0 | high | high |
| [0.3,0.6) | med | high | 1 | — | **0** (masked) |
| [0.6,1) | low | low | 0 | low | low |

Finiteize to \(N=3\) bins → finite `zone` masses reflect **masked** risk only.
Tonight plan uses those masses/labels as classical coeffs or State preparation
inputs — continuous table never appears in `measure`.

This table is **pedagogy**, not a required Runtime grid.

---

### CH-field-fork — one continuous carrier → dual finiteize (two resolutions)

| Field | Value |
|---|---|
| Seat ID | **CH-field-fork** |
| Ops story | Same damage / demand field: coarse bins for capital fairness Host, fine bins for K-ku tonight assignment |
| Why Lane B proper | Shared continuous root; two finiteizations; Host dual-pipeline loses a single typed source |
| Phase | Morning re-estimate + tonight dual inject |
| Hard gates | Both finiteize paths carry independent ADR 0074 provenance |

**Ideal form:**

```text
Continuous damage = …
state coarse = finiteize(damage, grid = CoarseWard)
state fine   = finiteize(damage, grid = FineBlock)
// Host may federate coarse; E-lane measures fine plan only
measure fine_plan tracing_out …
```

**Today:** two Host MC injects or two `finiteize` calls with **no shared Continuous value** — formulas duplicated in Python.

| Check | Ideal | Today | Gap |
|---|---|---|---|
| Shared continuous bind | Y | N | **B** |
| Dual finiteize provenance | Y | Host-only | A/H |
| Independent resolution | Y | Y (Host) | type story missing |

---

### CH-field-theory — Theory continuous_operator aligned with notebook continuous

| Field | Value |
|---|---|
| Seat ID | **CH-field-theory** |
| Ops story | Pedagogy seat: continuous operator / field equation in Theory scope → same continuous type vocabulary → finiteize → small Joint evolve (not full CFD) |
| Why Lane B proper | Unifies Theory bridge (ADR 0074 / LISS-0111) with notebook continuous carriers; without Continuous type, Theory and Host remain disconnected dialects |
| Phase | Teaching / constellation satellite (not tonight spine) |
| Hard gates | Explicit discretization contract; no silent FD; no measure continuous |

**Ideal form:**

```text
// Theory continuous_operator + contract (existing path, Ideal continuous type)
Continuous psi_c = …
state psi = finiteize(psi_c, contract = UniformGrid(…))
state psi = evolve psi under H_grid for t
measure psi
```

**Today:** Theory discretization bridge lowers to grid Hamiltonian; Host MC separate; **no** mid-program Continuous shared type.

| Check | Ideal | Today | Gap |
|---|---|---|---|
| One continuous type world | Y | N (two paths) | **B + vocabulary ADR** |
| Explicit discretization | Y | Y (Theory) | keep |
| Finite evolve + measure | Y | Y | — |

---

## 3. Expressiveness inventory (score like S01 A+B)

**Seat today:** Y = Ideal + Runtime path honest; weak = substitute only; N = Ideal only.  
**Baseline freeze (LISS-0319):** CH-field-compose Runtime path is **explicit and closed**;
aggregate seat stays **weak** until Lane B.

| Surface / intent | Ideal seat | Path today | Seat today | Lane | Language-design note | Expressiveness note | Class | Action |
|---|---|---|---|---|---|---|---|---|
| Mid-program `Continuous` bind | CH-field-compose/fork/theory | — | N | B future | ADR 0126 Decision 1 still holds | Core Ideal gap | **B** | needs-ADR (Lane B ship) — **not next** |
| Continuous multi-step map/weight/mask | CH-field-compose | **Host named stages** LISS-0317 | **weak** | H | Ideal form first | Multi-step readable on H; not typed Continuous | **B** | needs-ADR for Ideal Y; **Runtime keep** Host |
| H→E zone→coeffs→finite plan | CH-field-compose | **LISS-0318** bridge | **weak** (part of compose) | H→E | causal map honesty | Auditable feed; spine not rewritten | — | **keep** (baseline) |
| `finiteize` from Continuous value | all CH-field-* | `finiteize(lo,hi,…)` uniform MVP | weak | A | ADR 0185 Lane A | Entry honest; args thin | **E** | extend finiteize (optional later) |
| Dual finiteize shared root | CH-field-fork | dual Host inject | weak | H/A | provenance ×2 | Secondary to compose | **B** | park until compose Ideal Y needed |
| Theory continuous_operator | CH-field-theory | LISS-0111 bridge | weak | Theory | ADR 0074 | Vocabulary split vs Host MC | **B** | park |
| Host MC inject | demand / damage prior | 0163/0164 + S01 host | Y | H | OS shell | Good for one-shot inject | — | keep |
| Lane A `finiteize` Call | B18 | LISS-0313 | Y | A | shipped | Teaching entry | — | keep |
| Finite Joint plan + `tracing_out` | S01 spine | shipped | Y | E | NLTS | Disaster OS core | — | keep |
| Continuous `measure` | — | forbidden | N/A | — | hard gate | Must stay illegal | **A** | keep-forbidden |
| City-wide continuous QC | — | forbidden | N/A | — | locked scenario | Anti-goal | **A** | keep-forbidden |
| CFD / continuous seismic waveform | — | out | N/A | — | S0 honesty | Not language seat | — | permanent-out sample |

**Counts:** inventory **13** rows (H→E bridge row added).  
**needs-ADR (Lane B):** **3** active (compose multi-step Ideal, fork, theory) + bind.  
**compose Runtime:** **keep / frozen**. **extend finiteize:** **1** optional.  
**keep / keep-forbidden:** rest.

### 3.1 CH-field-compose baseline freeze (0 + 1)

| Decision | Value |
|---|---|
| Aggregate seat today | **weak** |
| Ideal scoring reference | §2A only |
| Runtime H path | `field_compose_inject.py` (0317) |
| Runtime H→E path | `field_compose_to_tonight_plan.py` (0318) |
| Mark seat Y? | **No** until Lane B ship ADR + Continuous Runtime |
| Reopen compose packaging? | **No** unless Ideal/honesty defect |
| Optional next language work | Lane A finiteize extend; other P3 — not more compose Host demos |

---

## 4. Language-design findings (ranked)

### P0 — Mid-program Continuous type world (blocked)

Ideal seats require `Continuous` as a distinct type with hard gates. **Not**
unsealed by ADR 0185. Opening is Architecture Path + ship ADR only.

### P1 — Finiteize consumption of Continuous values

Even after Lane B, `finiteize` must accept Continuous (not only uniform
positional floats). Lane A MVP is intentionally thin (LISS-0313).

### P1 — Vocabulary split Theory bridge vs Host MC vs Ideal Continuous

Three continuous-adjacent stories. Expressiveness review treats unification as
Lane B family work, not silent merge under Lane A.

### P2 — S01 spine must not absorb Continuous

Tonight spine stays finite dialect. CH-field-* are **constellation / pre-inject**
seats — same rule as scorecard: one main is not the whole OS.

### P2 — Pedagogical Ideal chalk must stay marked Ideal

Agents must not treat Ideal Continuous snippets as Kernel Green permission.

---

## 5. Verification plan (expressiveness check procedure)

Use this checklist in Architecture / Feature reviews (same spirit as S01
expressiveness Phase 0):

1. **Seat exists?** Each Ideal continuous demand maps to a CH-field-* ID here
   or is explicitly rejected as improper.
2. **Ideal form written?** Blackboard-first snippet present (ADR 0095).
3. **Hard gates stated?** No measure / no QPU / explicit finiteize.
4. **Today path honest?** Lane A/Host substitute named; no fake Runtime Continuous.
5. **Class + action?** needs-ADR / extend finiteize / keep / keep-forbidden.
6. **Spine purity?** No CH-field Continuous forced onto `main_disaster_response.sqx`.
7. **Physicist sentence?** One sentence per seat matching Ideal form.

**Pass:** inventory complete; no silent Lane B claim; gaps Class-tagged.  
**Fail:** Ideal Continuous sold as shipped; or city-wide continuous QC seated as
proper demand.

---

## 6. Out of inventory (improper demand — recorded so not re-proposed as B)

| Claim | Why improper for Lane B | Prefer |
|---|---|---|
| 首都圏 80-cell cover | Scale = Host grid of finite jobs | locked scenario scale-out |
| Rolling replan frequency | Orchestration, not continuous type | Host jobs |
| One histogram inject | Single finiteize | Lane A / Host MC |
| Continuous city optimum | Anti-goal | forbidden |

---

## 7. Next gates (not authorized by this doc)

| Gate | Artifact | Status |
|---|---|---|
| Architecture Accept Lane B ship shape | [ADR 0204](../architecture/adr/0204-continuous-lane-b-type-world.md) | **done** (Accepted 2026-08-10) |
| Feature Plan investigation + Red Continuous type | Future LISS batch under ADR 0204 | not started |
| Finiteize Continuous-valued args | Feature after or with B (ADR 0204 Decision 4) | not started |
| S01 chapter `.sqx` for CH-field-* | Only after Runtime surface exists — until then Host demos + Ideal chalk | not started |

This document **authorizes documentation seats and expressiveness scoring only**.
