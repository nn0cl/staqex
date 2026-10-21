# Optimistic quantum capacity horizon scenarios

## Status

**Draft architecture stress envelope. No delivery forecast or implementation
permission.**

Calendar-scenario amendment: 2026-10-21, requested by the Adjudicator.
The earliest challenge case is BQ-0 in 2028; the ambitious planning-center
band is 2029–2030. These are planning assumptions, not delivery predictions,
probability estimates, or a change to the proposed ADR's approval status.

This document deliberately accepts an optimistic viewpoint. It uses the
historical facility-computer-to-personal-computer curve for scale pressure, but
does **not** reuse its 35-year social-adoption delay. The quantum timeline begins
at a defined useful-computing breakthrough and assumes today's research,
capital, manufacturing, software-distribution, and public-awareness systems.
It then derives a quantum-supercomputer tier for the same future world.

The scenarios are design loads, not language limits or promises. The proposed
decision is [ADR 0110](decision-themes/dec-0006-host-qpu-and-external-ports.md).

## 1. Classical reference curve

Primary published reference points:

- ENIAC, introduced in 1946: approximately 5,000 operations per second,
  1,500 square feet, and 30 tons.
- IBM PC mass-market milestone, 1981: 35 years after ENIAC. This interval is
  historical context, not the adopted quantum diffusion interval.
- NVIDIA RTX 5090 household/enthusiast accelerator, 2025: a published headline
  value of 318 TFLOPS, 575 W board power, 32 GB memory.
- LineShine facility supercomputer, 2026: 2.198 HPL exaflop/s and approximately
  42.2 MW.

ENIAC's operation figure and the RTX headline TFLOPS figure are not equivalent
benchmarks. They are used only as an order-of-magnitude technology/adoption
curve:

```text
headline operation-rate ratio
  = 318e12 / 5_000
  = 6.36e10 over 79 years

equivalent annual factor
  ≈ 1.37

equivalent doubling interval
  ≈ 2.2 years
```

The current facility-to-household headline-performance ratio is approximately:

```text
2.198e18 / 318e12 ≈ 6.9e3
```

The power ratio is approximately:

```text
42.2e6 / 575 ≈ 7.3e4
```

Because the benchmarks differ, this supports a broad `10^4–10^5`
facility-to-household system gap, not a precision performance comparison or
an adoption schedule.

## 2. Breakthrough-relative projection method

BQ-0 is vendor- and modality-independent. Apollo and Starling are evidence
points, not prerequisites: another company or architecture may satisfy the
same useful-computing conditions first. A product launch, physical-qubit
count, or logical-memory result alone does **not** start the adoption clock.

The clock starts at `BQ-0`, the first publicly reproducible **useful quantum
computing breakthrough** satisfying all of:

- fault-tolerant work beats the best practical classical alternative on at
  least one economically or scientifically important workload;
- the result repeats across independent jobs with auditable error evidence;
- the machine exposes stable compiler/runtime contracts rather than a
  laboratory-only control script;
- modular replication and a credible manufacturing path exist;
- a developer ecosystem can build applications without inventing machine
  control for each experiment.

For arithmetic stress only, `BQ-0` is represented by a broad range:

```text
BQ-0 reference system
  logical carriers: 1e3–1e4
  sustainable logical operations per useful job: 1e10–1e12
```

These arithmetic reference values are not minimum qualification thresholds.
A smaller system can establish BQ-0 if it meets every useful-computing
condition above on an important workload. Conversely, reaching either
reference count does not establish BQ-0 without that evidence.

### 2.1 Evidence refresh and what moves (2026-10-21)

The following are dated first-party claims or goals, not joint achievements
of one composite machine. Their sources are listed in section 7.

