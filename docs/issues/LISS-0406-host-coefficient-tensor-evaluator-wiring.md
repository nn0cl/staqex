# LISS-0406: wire HostInputPort into the Host coefficient tensor path

## Metadata

- Local issue ID: LISS-0406
- Status: complete
- Type: Feature Path (Kernel: `compiler/staqex/runtime/evaluator.py` only —
  no new port, no new type, no new syntax; reuses ADR 0119/DEC-0006's
  already-Accepted `Float[N]… = host("key")` + `CoefficientTensor` +
  `merge_host_coefficient_arrays` surface and ADR 0194's already-Accepted
  `HostInputPort`)
- Priority: P1
- Planning size: `S`
- Owner / agent: Claude Code
- Parent: follow-on question disclosed in
  [LISS-0405](LISS-0405-s02-unified-selection-evolve.md) Design
  verification point 5 / open-work register
- Branch: `feature/liss-0406-host-coefficient-tensor-wiring`
- GitHub Issue / PR: (opened at Completion)

## [DESIGN CHECK]

- **Scope and expected behavior:** LISS-0405 disclosed "no channel today
  for per-position Host-computed weights to enter an `Operator`'s field
  terms" as the reason S02's `objective_hamiltonian` cannot correlate
  with the classical baseline's per-candidate scoring. Investigation
  (this Issue) found that claim was **not fully accurate**: the language
  surface for exactly this (`Float[N]… name = host("key")` bound and
  indexed inside a `sum (i in Index<0..N>) { w[i] * Z[i] }` binder body)
  already exists, is already typechecked
  (`typecheck.py:1540-1548`/`1809-1832`/`1993-2018`), and already has a
  tested lowering path (`finite_binder.py`'s `CoefficientTensor` +
  `merge_host_coefficient_arrays` + `lower_finite_binder_operators(...,
  host_arrays=...)`, ADR 0119, `tests/test_host_coefficient_tensor_red.py`).
  The actual gap is narrower: `Evaluator._run_unit_body`
  (`evaluator.py:312`) calls `lower_finite_binder_operators(unit)` with
  **no** `host_arrays` — `self.host_input` (the live `HostInputPort`) is
  never consulted for coefficient-tensor keys, so `host("key")`
  placeholders are unreachable from any real run today (only from a test
  that hand-builds and passes `host_arrays` directly).
- **Specifications and files inspected:**
  `compiler/staqex/finite_binder.py` (`_host_placeholder_keys` L822,
  `merge_host_coefficient_arrays` L858, `lower_finite_binder_operators`
  L935), `compiler/staqex/scientific_input.py` (`CoefficientTensor` L119),
  `compiler/staqex/runtime/evaluator.py` (`_run_unit_body` L280-312,
  `_bind_feasible_predicate` L4610-4660 as the fail-closed precedent),
  `compiler/staqex/host_input_port.py`, `compiler/staqex/host_input_binding.py`,
  `tests/test_host_coefficient_tensor_red.py`,
  `docs/architecture/decision-themes/dec-0006-host-qpu-and-external-ports.md`
  (confirms ADR 0119/ADR 0194 both "accepted current surface").
- **Component boundaries, ports/adapters, VO/DTO candidates:** No new
  boundary. `HostInputPort` (already an injected Port, ADR 0194) is
  wired into an already-Accepted UseCase-internal lowering step
  (`finite_binder.py`) inside the existing `Evaluator` Adapter. No new
  Port, no new Ty kind, no new parser grammar.
- **Applicable constraints:** Must fail closed
  (`KernelDiagnosticError`, matching the `pairwise_compatible`/
  `diversity_at_least` precedent at `evaluator.py:4630-4660`) on missing
  or malformed Host coefficient data — never silently substitute zeros
  or skip terms. Must not change behavior for any program without
  `host("key")` placeholders (regression guard).
- **Decisions, assumptions, unresolved ambiguities:** Evaluator looks up
  *only* the host keys the `.sqx` source itself already declares via
  `host("key")` placeholders (`_host_placeholder_keys(unit)`), never a
  blind/speculative fetch. Raw values from `HostInputPort.get(key)` are
  wrapped into `CoefficientTensor` using the placeholder's own declared
  shape (already known from the `Float[N]…` type annotation); a
  `ScientificInputValidationError` from that construction is re-raised
  as `KernelDiagnosticError` for the same fail-closed contract as every
  other Host-input consumer. No ambiguity requiring Architecture Path —
  this is closing a wiring gap in already-Accepted surface, not a new
  decision.
