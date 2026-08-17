# LISS-0437 Phase 3 target-realization design intake

## [DESIGN CHECK]

- **Scope and expected behavior:** Provide a target-owned QPU realization
  profile for the already accepted explicit source form. When the profile
  supplies an accepted Suzuki order and finite step count, lower
  `exp(-i * H * dur / hbar) * psi` through the existing provider-neutral
  Pauli/Trotter gate lowering. Without a profile, reject before allocation.
- **Specifications and files inspected:** ADR 0209; the explicit-evolution
  acceptance specification; WP-0100 Phase 2/3 target contract;
  `compiler/staqex/backend/qasm/lower.py`; QASM Trotter policy; runtime
  real-ℏ Hamiltonian path; S02 fixture; independent-review perspectives.
- **Component boundaries, ports/adapters, and VO/DTO candidates:**
  `EvolutionTargetProfile` is a target-side value object containing only
  approximation order and finite steps. The source AST remains unchanged.
  QASM lowering consumes the profile and emits the existing provider-neutral
  `Circuit`; no vendor adapter or physics policy is added.
- **Applicable constraints:** The source must retain blackboard meaning;
  target approximation cannot be inferred from `Evolve` or hidden in an
  adapter; unsupported targets fail closed with no partial circuit; terminal
  measurement and State ownership remain unchanged.
- **Decisions, assumptions, and unresolved ambiguities:** Phase 3 begins with
  explicit canonical exponentials whose generator is already supported by
  Pauli Suzuki lowering. Formal `Limit`, grid/Fock generators, unsupported
  operator algebra, QPU submission, and S02 numerical closeout remain later
  slices. A profile with no policy is intentionally rejected.
- **Included and omitted AI context:** Included the accepted ADR/Spec/WP,
  relevant lowering/runtime files, S02, and review ledger. Omitted vendor
  credentials, external providers, unrelated corpus files, and private data.
- **Task routing (model/assistant/tool):** deterministic local implementation
  and tests; independent read-only review after the slice.
- **Input/output evidence contract when AI output is involved:** no AI output
  is used as runtime data. Reviewers return only prioritized findings and
  evidence paths; implementation decisions remain source- and test-backed.
- **Verification plan:** explicit profile/no-profile QPU tests, inline and
  named runtime tests, S02 compilation, existing `times N` and `until`
  regressions, compileall, diff check, and independent review.

## Phase 3 first-slice decision

The target profile is supplied to `lower_unit_to_circuit` by the target
selection boundary. This preserves the distinction between the physicist's
equation and the target's approximation policy. No source syntax is added and
no QPU provider is selected.

## Independent review result

The first-slice review returned **READY** with no P0/P1 findings. The reviewed
boundary is limited to provider-neutral Suzuki realization; formal `Limit`,
wide migration, numerical S02 closeout, and real QPU submission remain out of
scope.

The final review found one documentation mismatch (`Measure psi_sel` versus
the current `Measure psi_final`), which was corrected. The bounded first slice
is now READY; formal `Limit`, broad migration, numerical equivalence closeout,
and real QPU submission remain separate residual slices.

## Subsequent residual verification

- S02 simulator fixed-seed equivalence: **PASS**; the expected terminal
  value is `(0, 1, 1, 1, 1, 1, 0, 0)`.
- S02 QPU profile attempt: explicitly rejected with
  `QASM_TROTTER_UNSUPPORTED_H` because the objective contains `OpBinder`
  terms. No partial circuit is emitted; binder-aware QPU lowering remains a
  separate capability slice.
- Existing corpus inventory: 92 legacy `Evolve { ... }` occurrences remain;
  broad migration is not silently performed by this slice.
