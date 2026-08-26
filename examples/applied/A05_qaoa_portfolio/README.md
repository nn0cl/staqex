# A05 — QAOA portfolio

Small **QUBO portfolio** selection in Ising form: one QAOA layer
(mixer `X` then cost `Z`/`ZZ` terms). Harvested from `06` Ising patterns and
`12` graph-selection narrative.

## Units and interpretation

This example encodes a QUBO portfolio selection cost function; its
`H_cost`/`H_mixer` coefficients represent relative cost weights, not
physical energies. [ADR 0195](../../../docs/architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
applies to examples modeling real physical Hamiltonians; this example's
QUBO cost Hamiltonian is given real `Energy`/`Time` dimensions (`eV`,
`fs`) to satisfy the Kernel's fail-closed `evolve` requirement (LISS-0330),
but its magnitudes are arbitrary problem-defined units, not
literature-traced physical constants — unlike
[A03_h2_vqe](../A03_h2_vqe/README.md), whose coefficients are derived
from published H₂ literature data. See
[LISS-0333](../../../docs/issues/LISS-0333-a05-qaoa-arbitrary-unit-migration.md)
for the full design decision.

## Honesty

| Claim | Status |
|-------|--------|
| Real market data, risk models, or transaction costs | **No** |
| Classical portfolio optimization baseline | **No** |
| Single-layer QAOA-style `evolve` alternation on 2 qubits | **Yes** |
| Hamiltonian coefficients and evolve durations are real, dimensioned `Energy`/`Time` values (`eV`/`fs`), not bare unit-free numbers | **Yes**, since LISS-0333 |
| Those coefficient magnitudes are literature-traced physical constants | **No** — they are arbitrary relative cost weights; see "Units and interpretation" above |

## Bibliography

- Farhi, E., Goldstone, J., Gutmann, S. "A Quantum Approximate Optimization Algorithm." arXiv:1411.4028 (2014).
- Cerezo, M. et al. "Variational quantum algorithms." *Nature Reviews Physics* **3**, 625–644 (2021). (Survey.)

## Run

```bash
python3 -m compiler.staqex run examples/applied/A05_qaoa_portfolio/main_qaoa_portfolio.sqx --seed 0
```
