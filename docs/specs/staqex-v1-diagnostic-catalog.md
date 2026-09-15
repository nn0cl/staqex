# Staqex v1 diagnostic catalog

| Field | Value |
|---|---|
| Status | **Promoted** — normative companions of [`staqex-language-specification.md`](staqex-language-specification.md) v1.0 (2026-07-28) |
| Replaces (when promoted) | `staqex-language-specification.md` Appendix B |
| Authority | Shipping `compiler/staqex/` + ADR 0013–0105 |
| Companion | [`staqex-v1-normative-outline-s12.md`](staqex-v1-normative-outline-s12.md) |
| Last updated | 2026-07-29 |

This catalog merges the v0.1 Appendix B snapshot with the shipping Python
Kernel. It splits **Kernel** (language compile + static-lane runtime),
**Backend emission**, **Host**, and **Harness** diagnostics so north-star
documentation does not conflate ports.

## 1. Versioning and stability

1. **Public codes** listed in Appendix K are immutable within a spec minor
   version; new codes may be added additively.
2. **Compile-hard set** — codes in `compiler/staqex/pipeline.py` `HARD_CODES`
   (exported; `run.py` / `cli.py` import the same object — LISS-0200).
   cause `CompileResult.ok == False`. This set is the v1 compile conformance
   oracle for static rejection.
3. **Runtime structured codes** — `KernelDiagnosticError.code` values that the
   reference Kernel may emit during execution (e.g. `EVOLVE_UNTIL_MAX_STEPS_ERROR`).
4. **Host appendix** — codes produced by Host adapters (`host.py`, resource
   enforcement, parametric binding, observation ports). They do not invalidate
   Kernel compilation of a statically valid program.
5. **Harness appendix** — SV meta-assertion failures (`NORM_MISMATCH`, …). Not
   emitted by end-user programs; conformance harness only.
6. **Backend emission** — QASM/QPU IR emission may report capability or lowering
   errors without retroactively invalidating an already-valid Static Kernel
   compile unless the diagnostic is also in Appendix K.

Promotion replaces v0.1 Appendix B and aligns
`docs/testing/staqex-spec-verification-protocol.md` §4 with this file.

---

## Appendix K — Kernel (compile-hard)

Source of truth: `compiler/staqex/pipeline.py` `HARD_CODES` (2026-08-01, LISS-0200).

### K.1 Lexical and parse

| Code | Meaning | ADR / spec |
|---|---|---|
| `LEX_ERROR` | Illegal character / unterminated token | 0035 |
| `PARSE_ERROR` | Grammar violation | 0035 |
| `FORBIDDEN_KEYWORD` | Forbidden surface (`if`, `while`, `throw`, …) | 0035, 0025 |
| `RETIRED_KEYWORD` | Retired spelling with fix-it | 0035 |
| `RETIRED_OPERATOR_INDEX_SYNTAX` | Parenthesized operator-index spelling retired | LISS-0054 |
| `NUMERIC_LITERAL_SEPARATOR_ERROR` | Invalid `_` placement in numeric literal | 0101 |

### K.2 Program shape, scope, and returns

| Code | Meaning | ADR / spec |
|---|---|---|
| `TOPLEVEL_EXECUTION_ERROR` | Executable stmt outside `main` | 0027 |
| `MAIN_RETURN_TYPE_ERROR` | `main` not `-> Unit` | 0064 |
| `MAIN_RETURN_ERROR` | `main` uses `return` | 0064 |
| `MAIN_RESULT_ERROR` | `main` result misuse | 0064 |
| `MISSING_RETURN_TYPE` | Function missing `-> Type` | 0064, 0068 |
| `MISSING_RETURN_STATEMENT` | Non-`main` fn missing terminal `return` | 0068 |
| `MISSING_RETURN_VALUE` | `return` without value | 0068 |
| `RETURN_TYPE_MISMATCH` | Declared vs actual return type | 0068 |
| `RETURN_NOT_TERMINAL` | Non-terminal `return` | 0068 |
| `INIT_RETURN_ERROR` | `fn init` return misuse | 0056 |
| `LEXICAL_SCOPE_ERROR` | Illegal cross-scope reference | 0068 |
| `MEASURE_IN_FUNCTION_ERROR` | `measure` inside ordinary `fn` | 0027 |
| `SNAPSHOT_IN_FUNCTION_ERROR` | `snapshot` inside ordinary `fn` | 0030 |
| `FUNCTION_ARITY_ERROR` | Call arity mismatch | 0068 |