| Evidence | Implication for this scenario | What it does not establish |
|---|---|---|
| IonQ, September 8: integrated Superion 256 QPUs fabricated and first ions trapped; customer deliveries planned for 2027 | Manufacturing and deployment are concrete preparation milestones | 256 working logical qubits, useful fault-tolerant computation, or BQ-0 |
| IonQ: 256 and 10K generations developed in parallel; CMOS-based fault tolerance targeted in a 2027 laboratory setting and manufacturable commercial form in 2028 | Include a 2028 early challenge case and prepare logical/physical and hybrid execution contracts before hardware arrival | Independent useful-workload verification or a guaranteed 2028 breakthrough |
| Quantinuum, October 19: Helios memory-error suppression with code distance; Apollo targeted for 2029 | Refresh the old 2030 Apollo research reference to the current 2029 company goal; track gates and complete computations separately from memory | A million arbitrary error-free gates or BQ-0 from memory fidelity alone |
| IBM, March roadmap: Starling targeted for client access in 2029, with 200 logical qubits and 100 million gates | Retain as a separate competing route, not the earliest possible BQ-0 date | A reason every other vendor must wait for 2029 |

Manufacturing acceleration, lower error rates, and hybrid integration address
different bottlenecks. Do not multiply their improvements into a fabricated
logical-performance result or count the same manufacturing acceleration again
in the post-BQ growth assumption.

### 2.2 Calendar scenarios, not a forecast

The calendar assumptions below implement the requested ambitious outlook.
2028 is the earliest challenge case selected for preparedness, not a proven
physical lower bound; 2027 or earlier is not declared impossible. The sources
do not justify assigning a probability to any of these cases.

| Scenario | Assumed BQ-0 | QP-1, BQ+3–5 | QP-2 and its QS-2 world, BQ+7–10 |
|---|---|---|---|
| Earliest challenge | 2028 | 2031–2033 | 2035–2038 |
| Ambitious planning center | 2029–2030 | 2032–2035 | 2036–2040 |
| Later qualification | 2031 or later | Recompute from actual BQ-0 +3–5 | Recompute from actual BQ-0 +7–10 |

Ranges spanning two possible BQ-0 years are unions, not the trajectory of
one machine. For example, BQ-0 in 2029 gives QP-1 in 2032–2034 and QP-2 in
2036–2039; BQ-0 in 2030 gives 2033–2035 and 2037–2040 respectively.
QS-2 is an architectural stress load in the assumed QP-2 world, not a
separately demonstrated facility-delivery forecast.

| Calendar preparation line | Staqex design obligation, not implementation permission |
|---|---|
| 2026–2027 | Preserve meaning, conformance and bounded current-machine witnesses while preparing provider-neutral capability and resource evidence |
| 2027–2028 | Prepare physical/logical resource distinction, hybrid CPU/GPU/QPU execution boundaries, and contracts for backends owning QEC/decoding |
| 2028 | Be ready for an early BQ-0 claim; require all qualification evidence before starting the clock |
| 2029–2030 | Planning-center BQ-0 band; support reproducible useful-workload comparisons and stable scientific workflows |
| 2031–2035 | QP-1 window across early/center cases; personal/research-lab accelerator workflows under the unchanged section 3 envelope |
| 2035–2040 | QP-2 window across early/center cases; also stress QS-2 partitioning, exact counts and compositional evidence |

If BQ-0 is later, dependent windows move with it; they are not fixed promises.
Readiness work may start earlier without claiming delivered hardware, selecting
a vendor/SDK, reopening completed work, or skipping per-feature approval.
Retain the post-BQ 12–18-month doubling assumption below, QP-1/QP-2 offsets,
power envelopes, failure criteria and capacity ranges in section 3.
Household cost, power and maintainability require their own evidence; a
data-center rack or foundry improvement does not prove household feasibility.

The previous document did not fix a calendar year for BQ-0. The conversational
old-center estimate of 2031 was retrospective, not a historical baseline.
This amendment therefore makes no measured claim of an exact one-year or
two-year acceleration.

The 79-year average above hides the semiconductor industry's fastest period.
Moore's original 1965 projection expected annual component-count doubling for
ten years; the historical record achieved approximately nine doublings in
that decade. The rate was revised toward two years only in 1975.

The adopted **golden-window envelope** therefore applies a 12–18-month
doubling interval to both logical capacity axes for the first ten years after
`BQ-0`. This is intentionally aggressive and is not a physical forecast:

```text
                       18-month doubling   12-month doubling
BQ+3 years                    4x                  8x
BQ+5 years                   10x                 32x
BQ+7 years                   25x                128x
BQ+10 years                 102x              1,024x
```

