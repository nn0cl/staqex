# 2026-09-07 Feature Path / Phase 0: explicit Suzuki finite-QPU projection

## [DESIGN CHECK]

- Scope and expected behavior: investigate the remaining finite Suzuki/QPU
  projection failure and decide whether it is a production defect, an
  acceptance-spec gap, or a stale test contract. The target boundary must
  preserve source meaning, require an explicit finite policy, emit only a
  canonical provider-neutral projection, and fail closed without partial QPU
  artifacts.
- Requested phase: Feature Path / Phase 0 / investigation and design.
- Proposed next phase: Feature Path / Phase 1 Red for a separately recorded
  fixture-reconciliation issue, after review of this design record.
- Adjudicator decision needed: approval to enter Phase 1 Red for the selected
  fixture-reconciliation scope; no implementation approval is requested here.
- Requested approval type: Phase 1 Red approval, after this Phase 0 record is
  reviewed.
- Approved scope: explicit Suzuki and finite QPU projection investigation only.
- Implementation allowed: no. This record contains no source or test change.
- Post-review required: yes; the Phase 1 Red result requires the normal
  same-context review and status synchronization.

## Context ledger

### Specifications and artifacts inspected

- `docs/specs/staqex-explicit-evolution-surface.md`
- `docs/specs/staqex-qpu-capability-rejection-contract.md`
- `docs/specs/staqex-scientific-semantic-core.md`
- `docs/specs/staqex-scientific-semantic-consumer-migration.md`
- `docs/issues/LISS-0017-higher-order-suzuki.md`
- `docs/issues/LISS-0444-scientific-semantic-core.md`
- `docs/issues/LISS-0438-explicit-evolution-residual-reconciliation.md`
- `docs/work-plans/WP-0107-scientific-semantic-core.md`
- `tests/test_liss_0444_finite_instruction_projection_red.py`
- `tests/test_explicit_trotter_steps_red.py`
- current compiler diagnostics in `typecheck.py`, `quantum_semantic_ir.py`,
  and `scientific_semantic_ir.py`.

### Included

- The currently failing LISS-0444 finite Suzuki fixture.
- The accepted `using Suzuki(order = 2, steps = N)` policy.
- Canonical QPU instruction/provenance/fingerprint obligations.
- The no-AST-fallback and no-partial-artifact boundary.
- The adjacent explicit-step regression family, to prevent an over-broad fix.

### Omitted

- `evolve ... until`, empty-domain identity, and Dirac paper syntax failures;
  they are separate semantic families and require separate Phase 0 records.
- Provider SDKs, AWS/Braket credentials, network calls, live QPU execution,
  resource allocation, and S02 numerical migration.
- Consumer-wide migration outside the already bounded Suzuki projection.

## Evidence and classification

| Evidence | Observed result | Phase 0 classification | Disposition |
|---|---|---|---|
| `test_finite_suzuki_produces_canonical_qpu_instructions` | `EVOLVE_HAMILTONIAN_SHORTCUT_RETIRED` and `QSEM_APPROXIMATION_OBLIGATION_MISSING` | stale fixture against accepted source/target boundary | reconcile the fixture in Phase 1 Red; do not relax either diagnostic |
| `test_finite_binder_produces_canonical_qpu_instructions` | shares the legacy implicit-Hamiltonian shape and requires separate binder evidence | adjacent fixture contract, not proven production defect | keep in the same narrowly bounded fixture issue only if the accepted binder source can be written without changing binder semantics |
| invalid Suzuki order / mutation-fingerprint tests | exercise fail-closed and provenance boundaries independently | valid boundary evidence | preserve unchanged and rerun after fixture reconciliation |
| `tests/test_explicit_trotter_steps_red.py` | explicit step-count cases pass after the bounded LISS-0511 correction | positive neighboring contract | use as a regression guard; no global approximation-obligation relaxation |

The key observed source shape is:

```staqex
State evolved = Evolve { psi under H for 1.0.s using Suzuki(order = 2, steps = 2) }.run()
```

The accepted explicit-evolution specification instead requires the source to
show the evolution operator application inside `Evolve()`, while the QPU
boundary may realize that meaning only when an accepted finite policy is
present. The current typechecker therefore correctly reports the retired
implicit Hamiltonian shortcut. The canonical semantic checker also correctly
requires an explicit approximation obligation for a non-exact lowering. A
test fixture cannot claim canonical finite projection while omitting those
accepted contracts.

## Boundary decision

The next implementation slice is test-contract reconciliation, not a compiler
relaxation:

1. Rewrite the selected LISS-0444 source fixture into the accepted explicit
   evolution surface, or document why the finite compatibility surface is a
   separately accepted source form.
2. Make the approximation obligation explicit only where the accepted target
   contract requires it. Direct `steps` must remain an explicit deterministic
   override and must not be silently clamped or converted to tolerance mode.
3. Keep canonical source-node identity, Suzuki order/steps, gate provenance,
   fingerprints, and empty-artifact rejection assertions unchanged.
4. Add a positive neighboring assertion for the Hamiltonian coefficient form
   used by explicit-step tests. The rejection check must remain scoped to the
   exact retired source shape; it must not classify a valid scalar-times-Pauli
   Hamiltonian term as a non-unitary product.