### K.3 State, dimensions, and products

| Code | Meaning | ADR / spec |
|---|---|---|
| `EARLY_COLLAPSE_ERROR` | Non-terminal `measure` | 0027 |
| `NESTED_WHEN_ERROR` | Nested `when` on State | 0039 |
| `TYPE_NOT_STATE` | Non-State where State required | 0018 |
| `TYPE_MISMATCH` | General type mismatch | 0037 |
| `DIMENSION_MISMATCH_ERROR` | Dimensional algebra failure | 0037 |
| `LOCAL_DIMENSION_TYPE_ERROR` | Invalid qutrit/qudit type-level shape or label | LISS-0074 |
| `UNSUPPORTED_LOCAL_DIMENSION` | Qudit runtime deferred except LISS-0112 D=3 measure + Identity; QASM / D≠3 / non-Identity remain reject (no silent qubit embed) | LISS-0074, LISS-0112 |
| `PRODUCT_BIND_ERROR` | Product bind on single name | 0044 |
| `PRODUCT_ARITY_ERROR` | Product arity ≠ names | 0044 |
| `PRODUCT_TYPE_MISMATCH` | Incompatible product carriers | 0044 |
| `EXPECT_CLASSICAL_ONLY_ERROR` | `expect` scalar mixed into State arith | 0038 |
| `COIN_IN_EVOLVE_ERROR` | `coin()` inside `evolve` | 0013 |
| `INTERFER_INDEPENDENT_STATE_ERROR` | `interfer` without shared lineage | 0021 |
| `CANNOT_MEASURE_CLASSICAL_VALUE_ERROR` | `measure` on non-State | 0018 |
| `PREDICATE_PROJECTOR_ERROR` | Invalid projector predicate | 0045 |

### K.4 Modules, visibility, and OOP

| Code | Meaning | ADR / spec |
|---|---|---|
| `MODULE_NOT_FOUND_ERROR` | Unresolved import | 0054 |
| `MODULE_CYCLE_ERROR` | Import cycle | 0054 |
| `PACKAGE_NOT_EXPORTED_ERROR` | Non-exported package symbol | 0054 |
| `CONFIG_HARVEST_COLLISION_ERROR` | Module config harvest collision | 0061 |
| `ACCESS_CONTROL_VIOLATION_ERROR` | Visibility rule violation | 0058 |
| `PRIVATE_ACCESS_VIOLATION_ERROR` | `_` / private member access | 0058 |
| `MODULE_PRIVATE_ACCESS_ERROR` | Cross-module non-`pub` access | 0058 |
| `IMMUTABLE_ASSIGNMENT_ERROR` | Write to `val` / immutable field | 0056 |
| `ENUM_TYPE_MISMATCH` | Enum assignment mismatch | 0055 |
| `IMPL_COHERENCE_ERROR` | `impl` coherence failure | 0082 |
| `IMPL_VISIBILITY_ERROR` | `pub` in `impl` | 0082 |
| `SYSTEM_EXPRESSION_ERROR` | Invalid `system` expression | 0082 |

### K.5 Operators, unitarity, and evolution

| Code | Meaning | ADR / spec |
|---|---|---|
| `NON_UNITARY_TRANSFORM_ERROR` | Non-unitary map / apply / evolve | 0045 |
| `OPERATOR_ALGEBRA_TYPE_ERROR` | Operator algebra type error | 0087 |
| `OPERATOR_DOMAIN_ERROR` | Operator domain mismatch | 0087 |
| `IDENTITY_ACTING_SPACE_UNDETERMINED` | Identity acting space unknown | 0102 |
| `ACTING_SPACE_MISMATCH` | Acting-space mismatch | 0102 |
| `EVOLVE_UNTIL_BOUND_ERROR` | Invalid `evolve until` bound | 0079 |
| `EVOLVE_UNTIL_EFFECT_ERROR` | Effect violation in `until` | 0079, 0081 |
| `SUZUKI_ORDER_ERROR` | Invalid Suzuki order | 0084 |
| `SUZUKI_POLICY_ERROR` | Missing/invalid Trotter policy | 0094 |

