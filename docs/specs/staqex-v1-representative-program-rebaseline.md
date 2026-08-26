# Staqex representative-program plan (rebaseline, 2026-07-31)

| Field | Value |
|---|---|
| Status | **Accepted** (2026-07-31) — P0+P1 complete; P2 locked; S0 ready; Option B complete; **S1 complete** (LISS-0134; PR pending) |
| Supersedes | [`staqex-v1-noether-forge-review-plan.md`](staqex-v1-noether-forge-review-plan.md) (Slice A–D execution record retained historically) |
| Related Issue | [LISS-0120](../issues/LISS-0120-representative-program-language-review-gate.md) — **rejected / deferred** pending prerequisites |
| Successor Issues | Gate P0/P1 complete. P2: [LISS-0126](../architecture/documentation-compression-map.md) (**complete**). S0: [LISS-0127](../architecture/documentation-compression-map.md) (**complete**, docs). S1: [LISS-0134](../issues/LISS-0134-showcase-s1-thin-slice.md). S2+ = new ID (do not reuse LISS-0120) |
| North-star lens | [Physicist × DX harmony](../architecture/physicist-dx-harmony.md); Clean Architecture / DDD in `AGENTS.md` |
| Friction evidence | [physicist-source-friction-ledger.md](../architecture/physicist-source-friction-ledger.md) |
| Mission lock | [staqex-v1-showcase-mission-lock.md](staqex-v1-showcase-mission-lock.md) |
| S0 spec | [staqex-v1-showcase-s0-disaster-response.md](staqex-v1-showcase-s0-disaster-response.md) |

```markdown
[DESIGN CHECK]
- Scope: reformulate the representative-program path so Staqex meets the
  joint professional standard of research physicists and senior DDD/CA
  engineers — including hard prerequisites and rejection of premature
  LISS-0120.
- Not in scope: implementing the showcase, fixing all examples in this
  document, accepting Open Topics by silence.
- Joint standard: blackboard-direct physics reading AND bounded contexts,
  ports, fail-closed diagnostics, no hidden policy in adapters (see
  physicist-dx-harmony).
- Ambiguity: concrete scientific mission theme for the showcase remains
  Adjudicator-chosen after prerequisites; coverage table rows need inventory.
- Verification: docs sync; no .sqx/compiler changes in this docs packet.
```

## 0. Why rebaseline

LISS-0120 assumed a representative sample could review the language once IR
gates opened. Adjudicator review found the opposite prerequisites missing:

1. **Language surface is not “all closed.”** Core Kernel is shipped, but Open
   Topics and honest “in / out of v1 review” boundaries were not locked.
2. **`examples/basics` and `examples/applied` are not reliably exemplary.**
   Many entries run with `compile.ok == False` (often LINEAR), and some fail
   at runtime. A showcase built on that baseline confuses language defects,
   sample debt, and review judgement.
3. **Physicist × DX harmony is not proven by line count or module trees.**
   It is proven when source is scientifically legible and architecturally
   maintainable under the same meaning.

Therefore LISS-0120 is **rejected for continuation as the active review
gate**. Work already shipped (plans, A11 prototype attempts, IR deps) remains
historical evidence, not authorization to proceed.

## 1. North star — Physicist × DX harmony (normative)

Authoritative framing:
[`physicist-dx-harmony.md`](../architecture/physicist-dx-harmony.md).

The representative program exists to make this **joint professional
standard** reviewable:

> Staqex expresses research-grade physical models and experimental intent
> directly, while preserving Clean Architecture / DDD discipline at
> application scale: clear bounded contexts, ubiquitous language shared with
> the physics, ports at the boundary, and fail-closed diagnostics.

Neither audience is secondary. Physics reading is not “DX decoration,” and
software structure is not “enterprise noise on equations.”

### 1.1 Physicist criteria (research reading)