No Phase 1 implementation target is authorized yet. If the corrected fixture
still cannot produce the accepted canonical projection, that becomes a new
production defect and must be split into its own reviewed issue rather than
being hidden by weakening the semantic or QPU boundary.

## Component boundaries and contracts

- Front end/typecheck owns source-form validity and the retired-shortcut
  diagnostic.
- Scientific Semantic IR owns source-derived evolution meaning, exactness,
  approximation obligation, Suzuki policy, and provenance.
- QPU IR owns the finite canonical instruction projection and executable
  fingerprint.
- QASM emission consumes canonical QPU IR only; it must not re-lower the AST.
- Provider adapters and live submission remain outside this slice.

No new port, adapter, value object, or technology choice is required for the
Phase 1 Red fixture investigation.

## Process lessons applied

- Authority boundary: the compatibility Suzuki projection remains a consumer
  of canonical semantic data; the fixture must not make an AST lowerer an
  alternate authority.
- Acceptance boundary: fail-closed checks must be scoped to the exact source
  context and paired with a positive neighboring Hamiltonian case.
- Phase-acceptance boundary: a supported projection is not evidence that an
  unsupported or stale source shape may produce a partial artifact.
- Status drift: existing completed LISS-0444/WP-0107 records are not reopened
  implicitly; this Phase 0 record proposes a separate follow-up only if Phase
  1 Red is approved.

## Phase 1 Red verification plan

- Record the exact fixture contract and expected diagnostics before editing.
- Add or update only the selected finite Suzuki/binder fixture assertions.
- Verify that the current production behavior fails the intended Red contract
  for the intended reason, without changing production code.
- Run the focused finite projection, explicit-step, QPU rejection, and
  provenance suites.
- Run `git diff --check` and the repository spec-verification command.
- Stop before Phase 2 Green; Phase 2 requires a separate typed approval.

## Stop conditions

- Stop and request an ADR/spec decision if the accepted source grammar must be
  changed, if `steps` semantics conflict with the approximation obligation, or
  if a new rejection code is proposed.
- Stop and split a new production issue if a compliant explicit fixture still
  cannot reach canonical finite projection.
- Stop before implementation if the Phase 1 issue and acceptance specification
  have not received independent review and typed Phase 1 Red approval.

## Phase 1 Red execution record

- User decision: `Feature Path / Phase 1 Red / explicit Suzuki・finite QPU fixture reconciliation 承認`.
- Canonical issue/work plan: LISS-0512 / WP-0129.
- Attempt: 1, local workspace, deterministic test-oriented execution.
- Model/reasoning setting: N/A; no external AI or provider was used.
- Scope: reconcile the finite Suzuki fixture only; no production implementation.
- Result: the fixture now uses explicit `exp` + `Realize` + `Evolve()` source.
  The focused suite reports **19 passed, 3 failed**. The remaining failures
  expose missing canonical finite gates, non-atomic invalid-policy artifact
  removal, and QASM projection unavailability.
- Verification: `PYTHONPATH=. .venv/bin/pytest -q ...` focused suites passed
  19/22; `PYTHONPATH=. .venv/bin/python tests/spec_verification/run_all.py`
  passed **161/161**; `git diff --check` passed.
- Changed files: LISS-0444 fixture test, LISS-0512, WP-0129, and this trace.
- Next safe action: review the Red tests and decide whether to approve Phase 2
  Green for canonical explicit-Realize finite projection. Do not implement from
  this Red approval alone.

## Phase 2 Green execution record

- User decision: `Feature Path / Phase 2 Green / LISS-0512 canonical explicit-Realize finite QPU projection 承認`.
- Scope: canonical Scientific Semantic IR projection for explicit Suzuki
  `Realize`; no provider or live-QPU work.
- Implementation: source-derived explicit `exp`/`Realize` Hamiltonian recovery
  now creates finite Suzuki canonical operations; invalid policy errors make
  QPU instructions atomic and empty. The QASM emitter propagates the typed
  canonical projection error before generic fallback diagnostics. Existing
  QASM consumers remain readers of canonical QPU IR.
- Verification: focused LISS-0512 and neighboring suites **64 passed**;
  spec verification **161/161**; `git diff --check` passed. Full regression
  completed at **1932 passed, 16 failed** in unrelated open suites.
- Changed production file: `compiler/staqex/scientific_semantic_ir.py`.
- Next safe action: same-context Phase 3 review/refactor only after typed
  Phase 3 approval. Do not add provider SDK or live execution.

## Phase 3 Refactor execution record

- User decision: short `承認` uniquely followed the explicit Phase 3 pending
  gate and was treated as Phase 3 approval.
- Refactor: extracted shared canonical Suzuki opcode/provenance construction;
  explicit and compatibility paths now use one pure helper.
- Same-context review: review packet recorded the authority, atomic rejection,
  duplication, and scope findings; isolation is weaker than separate-context.
- Verification after refactor: focused **64 passed**, Spec Verification
  **161/161**, compileall passed, and `git diff --check` passed.
- Next safe action: final Adjudicator review, then commit/PR and issue-status
  synchronization. No provider or live-QPU work is authorized by this phase.