- **Included and omitted AI context:** N/A — deterministic Kernel
  wiring, no AI-authored numeric output.
- **Task routing:** Claude Code, Feature Path, Kernel-only.
- **Input/output evidence contract:** N/A.
- **Verification plan:** Red — a `.sqx` program using
  `Float[8] w = host("weights")` inside a `sum` binder, run through a
  real `Evaluator` with `HostInputPort` supplying `"weights"`, currently
  either raises `HOST_COEFFICIENT_MISSING` (because `host_arrays` is
  never populated) or silently uses whatever `_collect_float_arrays`
  finds — must instead resolve to the real Host-supplied values. Green —
  wire `self.host_input` into `merge_host_coefficient_arrays`/
  `lower_finite_binder_operators` in `_run_unit_body`. Then apply this to
  S02's `main_selection.sqx` (real motivating case) and re-measure
  `top_k_overlap`. Full regression sweep after.

## Scope

1. In `Evaluator._run_unit_body`, before calling
   `lower_finite_binder_operators`, resolve `host("key")` placeholders
   via `self.host_input` into `CoefficientTensor`s, run
   `merge_host_coefficient_arrays`, fail closed on any diagnostic, and
   pass the merged arrays as `host_arrays`.
2. Apply the now-real capability to
   `examples/showcase/S02_drug_discovery/main_selection.sqx`: give
   `objective_hamiltonian` genuine per-candidate weights
   (`Float[8] activity_w = host("activity_weights")` etc., or a single
   combined tensor — decided during implementation) instead of one
   scalar weight shared by every position, sourced from
   `scoring.py`'s own `build_candidate_scores` via `run_selection.py`'s
   `HostInputPort` adapter (the same values the classical baseline
   already uses — this is what should let the two rankings actually
   correlate).
3. Re-measure `top_k_overlap` and record the honest result — improved,
   unchanged, or still mismatched for some other disclosed reason.
4. Full regression sweep.

## Explicitly out of scope

- Any parser/typecheck/new-Ty change — none needed (finding above).
- Any new ADR — reuses two already-Accepted decision surfaces
  (ADR 0119/DEC-0006, ADR 0194).
- Extending this beyond `Float[N]` 1-D/N-D coefficient tensors (e.g. Int
  arrays) — not needed for the S02 motivating case, not attempted here.

## Design verification performed during implementation

1. **Red confirmed the gap for the stated reason**: a real `Evaluator`
   run with `host_input` supplying `"coupling"` raised `KernelError:
   unknown function \`host\`` — the sum binder's `coeff[i]` was never
   lowered to a literal, so the raw `host(...)` Call fell through to
   generic evaluation.
2. **A second, adjacent gap was found and fixed in the same pass**: even
   after wiring `host_arrays` into `lower_finite_binder_operators`, a
   `Float[N]…` StateBind statement (host-sourced *or* literal) is still
   a normal statement in `main`'s body, and the generic per-statement
   Joint-binding dispatch had never been taught to skip it — it fell
   through to `_bind_names`, which doesn't understand a bare list/Call
   value either (`cannot bind expr ListExpr` for literals, `unknown
   function \`host\`` for host-sourced). **This means `Float[N]…`
   coefficient-tensor declarations — the entire ADR 0119 surface, not
   just the Host-sourced half — were unreachable from any real
   `Evaluator.run_unit` call before this Issue**, confirmed by testing
   the literal-array case in isolation. Fixed by skipping `Float[N]…`
   StateBinds from generic execution (`evaluator.py`, next to the
   existing `QubitRegister` compile-time-metadata skip) — they have no
   live Joint/scalar role; their value is consumed only via the
   `sum`-binder lowering above.