| Signal | Pass means |
|---|---|
| Domain directness | Source reads as model + protocol, not compiler choreography |
| State continuity | Joint / Never Leave the State is obvious in the mission spine |
| Honest capability | Unsupported realization is explicit (no fake QPU success) |
| Publishable intent | Symmetry, quench, observable, exactness obligations are named |
| Scientific ambition | Theme is credible on a quantum-machine research roadmap |

### 1.2 Software-architecture criteria (DDD / Clean Architecture)

| Signal | Pass means |
|---|---|
| Bounded contexts | Ownership directories match real responsibility, not quota folders |
| Ubiquitous language | Types share physicist vocabulary; no parallel DTO dialect in `.sqx` |
| Composition | `import` + constructors + small functions; every binding serves the mission |
| Ports | RNG / source / sink / future QPU behind ports; no provider SDK in sample |
| Fail-closed | Diagnostics name public rules; LINEAR and type errors are not normalized away |
| Reviewability | One mission spine; file/method size fit for human review |

**Reject criteria for the future showcase:** kitchen-sink syntax tourism;
padding; unlinked ownership trees; `compile.ok == False` treated as normal;
coverage that cannot state which surface is in scope.

## 2. Prerequisite program (must complete before a new showcase Issue)

### Gate P0 — Example health (basics first, then applied)

**Goal:** official examples are trustworthy teaching artifacts.

Minimum exit (Adjudicator may tighten):

1. Inventory every `examples/basics/**` and `examples/applied/**` entry point.
2. Classify each as: **green** (`compile.ok` + deterministic run), **amber**
   (runs but unclean diagnostics — must have Issue), **red** (runtime fail /
   missing modules).
3. Bring **all basics** to **green**, or mark retired with replacement pointer.
4. Bring **applied** to green-or-explicitly-deferred; no silent broken demos in
   the default catalog path (`QUICKSTART` links only to green).
5. Document LINEAR / multi-file / keyword landmines discovered while healing
   examples as language or docs Issues — do not hide them in samples.

Issue family (P0 start authorized; LISS-0119 **complete**):

| ID | Role |
|---|---|
| [LISS-0119](../architecture/documentation-compression-map.md) | Inventory — **complete** |
| [LISS-0122](../architecture/documentation-compression-map.md) | Basics heal — **ready** |
| [LISS-0123](../architecture/documentation-compression-map.md) | Applied heal/defer — **ready** |

### Gate P1 — Language coverage ledger (honest v1 boundary)

**Goal:** lock an honest v1 surface boundary for the showcase (what is in
scope, what is implemented, what is explicitly out).

Issue: [LISS-0124](../architecture/documentation-compression-map.md)
(**authorized**; not started). Deliverable: a coverage ledger (new spec or ADR
companion). Seed rows from
[`physicist-source-friction-ledger.md`](../architecture/physicist-source-friction-ledger.md)
(F-01…F-10) plus shipped surfaces. Table shape:

| Surface / concern | Status | Where proven today | In showcase? | Follow-up |
|---|---|---|---|---|
| e.g. `when`, `evolve for`, `class`/`init`, static QPU lane, … | shipped / partial / open | Bxx / SV / none | required / optional / out | Issue/ADR |

Rules:

- Open Topics from agent contracts are either **scheduled for implementation**
  before the showcase, or **explicitly out of showcase scope** with physicist-
  readable rationale (not “later maybe”).
- “All syntax” for the showcase means **all rows marked required**, not every
  historical ADR fantasy.
- Programmer rows include ports, diagnostics, module visibility, linear
  resources — not only grammar tokens.

### Gate P2 — Mission selection (only after P0+P1)

Pick one ambitious finite mission that:

- meets research-grade scientific credibility for its domain;
- is structured as a real bounded-context application under Clean
  Architecture / DDD reading;
- can declare simulator vs static-hardware honesty without false success;
- stays finite (no hidden continuous discretization in v1 showcase).

