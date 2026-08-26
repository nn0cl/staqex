# Physicist source-friction ledger (Kernel as of 2026-07-31)

| Field | Value |
|---|---|
| Status | **working ledger** — evidence-backed; not an ADR; not implementation approval |
| North star | [Adjudicator language vision](adjudicator-language-vision.md); [Physicist × DX harmony](physicist-dx-harmony.md); [axioms](staqex-language-axioms.md); [ADR 0095](decision-themes/dec-0003-language-surface-and-physicist-first-dx.md) |
| Companion plan | [representative-program rebaseline](../specs/staqex-v1-representative-program-rebaseline.md) (P1 coverage ledger consumes this) |
| Authority | Compile/run probes on Shipping Kernel `compiler/staqex/` + accepted ADRs; sample inspection |

```markdown
[DESIGN CHECK]
- Scope: answer whether writing Staqex source today forces equation breakage
  or coding away from a research physicist's mental model; document honestly.
- Not in scope: fixing Kernel; accepting Open Topics; reclaiming LISS-0120.
- Evidence: compile_source / run_source probes (2026-07-31) + ADR 0087/0095
  + applied sample A06/A11 patterns.
- Ambiguity: which frictions are axiomatic (keep), sugar gaps (ship later),
  or bugs (fix under Issues) — Adjudicator classifies for P1.
```

## 0. Direct answer

**Partially yes — but distinguish carefully.**

Classical control rejection (F-01) protects physics. Canonical binder *shapes*
(ADR 0096 / LISS-0055) largely parse today. **Named couplings / struct fields
into `Operator`** (F-02, F-05) are **closed** for Type-First `Float` and
`OpAttr` field sugar under ADR 0114 + LISS-0121 (2026-07-31). Residual sample
debt (hardcoded literals beside unused param structs; B08 other LINEAR sites)
is Class E / P0 hygiene, not a language block on the everyday coupling spelling.

Sample workarounds that hardcode literals beside unused param structs (A06)
are Class E debt and must not become style.

| Class | Meaning | Stance |
|---|---|---|
| **A — Axiomatic discipline** | Language rejects classical control / early collapse so the *physics* mental model (Never Leave the State) stays intact | Keep; teach, do not “fix” into `if` |
| **B — Sugar / composition gap** | Physicist can write the idea, but not with the natural spelling that mirrors the paper | Track for P1; Issue or ADR |
| **C — Bug / incomplete ship** | Accepted surface promised, Kernel does not deliver or mis-diagnoses | Fix under Feature Issues; do not paper over in samples |
| **D — Open Topic** | Not accepted / not shipped; writing it forces a detour or omission | Explicitly out until scheduled |
| **E — Sample debt** | Official example codes around the gap, teaching the wrong habit | P0 example health |

The industry pattern “beautiful equation → awkward DSL → port to QPU” is
**exactly what Class B/C/E recreate inside Staqex** if left undocumented.
Class A is the opposite: it asks physicists to drop *classical programmer*
habits, not physical ones.

## 1. What already aligns (do not over-claim friction)

These read close to the board when used as intended:

| Surface | Example | Note |
|---|---|---|
| Ket literals + evolve | `state psi = \|+>`; `evolve psi under H for t` | Matches Schrödinger narrative |
| Operator algebra (literals) | `Operator H = Z + 0.25 * X` | Compiles and runs (probe 2026-07-31) |
| Indexed Paulis outside binders | `Z[0] * Z[1]`, `X[0] + X[1]` | B08 teaching shape |
| `when` mixtures | B02 | Physics-linear alternative to `if` |
| Terminal `measure` only | axioms + vocabulary | Collapse boundary is explicit |
| `namespace` / `enum` / `struct` / `class` | B07, A06 domain files | Physics reading exists (harmony table) |
| Function-shaped Dirac algebra | `inner`, `adjoint`, … (ADR 0087) | Verbose than ⟨φ\|ψ⟩, but typed and parser-safe |

Soft Semantic IR notes (`QSEM_*`) on many programs are **IR honesty
obligations**, not “the equation is wrong.” Treat separately from source
friction unless a sample treats them as normal silence.

## 2. Friction inventory (source-writing stage)

### F-01 — Classical `if` / `&&` / loops forbidden (Class A)

- **Physicist expectation (classical code habit):** branch on a bit, short-circuit.
- **Staqex:** `if`, statement-level `&&`, `while`, bare `for` are forbidden; use
  `when` / `evolve`.
- **Carve-out (LISS-0141):** binder `where` predicates may use `&&` to chain
  static index comparisons (e.g. `where i < j && j < k`). That is compile-time
  comprehension filtering, not classical control in the experiment script.
