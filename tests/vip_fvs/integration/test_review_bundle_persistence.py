"""RED persistence/readback contract for ReviewBundle."""
from __future__ import annotations

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import pytest

from tests.vip_fvs.unit.test_review_bundle import payload_with_e01_artifact
from vip_fvs.review_bundle import (ReviewBundle, _dependency_projection,
                                   _sha, load_review_bundle, record_digest,
                                   save_review_bundle)


def test_atomic_save_and_fresh_process_readback_preserve_digest_and_status(tmp_path: Path):
    bundle = ReviewBundle.create(payload_with_e01_artifact(tmp_path), run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z")
    path = save_review_bundle(bundle, tmp_path / "review-bundle.json")
    loaded = load_review_bundle(path)
    assert loaded.record_digest == bundle.record_digest
    assert loaded.dependency_digest == bundle.dependency_digest
    assert loaded.to_record()["payload"]["review_status"] == "AWAITING_EDITORIAL_DECISION"
    code = "import json,sys; r=json.load(open(sys.argv[1])); assert set(r)=={'record_id','record_type','record_schema_version','record_digest','payload'}; assert r['payload']['review_status']=='AWAITING_EDITORIAL_DECISION'; print(r['record_digest'])"
    result = subprocess.run([sys.executable, "-c", code, str(path)], check=True, capture_output=True, text=True)
    assert result.stdout.strip() == bundle.record_digest


def test_load_rejects_tampered_record_digest(tmp_path: Path):
    bundle = ReviewBundle.create(payload_with_e01_artifact(tmp_path), run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z")
    path = save_review_bundle(bundle, tmp_path / "review-bundle.json")
    record = json.loads(path.read_text())
    record["payload"]["query"]["text"] = "tampered"
    path.write_text(json.dumps(record))
    import pytest
    with pytest.raises(ValueError, match="digest"):
        load_review_bundle(path)


@pytest.mark.parametrize("mutate", [
    lambda p: p["source"].update(source_sha256=123),
    lambda p: p["source"].update(source_byte_count="10"),
    lambda p: p["candidate"].update(rank="1"),
    lambda p: p["source"].update(timebase={"num": 1, "den": 0}),
    lambda p: p["candidate"].update(semantic_interval={"start": 1, "end": 2}),
])
def test_from_record_rejects_schema_invalid_payload_even_with_self_consistent_digests(tmp_path: Path, mutate):
    bundle = ReviewBundle.create(payload_with_e01_artifact(tmp_path), run_id="run-1", bundle_id="bundle-1", created_at="2026-09-21T12:00:00Z")
    record = bundle.to_record()
    mutate(record["payload"])
    record["payload"]["dependency_digest"] = _sha(_dependency_projection(record["payload"]))
    record["record_digest"] = record_digest(record)
    with pytest.raises(ValueError):
        ReviewBundle.from_record(record)


def test_concurrent_different_publishers_cannot_clobber_first_sealed_bundle(tmp_path: Path):
    path = tmp_path / "review-bundle.json"
    bundles = [
        ReviewBundle.create(payload_with_e01_artifact(tmp_path / f"publisher-{i}"), run_id="run-1", bundle_id=f"bundle-{i}", created_at="2026-09-21T12:00:00Z")
        for i in (1, 2)
    ]
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda b: _save_capturing(b, path), bundles))
    assert sorted(outcomes) == ["different", "ok"]
    winner = load_review_bundle(path)
    assert winner.record_digest in {bundle.record_digest for bundle in bundles}


def _save_capturing(bundle, path):
    try:
        save_review_bundle(bundle, path)
    except ValueError as exc:
        assert "different digest" in str(exc)
        return "different"
    return "ok"