### K.6 Lanes — Static Hilbert, Parametric, Dynamic

| Code | Meaning | ADR / spec |
|---|---|---|
| `HOST_TYPE_IN_KERNEL_ERROR` | `Host<T>` in Static Kernel body | 0069 |
| `FOR_EACH_DYNAMIC_BOUND_ERROR` | Dynamic bound in static `forEach` | 0069 |
| `FOR_EACH_MEASURE_ERROR` | `measure` in static `forEach` | 0069 |
| `QPU_CLASSICAL_CONTROL_ERROR` | Classical control in QPU static lane | 0069 |
| `STATIC_REGISTER_TYPE_ERROR` | Invalid `QubitRegister<N>` use | 0069 |
| `STATIC_HILBERT_SURFACE_ERROR` | Illegal static Hilbert surface | 0069 |
| `STATIC_HILBERT_RESOURCE_ERROR` | Static resource limit | 0069 |
| `PARAMETER_TYPE_ERROR` | Invalid `Param<T>` use | 0070 |
| `PARAMETER_CONTROL_ERROR` | Param controls shape/flow | 0070 |
| `QFT_REGISTER_TYPE_ERROR` | QFT register typing | 0078 |
| `QFT_RESOURCE_ERROR` | QFT resource bound | 0078 |
| `DYNAMIC_CAPABILITY_REQUIRED_ERROR` | Missing dynamic capability | 0071 |
| `DYNAMIC_UNSUPPORTED_FEATURE_ERROR` | Unsupported dynamic feature | 0071 |
| `MID_CIRCUIT_MEASUREMENT_REQUIRES_DYNAMIC_LANE` | Mid-circuit measure outside dynamic lane | 0071 |

### K.7 Pipelines, effects, and carriers

| Code | Meaning | ADR / spec |
|---|---|---|
| `PIPE_EFFECT_ERROR` | Effect violation in pipeline | 0080, 0081 |
| `PIPE_CALLABLE_ERROR` | Non-callable pipeline RHS | 0080 |
| `PIPE_TYPE_ERROR` | Pipeline type error | 0080 |
| `EFFECT_DECLARATION_ERROR` | Invalid effect declaration | 0081 |
| `EFFECT_VIOLATION_ERROR` | Transitive effect violation | 0081 |
| `EFFECT_MEASURE_RETURN_ERROR` | Measure effect in return | 0081 |
| `SEMANTIC_CARRIER_MISMATCH_ERROR` | Semantic carrier mismatch | 0038 |
| `SEMANTIC_CARRIER_OPERATION_ERROR` | Illegal carrier operation | 0038 |
| `PHASE_TYPE_VISIBILITY_ERROR` | Phase-local type / Execution·Report-symbol visibility in Theory/Experiment/Workflow bodies, transitive calls, and import-merged scopes | 0034, [0076](../architecture/documentation-compression-map.md), [0118](../architecture/documentation-compression-map.md), [scientific-scopes](staqex-scientific-scopes.md) |

### K.8 Binders, registers, and second quantization

