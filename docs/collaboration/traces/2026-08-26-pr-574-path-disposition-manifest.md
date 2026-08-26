# PR #574 exact path disposition manifest

This manifest covers every path in `git diff --name-only 9ca049f6 e87937ea`. A `SELECTED` row is design input only; it authorizes no implementation or merge. Every `REJECT` row is excluded from WP-0117 migration until a separate canonical owner and approval exist.

| Path | Disposition / canonical owner |
|---|---|
| `.github/workflows/ci.yml` | REJECT | current CI must be compared separately; no blind workflow migration |
| `AGENTS.md` | REJECT | not selected; no migration authority |
| `CLAUDE.md` | REJECT | not selected; no migration authority |
| `QUICKSTART.md` | REJECT | not selected; no migration authority |
| `compiler/staqex/parser.py` | REJECT | code/test migration requires a separate Issue and phase approval |
| `compiler/staqex/runtime/evaluator.py` | REJECT | code/test migration requires a separate Issue and phase approval |
| `compiler/staqex/scientific_vocabulary.py` | REJECT | code/test migration requires a separate Issue and phase approval |
| `docs/README.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/2026-08-03-language-design-rereview.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/README.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adjudicator-language-vision.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0001-design-first-ai-request-routing.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0002-input-output-reasoning-contracts.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0003-ai-human-collaboration-governance.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0004-human-readable-source-code-quality.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0005-local-issue-planning.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0006-prompt-instruction-change-control.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0007-trunk-oriented-branching.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0008-template-update-propagation.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0009-bug-planning-and-ai-usage-records.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0010-ai-failure-recovery-and-runner-cli-contract.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0011-external-resource-adoption-contract.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0012-rename-referee-to-adjudicator.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0013-staqex-language-axioms.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0014-mvp-discrete-pmf-representation.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0015-local-first-runtime-and-ports.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0016-pmf-mvp-amplitude-lift.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0017-surface-vocabulary.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0018-state-t-lift-and-classical-boundary.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0019-generics-traits-system.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0020-map-given-fold-conditioning.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0021-project-interfer-system-naming.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0022-quantum-native-optimizations.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0023-naming-conventions.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0024-kotlin-dx-packages-when-class.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0025-failure-as-superposition-no-exceptions.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0026-p1-locks-fun-result-project-vacuum-packages.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0027-entry-point-main-measure.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0028-no-threads-concurrency-is-superposition.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0029-host-io-boundary-measure-sink.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0030-inspect-non-destructive-debug.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0031-stdlib-packages-math-state.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0032-runtime-dag-data-parallel.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0033-immutable-class-reentrancy.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0034-vacuum-state-compare-prelude.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0035-token-specification-lexer-parser.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0036-backend-targets-cli.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0037-type-first-dimensions-structured-units.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0038-ket-hamiltonian-expect.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0039-nested-when-banned.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0040-physical-axiom-typechecking.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0041-arbitrary-hamiltonian-tensor.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0042-dtqw-apply-shift.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0043-capply-controlled-unitary.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0044-typed-product-state.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0045-static-unitarity-checks.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0046-multi-controlled-capply.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0047-open-controlled-ocapply.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0048-mixed-control-polarity.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0049-fock-quadrature-qp.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0050-sparse-pauli-sum-ir.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0051-position-grid-ho.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0052-extended-static-unitarity.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0053-physicist-surface-purification.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0054-user-module-import.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0055-namespace-scope.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0056-class-methods-this.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0057-density-cptp-lindblad.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0058-access-control-modules.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0059-openqasm3-zero-dependency-codegen.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0060-joint-coordinate-preservation.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0061-classical-module-config-harvest.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0062-prelude-pi-constant.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0063-pauli-trotter-qasm.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0064-explicit-main-unit-result.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0065-job-based-host-execution.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0066-rust-aligned-fn-surface.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0067-pub-only-visibility-surface.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0068-explicit-return-and-lexical-scope.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0069-kernel-static-hilbert-space.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0070-parametric-circuit.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0071-dynamic-qpu-lane.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0072-hybrid-workflow-host-contract.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0073-declarative-workflow-surface.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0074-explicit-discretization-contract.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0075-povm-measurement-contract.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0076-numeric-representation-policy.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0077-provider-neutral-qpu-ir-boundary.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0078-kernel-qft-iqft-surface.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0079-evolve-until-kernel-semantics.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0080-pipeline-currying-surface.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0081-effect-marking-and-propagation.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0082-interface-impl-and-system-boundary.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0083-provider-neutral-qpu-submit-port.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0084-higher-order-suzuki-error-contract.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0085-qpu-ir-lowering-opcodes.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0086-qft-basic-gate-lowering.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0087-operator-algebra-dirac-notation.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0088-finite-binder-lowering.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0089-observation-checkpoints-and-execution-diagnostics.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0090-scientific-input-and-parameter-binding.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0091-jobresult-observation-integration.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0092-local-observation-plan-execution.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0093-jordan-wigner-numerical-mapping.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0094-explicit-trotter-step-policy.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0095-design-horizon-ideal-form-first.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0096-indexed-operator-and-binder-surface.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0097-numeric-representation-horizon.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0098-binder-constraint-and-quantum-body-boundary.md` | REJECT | historical ADR compression; current main/baseline is canonical |
| `docs/architecture/adr/0100-resource-budget-policy.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0101-numeric-literal-separators.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0102-acting-space-typing.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0103-host-qpu-submit-orchestration.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0104-qpu-observation-result-integration.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0105-multi-register-acting-space-and-qpu-mapping.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0106-staqex-v1-north-star-language-and-compiler.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0107-linear-uncompute-amplitude-tolerance.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0108-quantum-semantic-ir-value-region-contract.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0109-quantum-machine-scale-and-model-envelope.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0110-optimistic-quantum-capacity-horizon.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0111-current-hardware-first-delivery-horizon.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0112-claude-code-contract-independence.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0113-work-plan-level-approval-and-pr-granularity.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0114-classical-coefficient-elaboration-vs-linear.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0115-typed-state-surface-annotations.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0116-classical-quantity-state-arithmetic.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0117-binder-index-endpoints-and-rev.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0118-basis-binder-and-partial-float.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0119-host-coefficient-tensor-inject.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0120-controlled-exact-qft.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0121-si-base-dims-current-temperature.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0122-pipeline-unary-bare-stage.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0123-function-partial-holes.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0124-si-scale-conversion-explicit.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0125-exact-rational-design-boundary.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0126-continuous-pdf-design-boundary.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0127-live-qpu-credentials-boundary.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0128-trait-effect-expansion-boundary.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0129-si-scale-catalog-wave2.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0130-user-fn-state-forming-args.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0131-stepwise-partial-fill.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0132-ev-joule-si-conversion.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0133-pipeline-leftmost-hole-fill.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0134-celsius-kelvin-affine.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0135-fahrenheit-kelvin-affine.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0136-gram-kilogram-scale.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0137-pipeline-operator-fusion-mvp.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0138-trace-out-gc-fn-scope.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0139-interference-prune-mvp.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0140-deferred-pushforward-mvp.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0141-algebraic-operator-fusion-mvp.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0142-evolve-trace-out-gc.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0143-call-partial-pipe-fusion-mvp.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0144-rankine-kelvin-affine.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0145-imperial-pound-mass.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0146-imperial-ounce-mass.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0147-imperial-stone-mass.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0148-tonne-mass.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0149-multi-hole-partial-pipe.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0150-us-uk-ton-mass.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0151-troy-ounce-mass.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0152-tuple-multi-hole-fusion.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0153-bare-block-trace-out.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0154-mixed-unit-reject.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0155-mixed-unit-canonical-promote.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0156-atomic-mass-and-ton-alias.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0157-polynomial-operator-fusion.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0158-interprocedural-trace-out.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0159-cpu-data-parallel-workers.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0160-classical-rational-literals.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0161-credential-port.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0162-continuous-host-bridge-first.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0163-host-mc-finite-state-inject.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0164-host-mc-inject-consumption-seam.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0165-dirac-paper-spelling-sugar.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0166-kernel-external-resource-ports.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0167-linear-obligation-follows-carrier-type.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0168-type-driven-linear-call-move.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0169-ship-dirac-paper-spelling-sugar.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0170-ship-kernel-rng-port.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0171-ship-kernel-measure-sink-port.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0172-ship-kernel-source-port.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0173-measure-tracing-out-leftover-policy.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0174-type-first-field-units.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0175-failure-glossary.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0176-experiment-surface-profile.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0177-import-use-ergonomics.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0178-lane-annotation.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0179-classical-call-in-expr.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0180-local-type-inference.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0181-named-struct-construction.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0182-default-experiment-profile.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0183-module-relative-import.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0184-classical-multi-bind.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0185-kernel-continuous-value.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0186-display-unit-restore.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0188-decision-theme-canonical-surface.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/adr/0189-quantum-mental-model-and-observation-contract.md` | SELECTED design input | ADR 0189 / WP-0092 |
| `docs/architecture/agent-quickstart.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/current-decision-register.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/current-hardware-delivery-envelope.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/decision-theme-register.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/decision-themes/dec-0001-governance-and-collaboration.md` | REJECT | current main canonicalization already owns this surface |
| `docs/architecture/decision-themes/dec-0002-state-first-semantics-and-measurement.md` | SELECTED reference | DEC-0002 |
| `docs/architecture/decision-themes/dec-0003-language-surface-and-physicist-first-dx.md` | SELECTED reference | DEC-0003 |
| `docs/architecture/decision-themes/dec-0004-type-first-scientific-model.md` | REJECT | current main canonicalization already owns this surface |
| `docs/architecture/decision-themes/dec-0005-quantum-operations-and-runtime.md` | REJECT | current main canonicalization already owns this surface |
| `docs/architecture/decision-themes/dec-0006-host-qpu-and-external-ports.md` | SELECTED reference | DEC-0006 |
| `docs/architecture/decision-themes/dec-0007-documentation-and-decision-records.md` | REJECT | current main canonicalization already owns this surface |
| `docs/architecture/documentation-canonicalization-policy.md` | REJECT | current main canonicalization already owns this surface |
| `docs/architecture/documentation-compression-map.md` | REJECT | current main canonicalization already owns this surface |
| `docs/architecture/external-resource-adoption-contract.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/open-work-register.md` | SELECTED current authority | open-work register |
| `docs/architecture/physicist-minimal-dialect.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/physicist-source-friction-ledger.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/quantum-capacity-horizon-scenarios.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/quantum-machine-scale-and-model-envelope.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/quantum-semantic-ir-contract.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/staqex-compiler-optimizations.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/staqex-destructive-simplification-sketch.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/staqex-language-axioms.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/staqex-runtime-execution-model.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/staqex-type-system.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/architecture/surface-modernization-north-star.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/adoption-guide.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/agent-sync-quantum-native-opts.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/branch-commit-pr-discipline.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/process-gap-register.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/reviews/2026-07-26-wp-0024-plan-approval.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/reviews/2026-07-31-adr-0162-architecture-approval.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/reviews/2026-07-31-adr-0164-host-mc-inject-seam.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/reviews/2026-08-02-s01-expressiveness-scenario-review.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/reviews/2026-08-03-continuous-kernel-architecture.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/reviews/2026-08-03-liss-0313-finiteize-plan-request.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/reviews/2026-08-03-wp-0089-sugar-adr-drafts-request.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/traces/2026-07-25-claude-md-full-mirror.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/traces/2026-07-27-qpex-v1-north-star-design.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/traces/2026-07-29-liss-0114-slice-f-complete.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/traces/2026-07-30-claude-contract-independence-wp-granularity.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/traces/2026-07-30-p0-p1-current-hardware-rebaseline.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/traces/2026-07-30-quantum-capacity-horizon-intake.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/traces/2026-07-31-adr-0164-host-mc-inject-seam.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/traces/2026-08-01-wp-0069-operations-review-intake.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/traces/2026-08-03-liss-0312-continuous-kernel-architecture.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/traces/2026-08-03-liss-0313-finiteize-surface.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/traces/2026-08-03-liss-0314-display-unit-restore.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/traces/2026-08-03-wp-0090-trace-topic-consolidation.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/collaboration/traces/2026-08-03-wp-0091-decision-theme-design.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0013-pipeline-currying.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0014-trait-impl-system.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0015-effect-marking.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0016-host-qpu-submit.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0017-higher-order-suzuki.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0031-operator-algebra-and-dirac-notation.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0035-hybrid-scientific-workflow.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0036-continuous-operator-and-discretization-boundary.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0047-local-observation-plan-execution.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0055-binder-body-as-operator-expression.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0111-continuous-discretization-numerical-lowering-mvp.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0120-representative-program-language-review-gate.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0202-linear-discipline-regression-cluster.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0213-proposed-adrs-with-shipped-issues.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0215-settled-decisions-documented-as-open.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0217-dirac-paper-spelling-sugar.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0218-kernel-external-resource-ports.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0221-state-transforming-calls-move-their-input-root.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0234-dirac-paper-spelling-sugar-red.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0235-kernel-rng-port-red.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0236-kernel-measure-sink-port-red.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0237-kernel-source-port-red.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0238-multi-hole-partial-pipe-lhs-move.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0240-observe-sink-to-vs-unit-convert.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/LISS-0258-failure-glossary-adr.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/inbox/archive/2026-07-23-examples-driven-brush-up.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/issues/inbox/archive/2026-07-23-openqasm3-braket-codegen.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/research/2026-07-24-scientific-input-data-and-sdk-study.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-continuous-discretization.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-density-cptp-lindblad.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-dynamic-qpu-lane.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-finite-binder-lowering.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-host-mc-finite-state-inject-sketch.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-hybrid-workflow.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-kernel-classical-boundary.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-language-specification.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-operator-algebra.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-parametric-circuit.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-static-hilbert-kernel.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-v1-adr-0057-showcase-boundary.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-v1-continuous-lane-b-expressiveness-scenarios.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-v1-normative-outline-s12.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-v1-open-topics-permanent-out.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-v1-quantum-mental-model-follow-up.md` | SELECTED design input | WP-0092 |
| `docs/specs/staqex-v1-quantum-semantic-ir-plan.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-v1-representative-program-rebaseline.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-v1-s01-coverage-scorecard.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-v1-s01-locked-scenario.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-v1-trait-effect-surface-examples.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/specs/staqex-workflow-surface.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/work-plans/WP-0003-examples-driven-brush-up.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/work-plans/WP-0020-scientific-input-and-parameter-binding.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/work-plans/WP-0021-observation-checkpoints-and-execution-diagnostics.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/work-plans/WP-0022-jobresult-observation-integration.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/work-plans/WP-0023-local-observation-plan-execution.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/work-plans/WP-0024-indexed-operator-and-binder-surface.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/work-plans/WP-0025-staqex-v1-north-star.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/work-plans/WP-0029-current-hardware-delivery-horizon.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/work-plans/WP-0069-operations-review-intake.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/work-plans/WP-0073-linear-transform-move.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/work-plans/WP-0091-decision-theme-canonicalization.md` | REJECT | not selected; map to current Issue/Spec/WP before any migration |
| `docs/work-plans/WP-0092-quantum-mental-model-follow-up.md` | SELECTED work-plan authority | WP-0092 |
| `examples/basics/README.md` | REJECT | not selected; no migration authority |
| `examples/showcase/S01_quantum_disaster_response/README.md` | REJECT | not selected; no migration authority |
| `scripts/check-coverage-ledger-consistency.py` | REJECT | not selected; no migration authority |
| `scripts/documentation_compression.py` | REJECT | not selected; no migration authority |
| `tests/spec_verification/suites/sv10_backend_targets.py` | REJECT | code/test migration requires a separate Issue and phase approval |
| `tests/test_jordan_wigner_mapping_red.py` | REJECT | code/test migration requires a separate Issue and phase approval |
| `tests/test_linear_hardening_slice_f_red.py` | REJECT | code/test migration requires a separate Issue and phase approval |
| `tests/test_quantum_scientific_aliases_red.py` | REJECT | code/test migration requires a separate Issue and phase approval |

Inventory count: 318 paths.

