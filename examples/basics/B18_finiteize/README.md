# B18 — `finiteize` surface

Teaches ADR 0185 **Lane A**: continuous → finite is an **explicit** notebook
step. There is no mid-program `Continuous` Kernel type.

```text
State psi = finiteize(lo, hi, n_bins, n_samples[, seed])
Measure psi
```

MVP uses Host equal-width histogram (ADR 0163/0164) of **uniform** continuous
draws on half-open `[lo, hi)`. Labels are bin indices `0 .. n_bins-1`.

Python Host inject remains valid (`examples/host/mc_finite_inject_demo.py`).

```bash
python3 -m compiler.staqex run --seed 0 \
  examples/basics/B18_finiteize/finiteize_surface.sqx
```
