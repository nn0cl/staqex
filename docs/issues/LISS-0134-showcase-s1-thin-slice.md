# LISS-0134: Showcase S1 vertical thin slice

## Metadata

- Local issue ID: LISS-0134
- Status: **complete** — 2026-07-31 (awaiting Adjudicator PR merge review)
- Phase: Feature Path Red → Green → Refactor (integrated; S1 authorize)
- Type: showcase / examples
- Priority: P0
- Depends on: [LISS-0127](../architecture/documentation-compression-map.md) S0;
  [LISS-0126](../architecture/documentation-compression-map.md) P2; Option B complete
- Spec: [rebaseline S1](../specs/staqex-v1-representative-program-rebaseline.md);
  [historical S1 example](../../examples/showcase/quantum_matter_discovery/README.md)
- Branch: `feature/liss-0134-showcase-s1-thin-slice`
- Implementation permission: **yes** (S1 authorize 2026-07-31 「承認」)
- Entry: `examples/showcase/quantum_matter_discovery/main_quantum_matter_discovery.sqx`
- Tests: `tests/test_showcase_s1_thin_slice_red.py`

## Summary

Ship one multi-file quantum-matter discovery spine:
prepare → evolve → expect/inspect → terminal measure, with domain/physics
modules supplying real couplings and duration. Prove required P1 ledger rows
for the thin slice. No live QPU; soft QSEM OK.

## Exit

- [x] Phase 1 Red failing acceptance suite
- [x] Phase 2 Green: `examples/showcase/quantum_matter_discovery/` green
  `compile` + `run_path`
- [x] Phase 3 Refactor / docs sync
- [x] No unused modules in the spine tree
- [ ] Adjudicator PR merge review

## Notes

- Sparse Pauli `Operator` return from helper `fn` — **fixed**
  [LISS-0136](LISS-0136-sparse-pauli-operator-return.md); showcase physics
  uses `build_ising_hamiltonian()`.
- Classical Float from fields/methods unbound in Operator / `evolve for` —
  [LISS-0137](LISS-0137-classical-float-operator-evolve-binding.md); duration
  literal + schedule inspect workaround.
- `when` ket prepare arms — [LISS-0138](LISS-0138-when-ket-prepare-arms.md);
  classical label arms (B02).
- Import basename `observe` is a retired keyword → protocol file is `quench.sqx`
  (intentional language rule; not a defect Issue).
