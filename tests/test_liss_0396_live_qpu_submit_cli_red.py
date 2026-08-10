"""AT-TDD Phase 1 Red: LISS-0396 `staqex submit-live-qpu` CLI surface.

Target: docs/architecture/adr/0203-live-qpu-submit-entrypoint.md (named
CLI follow-up) / docs/issues/LISS-0396-live-qpu-submit-cli.md.
"""

from __future__ import annotations

import io
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.cli import main  # noqa: E402


_SOURCE_OK = """
package t
pub fn main() -> Unit {
    state q = |0>
    measure q
}
"""

_SOURCE_HARD_DIAGNOSTIC = "package t\npub fn main() -> Unit {\n"


def _run_cli(argv: list[str]) -> tuple[int, str, str]:
    out = io.StringIO()
    err = io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as exc:
            raw = exc.code
            code = 0 if raw is None else (raw if isinstance(raw, int) else 1)
    return int(code), out.getvalue(), err.getvalue()


def test_unsupported_provider_fails_closed() -> None:
    code, stdout, stderr = _run_cli(
        [
            "submit-live-qpu",
            "-e",
            _SOURCE_OK,
            "--device-arn",
            "arn:aws:braket::device/fake",
            "--provider",
            "ibm-quantum",
        ]
    )
    assert code == 1
    assert "provider=" not in stdout
    assert "ibm-quantum" in stderr


def test_missing_braket_sdk_fails_closed_for_real() -> None:
    """This dev/CI environment does not have amazon-braket-sdk installed
    (confirmed in the LISS-0396 Plan). No mocking: this exercises the real
    `RealAwsBraketClient.__init__` version gate, proving the CLI fails
    closed rather than crashing or silently proceeding.
    """
    code, stdout, stderr = _run_cli(
        [
            "submit-live-qpu",
            "-e",
            _SOURCE_OK,
            "--device-arn",
            "arn:aws:braket::device/fake",
        ]
    )
    assert code == 1
    assert "provider=" not in stdout
    assert "amazon-braket-sdk" in stderr


class _FakeBraketClient:
    def __init__(self) -> None:
        self.create_task_calls: list[tuple[str, str, int]] = []

    def create_task(self, qasm: str, device_arn: str, shots: int) -> str:
        self.create_task_calls.append((qasm, device_arn, shots))
        return "fake-task-arn"

    def task_state(self, task_arn: str) -> str:
        return "COMPLETED"

    def task_result(self, task_arn: str):
        return {"measurements": []}

    def cancel_task(self, task_arn: str) -> None:
        pass


def test_successful_submission_prints_provider_job_id() -> None:
    fake_client = _FakeBraketClient()
    env = {"AWS_ACCESS_KEY_ID": "fake-key", "AWS_SECRET_ACCESS_KEY": "fake-secret"}
    with patch("compiler.staqex.cli.RealAwsBraketClient", return_value=fake_client), \
         patch.dict("os.environ", env, clear=False):
        code, stdout, stderr = _run_cli(
            [
                "submit-live-qpu",
                "-e",
                _SOURCE_OK,
                "--device-arn",
                "arn:aws:braket::device/fake",
            ]
        )
    assert code == 0, stderr
    assert stdout.strip() == "provider=aws-braket id=fake-task-arn"
    assert len(fake_client.create_task_calls) == 1


def test_missing_credentials_fails_closed_before_submit() -> None:
    fake_client = _FakeBraketClient()
    with patch("compiler.staqex.cli.RealAwsBraketClient", return_value=fake_client), \
         patch.dict("os.environ", {}, clear=True):
        code, stdout, stderr = _run_cli(
            [
                "submit-live-qpu",
                "-e",
                _SOURCE_OK,
                "--device-arn",
                "arn:aws:braket::device/fake",
            ]
        )
    assert code == 1
    assert "provider=" not in stdout
    assert "credentials" in stderr.lower()
    assert fake_client.create_task_calls == []


def test_hard_compile_diagnostic_prints_diagnostics_not_provider() -> None:
    fake_client = _FakeBraketClient()
    env = {"AWS_ACCESS_KEY_ID": "fake-key", "AWS_SECRET_ACCESS_KEY": "fake-secret"}
    with patch("compiler.staqex.cli.RealAwsBraketClient", return_value=fake_client), \
         patch.dict("os.environ", env, clear=False):
        code, stdout, stderr = _run_cli(
            [
                "submit-live-qpu",
                "-e",
                _SOURCE_HARD_DIAGNOSTIC,
                "--device-arn",
                "arn:aws:braket::device/fake",
            ]
        )
    assert code == 1
    assert "provider=" not in stdout
    assert fake_client.create_task_calls == []
