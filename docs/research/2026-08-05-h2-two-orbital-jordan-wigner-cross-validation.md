# Research: minimal two-orbital fermionic model ↔ literature H₂ qubit Hamiltonian (Jordan-Wigner cross-validation)

## Status

Verification/derivation record, produced during
[WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md) work
unit 2 design intake (`A03_h2_vqe` real-unit migration). This is **not** a
claim of new physics — the underlying result (electronic energy plus a
classical nuclear-repulsion constant equals total molecular energy) is
standard, textbook Born-Oppenheimer quantum chemistry. What this note
documents is a specific, explicit, checkable derivation connecting one
compiler's shipped Jordan-Wigner implementation, a minimal two-orbital
toy Hamiltonian's four free parameters, and a set of widely-reproduced,
literature-traced qubit-Hamiltonian coefficients — written down so the
chain of reasoning and arithmetic is reviewable, since this specific
connection did not appear already written out anywhere the author could
find. A live numerical cross-check against Staqex's own compiled output
was not performed when this note was first written (see Limitations);
it has since been performed and automated as a regression test — see
Follow-up.

## Research question

Does Staqex's shipped Jordan-Wigner mapping
(`compiler/staqex/second_quantization.py`) produce the same qubit
operator structure that the H₂ variational-quantum-eigensolver literature
reports for a minimal two-orbital model, and can the constant-term
(identity-coefficient) discrepancy between a bare "hopping + interaction"
toy Hamiltonian and the literature's full electronic Hamiltonian be
explained quantitatively, not just qualitatively?

## Method

### 1. Staqex's Jordan-Wigner convention

`compiler/staqex/second_quantization.py`'s module docstring states the
shipped convention (ADR 0093):

```text
a_p     = (prod_{k<p} Z_k) * (X_p + i Y_p) / 2
a_p^dag = (prod_{k<p} Z_k) * (X_p - i Y_p) / 2
```

