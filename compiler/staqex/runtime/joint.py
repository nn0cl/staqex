"""Joint store with complex amplitudes (stance a → amplitude-ready).

Each world carries amplitude c ∈ ℂ. Born weight is |c|².
Per-coordinate phase factors (from `phase`) apply when reading that
coordinate for interference — they do not mutate the shared world amp.

Coalescing **sums amplitudes** (interference); vacuum when Σ|c|² = 0.
"""

from __future__ import annotations

import cmath
import math
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Callable, Iterable, Iterator

EPS = 1e-12

_world_workers: ContextVar[int] = ContextVar("staqex_world_workers", default=1)


@contextmanager
def world_workers(n: int) -> Iterator[None]:
    """ADR 0159: opt-in CPU workers for independent Joint world maps."""
    token = _world_workers.set(max(1, int(n)))
    try:
        yield
    finally:
        _world_workers.reset(token)


def current_world_workers() -> int:
    return max(1, int(_world_workers.get()))


def _coerce_joint_atom(value: Any) -> Any:
    """ADR 0160: Fraction may live on classical scalars; Joint coords stay f64."""
    if isinstance(value, Fraction):
        return float(value)
    return value


def _as_amp(x: complex | float | int) -> complex:
    if isinstance(x, complex):
        return x
    return complex(float(x), 0.0)


@dataclass
class World:
    assign: dict[str, Any]
    amp: complex
    # Multipliers applied when reading a coordinate's amplitude (interfer / phase).
    coord_phase: dict[str, complex] = field(default_factory=dict)

    @property
    def mass(self) -> float:
        """Born probability weight |amp|² (compat alias)."""
        return float(abs(self.amp) ** 2)

    def amp_of(self, name: str) -> complex:
        """Amplitude attributed to coordinate `name` (includes coord phase)."""
        return self.amp * self.coord_phase.get(name, 1.0 + 0.0j)