3. **Applying the fix to S02 surfaced two more disclosed compiler
   limitations** (documented in `main_selection.sqx`'s own header
   comment, not worked around silently): a `Float[N]` array cannot be
   threaded through a free-function parameter into a `sum` binder body
   (`cannot compile sparse Pauli for OpBinder`), and a struct-field
   access cannot be used directly as an Operator coefficient outside a
   function-call return position (`cannot compile sparse Pauli for
   OpAttr`). Routed around by building the Hamiltonian with plain local
   variables at `main` level instead of a separate
   `objective_hamiltonian(w: ObjectiveWeights)` function — not a
   regression, `main_selection.sqx` never shipped that exact shape to
   users.
4. **A serious, unanticipated correctness finding, investigated and
   fixed rather than silently shipped**: once real per-candidate weights
   made the bias strong enough to observe clearly (weights re-tuned from
   0.02/0.01/0.01 to 2.0/1.0/1.0 — empirical sweep across several
   weight/duration configurations, not guessed), direct execution showed
   `benchmark_report.py` sampling terminal patterns **outside** the
   25-pattern feasible set `project onto feasible(...)` should confine
   `psi_sel` to. Root cause: `H_obj`'s `X[i]` field terms do not commute
   with the exactly-selected/pairwise/diversity projector — `X` flips a
   candidate's selected bit, changing Hamming weight, so real unitary
   evolution under a Hamiltonian containing `X` terms can genuinely leak
   probability mass outside a Hamming-weight-restricted subspace
   (confirmed: a `Z`/`ZZ`-only Hamiltonian, being diagonal, leaks
   nothing — but also provably does not change the measurement
   distribution at all, since diagonal evolution only adds phases).
   This is not a new architecture question: the S02 acceptance spec's
   own Constraint and objective contract already anticipates exactly
   this ("If a penalty Hamiltonian is used, the report must identify it
   as a penalty profile and must not claim that a low penalty guarantees
   feasibility") and requires feasibility to reflect the actual
   measurement, not be assumed. `benchmark_report.py`'s
   `feasibility_rate = len(non_vacuum)/len(outcomes)` and the existing
   test's "`feasibility_rate` must be exactly 1.0 by construction"
   comment were both wrong under the current design (they were true only
   for LISS-0402/0403's original disconnected-qubit-pair design, where
   `H_obj` never touched `psi_sel`). Fixed: `build_report` now validates
   every non-vacuum shot with `scoring.is_feasible` before counting it as
   feasible, excludes infeasible shots from `mean_objective_score`/
   `top_k_overlap` (comparing feasible-to-feasible against
   `baseline_score`/`baseline_top_k`, which are themselves feasible-only),
   reports a new `infeasible_shots` quality metric, and warns explicitly
   using the spec's own "penalty Hamiltonian" language. At the shipped
   weights, 6/20 seeds (0-19) leak — a real, disclosed, now-correctly-
   reported rate, not silently hidden.
5. **`top_k_overlap` re-measured, honestly, on the corrected
   (feasible-only) metric: 0.33** (up from LISS-0405's 0.0), confirmed
   reproducible across an independent weight/duration sweep (not a
   single lucky seed). This is a real, partial improvement — genuine
   per-candidate weight now reaches the Hamiltonian and produces a
   measurable, non-zero correlation with the classical baseline's
   ranking — but not a strong one: real-time unitary evolution under a
   fixed-duration Hamiltonian is not a scoring/ranking algorithm (no
   QAOA-style tuned cost/mixer alternation is shipped), so no particular
   overlap value was ever guaranteed. Recorded honestly in
   `benchmark_report.py`'s warning text, this Issue, and the README —
   not oversold as "solved."

## Exit criteria

- [x] Red test demonstrates the gap against a real `Evaluator` run (not
  a hand-built `lower_finite_binder_operators(host_arrays=...)` call).
- [x] Green: `self.host_input` wired into the coefficient-tensor path;
  fail-closed diagnostics on missing/malformed data; existing
  `test_host_coefficient_tensor_red.py` and all `host("key")`-free
  programs unaffected. (Also fixed the adjacent gap in Design
  verification point 2, found during Green.)
- [x] `main_selection.sqx` uses real per-candidate weights sourced from
  the same values `scoring.py` uses for the classical baseline.
- [x] `top_k_overlap` re-measured and the honest result recorded in the
  Issue/README/open-work register: 0.33, up from 0.0, on the
  feasibility-corrected metric (Design verification points 4-5).
- [x] Full regression sweep passes (1454 passed,
  `.venv/bin/python -m pytest -q`).
