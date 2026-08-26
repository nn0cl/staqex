# ADR 0194: Host input port and real `pairwise_compatible` / `diversity_at_least` Projector semantics

## Status

**Accepted** (2026-08-05) — Architecture Path decision, approved by the
Adjudicator. Acceptance approves the port shape and predicate semantics
defined below; it does not by itself authorize implementation — see
"Follow-up work required."

## Design check

- **Scope and expected behavior:** Give `project selection onto
  feasible(...)`'s `pairwise_compatible` and `diversity_at_least`
  predicates (ADR 0192, closed vocabulary already Accepted) real runtime
  semantics, alongside `exactly_selected` (which needs no new input and is
  covered by a separate, already-scoped Issue). These two predicates need
  data — which selection slots are compatible with which, and how diverse
  they are — that cannot come from the selection pattern alone and must
  never be candidate identity per the S02 spec's own rule ("Molecules and
  descriptors are not quantum states"). This ADR defines how that
  Host-computed, slot-indexed (never candidate-ID-indexed) structural data
  reaches the local `Evaluator`, and what the two predicates concretely
  compute once it is available.
- **Specifications and files inspected:**
  [S02 acceptance specification](../../specs/staqex-v1-s02-drug-discovery-benchmark.md)
  (Value model: candidate identity never becomes a Kernel value);
  [ADR 0192](0192-s02-projector-selection-semantics.md) (closed
  three-predicate vocabulary, Accepted; runtime execution explicitly
  deferred); [LISS-0322](../../issues/LISS-0322-s02-projector-region-semantics.md)
  (IR-lowering only, "Real Projector execution semantics... the Static
  Kernel does not execute S02 programs end-to-end yet"); the
  [kernel stub and placeholder registry](../kernel-stub-and-placeholder-registry.md)
  (`project ... onto feasible(...)` entry: runtime always crashes with
  `call cannot be classical value in Phase 2.2 value context`);
  `compiler/staqex/runtime/evaluator.py` (`project` op, line ~3797:
  confirmed the existing `PREDICATE_PROJECTOR_ERROR` guard in
  `unitarity_check.py` only rejects a literal `Lambda` AST node as
  `project`'s target — a closed-vocabulary `Call` like `feasible(...)`
  passes that check untouched and only fails later, at `_eval_value`, for
  lack of an implementation — so this ADR does not conflict with that
  guard's intent); `compiler/staqex/parametric_binding.py` (`Param<T>` /
  `parameter(...)`, ADR 0070/LISS-0027 — confirmed this binds only scalar
  QPU circuit parameters and is consumed exclusively by the QPU-circuit
  submission/backend path; grep of `runtime/evaluator.py` found **zero**
  references to `CircuitParameter` or `parameter(...)` binding — the local
  Joint simulator never reads it); `compiler/staqex/host.py`
  (`submit_source`/`_submit_compiled`: `Evaluator(seed=..., grid_hamiltonians=...,
  data_parallel_workers=...)` — confirmed no existing channel for
  Host-supplied structured classical data reaches the local evaluator
  today); `compiler/staqex/measure_sink_port.py` / `rng_port.py` (existing
  port shape convention: a `Protocol` + one or more adapters + a resolver
  function — the pattern this ADR's new port follows).
- **Component boundaries, ports/adapters, and VO/DTO candidates:** A new
  `HostInputPort` (Protocol, `compiler/staqex/host_input_port.py`) plus a
  `MappingHostInputAdapter` — the same shape as `MeasureSinkPort`/
  `TextIOMeasureSinkAdapter`. `Evaluator` gains a constructor-injected
  `host_input: HostInputPort | None` (dependency injection, matching how
  `stdout`/`seed` are already injected — no source-level syntax change).
  `host.py`'s `submit_source`/`run_source` gain a `settings["inputs"]`
  passthrough. A new `host_input_binding.py` module (mirroring
  `parametric_binding.py`'s shape) validates bound matrix shape/dtype
  against the selection width discovered at runtime.
- **Applicable constraints:** Candidate identity (descriptors, scores,
  tags, chemical strings) never crosses into the Kernel — bound matrices
  are indexed by **selection slot position** (`0..n-1`), never by
  `CandidateId`. No hidden hardcoded example-specific values (Class E
  discipline) — the port is general-purpose, not S02-specific, exactly
  like `RngPort`/`MeasureSinkPort`. Fail-closed: a predicate requiring a
  Host input that is missing or malformed rejects explicitly; it must
  never silently pass as vacuously true. `exactly_selected` needs no
  binding and is unaffected by this ADR. ADR 0192's already-Accepted
  `feasible(...)` keyword-argument shapes (`pairwise_compatible: Bool`,
  `diversity_at_least: Int`) are **not** changed by this ADR — the
  predicate's own call-site shape stays exactly as already shipped; only
  what the runtime does when it sees them changes.
- **Decisions, assumptions, unresolved ambiguities:** Binding-lookup
  strategy (§Decision 2) between implicit name-keyed lookup (recommended)
  and an explicit source-level declaration (rejected for this slice, noted
  as a future refinement). Diversity aggregation (§Decision 4) between
  minimum pairwise diversity (recommended, a worst-case guarantee) and
  average pairwise diversity (rejected as primary — a high outlier pair
  could mask an incompatible low pair). Matrix symmetry is required and
  validated, not assumed silently.
- **Included and omitted AI context:** Included direct reads of the
  evaluator, host boundary, existing port implementations, and ADR
  0192/LISS-0322's own stated boundaries. Omitted: any specific chemistry
  compatibility/diversity metric definition (that stays a Host/example
  fixture concern, per "Real compound data adapters... out of scope" in
  the S02 spec) and any live QPU adapter concern.
- **Task routing:** Architecture review for the port and predicate
  semantics decision; deterministic source inspection for all current-state
  claims above; no external AI/model call.
- **Input/output evidence contract:** N/A — no AI-generated runtime output;
  all current-state claims are grounded in direct source reads performed
  in this session.
- **Verification plan:** After acceptance, two sequenced Feature Path Local
  Issues (see "Follow-up work required") implement: (a) the `HostInputPort`
  foundation with real fail-closed binding validation, no predicate logic
  yet; (b) real `exactly_selected`/`pairwise_compatible`/`diversity_at_least`
  Projector execution built on (a), replacing the current unconditional
  runtime crash. Both keep the existing IR-lowering (LISS-0322) and
  `prepare_selection` (LISS-0324) behavior unchanged.

## Context

[LISS-0324](../../issues/LISS-0324-s02-prepare-selection.md) implemented
`prepare_selection(n: Int)` as a real Kernel op — an equal superposition
over all `2^n` selection patterns. The natural next step,
`project selection onto feasible(...)`, still crashes unconditionally at
runtime (registry entry, confirmed live). Of ADR 0192's three accepted
predicates:

- `exactly_selected(n)` needs no external data — it is a pure function of
  the selection pattern's own Hamming weight — and is scoped to a separate,
  already-agreed Issue that does not depend on this ADR.
- `pairwise_compatible` and `diversity_at_least` conceptually require
  knowing which selection slots are compatible with, or how diverse they
  are from, each other. This is exactly the kind of structural (not
  candidate-identity) relationship data the S02 spec anticipates staying
  classical, but **no existing Staqex mechanism carries Host-computed
  structured data into a local (non-QPU-circuit) program run.** The
  closest-looking existing mechanism, `Param<T>` (ADR 0070/LISS-0027), was
  investigated and found to be QPU-circuit-parameter-specific — it never
  reaches the local Joint evaluator at all, confirmed by its total absence
  from `runtime/evaluator.py`. Reusing or extending it would not actually
  solve this problem and would risk exactly the kind of keyword/concept
  collision the
  [kernel stub and placeholder registry](../kernel-stub-and-placeholder-registry.md)
  document was written to prevent (two different concepts — "symbolic QPU
  circuit angle" and "Host-supplied classical structural data" — sharing
  one name).

This ADR proposes a new, independent port instead.

## Decision proposal

### 1. New `HostInputPort`

```python
class HostInputPort(Protocol):
    def get(self, name: str) -> Any | None:
        """Return the bound classical value for `name`, or None if unbound."""
        ...

class MappingHostInputAdapter:
    def __init__(self, values: Mapping[str, Any]) -> None:
        self._values = dict(values)
    def get(self, name: str) -> Any | None:
        return self._values.get(name)
```

`Evaluator.__init__` gains `host_input: HostInputPort | None = None`
(constructor injection, the same pattern already used for `stdout`/`seed`
— no new `.sqx` syntax, no new keyword, no new AST node).
`host.py::_submit_compiled` reads an optional `settings["inputs"]: dict`,
wraps it in `MappingHostInputAdapter`, and passes it to `Evaluator(...)`.
A program that declares no `feasible(...)` predicate needing Host input is
completely unaffected — `host_input` stays `None`, matching how `seed`
already defaults to `None`.

### 2. Binding lookup: implicit, name-keyed by predicate name

When `project`'s runtime handler evaluates a `feasible(...)` call and finds
`pairwise_compatible = true`, it looks up
`self.host_input.get("pairwise_compatible")` from the injected port —
**not** a new source-level reference. Likewise `diversity_at_least = k`
looks up `self.host_input.get("diversity_at_least")`. ADR 0192's already-
shipped call-site shape (`feasible(exactly_selected = 2, pairwise_compatible
= true)`) does not change at all; only what the runtime now does with a
`true`/`Int` value changes. If the predicate is present in the call but no
port was injected, or the port has no binding for that name, the runtime
fails closed with a new `HOST_INPUT_BINDING_MISSING` diagnostic — never a
silent pass.

**Rejected alternative:** an explicit source-level declaration (e.g.
`requires host_input pairwise_compatible: Matrix<Bool>` at the top of
`main`). More visible in source, but adds new grammar/AST surface for a
binding whose actual values are only known at Job-submission time
regardless (a declaration could only ever check "was something bound", not
validate real data, since Host data doesn't exist at compile time) — not
ruled out as a future refinement once real usage patterns are known, but
unnecessary complexity for this first slice.

### 3. `exactly_selected` needs no Host input

Unchanged from the earlier scoped-down plan: `sum(pattern) == n` is a pure
function of the pattern itself. This predicate's implementation does not
depend on this ADR and may ship independently and first.

### 4. `pairwise_compatible` and `diversity_at_least` semantics

Given a selection pattern `p` (an `n`-tuple of `0`/`1`, from
`prepare_selection`), and a bound Host matrix `M` (an `n×n` structure,
validated at the point of use — never assumed):

- **`pairwise_compatible = true`** (requires `M: Matrix<Bool>`, symmetric):
  satisfied iff for every pair of selected slots `i < j` (both `p[i] == 1`
  and `p[j] == 1`), `M[i][j] is True`. `pairwise_compatible = false` (or
  absent) applies no constraint — a no-op, matching how the predicate is
  not currently required to appear at all.
- **`diversity_at_least = k`** (requires `M: Matrix<Float>`, symmetric,
  non-negative): satisfied iff the **minimum** pairwise value of `M[i][j]`
  over every pair of selected slots `i < j` is `>= k`. A selection with
  fewer than two selected slots vacuously satisfies this (no pair to
  violate it).

**Rejected alternative (diversity aggregation):** average pairwise
diversity instead of minimum. Rejected as primary because an average can
mask one badly-incompatible low-diversity pair behind several
high-diversity pairs; minimum gives a worst-case guarantee, which better
matches "diversity **at least** k" as a hard constraint rather than a soft
objective (soft, weighted objectives are already a separate, later S02
concern per the spec's own objective-normalization section).

**Validation, fail-closed:** `M` must be exactly `n×n` (n taken from the
actual bound pattern's tuple length at runtime — no separately tracked
width needed); `M[i][j] == M[j][i]` for every pair (symmetry); dtype
(`bool` for compatibility, finite non-negative `float`/`int` for
diversity). Any violation raises `HOST_INPUT_BINDING_VALUE_ERROR` with a
message naming the specific violation. Diagonal values (`M[i][i]`) are
never read.

### 5. Combined predicate application

All predicates present in one `feasible(...)` call combine with logical
AND into a single predicate function, applied via the existing
`joint.project_coord(name, predicate)` (the same Hilbert-projector-plus-
renormalize mechanism `project(psi, k)` already uses) — no new Joint
method needed.

## Consequences

- `pairwise_compatible`/`diversity_at_least` get real, fail-closed runtime
  semantics instead of an unconditional crash, without changing ADR 0192's
  already-shipped call-site shape.
- A new, general-purpose, non-S02-specific port (`HostInputPort`) exists
  for any future feature needing Host-computed structural data in a local
  run — added to the "External Resources Must Be Ports" list in
  `CLAUDE.md` as its own, separately-tracked documentation update (see
  Follow-up).
- Candidate identity still never crosses into the Kernel — bound matrices
  are strictly slot-indexed.
- `Param<T>`'s existing, narrower QPU-circuit-parameter meaning is
  preserved untouched; no keyword or concept is overloaded.

## Rejected alternatives

### Extending `Param<T>`'s domain to a Matrix type

Rejected. Investigation found `Param<T>` bindings never reach the local
Joint evaluator at all — they are consumed exclusively by the QPU-circuit
submission/backend path. Extending its domain would not solve the actual
problem (getting data into the local evaluator) and would conflate two
different concepts under one name.

### Explicit source-level Host-input declaration

Rejected for this first slice (see Decision 2) — deferred, not ruled out.

### Average instead of minimum for `diversity_at_least`

Rejected as primary (see Decision 4) — deferred as a possible later,
separately-named objective, not this hard constraint's meaning.

## Follow-up work required after acceptance

1. **Complete:** [LISS-0327](../../issues/LISS-0327-host-input-port-foundation.md)
   implements the `HostInputPort` foundation: `host_input_port.py`,
   `Evaluator(host_input=...)`, `host.py`'s `settings["inputs"]`
   passthrough, and `host_input_binding.py`'s validation
   (`HOST_INPUT_BINDING_MISSING`, `HOST_INPUT_BINDING_VALUE_ERROR`). No
   predicate logic in this Issue. PR #366 merged (`b1ce2bd`).
2. **Complete:** [LISS-0328](../../issues/LISS-0328-selection-projector-predicate-execution.md),
   built on LISS-0327, implements real `project ... onto feasible(...)`
   runtime execution for all three predicates (`exactly_selected`,
   `pairwise_compatible`, `diversity_at_least`) per Decisions 3–5,
   replacing the current unconditional crash. PR #368 merged (`73580d3`).
3. Add `HostInputPort` to `CLAUDE.md`'s "External Resources Must Be Ports"
   list — a documentation-only change requiring its own stated reason and
   AI work trace per CLAUDE.md's own change-control rule.

## Acceptance boundary

Acceptance of this ADR approves the port shape and predicate semantics
described above. It does **not** by itself authorize implementation —
the two Local Issues in "Follow-up work required" each need their own Plan
approval, per CLAUDE.md's Issue-Level Autonomy.
