# LISS-0483 source and observation conformance evidence

Evidence record, not a language specification. Authority:
[mental-model follow-up](../specs/staqex-v1-quantum-mental-model-follow-up.md#detailed-follow-up-issue-design)
and [ADR 0191](../architecture/adr/0191-ascii-quantum-notation-and-lexical-boundary.md).
Date: 2026-09-05. Parent: WP-0092. Previous correction merged in PR #577,
`da011801`; this inventory does not declare the issue complete.

All test paths below are relative to `tests/`. A passing test proves only the
named boundary; it does not imply complete language-family or hardware support.

| Family / proof | Deterministic evidence | Result and remaining gap |
|---|---|---|
| ASCII psi and display identity | `test_liss_0480_scientific_lexicon_contract_red.py::test_ascii_alias_and_blackboard_display_form_share_one_identity` | Pass; phi/rho and typed-context variants need coverage |
| Unicode source rejection | Same file, `test_unsupported_scientific_spelling_has_actionable_diagnostic` | Pass for API rejection; fixture is a fragment, not a full lexer acceptance proof |
| Alias scope/shadowing | Same file, `test_contextual_classical_name_remains_available_and_shadowing_is_deterministic` | Pass is insufficient: fixture has no shadowed declaration |
| Commutator display and comments | `test_liss_0483_observation_lexicon_conformance_red.py` | Pass for comments, actual operands and multiple calls; strings, nested calls and arbitrary operands remain uncovered |
| Invalid lexicon source | Same file, `test_invalid_source_cannot_produce_lexicon_bindings` | Pass: compile-invalid source cannot yield bindings |
| Mix control, branches and provenance | `test_liss_0448_coin_mix_semantic_red.py` | 8 pass; includes source spans, fingerprint changes and explicit QPU rejection |
| Superpose AST and type | `test_liss_0320_superpose_formal_grammar_red.py` | Distinct AST/type tests pass |
| Deferred Superpose evaluation | Same file, `test_evaluating_superpose_fails_closed_not_open` | Pass: COHERENT_EXECUTION_UNSUPPORTED and no measurements |
| Superpose unitarity | `test_liss_0376_unitarity_superpose_dispatch_red.py` | 2 pass; non-unitary map rejection |
| controlled call-form classification | `test_s02_selection_surface_red.py::test_controlled_is_not_lowered_to_mixture` | Pass; classification proof, not execution equivalence |
| when retirement | Same file, `test_removed_when_fails_without_mix_fallback` | Pass: RETIRED_KEYWORD, no Mix fallback |
| Inspect / terminal Measure inventory | `test_liss_0481_observation_contract_red.py` first three tests | Pass for order, diagnostic/non-collapsing Inspect and terminal Measure |
| Observation exactness/dimensions | `test_liss_0483_observation_lexicon_conformance_red.py::test_mapping_retains_semantic_values_including_unknowns` | 2 pass; canonical unknowns retained |
| Projection amplitude / explicit normalization | `test_liss_0431_project_no_implicit_renorm_red.py` first three tests | Pass for numerical source execution |
| Unsupported projection rejection | Same file, `test_project_onto_general_operator_rejects_non_diagonal` | Pass: test now requires the concrete `KernelError`; it cannot pass from its own assertion |
| Tomography compiler capability | `test_quantum_observation_contract_red.py` | Pass: OBSERVATION_CAPABILITY_UNSUPPORTED |
| Invalid observation fragments | `test_liss_0483_observation_source_evidence_red.py::test_invalid_fragment_cannot_fabricate_observation_evidence` | Pass: invalid source is rejected; no synthetic IDs |
| Actual projection inventory | Same file, `test_real_projection_is_reported_before_terminal_measurement` | Pass: contract and mapping report Project then terminal Measure with canonical IDs |
| expect / trace_out real-source inventory | `test_liss_0483_observation_source_evidence_red.py::test_real_non_collapsing_observation_calls_are_source_owned` | Pass: real calls retain source-owned IDs, non-collapsing lanes and lineage policy |

## Verification and next bounded correction

Selected suites: 43 pass across 0320, 0376, 0448, 0431,
quantum_observation_contract and 0480–0483 (prior regression file). S02 selection
adds 3 pass. New source-evidence suite: 5 failures before correction and 5 pass
after correction. A counted pass in
the table may still be inadequate proof, as explicitly noted above.

Correction completed: reject invalid fragments using the existing public error,
remove synthetic fallback evidence, and report the real projection call with
its canonical source node ID before terminal Measure. The four legacy
synthetic-success assertions were explicitly updated during the transition.
Do not reject source-only observations merely because finite lowering has
missing-evidence diagnostics: the accepted projection fixture has valid source
semantics and such diagnostics.

After that: strengthen projection rejection proof, replace lexicon raw-source
scanning with source-owned evidence, cover alias declaration contexts and
shadowing, then real expect/trace_out and dynamic-lane/provenance/loss coverage.
Each step remains bounded; no general tomography or POVM implementation is
authorized by this matrix.
