"""SV-04: Early Collapse — mid-Measure rejected at compile gate."""

from __future__ import annotations

from pathlib import Path

from harness.assertions import AssertionFailure, assertCompileError
from harness.compile_gate import analyze_source
from harness.report import CaseResult

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def run() -> list[CaseResult]:
    out: list[CaseResult] = []

    bad = (FIXTURES / "early_collapse_bad.sqx").read_text(encoding="utf-8")
    try:
        diags = analyze_source(bad)
        assertCompileError(diags, "EARLY_COLLAPSE_ERROR")
        out.append(
            CaseResult(
                "SV-04",
                "sv04-early-collapse-bad",
                "mid-Measure → EARLY_COLLAPSE_ERROR",
                True,
                ["assertCompileError(EARLY_COLLAPSE_ERROR)"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-04",
                "sv04-early-collapse-bad",
                "mid-Measure → EARLY_COLLAPSE_ERROR",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    good = (FIXTURES / "early_collapse_ok.sqx").read_text(encoding="utf-8")
    try:
        diags = analyze_source(good)
        codes = [d["code"] for d in diags]
        if "EARLY_COLLAPSE_ERROR" in codes:
            raise AssertionFailure("EARLY_COLLAPSE_ERROR", "false positive on terminal Measure")
        out.append(
            CaseResult(
                "SV-04",
                "sv04-early-collapse-ok",
                "terminal Measure accepted",
                True,
                ["assertCompileError(absent)"],
            )
        )
    except AssertionFailure as e:
        out.append(
            CaseResult(
                "SV-04",
                "sv04-early-collapse-ok",
                "terminal Measure accepted",
                False,
                error_code=e.code,
                message=str(e),
            )
        )

    return out
