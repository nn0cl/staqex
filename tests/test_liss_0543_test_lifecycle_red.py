"""Phase 1 Red contracts for explicit active-Red test lifecycle authority."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import textwrap


REPOSITORY = Path(__file__).resolve().parents[1]
CHECKER = REPOSITORY / "scripts" / "check-test-lifecycle.py"


def _issue(status: str = "phase-1-red", phase: str = "phase-1-red") -> str:
    return textwrap.dedent(
        f"""\
        # LISS-0600: fixture issue

        | Field | Value |
        |---|---|
        | Status | {status} |
        | Phase | {phase} |
        """
    )


def _entry(
    *,
    issue: str = "LISS-0600",
    test: str = "tests/test_future_red.py",
    review_by: str = "2026-10-01",
) -> str:
    return textwrap.dedent(
        f"""\
        [[active_red]]
        issue = "{issue}"
        test = "{test}"
        phase = "phase-1-red"
        owner = "fixture-owner"
        review_by = "{review_by}"
        review_condition = "Phase 2 Green approval"
        """
    )


def _repository_fixture(
    tmp_path: Path,
    *,
    issue_text: str | None = None,
    manifest_entries: str | None = None,
    create_test: bool = True,
    ci_command: str = "python3 -m pytest tests/ -q",
) -> Path:
    root = tmp_path / "repository"
    (root / "docs" / "issues").mkdir(parents=True)
    (root / "docs" / "testing").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / ".github" / "workflows").mkdir(parents=True)
    if issue_text is not None:
        (root / "docs" / "issues" / "LISS-0600-fixture.md").write_text(
            issue_text, encoding="utf-8"
        )
    if create_test:
        (root / "tests" / "test_future_red.py").write_text(
            "def test_future():\n    assert False\n", encoding="utf-8"
        )
    manifest = "version = 1\n\n" + (manifest_entries or _entry())
    (root / "docs" / "testing" / "active-red-tests.toml").write_text(
        manifest, encoding="utf-8"
    )
    (root / ".github" / "workflows" / "ci.yml").write_text(
        f"jobs:\n  tests:\n    steps:\n      - run: {ci_command}\n", encoding="utf-8"
    )
    return root


def _run_checker(root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--root",
            str(root),
            "--as-of",
            "2026-09-11",
            *extra,
        ],
        text=True,
        capture_output=True,
        check=False,
    )


def _assert_rejected(result: subprocess.CompletedProcess[str], code: str) -> None:
    assert result.returncode == 1, result.stdout + result.stderr
    assert code in result.stdout, result.stdout + result.stderr


def test_active_red_entry_for_open_phase_is_valid(tmp_path: Path) -> None:
    root = _repository_fixture(tmp_path, issue_text=_issue())

    result = _run_checker(root)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ACTIVE_RED_LIFECYCLE_OK" in result.stdout


def test_done_issue_cannot_remain_excluded(tmp_path: Path) -> None:
    root = _repository_fixture(
        tmp_path, issue_text=_issue(status="done", phase="done")
    )

    _assert_rejected(_run_checker(root), "ACTIVE_RED_ISSUE_DONE")


def test_unknown_issue_is_rejected(tmp_path: Path) -> None:
    root = _repository_fixture(tmp_path, issue_text=None)

    _assert_rejected(_run_checker(root), "ACTIVE_RED_ISSUE_UNKNOWN")


def test_missing_test_file_is_rejected(tmp_path: Path) -> None:
    root = _repository_fixture(tmp_path, issue_text=_issue(), create_test=False)

    _assert_rejected(_run_checker(root), "ACTIVE_RED_TEST_MISSING")


def test_duplicate_test_registration_is_rejected(tmp_path: Path) -> None:
    root = _repository_fixture(
        tmp_path,
        issue_text=_issue(),
        manifest_entries=_entry() + "\n" + _entry(),
    )

    _assert_rejected(_run_checker(root), "ACTIVE_RED_DUPLICATE")


def test_expired_review_date_is_rejected_deterministically(tmp_path: Path) -> None:
    root = _repository_fixture(
        tmp_path,
        issue_text=_issue(),
        manifest_entries=_entry(review_by="2026-09-10"),
    )

    _assert_rejected(_run_checker(root), "ACTIVE_RED_REVIEW_EXPIRED")


def test_global_red_filename_exclusion_is_rejected(tmp_path: Path) -> None:
    root = _repository_fixture(
        tmp_path,
        issue_text=_issue(),
        ci_command="python3 -m pytest tests/ -q --ignore-glob='*_red.py'",
    )

    _assert_rejected(_run_checker(root), "ACTIVE_RED_GLOBAL_GLOB")


def test_checker_emits_validated_per_file_pytest_arguments(tmp_path: Path) -> None:
    root = _repository_fixture(tmp_path, issue_text=_issue())

    result = _run_checker(root, "--pytest-ignore-args")

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip() == "--ignore=tests/test_future_red.py"
