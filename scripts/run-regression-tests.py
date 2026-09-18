#!/usr/bin/env python3
"""Run template regressions and emit scoped verification evidence in stdout."""
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
import unittest


def git(root, *args):
    result = subprocess.run(['git', *args], cwd=root, text=True, capture_output=True)
    return result.stdout.strip() if result.returncode == 0 else None


def main():
    root = Path(__file__).resolve().parents[1]
    start = datetime.now(timezone.utc).isoformat()
    suite = unittest.defaultTestLoader.discover(str(root/'scripts/tests'))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps(dict(
        scope='template-regression (not all-blocking)',
        status='passed' if result.wasSuccessful() else 'failed',
        sha=git(root, 'rev-parse', 'HEAD'),
        dirty_state=git(root, 'status', '--porcelain'),
        command=[sys.executable, *sys.argv], cwd=str(Path.cwd()),
        environment=dict(os=platform.platform(), python=platform.python_version()),
        started_at=start, ended_at=datetime.now(timezone.utc).isoformat(),
        total=result.testsRun, failures=len(result.failures), errors=len(result.errors),
        skipped=len(result.skipped),
        failure_ids=[test.id() for test, _ in result.failures + result.errors],
        baseline_comparison='not performed by this runner',
        exit_code=0 if result.wasSuccessful() else 1), indent=2))
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