@dataclass
class Joint:
    """Finite-support joint over named coordinates with complex amplitudes."""

    worlds: list[World] = field(default_factory=list)

    @staticmethod
    def empty() -> Joint:
        return Joint(worlds=[])

    @staticmethod
    def unit() -> Joint:
        return Joint(worlds=[World(assign={}, amp=1.0 + 0.0j)])

    def norm(self) -> float:
        """Σ |c|²."""
        return float(sum(abs(w.amp) ** 2 for w in self.worlds))

    def is_vacuum(self) -> bool:
        return abs(self.norm()) <= EPS or len(self.worlds) == 0

    def variables(self) -> list[str]:
        keys: set[str] = set()
        for w in self.worlds:
            keys.update(w.assign.keys())
        return sorted(keys)

    def marginal(self, name: str) -> dict[Any, float]:
        """Born marginal: Σ |c|² over worlds with given coordinate value."""
        acc: dict[Any, float] = defaultdict(float)
        for w in self.worlds:
            if name in w.assign:
                acc[w.assign[name]] += abs(w.amp) ** 2
        return {k: v for k, v in acc.items() if v > EPS}

    def amplitude_marginal(self, name: str) -> dict[Any, complex]:
        """Sum complex amplitudes for each value of `name` (interferes paths)."""
        acc: dict[Any, complex] = defaultdict(complex)
        for w in self.worlds:
            if name in w.assign:
                acc[w.assign[name]] += w.amp_of(name)
        return {k: v for k, v in acc.items() if abs(v) ** 2 > EPS}

    def support_rows(self) -> list[dict[str, Any]]:
        return [
            {
                "assignment": dict(w.assign),
                "mass": w.mass,
                "amp": w.amp,
                "coord_phase": dict(w.coord_phase),
            }
            for w in self.worlds
        ]

    def merge_support(self) -> Joint:
        """ADR 0139: merge equal atoms (sum amplitudes) and prune |amp|² ≤ EPS."""
        if self.is_vacuum():
            return Joint.empty()
        return Joint(worlds=_coalesce(self.worlds))

    def bind_const(self, name: str, value: Any) -> Joint:
        if self.is_vacuum():
            return Joint.empty()
        coerced = _coerce_joint_atom(value)
        return Joint(
            worlds=[
                World(
                    assign={**w.assign, name: coerced},
                    amp=w.amp,
                    coord_phase=dict(w.coord_phase),
                )
                for w in self.worlds
            ]
        )

    def bind_pushforward(self, name: str, f: Callable[[dict[str, Any]], Any]) -> Joint:
        if self.is_vacuum():
            return Joint.empty()
        workers = current_world_workers()
        if workers <= 1 or len(self.worlds) < 2:
            return Joint(
                worlds=[
                    World(
                        assign={
                            **w.assign,
                            name: _coerce_joint_atom(f(w.assign)),
                        },
                        amp=w.amp,
                        coord_phase=dict(w.coord_phase),
                    )
                    for w in self.worlds
                ]
            )

        def _one(w: World) -> World:
            return World(
                assign={**w.assign, name: _coerce_joint_atom(f(w.assign))},
                amp=w.amp,
                coord_phase=dict(w.coord_phase),
            )

        with ThreadPoolExecutor(max_workers=workers) as pool:
            out = list(pool.map(_one, self.worlds))
        return Joint(worlds=out)

    def bind_multi(self, updates: dict[str, Callable[[dict[str, Any]], Any]]) -> Joint:
        if self.is_vacuum():
            return Joint.empty()
        workers = current_world_workers()

        def _one(w: World) -> World:
            new_a = dict(w.assign)
            computed = {
                k: _coerce_joint_atom(fn(w.assign)) for k, fn in updates.items()
            }
            new_a.update(computed)
            return World(assign=new_a, amp=w.amp, coord_phase=dict(w.coord_phase))

        if workers <= 1 or len(self.worlds) < 2:
            out = [_one(w) for w in self.worlds]
        else:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                out = list(pool.map(_one, self.worlds))
        return Joint(worlds=_coalesce(out))

    def bind_split(
        self, name: str, dist: dict[Any, float] | Callable[[dict[str, Any]], dict[Any, float]]
    ) -> Joint:
        """Split with probability weights p: new amp = parent_amp * √p."""
        if self.is_vacuum():
            return Joint.empty()
        out: list[World] = []
        for w in self.worlds:
            local = dist(w.assign) if callable(dist) else dist
            for val, p in local.items():
                if p <= EPS:
                    continue
                amp = w.amp * cmath.sqrt(p)
                if abs(amp) ** 2 > EPS:
                    out.append(
                        World(
                            assign={**w.assign, name: _coerce_joint_atom(val)},
                            amp=amp,
                            coord_phase=dict(w.coord_phase),
                        )
                    )
        return Joint(worlds=_coalesce(out))

    def project_coord(self, name: str, pred: Callable[[Any], bool]) -> Joint:
        kept = [
            World(
                assign=dict(w.assign),
                amp=w.amp,
                coord_phase=dict(w.coord_phase),
            )
            for w in self.worlds
            if name in w.assign and pred(w.assign[name])
        ]
        if not kept:
            return Joint.empty()
        return Joint(worlds=_coalesce(kept))

    def project_world(self, pred: Callable[[dict[str, Any]], bool]) -> Joint:
        kept = [
            World(
                assign=dict(w.assign),
                amp=w.amp,
                coord_phase=dict(w.coord_phase),
            )
            for w in self.worlds
            if pred(w.assign)
        ]
        if not kept:
            return Joint.empty()
        return Joint(worlds=_coalesce(kept))

    def map_coord(self, src: str, dest: str, f: Callable[[Any], Any]) -> Joint:
        if self.is_vacuum():
            return Joint.empty()
        return Joint(
            worlds=[
                World(
                    assign={**w.assign, dest: f(w.assign[src])},
                    amp=w.amp,
                    coord_phase=dict(w.coord_phase),
                )
                for w in self.worlds
                if src in w.assign
            ]
        )

    def rename_coord(self, src: str, dest: str) -> Joint:
        """Rename a live coordinate without tracing or changing amplitudes."""
        if src == dest or self.is_vacuum():
            return self
        if any(dest in w.assign for w in self.worlds):
            raise ValueError(f"cannot rename `{src}` to occupied coordinate `{dest}`")
        return Joint(
            worlds=[
                World(
                    assign={
                        (dest if key == src else key): value
                        for key, value in w.assign.items()
                    },
                    amp=w.amp,
                    coord_phase={
                        (dest if key == src else key): value
                        for key, value in w.coord_phase.items()
                    },
                )
                for w in self.worlds
                if src in w.assign
            ]
        )

    def trace_out(self, name: str) -> Joint:
        """Partial trace over coordinate `name` (Born sum → √p amplitudes).

        For each remaining assignment, mass = Σ |amp|² over traced values;
        the reduced state carries real amplitude √mass (diagonal of ρ).
        """
        if self.is_vacuum():
            return Joint.empty()
        masses: dict[tuple, float] = defaultdict(float)
        assign_of: dict[tuple, dict[str, Any]] = {}
        for w in self.worlds:
            assign = {k: v for k, v in w.assign.items() if k != name}
            key = tuple(sorted(assign.items()))
            masses[key] += abs(w.amp) ** 2
            assign_of[key] = assign
        out = [
            World(assign=assign_of[k], amp=complex(math.sqrt(m), 0.0))
            for k, m in masses.items()
            if m > EPS
        ]
        return Joint(worlds=out)

    def replace_coord(self, name: str, f: Callable[[Any], Any]) -> Joint:
        return self.map_coord(name, name, f)

    def scale_amp(self, factor: complex) -> Joint:
        if self.is_vacuum():
            return Joint.empty()
        return Joint(
            worlds=[
                World(
                    assign=dict(w.assign),
                    amp=w.amp * factor,
                    coord_phase=dict(w.coord_phase),
                )
                for w in self.worlds
            ]
        )

    def phase_copy(self, src: str, dest: str, theta: float, only: Any | None = None) -> Joint:
        """Copy src→dest; attach e^{iθ} as dest's coordinate phase.

        If `only` is set, apply the phase solely when src's value equals `only`
        (Grover-style oracle mark); other values keep phase 1.
        """
        factor = cmath.exp(1j * float(theta))
        if self.is_vacuum():
            return Joint.empty()
        out: list[World] = []
        for w in self.worlds:
            if src not in w.assign:
                continue
            ph = dict(w.coord_phase)
            src_ph = ph.get(src, 1.0 + 0.0j)
            val = w.assign[src]
            mark = only is None
            if not mark and val == only:
                mark = True
            elif (
                not mark
                and isinstance(val, (int, float))
                and isinstance(only, (int, float))
                and float(val) == float(only)
            ):
                mark = True
            if mark:
                ph[dest] = src_ph * factor
            else:
                ph[dest] = src_ph
            out.append(
                World(
                    assign={**w.assign, dest: val},
                    amp=w.amp,
                    coord_phase=ph,
                )
            )
        return Joint(worlds=_coalesce(out))

    def diffuse_copy(self, src: str, dest: str) -> Joint:
        """Grover diffusion on amplitude marginal: c ↦ 2μ − c, then renorm.

        ADR 0060: preserve unrelated `assign` keys. Diffusion acts on the
        marginal of `src`; within each value bucket, world amplitudes are
        rescaled proportionally so sibling wires / classical coords survive.
        """
        if self.is_vacuum():
            return Joint.empty()
        amps = self.amplitude_marginal(src)
        if not amps:
            return Joint.empty()
        mu = sum(amps.values()) / len(amps)
        flipped = {v: (2 * mu - c) for v, c in amps.items()}
        alive = {v: c for v, c in flipped.items() if abs(c) ** 2 > EPS}
        if not alive:
            return Joint.empty()
        total = sum(abs(c) ** 2 for c in alive.values())
        scale = 1.0 / cmath.sqrt(total)
        out: list[World] = []
        for w in self.worlds:
            if src not in w.assign:
                continue
            v = w.assign[src]
            if v not in alive:
                continue
            old_c = amps[v]
            if abs(old_c) <= EPS:
                continue
            new_amp = w.amp * ((alive[v] * scale) / old_c)
            if abs(new_amp) ** 2 <= EPS:
                continue
            assign = {**w.assign, dest: v}
            ph = dict(w.coord_phase)
            if src in ph and dest != src:
                ph[dest] = ph[src]
            out.append(World(assign=assign, amp=new_amp, coord_phase=ph))
        return Joint(worlds=_coalesce(out))


