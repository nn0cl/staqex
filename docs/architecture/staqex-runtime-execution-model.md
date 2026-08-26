# Staqex runtime / compiler execution model

Status: **Working baseline** (2026-07-23). ADR **0032**.
Phase 3 DAG extraction: `compiler/staqex/ir/dag.py` (`staqex dag --dot`).
Deferred Pushforward MVP for eligible mains: [ADR 0140](decision-themes/dec-0005-quantum-operations-and-runtime.md).
GPU / data-parallel batching remains later-phase.

Audience: language implementers (compiler, runtime, VM, accelerator backends).

---

## 0. Thesis

Staqex has **no object-language `async`/`await`/Promise/Future**. Concurrency is
the **joint / mixture model**. The implementer’s job is therefore **not** to
build a classical async scheduler — it is to:

1. Lower pure programs to a **computation DAG**,
2. **Defer** materialization until terminal `measure` (or forced inspect),
3. Evaluate independent support atoms as **data-parallel** batches (SIMD/GPU/…),
4. Attach host I/O only at **lift / sink / snapshot / inspect** boundaries.

Axiom beauty → runtime simplicity: no function colouring, no per-task futures.

---

## 1. What classical async forces (and Staqex avoids)

| Classical async cost | Staqex stance |
|----------------------|-------------|
| Coroutine / state-machine transform | Unnecessary for pure evolution |
| Heap Future/Promise per task | One joint / support buffer (reuse) |
| Event loop + worker pool for *compute* | Vector kernels over supports |
| Function colouring (`async` infection) | Entire pure region is one colour |
| Locks / races | Immutable pushforwards — structurally race-free |

Host adapters may still use `io_uring` / `epoll` for **boundary** file reads
(ADR 0029). That is not programmer-visible async colouring.

---

## 2. Pipeline under the hood

### 2.1 Compile / lower — build a DAG (no execute)

While the programmer writes `mix` / `map` / `step`, the engine **need not**
evaluate. It records dependencies:

```text
sys0 ── mix ─┬─▶ worldline_A.step ─┐
              └─▶ worldline_B.step ─┴─▶ sys_final
```

IR nodes align with AST (`WhenExpr`, `Map`, `Project`, `Interfer`, `Call`, …)
plus fusion / trace-out rewrites (ADR 0022).

### 2.2 Runtime — evaluate at the boundary

On `measure sys_final` (ADR 0027):

1. Run DAG opts (fusion, merge/prune, trace-out).
2. Materialize the joint / marginal needed for the measured expression.
3. **Data-parallel apply** independent atoms (AVX / GPU / …) — not
   thread-per-worldline context switches.
4. One `RngPort` sample → Dirac → `MeasureSinkPort`.

`inspect` / `snapshot` may force a **read** of the current table without
sampling (ADR 0030 / 0029) while leaving the joint intact.

### 2.3 I/O wait (boundary only)

```text
File.readAsState  →  OS async I/O (io_uring/epoll)  →  inject Dirac/State root
        ↓
   pure DAG build / batch eval   (no I/O in the middle)
        ↓
measure … to Sink
```

---

## 3. Implementer advantages

| Concern | Classical `async` VM | Staqex engine |
|---------|----------------------|-------------|
| Context switch | Task switches thrash caches | Batch over vectors |
| Alloc | Per-future heaps | Arena / one support buffer |
| Deadlock | Possible | Structurally absent in pure region |
| Accelerators | Hard to map Promise graphs | Natural tensor/SIMD/QPU offload |

---

## 4. What the runtime must still implement

- Joint / PMF (then amplitude) store and pushforward kernels.
- DAG builder + ADR 0022 passes.
- Ports: `RngPort`, sinks, `StateSourcePort`, inspect sink.
- Optional: GPU/SIMD backends behind the same denotation.
- **Not required for MVP:** Promise runtime, async colouring, green threads
  for object-language compute.

Kernel PoC A/B may evaluate **eagerly** and still be correct; deferred DAG +
SIMD are performance profiles, not semantic requirements (ADR 0022).

---

## 5. Non-goals

- Exposing `async`/`await` in Staqex source “for familiarity.”
- Per-worldline OS threads as the primary execution strategy.
- Mid-pure blocking I/O APIs.

## 5.1 Host execution lifecycle (proposed ADR 0065)

The runtime's pure evaluation model is distinct from the host execution
lifecycle. Local simulation and remote QPU execution are both represented by a
host `Job`; Staqex source does not contain Job/Task operations.

```text
submit(program) -> Job -> status / wait / result / cancel
run(program) -> JobResult       # blocking convenience
```

`JobResult` is an opaque host DTO containing measurement envelopes and
execution metadata. It does not expose the internal Joint, AST, or simulator
buffers. A completed result implies that `main`, terminal measurement, and
result persistence have completed.

---

## 6. Open questions

- Default backend order (CPU scalar → SIMD → GPU).
- When inspect forces materialization vs printing symbolic DAG.
- Batching strategy for `evolve` loops vs one-shot measure.