This is the standard Jordan-Wigner transform as presented in Whitfield,
J. D., Biamonte, J., & Aspuru-Guzik, A. (2011), "Simulation of electronic
structure Hamiltonians using quantum computers," *Molecular Physics*,
109(5), 735-750
([arXiv:1001.3855](https://arxiv.org/abs/1001.3855)).

### 2. Symbolic derivation for two orbitals (sites 0, 1)

Using Staqex's own convention and the single-site Pauli product table
already implemented in `second_quantization.py` (`_PAULI_MUL`), the
following identities were derived by hand and cross-checked term-by-term
against that table (not re-derived from a different source's table):

```text
n_p = a_p^dag a_p = (I - Z_p) / 2

a_0^dag a_1 + a_1^dag a_0 = (X_0 X_1 + Y_0 Y_1) / 2

n_0 n_1 = (I - Z_0 - Z_1 + Z_0 Z_1) / 4
```

The hopping-term identity was verified by direct Pauli-algebra
substitution using `second_quantization.py`'s own multiplication table
values (`X·Z = -iY`, `Y·Z = iX`, `Z·X = iY`, `Z·Y = -iX`), confirming the
Jordan-Wigner string factor on site 1 cancels against the ladder-operator
combination exactly as the standard identity predicts, for this specific
implementation's sign convention.

### 3. A minimal parameterized two-orbital Hamiltonian

Take a generic two-orbital "hopping + on-site energy + interaction"
fermionic Hamiltonian, matching `examples/applied/A03_h2_vqe`'s existing
operator structure extended with the two on-site (orbital-energy) terms
it did not yet have:

```text
H = ε0 n_0 + ε1 n_1 + t (a_0^dag a_1 + a_1^dag a_0) + U n_0 n_1
```

Substituting the identities above and collecting terms by Pauli string
gives the mapped qubit Hamiltonian:

```text
H = g0 I + g1 Z_0 + g2 Z_1 + g3 Z_0 Z_1 + g4 X_0 X_1 + g5 Y_0 Y_1

g0 = ε0/2 + ε1/2 + U/4
g1 = -ε0/2 - U/4
g2 = -ε1/2 - U/4
g3 = U/4
g4 = g5 = t/2
```

This is the same six-term operator basis (`I`, `Z_0`, `Z_1`, `Z_0 Z_1`,
`X_0 X_1`, `Y_0 Y_1`) used by the widely-cited symmetry-reduced two-qubit
H₂ Hamiltonian in the VQE literature — see §4. This note does not claim
that plain Jordan-Wigner mapping alone produces that two-qubit reduction
for the full H₂ problem: the literature's two-qubit form is reached from
a four-spin-orbital (four-qubit) Jordan-Wigner-mapped Hamiltonian via an
additional symmetry-fixing/qubit-tapering step (particle-number and spin
symmetry), which this note's minimal two-orbital model does not perform
or need — it is parameterized directly at two orbitals/two qubits, and
the claim here is only that its Jordan-Wigner-mapped operator *basis*
coincides with the literature's, not that the reduction procedure is the
same.

### 4. Qubit Hamiltonian coefficients used for this cross-check (H₂, R = 0.75 Å)

The coefficients below are widely-reproduced pedagogical values traced to
O'Malley, P. J. J. et al. (2016), "Scalable Quantum Simulation of
Molecular Energies," *Physical Review X*, 6, 031007
([arXiv:1512.06860](https://arxiv.org/abs/1512.06860)), Table 1, at bond
length R = 0.75 Å (close to the equilibrium bond length, 0.7414 Å). This
note used the reproduction in
[ENCCS Quantum Autumn School 2023, "Tutorial: quantum
chemistry"](https://enccs.github.io/qas2023/notebooks/E2_VQE-H2/), which
states it is taken from that Table 1:

```text
g0 = 0.2252   g1 = 0.3435   g2 = -0.4347
g3 = 0.5716   g4 = 0.091    g5 = 0.091   (Hartree)
```

**Provenance caveat**: these six numbers were **not** independently
re-extracted from the primary paper's PDF in this session (table
extraction was attempted and failed to reliably parse); they are taken
on the secondary source's word that they reproduce Table 1. A reader
preparing this for formal peer review, or citing these specific digits
elsewhere, should re-verify them directly against the primary source
first — this note's own conclusion (§7) does not depend on their exact
digits being flawless, only on internal consistency with the derivation
in §5-§6, but any *external* citation of these six values should go
through the primary source.

### 5. Solving for the fermionic parameters

`g4 = g5 = 0.091` (equal, as the symmetric hopping form predicts) gives:

```text
t  = 2 g4                = 0.182     Hartree
U  = 4 g3                = 2.2864    Hartree
ε0 = -2(g1 + U/4)        = -1.8302   Hartree
ε1 = -2(g2 + U/4)        = -0.2738   Hartree
```

### 6. The g0 (identity-coefficient) discrepancy

Substituting the derived ε0, ε1, U back into `g0 = ε0/2 + ε1/2 + U/4`:

```text
g0 (predicted from this minimal model) = -0.4804   Hartree
g0 (literature)                        =  0.2252   Hartree
discrepancy                            =  0.7056   Hartree
```

This minimal model has no term representing the classical nuclear-nuclear
Coulomb repulsion — a constant (not operator-valued) contribution that
standard quantum chemistry Hamiltonians add to the electronic
Hamiltonian's eigenvalues to obtain the total Born-Oppenheimer molecular
energy (see e.g. Szabo & Ostlund, *Modern Quantum Chemistry*, §3.1). For
two unit nuclear charges separated by `R`, in atomic units:

```text
E_nn = 1 / R_bohr
```

Computed independently (CODATA 2018 Bohr radius, `a0 =
0.529177210903e-10` m, `R = 0.75 A`):

```text
R_bohr = 0.75e-10 / 0.529177210903e-10 = 1.4172945934693275
E_nn   = 1 / R_bohr                    = 0.7055696145373334   Hartree
```

### 7. Result

```text
discrepancy (from the qubit-coefficient derivation) = 0.7056 Hartree
E_nn (from bond length, independent calculation)     = 0.70557 Hartree
relative difference                                  = 0.0043 %
```

The two values agree to within the precision of the four-decimal
literature coefficients used in §4. This is consistent with (does not
contradict) the standard interpretation: the literature's reported `g0`
already includes the nuclear repulsion constant (and any other core/basis
contributions folded into the identity coefficient by the quantum
chemistry package that produced Table 1), while this minimal two-orbital
electronic-only model's own identity coefficient does not.

## Limitations

- The literature coefficients (§4) were sourced from a secondary
  reproduction, not the primary paper's PDF directly — flagged above,
  not independently re-verified in this session.
- This is a symbolic derivation cross-checked against Staqex's own
  multiplication table, not a live numerical run of Staqex's compiler on
  the full six-term Hamiltonian compared bit-for-bit against a reference
  matrix exponential. A live numerical Staqex-side confirmation (compile
  and inspect the mapped `QubitOperator`'s coefficients directly) was not
  performed as part of this note and would strengthen it further.
- `R = 0.75 Å` (the tutorial's stated value) is not exactly the
  equilibrium bond length (0.7414 Å per the same tutorial); the near-exact
  numeric agreement found here is specific to R = 0.75 Å and would need
  recomputing for a different bond length.
- This note does not claim the four derived parameters (ε0, ε1, t, U) are
  the "true" orbital energies of any specific quantum-chemistry
  calculation (e.g. Hartree-Fock orbital energies in a specific basis) —
  they are values that make this specific minimal model's qubit-mapped
  coefficients match the cited literature numbers, nothing stronger.

## Application

This derivation grounds
[WP-0095](../work-plans/WP-0095-real-hbar-hamiltonian-dynamics.md) work
unit 2's `A03_h2_vqe` migration: the fermionic Hamiltonian is extended
with the two on-site energy terms it previously lacked, parameterized
with the derived ε0/ε1/t/U values (each attached to a real `Energy`
dimension via Staqex's Type-First unit system), and the nuclear
repulsion constant is added explicitly as a separate `E_nn * I` term
after the Jordan-Wigner mapping — making the resulting qubit Hamiltonian
numerically consistent with the cited literature values, not merely
dimensionally real.

## Follow-up

**Done (2026-08-07, LISS-0351)**: this note's cross-check was symbolic
only until now. `A03_h2_vqe`'s actual compiled `H_electronic`
`QubitOperator` was extracted from a live `run_path` execution and its
six Pauli-term coefficients converted from Joules back to Hartree.
Result — all six match this note's derived/literature values to the
literature source's own 4-decimal precision:

| Term | Computed (live, post-LISS-0350) | This note / literature |
|---|---|---|
| I (electronic only) | −0.4804 Ha | −0.4804 Ha (§6, derived) |
| Z0 | 0.3435 Ha | 0.3435 Ha (`g1`) |
| Z1 | −0.4347 Ha | −0.4347 Ha (`g2`) |
| Z0Z1 | 0.5716 Ha | 0.5716 Ha (`g3`) |
| X0X1 | 0.0910 Ha | 0.091 Ha (`g4`) |
| Y0Y1 | 0.0910 Ha | 0.091 Ha (`g5`) |

`g0_electronic + E_nn = −0.4804 + 0.70557 = 0.2252 Ha`, matching the
literature's full `g0 = 0.2252 Ha` to within `0.013%` — consistent
with this note's own §7 symbolic result. This closes the gap named
above: the derivation is now independently confirmed against Staqex's
actual compiled output, not merely cross-checked by hand against the
mapping's own multiplication table.

Automated as a regression test:
[`tests/test_liss_0351_a03_jw_literature_crosscheck_red.py`](../../tests/test_liss_0351_a03_jw_literature_crosscheck_red.py)
(Local Issue
[LISS-0351](../issues/LISS-0351-a03-jw-literature-crosscheck-test.md)),
so a future regression in Staqex's own Jordan-Wigner implementation
would be caught automatically. This finding was reached via
[LISS-0350](../issues/LISS-0350-jw-mapping-scale-relative-tolerances.md),
which found and fixed a real bug this note's own symbolic cross-check
could not have caught on its own: `second_quantization.py`'s absolute
`_ZERO_TOL` epsilon was silently zeroing every term of this
Hamiltonian at its real Joule-scale magnitude (~1e-18), so
`A03_h2_vqe`'s `evolve` had produced no real H2 electronic-structure
dynamics from its own real-unit migration (LISS-0332) until that fix
landed — this note's derivation was correct throughout, but Staqex's
runtime output did not yet match it until LISS-0350.

**Not done**: the "Provenance caveat" in §4 (the literature
coefficients were sourced from a secondary reproduction, not
independently re-extracted from the primary O'Malley et al. 2016
paper's PDF) remains open — out of scope for both this note and
LISS-0351.
