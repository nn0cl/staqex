# Staqex open-work register

This is the canonical cross-reference for capabilities that are intentionally
open, deferred, or still awaiting a dedicated local Issue. It complements the
completed Issue ledger; an item listed here is not implementation approval.

The shipping Kernel remains the Python package under `compiler/staqex/`. Any
future feature must first have an accepted specification or ADR, an explicit
phase request, and the required ports/adapters review described in
[`AGENTS.md`](../../AGENTS.md).

## Staqex v1 north-star rebaseline

| Area | Current status | Tracking | Boundary / acceptance note |
|---|---|---|---|
| Ideal v1 language and compiler | **Accepted with conditions** | [ADR 0106](decision-themes/dec-0003-language-surface-and-physicist-first-dx.md); [LISS-0068](documentation-compression-map.md); [WP-0025](../work-plans/WP-0025-staqex-v1-north-star.md); [rebaseline register](../specs/staqex-v1-normative-rebaseline-register.md) | North-star target architecture accepted 2026-07-27. LISS-0068 slice 2 may proceed; implementation remains per-Issue gated.

## Explicit deferred work

| Area | Current status | Tracking | Boundary / acceptance note |
|---|---|---|---|
| **QPex → Staqex rename** | **complete** | [LISS-0113](documentation-compression-map.md) | Renamed project from `QPex` to `Staqex`, `.sqx` → `.sqx`; 43 example files, ~136 Python import paths, ~340 doc files, agent instruction files; PR #118 merged 2026-07-29. |
|---|---|---|---|
| Function signatures / returns | Complete | [LISS-0021](documentation-compression-map.md); ADR 0064, ADR 0068 | Explicit return types, terminal `return`, `main -> Unit`, and arity/type checks are shipped and normative. QASM function-call lowering split to LISS-0049; an Operator-return typecheck gap split to LISS-0048. |
| Operator-return typecheck gap | Complete | [LISS-0048](documentation-compression-map.md) | Operator locals are registered before return checking; mismatches produce `RETURN_TYPE_MISMATCH` before runtime evaluation. Adjudicator final review approved 2026-07-25. |
| QASM function-call lowering | Complete (Option B scope) | [LISS-0049](documentation-compression-map.md) | Split from LISS-0021. Architecture Path selected Option B (2026-07-25): calling a user-defined `fn` from `main` rejects with `QASM_FUNCTION_CALL_UNSUPPORTED` (backend `reject_code` and CLI exit code) instead of silently falling back to the empty-program sketch. Adjudicator final review approved 2026-07-25. Option A (correct inlined output) remains a possible future follow-up, not scheduled. |
| Function keyword migration | Complete | [LISS-0023](documentation-compression-map.md); ADR 0066 | `fn` is canonical; `fun` is retired with no alias. |
| Visibility keyword migration | Complete | [LISS-0024](documentation-compression-map.md); ADR 0067 | `pub` is canonical; `public` is retired with no fallback. |
| Explicit returns / lexical scope | Complete | [LISS-0025](documentation-compression-map.md); ADR 0068 | Explicit terminal returns and no hidden Operator harvest. |
| Kernel classical boundary / static `forEach` | Historical slice complete; superseded surface tracked | [LISS-0026](documentation-compression-map.md); [ADR 0069](decision-themes/dec-0005-quantum-operations-and-runtime.md) | Static elaboration remains shipped; normative `QubitRegister<N>` migration/resource boundary is complete in LISS-0029. |
| Static Hilbert Kernel type surface | Phase 3 reviewed | [LISS-0029](documentation-compression-map.md); ADR 0069 | `QubitRegister<N>` is normative; MVP logical-shape/resource checks are explicit; target routing profiles remain separate. |
| Parametric Circuit | **Runtime complete** | [LISS-0027](../issues/LISS-0027-parametric-circuit.md); ADR 0070 | Symbolic parameters in QPU IR/OpenQASM; Host binding validation before submission. |
| Dynamic QPU lane | Phase 3 reviewed; timing **complete**; mid-circuit Kernel **complete** (ADR 0197 / LISS-0382) | [LISS-0028](../issues/LISS-0028-dynamic-qpu-lane.md); ADR 0071; [ADR 0193](adr/0193-dynamic-qpu-timing-region-intent.md) / [LISS-0381](../issues/LISS-0381-dynamic-qpu-timing-region-intent.md); [ADR 0197](adr/0197-dynamic-mid-circuit-feed-forward.md) (**Accepted** 2026-08-09); [LISS-0382](../issues/LISS-0382-dynamic-mid-circuit-feed-forward.md) (**complete**) | Rejection + timing intent shipped. Mid-circuit / feed-forward meaning Accepted (ADR 0197); Kernel IR+diagnostics (Controller=`measure`, soft `match`, DynamicMeasurement/Control regions) **complete** (LISS-0382). JobResult composition and qubit reuse remain open. Lane remains non-executable until a Feature Issue explicitly schedules otherwise. |
| Real `qft` / `iqft` | Phase 3 reviewed; official example complete | [LISS-0010](documentation-compression-map.md); [LISS-0020](documentation-compression-map.md); [LISS-0042](../issues/LISS-0042-qft-basic-gate-lowering.md); [ADR 0078](decision-themes/dec-0005-quantum-operations-and-runtime.md) | Exact register-typed QFT/IQFT boundary and basic-gate lowering are complete; `examples/basics/B11_qft_registers/` is the canonical Basics path; integration capstone `examples/applied/A10_mission_observatory/`. Exact single-control `cqft`/`ciqft` shipped (ADR 0120 / LISS-0151); approximate QFT remains deferred. |
| Density matrix / Lindblad CPTP | Complete | [LISS-0011](documentation-compression-map.md); [ADR 0057](decision-themes/dec-0003-language-surface-and-physicist-first-dx.md) | Numeric/runtime/source slices are complete; symbolic Hamiltonian/jump operators now support any qubit count (dimension is derived from the actual `DensityState` source, not a hardcoded 1-qubit assumption). Adjudicator final review approved 2026-07-25. Adaptive integration, positivity projection, and QPU execution remain a possible future follow-up, not scheduled. |
| Explicit Lindblad jump inputs | Phase 3 reviewed | [LISS-0039](documentation-compression-map.md); [WP-0005](../work-plans/WP-0005-lindblad-jump-inputs.md) | `JumpSet([RawMatrix(...)])` lowers through the existing RK4 CPU lane; Channel reuse and symbolic jumps remain out of scope. |
| Symbolic Lindblad jump lowering | Phase 3 reviewed | [LISS-0040](documentation-compression-map.md); [WP-0018](../work-plans/WP-0018-symbolic-lindblad-jump-lowering.md) | Bound one-qubit `Operator` entries in `JumpSet` lower through the RK4 CPU lane; general operator algebra and QPU execution remain out of scope. |
| `evolve ... until` | **Runtime complete** | [LISS-0012](documentation-compression-map.md); [ADR 0079](decision-themes/dec-0005-quantum-operations-and-runtime.md) | Bounded pure repetition in the Joint evaluator; QPU emission remains unsupported. |
| Pipeline `|>` / currying | Phase 3 reviewed | [LISS-0013](../issues/LISS-0013-pipeline-currying.md); ADR 0080 / 0122–0123 / 0131 / 0133 / **0137** | Unary bare, Partial, stepwise, hole fill, and thin unary-fn Operator Fusion MVP shipped; ADR 0022 quartet MVPs shipped (0137–0140). |
| Trait `impl` / `system` expression model | Phase 3 reviewed | [LISS-0014](../issues/LISS-0014-trait-impl-system.md); [ADR 0082](decision-themes/dec-0005-quantum-operations-and-runtime.md) | Inline `<T: Interface>` bounds, post-merge coherence, marker `System`, and no `pub` in `impl` are shipped; dispatch and specialization remain deferred. |
| Effect marking | Phase 3 reviewed | [LISS-0015](../issues/LISS-0015-effect-marking.md); [ADR 0081](decision-themes/dec-0005-quantum-operations-and-runtime.md) | Fixed effect annotations and transitive call/pipeline diagnostics are shipped; effect rows and provider-specific effects remain deferred. |
| Host-side Braket / QPU submit | Phase 3 reviewed | [LISS-0016](../issues/LISS-0016-host-qpu-submit.md); [ADR 0083](decision-themes/dec-0006-host-qpu-and-external-ports.md) | Provider-neutral DTOs and submit/job ports are shipped; provider SDK, credentials, network adapter, and automatic retry remain deferred. |
| Job-based host execution/result boundary | Phase 3 complete | [LISS-0022](../issues/LISS-0022-job-based-host-execution.md); ADR 0065 | Local Job/JobResult boundary, linked-file APIs, CLI, and REPL integration are complete; provider submission, retries, and sessions remain deferred. |
| Operator-position bare `H` | Deferred | [LISS-0009](documentation-compression-map.md); ADR 0062 §7 | Existing `Hadamard` / explicit Operator forms remain authoritative until sugar receives a surface/typecheck specification. |
| Higher-order Suzuki / error control | **S2+S4 shipped** | [LISS-0017](../issues/LISS-0017-higher-order-suzuki.md); [LISS-0142](documentation-compression-map.md); [ADR 0084](decision-themes/dec-0006-host-qpu-and-external-ports.md) | S2 and S4 QASM lowering, static Bound/EmpiricalEstimate step derivation (order-aware), and `lowering_policy` provenance are shipped; adaptive selection remains deferred. |
| Concrete QPU IR lowering | Phase 3 reviewed | [LISS-0041](../issues/LISS-0041-qpu-ir-lowering.md); [ADR 0085](decision-themes/dec-0006-host-qpu-and-external-ports.md) | Immutable in-memory gate/parameter/measurement IR, provenance-preserving projection, and direct OpenQASM adapter input are shipped; dynamic opcodes and serialization remain deferred. |
| QFT/IQFT basic-gate lowering | Phase 3 reviewed | [LISS-0042](../issues/LISS-0042-qft-basic-gate-lowering.md); [ADR 0086](decision-themes/dec-0006-host-qpu-and-external-ports.md) | QFT/IQFT decompose controlled phase and register reversal into ADR 0085 basic gates; controlled/approximate QFT remains deferred. |
| Trotter step-count silent clamp | Complete | [LISS-0050](documentation-compression-map.md); [ADR 0094](decision-themes/dec-0005-quantum-operations-and-runtime.md) | QASM emission of a plain `evolve ... under H for t` (no `using Suzuki(...)` policy) rejects with `QASM_TROTTER_STEPS_REQUIRED` instead of silently clamping to 64 steps; the silently-clamped `trotter_step_count`/`trotter_gates` functions were removed. `using Suzuki(order = 2, steps/tolerance = ...)` (LISS-0017/ADR 0084) is the one remaining, already-correct mechanism. SV `evolve` (`expm_ih`) is unaffected. Adjudicator final review approved 2026-07-25. |
| Operator Pauli-atom-call parsing gap | Complete | [LISS-0051](documentation-compression-map.md) | Canonical bracketed references such as `Operator H = Z[0] * Z[1]` parse as `OpIndexed`/`OpBin`; genuine factory calls remain generic calls. The former parenthesized operator-index spelling is retired by LISS-0054. |

## Future theory-to-QPU coverage

The following proposed LISS are the next design inventory for writing common
theoretical-physics expressions without collapsing the Kernel/execution
boundary. Their complete dependency order and non-goals are recorded in
[`WP-0013`](../work-plans/WP-0013-theory-to-qpu-feature-roadmap.md) and the
research roadmap
[`theory-to-qpu-feature-roadmap.md`](../research/2026-07-23-theory-to-qpu-feature-roadmap.md).

