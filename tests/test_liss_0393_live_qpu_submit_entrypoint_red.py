"""AT-TDD Phase 1 Red: LISS-0393 submit_live_qpu Host entrypoint.

Target: docs/architecture/adr/0203-live-qpu-submit-entrypoint.md /
LISS-0393.

All tests exercise a fake QpuSubmitPort. No real network call, no real
credentials, no real provider SDK import anywhere in this file (ADR 0202
Decision 5 / ADR 0203, standing constraint).
"""

from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.qpu_submit import ProviderJobId, QpuSubmitRequest  # noqa: E402


_SOURCE_STATIC = """
package t
pub fn main() -> Unit {
    QubitRegister<1> reg = system()
    forEach q in reg {
        apply(H, q)
    }
    State<Int> observed = coin()
    measure observed
}
"""

_SOURCE_DYNAMIC = """
package t
pub fn main() -> Unit {
    dynamic qpu {
        state q = |0>
        Controller<Bit> bit = measure q
        reset q
    }
    State<Int> observed = coin()
    measure observed
}
"""

_SOURCE_INVALID = """
package t
pub fn main() -> Unit {
    this is not valid staqex source ###
}
"""


class FakeQpuSubmitPort:
    """Records the request it received; returns a deterministic id."""

    def __init__(self) -> None:
        self.received: QpuSubmitRequest | None = None

    def submit(self, request: QpuSubmitRequest) -> ProviderJobId:
        self.received = request
        return ProviderJobId(provider="fake", opaque_id="fake-job-1")


def test_static_source_emits_static_qasm_and_submits() -> None:
    from compiler.staqex.live_submit import submit_live_qpu

    adapter = FakeQpuSubmitPort()
    job_id, diagnostics = submit_live_qpu(_SOURCE_STATIC, adapter=adapter)

    assert diagnostics == ()
    assert job_id == ProviderJobId(provider="fake", opaque_id="fake-job-1")
    assert adapter.received is not None
    assert "OPENQASM 3" in adapter.received.artifact.qasm
    assert "h q" in adapter.received.artifact.qasm.lower()


def test_dynamic_source_emits_dynamic_qasm_and_submits() -> None:
    from compiler.staqex.live_submit import submit_live_qpu

    adapter = FakeQpuSubmitPort()
    job_id, diagnostics = submit_live_qpu(_SOURCE_DYNAMIC, adapter=adapter)

    assert diagnostics == ()
    assert job_id is not None
    assert adapter.received is not None
    qasm = adapter.received.artifact.qasm
    assert "bit = measure q;" in qasm
    assert "reset q;" in qasm


def test_returns_provider_job_id_not_a_job_result() -> None:
    from compiler.staqex.live_submit import submit_live_qpu

    adapter = FakeQpuSubmitPort()
    job_id, _ = submit_live_qpu(_SOURCE_STATIC, adapter=adapter)

    assert type(job_id).__name__ == "ProviderJobId"
    assert not hasattr(job_id, "measurements")
    assert not hasattr(job_id, "status")


def test_compile_failure_returns_none_and_diagnostics_not_an_exception() -> None:
    from compiler.staqex.live_submit import submit_live_qpu

    adapter = FakeQpuSubmitPort()
    job_id, diagnostics = submit_live_qpu(_SOURCE_INVALID, adapter=adapter)

    assert job_id is None
    assert len(diagnostics) > 0
    assert adapter.received is None


def test_content_hash_is_deterministic_sha256_of_qasm() -> None:
    import hashlib

    from compiler.staqex.live_submit import submit_live_qpu

    adapter = FakeQpuSubmitPort()
    submit_live_qpu(_SOURCE_STATIC, adapter=adapter)

    assert adapter.received is not None
    expected = hashlib.sha256(adapter.received.artifact.qasm.encode()).hexdigest()
    assert adapter.received.artifact.content_hash == expected


def test_submit_source_is_unaffected() -> None:
    """Regression guard: submit_source stays local-only, unchanged (ADR 0203
    Decision 1) -- not a new assertion, confirms this Issue touched nothing
    there.
    """
    from compiler.staqex.host import submit_source

    job = submit_source(_SOURCE_STATIC, settings={})
    assert job.id.startswith("local-")
