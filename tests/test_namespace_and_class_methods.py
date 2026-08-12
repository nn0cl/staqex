"""AT-TDD: ADR 0055 namespace + ADR 0056 class methods / this."""

from __future__ import annotations

import io
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.ast_nodes import ClassDecl, FunDecl  # noqa: E402
from compiler.staqex.pipeline import compile_source  # noqa: E402
from compiler.staqex.run import run_source  # noqa: E402


SRC = """
package com.staqex.test.ns_oop

namespace Topology {
  class ChainLattice {
    Float num_cells = 10.0
    Length lattice_constant = 0.5.nm

    pub fn total_sites() -> Float {
      Float total = this.num_cells * 2.0
      return total
    }

    pub fn doubled_cells() -> Float {
      Float d = this.num_cells + this.num_cells
      return d
    }
  }
}

namespace Physics.Parameters {
  class SSHParameters {
    Float v_intra = 0.5
    Float w_inter = 1.5

    pub fn topological_index() -> Float {
      Float winding = 1.0
      return winding
    }

    pub fn band_gap() -> Float {
      Float gap = this.w_inter - this.v_intra
      Float gap2 = gap + gap
      return gap2
    }
  }
}

pub fn main() -> Unit {
  Topology.ChainLattice lat = Topology.ChainLattice()
  Physics.Parameters.SSHParameters params = Physics.Parameters.SSHParameters()

  Float sites = lat.total_sites()
  Float wind = params.topological_index()
  Float gap = params.band_gap()

  State viewed = inspect(sites)
  measure sites
}
"""


def test_namespace_class_methods_compile_and_run() -> None:
    compiled = compile_source(SRC)
    hard = [
        d
        for d in compiled.diagnostics
        if d.get("code")
        in {
            "PARSE_ERROR",
            "LEX_ERROR",
            "TYPE_NOT_STATE",
            "DIMENSION_MISMATCH_ERROR",
            "FORBIDDEN_KEYWORD",
        }
    ]
    assert not hard, hard
    assert compiled.unit is not None

    classes = {
        d.qualified_name: d for d in compiled.unit.decls if isinstance(d, ClassDecl)
    }
    assert "Topology.ChainLattice" in classes
    assert "Physics.Parameters.SSHParameters" in classes
    lat = classes["Topology.ChainLattice"]
    assert any(f.names == ["num_cells"] for f in lat.fields)
    assert any(m.name == "total_sites" for m in lat.methods)

    buf = io.StringIO()
    result = run_source(SRC, seed=0, stdout=buf)
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 20.0


def test_this_field_and_method_return() -> None:
    src = """
package t
namespace N {
  class Box {
    Float x = 3.0
    pub fn sq() -> Float {
      Float y = this.x * this.x
      return y
    }
  }
}
pub fn main() -> Unit {
  N.Box b = N.Box()
  Float y = b.sq()
  measure y
}
"""
    result = run_source(src, seed=0, stdout=io.StringIO())
    assert result.compile_ok, result.diagnostics
    assert result.eval.measure is not None
    assert result.eval.measure.value == 9.0


if __name__ == "__main__":
    test_namespace_class_methods_compile_and_run()
    test_this_field_and_method_return()
    print("OK — namespace + class methods")