| Area | Current status | Tracking | Boundary / acceptance note |
|---|---|---|---|
| Mathematical binders, finite domains, indexed expressions | Phase 3 reviewed | [LISS-0030](../issues/LISS-0030-mathematical-binders-and-indexed-expressions.md); [LISS-0055](../issues/LISS-0055-binder-body-as-operator-expression.md) | `sum`/`product` remain pure mathematical binders; the approved finite executable slice now lowers nested bodies, guards, products, and supported second-quantized expressions. Broader model-size acceptance remains open. |
| Finite mathematical binder lowering | Complete | [LISS-0052](documentation-compression-map.md); [LISS-0043](../issues/LISS-0043-finite-binder-lowering.md); [ADR 0088](decision-themes/dec-0002-state-first-semantics-and-measurement.md) | Inclusive finite sums retain inspection provenance and now also produce executable `OpExpr` trees consumed by the SV and QASM Hamiltonian paths. Literal indexed Pauli sites are supported wherever site-qualified Pauli operators are valid; Adjudicator completion approved 2026-07-27. |
| Binder composition and honest deferral | Phase 3 complete | [LISS-0053](documentation-compression-map.md); [LISS-0055](../issues/LISS-0055-binder-body-as-operator-expression.md); [ADR 0096](decision-themes/dec-0005-quantum-operations-and-runtime.md) | Composed finite sums and named scalar coefficients lower through existing execution paths. The LISS-0055 executable slice also handles supported `product`, nested binders, guards, and second-quantized bodies; unsupported forms remain explicit hard diagnostics. |
| Indexed operator and binder surface (final form) | LISS-0054…LISS-0058 complete; multi-register follow-up open | [ADR 0096](decision-themes/dec-0005-quantum-operations-and-runtime.md); [WP-0024](../work-plans/WP-0024-indexed-operator-and-binder-surface.md); [ADR 0102](decision-themes/dec-0002-state-first-semantics-and-measurement.md) | LISS-0054 ships one bracket notation `Op[i]`; LISS-0055 covers the approved executable binder slice; LISS-0056 defines empty-domain identities; LISS-0057 adds explicit periodic `wrap(i)`; LISS-0058 carries single-register acting space through operator values. Remaining empty-body/guard diagnostics and multi-register systems remain explicit follow-ups. |
| ADR deferred finite slices (honesty / `&&` / S4 / `J[i]`) | **complete** (WP-0032) | [WP-0032](documentation-compression-map.md); [LISS-0140](documentation-compression-map.md)–[LISS-0143](documentation-compression-map.md) | Binder honesty diagnostics; compound `where &&`; Suzuki S4; 1D `Float[N]` + `J[i]`. Still deferred: `rev`/dependent ranges, Basis expansion, Host tensors, cQFT. |
| ND Kernel coefficient tensors | **complete** (WP-0033) | [WP-0033](documentation-compression-map.md); [LISS-0144](documentation-compression-map.md); ADR 0096 | `Float[N][M]…` literals + full-rank `a[i][j]…` binder lookup. Host/Param tensors and partial slices remain deferred. |
| Binder endpoints / `where \|\|` / `rev` | **complete** (WP-0034) | [WP-0034](documentation-compression-map.md); [ADR 0117](decision-themes/dec-0002-state-first-semantics-and-measurement.md); LISS-0145–0147 | Static additive Index endpoints, dependent ranges, `rev(D)`, binder `\|\|`. |
| Basis binder / partial Float | **complete** (WP-0035) | [WP-0035](documentation-compression-map.md); [ADR 0118](decision-themes/dec-0004-type-first-scientific-model.md); LISS-0148–0149 | `Basis<N>` expansion; classical `Float[M…] row = h[i]`. |
| Host tensors + exact cqft | **complete** (WP-0036) | [WP-0036](documentation-compression-map.md); ADR 0119–0120; LISS-0150–0151 | In-memory `CoefficientTensor` + `host("…")`; exact `cqft`/`ciqft`. Approx QFT, file adapters, permanent-out remain out. |
| Acting-space typing | Phase 3 complete | [LISS-0058](documentation-compression-map.md); [ADR 0102](decision-themes/dec-0002-state-first-semantics-and-measurement.md); ADR 0096 D12 | Acting space is carried by operator values, with `QubitRegister<N>` as the canonical single-register shape and enclosing context as a secondary resolver. Declared shape is used during Hamiltonian evolution, context-free site-free identities fail explicitly, and no syntax-derived or one-qubit execution fallback is allowed. Multi-register naming and provider mapping remain deferred. |
| Multi-register acting-space and QPU mapping | Phase 3 reviewed | [LISS-0067](documentation-compression-map.md); [ADR 0105](decision-themes/dec-0006-host-qpu-and-external-ports.md) | Named static registers, RegisterSet typing, qualified-site checks, and logical/flat QPU mapping are reviewed complete; provider selection and physical routing remain gated. |
| Staqex v1 normative rebaseline | **closed — promoted** | [LISS-0068](documentation-compression-map.md), [spec v1.0](../specs/staqex-language-specification.md), [migration matrix](../specs/staqex-v1-migration-matrix.md) | Spec promotion 2026-07-28; next was LISS-0069. |
| Canonical Unicode math source | **superseded by ASCII source policy** | [ADR 0191](adr/0191-ascii-quantum-notation-and-lexical-boundary.md), [WP-0094](../work-plans/WP-0094-ascii-quantum-notation.md) | LISS-0069 remains historical migration evidence; current source is ASCII-only and Unicode is presentation/tooling input. |
| Versioned conformance / differential oracle | **closed — Slice A/B/C** | [LISS-0071](documentation-compression-map.md), [scenario catalog](../specs/staqex-v1-conformance-scenario-catalog.md) | Completed 2026-07-28; E-07/13/14 deferred; Rust differential with LISS-0070. |
| Lossless CST / formatter / source versioning | **closed — Slice A/B/C/D** | [LISS-0072](documentation-compression-map.md), [CST/formatter plan](../specs/staqex-v1-cst-formatter-plan.md) | Completed 2026-07-28; NFC / full pretty-print / LSP remain separate; no Rust gate. |
| Named Dirac notation / algebra AST | **closed — AST retained; source spelling revised** | [LISS-0073](documentation-compression-map.md), [ADR 0191](adr/0191-ascii-quantum-notation-and-lexical-boundary.md) | AST semantics remain; Unicode source sugar is superseded by ASCII ket/bra/tensor spelling. |
| Qutrit / qudit / finite local dimension | **complete** | [LISS-0074](documentation-compression-map.md), [qudit plan](../specs/staqex-v1-qudit-local-dimension-plan.md) | A–E complete; SV deferred to LISS-0112. |
| Qutrit / qudit D=3 state-vector MVP | **complete** | [LISS-0112](documentation-compression-map.md), [D=3 SV plan](../specs/staqex-v1-qudit-d3-sv-plan.md) | A–C complete; measure + Identity; QASM/D≠3 reject; E06-003. |
| Phase-resolved typed HIR | **complete** | [LISS-0080](documentation-compression-map.md), [HIR plan](../specs/staqex-v1-phase-resolved-hir-plan.md) | A–D complete; unlocks LISS-0075. |
| Linear quantum usage and safe uncomputation | **complete** | [LISS-0075](documentation-compression-map.md) | A–D complete; residuals triaged to LISS-0114 (not LISS-0077). |
| Linear verifier hardening / residual risks | **complete** | [LISS-0114](documentation-compression-map.md), [ADR 0107](decision-themes/dec-0002-state-first-semantics-and-measurement.md) (**Accepted**) | A–F complete; runtime ≈\|0⟩ tol 1e-12 locked by ADR 0107. |
| Rust compiler infrastructure | **deferred — next version** | [LISS-0070](../issues/LISS-0070-rust-compiler-infrastructure-deferred.md) (WP-0025 north-star) | Shipping Kernel stays Python; Rust VM later behind same semantics. |
| Numeric representation horizon | proposed | [ADR 0097](decision-themes/dec-0004-type-first-scientific-model.md); ADR 0076 | `f64` stays the concrete Kernel representation but is recorded as provisional, not permanent. The coefficient type is deliberately **not** genericised now; instead the `f64` conversion boundary and rounding rules must be explicit so a future exact/symbolic layer is additive. |
| Operator algebra and Dirac notation | Phase 3 reviewed; Unicode sugar **closed via LISS-0073** | [LISS-0031](../issues/LISS-0031-operator-algebra-and-dirac-notation.md); [ADR 0087](decision-themes/dec-0002-state-first-semantics-and-measurement.md); [LISS-0073](documentation-compression-map.md) | Function-shaped typed algebra (LISS-0031) + punctuation surface (LISS-0073 A–G) shipped; M-P06 dual-accept retained. |
| Typed second quantization | Complete (Jordan-Wigner scope) | [LISS-0032](documentation-compression-map.md); [ADR 0093](decision-themes/dec-0005-quantum-operations-and-runtime.md) | Fermion/boson/spin/qubit family boundaries, statistics provenance, and explicit mapping metadata are shipped. Jordan-Wigner numerical mapping for `FermionOperator` (one-body and two-body terms) is shipped: a mapped Hamiltonian runs on the SV simulator and emits QASM. Adjudicator final review approved 2026-07-25. Bravyi-Kitaev, Boson, and Spin mappings, and exchange-law normalization beyond canonical ordering, remain a possible future follow-up, not scheduled. |
| Symbolic expression IR and provenance | Phase 3 reviewed | [LISS-0033](../issues/LISS-0033-symbolic-expression-ir-and-provenance.md) | Source-preserving Symbolic/Resolved IR inspection boundary is shipped; serialized interchange and executable lowering records remain deferred. |
| Phase-separated scientific scopes | Phase 3 reviewed | [LISS-0034](../issues/LISS-0034-phase-separated-scientific-scopes.md) | Sealed contracts complete; body-level → [LISS-0076](documentation-compression-map.md). |
| Body-level scientific phase typing | **complete** | [LISS-0076](documentation-compression-map.md), [scientific-scopes](../specs/staqex-scientific-scopes.md) | A–E complete 2026-07-29; Execution leaks → PHASE_TYPE_VISIBILITY_ERROR across CU, Exp/Wf, import, call/method. Residuals → [LISS-0118](documentation-compression-map.md) (**not** 0116). |
| Physics IR (equations / operator algebra) | **complete** | [LISS-0081](documentation-compression-map.md), [physics-ir plan](../specs/staqex-v1-physics-ir-plan.md) | A–D + E + follow-ups 0115–0117 (WP-0028 closed). Soft `CompileResult.physics_ir`; Equation DTOs; oscillator lowered-IR evidence. Full six-family public oracle deferred (0119+). PR #124 / #133. |
| Quantum Semantic IR | **complete** (A–F) | [LISS-0082](documentation-compression-map.md), [quantum-semantic-ir plan](../specs/staqex-v1-quantum-semantic-ir-plan.md), [detailed contract](quantum-semantic-ir-contract.md), [ADR 0108](decision-themes/dec-0006-host-qpu-and-external-ports.md) (**Accepted**) | Slices A–E merged (PR #145); Slice F soft `CompileResult.quantum_semantic_ir` merged (PR #160). |
| Resource estimation and feasibility | **complete** (PR #161) | [LISS-0091](documentation-compression-map.md), [resource-estimation plan](../specs/staqex-v1-resource-estimation-plan.md) | Integrated A–E; `compiler/staqex/resource_estimate.py`; Red `12/12`. Distinct from host `SimulationResourceEstimate` (ADR 0100). No provider prices/SDK. |
| Target layout / routing / schedule | **complete** (PR #163) | [LISS-0092](documentation-compression-map.md), [target-routing plan](../specs/staqex-v1-target-routing-plan.md) | Integrated A–E; `compiler/staqex/target_routing.py`; Red `11/11`. Synthetic `TargetSnapshot` fixtures; LISS-0099 live ports deferred. No provider SDK / Theory leakage. |
| Target capability profile / physical port | **complete** (PR #165) | [LISS-0099](documentation-compression-map.md), [target-capability plan](../specs/staqex-v1-target-capability-plan.md) | Integrated A–E; `compiler/staqex/target_capability.py`; Red `10/10`. Fake port + CH0/CH1/NH5 fixtures; projection to LISS-0092 snapshot. No provider SDK / Semantic leakage. |
| Simulator port / capability profiles | **complete** (PR #166) | [LISS-0094](documentation-compression-map.md), [simulator-port plan](../specs/staqex-v1-simulator-port-plan.md) | Integrated A–E; `compiler/staqex/simulator_port.py`; Red `11/11`. Fake `SIM0_EXACT`/`SIM1_MIXED`; no engine selection (LISS-0095). |
| OpenQASM static CH0 subset | **complete** (P0, PR #167) | [LISS-0097](documentation-compression-map.md), [openqasm-ch0 plan](../specs/staqex-v1-openqasm-ch0-plan.md) | P0 integrated A–C; `backend/qasm/ch0_emit.py`; Red `10/10`. D/E/F deferred. |
| Dynamic QPU controller / feed-forward | **complete** (P0) | [LISS-0077](documentation-compression-map.md), [dynamic-qpu plan](../specs/staqex-v1-dynamic-qpu-plan.md) | P0 integrated A–D; `dynamic_qpu.py`; Red `10/10`. Fake supplied-outcome exec. E deferred. |
| Quantum machine scale/model envelope | **Accepted** (ADR 0109) | [detailed envelope](quantum-machine-scale-and-model-envelope.md), [ADR 0109](decision-themes/dec-0006-host-qpu-and-external-ports.md), [research](../research/2026-07-30-quantum-machine-scale-and-model-horizon.md) | One semantics from Personal Quantum Appliance to utility-scale FTQC; hierarchical/symbolic plans; no implicit remote fallback. Not language maxima. |
| Optimistic quantum capacity horizon | **Accepted** (ADR 0110) | [scenario envelope](quantum-capacity-horizon-scenarios.md), [ADR 0110](decision-themes/dec-0006-host-qpu-and-external-ports.md) | Non-normative QP-1/QP-2/QS-2 stress loads from BQ-0; never delivery forecasts or language limits. |
| Current and five-year delivery horizon | **Accepted** (ADR 0111) | [delivery envelope](current-hardware-delivery-envelope.md), [ADR 0111](decision-themes/dec-0006-host-qpu-and-external-ports.md), [WP-0029](../work-plans/WP-0029-current-hardware-delivery-horizon.md), [research](../research/2026-07-30-current-quantum-hardware-delivery-envelope.md) | CH*/SIM* current profiles + NH5 roadmap stress; provider selection remains separate Technology approval. |
| Representative program language review | **rejected / deferred** (LISS-0120) | [LISS-0120](../issues/LISS-0120-representative-program-language-review-gate.md), [rebaseline](../specs/staqex-v1-representative-program-rebaseline.md) (**Accepted** 2026-07-31) | Premature gate closed. P0/P1 start authorized; LISS-0119 complete. |
| Examples health (rebaseline Gate P0) | **complete** (0119/0122/0123) | [LISS-0119](documentation-compression-map.md), [LISS-0122](documentation-compression-map.md), [LISS-0123](documentation-compression-map.md) | Basics+applied catalogs green; A11 on SV-09. |
| Language coverage ledger (Gate P1) | **complete** | [LISS-0124](documentation-compression-map.md), [ledger](../specs/staqex-v1-language-coverage-ledger.md) | Option B complete; typed surface shipped; permanent-out recorded; S1 authorize unblocked. |
| Showcase mission lock (Gate P2) | **complete** | [LISS-0126](documentation-compression-map.md), [mission lock](../specs/staqex-v1-showcase-mission-lock.md) | Quantum-matter / Noether Forge lineage locked 2026-07-31. |
| Showcase S0 specification | **complete** (docs) | [LISS-0127](documentation-compression-map.md), [S0 disaster-response spec](../specs/staqex-v1-showcase-s0-disaster-response.md) | Canonical S0 is the disaster-response mission; the former quantum-matter S1 thin slice remains as historical implementation evidence. |
| Showcase S1 thin slice | **complete** | [LISS-0134](../issues/LISS-0134-showcase-s1-thin-slice.md), `examples/showcase/quantum_matter_discovery/` | Merged #179. |
| Sparse Pauli Operator return | **complete** | [LISS-0136](../issues/LISS-0136-sparse-pauli-operator-return.md) | Merged #180; factory local Float fold. |
| Classical Float → Operator / evolve + param factory | **complete** (PR pending) | [LISS-0137](../issues/LISS-0137-classical-float-operator-evolve-binding.md) | \(H(J,h)\); field/`evolve for` binding. |
| Operator method Call return | **complete** (PR pending) | [LISS-0139](../issues/LISS-0139-operator-method-call-return.md) | `Operator H = m.hamiltonian()`. |
| `when` ket prepare arms | **complete** (PR pending) | [LISS-0138](../issues/LISS-0138-when-ket-prepare-arms.md) | Ket arms in `when`; B02 + showcase updated. |
| Hamiltonian library surface program | **complete** (PR pending) | [WP-0031](../work-plans/WP-0031-hamiltonian-library-surface.md), [plan](../specs/staqex-v1-hamiltonian-library-surface-plan.md) | 0137+0139+showcase. |
| Open Topics before S1 (Option B) | **complete** | [LISS-0128](documentation-compression-map.md), [WP-0030](documentation-compression-map.md) | 0129–0133 + 0135 done; S1 shipped. |
| Open Topics permanent-out | **reopened** | [LISS-0152](documentation-compression-map.md), [note](../specs/staqex-v1-open-topics-permanent-out.md), [WP-0037](documentation-compression-map.md) | Pre-S1 out lifted 2026-07-31. Thin ships: ADR 0121–0122 / LISS-0153–0154. Follow-on WP-0038. |
| Permanent-out thin Kernel slices | **complete** (WP-0037) | ADR 0121–0122; LISS-0152–0154 | `Current`/`Temperature` dims; unary bare `\|\> f`. |
| Partial holes + SI `to` + design ADRs | **complete** (WP-0038) | [WP-0038](documentation-compression-map.md); ADR 0123–0128; LISS-0155–0160 | Ship Partial `_` + `expr to unit`; design boundaries for rational/PDF/live QPU/trait. |
| SI catalog wave-2 + KetLit fn args | **complete** (WP-0039) | [WP-0039](documentation-compression-map.md); ADR 0129–0130; LISS-0161–0162 | `ps`/`us`/`km`/`kHz`/`MHz` scales; user-fn KetLit Call args. |
| Stepwise Partial + eV↔J | **complete** (WP-0040) | [WP-0040](documentation-compression-map.md); ADR 0131–0132; LISS-0163–0164 | Left-to-right Partial fill; exact SI `eV`↔`J`. |
| Pipe hole fill + °C↔K | **complete** (WP-0041) | [WP-0041](documentation-compression-map.md); ADR 0133–0134; LISS-0165–0166 | Pipe fills leftmost `_`; affine Celsius↔Kelvin. |
| Fahrenheit + gram scale | **complete** (WP-0042) | [WP-0042](documentation-compression-map.md); ADR 0135–0136; LISS-0167–0168 | Affine °F↔K/C; `g`↔`kg`. |
| Pipeline Operator Fusion MVP | **complete** (WP-0043) | [WP-0043](documentation-compression-map.md); ADR 0137; LISS-0169 | Hold partial unseal; pure unary `fn` pipe chains fuse to one Joint pass. |
| Trace-Out GC fn-scope MVP | **complete** (WP-0044) | [WP-0044](documentation-compression-map.md); ADR 0138; LISS-0170 | Drop dead fn-local Joint axes after library `fn` Calls. |
| Interference prune MVP | **complete** (WP-0045) | [WP-0045](documentation-compression-map.md); ADR 0139; LISS-0171 | Amp-sum support merge + exact-zero prune via `Joint.merge_support`. |
| Deferred Pushforward MVP | **complete** (WP-0046) | [WP-0046](documentation-compression-map.md); ADR 0140; LISS-0172 | Eligible mains batch StateBind materialization at `measure`. |
| Algebraic Operator Fusion MVP | **complete** (WP-0047) | [WP-0047](documentation-compression-map.md); ADR 0141; LISS-0173 | Affine `scale·x+bias` collapse on unary pipe Fusion. |
| Evolve Trace-Out GC MVP | **complete** (WP-0048) | [WP-0048](documentation-compression-map.md); ADR 0142; LISS-0174 | Drop block-evolve `let` temps after exit. |
| Call/Partial pipe Fusion MVP | **complete** (WP-0049) | [WP-0049](documentation-compression-map.md); ADR 0143; LISS-0175 | One-hole Call/Partial stages in pipe Fusion. |
| Rankine affine | **complete** (WP-0050) | [WP-0050](documentation-compression-map.md); ADR 0144; LISS-0176 | `.R` ↔ K/F/C via Kelvin affine. |
| Imperial pound mass | **complete** (WP-0051) | [WP-0051](documentation-compression-map.md); ADR 0145; LISS-0177 | `.lb` ↔ kg/g (exact 0.45359237 kg). |
| Imperial ounce mass | **complete** (WP-0052) | [WP-0052](documentation-compression-map.md); ADR 0146; LISS-0178 | `.oz` ↔ lb/kg (16 oz = 1 lb). |
| Imperial stone mass | **complete** (WP-0053) | [WP-0053](documentation-compression-map.md); ADR 0147; LISS-0179 | `.st` ↔ lb/oz/kg (14 lb = 1 st). |
| Metric tonne mass | **complete** (WP-0054) | [WP-0054](documentation-compression-map.md); ADR 0148; LISS-0180 | `.t` ↔ kg (10³ kg). |
| Multi-hole Partial pipe fill | **complete** (WP-0055) | [WP-0055](documentation-compression-map.md); ADR 0149; LISS-0181 | Bare `|>` fills leftmost Partial hole; mid result may stay Partial. (Tuple simultaneous fill: ADR 0152.) |
| US/UK ton mass | **complete** (WP-0056) | [WP-0056](documentation-compression-map.md); ADR 0150; LISS-0182 | `.ton_us` = 2000 lb; `.ton_uk` = 2240 lb; share kg with `.t`. |
| Troy ounce mass | **complete** (WP-0057) | [WP-0057](documentation-compression-map.md); ADR 0151; LISS-0183 | `.oz_t` = 31.1034768 g; distinct from avoirdupois `.oz`. |
| Tuple multi-hole Fusion fill | **complete** (WP-0058) | [WP-0058](documentation-compression-map.md); ADR 0152; LISS-0184 | `(a,b) |> f(_, _)` fills all holes; Fusion peels tuple head. |
| Bare-block Trace-Out GC | **complete** (WP-0059) | [WP-0059](documentation-compression-map.md); ADR 0153; LISS-0185 | `{ let …; e }` BlockExpr; drop dead let axes. |
| Mixed-unit arithmetic reject | **superseded** (WP-0060) | ADR 0154 → [0155](decision-themes/dec-0004-type-first-scientific-model.md) | Reject-only policy withdrawn for shared-canonical families. |
| Mixed-unit canonical promote | **complete** (WP-0061) | [WP-0061](documentation-compression-map.md); ADR 0155; LISS-0187 | Mixed known units → canonical then `+`/`-`. |
| ADR 0057 showcase boundary | **complete** | [LISS-0131](documentation-compression-map.md) | Boundary doc only. |
| QPU capability honesty | **complete** | [LISS-0135](documentation-compression-map.md), [catalog](../specs/staqex-v1-qpu-capability-honesty.md) | Writable ≠ QPU-executable table. |
| Typed surface annotations | **complete** | [LISS-0129](documentation-compression-map.md), ADR 0115 | `state x: State<T> = …` shipped. |
| Expression residuals | **complete** | [LISS-0133](documentation-compression-map.md), ADR 0116 | LINEAR return, Float return, MULTI FP, Classical⊕State. |
| Physicist source friction ledger | **working** | [friction ledger](physicist-source-friction-ledger.md) | F-02/F-05 closed (ADR 0114 + LISS-0121); residual sample debt feeds P0; ledger seeds P1. Not an ADR. |
| Adjudicator language vision | **Accepted** (2026-07-31; **§2.2 Accepted 2026-08-08**) | [vision](adjudicator-language-vision.md) | Physicist-first; ideal form first; §2.1 writeable≠executable (= meaning vs realization, not “non-executable”); **§2.2 source denotes the same blackboard meaning** (intentional transform priority; composition stability); §3.1 Outer/Kernel/lanes; §6 Stop narrowed; §6.1 friction ops. Wired into agent contracts + spec §1.1. |
| HIR BinOp expr children | **complete** (LISS-0125) | [LISS-0125](documentation-compression-map.md), [suite](../../tests/test_liss_0125_hir_binop_expr_children_red.py) | `BinOp.lhs/rhs` walk; unblocks B03/A01 compile crash. |

| HIR → Physics IR lowering | **complete** (A–D) | [LISS-0115](documentation-compression-map.md) | `physics_ir_lower.py` + soft `CompileResult.physics_ir`; equations still explicit. **Do not reuse ID.** |
| Equation / Unit DTO | **complete** (Agent A A–C) | [LISS-0116](documentation-compression-map.md) | `physics_equation.py` shipped; not re-exported into frozen `physics_ir.py`. **Do not reuse ID.** |
| Source-backed Physics IR goldens | **complete** (Agent C A–C) | [LISS-0117](documentation-compression-map.md) | Loader + oscillator lowered-IR evidence; full six-family public oracle deferred. **Do not reuse ID.** |
| Body-level phase typing residuals | **complete** | [LISS-0118](documentation-compression-map.md) | A–C complete 2026-07-29: transitive taint, Report matrix, short-name fail-closed + catalog closeout. |
| Hybrid scientific workflow | Phase 4 reviewed | [LISS-0035](../issues/LISS-0035-hybrid-scientific-workflow.md), [ADR 0072](decision-themes/dec-0006-host-qpu-and-external-ports.md), [ADR 0073](decision-themes/dec-0006-host-qpu-and-external-ports.md) | Immutable provider-neutral Workflow/Job DTO boundary; declarative surface and named Host update callback, no provider SDK. |
| Continuous operators and discretization | Phase 3 reviewed | [LISS-0036](../issues/LISS-0036-continuous-operator-and-discretization-boundary.md), [ADR 0074](decision-themes/dec-0004-type-first-scientific-model.md), [LISS-0111](../issues/LISS-0111-continuous-discretization-numerical-lowering-mvp.md) | No hidden discretization; explicit contract and Theory-to-Kernel Bridge. MVP numerical lowering (`Position` + `UniformGrid` + periodic FD order 2) ships via `grid_hamiltonians` and Joint evolve. |
| POVM, measurement, and channel contracts | Phase 3 reviewed | [LISS-0037](documentation-compression-map.md); [ADR 0075](decision-themes/dec-0002-state-first-semantics-and-measurement.md); [WP-0014](../work-plans/WP-0014-povm-measurement-contract.md) | Terminal computational-basis measurement works for pure/mixed one-qubit states; general effects and dynamic measurement remain out of scope. |
| Semantic discrete carriers and phase-local types | Phase 3 reviewed | [LISS-0038](../issues/LISS-0038-semantic-discrete-carriers.md) | Separate dimensions, indices, counts, basis labels, and physical discrete values before indexed syntax; indexed syntax remains LISS-0030. |
| Numerical representation and continuous PDFs | Phase 3 reviewed | [LISS-0018](documentation-compression-map.md); [ADR 0076](decision-themes/dec-0004-type-first-scientific-model.md); [WP-0015](../work-plans/WP-0015-numeric-representation-policy.md) | Shared dependency-free f64/complex-f64 policy and non-repair validation are shipped; continuous PDFs and exact arithmetic remain deferred. |
| Observation checkpoints and execution diagnostics | Phase 3 reviewed | [LISS-0044](../issues/LISS-0044-observation-checkpoints-and-execution-diagnostics.md); [ADR 0089](decision-themes/dec-0002-state-first-semantics-and-measurement.md); [WP-0021](../work-plans/WP-0021-observation-checkpoints-and-execution-diagnostics.md) | Dependency-free Host observation requests/reports, simulator-only snapshot capability, no hidden measurement, explicit resource cost, and readability review are complete; execution adapters remain deferred. |
| Scientific input and parameter binding | Phase 3 complete | [LISS-0045](documentation-compression-map.md); [ADR 0090](decision-themes/dec-0004-type-first-scientific-model.md); [WP-0020](../work-plans/WP-0020-scientific-input-and-parameter-binding.md) | Dependency-free scalar Host input, `Param<T>` bindings, immutable sweeps, provenance validation, and readability refactor are complete; result-envelope integration and provider SDKs remain deferred. |
| JobResult observation integration | Phase 3 reviewed | [LISS-0046](../issues/LISS-0046-jobresult-observation-integration.md); [ADR 0091](decision-themes/dec-0006-host-qpu-and-external-ports.md); [WP-0022](../work-plans/WP-0022-jobresult-observation-integration.md) | Additive immutable `JobResult.observations` preserves existing positional construction and measurement separation; provider adapters, partial-result policy, and WorkflowReport composition remain deferred. |
| Local observation plan execution | Phase 3 reviewed | [LISS-0047](../issues/LISS-0047-local-observation-plan-execution.md); [ADR 0092](decision-themes/dec-0006-host-qpu-and-external-ports.md); [WP-0023](../work-plans/WP-0023-local-observation-plan-execution.md) | Dependency-free local adapter, deterministic fake source, portable reports, cost-only separate jobs, and hard unsupported-projection diagnostics are reviewed complete; provider/QPU execution remains deferred. |
| Resource profile manifest and simulator budget | Phase 3 reviewed; local execution wiring complete | [LISS-0062](documentation-compression-map.md); [LISS-0063](../issues/LISS-0063-simulator-resource-enforcement.md); [LISS-0064](../issues/LISS-0064-simulator-resource-execution-wiring.md); [ADR 0100](decision-themes/dec-0005-quantum-operations-and-runtime.md) | Host-side manifest/estimate boundary, provider-neutral Warn/Abort decision, and local run/QASM enforcement are complete. Provider submission and benchmark calibration remain deferred. |
| Host QPU submit orchestration | Phase 3 Refactor complete | [LISS-0065](documentation-compression-map.md); [LISS-0016](../issues/LISS-0016-host-qpu-submit.md); [ADR 0083](decision-themes/dec-0006-host-qpu-and-external-ports.md); [ADR 0103](decision-themes/dec-0006-host-qpu-and-external-ports.md) | Dedicated Host use case, explicit JobRequest/QpuArtifact mapping, fixed lifecycle, no partial measurements, explicit retry attempts, and provider-neutral orchestration are implemented and refactored. Provider SDK, credentials, network, and technology selection remain out of scope. |
| QPU observation/result integration | Phase 3 Refactor complete | [LISS-0066](documentation-compression-map.md); [ADR 0104](decision-themes/dec-0006-host-qpu-and-external-ports.md) | Host projector maps structured QPU payloads into ordered immutable JobResult observations, fails closed on incomplete results, preserves attempt metadata, and keeps separate jobs metadata-only; live provider integration remains deferred. |
| Numeric literal separators | Phase 3 Refactor complete | [LISS-0061](documentation-compression-map.md); [ADR 0101](decision-themes/dec-0004-type-first-scientific-model.md) | Java-compatible placement between digits is implemented; leading-underscore private identifiers remain unchanged; formatter and QPU provenance remain deferred. |

## Related open evaluations

These are broader research or technology questions already listed in the
architecture overview and remain unassigned unless a row above or a future
Issue gives them a concrete scope:

- Broader SI / atomic mass / bare `.ton` (WP-0062 / ADR 0156 when merged);
  **display-unit restore shipped**
  [ADR 0186](decision-themes/dec-0004-type-first-scientific-model.md) /
  [LISS-0314](documentation-compression-map.md)
  (LISS-0197 superseded);
  continuous PDF Kernel values (ADR 0126 boundary) — strategy
  [ADR 0162](decision-themes/dec-0006-host-qpu-and-external-ports.md); Host inject MVP
  [ADR 0163](decision-themes/dec-0006-host-qpu-and-external-ports.md) /
  [LISS-0195](documentation-compression-map.md) (**complete**);
  Host seam [ADR 0164](decision-themes/dec-0006-host-qpu-and-external-ports.md) /
  [LISS-0198](documentation-compression-map.md) /
  [WP-0068](documentation-compression-map.md) (**complete**);
  **finiteize surface shipped** [ADR 0185](decision-themes/dec-0004-type-first-scientific-model.md)
  Lane A / [LISS-0313](documentation-compression-map.md) **complete**
  (`finiteize` + B18); mid-program Continuous still deferred — **expressiveness
  seats** [scenarios](../specs/staqex-v1-continuous-lane-b-expressiveness-scenarios.md)
  / [LISS-0315](documentation-compression-map.md);
  **CH-field-compose baseline frozen weak** (Ideal §2A + Host 0317 + H→E 0318;
  [LISS-0319](documentation-compression-map.md));
  Joint rational mode still ADR 0125 (classical path: ADR 0160 shipped);
  numeric literal lifting: [LISS-0018](documentation-compression-map.md).
- Concrete live QPU provider **SDK** after honesty ports (ADR 0127);
  CredentialPort shipped ADR 0161: [LISS-0019](documentation-compression-map.md),
  [ADR 0077](decision-themes/dec-0006-host-qpu-and-external-ports.md).
- Trait specialization / effect-row surface examples (ADR 0128):
  [LISS-0196](documentation-compression-map.md) —
  **complete** (Adjudicator 採択 2026-08-03: examples accepted, **no ship ADR**)
  ([examples](../specs/staqex-v1-trait-effect-surface-examples.md)); no Kernel Red
  until a future ship ADR is Accepted separately.
- Whether numeric literals are sugar for `dirac`.
- **Kernel External Resources ports (ADR 0166) — shipped:**
  `RngPort` (WP-0082 / LISS-0235 / ADR 0170),
  `MeasureSinkPort` (WP-0083 / LISS-0236 / ADR 0171),
  `SourcePort` (WP-0084 / LISS-0237 / ADR 0172; below `load_module_graph`).
  Design [ADR 0166](decision-themes/dec-0006-host-qpu-and-external-ports.md) (**Accepted**) /
  [LISS-0218](documentation-compression-map.md) (**complete** — design).
  Binding constraint: seeded outputs must stay bit-identical.
- Dirac paper spelling `⟨φ|ψ⟩` as sugar over `inner`/`outer` (**shipped**
  WP-0081 / LISS-0234 / ADR 0169; ledger F-04):
  [ADR 0165](decision-themes/dec-0003-language-surface-and-physicist-first-dx.md) (**Accepted**) /
  [LISS-0217](documentation-compression-map.md) (**complete** — design).
- `inspect` vs measure teaching risk and circuit-vs-Hamiltonian lane choice
  (friction ledger F-06 / F-10, Class B, no ADR yet):
  [LISS-0219](documentation-compression-map.md) (**complete** — docs guidance).
- **Not open — decided:** user-defined operator overloading is out of scope per
  [ADR 0114 §D5](decision-themes/dec-0002-state-first-semantics-and-measurement.md).
  Friction ledger F-08 cites that decision
  ([LISS-0215](documentation-compression-map.md)
  **complete**).
- **Quantum mental-model follow-up:** remaining design is open under
  [WP-0092](../work-plans/WP-0092-quantum-mental-model-follow-up.md), following
  accepted [ADR 0189](adr/0189-quantum-mental-model-and-observation-contract.md)
  (§2 and the related Consequences bullet superseded in part by ADR 0190).
  The first `DiagnosticView<T>` compiler classification shipped in PR #342
  (`abaa7cb`). The `mix` canonical grammar and `when` hard-retirement
  diagnostic also shipped, in PR #337 (`321de3a`), under ADR 0190/WP-0093
  Phase 2 approval. The `superpose` formal grammar/AST/type boundary is also
  shipped, [LISS-0320](../issues/LISS-0320-superpose-formal-grammar.md) /
  PR #345: `superpose (control) { pat -> expr, … }` parses to a distinct
  `SuperposeExpr` (never `WhenExpr`/`Mixture`), type-checks to `State<T>`,
  and fails closed with `COHERENT_EXECUTION_UNSUPPORTED` if a program tries
  to evaluate it — coherent amplitude/phase execution and target/QASM
  lowering remain separate, unimplemented slices. Specification approval and
  Phase 1 approval remain required before the remaining `controlled`
  grammar, the scientific lexicon, conformance scenarios, or the public
  observation-surface changes. Work unit 6 (H1 theory/experiment diagnostic
  honesty, added 2026-08-05 from the
  [kernel stub and placeholder registry](kernel-stub-and-placeholder-registry.md)
  audit) closed all three misleading-diagnostic gaps in `h1_authoring.py`,
  work unit 6 now **complete**:
  [LISS-0325](../issues/LISS-0325-h1-non-hermitian-operator-diagnostic.md)
  (`NON_HERMITIAN_OPERATOR_ERROR` now consults `parameter_types` instead of
  identifier spelling) shipped, PR #359 (`765ed17`).
  [LISS-0326](../issues/LISS-0326-h1-basis-target-capability-diagnostics.md)
  (`BASIS_MISMATCH_ERROR`/`TARGET_CAPABILITY_REJECT`) shipped, PR #361
  (`632e96e`): new `basis`/`coordinate`/top-level `realize` AST (previously
  discarded entirely by the parser — `realize` did not even parse) and a
  real `target_capability.py`-backed capability lookup replace both
  substring heuristics.
- **S02 drug-discovery benchmark:** [ADR 0190](adr/0190-s02-selection-boundary-and-mix-control.md)
  (Accepted; Phase 2 implementation approved 2026-08-04),
  [WP-0093](../work-plans/WP-0093-s02-language-expressiveness-and-selection.md),
  and [S02 spec](../specs/staqex-v1-s02-drug-discovery-benchmark.md). The
  `mix`/`controlled` language-surface slice (work unit A) is implemented and
  shipped (PR #337) — `mix` is canonical, `when` is a hard `RETIRED_KEYWORD`
  diagnostic, `controlled` is not lowered to `Mixture`. Work unit B (Host
  domain records and finite-manifest witness) is implemented and shipped,
  Host-side only ([LISS-0321](../issues/LISS-0321-s02-host-domain-and-finite-boundary.md) / PR #349):
  `Candidate`/`Constraint`/`Score`/`TargetProfile`/`SelectionProblem` and
  `FiniteManifestWitness`/`validate_manifest()` under
  `examples/showcase/S02_drug_discovery/host/`; no `compiler/staqex/**`
  change. Work unit C's semantics/type contract is Accepted via
  [ADR 0192](adr/0192-s02-projector-selection-semantics.md) (2026-08-05) —
  a structured `constraint_ref`, a fixed three-predicate vocabulary
  (`exactly_selected`/`pairwise_compatible`/`diversity_at_least`), Host-side
  objective normalization, and penalty-vs-Projector disposition tracking.
  Its Kernel-touching slice is implemented and shipped
  ([LISS-0322](../issues/LISS-0322-s02-projector-region-semantics.md) /
  PR #352): `_append_selection_projector_region`'s `constraint_ref` is now
  derived from the actual recognized predicate names instead of the
  hardcoded `"S02.feasible"` literal, and an unrecognized predicate fails
  closed with `S02_UNKNOWN_CONSTRAINT_PREDICATE`. The Host-side
  `ConstraintDisposition`/`objective_profile` fields (ADR 0192 Follow-up
  item 2) remain a separate, unstarted Issue. Work unit D
  (observation/result contract) is implemented and shipped, Host-side only
  ([LISS-0323](../issues/LISS-0323-s02-observation-matrix-and-benchmark-result.md) /
  PR #354): a `BenchmarkResult`-shaped Host DTO maps already-shipped
  Kernel primitives (non-destructive `expect`, terminal `measure`,
  `MeasurementEnvelope.vacuum`) into the S02 result contract — an empty or
  vacuum terminal measurement is recorded as a failed result, never a
  fabricated selection or score; no `Selection` Kernel type was added.
  Work unit E's first slice — real `prepare_selection(n: Int)` as a Kernel
  op — is implemented and shipped
  ([LISS-0324](../issues/LISS-0324-s02-prepare-selection.md) / PR #363,
  `746d002`): `Evaluator._bind_prepare_selection` produces an equal
  superposition over all `2^n` selection patterns via the same
  `Joint.bind_split` primitive `coin()`/`finiteize(...)` use; `measure`
  needed no change. Real `project ... onto feasible(...)` runtime
  execution is also now shipped, via
  [ADR 0194](adr/0194-host-input-port-and-selection-predicate-semantics.md)
  (Accepted) and its two Follow-up Issues:
  [LISS-0327](../issues/LISS-0327-host-input-port-foundation.md) (new
  `HostInputPort`, PR #366, `b1ce2bd`) and
  [LISS-0328](../issues/LISS-0328-selection-projector-predicate-execution.md)
  (real predicate execution for `exactly_selected`/`pairwise_compatible`/
  `diversity_at_least`, PR #368, `73580d3`). The remaining work unit E
  scope (conformance scenarios, classical baselines, and the first
  actually-runnable S02 `.sqx` program) remains open — no S02 example
  program exists yet; S01 disaster-response
  showcase is unchanged.
- **ASCII quantum notation:** **complete — PR #339 merged 2026-08-04** under
  [ADR 0191](adr/0191-ascii-quantum-notation-and-lexical-boundary.md),
  [WP-0094](../work-plans/WP-0094-ascii-quantum-notation.md), and the
  [acceptance specification](../specs/staqex-v1-ascii-quantum-notation.md).
  Unicode source forms are removed. Tensor alias parity, arity, factor-order,
  and grouping tests are green. Completion packet synchronized after merge.
- **Real ℏ and dimensioned Hamiltonian dynamics:** [ADR 0195](adr/0195-real-hbar-hamiltonian-dynamics.md)
  (Accepted), [WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md).
  Work unit 1 (Kernel primitive) is **complete**
  ([LISS-0330](../issues/LISS-0330-real-hbar-kernel-primitive.md) / PR #376,
  `29f2ee8`): `evolve`'s formula changed from `exp(-iHt)` (natural units)
  to `exp(-iHt/hbar)` with ℏ's real SI value; a bare dimensionless
  duration now fails closed (`EVOLVE_UNRESOLVED_UNIT_ERROR`). Work unit 2
  (`A03_h2_vqe`, first example migration) is also **complete**
  ([LISS-0332](../issues/LISS-0332-a03-h2-real-unit-migration.md) / PR
  #381, `510e860`). Work unit 3 (`A05_qaoa_portfolio`) is also
  **complete** ([LISS-0333](../issues/LISS-0333-a05-qaoa-arbitrary-unit-migration.md)
  / PR #383, `8d36278`) — A05 models an abstract QUBO cost function, not
  a real physical system, so its coefficients are given real
  `Energy`/`Time` dimensions but honestly documented as arbitrary
  problem-defined cost units, not physical constants (contrast with
  A03). Work unit 4 (`A06_topological_edge_memory`) is also **complete**
  ([LISS-0334](../issues/LISS-0334-a06-ssh-real-unit-migration.md) / PR
  #385, `780707a`) — A06 models a real physical model class (the SSH
  tight-binding chain), so its hopping amplitudes are given real
  `eV`-scale `Energy` values (ratio preserved), documented as physically
  plausible but not literature-traced to a specific measurement — a
  third honesty category between A03 and A05. Work unit 5
  (`A10_mission_observatory`) is also **complete**
  ([LISS-0335](../issues/LISS-0335-a10-mission-observatory-real-unit-migration.md)
  / PR #387, `556d459`) — same SSH honesty category as A06; also surfaced
  a Kernel limitation (the fail-closed check doesn't recognize
  dimensioned struct-field-access durations, worked around, not fixed —
  see WP-0095's "Related, not blocking"). An urgent interleaved Kernel
  fix ([LISS-0336](../issues/LISS-0336-evolve-real-unit-canonicalization-bugs.md)
  / PR #389, `bbd7c06`) then corrected two independent bugs found live
  during work unit 6 design intake: a coalescing epsilon that silently
  zeroed real Joule-scale Hamiltonian coefficients (confirmed to have
  broken A05's `evolve` entirely) and a missing Time-unit-to-seconds
  canonicalization for the evolve duration (affected all four merged
  examples). A05/A06/A10 are re-verified to now show real, non-trivial
  evolution; A03 was found to be affected by a third, separate,
  pre-existing bug (`op_n_qubits` undercounting for Jordan-Wigner-mapped
  Operators), deferred to its own new Issue, not yet fixed.
  **Correction (2026-08-07, LISS-0350)**: `op_n_qubits`'s undercount was
  itself only a symptom — the true root cause, found while finally
  filing that deferred Issue, was `second_quantization.py::jordan_wigner_map`'s
  absolute `_ZERO_TOL`/`_REAL_TOL` thresholds silently zeroing A03's
  entire real-Joule-scale (~1e-18) electronic Hamiltonian (six orders of
  magnitude below the fixed `1e-12` epsilon). **A03's `evolve` produced
  no real H2 electronic-structure dynamics from LISS-0332's real-unit
  migration until this fix landed** — its own test only checked
  "compiles, runs, non-vacuum measurement," which a global-phase-only
  evolution (from the surviving `nuclear_repulsion * I` term alone)
  still satisfied, so the bug went uncaught through LISS-0332, LISS-0336,
  and WP-0095's closure. See LISS-0350 below for the fix and a
  systematic audit confirming no other example or `spec_verification`
  suite fixture was exposed to the same bug class. **By explicit
  Adjudicator decision this real-unit migration is a real, one-time
  change with no natural-units fallback**. [LISS-0337](../issues/LISS-0337-spec-verification-suite-real-unit-fixtures.md)
  (PR #390, `339ae99`) then migrated 5 `spec_verification` suites' own
  internal test fixtures (never updated for ADR 0195, previously
  crashing outright) to real units, restoring `spec_verification`'s full
  161-case reporting. Work unit 6 (`A11_noether_forge`) is also
  **complete** ([LISS-0338](../issues/LISS-0338-a11-structural-monitoring-magnetometer.md)
  / PR #392, `42ca5ed`) — rethemed from the rejected/deferred Noether
  Forge theme to a structural-monitoring quantum magnetometer (real
  D≈2.87GHz NV-center physics, Doherty et al. 2013), with all 14 module
  files genuinely wired. Found and fixed a real Kernel bug (struct
  constructor calls from within an imported function's own body failed
  at runtime); found and documented (not fixed) three further
  classical-language gaps — see WP-0095's "Related, not blocking". Work
  unit 7 (`B04_evolve_not_loops`) is also **complete**
  ([LISS-0339](../issues/LISS-0339-b04-evolve-not-loops-real-unit-migration.md)
  / PR #394, `084feb4`) — reused LISS-0337's `sv17` fix pattern for the
  legacy bare-Pauli-letter evolve form (not ℏ-divided), no new findings.
  Work unit 8 (`B07_structure_visibility`) is also **complete**
  ([LISS-0340](../issues/LISS-0340-b07-structure-visibility-real-unit-migration.md)
  / PR #396, `f385df8`) — `IsingParams.J`/`.h` became real `Energy`
  (qubit-Pauli sparse path, genuinely needed real-scaled values); the
  struct-field-derived duration (`scale * 0.25`) became an independent
  `Time` literal, since unit suffixes only attach to literals, not
  expressions. Work unit 9 (`B08_operators_hamiltonians`) is also
  **complete** ([LISS-0341](../issues/LISS-0341-b08-operators-hamiltonians-real-unit-migration.md)
  / PR #398, `45fe41d`) — found and fixed a real Kernel bug in the same
  systemic category as LISS-0336/0338: `backend/qasm/trotter.py`'s
  Suzuki gate-angle computation was never updated for ADR 0195's real-ℏ
  formula, silently collapsing real-unit QASM3 Trotter emission into an
  "idle" no-op circuit — confirmed general, not B08-specific.
  `spec_verification` reached **161/161 (100%, Gate: PASS)**, but this
  is scoped to that suite's own 161 cases, **not** a complete repository
  audit: `B16_effect_marking` was confirmed still unmigrated (simply not
  exercised by any `spec_verification` suite). Work unit 10
  (`B16_effect_marking`) is also **complete**
  ([LISS-0342](../issues/LISS-0342-b16-effect-marking-real-unit-migration.md)
  / PR #400, `adf63b4`) — identical fix pattern to B08, no new findings;
  a bonus pre-existing test also flipped to passing. **All
  `examples/basics`/`examples/applied` entries are now confirmed
  migrated** (checked directly, not inferred from `spec_verification`
  alone). Work unit 11 (`quantum_matter_discovery`) is also **complete**
  ([LISS-0343](../issues/LISS-0343-typecheck-classical-payload-and-quantum-matter-discovery-migration.md)
  / PR #402, `fbf0f58`)
  — `IsingCouplings.J`/`.h` and `QuenchSchedule.duration` became real
  `Energy`/`Time`, propagated through the struct-field-typed free
  functions' return types (a multi-file showcase slice, unlike the
  single-file B04/B07/B08/B16 migrations). Found and fixed a fifth
  instance of the same systemic category:
  `typecheck.py::_infer_binop`'s Classical `+`/`-` branch hardcoded its
  result payload to `"Float"` regardless of operand payload (the
  dimension itself was tracked correctly), so `Energy + Energy`
  type-checked as `Classical<Float>` with an `Energy` dimension, failing
  `RETURN_TYPE_MISMATCH` against a declared `-> Energy` return. Fixed
  with a payload check that preserves a non-bare-numeric operand's
  payload and otherwise falls back to the existing `Int + Int -> Float`
  legacy convention (confirmed load-bearing by an existing passing
  test — using the shared `_promote()` helper as-is would have broken
  it, caught before shipping). **Bonus fix**: the locked S01
  disaster-response spine test independently hit the same bug and now
  passes — S01's own migration (work unit 12+) is still not done. The
  sibling Classical `*`/`/` branches are suspected to have the identical
  hardcoded-payload issue but were not touched (no live repro forces
  that path yet). Work unit 12 (S01 lock-boundary + energy-scale
  survey, `main_fuel_search`) is also **complete**
  ([LISS-0344](../issues/LISS-0344-s01-fuel-search-real-unit-migration.md)
  / PR #404, `2c62100`)
  — confirmed the migrations don't conflict with the S01 lock boundary
  (value-internal retype only); found 3 of the 5 S01 files reference
  implicit-coefficient-1 Hamiltonians that are numerically meaningless
  under real ℏ for any human-scale duration (confirmed live:
  `RUNTIME_ERROR: evolve magnitude |H*t/hbar| ~= 2**61 exceeds the
  sparse evolution step budget`); adopted a shared `ops_energy_scale()
  -> Energy` function (new, purely-additive file, A05-style
  arbitrary-unit honesty category) multiplied in at each Hamiltonian's
  call site, requiring no changes to the existing shared factory
  functions. `main_fuel_search` itself needed only the established
  B04-pattern fix. Work unit 13 (`main_lattice_four`) is also
  **complete**
  ([LISS-0345](../issues/LISS-0345-s01-lattice-four-real-unit-migration.md)
  / PR #406, `1c1b2c6`)
  — first file to add `physics/ops_energy_scale.sqx`; found and
  corrected two implementation wrinkles during Green (not new Kernel
  bugs): `scale * <factory call>()` written inline fails
  `RUNTIME_ERROR: cannot compile sparse Pauli for OpCall` (the
  Operator-compiler's scalar multiplication only recognizes a `Var`
  operand, needs pre-binding), and an inline unit-suffixed literal in
  the `for` clause doesn't satisfy the fail-closed duration check
  either (`duration_unit` is only resolved for a bare `Var`, needs its
  own `Time`-typed variable) — both apply to every remaining S01
  Hamiltonian-wrapping migration. Work unit 14 (`main_morning_collect`)
  is also **complete**
  ([LISS-0346](../issues/LISS-0346-s01-morning-collect-real-unit-migration.md)
  / PR #408, `c1ab33f`)
  — `Operator H = Z` wrapped with `ops_energy_scale()` using work unit
  13's confirmed pattern; no new findings, Green passed on the first
  attempt. Work unit 15 (`main_day2_recovery`) is also **complete**
  ([LISS-0347](../issues/LISS-0347-s01-day2-recovery-real-unit-migration.md)
  / PR #410, `cde5191`)
  — the first of the two `ConstraintCoeffs`-based files (shared with
  `main_disaster_response`); `ConstraintCoeffs` itself stays `Float`
  (per work unit 12's confirmed design), `recovery_hamiltonian(coeffs)`
  wrapped with the same pattern; no new findings, confirming it holds
  equally for a computed-`Float`-weighted Hamiltonian, not just the
  coefficient-1 case. Work unit 16 (`main_disaster_response`, the
  flagship "tonight spine") is also **complete**
  ([LISS-0348](../issues/LISS-0348-s01-disaster-response-real-unit-migration.md)
  / PR #412, `f22d78a`)
  — all 4 Hamiltonians wrapped with `ops_energy_scale()` (including its
  first use on a `product(...)`-built Hamiltonian, `corridor_product()`,
  confirmed the scale applies once to the whole assembled result, not
  distributed into factors); 3 of 4 evolve durations needed B07's
  independent-`Time`-literal workaround (confirmed live a computed
  dimensionless `Float` cannot be `to`-converted to `Time` either). No
  new Kernel findings — every constituent pattern was already proven;
  this Issue combined them in one file for the first time. **Bonus
  fix**: all 3 `test_s01_tonight_ticket_export.py` cases (depend on
  this file running end-to-end) flipped from failing to passing.
  **WP-0095 is now complete** — every ADR 0195-affected `.sqx` example
  is confirmed migrated. See the "Repository health" note below.
- Living backlog: WP-0062–0068 shipped; next free WP-0096+ / LISS-0331+.

## Repository health (2026-08-02; regression note added 2026-08-05)

Root suites and spec-verification were green locally and gated in CI as
of 2026-08-02:

- Blocking `kernel-tests`: `python3 -m pytest tests/ -q` (WP-0080 / LISS-0209).
- Blocking `spec-verification`: `python3 tests/spec_verification/run_all.py`
  (WP-0086 / LISS-0241).
- Floor observed 2026-08-02: **1084+** pytest passed; SV gate **161/161**.

**2026-08-05: `main` currently does not meet this floor, by explicit,
tracked, ADR-approved design** — see "Real ℏ and dimensioned Hamiltonian
dynamics" above. After work unit 5 (`A10_mission_observatory`, PR #387)
landed, `pytest tests/ -q` reported 1203 passed / 60 failed (down from 63
— A10 no longer contributes a failure, plus three more bonus fixes to
tests exercising A10's legacy multi-file/capstone source;
`test_applied_catalog_health_red.py` now only lists A11 as failing);
`spec_verification` reported 136/145 (+1 vs. work unit 4's 135/145). The
LISS-0336 Kernel bug fix (PR #389) that followed added its own 2 tests
without changing this count: `pytest tests/ -q` reported 1205 passed /
60 failed; `spec_verification` stayed at 136/145.

**2026-08-05, LISS-0337**: investigating PR #390's CI failure found the
136/145 figure conflated two different categories: 4 already-tracked
WP-0095 unmigrated examples, and **5 `spec_verification` suites whose own
internal test fixtures had never been updated for ADR 0195** and were
crashing outright (`sv17_quantum_mechanics_syntax`,
`sv19_arbitrary_hamiltonian`, `sv27_fock_quadrature`, `sv28_sparse_pauli`,
`sv29_position_grid_ho` — an uncaught `KernelDiagnosticError`/`ValueError`
per suite, collapsing each suite's many individual cases into one
"suite-crash" placeholder). Migrating those 5 suites' fixtures to real
units restored `spec_verification`'s reporting to its full, un-collapsed
case count: **156/161** (96.89%) — matching the 161-case total from the
2026-08-02 healthy floor. Only 5 cases remain failing, all directly
attributable to the 4 already-tracked WP-0095 examples (`B08` appears
twice: once directly, once via a cross-reference in `sv19`). `pytest
tests/ -q` remains 1205 passed / 60 failed (unchanged — LISS-0337 only
touched test fixtures and one small QASM-backend gap it surfaced, not
Kernel evolve semantics). This SV/pytest state is expected to persist
until WP-0095's remaining work units (6+) migrate every affected example.
Do not "fix" these failures by reverting LISS-0330 or reintroducing a
natural-units fallback — that would undo an
explicit Adjudicator decision.

**2026-08-06, LISS-0338**: work unit 6 (`A11_noether_forge`) landed (PR
#392, `42ca5ed`). `pytest tests/ -q` reported **1206 passed / 57
failed** (-3 vs. LISS-0337's 60 — A11 and the two `noether_forge`
structural test files' pre-existing failures resolved;
`test_applied_catalog_health_red.py`'s failure list is now **empty**);
`spec_verification` reported **157/161** (97.52%, +1 vs. LISS-0337's
156/161).

**2026-08-06, LISS-0339**: work unit 7 (`B04_evolve_not_loops`) landed
(PR #394, `084feb4`). `pytest tests/ -q` reported **1207 passed / 57
failed** (unchanged failure count, +1 this Issue's own new test);
`spec_verification` reported **158/161** (98.14%, +1 vs. LISS-0338's
157/161).

**2026-08-06, LISS-0340**: work unit 8 (`B07_structure_visibility`)
landed (PR #396, `f385df8`). `pytest tests/ -q` reported **1208
passed / 57 failed** (unchanged failure count, +1 this Issue's own new
test); `spec_verification` reported **159/161** (98.76%, +1 vs.
LISS-0339's 158/161).

**2026-08-06, LISS-0341**: work unit 9 (`B08_operators_hamiltonians`)
landed (PR #398, `45fe41d`), along with a real QASM-backend ℏ fix (see
"Real ℏ and dimensioned Hamiltonian dynamics" above). `pytest tests/ -q`
reported **1209 passed / 57 failed** (unchanged failure count, +1 this
Issue's own new test); `spec_verification` reported **161/161 (100%,
Gate: PASS)** — the first fully-green SV run since the ADR 0195
regression began. **This did not mean the regression was fully closed**:
`B16_effect_marking` (confirmed unmigrated, `EVOLVE_UNRESOLVED_UNIT_ERROR`)
and the 5 locked S01 files plus `quantum_matter_discovery` were simply
not exercised by any `spec_verification` suite, so were never counted.

**2026-08-06, LISS-0342**: work unit 10 (`B16_effect_marking`) landed
(PR #400, `adf63b4`) — identical fix pattern to B08, no new findings.
`pytest tests/ -q` now reports **1211 passed / 56 failed** (-1 vs.
LISS-0341's 57 — a bonus pre-existing test also flipped to passing);
`spec_verification` remains **161/161 (100%, Gate: PASS)** (B16 isn't
exercised by any SV suite, so this number is unchanged by design).
**All `examples/basics`/`examples/applied` entries are now confirmed
migrated** (checked directly). Only the 5 locked S01 files and
`quantum_matter_discovery` remain, expected to persist until WP-0095's
remaining work units (11+) migrate each. Do not "fix" these failures by
reverting LISS-0330 or reintroducing a natural-units fallback — that
would undo an explicit Adjudicator decision.

**2026-08-06, LISS-0343**: work unit 11 (`quantum_matter_discovery`)
landed, along with a `typecheck.py` Classical `+`/`-` payload-collapse
Kernel fix (see "Real ℏ and dimensioned Hamiltonian dynamics" above).
`pytest tests/ -q` reports **1215 passed / 55 failed** (-1 vs.
LISS-0342's 56 — a bonus pre-existing test,
`test_showcase_s1_thin_slice_red.py::test_s1_spine_compiles_and_runs`,
independently hit the same Classical `+`/`-` bug and now passes; +3 this
Issue's own new tests); `spec_verification` remains **161/161 (100%,
Gate: PASS)** (`quantum_matter_discovery` isn't exercised by any SV
suite, unchanged by design). Only the 5 locked S01 files remain,
expected to persist until WP-0095's work unit 12+ migrates each — these
need their own explicit lock-boundary check first, not just a value
substitution (see WP-0095 work unit 12+).

**2026-08-06, LISS-0344**: work unit 12 (S01 lock-boundary +
energy-scale survey, `main_fuel_search`) landed. Confirmed no
lock-boundary conflict for any of the 5 S01 files (value-internal
retype only). Found 3 of the 5 reference implicit-coefficient-1
Hamiltonians that are numerically meaningless under real ℏ for any
human-scale duration — adopted a shared `ops_energy_scale()` function
(A05-style arbitrary-unit honesty category, no changes needed to the
existing shared factory functions). `main_fuel_search` itself needed
only the established B04-pattern fix. `pytest tests/ -q` reports
**1216 passed / 55 failed** (unchanged failure count vs. LISS-0343's
55, +1 this Issue's own new test); `spec_verification` remains
**161/161 (100%, Gate: PASS)** (`main_fuel_search` isn't exercised by
any SV suite, unchanged by design). Only the remaining 4 S01 files
persist, expected until WP-0095's work unit 13+ migrates each in the
sequenced order (`main_lattice_four` → `main_morning_collect` →
`main_day2_recovery` → `main_disaster_response`).

**2026-08-06, LISS-0345**: work unit 13 (`main_lattice_four`) landed,
adding `physics/ops_energy_scale.sqx`. Found and corrected two
implementation wrinkles during Green (not new Kernel bugs, resolved by
testing directly): `scale * <factory call>()` written inline fails
`RUNTIME_ERROR: cannot compile sparse Pauli for OpCall` (needs
pre-binding to a local `Operator` variable first), and an inline
unit-suffixed literal in the `for` clause doesn't satisfy the
fail-closed duration check either (needs its own `Time`-typed
variable) — both apply to every remaining S01 Hamiltonian-wrapping
migration. `pytest tests/ -q` reports **1217 passed / 55 failed**
(unchanged failure count vs. LISS-0344's 55, +1 this Issue's own new
test); `spec_verification` remains **161/161 (100%, Gate: PASS)**
(`main_lattice_four` isn't exercised by any SV suite, unchanged by
design). Only the remaining 3 S01 files persist, expected until
WP-0095's work unit 14+ migrates each in the sequenced order
(`main_morning_collect` → `main_day2_recovery` →
`main_disaster_response`).

**2026-08-06, LISS-0346**: work unit 14 (`main_morning_collect`)
landed. `Operator H = Z` wrapped with `ops_energy_scale()` using work
unit 13's confirmed pattern (pre-bind before `scale *`, duration as its
own `Time` variable) — no new findings, Green passed on the first
attempt. `pytest tests/ -q` reports **1218 passed / 55 failed**
(unchanged failure count vs. LISS-0345's 55, +1 this Issue's own new
test); `spec_verification` remains **161/161 (100%, Gate: PASS)**
(`main_morning_collect` isn't exercised by any SV suite, unchanged by
design). Only the remaining 2 S01 files persist, expected until
WP-0095's work unit 15+ migrates each in the sequenced order
(`main_day2_recovery` → `main_disaster_response`).

**2026-08-06, LISS-0347**: work unit 15 (`main_day2_recovery`) landed.
`Operator H = recovery_hamiltonian(coeffs)` (a `ConstraintCoeffs`-
weighted Hamiltonian, not coefficient-1) wrapped with
`ops_energy_scale()` using work unit 13's confirmed pattern —
`ConstraintCoeffs` itself stays `Float`, no new findings, confirming
the wrap-at-call-site pattern holds equally for a computed-`Float`-
weighted Hamiltonian. `pytest tests/ -q` reports **1219 passed / 55
failed** (unchanged failure count vs. LISS-0346's 55, +1 this Issue's
own new test); `spec_verification` remains **161/161 (100%, Gate:
PASS)** (`main_day2_recovery` isn't exercised by any SV suite,
unchanged by design). Only `main_disaster_response` (the flagship
"tonight spine", 4 Hamiltonians, 4 durations) persists, expected until
WP-0095's work unit 16 migrates it.

**2026-08-06, LISS-0348**: work unit 16 (`main_disaster_response`, the
flagship "tonight spine") landed — **WP-0095's final work unit**. All 4
Hamiltonians (`H_drive`, `H_damage`, `H_flood`, `H_corridor`) wrapped
with `ops_energy_scale()`, including its first use on a
`product(...)`-built Hamiltonian (`corridor_product()` — the scale
applies once to the whole assembled result, not distributed into
factors). 3 of 4 evolve durations (`t_drive`, `t_damage`, `t_corridor`)
needed B07's independent-`Time`-literal workaround — confirmed live a
computed dimensionless `Float` cannot be `to`-converted to `Time`
either (`DIMENSION_MISMATCH_ERROR: [1] vs [Time]`). No new Kernel
findings; every constituent pattern was already proven by prior work
units. `pytest tests/ -q` reports **1223 passed / 52 failed** (**-3**
vs. LISS-0347's 55 — bonus fix: all 3 `test_s01_tonight_ticket_export.py`
cases, which depend on this file running end-to-end, flipped from
failing to passing; +1 this Issue's own new test); `spec_verification`
remains **161/161 (100%, Gate: PASS)** (`main_disaster_response` isn't
exercised by any SV suite, unchanged by design).

**WP-0095 is now complete.** Every ADR 0195-affected `.sqx` example
(`examples/basics`, `examples/applied`,
`examples/showcase/quantum_matter_discovery`,
`examples/showcase/S01_quantum_disaster_response`) is confirmed
migrated to real ℏ / real Energy-Time units. `main` no longer carries
any ADR-approved real-unit regression from this program.

**2026-08-06, LISS-0349** (PR #414, `e1b0797`; standalone, not part of WP-0095):
`typecheck.py::_infer_binop`'s Classical `*`/`/` branch, flagged as a
*suspected* sibling of LISS-0343's already-fixed `+`/`-`
hardcoded-payload bug but left unfixed for lack of a live repro, is now
confirmed and fixed. Repro: `Energy / Length -> Force` failed
`RETURN_TYPE_MISMATCH` (dimension computed correctly, payload name
stayed `"Float"`). Fixed by mirroring the same function's
already-correct State-side `*`/`/` implementation
(`_payload_for_dim(dim, _promote(...))`, deriving the payload from the
*result* dimension — the right tool for `*`/`/`, which produce a new
physical dimension, unlike `+`/`-`, which preserve the operands'
shared one). No regression this time (unlike LISS-0343's `+`/`-` fix):
`_payload_for_dim`'s dimensionless fallback already matches the
existing `Int`/`Float` legacy convention, confirmed via the
already-shipped, already-tested State-side sibling using the identical
helper. `pytest tests/ -q` reports **1225 passed / 52 failed**
(unchanged failure count vs. WP-0095's closing baseline, +2 this
Issue's own new tests); `spec_verification` remains **161/161 (100%,
Gate: PASS)**.

**2026-08-07, LISS-0350** (PR #416, `add8447`; standalone, not part of WP-0095): while
finally filing the `op_n_qubits` Jordan-Wigner qubit-undercount Issue
deferred since LISS-0336, found the undercount was only a symptom.
`second_quantization.py::jordan_wigner_map`'s absolute `_ZERO_TOL`
(`1e-12`) silently dropped every term of A03_h2_vqe's real-Joule-scale
(~1e-18) electronic Hamiltonian, collapsing `H_electronic` to a bare
zero literal — **A03's `evolve` has produced no real H2
electronic-structure dynamics since its own real-unit migration
(LISS-0332)**, undetected through LISS-0332, LISS-0336, and WP-0095's
closure because A03's test only checks "compiles, runs, non-vacuum
measurement" (satisfied by the surviving `nuclear_repulsion * I`
global-phase term alone). Fixed by mirroring
`sparse_pauli.py::_coalesce`'s already-shipped scale-relative pattern
(LISS-0336) for both `_ZERO_TOL` and its sibling `_REAL_TOL`
(non-Hermitian-residual check, same latent-risk mechanism, fixed
together though not yet observed causing wrong output). A systematic
audit of every other absolute numeric threshold in
`compiler/staqex/runtime/` and `compiler/staqex/` confirmed no other
location is exposed to the same bug class (all others operate on
dimensionless, normalized quantities — Born-rule probability,
quantum-amplitude, or an already-ℏ-divided dimensionless matrix
exponent), and confirmed no other shipped example or `spec_verification`
suite fixture uses Jordan-Wigner mapping with real-unit-scale
coefficients. `pytest tests/ -q` reports **1227 passed / 52 failed**
(unchanged failure count vs. LISS-0349's 52, +2 this Issue's own new
tests); `spec_verification` remains **161/161 (100%, Gate: PASS)**.
`examples/applied/A03_h2_vqe/main_h2_vqe.sqx` itself is unchanged — the
bug and fix are entirely in the Kernel's JW-mapping pipeline; A03's
own literature-cross-validation claim
(`docs/research/2026-08-05-h2-two-orbital-jordan-wigner-cross-validation.md`)
has not yet been independently re-verified against the now-corrected
measurement output — flagged as follow-up, not done here.

**2026-08-07, LISS-0351** (PR #418, `4eb91ad`; standalone, not part of WP-0095): performed
that follow-up. Extracted A03's actual compiled `H_electronic` Pauli-
term coefficients (post-LISS-0350) and converted Joules back to
Hartree — all six match the research note's derived/literature values
(O'Malley et al. 2016 Table 1, via the ENCCS reproduction) to the
source's own 4-decimal precision, and `g0_electronic + E_nn` matches
the literature's full `g0 = 0.2252 Ha` to within `0.013%`. This
confirms LISS-0350's fix produced the numerically correct physics, not
merely nonzero physics. Automated as
`tests/test_liss_0351_a03_jw_literature_crosscheck_red.py`; the
research note's own "Follow-up (not yet done)" section is updated in
place to record this. `pytest tests/ -q` reports **1229 passed / 52
failed** (unchanged failure count vs. LISS-0350's 52, +2 this Issue's
own new tests); `spec_verification` remains **161/161 (100%, Gate:
PASS)**.

**2026-08-07, LISS-0352** (PR #420, `eeafbb8`; standalone, not part of WP-0095): fixes one
of LISS-0338's documented, deferred "Related, not blocking" gaps —
Classical relational comparisons (`>`,`<`,`>=`,`<=`) mistyped as
`Classical<Float>` instead of `Classical<Bool>`.
`typecheck.py::_infer_binop`'s Classical branch had no explicit
`RELATIONAL` case, falling through to its `Classical<Float>` catch-all
fallback — fixed by mirroring the already-correct State-side
`RELATIONAL` case 8 lines below in the same function. `pytest tests/ -q`
reports **1230 passed / 52 failed** (unchanged failure count vs.
LISS-0351's 52, +1 this Issue's own new test); `spec_verification`
remains **161/161 (100%, Gate: PASS)**.

**2026-08-07, LISS-0353** (PR #422, `dbeb100`; standalone, not part of WP-0095): fixes
another of LISS-0338's documented, deferred "Related, not blocking"
gaps — no execution path for free functions that return a struct type.
Turned out to be 3 compounding gaps, not one, only visible one at a
time as each was fixed: (1) the top-level struct-typed-binding dispatch
always assumed the RHS call was the struct's own constructor, never
considering it could be a free function that internally constructs and
returns the struct; (2) `_eval_classical_call`'s `classical_heads` gate
excluded struct return types entirely; (3) `_construct_struct` (and its
`_eval_struct_arg` helper) had no way to resolve an enclosing free
function's own local parameters, only globally-registered
`self.objects` names — so a struct constructed inside that function's
own `return Point(a, b)` failed to resolve `a`/`b` even after (1)-(2)
were fixed. All three fixed; `_construct_struct`/`_eval_struct_arg` now
accept and thread an optional caller-local frame, backward compatible
at every pre-existing call site (defaults to `None`). `pytest tests/ -q`
reports **1233 passed / 52 failed** (unchanged failure count vs.
LISS-0352's 52, +3 this Issue's own new tests); `spec_verification`
remains **161/161 (100%, Gate: PASS)**. `_construct_instance` (the
equivalent path for classes, not structs) was not audited or touched —
flagged for a future Issue if a class-returning free function is ever
needed.

**2026-08-07, ADR 0196**: triaging the last of LISS-0338's documented
gaps (`&&` unsupported in expression position) found this is not an
oversight bug like the other three — `staqex-type-system.md`'s own
normative table already lists short-circuit `&&`/`||` under "Deferred
/ research (do not implement in Kernel)," since classical short-circuit
conflicts with the project's own accepted "every overloaded op on
`State<T>` is a pushforward, never an early collapse" principle
(`dec-0002`). [ADR 0196](adr/0196-boolean-total-pushforward-logical-operators.md)
is the design work that spec itself names as required first: `&&`/`||`
as **total-pushforward** operators (both operands always evaluated,
truth-table-combined per Joint world, no short-circuit), added as a new
general-expression grammar production separate from the Operator-DSL's
existing, unaffected binder-guard `&&`/`||`. `!` (logical NOT) is
explicitly out of scope, left for a future ADR. **Accepted** by the
Adjudicator (2026-08-07) — acceptance approves the semantics and
grammar-insertion approach only; implementation is a separate Local
Issue with its own Plan approval, not yet started.

**2026-08-07, LISS-0354** (PR #425, `fcda1c6`; standalone, not part of WP-0095): implements
ADR 0196. `_logical_or`/`_logical_and` grammar levels added between
`_pipe` and `_comparison`; `typecheck.py` Classical/State cases (Bool-
only, `TYPE_MISMATCH` otherwise); `_apply_op` truth-table cases.
Concretely verified the "total pushforward, not short-circuit"
property via a 400-trial seed sweep on two independent fair coins each
mapped to `State<Bool>` and combined with `&&`: `P(true) ≈ 0.25`,
matching the theoretical product of two independent fair coins —
would not match if evaluation had incorrectly short-circuited per
world. **Found and updated (Adjudicator-confirmed) a real regression
in two pre-existing tests**
(`test_binder_compound_where_red.py::test_classical_ampersand_outside_where_still_errors`,
`test_binder_where_or_red.py::test_statement_or_still_errors`) that
asserted `Float && Float` must be a parse-level rejection — exactly
the pre-ADR-0196 behavior this ADR superseded; both renamed and
updated to assert the new contract (parses cleanly, `TYPE_MISMATCH`
at typecheck). `dec-0002-state-first-semantics-and-measurement.md`
updated per ADR 0188's DEC-page-update rule. `pytest tests/ -q`
reports **1237 passed / 52 failed** (unchanged failure count vs. the
established baseline, no new failures — +4 this Issue's own new
tests, net of the 2 pre-existing tests' updated assertions);
`spec_verification` remains **161/161 (100%, Gate: PASS)**.

**Correction (2026-08-07)**: LISS-0354 originally flagged a suspected
`mix` type-inference quirk here (`mix (coin_result) { 0 ->
dirac(false), else -> dirac(true) }` without an explicit `State<Bool>`
annotation reportedly inferring payload `"Coin"` from the scrutinee
instead of `"Bool"` from the arm bodies). Re-investigated directly:
this does **not** reproduce, not even at LISS-0354's own merged commit
(`fcda1c6`) — `typecheck.py`'s `WhenExpr` inference already correctly
derives payload from the arm bodies, never the scrutinee. The original
finding was almost certainly a documentation error (likely tested
against an intermediate, not-yet-finished state of LISS-0354's own
`typecheck.py` work), not a persistent Kernel bug. No fix needed; the
"separate future Issue" flagged here is withdrawn.

**2026-08-07, LISS-0355** (PR #427, `62d2285`; standalone, not part of WP-0095): while
investigating `abs()`'s missing classical-scalar implementation
(LISS-0338's last documented gap), found `typecheck.py::_infer_binop`'s
Classical-vs-bare-literal mixing branch (originally written to allow
`pi / 2.0`-style expressions) unconditionally hardcoded **every**
operator's result to `Classical<Float>`, discarding not just payload
naming (like the four sibling bugs LISS-0343/0349/0352/0354 already
fixed for the variable-vs-variable case) but the operand's **dimension
itself** — confirmed live: `fn scale(e: Energy) -> Energy { return e *
2.0 }` failed `DIMENSION_MISMATCH_ERROR: [Energy] vs [1]`, the `Energy`
dimension silently dropped. Root cause: the branch's `other` variable
was the *literal's own* Ty (always trivially dimensionless), not the
actual Classical operand's, so it fired for any Classical operand
paired with a bare literal, via any operator. Blast-radius grep across
`examples/` found exactly one coincidental match
(`recovery.sqx`'s `effect_on_rescue * 10.0`), unaffected since already
dimensionless `Float` — **no shipped example was actually broken**.
Fixed by reinterpreting the literal side as genuinely Classical before
any kind-based dispatch runs, letting the already-correct "Classical ⊕
Classical" logic handle it uniformly; the now-dead hardcoded branch was
removed. `pytest tests/ -q` reports **1241 passed / 52 failed**
(unchanged failure count vs. LISS-0354's 52 — confirmed via full
failure-list diff, not just count, identical before and after; +4 this
Issue's own new tests); `spec_verification` remains **161/161 (100%,
Gate: PASS)**. `abs()`'s own classical-scalar implementation remains
open, deferred to its own follow-up Issue.

**2026-08-07, LISS-0356** (PR #429, `32b0852`; standalone, not part of WP-0095): closes the
follow-up named above and the last item in LISS-0338's documented
backlog. `stdlib/math_ops.py::MATH_OPS` (`sin`, `cos`, `exp`, `sqrt`,
`abs`, `log`, `tan`) was consumed only via `joint.map_coord` (a State-
pushforward path) — a classical-scalar call (`Float y = abs(x)` inside
an ordinary classical free function) had no evaluator support at all,
failing `RUNTIME_ERROR: call cannot be classical value in Phase 2.2
value context` at runtime despite compiling successfully (typecheck.py
has no `MATH_OPS` awareness; unrecognized function calls fall through
to a permissive `State<Any>` default that happens to satisfy any
declared classical type). Confirmed the identical gap in all seven
`MATH_OPS` entries, not just `abs()` as LISS-0338 named — fixed the
whole family together (Adjudicator-confirmed scope), not just `abs()`.
Fixed in `evaluator.py::_eval_classical_call`: check
`math_ops.known_math_op` before the `self.funs` lookup, evaluate the
single argument classically, apply `math_ops.apply_math` (reusing the
same implementation the quantum `map_coord` path already uses).
`typecheck.py` left untouched — its existing permissive fallback
already lets this pattern compile. `pytest tests/ -q` reports **1249
passed / 52 failed** (unchanged failure count vs. LISS-0355's 52,
confirmed via full failure-list diff; +8 this Issue's own new tests);
`spec_verification` remains **161/161 (100%, Gate: PASS)**.

**This closes every item in LISS-0338's original "Related, not
blocking" backlog** (Float relational mistyping — LISS-0352; struct-
returning free functions — LISS-0353; `&&` — ADR 0196/LISS-0354;
`abs()`/`MATH_OPS` — LISS-0356), plus the deeper, previously-unknown
bugs found while fixing them (Classical `*`/`/` payload — LISS-0349;
the JW-mapping absolute-epsilon regression that had silently zeroed
A03's Hamiltonian since LISS-0332 — LISS-0350/0351; Classical-vs-bare-
literal mixing discarding dimension — LISS-0355).

**2026-08-07, LISS-0357** (PR #432, `8f25c61`; standalone, not part of
WP-0095): fixes the
"Related, not blocking" item flagged in LISS-0335 (2026-08-05).
`evaluator.py::_hamiltonian_evolve_one_step`'s ADR 0195 fail-closed
`evolve ... for <duration>` unit check only recognized a bare `Var`
duration (`isinstance(expr.duration, Var)`), rejecting both a
dimensioned struct-field access (`evolve ... for config.duration`,
LISS-0335's finding) and an inline unit-suffixed literal (`evolve ...
for 0.25.fs`, LISS-0345's finding) with `EVOLVE_UNRESOLVED_UNIT_ERROR`
even though both genuinely carry a resolvable `Time` unit. Fixed by
replacing the narrow check with a single call to the already-correct
`_eval_value_with_unit` (used elsewhere for unit-aware `+`/`-`
arithmetic), which already generalizes `Var`, struct-field `Attr` (via
ADR 0174 `field_units`), and literal-suffix `Attr` resolution — one
change fixes both gaps, since they share the identical root cause.
ADR 0195's fail-closed behavior for genuinely dimensionless durations
is unchanged and covered by a dedicated regression test. `pytest tests/
-q` reports **1252 passed / 52 failed** (unchanged failure count vs.
LISS-0356's 52, confirmed via full failure-list diff; +3 this Issue's
own new tests); `spec_verification` remains **161/161 (100%, Gate:
PASS)**.

**2026-08-08, LISS-0358** (PR #434, `693d395`; standalone, not part of
WP-0095): a general architectural audit (requested by the Adjudicator
after LISS-0357, to check for other instances of the same "narrow
AST-shape dispatch" bug category) found three `evaluator.py` functions
(`_bind_call`, `_eval_classical_method_call`,
`_resolve_operator_method_call`) independently gating `recv.method(...)`
resolution on `isinstance(recv_expr, Var) and recv_expr.name in
self.objects`, rejecting a nested-field receiver
(`outer.inner.method()`) even though `typecheck.py` already
type-checks it generally. Fixed with a shared
`_resolve_receiver_instance` helper (mirrors the existing `_attr_host`
pattern), applied identically at all three sites. Verifying the third
(Operator-returning) site surfaced a same-category bug one layer up:
`parser.py::_type_first_bind`'s LISS-0139 heuristic for `Operator H =
recv.method()` used a fixed 4-token lookahead recognizing only exactly
one dotted hop before the call, so `outer.inner.h()` failed to even
parse; fixed with a new `_dotted_call_lookahead` helper accepting any
depth of dotted hops. `pytest tests/ -q` reports **1256 passed / 52
failed** (identical failure list vs. LISS-0357's 52, confirmed via
direct list comparison; +4 this Issue's own new tests);
`spec_verification` remains **161/161 (100%, Gate: PASS)**.

The audit also investigated and ruled out (false positives, already
general or structurally necessary) the tensor `*|*` bind, the
`converged(state)` predicate argument, the Operator-DSL `OpExpr`
index/register grammar, `WhenExpr`/`SuperposeExpr` inference/binding,
and the `Var`-arg fast paths in classical/Operator method-call
argument binding.

**2026-08-08, LISS-0359** (PR #437, `9eacfc8`;
[WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
work unit 1 of 8): migrates the 4 `EVOLVE_UNRESOLVED_UNIT_ERROR`
failures using the legacy single-Pauli-letter `evolve ψ under X for t`
path (`pauli_u`, no `ℏ` reference) to real `Time` units. Test-fixture-
only, no Kernel source change. Caught and corrected an error in
WP-0096's own investigation before any test was edited: the unit
suffix must be `.s` specifically (canonical seconds, scale factor 1),
not `.fs` (canonicalizes ×1e-15, silently producing a near-zero
rotation instead of the intended angle) — live-verified before
committing to the fix. `pytest tests/ -q` reports **1260 passed / 48
failed** (exactly -4 vs. LISS-0358's 52, confirmed via full
failure-list diff); `spec_verification` remains **161/161 (100%, Gate:
PASS)**. 48 known failures remain across WP-0096's remaining 7 work
units.

**2026-08-08, LISS-0360** (PR #439, `80c0353`;
[WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
work unit 2 of 8): migrates 14 `EVOLVE_UNRESOLVED_UNIT_ERROR` failures
(WP-0096's own investigation had undercounted this group as 13,
corrected during Red) across 6 files composing their Hamiltonian via
the Operator-DSL `sum`/`product` binder machinery, scaling by
`K = ℏ/1fs` with duration numerals kept unchanged and `.fs` appended
(preserves `H·t/ℏ` exactly). Found and fixed a real regression during
Green: wrapping a binder expression's whole top-level RHS in `K` breaks
`qpu_ir["binder_lowering"]` provenance tracking in two files; corrected
to inject `K` inside each binder body instead (mathematically
identical). Found and fixed a genuine, previously-undiscovered Kernel
bug, confirmed with the Adjudicator before including it in this Issue:
`backend/qasm/trotter.py::_eval_float`'s `Attr` unit-suffix handling
used a local, independently-hardcoded Time-unit-scale table that
predated ADR 0195's `ps`/`fs` additions and had gone stale — replaced
with a lookup against `dimensions.py`'s own `UNIT_SCALE_TO_CANONICAL`.
`pytest tests/ -q` reports **1274 passed / 34 failed** (exactly -14 vs.
LISS-0359's 48, confirmed via full failure-list diff); `spec_
verification` remains **161/161 (100%, Gate: PASS)**. 34 known
failures remain across WP-0096's remaining 6 work units.

**2026-08-08, LISS-0361** (PR #441, `8e44252`;
[WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
work unit 3 of 8): migrates the last 4 `EVOLVE_UNRESOLVED_UNIT_ERROR`
failures concerning periodic-boundary (`wrap()`) and acting-space
typing (`test_liss0057_periodic_boundary_red.py`,
`test_liss0058_acting_space_typing_red.py`), applying the same
`K = ℏ/1fs` coefficient scale / `.fs`-suffixed duration conversion
established in LISS-0360. No new Kernel gap found this time — the
pattern applied cleanly. `pytest tests/ -q` reports **1278 passed / 30
failed** (exactly -4 vs. LISS-0360's 34, confirmed via full
failure-list diff); `spec_verification` remains **161/161 (100%, Gate:
PASS)**. 30 known failures remain across WP-0096's remaining 5 work
units.

**2026-08-08, LISS-0362** (PR #443, `bead530`;
[WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
work unit 4 of 8): migrates 19 `EVOLVE_UNRESOLVED_UNIT_ERROR` failures
(WP-0096's own investigation had undercounted this group as 18,
corrected during Red) across 10 files where the Hamiltonian's
coefficient reaches `Operator H = ...` through a function/method
return, a struct/class field, or a classical multi-bind — applying
`K = ℏ/1fs` scaling at each coefficient's actual source rather than at
the `Operator` expression itself. One file
(`test_liss0051_operator_factory_runtime_red.py`) needed no direct
edit, since it re-exports its failing test from
`test_liss0107_examples_linker_runtime_red.py` and was fixed
transitively. One new pattern required declaring a `Schedule` class's
duration field/init-parameter/`t()`-return chain `Time`-typed (not
`Float`) so unit tracking propagates through a method-returned
duration — confirmed live before implementing, no Kernel change
needed. Kept as one Issue rather than splitting (flagged as a
candidate in WP-0096's own investigation) after full-file review found
the conversion pattern fully uniform. `pytest tests/ -q` reports
**1297 passed / 11 failed** (exactly -19 vs. LISS-0361's 30, confirmed
via full failure-list diff); `spec_verification` remains **161/161
(100%, Gate: PASS)**. 11 known failures remain across WP-0096's
remaining 4 work units.

**2026-08-08, LISS-0363** (PR #445, `77c177f`;
[WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
work unit 5 of 8): migrates the last 3 `EVOLVE_UNRESOLVED_UNIT_ERROR`
failures concerning explicit Suzuki/Trotter step policy
(`test_explicit_trotter_steps_red.py`,
`test_liss_0270_experiment_surface_profile_red.py`,
`test_liss_0280_0288_sugar_red.py`), applying the established
`K = ℏ/1fs` conversion. Verified a larger duration numeral (100.0)
does not overflow the sparse-evolution step-budget check, and that a
shared fixture's two currently-passing QASM-emission tests (which
never reach the runtime fail-closed duration check) are unaffected. No
new Kernel gap found. `pytest tests/ -q` reports **1300 passed / 8
failed** (exactly -3 vs. LISS-0362's 11, confirmed via full
failure-list diff); `spec_verification` remains **161/161 (100%, Gate:
PASS)**. 8 known failures remain across WP-0096's remaining 3 work
units.

**2026-08-08, LISS-0364** (PR #447, `800584b`;
[WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
work unit 6 of 8): migrates the 4 `EVOLVE_UNRESOLVED_UNIT_ERROR`
failures in `test_jordan_wigner_mapping_red.py`, each comparing a
`FermionOperator` mapped via `map(H, JordanWigner)` against a
hand-written equivalent Pauli `Operator` — both sides scaled
identically by `K = ℏ/1fs` so the marginal-equality comparison remains
meaningful. Found a real syntax constraint during design intake:
neither wrapping the whole `FermionOperator` RHS in parens nor scaling
the already-mapped `QubitOperator` result parses/type-checks; resolved
with a per-term `K *` prefix instead (mirrors the Pauli-sum body-
injection pattern from earlier work units, applied to the Fermionic
ladder-operator grammar), live-verified end-to-end including the
marginal comparisons before Red. `pytest tests/ -q` reports **1304
passed / 4 failed** (exactly -4 vs. LISS-0363's 8, confirmed via full
failure-list diff); `spec_verification` remains **161/161 (100%, Gate:
PASS)**. 4 known failures remain across WP-0096's remaining 2 work
units.

**2026-08-08, LISS-0365** (PR #449, `bbb5a18`;
[WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
work unit 7 of 8): migrates the 2 `EVOLVE_UNRESOLVED_UNIT_ERROR`
failures in `test_continuous_lowering_red.py` (the position-grid/
continuous Hamiltonian discretization bridge — `theory`/
`discretization`/`use ... as` DSL). Resolves WP-0096's own flagged open
question: the grid Hamiltonian path uses the same `expm_ih` primitive
WP-0095 work unit 1 updated together with the sparse-Pauli path, so
the identical `K = ℏ/1fs` constant applies — confirmed live via
Born-rule norm preservation and bridge-vs-direct marginal equality
before Red. `pytest tests/ -q` reports **1306 passed / 2 failed**
(exactly -2 vs. LISS-0364's 4, confirmed via full failure-list diff);
`spec_verification` remains **161/161 (100%, Gate: PASS)**. Only 2
known failures remain, both in WP-0096's final work unit 8.

**2026-08-08, LISS-0366** (PR #451, `31a9bd5`;
[WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
work unit 8 of 8, **final**): migrates the last 2
`EVOLVE_UNRESOLVED_UNIT_ERROR` failures
(`test_operator_pauli_atom_call_parse_red.py`,
`test_when_ket_prepare_arms_red.py`). **This closes WP-0096 in its
entirety and resolves the "`main` currently does not meet this floor"
note recorded above on 2026-08-05** — `pytest tests/ -q` now reports
**1308 passed, 0 failed**, the first fully green root-suite run since
the ADR 0195 real-ℏ migration began. `spec_verification` remains
**161/161 (100%, Gate: PASS)**. WP-0096 ran as 8 sequential Issues
(LISS-0359 through LISS-0366), each with its own Plan/Completion
approval, migrating 52 test-fixture `evolve` durations off the
pre-ADR-0195 dimensionless convention via a behavior-preserving
`H·t/ℏ`-conserving scale identity — no test's physics or numeric
assertions were altered, only their unit declarations. Two genuine,
previously-undiscovered Kernel bugs were found and fixed along the way
(both confirmed narrow-blast-radius and Adjudicator-approved before
inclusion): `backend/qasm/trotter.py::_eval_float`'s stale local
Time-unit table (LISS-0360) and the provenance-tracking constraint on
top-level binder-expression scaling (also LISS-0360, worked around
without a Kernel change). See
[WP-0096](../work-plans/WP-0096-tests-real-hbar-duration-migration.md)
for the full work-unit-by-work-unit record.

**2026-08-08, LISS-0367** (PR #453, `92c6a56`; standalone, not part of
WP-0096): closes a parser gap found and deliberately deferred during
LISS-0364 (WP-0096 work unit 6). `parser.py::_second_quantized_rhs_
is_op_dsl` — the heuristic deciding whether a `FermionOperator`/
`BosonOperator`/`SpinOperator`/`QubitOperator`-typed bind's RHS parses
via the Operator-DSL or the general expression grammar — skipped a
parenthesized group's contents opaquely when scanning for a leading
scalar-coefficient chain, never checking whether the second-quantized
atom was itself *inside* the parens (`K * (create[0] *
annihilate[0])` failed with a confusing `PARSE_ERROR`, forcing
LISS-0364's workaround of dropping the parens). Fixed by scanning
inside a skipped group for an `IDENT[` pattern before falling through
to the compound-coefficient assumption. `pytest tests/ -q` reports
**1312 passed, 0 failed** — `main` remains fully green; `spec_
verification` remains **161/161 (100%, Gate: PASS)**.

**2026-08-08, LISS-0368** (PR #455, `0682e1a`; standalone, not part of
WP-0096): a second architectural audit (requested after LISS-0367, same
"narrow AST-shape dispatch" category) found and fixed two gaps in
`second_quantization.py`'s Jordan-Wigner mapping: `_orbital_index` only
accepted a literal integer index, rejecting a named integer local
carrying the identical value (`Int site = 0; create[site]`); and
`_scalar_value` only recognized `*` as a scalar `OpBin`, rejecting a
compound coefficient combined with `+`/`-` (`(a + b) * create[0] *
annihilate[0]`). Both fixed by mirroring already-correct sibling logic
in the same file. Notable: LISS-0367's own regression guard already
used the `(a + b) * ...` shape but only asserted parse success, never
execution — this execution-time gap was invisible to it. `pytest
tests/ -q` reports **1316 passed, 0 failed** — `main` stays fully
green; `spec_verification` remains **161/161 (100%, Gate: PASS)**.

**2026-08-08, LISS-0369** (PR #457, `421edf6`; standalone, not part of
WP-0096): closes the fourth candidate from the second architectural
audit (LISS-0368 covered the other two). `parser.py::_type_first_bind`'s
ADR 0118 / LISS-0149 gate for `Float[M…] row = h[i]` only recognized a
bare variable name immediately followed by `[`; a struct/class-field
array (`m.h[1]`) fell through to the general expression grammar and
failed with a misleading `PARSE_ERROR`. Fixed with
`_dotted_index_lookahead`, mirroring `_dotted_call_lookahead`'s
pattern from LISS-0358. **Scope note**: applying the fix surfaced a
second, larger gap — `typecheck.py::_check_float_partial_bind` has no
struct/class field-array shape-tracking anywhere in the codebase, so
`m.h[1]` still does not fully compile; confirmed with the Adjudicator
to keep this Issue's scope as originally approved (parser-only) —
`m.h[1]` now reaches the correct grammar and surfaces the accurate ADR
0118 `TYPE_MISMATCH` instead of the misleading `PARSE_ERROR`, a real
diagnostic-quality improvement even though full field-array-indexing
support remains a separate, unimplemented future Issue (would need a
`field_shapes`-style tracking mechanism analogous to ADR 0174's
`field_units`). `pytest tests/ -q` reports **1318 passed, 0 failed** —
`main` stays fully green; `spec_verification` remains **161/161 (100%,
Gate: PASS)**.

**2026-08-08, LISS-0370** (PR #459, `de176cf`; standalone, not part of
WP-0096): closes the fourth and final candidate from the second
architectural audit (LISS-0368/0369 covered the other three), re-
verified with corrected combining syntax after the first repro attempt
failed for unrelated reasons. `adjoint(create[i])` (physically
equivalent to `annihilate[i]`) failed in three different contexts with
three different errors, all tracing to `second_quantization.py::
_expand` having no case at all for `OpCall`. Unlike LISS-0368/0369
(mirroring already-correct sibling recognition patterns), this
required implementing new mapping logic — verified for physical
correctness two ways before implementation: analytically (every term's
Pauli-tensor factor is Hermitian, so `(c·Op)† = c̄·Op`) and numerically
(conjugating `_create(0)`'s terms exactly reproduces `_annihilate(0)`'s
terms). Required three fix sites, not the two anticipated at Plan time
— a third gap (`finite_binder.py::_substitute_indices` not recursing
into `OpCall`, so a binder's index variable never got substituted
inside `adjoint(...)`) was found only while confirming Green for the
binder-body case. `pytest tests/ -q` reports **1321 passed, 0 failed**
— `main` stays fully green; `spec_verification` remains **161/161
(100%, Gate: PASS)**.

**This closes the second architectural audit's full candidate list**
(LISS-0368/0369/0370 — three real, live-verified bugs fixed; the audit
also flagged and ruled out several false positives, recorded in each
Issue's own design decision section).

**2026-08-08, LISS-0371** (PR #461, `24a63ad`; standalone, not part of
WP-0096): first candidate from a third architectural audit round.
`using Suzuki(order = ord, steps = M)` (`ord` a named `Int` constant
equal to a literal that already works) was spuriously rejected with
`SUZUKI_ORDER_ERROR`. **Self-correction recorded here**: the first
finding reported this as a *silent* wrong-output bug — verified by
calling `QASM3Emitter.emit_unit()` directly without first checking
`compiled.ok`, unlike every other call site in this codebase. Properly
re-verifying (`compile_source(...).ok` checked first) showed the
program is actually hard-rejected at typecheck time — the same
spurious-rejection category as every other finding this session, not a
new, more severe one. The fix still required genuinely new
infrastructure, unlike LISS-0368/0369's mirror-an-existing-sibling
fixes: `typecheck.py` had zero constant-folding/static-value tracking
anywhere (`grep` for `_fold`/`_const_fold`/`self.scalars` returned
nothing). Added `self.static_scalars: dict[str, float]`, populated at
the two places a plain classical scalar bind's value becomes known
(`check_unit`'s main-loop and `_check_function_body`, the latter with
its own save/restore swap so a function's locals never leak across
scopes), and widened `_check_suzuki_policy` to resolve a named constant
through it. The runtime layer's three independently duplicated
literal-only `order` checks (`trotter.py::resolve_suzuki_steps`,
`lower.py::_lower_evolve`'s inline copy, `qpu_ir.py::
_lowering_policy_projection`) were also deduplicated behind one new
`trotter.py::resolve_suzuki_order` helper, mirroring LISS-0360's
dedup principle. `pytest tests/ -q` reports **1324 passed, 0 failed**
— `main` stays fully green; `spec_verification` remains **161/161
(100%, Gate: PASS)**.

**2026-08-08, LISS-0372** (PR #463, `fe73ced`; standalone, not part of
WP-0096): second and final candidate from the third architectural audit
round (LISS-0371 covered the first). `apply(rx(theta), q)` with a named
`Float` variable angle (equal to a literal that already works) silently
dropped the gate from the emitted QASM entirely, with both
`compiled.ok` and `emitted.ok` reporting `True` — re-verified against
the LISS-0371 lesson (checking both `ok` flags before inspecting
output) and confirmed this one really is silent, unlike LISS-0371.
Root cause: `lower.py::_rotation_angle` (the same narrow-AST-shape-
dispatch category) only recognized `LitFloat`/`LitInt`/a prelude-
constant `Var`/a `pi/N` `BinOp`. Fixed in two parts: (1) widened
`_rotation_angle` to resolve a named `Var` through the same `scalars`
dict `_from_ast_patterns` already builds before the `apply(...)`
lowering loop runs (the dict/naming convention LISS-0371 established);
(2) converted the remaining unresolvable-angle fallback from a silent
note-and-continue into an explicit rejection
(`reject_code = QASM_ROTATION_ANGLE_UNRESOLVED`), mirroring the
already-correct `STATIC_HILBERT_RESOURCE_ERROR` sibling pattern a few
dozen lines earlier in the same function — a larger semantics change
than LISS-0371's recognition-only widening, explicitly approved by the
Adjudicator before implementation given a dropped gate is a more severe
failure mode than a fallback to a different-but-still-valid value.
`pytest tests/ -q` reports **1326 passed, 0 failed** — `main` stays
fully green; `spec_verification` remains **161/161 (100%, Gate:
PASS)**.

**This closes the third architectural audit's full candidate list**
(LISS-0371/0372 — two real, live-verified bugs fixed; LISS-0371's
initial "silent" framing was self-corrected to "spurious rejection"
during verification, while LISS-0372 was independently confirmed
genuinely silent using the corrected verification method).

**2026-08-08, LISS-0373** (PR #465, `2951c4e`; standalone): first
candidate from a fourth architectural audit round (LISS-0374 tracks the
round's second candidate). `sum (i in Index<0..2>, j in Index<0..2>)
where i == next(j) { ... }` — a `where` guard using the `next(...)`
index accessor, the same accessor that already works correctly in an
indexed operator body (`Z[next(i)]`) — crashed `compile_source()`
itself with an **uncaught `ValueError`** ("where guard must use static
binder indices"), propagating all the way out of the public compiler
API. This is the most severe finding of the entire session: every prior
narrow-AST-shape-dispatch bug produced at worst a diagnostic (spurious
rejection) or a value silently propagating with an `ok=True` result;
this one crashed the compiler outright for a physically plausible
program (a nearest-neighbor guard). Root cause: `_static_value` (used
only for `where`-guard evaluation) called the narrow
`_resolve_bound_index` (`OpVar`/`OpLit` only) and raised unconditionally
when it returned `None`, while the already-correct, more general
`_resolve_index` (already handling `next`/`wrap` via
`_resolve_accessor`) sat unused one function away. Fixed by threading a
`_Context` through `_static_value`/`_guard_matches`/`_binder_values`
(which already computed everything a `_Context` needs, just after the
point the guard check ran) and having `_static_value` call
`_resolve_index` directly — eliminating the narrow duplicate rather
than widening it. Live-verified correct semantics, not just absence of
crash: the `next(j)`-guard Hamiltonian emits the identical 3-`rz`-gate
QASM as the hand-written equivalent `Z[1]*Z[0] + Z[2]*Z[1]`. `pytest
tests/ -q` reports **1328 passed, 0 failed** — `main` stays fully
green; `spec_verification` remains **161/161 (100%, Gate: PASS)**.

**2026-08-08, LISS-0374** (PR #467, `a7783c0`; standalone): second and
final candidate from the fourth architectural audit round (LISS-0373
covered the first). `⟨0|psi|1⟩` (`psi`: `State`) correctly raises
`OPERATOR_ALGEBRA_TYPE_ERROR`; the equivalent-shaped misuse through a
class method returning `State` (`⟨0|b.getPsi|1⟩`) silently compiled
clean — `typecheck.py::_check_matrix_element_middle` bailed for any
non-`Var` callee shape, the same nested-`Attr`-receiver-dispatch
category as this session's very first round (LISS-0357/0358). Fixed by
widening the callee-shape recognition to a single-level
`Attr(Var, name)`, resolved through `self.fun_returns` — the same table
`check_unit` already populates for every class method with a return
type, already used elsewhere for method-call return-type inference — no
new lookup infrastructure needed. `pytest tests/ -q` reports **1330
passed, 0 failed** — `main` stays fully green; `spec_verification`
remains **161/161 (100%, Gate: PASS)**.

**This closes the fourth architectural audit's full candidate list**
(LISS-0373/0374 — two real, live-verified bugs fixed, one of them
(LISS-0373) this session's most severe finding: an uncaught crash in
the public compiler API, not merely a diagnostic-quality issue).

**2026-08-08, LISS-0375** (PR #469, `fe29104`; standalone): first
candidate from a fifth architectural audit round (LISS-0376 tracks the
round's second candidate). The ADR 0045 `NESTED_WHEN_ERROR` static
coherence guard correctly rejects a `mix` nested directly inside
another `mix`'s arm, but silently missed the identical violation when
embedded inside a `*|*` tensor-product statement —
`nested_when.py::_walk` had cases for `BinOp`/`Call`/`Attr`/`Dirac`/
`Inspect`/`Pipe`/`Lambda`/`TupleExpr`/`EvolveExpr`/`WhenExpr` but none
for `TensorExpr`. **Verification note recorded in the Issue**: the
first repro attempt (binding the nested `mix` to its own name in a
separate statement, then tensor-combining it in a second statement)
produced a false negative — `check_nested_when` checks each
statement's own top-level expression independently, and a bind
statement whose `.expr` is itself a `WhenExpr` was already correctly
covered regardless of this gap. The corrected repro embeds the nested
`mix` directly inside the tensor expression at the same statement,
confirming the actual gap. Fixed by adding a `TensorExpr` case to
`_walk`, mirroring the existing `BinOp`/`Pipe` two-operand cases
immediately above it. `pytest tests/ -q` reports **1332 passed, 0
failed** — `main` stays fully green; `spec_verification` remains
**161/161 (100%, Gate: PASS)**.

**2026-08-08, LISS-0376** (PR #470, `2cd8950`; standalone): second and
final candidate from the fifth architectural audit round (LISS-0375
covered the first). `unitarity_check.py::_expr_is_quantum` (feeds the
`quantum`/`strict` tracking dicts the ADR 0045/0052 non-unitary-
transform guard uses) had no case for `SuperposeExpr` — LISS-0320's
coherent-lane surface, "structurally parallel to `WhenExpr`" per
`SuperposeArm`'s own docstring — so a `superpose(...)`-bound state was
silently tracked as non-quantum, skipping every subsequent non-unitary-
transform check on it. **Currently non-exploitable**: any
`superpose(...)`-bound state already fails at runtime with
`COHERENT_EXECUTION_UNSUPPORTED` (a separate, deliberate LISS-0320
fail-closed gate), so this static-analysis gap could not yet produce a
silently-wrong measured result — fixed as regression prevention so it
does not resurface, harder to trace, once superpose coherent execution
ships. Fixed by adding a `SuperposeExpr` case mirroring the existing
`WhenExpr` case immediately above it exactly. `pytest tests/ -q`
reports **1332 passed, 0 failed** — `main` stays fully green;
`spec_verification` remains **161/161 (100%, Gate: PASS)**.

**This closes the fifth architectural audit's full candidate list**
(LISS-0375/0376 — two real, live-verified bugs fixed; LISS-0376 is
notable for being a confirmed real gap that is nonetheless currently
dormant/non-exploitable, a new nuance this session's audit taxonomy
had not yet produced).

**2026-08-08, LISS-0377** (PR #473, `3b2d3ad`; standalone; Cursor
Claude-process handoff): first candidate from a sixth architectural
audit round. Terminal `measure make()` where `make` is a zero-arg user
function returning `DensityState<Qubit>` silently succeeded with an
empty marginal and skipped `POVM_DOMAIN_MISMATCH` for a
domain-mismatched POVM — both because `measurement.py` and the
evaluator's mixed-measure path only recognized bare `Var` targets.
Fixed by resolving FunDecl return-type domains for zero-arg Calls and
evaluating `return DensityState(...)` via `density_from_call` into
`_measure_mixed`. `pytest tests/ -q` reports **1338 passed, 0 failed**;
`spec_verification` remains **161/161 (100%, Gate: PASS)**.

**2026-08-08, LISS-0378** (PR #475, `b9f03d5`; standalone; sixth audit candidate 2):
`mixed_state._number` / runtime twin accepted only `LitInt`/`LitFloat`,
so `Ensemble([(1.0 * 1.0, |0>)])` and named `Float w` weights raised
spurious `MALFORMED_DENSITY_STATE`. Fixed by folding literal `BinOp`
and resolving `Var` against classical Float/Int binds threaded into
`density_from_call`. `pytest tests/ -q` → **1341 passed**; SV **161/161**.

**2026-08-08, LISS-0379** (PR #476, `56357b5`; standalone; sixth audit candidate 3):
`apply(ch, State)` MIXED_STATE_TYPE_ERROR only fired for bare `Var`
sources; a Call returning `State` compiled without that diagnostic.
Fixed via `_apply_arg_is_state` FunDecl return-type lookup.
`pytest tests/ -q` → **1343 passed**; SV **161/161**.

**2026-08-08, LISS-0380** (PR #477, `deab864`; standalone; sixth audit candidate 4 — final):
static Ensemble validation allowed `Var` ket states, but runtime
`_matrix_from_ensemble` required `KetLit` only, so
`Ensemble([(1.0, psi)])` with `psi = |0>` compiled then failed. Fixed
by tracking pure ket labels on State binds and resolving Vars at
runtime. `pytest tests/ -q` → **1345 passed**; SV **161/161**.

**This closes the sixth architectural audit's full candidate list**
(LISS-0377/0378/0379/0380 — four real, live-verified bugs fixed;
category (b)/(a)/static-evasion/contract-gap respectively).

Historical note: the 2026-08-01 operations review recorded ~50 root failures and
no CI tests ([WP-0069](../work-plans/WP-0069-operations-review-intake.md)); that
floor was closed by WP-0079–0080 and WP-0086.

## Status rule

`Open` means the design question is known but not accepted for implementation.
`Deferred` means the current Kernel deliberately stops before that boundary.
`Done` on a related Issue does not close a later follow-on listed here; for
example, first-order Trotter is done while higher-order Suzuki remains
deferred.
