# A06 — Topological edge memory

SSH edge occupation as pedagogical **topological memory** on a tight-binding chain.

Legacy source: `examples/10_topological_physics/`.

## Units and interpretation

The SSH hopping amplitudes (`v_intra`, `w_inter`) are a real physical
`Energy` quantity in real tight-binding systems (e.g. polyacetylene).
Since [ADR 0195](../../../docs/architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
(LISS-0334), `build_ssh_hamiltonian()`'s coefficients are real `eV`-scale
`Energy` values (ratio unchanged from the original `0.5`/`1.5`), and the
evolution duration is a real `fs`-scale `Time` value — but these
magnitudes are **physically plausible for a tight-binding hopping
amplitude, not traced to a specific cited measurement** (contrast with
[A03_h2_vqe](../A03_h2_vqe/README.md), whose coefficients are derived
from published literature data). See
[LISS-0334](../../../docs/issues/LISS-0334-a06-ssh-real-unit-migration.md)
for the full design decision.

## Layout

```text
examples/applied/A06_topological_edge_memory/
├── domain/
│   ├── topology.sqx
│   └── ssh_parameters.sqx
├── operators/
│   └── hamiltonian_builder.sqx
└── main_topological_edge_memory.sqx
```

## Honesty

| Claim | Status |
|-------|--------|
| Full SSH phase diagram / disorder / finite-size scaling | **No** |
| OOP domain + multi-file `import` + `evolve` on `hop` Hamiltonian | **Yes** |
| Production topological qubit / Majorana hardware | **No** |
| Hamiltonian coefficients and evolve duration are real, dimensioned `Energy`/`Time` values (`eV`/`fs`), not bare unit-free numbers | **Yes**, since LISS-0334 |
| Those coefficient magnitudes are literature-traced to a specific measurement | **No** — physically plausible in magnitude for a tight-binding hopping amplitude, but pedagogical, not a reproduction of a cited paper's numeric SSH parameters; see "Units and interpretation" above |

## Bibliography

- Su, W. P., Schrieffer, J. R., Heeger, A. J. "Solitons in polyacetylene." *Phys. Rev. Lett.* **42**, 1698 (1979).

## Run

```bash
python3 -m compiler.staqex run examples/applied/A06_topological_edge_memory/main_topological_edge_memory.sqx --seed 0
```
