"""Cross-index integrity for separately Owner-adopted H3 contract-only successors.

This is metadata/synthetic-only. No Task-6, source, model, network or media run.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / ".orchestration/remaining-work"
PROMPTS = WORK / "prompts"
EXPECTED = {
    "H3-C05": ("h3-c05-core-v1.0.2", "H3-C05/v1.0.2",
               {"vip_fvs_retrieval_adapter": "0f0268d83da4ff6c06c45ad54d85070071d6e155",
                "vip_fvs_coordinator": "1696b31afc58d83269389f025759b2ef7dba7670"}),
    "H3-A04": ("h3-a04-core-v1.0.1", "H3-A04/v1.0.1", {}),
}

def test_owner_adopted_cores_are_exactly_bound_in_atlas_and_prompt_index():
    atlas = {item["id"]: item for item in json.loads((WORK / "atlas/atlas.json").read_text())["nodes"]}
    index = {item["task_id"]: item for item in json.loads((PROMPTS / "index.json").read_text())["entries"]}
    for task_id, (version, subpath, fingerprints) in EXPECTED.items():
        md = PROMPTS / subpath / "core.md"
        js = PROMPTS / subpath / "core.json"
        digest = hashlib.sha256(md.read_bytes()).hexdigest()
        meta = json.loads(js.read_text())
        task = atlas[task_id]
        entry = index[task_id]
        assert meta["task_id"] == task_id
        assert meta["prompt_core"]["version"] == version
        assert meta["prompt_core"]["sha256"] == digest
        assert task["prompt_core_ref"] == str(md.relative_to(ROOT))
        assert task["prompt_core_sha256"] == digest
        assert entry["version"] == version
        assert entry["sha256"] == digest
        assert entry["core_ref"] == str(md.relative_to(ROOT))
        assert entry["metadata_ref"] == str(js.relative_to(ROOT))
        assert {c["id"]: c["fingerprint"] for c in task["consumed_contracts"]} == {
            c["id"]: c["fingerprint"] for c in meta["prompt_core"]["consumed_contracts"]}
        for ident, fingerprint in fingerprints.items():
            assert {c["id"]: c["fingerprint"] for c in task["consumed_contracts"]}[ident] == fingerprint
        # Contract adoption does not promote product, workers or Gate state.
        assert task["state"] == "PLANNED"
        assert entry["atlas_state"] == "PLANNED"
        assert task["candidate_generation"] is None
        assert task["overlay_ref"] is None