**Default scientific theme — LOCKED 2026-07-31:** finite quantum-matter
discovery (Noether Forge lineage) — quench + symmetry + magnetization /
correlation evidence + provenance dossier — **rewritten as one mission spine**,
not a type museum. See
[`staqex-v1-showcase-mission-lock.md`](staqex-v1-showcase-mission-lock.md).

Alternates (observatory networking; Lindblad-first) are **rejected for this
lock**; require a new Adjudicator scope approval to reopen.

## 3. Showcase construction plan (after P0–P2)

Call this **Phase S** (showcase). New Issue ID after reclaim policy is set.

### S0 — Showcase specification (docs-only)

- Mission problem statement in one paragraph (physicist) + context map
  (programmer).
- Coverage ledger subset: which required rows the showcase must exercise.
- Module map by bounded context; entrypoint naming (`main_<mission>.sqx`).
- Joint rubric (extend §1) with evidence artifacts (source citations, IR
  traces, example-green dependency).
- Non-goals: provider SDKs, live QPU credentials, padding, silent Kernel fixes
  inside the sample.

### S1 — Vertical thin slice (integrated Red→Green→Refactor)

One path: prepare → evolve → observe intent → terminal measure, **using**
domain/physics/application types for real values (duration, couplings, model),
`compile.ok`, multi-file `run_path`, no unused catalogs.

### S2 — Full mission scale

Grow coherently to the agreed size band (revisit 1k–3k only after P0 removes
pressure to pad). Every module participates in the mission spine or is deleted.

### S3 — Coverage completion + IR evidence

Close remaining **required** ledger rows inside the showcase or demote them
with Adjudicator approval. Keep soft Semantic / Physics IR evidence honest.

### S4 — Joint human review (Adjudicator)

Separate passes:

1. Physicist pass — §1.1  
2. Maintainer / CA pass — §1.2  
3. Friction ledger → Issues/ADRs only (no silent sample patches for language
   bugs)

## 4. Relationship to prior LISS-0120 artifacts

| Artifact | Fate |
|---|---|
| LISS-0120 Issue | **Rejected / deferred** as active gate; keep file for history + pointers |
| Noether Forge Slice A plan | Historical; superseded by this rebaseline |
| A11 tree / NF-E01 attempts | Optional salvage after P0; not authoritative until rewritten under S* |
| ADR 0108–0111, LISS-0082 | Remain prerequisites for IR honesty when S3 runs |

## 5. Execution order (summary)

```text
P0 example health  ──┐
                     ├──► P2 mission lock ──► S0 spec ──► S1..S4 joint review
P1 coverage ledger ──┘
```

No showcase Red/Green until **P0 and P1 are Adjudicator-accepted complete**
and **P2 mission is locked**.

## 6. Adjudicator decision points

- [x] Accept this rebaseline plan (Physicist × DX harmony; P0→P1→P2→S*).
      Accepted 2026-07-31.
- [x] Confirm LISS-0120 status **rejected / deferred** (not quietly continued).
- [x] Accept [ADR 0114](../architecture/decision-themes/dec-0002-state-first-semantics-and-measurement.md)
      (classical coefficient elaboration vs LINEAR; fold-invariant) —
      [LISS-0121](../architecture/documentation-compression-map.md)
      Phase 3 complete (2026-07-31).
- [x] Authorize starting **P0** (examples conformance) as the next
      implementation program — Issues filed:
      [LISS-0119](../architecture/documentation-compression-map.md) (**complete**),
      [LISS-0122](../architecture/documentation-compression-map.md) (**ready**),
      [LISS-0123](../architecture/documentation-compression-map.md) (**ready**).
      Authorized 2026-07-31. Inventory done; heal next.
      Named-coeff LINEAR no longer blocks B08; other residuals may remain.
- [x] Authorize starting **P1** coverage ledger (docs; may parallel after
      LISS-0119 exists) — Issue filed:
      [LISS-0124](../architecture/documentation-compression-map.md).
      Authorized 2026-07-31.
