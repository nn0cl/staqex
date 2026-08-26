# A11 — Structural-monitoring quantum magnetometer

A 3-sensor NV-center-like array (site 1 "stressed", sites 0/2 "healthy")
detects a stress/defect signature via a symmetry-breaking transverse
coupling and real dipolar inter-sensor coupling. Rewritten from A11's
original "Noether Forge" quantum-matter-discovery theme (LISS-0120,
formally superseded — see `staqex-v1-showcase-mission-lock.md` §Locked
mission — "optional salvage only, not authoritative"), with the
Adjudicator's explicit direction to reuse and rewire the existing
14-module ownership tree around a real quantum-sensing application. The
official entry is `main_static.sqx` (self-contained runnable via path or
source, imports and wires all 14 modules).

This is the first of three planned quantum-sensing themes for this
directory; medical (biomagnetic cardiac/cerebral) and resource-exploration
(ore-body magnetic anomaly) themes are queued as future candidates, not
part of this migration.

## Units and interpretation

The NV-center zero-field splitting **D ≈ 2.87 GHz** is a real, extensively
published physical constant (Doherty, M.W. et al. "The nitrogen-vacancy
colour centre in diamond." *Physics Reports* **528**, 1–45 (2013)). This
example uses the standard **rotating-frame simplification** from magnetic-
resonance simulation: D defines the qubit basis and is transformed away,
not itself simulated — only the physically smaller, relevant terms are
evolved (`physics/hamiltonian_builder.sqx`):

- a transverse (`X`) defect/strain coupling on the stressed sensor
  (real physics — NV strain-magnetic coupling is documented in Barson et
  al. 2017 *Nano Lett.* and MacQuarrie et al. 2013 *PRL* — magnitude here
  is physically plausible in order but not traced to one specific cited
  measurement);
- a real dipolar (`ZZ`) coupling between neighboring sensors (same
  honesty category).

This is the same honesty category established for A06/A10's SSH
treatment: a real physical model class, illustrative-but-plausible
magnitudes, not literature-pinned numeric values.

**Kernel `expect(Z, …)` caveat**: this Kernel's `expect` does not perform
a true partial-trace reduced-density-matrix calculation on an entangled
multi-qubit state (a pre-existing simplification, not introduced or fixed
by this example) — so a healthy sensor's `⟨Z⟩` readout can read slightly
above `|1|` in magnitude when entangled with the stressed sensor via the
dipolar coupling. The qualitative signal (stressed sensor ≈ −1, healthy
≈ +1) is still clearly distinguishable and is what this example
demonstrates.

## Layout

```text
examples/applied/A11_noether_forge/
├── domain/               — sensor identity, couplings, array geometry, config
├── physics/               — rotating-frame Hamiltonian, model family, symmetry
├── application/            — quench protocol bundle, confidence scoring, evidence
├── presentation/            — human-readable detection label
└── main_static.sqx          — wires all of the above, real evolve + measurement
```

## Honesty

| Claim | Status |
|---|---|
| Full NV-center spin-1 physics (both `ms=±1` sublevels, real T1/T2) | **No** — a qubit (2-level) toy, not spin-1 |
| Production quantum sensing / calibrated magnetometer hardware | **No** |
| D≈2.87GHz zero-field splitting is a real, cited physical constant | **Yes**, Doherty et al. 2013 |
| Defect coupling / dipolar coupling magnitudes are literature-traced to one specific measurement | **No** — physically plausible in order, illustrative (contrast with A03) |
| The evolve Hamiltonian/duration use real, dimensioned `Energy`/`Time` values (ADR 0195) | **Yes**, since LISS-0338 |
| All 14 domain/physics/application/presentation modules are wired and exercised (not dead scaffolding) | **Yes**, since LISS-0338 |
| `expect(Z, …)` performs a rigorous partial-trace calculation on entangled sensors | **No** — a known Kernel simplification, see "Units and interpretation" |
| Stress/healthy signal is qualitatively distinguishable | **Yes** — stressed ≈ −1, healthy ≈ +1 |

## Kernel surfaces

- Type-First `state` / `Operator`, real `Energy`/`Time` dimensions (ADR 0195)
- Multi-file `import`, cross-module struct/enum types and free functions
- `evolve … under H for t`, `expect`, `inspect`, terminal `measure`

## Bibliography

- Doherty, M.W. et al. "The nitrogen-vacancy colour centre in diamond."
  *Physics Reports* **528**, 1–45 (2013). (D≈2.87GHz zero-field splitting.)
- Barson, M.S.J. et al. "Nanomechanical sensing using spins in diamond."
  *Nano Lett.* **17**, 4, 2652–2660 (2017). (NV strain-magnetic coupling.)
- MacQuarrie, E.R. et al. "Mechanical Spin Control of Nitrogen-Vacancy
  Centers in Diamond." *Phys. Rev. Lett.* **111**, 227602 (2013).

## Run

```bash
python3 -m compiler.staqex check examples/applied/A11_noether_forge/main_static.sqx
python3 -m compiler.staqex run examples/applied/A11_noether_forge/main_static.sqx --seed 0
```
