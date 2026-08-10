"""AT-TDD Phase 1 Red: LISS-0397 `QpuJobPort` CLI surface
(`qpu-job-status`/`-wait`/`-result`/`-cancel`).

Target: docs/issues/LISS-0397-qpu-job-port-cli.md.
"""

from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from compiler.staqex.cli import main  # noqa: E402


_DEVICE_ARN = "arn:aws:braket::device/fake"
_JOB_ID = "fake-task-arn"


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


class _FakeBraketClient:
    def __init__(self) -> None:
        self.task_state_calls: list[str] = []
        self.task_result_calls: list[str] = []
        self.cancel_task_calls: list[str] = []

    def create_task(self, qasm: str, device_arn: str, shots: int) -> str:
        raise AssertionError("create_task should not be called by job-port commands")

    def task_state(self, task_arn: str) -> str:
        self.task_state_calls.append(task_arn)
        return "COMPLETED"

    def task_result(self, task_arn: str):
        self.task_result_calls.append(task_arn)
        return {"measurements": [[0, 1], [1, 0]]}

    def cancel_task(self, task_arn: str) -> None:
        self.cancel_task_calls.append(task_arn)


_ENV = {"AWS_ACCESS_KEY_ID": "fake-key", "AWS_SECRET_ACCESS_KEY": "fake-secret"}


def test_missing_braket_sdk_fails_closed_for_real_on_status() -> None:
    """This dev/CI environment lacks amazon-braket-sdk (confirmed in the
    LISS-0396/0397 Plans). No mocking: exercises the real
    RealAwsBraketClient version gate for a job-status command.
    """
    code, stdout, stderr = _run_cli(
        ["qpu-job-status", "--id", _JOB_ID, "--device-arn", _DEVICE_ARN]
    )
    assert code == 1
    assert stdout == ""
    assert "amazon-braket-sdk" in stderr


def test_unsupported_provider_fails_closed_on_status() -> None:
    code, stdout, stderr = _run_cli(
        [
            "qpu-job-status",
            "--id",
            _JOB_ID,
            "--device-arn",
            _DEVICE_ARN,
            "--provider",
            "ibm-quantum",
        ]
    )
    assert code == 1
    assert stdout == ""
    assert "ibm-quantum" in stderr


def test_status_prints_provider_job_state() -> None:
    fake_client = _FakeBraketClient()
    with patch("compiler.staqex.cli.RealAwsBraketClient", return_value=fake_client), \
         patch.dict("os.environ", _ENV, clear=False):
        code, stdout, stderr = _run_cli(
            ["qpu-job-status", "--id", _JOB_ID, "--device-arn", _DEVICE_ARN]
        )
    assert code == 0, stderr
    assert stdout.strip() == "succeeded"
    assert fake_client.task_state_calls == [_JOB_ID]


def test_wait_prints_provider_job_state() -> None:
    fake_client = _FakeBraketClient()
    with patch("compiler.staqex.cli.RealAwsBraketClient", return_value=fake_client), \
         patch.dict("os.environ", _ENV, clear=False):
        code, stdout, stderr = _run_cli(
            ["qpu-job-wait", "--id", _JOB_ID, "--device-arn", _DEVICE_ARN]
        )
    assert code == 0, stderr
    assert stdout.strip() == "succeeded"


def test_cancel_calls_cancel_task_and_prints_resulting_state() -> None:
    fake_client = _FakeBraketClient()
    with patch("compiler.staqex.cli.RealAwsBraketClient", return_value=fake_client), \
         patch.dict("os.environ", _ENV, clear=False):
        code, stdout, stderr = _run_cli(
            ["qpu-job-cancel", "--id", _JOB_ID, "--device-arn", _DEVICE_ARN]
        )
    assert code == 0, stderr
    assert stdout.strip() == "succeeded"
    assert fake_client.cancel_task_calls == [_JOB_ID]


def test_result_prints_json_serialized_mapping() -> None:
    fake_client = _FakeBraketClient()
    with patch("compiler.staqex.cli.RealAwsBraketClient", return_value=fake_client), \
         patch.dict("os.environ", _ENV, clear=False):
        code, stdout, stderr = _run_cli(
            ["qpu-job-result", "--id", _JOB_ID, "--device-arn", _DEVICE_ARN]
        )
    assert code == 0, stderr
    assert json.loads(stdout) == {"measurements": [[0, 1], [1, 0]]}
    assert fake_client.task_result_calls == [_JOB_ID]


def test_status_unaffected_by_missing_credentials() -> None:
    """AwsBraketAdapter._require_credentials() only runs inside `submit()`
    (adapters/aws_braket.py:152-166) -- status/wait/result/cancel never
    call it, by already-shipped design (LISS-0392), unchanged by this
    Issue. Discovered while running Red: the Plan's Design verification
    did not check this specific asymmetry before drafting the original
    (wrong) "fails closed on missing credentials" expectation for a
    job-status command; corrected before any Green code changed to
    accommodate it -- the shared `_cmd_qpu_job` dispatcher needed no
    credential-specific branch at all, since it simply calls through to
    whatever the adapter does.
    """
    fake_client = _FakeBraketClient()
    with patch("compiler.staqex.cli.RealAwsBraketClient", return_value=fake_client), \
         patch.dict("os.environ", {}, clear=True):
        code, stdout, stderr = _run_cli(
            ["qpu-job-status", "--id", _JOB_ID, "--device-arn", _DEVICE_ARN]
        )
    assert code == 0, stderr
    assert stdout.strip() == "succeeded"
    assert fake_client.task_state_calls == [_JOB_ID]
