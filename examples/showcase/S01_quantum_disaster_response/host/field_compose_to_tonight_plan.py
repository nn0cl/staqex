#!/usr/bin/env python3
"""H→E bridge: CH-field-compose zone masses → finite tonight plan sample (LISS-0318).

Pipeline:
  1) Host field compose + inject (LISS-0317) → zone bin masses
  2) Map masses → ConstraintCoeffs-shaped floats (congestion, fairness)
  3) Run a **thin finite E-lane** program with those coeffs under constraint H
  4) Emit a JSON envelope (provenance + feed + plan sample)

Honesty:
  - Not Kernel Continuous; not city-wide continuous QC
  - Not a rewrite of main_disaster_response.sqx desk packs
  - Demonstrates causal map: Host zone feed → classical coeffs → evolve → measure
  - Full OS spine remains the constellation main; this is the compose-fed seat link
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_HOST = Path(__file__).resolve().parent
if str(_HOST) not in sys.path:
    sys.path.insert(0, str(_HOST))

from compiler.staqex.run import run_source  # noqa: E402

from field_compose_inject import run_field_compose  # noqa: E402


def zone_atoms_to_plan_coeffs(
    atoms: tuple[tuple[Any, float], ...],
) -> dict[str, float]:
    """Map finite zone masses → ConstraintCoeffs-like classical floats.

    Toy narrative (1-D K-ku bins 0..n-1):
      congestion — mass concentrated in mid / corridor-adjacent bins
      fairness  — flatter zone mass → higher fairness weight
    """
    if not atoms:
        raise SystemExit("zone_atoms_to_plan_coeffs: empty atoms — fail closed")
    by = {int(label): float(mass) for label, mass in atoms}
    n = max(by.keys()) + 1
    masses = [by.get(i, 0.0) for i in range(n)]
    total = sum(masses)
    if total <= 0.0:
        raise SystemExit("zone_atoms_to_plan_coeffs: zero mass — fail closed")
    # Normalize (should already be ~1 from inject)
    masses = [m / total for m in masses]

    # Mid third of bins ≈ corridor / dense ops pressure
    lo, hi = n // 3, max(n // 3 + 1, (2 * n) // 3)
    mid_mass = sum(masses[lo:hi])
    peak = max(masses)
    # Spread: 1 - peak (uniform → ~1-1/n; delta → 0)
    spread = 1.0 - peak

    congestion = 0.3 + 0.7 * min(1.0, mid_mass)
    fairness = 0.25 + 0.65 * min(1.0, max(0.0, spread))
    return {
        "congestion": float(congestion),
        "fairness": float(fairness),
        "_pad": 0.0,
    }


def _finite_plan_source(congestion: float, fairness: float) -> str:
    """Minimal E-lane program: Host-fed coeffs → constraint H → terminal measure."""
    # Literals only — no Continuous mid-program.
    return f"""
package examples.showcase.s01_disaster.host_zone_fed
// Generated narrative seat: zone inject → ConstraintCoeffs → finite plan.
// LISS-0318; not the full tonight spine desk.

pub fn main() -> Unit {{
    Float congestion = {congestion:.10f}
    Float fairness = {fairness:.10f}
    Operator H = congestion * (Z[0] * Z[1]) + fairness * (X[0] + X[1])
    State plan0 = |+>
    State plan1 = |0>
    State (plan0, plan1) = evolve {{ (plan0, plan1) under H for 0.35 using Suzuki(order = 2, steps = 4) }}.run()
    measure plan0 tracing_out plan1
}}
"""


def build_envelope(
    *,
    inject: Any,
    joint: Any,
    pipeline: list[str],
    coeffs: dict[str, float],
    plan_value: Any,
    seed: int,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "seat": "CH-field-compose",
        "bridge": "H_zone_to_E_plan",
        "lane_story": ["H-compose", "H-map-coeffs", "E-finite-plan"],
        "ideal_ref": "docs/specs/staqex-v1-continuous-lane-b-expressiveness-scenarios.md#2a",
        "continuous_pipeline": pipeline,
        "zone_atoms": [[label, mass] for label, mass in inject.atoms],
        "discretization": inject.provenance.get("discretization"),
        "plan_coeff_feed": {
            "shape": "Disaster.Physics.ConstraintCoeffs",
            "fields": coeffs,
            "mapping": (
                "zone bin masses → congestion (mid-band mass) + fairness "
                "(1 - peak mass); Host narrative feed for finite H"
            ),
        },
        "finite_plan": {
            "seed": seed,
            "measure_wire": "plan0",
            "sample_value": plan_value,
            "note": (
                "Thin E-lane evolve under constraint-shaped H; "
                "full OS spine (main_disaster_response.sqx) still owns desk packs"
            ),
        },
        "honesty": {
            "kernel_continuous": False,
            "city_wide_continuous_qc": False,
            "spine_rewritten": False,
        },
    }


def run_bridge(*, seed: int = 42, out: Path | None = None) -> dict[str, Any]:
    inject, joint, pipeline = run_field_compose(seed=seed)
    coeffs = zone_atoms_to_plan_coeffs(inject.atoms)
    src = _finite_plan_source(coeffs["congestion"], coeffs["fairness"])
    buf = io.StringIO()
    result = run_source(src, seed=seed, stdout=buf)
    if not result.ok or result.eval.measure is None:
        raise SystemExit(
            f"finite plan failed: compile_ok={result.compile_ok} "
            f"diags={result.diagnostics[:3]}"
        )
    plan_value = result.eval.measure.value
    envelope = build_envelope(
        inject=inject,
        joint=joint,
        pipeline=pipeline,
        coeffs=coeffs,
        plan_value=plan_value,
        seed=seed,
    )
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(envelope, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return envelope


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Write JSON envelope (zone + coeffs + plan sample)",
    )
    args = parser.parse_args()
    envelope = run_bridge(seed=args.seed, out=args.out)

    print("bridge: CH-field-compose Host zone → finite tonight plan (LISS-0318)")
    print("continuous_pipeline:", envelope["continuous_pipeline"])
    print("plan_coeff_feed:", envelope["plan_coeff_feed"]["fields"])
    print("finite_plan.sample_value:", envelope["finite_plan"]["sample_value"])
    print("honesty:", envelope["honesty"])
    if args.out:
        print("wrote:", args.out)


if __name__ == "__main__":
    main()
