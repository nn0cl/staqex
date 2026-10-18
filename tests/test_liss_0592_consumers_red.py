"""R05 unchanged statuses and ordered diagnostics from actual consumers."""

import hashlib
import json

import pytest

from tests import liss_0592_guard_support as guard
from tests.liss_0592_consumer_support import CASES, METADATA, PROGRAMS, snapshot


def baseline():
    data = (guard.FIXTURES / "consumer-baseline.json").read_bytes()
    assert hashlib.sha256(data).hexdigest() == "180fb8c72fabd8f20ee54efbe1c9940ce29fd28abb9edb7496cdd9011b5738ae"
    evidence = json.loads(data)
    assert evidence["source_base"] == guard.baseline()["base"]
    assert evidence["parser_sha256"] == guard.baseline()["parser_sha256"]
    assert evidence["programs"] == PROGRAMS and evidence["metadata"] == METADATA
    return evidence["observations"]


@pytest.mark.parametrize("kind,name", CASES)
def test_r05_real_consumer_status_and_exact_ordered_diagnostics(tmp_path, kind, name):
    assert snapshot(kind, name, tmp_path) == baseline()[f"{kind}/{name}"]


def test_r05_modified_consumer_evidence_is_rejected(tmp_path, monkeypatch):
    target = tmp_path / "consumer-baseline.json"
    target.write_bytes((guard.FIXTURES / target.name).read_bytes() + b"\n")
    monkeypatch.setattr(guard, "FIXTURES", tmp_path)
    with pytest.raises(AssertionError):
        baseline()