| Code | Meaning | ADR / spec |
|---|---|---|
| `BINDER_DOMAIN_ERROR` | Binder domain error | 0096 |
| `BINDER_RESOURCE_ERROR` | Binder resource bound | 0096 |
| `BINDER_INDEX_OUT_OF_BOUNDS` | Binder index OOB | 0096 |
| `BINDER_LOWERING_UNSUPPORTED` | Unsupported binder lowering | 0088 |
| `BINDER_GUARD_UNSUPPORTED` | Unsupported binder guard | 0055 |
| `MATHEMATICAL_BINDER_EFFECT_ERROR` | Effect in mathematical binder | 0096 |
| `MULTI_REGISTER_INDEX_AMBIGUOUS` | Ambiguous multi-register index | 0105 |
| `MULTI_REGISTER_SHAPE_ERROR` | RegisterSet shape error | 0105 |
| `UNKNOWN_REGISTER_ID` | Unknown register id | 0105 |
| `SECOND_QUANTIZATION_TYPE_ERROR` | Second-quantized type error | 0093 |
| `FERMION_MAPPING_REQUIRED_ERROR` | Mapping required | 0093 |
| `SECOND_QUANTIZATION_MAPPING_UNSUPPORTED` | Unsupported mapping | 0093 |

### K.9 Scientific scopes, workflow, discretization

| Code | Meaning | ADR / spec |
|---|---|---|
| `PHASE_SCOPE_DEPENDENCY_ERROR` | Missing scope dependency | 0034 |
| `PHASE_SCOPE_CYCLE_ERROR` | Scope dependency cycle | 0034 |
| `PHASE_SCOPE_DIRECTION_ERROR` | Illegal phase direction | 0034, 0106 D1 |
| `PHASE_SCOPE_REFERENCE_ERROR` | Unknown scope reference | 0034 |
| `WORKFLOW_SURFACE_ERROR` | Workflow surface error | 0073 |
| `DISCRETIZATION_REQUIRED_ERROR` | Continuous op without contract | 0074 |
| `DISCRETIZATION_CONTRACT_ERROR` | Invalid discretization contract | 0074 |
| `DISCRETIZATION_BRIDGE_ERROR` | Invalid bridge | 0074 |
| `DISCRETIZATION_LOWERING_ERROR` | Lowering failure / non-MVP contract | 0111 |

### K.10 Mixed state, channels, and POVM

| Code | Meaning | ADR / spec |
|---|---|---|
| `MIXED_STATE_TYPE_ERROR` | Mixed-state type error | 0057 |
| `MALFORMED_DENSITY_STATE` | Malformed density constructor | 0057 |
| `INCOMPLETE_KRAUS_CHANNEL` | Incomplete Kraus channel | 0057 |
| `INVALID_LINDBLAD_JUMP_SET` | Invalid Lindblad jumps | 0057 |
| `LINDBLAD_JUMP_DIMENSION_ERROR` | Jump dimension mismatch | 0057 |
| `SYMBOLIC_JUMP_LOWERING_REQUIRED` | Symbolic jump needs lowering | 0039 |
| `POVM_DOMAIN_MISMATCH` | POVM domain mismatch | 0075 |
| `INVALID_POVM_EFFECT` | Invalid POVM effect | 0075 |
| `INCOMPLETE_POVM` | Incomplete POVM | 0075 |

### K.11 Kernel runtime (structured)

Emitted via `KernelDiagnosticError` or wrapped as structured runtime failure.
Not all are compile-hard; listed for differential-oracle completeness.

| Code | Meaning | When |
|---|---|---|
| `EVOLVE_UNTIL_MAX_STEPS_ERROR` | `until` predicate not met within `max` | Runtime evaluator |
| `RUNTIME_ERROR` | Unstructured Kernel failure wrapper | Host `submit` path |

Future v1 work may promote additional runtime codes to structured diagnostics
with stable codes (ADR 0106 D7).

### K.12 Kernel warnings (non-fatal)

| Code | Meaning |
|---|---|
| `EMPTY_BINDER_DOMAIN_WARNING` | Empty binder domain (warn) |

Warnings do not set `CompileResult.ok == False`.

### K.13 Physics IR inspection diagnostics (non-compile-hard)

These codes are emitted by the provider-neutral Physics IR verifier and
inspection projection. They are not automatically added to the Kernel
compile-hard set and do not change runtime/backend acceptance.

| Code | Meaning | Boundary |
|---|---|---|
| `PHYSICS_IR_PROVENANCE_ERROR` | Physics IR root or inspection record lacks source ancestry | LISS-0081 |
| `PHYSICS_IR_DOMAIN_ERROR` | Binder, channel, or symmetry lacks a required domain reference | LISS-0081 |
| `PHYSICS_IR_STATISTICS_ERROR` | Operator fixture lacks an explicit statistics reference | LISS-0081 |
| `PHYSICS_IR_FAMILY_ERROR` | Inspection record has no recognized formula family | LISS-0081 |

