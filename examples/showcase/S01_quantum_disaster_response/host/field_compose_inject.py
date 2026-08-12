#!/usr/bin/env python3
"""CH-field-compose Host substitute (LISS-0317 / Ideal §2A).

Ideal form (Lane B — NOT Runtime Continuous):
  Continuous damage, flood, fire, impassable
  Continuous risk   = weight(...)
  Continuous masked = mask(risk, impassable)
  State zone = finiteize(masked, ...)

This demo keeps the multi-step continuous algebra on the **Host (H-lane)**
with named stages and provenance ``continuous_pipeline``. Only the finite
Joint enters Kernel-shaped Born accounting (ADR 0163/0164).

Does **not** ship mid-program Continuous. Tonight spine stays finite.
Toy 1-D Ω=[0,1) — not GIS / city-wide continuous QC.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Callable

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.host_monte_carlo import HostRngPort, run_host_mc_inject

# --- Toy continuous fields on Ω = [0, 1) (Host-only; Ideal Continuous world) ---


def damage(x: float) -> float:
    """Collapse / damage density proxy — higher on eastern lowland band."""
    return 0.2 + 0.8 * math.exp(-((x - 0.25) ** 2) / (2 * 0.08**2))


def flood(x: float) -> float:
    """Inundation / liquefaction pressure — river-adjacent peak."""
    return 0.15 + 0.7 * math.exp(-((x - 0.55) ** 2) / (2 * 0.1**2))


def fire(x: float) -> float:
    """Fire / firestorm pressure — wooden dense pocket."""
    return 0.1 + 0.6 * math.exp(-((x - 0.4) ** 2) / (2 * 0.06**2))


def impassable(x: float) -> float:
    """1 = blocked geometry (Ideal mask); Host uses hard threshold."""
    # Blocked corridor band ~[0.35, 0.45)
    return 1.0 if 0.35 <= x < 0.45 else 0.0


def weight(d: float, fl: float, fi: float) -> float:
    """Ideal ``weight(damage, flood, fire)`` — pointwise operational pressure."""
    return d * (1.0 + fl) * (1.0 + fi)


def mask(risk: float, blocked: float) -> float:
    """Ideal ``mask(risk, impassable)`` — suppress where units cannot go."""
    return 0.0 if blocked >= 0.5 else risk


def masked_density(x: float) -> float:
    """Named continuous pipeline on Host (compose seat substitute)."""
    return mask(weight(damage(x), flood(x), fire(x)), impassable(x))


def _build_inverse_cdf(
    density: Callable[[float], float],
    *,
    n_grid: int = 512,
) -> tuple[list[float], list[float]]:
    """Piecewise-linear inverse CDF for sampling from a 1-D non-negative density."""
    xs = [i / n_grid for i in range(n_grid)]
    # half-open last edge at 1.0
    raw = [max(0.0, density(x)) for x in xs]
    total = sum(raw)
    if total <= 0.0:
        raise SystemExit("masked density vanished — fail closed (no silent empty inject)")
    masses = [r / total for r in raw]
    cdf: list[float] = []
    acc = 0.0
    for m in masses:
        acc += m
        cdf.append(acc)
    cdf[-1] = 1.0
    return xs, cdf


def _make_draw(xs: list[float], cdf: list[float]) -> Callable[[HostRngPort], float]:
    def continuous_draw(rng: HostRngPort) -> float:
        u = float(rng.random())
        # inverse CDF on piecewise-constant cells of width 1/n
        lo, hi = 0, len(cdf) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if cdf[mid] < u:
                lo = mid + 1
            else:
                hi = mid
        # uniform within cell [xs[i], xs[i]+dx)
        i = lo
        dx = 1.0 / len(xs)
        return min(1.0 - 1e-12, xs[i] + dx * float(rng.random()))

    return continuous_draw


CONTINUOUS_PIPELINE = [
    "field_from_host:damage",
    "field_from_host:flood",
    "field_from_host:fire",
    "field_from_host:impassable",
    "weight",
    "mask",
]


def run_field_compose(
    *,
    n_bins: int = 8,
    n_samples: int = 2000,
    seed: int = 42,
):
    """Host compose → finite inject. Return (inject, joint, pipeline)."""
    xs, cdf = _build_inverse_cdf(masked_density)
    continuous_draw = _make_draw(xs, cdf)
    inject, joint = run_host_mc_inject(
        domain_label="MaskedRisk",
        interval=(0.0, 1.0),
        n_bins=n_bins,
        n_samples=n_samples,
        coordinate="zone",
        continuous_draw=continuous_draw,
        seed=seed,
        label_mode="bin_index",
        provenance={
            "phase": "pre_tonight_field_compose",
            "seat": "CH-field-compose",
            "lane": "H",
            "ideal_ref": "docs/specs/staqex-v1-continuous-lane-b-expressiveness-scenarios.md#2a",
            "continuous_pipeline": list(CONTINUOUS_PIPELINE),
            "note": (
                "finite approximation of Host-composed masked risk; "
                "not mid-program Continuous; not city-wide continuous QC"
            ),
            "error_bound": "Unbounded",
            "omega": "[0,1) toy 1-D K-ku plane",
        },
    )
    return inject, joint, list(CONTINUOUS_PIPELINE)


def main() -> None:
    inject, joint, pipeline = run_field_compose()
    print("seat: CH-field-compose (Host substitute — Ideal §2A)")
    print("lane: H  |  Kernel Continuous: no")
    print("continuous_pipeline:", pipeline)
    print("discretization:", inject.provenance["discretization"])
    print("atoms (zone_bin, mass):", inject.atoms)
    born = sum(abs(w.amp) ** 2 for w in joint.worlds)
    print("born_sum:", round(born, 6))
    print("next: host/field_compose_to_tonight_plan.py  # H→E zone feed (LISS-0318)")


if __name__ == "__main__":
    main()