Household profiles receive only a fraction of frontier capacity. The shorter
timeline is an explicit scenario assumption: recognition, investment,
developer distribution, and global supply chains already exist when `BQ-0`
occurs. After BQ+10, no fixed exponential rate is assumed; profile revision
requires new evidence and architecture review.

## 3. Optimistic reference profiles

All figures are ranges and use logical, not physical, resources.

### QP-1 — Early Personal Quantum Workstation, BQ+3–5 years

| Axis | Stress-envelope value |
|---|---|
| Logical carriers | `10^3–10^5` |
| Sustainable logical operations per job | `10^10–10^13` |
| Parallel logical lanes | `10^2–10^4` |
| Aggregate job failure target | `<1%` |
| Implied average logical-operation failure envelope | approximately `10^-12–10^-15` |
| Deployment | local rack/workstation quantum accelerator |
| Power | `2–20 kW` |
| Interaction | local, low-queue, incremental compile/inspect/run |
| Host | ordinary CPU/GPU/storage plus quantum co-processor |

### QP-2 — Mature Household Quantum Computer, BQ+7–10 years

| Axis | Stress-envelope value |
|---|---|
| Logical carriers | `10^4–10^7` |
| Sustainable logical operations per job | `10^11–10^15` |
| Parallel logical lanes | `10^3–10^5` |
| Aggregate job failure target | `<1%` |
| Implied average logical-operation failure envelope | approximately `10^-13–10^-17` |
| Deployment | household tower/appliance or integrated local accelerator |
| Power | `0.5–2 kW` typical active envelope |
| Interaction | offline-capable, immediate local sessions, private local data |
| Modality | replaceable/upgradeable modules; model profile discovered at runtime |

This is intentionally optimistic. It assumes radical progress in physical
carriers, error correction, control, packaging, and energy efficiency.

### QS-2 — Quantum Supercomputer in the QP-2 world

Applying the current `10^4–10^5` facility/consumer system gap gives:

| Axis | Stress-envelope value |
|---|---|
| Logical carriers | `10^8–10^12` |
| Sustainable logical operations per campaign | `10^15–10^20` |
| Parallel logical lanes | `10^6–10^10` |
| Aggregate campaign failure target | `<1%` per declared critical region |
| Implied logical-operation failure envelope | approximately `10^-17–10^-22`, or stronger compositional proof |
| Deployment | globally or nationally distributed modular quantum facility |
| Power | `10–100 MW` facility envelope |
| Modules | `10^3–10^5` appliance-class or denser logical processing modules |
| Network | fault-tolerant entanglement fabric, hierarchical routing and scheduling |
| Host | exascale/post-exascale classical control, decoding, storage, and analysis |

At this scale, a "program" is a distributed campaign of verified plan
fragments, not one circuit file or one globally materialized instruction list.

## 4. Required compiler properties

The optimistic envelope is useful only if it changes design pressure.

### 4.1 No expanded-operation cardinality in core data structures

`10^20` operations cannot correspond to `10^20` DTO instances, IDs, source
records, or diagnostics. The compiler represents:

- templates and callable regions;
- exact symbolic multiplicity;
- parameterized instance paths;
- aggregate provenance;
- compositional resource and failure summaries;
- bounded, streamed, or partitioned materialization.

### 4.2 Exact large-count arithmetic

Counts such as `10^20` exceed unsigned 64-bit range. Resource values require an
exact arbitrary-precision or symbolic `ResourceMagnitude` contract.

Serialization uses canonical decimal strings or a reviewed symbolic schema,
not JSON numbers that may lose integer precision. Python may use built-in
arbitrary-precision integers; a future Rust implementation selects its numeric
representation through a separate dependency/technology review.

### 4.3 Failure arithmetic is compositional

Per-operation multiplication in ordinary floating point is insufficient as
the only model. Plans carry:

- critical-region failure budgets;
- compositional upper bounds;
- independence/correlation assumptions;
- log-domain, rational, interval, or other reviewed numeric evidence;
- explicit `Unbounded` when no proof exists.

This extends, rather than replaces, the Algorithm Plan error ledger.

