"""AT-TDD: LISS-0114 Slice C — R2 strict alias policy lock (design gate)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.pipeline import compile_source


def _codes(diags: list[dict]) -> set[str]:
    return {str(d.get("code", "")) for d in diags}


def test_linear_alias_policy_is_strict() -> None:
    """R2 locked: LINEAR_ALIAS_POLICY must remain strict (no rename)."""
    from compiler.staqex import hir as hir_mod

    assert getattr(hir_mod, "LINEAR_ALIAS_POLICY", None) == "strict"


def test_alias_rebinding_still_rejected_under_strict_policy() -> None:
    compiled = compile_source(
        """
        package t
        pub fn main() -> Unit {
            State<Int> q = Coin()
            State<Int> alias = q
            Measure alias
        }
        """
    )
    assert "LINEAR_DUPLICATE_USE" in _codes(compiled.diagnostics)
    assert compiled.ok is False


def main() -> None:
    test_linear_alias_policy_is_strict()
    print("PASS test_linear_alias_policy_is_strict")
    test_alias_rebinding_still_rejected_under_strict_policy()
    print("PASS test_alias_rebinding_still_rejected_under_strict_policy")
    print("OK - LISS-0114 Slice C design gate")


if __name__ == "__main__":
    main()