def _coalesce(worlds: Iterable[World]) -> list[World]:
    # Key: assignment + frozenset of coord phases (so phased copies don't falsely merge).
    acc: dict[tuple, complex] = defaultdict(complex)
    phase_of: dict[tuple, dict[str, complex]] = {}
    assign_of: dict[tuple, dict[str, Any]] = {}
    for w in worlds:
        phase_key = tuple(
            sorted((k, (v.real, v.imag)) for k, v in w.coord_phase.items())
        )
        key = (tuple(sorted(w.assign.items())), phase_key)
        acc[key] += w.amp
        phase_of[key] = dict(w.coord_phase)
        assign_of[key] = dict(w.assign)
    return [
        World(assign=assign_of[k], amp=a, coord_phase=phase_of[k])
        for k, a in acc.items()
        if abs(a) ** 2 > EPS
    ]


def sample_from_marginal(
    marginal: dict[Any, float],
    rng: Any,
) -> Any | None:
    items = [(v, m) for v, m in marginal.items() if m > EPS]
    if not items:
        return None
    total = sum(m for _, m in items)
    if total <= EPS:
        return None
    u = rng.random() * total
    acc = 0.0
    for v, m in items:
        acc += m
        if u <= acc:
            return v
    return items[-1][0]


def cis(theta: float) -> complex:
    """e^{iθ}."""
    return cmath.exp(1j * float(theta))