### 4.4 Complexity is measured against compact plan size

Compiler validation and routine transformations should be polynomial in the
compact hierarchy/plan size, not in expanded operation count. A pass that must
expand a region declares:

- predicted output cardinality;
- memory/time budget;
- streaming/partition strategy;
- stopping/rejection behavior;
- provenance aggregation policy.

### 4.5 Local and supercomputer artifacts share formats

QP-2 and QS-2 use the same versioned semantic and plan-fragment contracts.
Differences are capability, partitioning, scheduling, fault tolerance, and
deployment—not source meaning.

## 5. Implications for language and user experience

The source language remains readable and does not expose `10^20` gate lines.

A user expresses:

- systems and acting spaces;
- equations, transformations, protocols, and observables;
- bounded/static semantic repetition;
- accuracy, failure, resource, privacy, and deployment intent through reviewed
  contracts;
- local-only or explicitly remote workflow policy.

The compiler reports:

- compact logical plan size and expanded estimate separately;
- whether the household target can execute locally;
- which requirement exceeds local capability;
- alternative plans without silently selecting one;
- what would be transmitted if remote execution is authorized;
- semantic, logical, and physical resource estimates separately.

## 6. Verification scenarios

Future deterministic tests should use synthetic target profiles:

- `QP1_REFERENCE`
- `QP2_REFERENCE`
- `QS2_REFERENCE`

They do not emulate the hardware. They verify that:

- large counts serialize exactly;
- no core pass allocates proportional to expanded operation volume;
- target rejection identifies the exceeded dimension;
- hierarchy and provenance survive partitioning;
- local insufficiency never triggers implicit remote fallback;
- the same semantic artifact can be replanned for QP-2 and QS-2.

## 7. Primary sources

- Computer History Museum, [ENIAC
  introduction](https://www.computerhistory.org/tdih/february/14/).
- IBM, [IBM PC history](https://www.ibm.com/history/personal-computer).
- Computer History Museum, [Moore's original annual-doubling decade and 1975
  revision](https://www.computerhistory.org/siliconengine/moores-law-predicts-the-future-of-integrated-circuits/).
- Intel, [Moore's Law historical
  summary](https://newsroom.intel.com/press-kit/moores-law).
- NVIDIA, [RTX 5090 published
  specifications](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5090/).
- TOP500, [LineShine 2026
  results](https://www.top500.org/news/lineshine-debuts-no-1-top500-enters-new-global-exascale-era/).
- IBM, [Quantum 2030 roadmap](https://www.ibm.com/roadmaps/quantum/2030/).
- IonQ, [Superion product-line announcement, September 8, 2026](https://www.ionq.com/news/ionq-launches-superion-product-line-industry-leading-upgradeable-platform-designed-to-scale-manufacturable-fault-tolerant-quantum-computing).
- Quantinuum, [Helios QEC results and Apollo goal, October 19, 2026](https://www.quantinuum.com/blog/quantinuum-closes-in-on-one-million-error-free-operations).

The 2026 sources inform section 2.1; the BQ-0 calendar cases in section 2.2
are Staqex scenario assumptions, not dates forecast or endorsed by those vendors.

## 8. Interpretation limits

- Classical and quantum operations are not equivalent units.
- Headline GPU TFLOPS and HPL exaflops are not equivalent benchmarks.
- Exponential curves cannot continue indefinitely.
- `BQ-0` is a capability gate, not a date or a single vendor milestone.
- Relative dates and values are optimistic architecture stress scenarios.
- The shortened diffusion interval is an explicit modern-ecosystem assumption,
  not a conclusion derived from ENIAC-to-PC history.
- Annual component-count doubling in semiconductor history does not prove
  annual logical-quantum-capacity doubling; it defines the requested
  golden-window stress envelope.
- The language has no minimum or maximum machine encoded from these profiles.
- Failure envelopes are simplified union-bound design pressures, not complete
  fault-tolerance analyses.
- The earliest challenge year is not an impossibility boundary; the planning
  center is not a probability-weighted forecast.
- Calendar updates do not promote synthetic future profiles to current device
  capabilities or change existing implementation/technology approval gates.
