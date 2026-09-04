"""Canonical evaluator helper for specification-verification suites."""

from __future__ import annotations

import io
from pathlib import Path
import sys
from typing import Any, TextIO

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from compiler.staqex.runtime.evaluator import Evaluator


def run_canonical(compiled: Any, evaluator: Evaluator, *, stdout: TextIO | None = None):
    """Execute the unit and its compile-owned semantic IR as one snapshot."""

    if compiled.unit is None or compiled.scientific_semantic_ir is None:
        raise AssertionError("canonical semantic IR is required for execution")
    return evaluator.run_canonical_unit(
        compiled.unit,
        semantic_ir=compiled.scientific_semantic_ir,
        stdout=stdout if stdout is not None else io.StringIO(),
    )
