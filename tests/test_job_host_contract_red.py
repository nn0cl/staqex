"""AT-TDD Phase 1 Red: LISS-0022 / ADR-0065 Job host boundary."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


SOURCE = """
pub fn main() -> Unit {
    State<Int> answer = Dirac(42)
    Measure answer
}
"""


class JobHostContractRedTests(unittest.TestCase):
    def test_submit_returns_provider_neutral_job(self) -> None:
        from compiler.staqex.host import submit_source

        job = submit_source(SOURCE, settings={"target": "local"})

        self.assertTrue(job.id)
        self.assertIn(job.status(), {"queued", "running", "succeeded"})


    def test_result_is_available_only_after_terminal_measurement(self) -> None:
        from compiler.staqex.host import submit_source

        job = submit_source(SOURCE, settings={"target": "local"})
        result = job.result()

        self.assertEqual(result.status, "succeeded")
        self.assertTrue(result.measurements)
        self.assertFalse(hasattr(result, "joint"))
        self.assertFalse(hasattr(result, "ast"))


    def test_run_is_blocking_job_convenience_api(self) -> None:
        from compiler.staqex.host import run_source

        result = run_source(SOURCE, settings={"target": "local"})

        self.assertEqual(result.status, "succeeded")
        self.assertTrue(result.measurements)


    def test_failed_job_is_structured_without_provider_sdk(self) -> None:
        from compiler.staqex.host import submit_source

        job = submit_source("not valid Staqex", settings={"target": "local"})
        result = job.result()

        self.assertEqual(result.status, "failed")
        self.assertTrue(result.diagnostics)


    def test_cancel_is_part_of_the_provider_neutral_contract(self) -> None:
        from compiler.staqex.host import submit_source

        job = submit_source(SOURCE, settings={"target": "local"})

        self.assertIn(job.cancel(), {"accepted", "already-complete", "unsupported"})


if __name__ == "__main__":
    unittest.main()