### K.14 Physics equation DTO diagnostics (non-compile-hard)

Module-local verifier in `compiler/staqex/physics_equation.py` (LISS-0116).
Not Kernel compile-hard.

| Code | Meaning | Boundary |
|---|---|---|
| `PHYSICS_EQUATION_PROVENANCE_ERROR` | Unit, Coefficient, or EquationNode lacks source ancestry | LISS-0116 |
| `PHYSICS_EQUATION_UNIT_ERROR` | Coefficient lacks a unit reference | LISS-0116 |

---

## Appendix B — Backend emission (Kernel port boundary)

These codes originate from QPU IR / OpenQASM emission. They mark **backend
capability or lowering** limits; a program may compile as a valid Static Kernel
program yet fail emission. Narrative catalog:
[`staqex-v1-qpu-capability-honesty.md`](staqex-v1-qpu-capability-honesty.md).

| Code | Meaning | ADR / Issue |
|---|---|---|
| `E_QPU_UNSUPPORTED_CAPABILITY` | QPU lane unsupported capability | 0069, 0071 |
| `QPU_IR_UNAVAILABLE` | QPU IR cannot be built | 0077 |
| `QASM_EMISSION_ERROR` | Generic QASM emission failure | 0059 |
| `QASM_FUNCTION_CALL_UNSUPPORTED` | User `fn` call in QASM path | LISS-0049 |
| `UNSUPPORTED_LOCAL_DIMENSION` | Qudit carrier in OpenQASM emission (reuse Kernel code; LISS-0112 does not lift QASM) | LISS-0074, LISS-0112 |
| `QASM_TROTTER_STEPS_REQUIRED` | Plain evolve needs Suzuki policy | 0094 |
| `QASM_TROTTER_BAD_TIME` | Invalid evolution time for Trotter | 0094 |
| `QASM_TROTTER_UNSUPPORTED_H` | Unsupported Hamiltonian for Trotter | 0094 |
| `QASM_TROTTER_COMPLEX_COEFF` | Unsupported complex coefficient | 0094 |
| `TARGET_WARN` | Target profile warning | 0036 |

---

## Appendix H — Host (orchestration and adapters)

Host diagnostics are **outside** Kernel compile-hard conformance. They govern
Job submission, resource policy, scientific input, observations, and QPU result
integration.

### H.1 Parametric binding

| Code | Meaning | ADR / Issue |
|---|---|---|
| `PARAM_BINDING_MISSING` | Required binding absent | 0070, LISS-0027 |
| `PARAM_BINDING_UNKNOWN` | Unknown binding key | 0070 |
| `PARAM_BINDING_VALUE_ERROR` | Invalid binding value | 0070 |

### H.2 Scientific input

| Code | Meaning | ADR |
|---|---|---|
| `SCIENTIFIC_INPUT_PARAMETER_ERROR` | Parameter declaration error | 0090 |
| `SCIENTIFIC_INPUT_UNKNOWN_PARAMETER` | Unknown parameter | 0090 |
| `SCIENTIFIC_INPUT_DUPLICATE_PARAMETER` | Duplicate parameter | 0090 |
| `SCIENTIFIC_INPUT_VALUE_ERROR` | Invalid value | 0090 |
| `SCIENTIFIC_INPUT_UNIT_ERROR` | Unit error | 0090 |
| `SCIENTIFIC_INPUT_DIMENSION_ERROR` | Dimension error | 0090 |
| `SCIENTIFIC_INPUT_PROVENANCE_ERROR` | Provenance error | 0090 |
| `SCIENTIFIC_INPUT_EMPTY_SWEEP` | Empty sweep | 0090 |

### H.3 Resource profile and simulator budget