- **Evidence:** `FORBIDDEN_KEYWORD` / lex-or-parse error on statement `&&`;
  binder `&&` accepted after LISS-0141.
- **Equation impact:** none for unitary narratives; **coding impact:** high for
  anyone importing classical control flow into the experiment script.
- **Judgement:** axiomatic for classical control; binder `&&` is accepted sugar
  for mathematical constraints.

### F-02 — Parameter packs compose into Hamiltonians (Class C → **closed for named Float + field OpDSL**)

Physicists write \( H = h_x X + \ldots \) with \(h_x\) from a parameter object.

| Spelling | Result after LISS-0121 |
|---|---|
| `Operator H = c.h_x * X` | **OK** (`OpAttr` → OpLit elaboration) |
| `Float hx = c.h_x` then `Operator H = hx * X` | **OK** (Classical; no LINEAR on `hx`) |
| `Operator H = 0.25 * X` (literal) | **OK** |

- **Closed by:** [ADR 0114](decision-themes/dec-0002-state-first-semantics-and-measurement.md) +
  [LISS-0121](documentation-compression-map.md)
  (2026-07-31).
- **Residual (E):** older samples that still hardcode literals beside unused
  param structs remain sample debt under P0 — not a language block.

### F-03 — Many-body binders: design largely decided; residual is not “mystery”

**Correction (2026-07-31):** an earlier note called “ADR 0095系 Hostile” after
probes used illegal domains (`0..1` instead of `Index<0..N>`), which produced
blanket `PARSE_ERROR` and overstated the gap. Re-probe with the accepted
surface:

| Physicist form | Kernel today (`Index<0..N>`) | Kind |
|---|---|---|
| Ising nearest-neighbour `sum { -1.0 * Z[i]*Z[next(i)] }` | **Parses / typechecks** | mostly shipped (LISS-0043/0052/0055) |
| Heisenberg `sum { X[i]X[next(i)] + Y[i]Y[next(i)] }` | **Parses / typechecks** (`+` in body) | shipped by LISS-0055 / ADR 0096 D2 |
| TFIM as `sum{…} + sum{…}` | **Parses / typechecks** | shipped composition path |
| `product (i in …)` | **Parses / typechecks** | ADR 0096 D10 path |
| `Z(k)` vs `Z[k]` | **`Z(k)` retired** → write `Z[k]` | design gap closed |
| Named `Float J` then `J * Z[i]*…` in binder | **OK** (Classical; no LINEAR on `J`) | closed by ADR 0114 + LISS-0121 |
| Indexed `Float[N] J` then `J[i] * Z[i]*…` | **OK** (LISS-0143 / WP-0032) | 1D vector |
| ND `Float[N][M]…` then `h[p][q]…` | **OK** (LISS-0144 / WP-0033) | Kernel literals; Host tensors deferred |
| `sum (i in Basis<N>)` | **OK** (LISS-0148 / WP-0035) | Computational-basis labels; not Index coercion |
| `Float[M…] row = h[i]` partial | **OK** (LISS-0149 / WP-0035) | Static literal prefix; scalar binder still full-rank |
| `Float[…] h = host("h")` | **OK** (LISS-0150 / WP-0036) | In-memory Host CoefficientTensor overlay |
| `cqft(ctrl, reg)` | **OK** (LISS-0151 / WP-0036) | Exact single control; approx QFT still out |
| Compound `where i < j && …` / `\|\|` | **OK** (LISS-0141 / LISS-0145) | binder-only; statement control still forbidden |
| `Index<0..register-1>` / `Index<i+1..…>` | **OK** (LISS-0146 / ADR 0117) | static endpoints |
| `rev(Index<a..b>)` | **OK** (LISS-0147) | descending enumeration |
| Evolve under lowered binder | can fail wire/bind mismatch if state width ≠ op width | execution hygiene, not chalk spelling |

ADR 0095 itself is the **ideal-form principle**, not a binder feature ADR.
Binder final form is **ADR 0096** (+ 0088 historical). ADR 0095’s original
evidence table mixed bugs / deferrals / one design gap; most design rows were
later decided. The former “named classical coefficients as linear” residual
(F-05) and field-into-Operator residual (F-02) are **closed** for Type-First
`Float` + `OpAttr` (ADR 0114 + LISS-0121). Occasional **run/QASM / width**
hygiene and unrelated B08 LINEAR sites remain P0 sample debt — not a
philosophical conflict between physicist and programmer.

### F-04 — Dirac paper spelling vs function calls (Class B → **sugar shipped**)