- [x] Defer mission finalization (P2) until P0+P1 exit.
- [x] **Lock P2 mission** (default quantum-matter / Noether Forge lineage) —
      [LISS-0126](../architecture/documentation-compression-map.md);
      [mission lock](staqex-v1-showcase-mission-lock.md). Locked 2026-07-31.
- [x] Publish **S0** showcase specification (docs only) —
      [LISS-0127](../architecture/documentation-compression-map.md);
[S0 spec](staqex-v1-showcase-s0-disaster-response.md).
- [x] Authorize **S1** vertical thin slice (Feature Path; [LISS-0134](../issues/LISS-0134-showcase-s1-thin-slice.md)) — authorized and shipped 2026-07-31 (PR pending).
- [x] Choose Option **B** (2026-07-31): selected Open Topics spec+ship before S1.
- [x] Complete Option B program (0129–0133, 0135).
- [ ] Authorize **S2** full mission scale (new Issue LISS-0136+).
- [x] Accept §7's two-phase examples/showcase benchmark role and the S02
      lineage connection. Accepted 2026-08-05.

## 7. Examples/showcase two-phase benchmark role, and the S02 lineage (2026-08-05)

**Terminology note:** "S02" below means the second *numbered showcase*
(the drug-discovery benchmark), not this document's own §3 "S0–S4" labels,
which name *phases of building one showcase mission* (S0 spec → S1 thin
slice → S2 full mission scale → S3 coverage completion → S4 joint review).
The two numbering systems are independent; do not conflate a showcase
named S02 with the "S2" phase above.

### The two-phase role

Examples/showcases are not a one-time deliverable that is finished once it
first compiles and runs. They serve two distinct, sequential benchmark
roles for the language, and are expected to be revisited for both:

1. **Current — language-expressiveness coverage.** Each showcase should
   push the language spec across a distinct real-world use case, testing
   whether it is genuinely expressive enough for that case — not merely
   whether some narrow slice of it compiles. This is exactly what §1's
   joint rubric and the [P1 coverage ledger](staqex-v1-language-coverage-ledger.md)
   already establish for S0/S1: required/optional/out rows per showcase,
   with Adjudicator approval needed to demote a required row rather than
   silently under-using the language.
2. **Future — real-hardware gap discovery.** When Staqex targets a real
   QPU backend, the same showcases get revisited and updated, and
   attempting real deployment is expected to surface language-spec gaps
   that the Python simulator cannot expose on its own.
   [ADR 0193](../architecture/adr/0193-dynamic-qpu-timing-region-intent.md)
   (dynamic QPU lane timing intent) is the first concrete instance of this
   role: the need for a backend-neutral timing-intent construct was
   identified by reasoning about what a showcase would require once real
   hardware execution is attempted — not by any gap the simulator-only
   Kernel itself exposed. A showcase is not "done" in the sense this
   section means until it has been through this pass at least once for
   any target it is expected to eventually run on.

### S02 lineage connection

This document's §4 already anticipated a successor: "S2+ = new ID (do not
reuse LISS-0120)." The [S02 drug-discovery benchmark](staqex-v1-s02-drug-discovery-benchmark.md)
(ADR 0190; [WP-0093](../work-plans/WP-0093-s02-language-expressiveness-and-selection.md))
is that successor. Its own document chain (design draft, accepted spec,
ADR 0190, WP-0093) never linked back to this rebaseline, to the
[coverage ledger](staqex-v1-language-coverage-ledger.md), or to the
[showcase mission lock](staqex-v1-showcase-mission-lock.md) — verified by
direct search; the omission was accidental, not a deliberate decision to
exclude S02 from this lineage. S02 is hereby formally part of the
representative-program lineage this document establishes, and is subject
to the two-phase role above.

**Not done by this entry:** populating S02's own row-by-row
coverage-ledger table (mirroring §1's friction-seeded surface table for
S0/S1) is separate, unstarted future work. This entry establishes the
connection and the operating principle; it does not itself constitute
that coverage inventory.
