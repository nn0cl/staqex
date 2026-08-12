"""Discrete PMF State for Staqex Spec Verification PoC."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, Generic, Hashable, Iterable, TypeVar

T = TypeVar("T", bound=Hashable)
U = TypeVar("U", bound=Hashable)

EPS = 1e-12


@dataclass(frozen=True, slots=True)
class ResultOk(Generic[T]):
    value: T

    def tag(self) -> str:
        return "Ok"


@dataclass(frozen=True, slots=True)
class ResultErr(Generic[T]):
    error: T

    def tag(self) -> str:
        return "Err"


class State(Generic[T]):
    """Finite discrete probability mass function over hashable values.

    Never exposes a bare classical scalar as the public result of ops:
    every public method returns State[...] or a MeasureOutcome.
    """

    __slots__ = ("_mass", "_payload_type")

    def __init__(
        self,
        support: dict[T, float] | None = None,
        *,
        payload_type: type | str = "Any",
    ) -> None:
        self._mass: dict[T, float] = {}
        if support:
            for k, m in support.items():
                if m < 0:
                    raise ValueError("negative mass")
                if m > EPS:
                    self._mass[k] = float(m)
        self._payload_type = payload_type

    @staticmethod
    def dirac(value: T, *, payload_type: type | str | None = None) -> State[T]:
        pt = payload_type if payload_type is not None else type(value)
        return State({value: 1.0}, payload_type=pt)

    @staticmethod
    def vacuum(*, payload_type: type | str = "Any") -> State[T]:
        return State({}, payload_type=payload_type)

    @staticmethod
    def coin() -> State[int]:
        return State({0: 0.5, 1: 0.5}, payload_type=int)

    @property
    def payload_type(self) -> type | str:
        return self._payload_type

    def support(self) -> dict[T, float]:
        return dict(self._mass)

    def norm(self) -> float:
        return float(sum(self._mass.values()))

    def is_vacuum(self) -> bool:
        return abs(self.norm()) <= EPS and len(self._mass) == 0

    def map(self, f: Callable[[T], U], *, payload_type: type | str | None = None) -> State[U]:
        if self.is_vacuum():
            pt = payload_type if payload_type is not None else self._payload_type
            return State.vacuum(payload_type=pt)  # type: ignore[return-value]
        acc: dict[U, float] = defaultdict(float)
        for v, m in self._mass.items():
            acc[f(v)] += m
        pt = payload_type if payload_type is not None else self._payload_type
        return State(dict(acc), payload_type=pt)

    def project(self, pred: Callable[[T], bool]) -> State[T]:
        """Keep worlds where pred holds. All rejected → Vacuum (no exception)."""
        kept = {v: m for v, m in self._mass.items() if pred(v)}
        if not kept:
            return State.vacuum(payload_type=self._payload_type)
        # renormalize surviving mass to preserve MVP "conditional" style for non-empty
        # ADR 0034 vacuum path: empty only. Non-empty project keeps absolute mass
        # for Spec SV-05 vacuum case (full reject). For partial project, keep masses
        # as absolute (norm may drop) — language may later renormalize; protocol
        # SV-05 only requires full-reject → vacuum.
        return State(kept, payload_type=self._payload_type)

    def when(
        self,
        arms: dict[Any, Callable[[], State[U]]] | Iterable[tuple[Any, Callable[[], State[U]]]],
        *,
        else_arm: Callable[[], State[U]] | None = None,
        payload_type: type | str | None = None,
    ) -> State[U]:
        """Non-destructive branch: Mix arm states weighted by matching mass."""
        arm_list = list(arms.items()) if isinstance(arms, dict) else list(arms)
        acc: dict[U, float] = defaultdict(float)
        matched_mass = 0.0
        for key, thunk in arm_list:
            w = self._mass.get(key, 0.0)
            if w <= EPS:
                continue
            matched_mass += w
            branch = thunk()
            for bv, bm in branch.support().items():
                acc[bv] += w * bm
        else_mass = self.norm() - matched_mass
        if else_arm is not None and else_mass > EPS:
            branch = else_arm()
            for bv, bm in branch.support().items():
                acc[bv] += else_mass * bm
        pt = payload_type if payload_type is not None else "Any"
        if not acc:
            return State.vacuum(payload_type=pt)
        return State(dict(acc), payload_type=pt)

    def __add__(self, other: State[T] | T) -> State[Any]:
        return self._binop(other, lambda a, b: a + b)  # type: ignore[operator]

    def __sub__(self, other: State[T] | T) -> State[Any]:
        return self._binop(other, lambda a, b: a - b)  # type: ignore[operator]

    def __mul__(self, other: State[T] | T) -> State[Any]:
        return self._binop(other, lambda a, b: a * b)  # type: ignore[operator]

    def __truediv__(self, other: State[T] | T) -> State[ResultOk[Any] | ResultErr[str]]:
        """Division as Result superposition — never raises ZeroDivisionError."""
        rhs = _as_state(other)
        acc: dict[ResultOk[Any] | ResultErr[str], float] = defaultdict(float)
        for a, ma in self._mass.items():
            for b, mb in rhs.support().items():
                w = ma * mb
                if b == 0 or b == 0.0:
                    acc[ResultErr("DivByZero")] += w
                else:
                    acc[ResultOk(a / b)] += w  # type: ignore[operator]
        return State(dict(acc), payload_type="Result")

    def __ge__(self, other: State[T] | T) -> State[bool]:
        return self._cmp(other, lambda a, b: a >= b)  # type: ignore[operator]

    def __gt__(self, other: State[T] | T) -> State[bool]:
        return self._cmp(other, lambda a, b: a > b)  # type: ignore[operator]

    def __le__(self, other: State[T] | T) -> State[bool]:
        return self._cmp(other, lambda a, b: a <= b)  # type: ignore[operator]

    def __lt__(self, other: State[T] | T) -> State[bool]:
        return self._cmp(other, lambda a, b: a < b)  # type: ignore[operator]

    def __eq__(self, other: object) -> bool:  # identity for Python; use cmp_eq for State[bool]
        return object.__eq__(self, other)

    def cmp_eq(self, other: State[T] | T) -> State[bool]:
        return self._cmp(other, lambda a, b: a == b)

    def _binop(self, other: State[T] | T, op: Callable[[Any, Any], Any]) -> State[Any]:
        rhs = _as_state(other)
        acc: dict[Any, float] = defaultdict(float)
        for a, ma in self._mass.items():
            for b, mb in rhs.support().items():
                acc[op(a, b)] += ma * mb
        return State(dict(acc), payload_type=self._payload_type)

    def _cmp(self, other: State[T] | T, op: Callable[[Any, Any], bool]) -> State[bool]:
        rhs = _as_state(other)
        acc: dict[bool, float] = defaultdict(float)
        for a, ma in self._mass.items():
            for b, mb in rhs.support().items():
                acc[op(a, b)] += ma * mb
        return State(dict(acc), payload_type=bool)

    def measure(self) -> MeasureOutcome:
        """Terminal collapse simulation: return support snapshot (no RNG required for specs)."""
        return MeasureOutcome(dict(self._mass), self.norm(), self.is_vacuum())


@dataclass(frozen=True, slots=True)
class MeasureOutcome:
    support: dict[Any, float]
    norm: float
    is_vacuum: bool


def _as_state(x: State[Any] | Any) -> State[Any]:
    if isinstance(x, State):
        return x
    return State.dirac(x)


def lift(value: Any) -> State[Any]:
    """Lit-Lift: classical literal → State (Dirac)."""
    return State.dirac(value)