- Paper: \(\langle\phi\|\psi\rangle\), \(\|\psi\rangle\langle\phi\|\).
- Kernel teaching default: `inner(phi, psi)`, `outer(psi, phi)` (ADR 0087).
- Dual-accept paper sugar (ADR 0165 / ship ADR 0169 / LISS-0234): identifier
  interiors desugar to `Var` in `inner` / `outer` / `projector` Calls;
  numeric/`+`/`-` labels stay `BraLit`/`KetLit` (LISS-0073). Alone named
  `\|psi⟩` remains a label ket, not a Var binding.
- **Equation impact:** low after sugar (chalk ≈ Call semantics).
- **Stance:** Call form remains the documented teaching default.

### F-05 — Linear resource discipline on classical couplings (Class C → **closed for Type-First Float**)

- After LISS-0121: `Float J = 1.0` used as `J * Z[i] * Z[next(i)]` → **no**
  `LINEAR_IMPLICIT_DISCARD` on `J` (Classical elaboration coefficient).
- True quantum `state` leftovers still emit LINEAR (regression guarded).
- Misuse as `when` / `measure` → fail-closed
  (`COEFFICIENT_IN_QUANTUM_POSITION` / measure messaging).
- **Closed by:** [ADR 0114](decision-themes/dec-0002-state-first-semantics-and-measurement.md)
  (**Accepted**) + [LISS-0121](documentation-compression-map.md)
  (**Phase 3 complete**, 2026-07-31).
- **Residual (E):** B08 / other samples may still fail for **unrelated** LINEAR
  sites; heal under P0 — do not reopen F-05 as “coefficients are quantum.”

### F-06 — Expectation / inspect choreography (Class B) — **guidance locked**

- Board: “look at \(\langle Z\rangle\)” mid-protocol without collapsing \(\psi\).
- Kernel pattern: `state m = expect(Z, psi)` then `inspect(m)`; terminal
  `measure psi` still required for the spine.
- **Ruling (WP-0078 / LISS-0219):** docs-only — `inspect` ≠ `measure`. Guidance in
  [`physicist-dx-harmony.md`](physicist-dx-harmony.md) and
  [`examples-catalog-conventions.md`](../collaboration/examples-catalog-conventions.md).
  No rename / diagnostic surface change without a new ADR.
- Audit note: Showcase S01 / matter-discovery use many `viewed_* = inspect(...)`
  bindings; treat as non-collapse views, not readout.

### F-07 — Typed surface annotations (Class D) — **closed**

- Desired: `state x: State<Int> = …` — **shipped** ADR 0115 / LISS-0129.
- Type-First `State<T> x = …` and inference-only `state x = …` remain legal.

### F-08 — Open systems / continuous / SI / overload (Class D)

From Open Topics and stance memos (not re-probed exhaustively here):

| Topic | Source effect today |
|---|---|
| Density / Lindblad (ADR 0057) | Mixed-state experiments need partial / deferred surface |
| `evolve until` | **Shipped** (ADR 0079 / LISS-0012); prefer `for`/`times` in pedagogy when simpler |
| `\|>` / currying | Pipeline experimental programs detour |
| SI beyond (L,M,T) | Dimensionful equations stay tagged-toy |
| Continuous PDF / Monte Carlo | Continuum models cannot be honest Kernel programs |
| Exact rational masses | Probabilities look like `f64` numerics — **decided out 2026-08-10**: ADR 0125/0076/0097 design boundary reconfirmed; classical-path rationals already shipped (ADR 0160), Joint/PMF masses stay `f64` |
| No user operator overload | **Decided out** — [ADR 0114 §D5](decision-themes/dec-0002-state-first-semantics-and-measurement.md); Domain `add`/`eq` named methods — not chalk `+` on arbitrary types |

### F-09 — Multi-file / import landmines (Class C/E) — **mostly healed**

- A06 historical `MODULE_NOT_FOUND_ERROR` probe is **superseded** — official
  multi-file applied mains use relative + selective import (ADR 0177/0183;
  LISS-0289/0291/0296); seed-0 `main_topological_edge_memory` is green.
- Residual risk remains if authors invent unlinked trees: import ceremony is
  software architecture, not physics (A11 NF-E01 history). Prefer selective
  braces over bare module imports (LISS-0299).

### F-10 — QPU / circuit lane vocabulary (Class B when used) — **guidance locked**

- Static/parametric QPU surfaces (`QubitRegister`, `apply`, `Param`) are a
  **second dialect** beside Hamiltonian `evolve`. Honest when the mission is
  circuits; corrosive when a many-body paper is rewritten as gates “because
  that is what runs.”