| Code | Meaning | ADR |
|---|---|---|
| `RESOURCE_MANIFEST_NOT_FOUND` | Missing manifest | 0100 |
| `RESOURCE_MANIFEST_PARSE_ERROR` | Manifest parse error | 0100 |
| `RESOURCE_MANIFEST_SCHEMA_ERROR` | Manifest schema error | 0100 |
| `RESOURCE_SETTING_INVALID` | Invalid resource setting | 0100 |
| `SIMULATOR_RESOURCE_ERROR` | Simulator budget abort | 0100 |
| `SIMULATOR_RESOURCE_WARNING` | Simulator budget warn | 0100 |

### H.4 Observation checkpoints

| Code | Meaning | ADR |
|---|---|---|
| `OBSERVATION_REQUEST_ERROR` | Invalid observation request | 0089 |
| `OBSERVATION_UNSUPPORTED` | Observation capability is unsupported in the selected lane | 0189, 0226 |
| `OBSERVATION_TARGET_LANE_ERROR` | Wrong execution lane | 0089 |
| `OBSERVATION_EXECUTION_CONTEXT_ERROR` | Invalid execution context | 0089 |
| `OBSERVATION_PROGRAM_ID_ERROR` | Invalid program id | 0089 |
| `OBSERVATION_JOB_ID_ERROR` | Invalid job id | 0089 |
| `OBSERVATION_CHECKPOINT_ID_ERROR` | Invalid checkpoint id | 0089 |
| `OBSERVATION_PROVENANCE_ERROR` | Provenance error | 0089 |
| `OBSERVATION_RESOURCE_ERROR` | Resource error | 0089 |
| `OBSERVATION_SNAPSHOT_CAPABILITY_ERROR` | Snapshot capability error | 0089 |
| `OBSERVATION_SNAPSHOT_CAPABILITY_REQUIRED` | Snapshot capability required | 0089 |
| `OBSERVATION_PROJECTION_UNSUPPORTED` | Unsupported projection | 0089 |
| `OBSERVATION_QPU_SNAPSHOT_UNSUPPORTED` | QPU snapshot unsupported | 0089 |

### H.5 QPU result integration

| Code | Meaning | ADR |
|---|---|---|
| `QPU_RESULT_UNAVAILABLE` | Incomplete QPU result | 0104 |
| `QPU_OBSERVATION_INCOMPLETE` | Incomplete observation payload | 0104 |

---

## Appendix V — Harness and verification only

Used by `tests/spec_verification/` meta-assertions. Not part of the language
runtime contract for application programs.

| Code | Meaning | Protocol |
|---|---|---|
| `NORM_MISMATCH` | Born norm mismatch | SV §1.1 |
| `SUPERPOSITION_MISMATCH` | Support / mass mismatch | SV §1.2 |
| `NOT_VACUUM` | Expected Vacuum | SV §1.5 |
| `UNEXPECTED_EXCEPTION` | Object language threw | SV harness |
| `PACKAGE_RESOLVE_ERROR` | Legacy harness import resolve | v0.1 Appendix B (audit for removal) |

---

## Gap register (v0.1 Appendix B → this catalog)

| Gap | Resolution |
|---|---|
| Appendix B stops at ~30 codes | Appendix K lists full compile-hard set (~100+) |
| Parametric/Dynamic/Until codes absent | Added in K.6, K.5 |
| Discretization / scope / binder codes absent | Added in K.8–K.9 |
| Host codes mixed or missing | Split to Appendix H |
| QASM codes missing | Appendix B (emission) |
| SV harness codes undocumented | Appendix V |
| `PACKAGE_RESOLVE_ERROR` legacy | Mark audit/remove in LISS-0071 |

---

## Promotion checklist

- [x] Adjudicator review of appendix split and compile-hard authority (E0, 2026-07-27).
- [x] Sync `staqex-language-specification.md` Appendix B on promotion.
- [x] Sync `staqex-spec-verification-protocol.md` §4 on promotion.
- [ ] Add CI drift check: `_HARD_CODES` ⊆ catalog Appendix K (future LISS-0071).

## E0 status

**LISS-0068 E0 + promotion complete** (2026-07-28). Next gate: LISS-0069.
