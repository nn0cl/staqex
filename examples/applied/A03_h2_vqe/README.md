# A03 — H₂ VQE (minimal)

Demonstrates `FermionOperator` construction, `map(…, JordanWigner)`, and
Schrödinger `evolve` on the mapped qubit Hamiltonian — a **toy** stand-in for
variational chemistry workflows. Since [ADR 0195](../../../docs/architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
(LISS-0332), the Hamiltonian's coefficients and the evolution duration are
real, dimensioned physical quantities (Hartree / femtoseconds), not bare
unit-free numbers — but this remains a minimal two-orbital toy model, not a
computed molecular-chemistry result. See the full derivation and its stated
limitations:
[docs/research/2026-08-05-h2-two-orbital-jordan-wigner-cross-validation.md](../../../docs/research/2026-08-05-h2-two-orbital-jordan-wigner-cross-validation.md).

## Honesty

| Claim | Status |
|-------|--------|
| Full VQE optimizer loop / parameter-shift gradients | **No** |
| Production molecular integrals or basis sets (this program does not run PySCF/OpenFermion or any electronic-structure solver) | **No** |
| Fermion → JW → `evolve` on 2 qubits | **Yes** |
| Hamiltonian coefficients (ε0, ε1, coupling, interaction) are real, dimensioned Energy values (`Ha`/`eV`), not bare unit-free numbers | **Yes**, since LISS-0332 |
| Those coefficient values are literature-traced — derived by solving the Jordan-Wigner mapping identities backward from published two-qubit H₂ Hamiltonian coefficients (R = 0.75 Å, traced to O'Malley et al. 2016 Table 1 via a secondary tutorial source, not independently re-verified against the primary PDF) | **Yes, with that provenance caveat** — see the research note |
| The nuclear-repulsion constant added to close the model's identity-term gap is a real, independently-computed physical quantity (1/R in atomic units), not a fitted fudge factor | **Yes** — matches the gap to within 0.0043% (research note §6-7) |
| The evolution duration (`1.0 fs`) reproduces a specific published Trotter-step protocol | **No** — it is an illustrative, physically-plausible electronic-timescale duration, not derived from a cited source |
| This program's own output was cross-checked live against the cited literature coefficients (e.g. by dumping the compiled `QubitOperator` and diffing) | **No** — the cross-check is a hand/symbolic derivation (research note); a live automated check is documented there as follow-up work, not yet built |

## Bibliography

- Peruzzo, A. et al. "A variational eigenvalue solver on a quantum processor." *Nature Communications* **5**, 4213 (2014).
- Kandala, A. et al. "Hardware-efficient variational quantum eigensolver for small molecules." *Nature* **549**, 242–246 (2017). (Context.)
- Cerezo, M. et al. "Variational quantum algorithms." *Nature Reviews Physics* **3**, 625–644 (2021). (Survey.)
- O'Malley, P. J. J. et al. "Scalable Quantum Simulation of Molecular Energies." *Physical Review X* **6**, 031007 (2016). (Source of the two-qubit H₂ Hamiltonian coefficients this example's Hamiltonian is derived from; see the research note for the exact secondary-source provenance.)

## Run

```bash
python3 -m compiler.staqex run examples/applied/A03_h2_vqe/main_h2_vqe.sqx --seed 0
python3 -m compiler.staqex emit-qasm examples/applied/A03_h2_vqe/main_h2_vqe.sqx
```
