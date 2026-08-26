# Staqex v1 language coverage ledger (Gate P1)

| Field | Value |
|---|---|
| Status | **Accepted** (2026-07-31) — Option B complete; typed surface shipped; QPU honesty catalog; **S1 complete** (LISS-0134) |
| Authority | [rebaseline](staqex-v1-representative-program-rebaseline.md) Gate P1; [friction ledger](../architecture/physicist-source-friction-ledger.md) |
| Issue | [LISS-0124](../architecture/documentation-compression-map.md) |
| Mission | [showcase mission lock](staqex-v1-showcase-mission-lock.md) (P2) |
| QPU honesty | [staqex-v1-qpu-capability-honesty.md](staqex-v1-qpu-capability-honesty.md) |
| Not | S2 without separate authorize; silent live QPU |

**2026-08-05 addition:** the [S02 drug-discovery benchmark](staqex-v1-s02-drug-discovery-benchmark.md)
(a numbered showcase, distinct from this ledger's own "S2" phase label
above) is formally connected to this Gate P1 lineage via
[rebaseline §7](staqex-v1-representative-program-rebaseline.md#7-examplesshowcase-two-phase-benchmark-role-and-the-s02-lineage-2026-08-05).
S02's own row-by-row entries in this ledger are not yet populated — that
remains separate, unstarted future work.

```markdown
[DESIGN CHECK]
- Scope: honest in/partial/out rows for showcase prerequisites.
- Seed: F-01…F-10 + shipped Kernel + Open Topics + ports/diagnostics/LINEAR.
- Ambiguity: “In showcase?” means default recommendation for the **locked**
  P2 mission; demotions still need Adjudicator approval.
```

## Legend

| Status | Meaning |
|---|---|
| **shipped** | Accepted + Kernel-usable for teaching / showcase |
| **partial** | Accepted intent with known residuals / soft obligations |
| **open** | Not accepted / not shipped (Open Topic or deferred ADR) |
| **axiomatic** | Intentionally restricted (Class A) — keep |

| In showcase? | Meaning |
|---|---|
| **required** | Future showcase must exercise or explicitly demote with approval |
| **optional** | May appear if mission needs it |
| **out** | Must not pretend shipped; omit or refuse honestly |

---

## 1. Friction-seeded surfaces (F-01…F-10)

| Surface / concern | Status | Where proven today | In showcase? | Follow-up |
|---|---|---|---|---|
| Classical `if` / `&&` / bare loops rejected; use `when` / `evolve` | **axiomatic** | B02; vocabulary Forbidden | required (teach `when`) | keep; pedagogy only |
| Named `Float` / struct field coeffs in `Operator` | **shipped** | ADR 0114; LISS-0121; B08 | required | none (F-02/F-05 closed) |
| Many-body binders `sum`/`product` + `Index<…>` | **shipped** | ADR 0096; LISS-0055 | optional | width/QASM hygiene as sample debt |
| Dirac paper spelling `⟨φ\|ψ⟩` | **partial** | `inner`/`outer` (ADR 0087) | optional | sugar later; function form OK |
| `expect` / `inspect` choreography | **shipped** | B04/B08/A06 | required | teach ≠ measure |
| Typed surface `state x: State<Int>` | **shipped** | ADR 0115; LISS-0129 | required | — |
| Density / Lindblad general CPTP | **partial** | ADR 0057; LISS-0131 boundary | optional | no full-CPTP claim |
| `evolve until` | **shipped** | ADR 0079; LISS-0012; axioms | optional | — |
| Continuous PDF / Monte Carlo | **open** | reopened — design ADR | **design** | [permanent-out reopen](staqex-v1-open-topics-permanent-out.md) |
| SI scale beyond (L,M,T) | **partial** | base $I$,$\Theta$ (0121); explicit `to` through 0151; mixed promote 0155; residual atomic mass / display-unit | **shipped** + residuals | ADR 0121–0155 |
| Exact rational masses | **open** | reopened — design ADR | **design** | ADR 0076/0097 constrain runtime |
| Multi-file `import` / modules | **shipped** | B09; A06; A11 | required | — |
| QPU / OpenQASM lanes | **partial** | B10; CH0; [honesty catalog](staqex-v1-qpu-capability-honesty.md) | optional | live provider **out** |
| Soft `QSEM_*` obligations | **partial** | most green samples | optional | honesty, not failure |

## 2. Shipped language core (required baseline)

| Surface / concern | Status | Where proven today | In showcase? | Follow-up |
|---|---|---|---|---|
| `state` / Never Leave the State + terminal `measure` | **shipped** | B01; axioms | required | — |
| Ket literals + `evolve … under … for/times` | **shipped** | B04; ADR 0037 | required | — |
| Operator algebra + Suzuki | **shipped** | B08 | required | — |
| `namespace` / `enum` / `struct` / `class` / `fn init` / visibility | **shipped** | B07; A06; ADR 0054–0056, 0058 | required | — |
| LINEAR resource discipline (true quantum) | **shipped** | LISS-0114; green samples; LISS-0133 | required | — |
| Ports: RNG / Source / MeasureSink | **shipped** | Kernel runtime | required (architecture) | no provider SDK in showcase |
| Diagnostics fail-closed | **shipped** | LINEAR / TYPE / MODULE codes | required | — |
| Soft Physics / Semantic IR | **partial** | LISS-0082; A11 | optional | honest soft only |

## 3. Open Topics — Option B + permanent-out reopen (2026-07-31)

Authority: [permanent-out reopen](staqex-v1-open-topics-permanent-out.md)
(LISS-0152); [program](staqex-v1-open-topics-before-s1-program.md).

| Topic | In showcase? | Status note |
|---|---|---|
| Typed surface annotations | **required** | **shipped** (ADR 0115 / LISS-0129) |
| `evolve … until` | **optional** | **shipped** (ADR 0079 / LISS-0012) |
| ADR 0057 density / Lindblad | **optional** (toy OK) | Runtime complete; boundary [LISS-0131](../architecture/documentation-compression-map.md) |
| Further `\|>` / currying | **partial** | Unary/Partial/hole-fill; ADR 0022 MVPs; affine + Call/Partial Fusion (0141/0143); sequential multi-hole (0149); tuple simultaneous (0152); residual poly≥2 / GPU DAG |
| Further trait `impl` / effect rows | **parked** | Core shipped (ADR 0081–0082); surface examples **accepted, no ship ADR** ([LISS-0196](../architecture/documentation-compression-map.md) / [examples](staqex-v1-trait-effect-surface-examples.md)); no Kernel Red until a future ship ADR |
| SI beyond (L,M,T) | **partial** | Base $I$,$\Theta$ + explicit `to` through 0151 + mixed promote 0155; residual atomic mass / display-unit / bare `.ton` |
| Continuous PDF / Monte Carlo | **design** | Reopened; Kernel continuous value not yet Accepted |
| Exact rational vs f64 | **design** | Reopened; ADR 0076/0097 constrain |
| Concrete live QPU IR | **design** | Reopened Architecture Path; see [QPU honesty](staqex-v1-qpu-capability-honesty.md) |

## 4. Known residuals (not showcase blockers if demoted)

| Residual | Status | Follow-up |
|---|---|---|
| Consume-on-return LINEAR on product/apply chains | **closed** | LISS-0133 |
| Namespace/`Float` method return runtime bind | **closed** | LISS-0133 |
| Soft `MULTI_REGISTER_INDEX_AMBIGUOUS` false positive | **closed** | LISS-0133 |
| Classical Type-First ⊕ State arithmetic | **closed** | ADR 0116 / LISS-0133 |
| Sample hardcode params beside unused structs | Class E | style guard remains |

## 5. Gate implication

- **P0 examples health:** complete.
- **P1:** Option B **complete** — typed surface shipped; permanent-out recorded;
  residuals closed (LISS-0129/0130/0131/0132/0133); QPU honesty catalog
  (LISS-0135).
- **P2:** mission locked.
- **S1:** ready for Adjudicator authorize (new Issue LISS-0134+).
