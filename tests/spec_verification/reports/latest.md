# Staqex Spec Compliance Report

- Generated: `2026-08-23T15:37:35.877465+00:00`
- Spec Compliance Rate: **100.0%**
- Gate: **PASS** (161/161 passed)

| Suite | Case | Result | Assertions |
|-------|------|--------|------------|
| SV-01 | sv01-int-lift | PASS | assertTypeIsState, assertNormEquals, assertSuperposition |
| SV-01 | sv01-float-lift | PASS | assertTypeIsState, assertNormEquals, assertSuperposition |
| SV-01 | sv01-add-state | PASS | assertTypeIsState, assertNormEquals, assertSuperposition |
| SV-01 | sv01-Dirac | PASS | assertTypeIsState, assertNormEquals |
| SV-01 | sv01-compiler-lit-lift | PASS | assertTypeIsState (compiler) |
| SV-02 | sv02-when-Coin | PASS | assertTypeIsState, assertNormEquals, assertSuperposition |
| SV-02 | sv02-when-nested | PASS | assertNormEquals, assertSuperposition |
| SV-03 | sv03-div-by-zero | PASS | assertTypeIsState, assertNormEquals, assertSuperposition |
| SV-03 | sv03-div-ok | PASS | assertTypeIsState, assertNormEquals, assertSuperposition |
| SV-04 | sv04-early-collapse-bad | PASS | assertCompileError(EARLY_COLLAPSE_ERROR) |
| SV-04 | sv04-early-collapse-ok | PASS | assertCompileError(absent) |
| SV-05 | sv05-Vacuum-project | PASS | assertVacuum, assertNormEquals |
| SV-05 | sv05-compare-state-bool | PASS | assertTypeIsState<Bool>, assertNormEquals, assertSuperposition |
| SV-05 | sv05-Vacuum-ctor | PASS | assertVacuum |
| SV-05 | sv05-compiler-compare-bool | PASS | assertTypeIsState<Bool> (compiler) |
| SV-06 | sv06-package-tensor | PASS | namespace resolve, tensor_compose |
| SV-06 | sv06-forbidden-if | PASS | assertCompileError(FORBIDDEN_KEYWORD) |
| SV-06 | sv06-forbidden-null-throw | PASS | assertCompileError(FORBIDDEN_KEYWORD) |
| SV-06 | sv06-retired-observe-span | PASS | assertCompileError(RETIRED_KEYWORD) |
| SV-06 | sv06-nested-when | PASS | assertCompileError(NESTED_WHEN_ERROR) |
| SV-07 | sv07-correlated-self-sum | PASS | assertSuperposition, assertNormEquals |
| SV-07 | sv07-when-mixture | PASS | assertSuperposition, assertNormEquals |
| SV-07 | sv07-project-Vacuum | PASS | assertVacuum |
| SV-07 | sv07-map | PASS | assertSuperposition |
| SV-07 | sv07-interfer | PASS | assertSuperposition, assertNormEquals |
| SV-07 | sv07-Measure-stdout | PASS | Measure output |
| SV-08 | sv08-prelude | PASS | prelude |
| SV-08 | sv08-math-sin | PASS | assertSuperposition, Math.sin |
| SV-08 | sv08-Inspect | PASS | Inspect |
| SV-08 | sv08-Snapshot | PASS | Snapshot |
| SV-08 | sv08-cli-check | PASS | cli check |
| SV-08 | sv08-dag-ir | PASS | dag ir |
| SV-09 | sv09-basics-B01_never_leave_the_state-never_leave_the_state | PASS | staqex check, staqex run |
| SV-09 | sv09-basics-B02_when_not_if-when_not_if | PASS | staqex check, staqex run |
| SV-09 | sv09-basics-B03_failure_worldline-failure_worldline | PASS | staqex check, staqex run |
| SV-09 | sv09-basics-B04_evolve_not_loops-evolve_not_loops | PASS | staqex check, staqex run |
| SV-09 | sv09-basics-B05_phase_interference-phase_interference | PASS | staqex check, staqex run |
| SV-09 | sv09-basics-B06_type_first_dimensions-type_first_dimensions | PASS | staqex check, staqex run |
| SV-09 | sv09-basics-B07_structure_visibility-structure_visibility | PASS | staqex check, staqex run |
| SV-09 | sv09-basics-B08_operators_hamiltonians-operators_hamiltonians | PASS | staqex check, staqex run |
| SV-09 | sv09-basics-B09_multi_file_modules-main_multi_file_modules | PASS | staqex check, staqex run |
| SV-09 | sv09-basics-B10_static_qpu_lane-main_static_qpu_lane | PASS | staqex check, staqex run |
| SV-09 | sv09-basics-B11_qft_registers-main_qft_registers | PASS | staqex check, staqex run |
| SV-09 | sv09-basics-B12_open_systems-main_open_systems | PASS | staqex check, staqex run |
| SV-09 | sv09-basics-B13_host_job_api-main_host_job | PASS | staqex check, staqex run |
| SV-09 | sv09-basics-B14_resource_profile-main_resource_profile | PASS | staqex check, staqex run |
| SV-09 | sv09-basics-B15_multi_register-main_multi_register | PASS | staqex check, staqex run |
| SV-09 | sv09-applied-A01_quantum_attention_toy-main_quantum_attention_toy | PASS | staqex check, staqex run |
| SV-09 | sv09-applied-A02_robot_graph_planner-main_robot_graph_planner | PASS | staqex check, staqex run |
| SV-09 | sv09-applied-A03_h2_vqe-main_h2_vqe | PASS | staqex check, staqex run |
| SV-09 | sv09-applied-A04_hp_protein_folding-main_hp_protein_folding | PASS | staqex check, staqex run |
| SV-09 | sv09-applied-A05_qaoa_portfolio-main_qaoa_portfolio | PASS | staqex check, staqex run |
| SV-09 | sv09-applied-A06_topological_edge_memory-main_topological_edge_memory | PASS | staqex check, staqex run |
| SV-09 | sv09-applied-A07_open_system_sensor-main_open_system_sensor | PASS | staqex check, staqex run |
| SV-09 | sv09-applied-A08_entangled_compute_ancilla-main_entangled_compute_ancilla | PASS | staqex check, staqex run |
| SV-09 | sv09-applied-A09_qkd_corridor-main_qkd_corridor | PASS | staqex check, staqex run |
| SV-09 | sv09-applied-A10_mission_observatory-main_mission_observatory | PASS | staqex check, staqex run |
| SV-09 | sv09-applied-A11_noether_forge-main_static | PASS | staqex check, staqex run |
| SV-09 | sv09-docs | PASS | docs |
| SV-10 | sv10-openqasm-bell | PASS | emit_openqasm3 |
| SV-10 | sv10-cli-emit-qasm | PASS | cli |
| SV-10 | sv10-target-cpu | PASS | --target cpu |
| SV-10 | sv10-target-qpu-emit | PASS | --target qpu |
| SV-10 | sv10-docs | PASS | docs |
| SV-11 | sv11-qasm3-syntax | PASS | QASM3Emitter |
| SV-11 | sv11-gate-map | PASS | lower |
| SV-11 | sv11-swap-route | PASS | router |
| SV-11 | sv11-cli-openqasm3 | PASS | cli |
| SV-13 | sv13-Evolve-parse | PASS | parser |
| SV-13 | sv13-Evolve-correlated | PASS | assertSuperposition, joint |
| SV-13 | sv13-Evolve-times2 | PASS | Evolve |
| SV-13 | sv13-examples-Evolve | PASS | examples |
| SV-14 | sv14-destructive-Vacuum | PASS | assertVacuum |
| SV-14 | sv14-constructive-Dirac | PASS | assertSuperposition, assertNormEquals |
| SV-14 | sv14-cis-prelude | PASS | cis, Complex.cis |
| SV-14 | sv14-double-slit-cancel | PASS | assertSuperposition |
| SV-14 | sv14-grover-amplify | PASS | assertSuperposition |
| SV-15 | sv15-type-first-parse | PASS | Type-First, unit literal |
| SV-15 | sv15-dim-ok-Evolve | PASS | dimensional analysis |
| SV-15 | sv15-dim-reject-add | PASS | assertCompileError(DIMENSION_MISMATCH_ERROR) |
| SV-15 | sv15-phase-space-example | PASS | example |
| SV-16 | sv16-main-ok | PASS | main, Type-First |
| SV-16 | sv16-toplevel-reject | PASS | assertCompileError(TOPLEVEL_EXECUTION_ERROR) |
| SV-16 | sv16-package-import | PASS | unit.package, unit.main |
| SV-17 | sv17-ket-literals | PASS | KetLit |
| SV-17 | sv17-Evolve-under-x | PASS | hamiltonian |
| SV-17 | sv17-expect-z | PASS | expect |
| SV-17 | sv17-cnot-zz | PASS | cnot, ZZ |
| SV-17 | sv17-dim-pretty | PASS | DIMENSION_MISMATCH_ERROR |
| SV-18 | sv18-h-Evolve-length | PASS | DIMENSION_MISMATCH_ERROR |
| SV-18 | sv18-interfer-independent | PASS | INTERFER_INDEPENDENT_STATE_ERROR |
| SV-18 | sv18-expect-Mix | PASS | EXPECT_CLASSICAL_ONLY_ERROR |
| SV-18 | sv18-Evolve-tuple-swap | PASS | DIMENSION_MISMATCH_ERROR |
| SV-18 | sv18-length-eq-float | PASS | DIMENSION_MISMATCH_ERROR |
| SV-18 | sv18-when-in-ctrl | PASS | NESTED_WHEN_ERROR |
| SV-18 | sv18-Coin-in-Evolve | PASS | COIN_IN_EVOLVE_ERROR |
| SV-18 | sv18-interfer-shared-ok | PASS | ok |
| SV-19 | sv19-fock-ho-unitary | PASS | Operator, expm |
| SV-19 | sv19-ising-unitary | PASS | Operator, Z[index], Float coeff |
| SV-19 | sv19-expm-unitary-matrix | PASS | matrix.expm_ih |
| SV-19 | sv19-tensor-trace-out | PASS | TensorExpr, trace_out |
| SV-19 | sv19-energy-eigenstate | PASS | expect, Evolve under H |
| SV-19 | sv19-example-files | PASS | examples |
| SV-20 | sv20-hadamard | PASS | hadamard |
| SV-20 | sv20-apply-x | PASS | apply |
| SV-20 | sv20-dtqw-one-step | PASS | apply, shift, *|* |
| SV-20 | sv20-dtqw-two-step | PASS | DTQW |
| SV-20 | sv20-apply-hadamard-name | PASS | Hadamard |
| SV-20 | sv20-example-files | PASS | examples |
| SV-21 | sv21-capply-x-bell | PASS | capply, X |
| SV-21 | sv21-cnot-equiv-capply-x | PASS | cnot, capply |
| SV-21 | sv21-capply-z-phase | PASS | CZ |
| SV-21 | sv21-capply-ctrl0-id | PASS | controlled-I |
| SV-21 | sv21-example-file | PASS | examples |
| SV-22 | sv22-typed-product-bind | PASS | TypeRef Tuple, *|* |
| SV-22 | sv22-product-single-name | PASS | PRODUCT_BIND_ERROR |
| SV-22 | sv22-product-arity | PASS | PRODUCT_ARITY_ERROR |
| SV-22 | sv22-product-payload-mismatch | PASS | PRODUCT_TYPE_MISMATCH |
| SV-22 | sv22-trace-out-typed | PASS | trace_out |
| SV-22 | sv22-dtqw-typed-example | PASS | examples |
| SV-23 | sv23-project-predicate | PASS | PREDICATE_PROJECTOR_ERROR |
| SV-23 | sv23-map-constant | PASS | NON_UNITARY_TRANSFORM_ERROR |
| SV-23 | sv23-when-collapse | PASS | NON_UNITARY_TRANSFORM_ERROR |
| SV-23 | sv23-apply-non-unitary | PASS | NON_UNITARY_TRANSFORM_ERROR |
| SV-23 | sv23-apply-hadamard-ok | PASS | ok |
| SV-23 | sv23-hilbert-project-ok | PASS | ok |
| SV-23 | sv23-Coin-project-banned | PASS | PREDICATE_PROJECTOR_ERROR |
| SV-23 | sv23-gauge-u1-ok | PASS | examples |
| SV-24 | sv24-ccx-flip | PASS | CCX |
| SV-24 | sv24-toffoli-idle | PASS | toffoli |
| SV-24 | sv24-single-ctrl-compat | PASS | compat |
| SV-24 | sv24-example | PASS | examples |
| SV-25 | sv25-ocx-on-zero | PASS | ocapply |
| SV-25 | sv25-ocx-idle-on-one | PASS | open |
| SV-25 | sv25-dual-open | PASS | multi-open |
| SV-25 | sv25-example | PASS | examples |
| SV-26 | sv26-mixed-fire | PASS | ! |
| SV-26 | sv26-mixed-idle | PASS | polarity |
| SV-26 | sv26-double-bang-eq-ocapply | PASS | ocapply |
| SV-26 | sv26-example | PASS | examples |
| SV-27 | sv27-hermitian-e0 | PASS | Q, P |
| SV-27 | sv27-Evolve-ground | PASS | Evolve |
| SV-27 | sv27-example | PASS | examples |
| SV-28 | sv28-sparse-eq-dense-h | PASS | sparse |
| SV-28 | sv28-taylor-eq-dense-u | PASS | expm |
| SV-28 | sv28-ising4-norm | PASS | n=4 |
| SV-28 | sv28-example | PASS | examples |
| SV-29 | sv29-grid-hermitian | PASS | X, P |
| SV-29 | sv29-Evolve-norm-mean | PASS | wavepacket |
| SV-29 | sv29-example | PASS | examples |
| SV-30 | sv30-apply-fock | PASS | NON_UNITARY_TRANSFORM_ERROR |
| SV-30 | sv30-apply-grid | PASS | NON_UNITARY_TRANSFORM_ERROR |
| SV-30 | sv30-map-bit-collapse | PASS | NON_UNITARY_TRANSFORM_ERROR |
| SV-30 | sv30-map-flip-ok | PASS | ok |
| SV-30 | sv30-capply-non-unitary | PASS | NON_UNITARY_TRANSFORM_ERROR |
| SV-30 | sv30-Evolve-non-hermitian | PASS | NON_UNITARY_TRANSFORM_ERROR |
| SV-30 | sv30-Evolve-grid-ok | PASS | ok |
| SV-31 | sv31-link-symbols | PASS | compile_path, merge |
| SV-31 | sv31-linked-run | PASS | run_path, step_quantum_walk |
| SV-31 | sv31-missing-import | PASS | MODULE_NOT_FOUND_ERROR |
| SV-31 | sv31-class-fields | PASS | class, Type-First |

