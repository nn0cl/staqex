# A10 — Mission observatory (slim capstone)

Integration read path across **domain modules**, **SSH evolve**, **static QPU lane**,
and **Bell link** — without re-expanding into the full legacy kitchen sink.

Legacy source: slimmed from `examples/16_quantum_observatory/`.

## Units and interpretation

The SSH hopping amplitudes in `operators/ssh_hamiltonian.sqx` are a real
physical `Energy` quantity in real tight-binding systems. Since
[ADR 0195](../../../docs/architecture/adr/0195-real-hbar-hamiltonian-dynamics.md)
(LISS-0335), `build_ssh_hamiltonian()`'s coefficients are real `eV`-scale
`Energy` values (ratio unchanged from the original `0.5`/`1.5`), and
`Config.duration` is a real `fs`-scale `Time` value — but these
magnitudes are **physically plausible for a tight-binding hopping
amplitude, not traced to a specific cited measurement**, the same
honesty category established for
[A06_topological_edge_memory](../A06_topological_edge_memory/README.md).
See
[LISS-0335](../../../docs/issues/LISS-0335-a10-mission-observatory-real-unit-migration.md)
for the full design decision, including a noted (not fixed) Kernel
limitation around dimensioned struct-field-access durations.

## What this capstone is not

- Not the only place a surface is documented — see B01–B12 and A06–A09.
- Not a production mission simulator, provider SDK, or full open-systems lab
  (Lindblad: see B12 / future A07).

## Honesty

| Claim | Status |
|-------|--------|
| Full observatory (walk, Grover, interferometer, Lindblad in one file) | **No** |
| Multi-module `import` + SSH + QPU register + Bell witness | **Yes** |
| Real spacecraft operations / spectrum mission data | **No** |
| Hamiltonian coefficients and evolve duration are real, dimensioned `Energy`/`Time` values (`eV`/`fs`), not bare unit-free numbers | **Yes**, since LISS-0335 |
| Those coefficient magnitudes are literature-traced to a specific measurement | **No** — physically plausible in magnitude, pedagogical, not a reproduction of a cited paper's numeric SSH parameters; see "Units and interpretation" above |

## Run

```bash
python3 -m compiler.staqex run examples/applied/A10_mission_observatory/main_mission_observatory.sqx --seed 0
```

## Suggested read order

`B01 → … → B10 → A06 → A09 → A10` (see `docs/specs/staqex-examples-catalog-v2.md` §6).