- **Ruling (WP-0078 / LISS-0219):** written lane-choice rule — Hamiltonian source
  → `evolve`; circuit mission → circuit lane; cross-lane examples need Honesty
  notes. Same docs as F-06.
- Dynamic QPU remains capability-rejection first (ADR 0071).

### F-11 — Showcase S1 Kernel residuals (Class C; deferred Issues)

Discovered while shipping [LISS-0134](../issues/LISS-0134-showcase-s1-thin-slice.md)
(`examples/showcase/quantum_matter_discovery/`). Workarounds are in-sample;
do **not** silent-patch Kernel inside the showcase.

| Friction | Runtime symptom | Tracking |
|---|---|---|
| Return sparse-Pauli `Operator` from helper `fn` | was: unbound local scalar | [LISS-0136](../issues/LISS-0136-sparse-pauli-operator-return.md) **complete** (#180) |
| Method/field `Float` in Operator / `evolve for`; **param** `fn(J,h)->Operator` | was: unbound | [LISS-0137](../issues/LISS-0137-classical-float-operator-evolve-binding.md) **complete** (PR pending) |
| `Operator H = m.hamiltonian()` | was: empty tuple | [LISS-0139](../issues/LISS-0139-operator-method-call-return.md) **complete** (PR pending) |
| `when` arms with `\|0>` / `\|+>` | was: cannot evaluate KetLit | [LISS-0138](../issues/LISS-0138-when-ket-prepare-arms.md) **complete** (PR pending) |

Program plan: [hamiltonian-library-surface-plan](../specs/staqex-v1-hamiltonian-library-surface-plan.md).

Note: F-02’s “`Float hx = c.h_x` then `hx * X` OK” remains for simple OpDSL
probes; S1 still hit unbound paths for multi-site Pauli / duration — treat
0137 as a **remaining** elaboration gap, not a reopen of F-05 LINEAR.

## 3. Reading guide for Adjudicator

When asking “must the physicist leave their mental model?”:

1. **If the answer is Class A** — they leave *classical programming*, not
   physics. That is the product.
2. **If Class B/C** — Staqex is currently recreating industry equation-breakage
   *inside* the language. That is the debt P0/P1 exist to surface and schedule.
3. **If Class D** — do not pretend the showcase or Kernel already covers it.
4. **If Class E** — delete or rewrite the sample; do not cite it as harmony proof.

## 4. Minimal evidence log (2026-07-31 probes)

Recorded via `compiler.staqex.pipeline.compile_source` /
`run_source` on that day’s Kernel.

**Supersession note (2026-07-31 later):** rows that show `PARSE_ERROR` on
`c.h_x`, or `LINEAR_IMPLICIT_DISCARD` on named `Float` coefficients (`hx`,
`J`), are **historical**. They are closed for Type-First `Float` + `OpAttr`
by [ADR 0114](decision-themes/dec-0002-state-first-semantics-and-measurement.md) +
[LISS-0121](documentation-compression-map.md).
Re-probe before treating those rows as current Kernel behavior. B08 / A06
residuals **unrelated** to named coeffs remain P0 sample debt
([LISS-0119](documentation-compression-map.md) family).

| Probe | Outcome (historical unless noted) |
|---|---|
| `Operator H = Z + 0.25 * X` + evolve + measure | compile soft-ok; **run ok** |
| `Operator H = c.h_x * X` | **PARSE_ERROR** `.` — **superseded** (OpAttr) |
| `Float hx = c.h_x`; `Operator H = hx * X` | LINEAR on `hx` — **superseded** (Classical) |
| `Operator H = hx * X` with `Float hx = 0.25` | LINEAR on `hx` — **superseded** |
| binder with `Index<0..N>` Ising / Heisenberg `+` / `sum+sum` / `product` | **parse ok** (soft `QSEM_*`) |
| named `Float J` in binder body | LINEAR on `J` — **superseded** |
| `Z(0)` outside binder | **`RETIRED_OPERATOR_INDEX_SYNTAX`** → use `Z[0]` |
| illegal domain `0..1` (not `Index<…>`) | **PARSE_ERROR** (probe artifact; not “binder dead”) |
| `state x: State<Int> = coin()` | **PARSE_ERROR** |
| `a && b` | **LEX_ERROR** `&` |
| B08 file compile | **not ok** (`LINEAR_IMPLICIT_DISCARD`, …) — P0 residual |
| A11 `main_static.sqx` | soft-ok compile |
| A06 directory `run_path` | **MODULE_NOT_FOUND_ERROR** (historical) — **superseded**; selective/relative import face green (LISS-0296) |
| S1: return Pauli `Operator` from `fn` | **fixed** unbound scalar — [LISS-0136](../issues/LISS-0136-sparse-pauli-operator-return.md) |
| S1: `evolve for duration` from method Float | **RUNTIME** unbound `duration` — [LISS-0137](../issues/LISS-0137-classical-float-operator-evolve-binding.md) |
| S1: `when` ket arms | **RUNTIME** KetLit as value — [LISS-0138](../issues/LISS-0138-when-ket-prepare-arms.md) |

Re-run when Kernel changes; do not treat this table as eternal.

## 5. Post–WP-0088 / WP-0089 surface face (updated 2026-08-03; post LISS-0296)

| Friction | Class | Status |
|---|---|---|
| Package + `main` ceremony on single-file basics | E | **Healed** — default experiment profile (ADR 0182); markers dropped on official singles ([LISS-0291](documentation-compression-map.md)) |
| Selective / relative import unused in official samples | E | **Healed** — S01 + applied multi-file mains use relative + selective braces (ADR 0177/0183; LISS-0289/0291/**0296**) |
| Reverse-DNS `com.staqex.examples` | E | **Healed** — official root `examples.…` ([package-root-naming](package-root-naming.md)) |
| S01 DTO `class` forests | E | **Healed** for pure packs incl. nested boards + Operator drives (LISS-0277 / **0293–0294** / **0297**); keep `class` for interface systems (`RescueSquad`, `SupplyTruck`) |
| QMD (S1) enterprise face | E | **Healed** — selective import + free scores/Operator factories ([LISS-0298](documentation-compression-map.md)); mutable `DiscoveryModel` clock stays `class` |
| A06 inspect museum | E | **Healed** on main path; pure SSH scores free-fn (**0296**); mutable clock stays `class` |
| Local type inference / named struct / default profile / relative import | B→**shipped** | ADR 0180–0183 **Accepted** + Kernel; ty-fill residual [LISS-0290](documentation-compression-map.md) **complete**; B08 chalk + QASM |
| Dual `state` keyword vs `State<T>` vocabulary | B (docs) | Noted in QUICKSTART / basics README; not a bug |
| LINEAR + `tracing_out`, `when`, circuit soft-in-experiment | A | **Keep** — physics law / lane honesty |
| Free-fn Call with Type-First field objects | C | **Closed** — [LISS-0292](documentation-compression-map.md) classical free-fn path (not Joint param bind) |
| Nested free-fn under selective import | C | **Closed** — runtime frame + shadowing [LISS-0294](documentation-compression-map.md); transitive link Call + bare pipe stages [LISS-0295](documentation-compression-map.md) / **0299** |
| Operator free-fn + struct field coeffs | C | **Closed** — [LISS-0297](documentation-compression-map.md) binds free-fn object params under param names for OpAttr; S01 ConstraintDrive/Lattice → free factories; **B07** free `ising_hamiltonian` ([LISS-0300](documentation-compression-map.md)) |

## 6. Next documentation turns (suggested)

1. Fold remaining face rows into **P1 coverage ledger** as needed
   ([LISS-0124](documentation-compression-map.md)).
2. **Trait / effect expansion:** surface examples **accepted, no ship ADR**
   ([LISS-0196](documentation-compression-map.md)
   **complete**;
   [examples](../specs/staqex-v1-trait-effect-surface-examples.md)). No Kernel
   Red under ADR 0128 until a future ship ADR. **Reconfirmed 2026-08-10** —
   no new friction row added since 2026-08-03; "not now" stands.
3. Optional: further Operator free-fn edge cases (class receivers without intermediate Float, multi-level Attr).
4. **Pedagogy north star (Accepted 2026-08-02):**
   [physicist-minimal-dialect.md](physicist-minimal-dialect.md) gates example
   scoring and [S01 redesign](../specs/staqex-v1-s01-redesign-toward-minimal-dialect.md).
   Cut/demote inventory:
   [staqex-destructive-simplification-sketch.md](staqex-destructive-simplification-sketch.md).

## 7. Priority rule (normative for this ledger)

**Physicist vs programmer:** prefer the physicist’s mental model. Staqex is a
language for physicists. Programmer DX exists to scale that physics reading,
not to replace it with gate DSL habits or enterprise ceremony.

## 8. One-sentence summary

**Staqex already protects quantum continuity against classical control (F-01),
parses canonical binder shapes (ADR 0096 / LISS-0055), and accepts everyday
named-coupling / field-into-`Operator` spelling for Type-First coeffs
(F-02/F-05 closed via ADR 0114 + LISS-0121); residual sample debt is P0 hygiene.**
