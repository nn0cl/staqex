# Host MC → finite State inject (ADR 0163 / 0164)

Runnable Host demo: continuous draw → equal-width histogram finiteization →
finite Joint Born masses. No Kernel `Continuous` type.

**Notebook surface (preferred teaching path):** ADR 0185 Lane A

```bash
python3 -m compiler.staqex run --seed 0 \
  examples/basics/B18_finiteize/finiteize_surface.sqx
```

```bash
python3 examples/host/mc_finite_inject_demo.py
```

## Live QPU demo (AWS Braket)

[`live_qpu_braket_demo/`](live_qpu_braket_demo/) — end-to-end
`submit-live-qpu` / `qpu-job-status` / `qpu-job-wait` / `qpu-job-result`
CLI walkthrough (ADR 0202/0203, LISS-0392/0393/0396/0397) against a real
AWS Braket device. Local verification is free; the real-submission steps
are written for you to run yourself — no agent in this repository invokes
them autonomously.
