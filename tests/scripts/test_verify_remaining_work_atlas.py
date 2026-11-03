from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify-remaining-work-atlas.py"
ATLAS_REL = Path(".orchestration/remaining-work/atlas/atlas.json")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def write_json(root: Path, rel: Path | str, obj) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return p


def core(root: Path, task_id: str, body: str = "execute\n") -> tuple[str, str]:
    rel = f".orchestration/remaining-work/prompts/{task_id}/core.md"
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body, encoding="utf-8")
    return rel, sha256_text(body)


def node(
    task_id: str,
    *,
    state="READY",
    weight=0.0,
    parent="H0",
    write_domain=None,
    resource_class="LIGHTWEIGHT_CPU_TEST",
    dependencies=None,
    consumed=None,
    prompt_ref=None,
    prompt_sha=None,
    candidate=None,
):
    return {
        "id": task_id,
        "level": "H3" if task_id != "H0" else "H0",
        "title": task_id,
        "parent_id": None if task_id == "H0" else parent,
        "weight": weight,
        "state": state,
        "candidate_generation": candidate,
        "dependencies": dependencies or [],
        "consumed_contracts": consumed or [],
        "produced_contracts": [],
        "write_domain": write_domain or [],
        "resource_class": resource_class,
        "executor_mode": "PARALLEL_PORTFOLIO",
        "prompt_core_ref": prompt_ref,
        "prompt_core_sha256": prompt_sha,
        "overlay_ref": None,
        "verification_ref": None,
        "problem_ids": [],
        "unlocks": [],
    }


def valid_atlas(root: Path):
    p1, h1 = core(root, "H3-A")
    p2, h2 = core(root, "H3-B")
    return {
        "schema_version": "remaining-work-atlas.v1",
        "active_finish_line": "VERIFICATION_COMPLETE_FOR_CURRENT_AUTHORIZED_LOCAL_FIRST_SCOPE",
        "baseline_total_weight": 100.0,
        "contract_registry": {"contract-A": "a" * 40},
        "resource_leases": {
            "LIGHTWEIGHT_CPU_TEST": 16,
            "HEAVY_CPU": 2,
            "FFMPEG_HEAVY": 2,
            "MODEL_MPS": 2,
            "ENV_ADMIN": 1,
        },
        "nodes": [
            node("H0", state="BUILDING", weight=100.0),
            node(
                "H3-A",
                weight=50.0,
                write_domain=["src/a.py"],
                prompt_ref=p1,
                prompt_sha=h1,
                consumed=[{"id": "contract-A", "fingerprint": "a" * 40}],
            ),
            node("H3-B", weight=50.0, write_domain=["src/b.py"], prompt_ref=p2, prompt_sha=h2),
        ],
    }


def run_verify(root: Path, *extra: str):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *extra],
        text=True,
        capture_output=True,
    )


def test_valid_atlas_passes(tmp_path):
    write_json(tmp_path, ATLAS_REL, valid_atlas(tmp_path))
    p = run_verify(tmp_path)
    assert p.returncode == 0, p.stderr + p.stdout
    assert "ATLAS-VERIFY status=PASS" in p.stdout


def test_duplicate_ids_refuse(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"].append(dict(a["nodes"][1]))
    write_json(tmp_path, ATLAS_REL, a)
    p = run_verify(tmp_path)
    assert p.returncode == 2
    assert "duplicate node id" in p.stderr


def test_unknown_parent_refuses(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][1]["parent_id"] = "missing"
    write_json(tmp_path, ATLAS_REL, a)
    p = run_verify(tmp_path)
    assert p.returncode == 2
    assert "unknown parent" in p.stderr


def test_h3_weights_must_sum_to_100(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][2]["weight"] = 40.0
    write_json(tmp_path, ATLAS_REL, a)
    p = run_verify(tmp_path)
    assert p.returncode == 2
    assert "H3 weight total" in p.stderr


def test_dependency_cycle_refuses(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][1]["dependencies"] = [
        {"node_id": "H3-B", "kind": "SOFT_BUILD_DEPENDENCY"}
    ]
    a["nodes"][2]["dependencies"] = [
        {"node_id": "H3-A", "kind": "SOFT_BUILD_DEPENDENCY"}
    ]
    write_json(tmp_path, ATLAS_REL, a)
    p = run_verify(tmp_path)
    assert p.returncode == 2
    assert "dependency cycle" in p.stderr


def test_ready_node_with_unsatisfied_hard_dependency_refuses(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][1]["dependencies"] = [
        {"node_id": "H3-B", "kind": "HARD_VERIFY_DEPENDENCY"}
    ]
    write_json(tmp_path, ATLAS_REL, a)
    p = run_verify(tmp_path)
    assert p.returncode == 2
    assert "unsatisfied HARD_VERIFY_DEPENDENCY" in p.stderr


def test_build_green_requires_candidate_generation(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][1]["state"] = "BUILD_GREEN"
    write_json(tmp_path, ATLAS_REL, a)
    p = run_verify(tmp_path)
    assert p.returncode == 2
    assert "candidate_generation required" in p.stderr


def test_verifying_requires_exact_candidate_generation(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][1]["state"] = "VERIFYING"
    a["nodes"][1]["candidate_generation"] = {"sha": "abc"}
    write_json(tmp_path, ATLAS_REL, a)
    p = run_verify(tmp_path)
    assert p.returncode == 2
    assert "invalid candidate_generation" in p.stderr


def test_prompt_core_hash_mismatch_refuses(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][1]["prompt_core_sha256"] = "0" * 64
    write_json(tmp_path, ATLAS_REL, a)
    p = run_verify(tmp_path)
    assert p.returncode == 2
    assert "prompt core hash mismatch" in p.stderr


def test_contract_fingerprint_mismatch_requires_dirty_state(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][1]["consumed_contracts"][0]["fingerprint"] = "b" * 40
    write_json(tmp_path, ATLAS_REL, a)
    p = run_verify(tmp_path)
    assert p.returncode == 2
    assert "contract fingerprint mismatch" in p.stderr


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def _candidate_contract_repo(tmp_path, *, surfaces=1):
    root = tmp_path / "candidate-repo"
    root.mkdir(parents=True)
    _git(root, "init", "-b", "main")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test User")
    old = "a" * 40
    produced = []
    contract_registry = {}
    entries = []
    for index in range(surfaces):
        contract_id = f"contract-{index}"
        path = f"src/surface-{index}.py"
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"VALUE = {index}\n", encoding="utf-8")
        fingerprint = _git(root, "hash-object", str(target))
        produced.append({"id": contract_id, "fingerprint": fingerprint})
        contract_registry[contract_id] = fingerprint
        entries.append({
            "id": contract_id,
            "fingerprint": fingerprint,
            "kind": "GIT_BLOB",
            "source": f"{path}@PENDING",
        })
    _git(root, "add", "src")
    _git(root, "commit", "-m", "candidate")
    candidate_sha = _git(root, "rev-parse", "HEAD")
    tree = _git(root, "rev-parse", "HEAD^{tree}")
    for entry in entries:
        entry["source"] = entry["source"].replace("PENDING", candidate_sha)
    producer = node(
        "H3-PRODUCER",
        state="VERIFY_READY",
        weight=100.0,
        consumed=[{"id": entry["id"], "fingerprint": old} for entry in entries],
        candidate={
            "sha": candidate_sha,
            "tree": tree,
            "prompt_core_version": "producer-core-v1",
            "overlay_version": "producer-overlay-v1",
            "contract_fingerprints": {
                entry["id"]: old for entry in entries
            },
        },
    )
    producer["produced_contracts"] = produced
    atlas = {
        "schema_version": "remaining-work-atlas.v1",
        "active_finish_line": "VERIFICATION_COMPLETE_FOR_CURRENT_AUTHORIZED_LOCAL_FIRST_SCOPE",
        "baseline_total_weight": 100.0,
        "contract_registry": contract_registry,
        "resource_leases": {"LIGHTWEIGHT_CPU_TEST": 16},
        "nodes": [node("H0", state="BUILDING", weight=100.0), producer],
    }
    write_json(root, ATLAS_REL, atlas)
    write_json(root, ".orchestration/remaining-work/atlas/contract-registry.json", {
        "schema_version": "remaining-work-contract-registry-provenance.v1",
        "entries": entries,
    })
    return root, atlas, old, produced, candidate_sha


def test_producer_keeps_old_consumed_evidence_while_advancing_its_output(tmp_path):
    root, atlas, old, produced, _ = _candidate_contract_repo(tmp_path)
    p = run_verify(root)
    assert p.returncode == 0, p.stderr + p.stdout
    producer = atlas["nodes"][1]
    assert producer["consumed_contracts"] == [{"id": "contract-0", "fingerprint": old}]
    assert producer["candidate_generation"]["contract_fingerprints"] == {"contract-0": old}
    assert producer["produced_contracts"] == produced
    assert atlas["contract_registry"]["contract-0"] == produced[0]["fingerprint"]


def test_downstream_old_consumer_stays_dirty_after_registry_advance(tmp_path):
    root, atlas, old, _, _ = _candidate_contract_repo(tmp_path)
    downstream = node(
        "H3-DOWNSTREAM",
        state="DIRTY_BY_CONTRACT_DELTA",
        weight=0.1,
        consumed=[{"id": "contract-0", "fingerprint": old}],
    )
    atlas["nodes"][1]["weight"] = 99.9
    atlas["nodes"].append(downstream)
    write_json(root, ATLAS_REL, atlas)
    p = run_verify(root)
    assert p.returncode == 0, p.stderr + p.stdout
    assert atlas["nodes"][2]["state"] == "DIRTY_BY_CONTRACT_DELTA"
    assert atlas["nodes"][2]["consumed_contracts"][0]["fingerprint"] == old


def test_changed_consumed_fingerprint_without_produced_transition_fails_closed(tmp_path):
    root, atlas, _, _, _ = _candidate_contract_repo(tmp_path)
    consumer = node(
        "H3-UNAUTHORIZED",
        state="READY",
        weight=0.0,
        consumed=[{"id": "contract-0", "fingerprint": "b" * 40}],
    )
    atlas["nodes"].append(consumer)
    write_json(root, ATLAS_REL, atlas)
    p = run_verify(root)
    assert p.returncode == 2
    assert "contract fingerprint mismatch" in p.stderr


def test_claimed_produced_fingerprint_must_match_exact_candidate_blob(tmp_path):
    root, atlas, _, _, _ = _candidate_contract_repo(tmp_path)
    atlas["nodes"][1]["produced_contracts"][0]["fingerprint"] = "c" * 40
    atlas["contract_registry"]["contract-0"] = "c" * 40
    registry = root / ".orchestration/remaining-work/atlas/contract-registry.json"
    payload = json.loads(registry.read_text())
    payload["entries"][0]["fingerprint"] = "c" * 40
    write_json(root, registry.relative_to(root), payload)
    write_json(root, ATLAS_REL, atlas)
    p = run_verify(root)
    assert p.returncode == 2
    assert "produced contract fingerprint does not match candidate blob" in p.stderr


def test_contract_transition_verification_does_not_mutate_historical_receipt(tmp_path):
    root, _, _, _, _ = _candidate_contract_repo(tmp_path)
    receipt_path = root / ".orchestration/remaining-work/runs/H3-PRODUCER/receipt.json"
    receipt = write_json(root, receipt_path.relative_to(root), {
        "status": "BUILD_GREEN",
        "candidate_generation": {"sha": "d" * 40, "tree": "e" * 40},
        "contract_deltas": [],
    })
    before = hashlib.sha256(receipt.read_bytes()).hexdigest()
    p = run_verify(root)
    assert p.returncode == 0, p.stderr + p.stdout
    assert hashlib.sha256(receipt.read_bytes()).hexdigest() == before


def test_one_candidate_can_advance_multiple_registered_surfaces(tmp_path):
    root, atlas, old, produced, _ = _candidate_contract_repo(tmp_path, surfaces=3)
    p = run_verify(root)
    assert p.returncode == 0, p.stderr + p.stdout
    assert [item["fingerprint"] for item in atlas["nodes"][1]["consumed_contracts"]] == [old] * 3
    assert atlas["nodes"][1]["produced_contracts"] == produced
    assert atlas["contract_registry"] == {
        item["id"]: item["fingerprint"] for item in produced
    }


def _clone_current_repository(tmp_path):
    tmp_path.mkdir(parents=True, exist_ok=True)
    root = tmp_path / "b04-repository"
    subprocess.run(
        ["git", "clone", "--shared", "--quiet", str(ROOT), str(root)],
        check=True,
        text=True,
        capture_output=True,
    )
    return root


def _b04_records(root):
    atlas = json.loads((root / ATLAS_REL).read_text(encoding="utf-8"))
    registry = json.loads(
        (root / ".orchestration/remaining-work/atlas/contract-registry.json")
        .read_text(encoding="utf-8")
    )
    by_id = {item["id"]: item for item in atlas["nodes"]}
    provenance = {item["id"]: item for item in registry["entries"]}
    return atlas, by_id, provenance


def test_concrete_b04_transition_and_batch005_are_candidate_bound(tmp_path):
    root = _clone_current_repository(tmp_path)
    atlas, nodes, registry = _b04_records(root)
    producer = nodes["H3-B04"]
    candidate_sha = "73959e08ce962d9d21d294b29a703afc69e54009"
    old = {
        "vip_fvs_local_semantic": "851b18616d0b2e338e8221728bcfa5b423462156",
        "vip_fvs_retrieval_adapter": "473948ce43ecc41f1b5e68a0208f58b217457fd0",
    }
    new = {
        "vip_fvs_local_semantic": "a00fd25861358a022f1fcfc97eae434f5bd62bc8",
        "vip_fvs_retrieval_adapter": "348bf9979e5c2e0a77e338e7cb5ff84910db2ad6",
        "vip_fvs_semantic_index": "e81fd15ee243b59b02bace14131c9d6b39b66701",
    }

    assert producer["state"] == "VERIFY_READY"
    consumed = {
        item["id"]: item["fingerprint"] for item in producer["consumed_contracts"]
    }
    for contract_id, fingerprint in old.items():
        assert consumed[contract_id] == fingerprint
        assert producer["candidate_generation"]["contract_fingerprints"][contract_id] == fingerprint
    assert {item["id"]: item["fingerprint"] for item in producer["produced_contracts"]} == new

    expected_paths = {
        "vip_fvs_local_semantic": "src/vip_fvs/local_semantic.py",
        "vip_fvs_retrieval_adapter": "src/vip_fvs/retrieval_adapter.py",
        "vip_fvs_semantic_index": "src/vip_fvs/semantic_index.py",
    }
    for contract_id, fingerprint in new.items():
        entry = registry[contract_id]
        path, revision = entry["source"].rsplit("@", 1)
        assert entry["kind"] == "GIT_BLOB"
        assert path == expected_paths[contract_id]
        assert revision == candidate_sha
        assert entry["fingerprint"] == fingerprint
        assert _git(root, "rev-parse", f"{candidate_sha}:{path}") == fingerprint
        assert atlas["contract_registry"][contract_id] == fingerprint

    consumer = nodes["H3-B05"]
    assert consumer["state"] == "READY"
    assert consumer["prompt_core_ref"].endswith("/v1.0.1/core.md")
    assert {item["id"]: item["fingerprint"] for item in consumer["consumed_contracts"]}[
        "vip_fvs_retrieval_adapter"
    ] == new["vip_fvs_retrieval_adapter"]
    assert {
        (item["node_id"], item["kind"]) for item in consumer["dependencies"]
    } >= {("H3-B04", "HARD_BUILD_DEPENDENCY")}

    p = run_verify(
        root,
        "--launch-pack",
        str(root / ".orchestration/remaining-work/launch-packs/batch-005/manifest.json"),
        "--historical-launch-pack",
    )
    assert p.returncode == 0, p.stderr + p.stdout


def test_concrete_b04_old_snapshot_and_ready_old_consumer_are_rejected(tmp_path):
    root = _clone_current_repository(tmp_path)
    atlas, nodes, _ = _b04_records(root)
    producer = nodes["H3-B04"]
    old = "473948ce43ecc41f1b5e68a0208f58b217457fd0"
    new = "348bf9979e5c2e0a77e338e7cb5ff84910db2ad6"

    producer["consumed_contracts"] = [
        {**item, "fingerprint": new}
        if item["id"] == "vip_fvs_retrieval_adapter"
        else item
        for item in producer["consumed_contracts"]
    ]
    producer["candidate_generation"]["contract_fingerprints"][
        "vip_fvs_retrieval_adapter"
    ] = new
    transition_path = root / producer["overlay_ref"]
    transition = json.loads(transition_path.read_text(encoding="utf-8"))
    transition["contract_fingerprints"]["vip_fvs_retrieval_adapter"] = new
    write_json(root, producer["overlay_ref"], transition)
    write_json(root, ATLAS_REL, atlas)
    p = run_verify(root, "--require-prompt-metadata")
    assert p.returncode == 2
    assert "prompt consumed_contracts mismatch for H3-B04" in p.stderr
    assert old != new

    root = _clone_current_repository(tmp_path / "second")
    atlas, nodes, _ = _b04_records(root)
    consumer = nodes["H3-B05"]
    consumer["consumed_contracts"] = [
        {**item, "fingerprint": old}
        if item["id"] == "vip_fvs_retrieval_adapter"
        else item
        for item in consumer["consumed_contracts"]
    ]
    write_json(root, ATLAS_REL, atlas)
    p = run_verify(root)
    assert p.returncode == 2
    assert "contract fingerprint mismatch for H3-B05: vip_fvs_retrieval_adapter" in p.stderr

    root = _clone_current_repository(tmp_path / "reconciled")
    atlas, nodes, _ = _b04_records(root)
    consumer = nodes["H3-B05"]
    consumer["state"] = "DIRTY_BY_CONTRACT_DELTA"
    consumer["consumed_contracts"] = [
        {**item, "fingerprint": old}
        if item["id"] == "vip_fvs_retrieval_adapter"
        else item
        for item in consumer["consumed_contracts"]
    ]
    write_json(root, ATLAS_REL, atlas)
    p = run_verify(root)
    assert p.returncode == 0, p.stderr + p.stdout


def test_concrete_b04_each_output_is_checked_against_its_candidate_blob(tmp_path):
    root = _clone_current_repository(tmp_path)
    atlas, nodes, registry = _b04_records(root)
    output_id = "vip_fvs_semantic_index"
    forged = "1" * 40
    nodes["H3-B04"]["produced_contracts"] = [
        {**item, "fingerprint": forged} if item["id"] == output_id else item
        for item in nodes["H3-B04"]["produced_contracts"]
    ]
    atlas["contract_registry"][output_id] = forged
    registry[output_id]["fingerprint"] = forged
    registry[output_id]["source"] = "src/vip_fvs/semantic_index.py@main"
    for node_record in atlas["nodes"]:
        node_record["consumed_contracts"] = [
            {**item, "fingerprint": forged} if item.get("id") == output_id else item
            for item in node_record.get("consumed_contracts", [])
        ]
    write_json(root, ATLAS_REL, atlas)
    write_json(
        root,
        ".orchestration/remaining-work/atlas/contract-registry.json",
        {"schema_version": "remaining-work-contract-registry-provenance.v1", "entries": list(registry.values())},
    )

    p = run_verify(root)
    assert p.returncode == 2
    assert "produced contract fingerprint does not match candidate blob for H3-B04: vip_fvs_semantic_index" in p.stderr


def test_each_same_candidate_output_requires_candidate_pinned_provenance(tmp_path):
    for index in range(3):
        root, atlas, _, produced, _ = _candidate_contract_repo(
            tmp_path / f"surface-{index}", surfaces=3
        )
        registry_path = root / ".orchestration/remaining-work/atlas/contract-registry.json"
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        registry["entries"][index]["source"] = (
            registry["entries"][index]["source"].rsplit("@", 1)[0] + "@main"
        )
        write_json(root, registry_path.relative_to(root), registry)
        p = run_verify(root)
        assert p.returncode == 2
        contract_id = produced[index]["id"]
        assert (
            "produced contract fingerprint does not match candidate blob "
            f"for H3-PRODUCER: {contract_id}"
        ) in p.stderr


def test_historical_b04_launch_snapshot_stays_immutable_during_current_verification(tmp_path):
    root = _clone_current_repository(tmp_path)
    historical_manifest = root / ".orchestration/remaining-work/launch-packs/batch-003/manifest.json"
    historical_prompt = root / ".orchestration/remaining-work/launch-packs/batch-003/prompts/02-H3-B04.md"
    before = {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (historical_manifest, historical_prompt)
    }
    prompt_text = historical_prompt.read_text(encoding="utf-8")
    assert "473948ce43ecc41f1b5e68a0208f58b217457fd0" in prompt_text
    assert "851b18616d0b2e338e8221728bcfa5b423462156" in prompt_text
    assert "a00fd25861358a022f1fcfc97eae434f5bd62bc8" not in prompt_text

    p = run_verify(
        root,
        "--launch-pack",
        str(root / ".orchestration/remaining-work/launch-packs/batch-005/manifest.json"),
        "--historical-launch-pack",
    )
    assert p.returncode == 0, p.stderr + p.stdout

    historical_check = run_verify(
        root,
        "--launch-pack",
        str(historical_manifest),
        "--historical-launch-pack",
    )
    assert historical_check.returncode == 0, historical_check.stderr + historical_check.stdout
    after = {
        path: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (historical_manifest, historical_prompt)
    }
    assert after == before


def write_test_launch_bootstrap(root: Path):
    ref = ".orchestration/remaining-work/prompts/_template/launch-bootstrap-v2.md"
    text = "# Launch Bootstrap v2\n"
    p = root / ref
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    digest = hashlib.sha256(text.encode()).hexdigest()
    meta_ref = ".orchestration/remaining-work/prompts/_template/launch-bootstrap-v2.json"
    write_json(root, meta_ref, {
        "schema_version": "remaining-work-launch-bootstrap.v2",
        "version": "launch-bootstrap-v2.0.3",
        "sha256": digest,
        "ref": ref,
        "preflight_script_ref": "scripts/preflight-remaining-work-launch.py",
        "verified_superpowers_skills": ["using-superpowers"],
    })
    script = root / "scripts/preflight-remaining-work-launch.py"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text("#!/usr/bin/env python3\n")
    return {
        "version": "launch-bootstrap-v2.0.3",
        "sha256": digest,
        "ref": ref,
        "metadata_ref": meta_ref,
        "preflight_script_ref": "scripts/preflight-remaining-work-launch.py",
    }


def write_launch_pack(root: Path, tasks):
    bootstrap = write_test_launch_bootstrap(root)
    return write_json(
        root,
        ".orchestration/remaining-work/launch-packs/batch-001/manifest.json",
        {
            "schema_version": "remaining-work-launch-pack.v1",
            "batch_id": "batch-001",
            "generated_at_head": "c" * 40,
            "launch_bootstrap": bootstrap,
            "entries": [{"task_id": t} for t in tasks],
        },
    )


def test_launch_pack_rejects_overlapping_writers(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][2]["write_domain"] = ["src/a.py"]
    write_json(tmp_path, ATLAS_REL, a)
    lp = write_launch_pack(tmp_path, ["H3-A", "H3-B"])
    p = run_verify(tmp_path, "--launch-pack", str(lp))
    assert p.returncode == 2
    assert "overlapping write ownership" in p.stderr


def test_launch_pack_rejects_resource_lease_overflow(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][1]["resource_class"] = "FFMPEG_HEAVY"
    a["nodes"][2]["resource_class"] = "FFMPEG_HEAVY"
    p3, h3 = core(tmp_path, "H3-C")
    a["nodes"].append(
        node(
            "H3-C",
            weight=33.0,
            write_domain=["src/c.py"],
            resource_class="FFMPEG_HEAVY",
            prompt_ref=p3,
            prompt_sha=h3,
        )
    )
    a["nodes"][1]["weight"] = 34.0
    a["nodes"][2]["weight"] = 33.0
    write_json(tmp_path, ATLAS_REL, a)
    lp = write_launch_pack(tmp_path, ["H3-A", "H3-B", "H3-C"])
    p = run_verify(tmp_path, "--launch-pack", str(lp))
    assert p.returncode == 2
    assert "resource lease exceeded" in p.stderr


def test_launch_pack_rejects_non_ready_task(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][1]["state"] = "PARKED"
    write_json(tmp_path, ATLAS_REL, a)
    lp = write_launch_pack(tmp_path, ["H3-A"])
    p = run_verify(tmp_path, "--launch-pack", str(lp))
    assert p.returncode == 2
    assert "launch entry is not READY" in p.stderr


def test_stale_in_flight_cannot_launch(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][1]["state"] = "STALE_IN_FLIGHT"
    write_json(tmp_path, ATLAS_REL, a)
    lp = write_launch_pack(tmp_path, ["H3-A"])
    p = run_verify(tmp_path, "--launch-pack", str(lp))
    assert p.returncode == 2
    assert "launch entry is not READY" in p.stderr


def test_schema_contract_files_parse_and_include_required_enums():
    atlas_schema = json.loads(
        (ROOT / "schemas/orchestration/remaining-work-atlas.schema.json").read_text()
    )
    launch_schema = json.loads(
        (ROOT / "schemas/orchestration/remaining-work-launch-pack.schema.json").read_text()
    )
    prompt_schema = json.loads(
        (ROOT / "schemas/orchestration/remaining-work-prompt-packet.schema.json").read_text()
    )

    state_enum = set(
        atlas_schema["$defs"]["node"]["properties"]["state"]["enum"]
    )
    assert {"BUILD_GREEN", "VERIFYING", "REPAIRING", "STALE_IN_FLIGHT"} <= state_enum
    dep_enum = set(
        atlas_schema["$defs"]["dependency"]["properties"]["kind"]["enum"]
    )
    assert {"SOFT_BUILD_DEPENDENCY", "HARD_VERIFY_DEPENDENCY"} <= dep_enum
    assert (
        launch_schema["properties"]["schema_version"]["const"]
        == "remaining-work-launch-pack.v1"
    )
    assert (
        prompt_schema["properties"]["schema_version"]["const"]
        == "remaining-work-prompt-packet.v1"
    )


def test_controller_bootstrap_state_is_self_locating():
    state_path = ROOT / ".orchestration/remaining-work/controller-state.json"
    start_path = ROOT / ".orchestration/remaining-work/CONTROLLER_START_HERE.md"
    state = json.loads(state_path.read_text())
    start = start_path.read_text()

    assert state["schema_version"] == "remaining-work-controller-state.v1"
    assert (
        state["current_resource_policy_ref"]
        == "docs/portfolio/portfolio-v1/resource-policy-v5.yaml"
    )
    assert (
        state["active_finish_line"]
        == "VERIFICATION_COMPLETE_FOR_CURRENT_AUTHORIZED_LOCAL_FIRST_SCOPE"
    )
    assert isinstance(state["stage"], str) and state["stage"]
    assert state["atlas_ref"] == ".orchestration/remaining-work/atlas/atlas.json"
    assert (ROOT / state["atlas_ref"]).is_file()
    assert (ROOT / state["current_resource_policy_ref"]).is_file()
    assert state["prompt_library_state"] == "FULL_H1_A_H1_B_H1_C_H1_D_H1_E_H1_F_H1_G_FROZEN"

    current_pack_ref = state["current_launch_pack_ref"]
    assert isinstance(current_pack_ref, str) and current_pack_ref
    pack_path = ROOT / current_pack_ref
    assert pack_path.is_file()
    pack = json.loads(pack_path.read_text())
    assert pack["schema_version"] == "remaining-work-launch-pack.v1"
    expected_next_chunk = "EXECUTION_" + pack["batch_id"].upper().replace("-", "_")
    assert state["next_chunk"] == expected_next_chunk
    assert state["launch_base_sha"] == pack["generated_at_head"]

    if state.get("current_launch_pack_state") == "GENERATED_NOT_DISPATCHED":
        assert state["current_launch_pack_dispatched"] is False
        assert state["prompts_dispatched"] is False

    last_reconciliation_ref = state.get("last_reconciliation_ref")
    if last_reconciliation_ref:
        assert (ROOT / last_reconciliation_ref).is_file()

    assert "Launch Delta Reconciliation" in start
    assert "Do not regenerate Frozen Cores" in start

def test_h3_zero_weight_refuses(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][1]["weight"] = 0.0
    a["nodes"][2]["weight"] = 100.0
    write_json(tmp_path, ATLAS_REL, a)
    p = run_verify(tmp_path)
    assert p.returncode == 2
    assert "H3 weight must be positive" in p.stderr


def test_prompt_core_ref_cannot_escape_repo_root(tmp_path):
    a = valid_atlas(tmp_path)
    outside = tmp_path.parent / "outside-core.md"
    outside.write_text("outside\n")
    a["nodes"][1]["prompt_core_ref"] = "../outside-core.md"
    a["nodes"][1]["prompt_core_sha256"] = sha256_text("outside\n")
    write_json(tmp_path, ATLAS_REL, a)
    p = run_verify(tmp_path)
    assert p.returncode == 2
    assert "prompt_core_ref escapes repository root" in p.stderr


def test_launch_pack_rejects_duplicate_task_ids(tmp_path):
    a = valid_atlas(tmp_path)
    write_json(tmp_path, ATLAS_REL, a)
    lp = write_launch_pack(tmp_path, ["H3-A", "H3-A"])
    p = run_verify(tmp_path, "--launch-pack", str(lp))
    assert p.returncode == 2
    assert "duplicate launch task" in p.stderr


def write_frozen_core_metadata(root: Path, task_id: str, atlas_node: dict, *, mutate=None):
    core_ref = atlas_node["prompt_core_ref"]
    assert core_ref
    core_path = root / core_ref
    payload = {
        "schema_version": "remaining-work-frozen-core.v1",
        "task_id": task_id,
        "prompt_core": {
            "version": f"{task_id.lower()}-core-v1",
            "sha256": sha256_text(core_path.read_text()),
            "goal": f"Complete {task_id}",
            "dependencies": atlas_node["dependencies"],
            "expected_deliverables": ["verified implementation candidate"],
            "read_scope": [
                "AGENTS.md",
                ".orchestration/remaining-work/CONTROLLER_START_HERE.md",
                ".orchestration/remaining-work/atlas/atlas.json",
            ],
            "write_domain": atlas_node["write_domain"],
            "consumed_contracts": atlas_node["consumed_contracts"],
            "prohibited_scope": ["canonical main integration"],
            "focused_tests": ["focused-test-command"],
            "verification_hooks": [
                "QUEUE_ASYNC_FEATURE_REVIEW_ON_VERIFY_FRONTIER",
                "verification-before-completion",
            ],
            "h4_decomposition_guidance": ["split independent read/test domains"],
            "parallelism_contract": [
                "DISPATCH_INDEPENDENT_H4_CONCURRENTLY",
                "ROOT_IS_CONTROL_PLANE",
                "RECYCLE_TERMINAL_CHILD_SLOTS",
                "EXCLUSIVE_WRITER_OWNERSHIP",
                "ASYNC_FEATURE_REVIEW_ON_VERIFY_FRONTIER",
                "VERIFY_DOES_NOT_BLOCK_UNRELATED_BUILD",
                "NO_STOCK_SUBAGENT_DRIVEN_DEVELOPMENT_DEFAULT",
            ],
            "failure_policy": {
                "systematic_debugging_on_unexpected_failure": True,
                "max_failed_generations_per_root_cause_family": 3,
                "continue_unaffected_ready_work": True,
            },
            "receipt_contract": {
                "required_fields": [
                    "TASK",
                    "STATUS",
                    "BASE_SHA",
                    "HEAD_SHA",
                    "CHANGED_PATHS",
                    "FOCUSED_TESTS",
                    "CANDIDATE_GENERATION",
                    "CONTRACT_DELTAS",
                    "PROBLEMS",
                    "DURABLE_HANDOFF",
                    "UNLOCKS",
                    "PUSH_STATUS",
                ]
            },
            "executor_mode": atlas_node["executor_mode"],
            "resource_class": atlas_node["resource_class"],
        },
    }
    if mutate:
        mutate(payload)
    meta_path = core_path.with_name("core.json")
    write_json(root, meta_path.relative_to(root), payload)
    return meta_path


def test_prompt_schema_requires_deliverables_executor_and_parallelism_contract():
    prompt_schema = json.loads(
        (ROOT / "schemas/orchestration/remaining-work-prompt-packet.schema.json").read_text()
    )
    required = set(prompt_schema["$defs"]["prompt_core"]["required"])
    assert {
        "expected_deliverables",
        "executor_mode",
        "resource_class",
        "parallelism_contract",
        "receipt_contract",
    } <= required


def test_prompt_metadata_matches_atlas_contract(tmp_path):
    a = valid_atlas(tmp_path)
    write_json(tmp_path, ATLAS_REL, a)
    for n in a["nodes"]:
        if n.get("prompt_core_ref"):
            write_frozen_core_metadata(tmp_path, n["id"], n)
    p = run_verify(tmp_path, "--require-prompt-metadata")
    assert p.returncode == 0, p.stderr + p.stdout


def test_prompt_metadata_blocks_required_authority_without_owner_reference(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][1]["implementation_authorization_required"] = True
    a["nodes"][1]["historical_implementation_authority"] = "PARKED / NOT AUTHORIZED"
    write_json(tmp_path, ATLAS_REL, a)
    for n in a["nodes"]:
        if n.get("prompt_core_ref"):
            write_frozen_core_metadata(tmp_path, n["id"], n)
    p = run_verify(tmp_path, "--require-prompt-metadata")
    assert p.returncode == 2
    assert "implementation_authorization_ref_missing for H3-A" in p.stderr


def test_prompt_metadata_contract_delta_refuses(tmp_path):
    a = valid_atlas(tmp_path)
    write_json(tmp_path, ATLAS_REL, a)
    for n in a["nodes"]:
        if n.get("prompt_core_ref"):
            def mutate(payload):
                if payload["task_id"] == "H3-A":
                    payload["prompt_core"]["consumed_contracts"][0]["fingerprint"] = "b" * 40
            write_frozen_core_metadata(tmp_path, n["id"], n, mutate=mutate)
    p = run_verify(tmp_path, "--require-prompt-metadata")
    assert p.returncode == 2
    assert "prompt consumed_contracts mismatch" in p.stderr


def test_prompt_metadata_write_domain_mismatch_refuses(tmp_path):
    a = valid_atlas(tmp_path)
    write_json(tmp_path, ATLAS_REL, a)
    for n in a["nodes"]:
        if n.get("prompt_core_ref"):
            def mutate(payload):
                if payload["task_id"] == "H3-A":
                    payload["prompt_core"]["write_domain"] = ["src/not-authorized.py"]
            write_frozen_core_metadata(tmp_path, n["id"], n, mutate=mutate)
    p = run_verify(tmp_path, "--require-prompt-metadata")
    assert p.returncode == 2
    assert "prompt write_domain mismatch" in p.stderr


def test_prompt_metadata_launch_fields_are_forbidden_in_frozen_core(tmp_path):
    a = valid_atlas(tmp_path)
    write_json(tmp_path, ATLAS_REL, a)
    for n in a["nodes"]:
        if n.get("prompt_core_ref"):
            def mutate(payload):
                if payload["task_id"] == "H3-A":
                    payload["prompt_core"]["base_sha"] = "c" * 40
            write_frozen_core_metadata(tmp_path, n["id"], n, mutate=mutate)
    p = run_verify(tmp_path, "--require-prompt-metadata")
    assert p.returncode == 2
    assert "launch-only field in Frozen Core" in p.stderr


def test_prompt_metadata_requires_async_review_and_parallelism_hooks(tmp_path):
    a = valid_atlas(tmp_path)
    write_json(tmp_path, ATLAS_REL, a)
    for n in a["nodes"]:
        if n.get("prompt_core_ref"):
            def mutate(payload):
                if payload["task_id"] == "H3-A":
                    payload["prompt_core"]["parallelism_contract"] = ["ROOT_IS_CONTROL_PLANE"]
            write_frozen_core_metadata(tmp_path, n["id"], n, mutate=mutate)
    p = run_verify(tmp_path, "--require-prompt-metadata")
    assert p.returncode == 2
    assert "missing mandatory parallelism hook" in p.stderr


def test_prompt_metadata_receipt_contract_is_exact(tmp_path):
    a = valid_atlas(tmp_path)
    write_json(tmp_path, ATLAS_REL, a)
    for n in a["nodes"]:
        if n.get("prompt_core_ref"):
            def mutate(payload):
                if payload["task_id"] == "H3-A":
                    payload["prompt_core"]["receipt_contract"]["required_fields"] = ["TASK", "STATUS"]
            write_frozen_core_metadata(tmp_path, n["id"], n, mutate=mutate)
    p = run_verify(tmp_path, "--require-prompt-metadata")
    assert p.returncode == 2
    assert "prompt receipt contract mismatch" in p.stderr


def test_full_h1_a_through_h1_g_real_frozen_prompt_library_is_self_consistent():
    atlas = json.loads(
        (ROOT / ".orchestration/remaining-work/atlas/atlas.json").read_text()
    )
    index = json.loads(
        (ROOT / ".orchestration/remaining-work/prompts/index.json").read_text()
    )
    by_id = {n["id"]: n for n in atlas["nodes"]}
    expected = (
        [f"H3-A0{i}" for i in range(1, 8)]
        + [f"H3-B0{i}" for i in range(1, 6)]
        + [f"H3-C0{i}" for i in range(1, 6)]
        + [f"H3-D0{i}" for i in range(1, 6)]
        + [f"H3-E0{i}" for i in range(1, 6)]
        + [f"H3-F0{i}" for i in range(1, 4)]
        + [f"H3-G0{i}" for i in range(1, 4)]
    )

    assert index["generated_chapters"] == ["H1-A", "H1-B", "H1-C", "H1-D", "H1-E", "H1-F", "H1-G"]
    assert index["library_state"] == "FULL_H1_A_H1_B_H1_C_H1_D_H1_E_H1_F_H1_G_FROZEN"
    assert [e["task_id"] for e in index["entries"]] == expected

    for entry in index["entries"]:
        task_id = entry["task_id"]
        node = by_id[task_id]
        core_path = ROOT / node["prompt_core_ref"]
        meta_path = core_path.with_name("core.json")
        meta = json.loads(meta_path.read_text())["prompt_core"]
        digest = hashlib.sha256(core_path.read_bytes()).hexdigest()

        assert digest == node["prompt_core_sha256"] == entry["sha256"] == meta["sha256"]
        assert meta["dependencies"] == node["dependencies"]
        assert meta["write_domain"] == node["write_domain"]
        assert meta["consumed_contracts"] == node["consumed_contracts"]
        assert meta["executor_mode"] == node["executor_mode"]
        assert meta["resource_class"] == node["resource_class"]
        assert "ASYNC_FEATURE_REVIEW_ON_VERIFY_FRONTIER" in meta["parallelism_contract"]
        assert "NO_STOCK_SUBAGENT_DRIVEN_DEVELOPMENT_DEFAULT" in meta["parallelism_contract"]

    outside_generated_chapters = [
        n["id"]
        for n in atlas["nodes"]
        if n["level"] == "H3"
        and n["id"] not in expected
        and n["prompt_core_ref"] is not None
    ]
    assert outside_generated_chapters == []


def _valid_candidate_generation_for_launch_test():
    return {
        "sha": "a" * 40,
        "tree": "b" * 40,
        "prompt_core_version": "core-v1",
        "overlay_version": "overlay-v1",
        "contract_fingerprints": {},
    }


def test_launch_pack_verify_lane_is_read_only_and_can_overlap_build(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][1]["state"] = "VERIFY_READY"
    a["nodes"][1]["candidate_generation"] = _valid_candidate_generation_for_launch_test()
    a["nodes"][2]["write_domain"] = ["src/a.py"]
    bootstrap = write_test_launch_bootstrap(tmp_path)
    bootstrap_text = (tmp_path / bootstrap["ref"]).read_text()
    entries = []
    for node, lane, mode, executor in [
        (a["nodes"][1], "VERIFY", "READ_ONLY", "VERIFY_ONLY"),
        (a["nodes"][2], "BUILD", "WRITE", "PARALLEL_PORTFOLIO"),
    ]:
        task_id = node["id"]
        overlay_ref, overlay = _write_exact_overlay_for_launch_prompt(tmp_path, task_id, "c" * 40)
        node["overlay_ref"] = overlay_ref
        prompt_rel = f"prompts/{task_id}.md"
        core_text = (tmp_path / node["prompt_core_ref"]).read_text()
        core_marker = "## Governing Frozen Core" if lane == "VERIFY" else "## Frozen Core"
        prompt_path = tmp_path / ".orchestration/remaining-work/launch-packs/batch-verify" / prompt_rel
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(
            f"# {task_id}\n\n## Launch Bootstrap v2\n\n"
            + bootstrap_text.rstrip()
            + "\n\n## Launch Overlay\n\n"
            + json.dumps(overlay, indent=2, sort_keys=True)
            + f"\n\n{core_marker}\n\n"
            + core_text
        )
        entries.append({
            "task_id": task_id,
            "lane": lane,
            "write_mode": mode,
            "prompt_ref": prompt_rel,
            "core_ref": node["prompt_core_ref"],
            "overlay_ref": overlay_ref,
            "executor_mode": executor,
            "resource_class": "LIGHTWEIGHT_CPU_TEST",
        })
    write_json(tmp_path, ATLAS_REL, a)
    lp = write_json(
        tmp_path,
        ".orchestration/remaining-work/launch-packs/batch-verify/manifest.json",
        {
            "schema_version": "remaining-work-launch-pack.v1",
            "batch_id": "batch-verify",
            "generated_at_head": "c" * 40,
            "launch_bootstrap": bootstrap,
            "entries": entries,
        },
    )
    p = run_verify(tmp_path, "--launch-pack", str(lp))
    assert p.returncode == 0, p.stderr + p.stdout


def test_launch_pack_repair_lane_still_owns_writer_paths(tmp_path):
    a = valid_atlas(tmp_path)
    a["nodes"][1]["state"] = "REPAIRING"
    a["nodes"][1]["candidate_generation"] = _valid_candidate_generation_for_launch_test()
    a["nodes"][2]["write_domain"] = ["src/a.py"]
    write_json(tmp_path, ATLAS_REL, a)
    lp = write_json(
        tmp_path,
        ".orchestration/remaining-work/launch-packs/batch-repair/manifest.json",
        {
            "schema_version": "remaining-work-launch-pack.v1",
            "batch_id": "batch-repair",
            "generated_at_head": "c" * 40,
            "launch_bootstrap": write_test_launch_bootstrap(tmp_path),
            "entries": [
                {
                    "task_id": "H3-A",
                    "lane": "REPAIR",
                    "write_mode": "WRITE",
                    "executor_mode": "REPAIR_CELL",
                    "resource_class": "LIGHTWEIGHT_CPU_TEST",
                },
                {"task_id": "H3-B"},
            ],
        },
    )
    p = run_verify(tmp_path, "--launch-pack", str(lp))
    assert p.returncode == 2
    assert "overlapping write ownership" in p.stderr


def test_launch_pack_schema_allows_lane_and_copy_ready_metadata():
    schema = json.loads(
        (ROOT / "schemas/orchestration/remaining-work-launch-pack.schema.json").read_text()
    )
    props = schema["properties"]
    entry_props = props["entries"]["items"]["properties"]
    assert {"fresh_codex_default", "instruction"} <= set(props)
    assert {"lane", "state", "write_mode", "core_ref", "overlay_ref"} <= set(entry_props)
    required_entry = set(schema["properties"]["entries"]["items"]["required"])
    assert {"task_id", "prompt_ref", "core_ref", "overlay_ref", "lane", "write_mode", "executor_mode", "resource_class"} <= required_entry
    assert set(entry_props["lane"]["enum"]) == {"BUILD", "VERIFY", "REPAIR"}


def test_first_real_launch_pack_binds_the_six_root_ready_frontier():
    pack_path = (
        ROOT / ".orchestration/remaining-work/launch-packs/batch-001/manifest.json"
    )
    pack = json.loads(pack_path.read_text())
    expected = ["H3-B01", "H3-C01", "H3-E01", "H3-A01", "H3-D01", "H3-F01"]

    assert pack["schema_version"] == "remaining-work-launch-pack.v1"
    assert pack["fresh_codex_default"] is True
    assert [e["task_id"] for e in pack["entries"]] == expected
    assert len(pack["entries"]) == 6

    owned = []
    historical_resource_leases = None
    overlay_marker = "## Launch Overlay\n\n```json\n"
    overlay_end_marker = "\n```\n\n## Frozen Core"

    for entry in pack["entries"]:
        task_id = entry["task_id"]
        assert entry["lane"] == "BUILD"
        assert entry["state"] == "READY"
        assert entry["write_mode"] == "WRITE"

        core_path = ROOT / entry["core_ref"]
        core_meta_path = core_path.with_name("core.json")
        core_meta = json.loads(core_meta_path.read_text())
        core = core_meta["prompt_core"]
        assert core_meta["task_id"] == task_id
        assert core["sha256"] == sha256_text(core_path.read_text())
        assert core["dependencies"] == []
        assert entry["executor_mode"] == core["executor_mode"]
        assert entry["resource_class"] == core["resource_class"]

        prompt_path = pack_path.parent / entry["prompt_ref"]
        prompt = prompt_path.read_text()
        assert "fresh top-level Codex" in prompt
        assert core_path.read_text() in prompt

        overlay_start = prompt.index(overlay_marker) + len(overlay_marker)
        overlay_end = prompt.index(overlay_end_marker, overlay_start)
        historical_overlay = json.loads(prompt[overlay_start:overlay_end])

        assert historical_overlay["task_id"] == task_id
        assert historical_overlay["base_sha"] == pack["generated_at_head"]
        assert historical_overlay["reconciled_at_head"] == pack["generated_at_head"]
        assert historical_overlay["dependency_heads"] == {}
        assert historical_overlay["open_problem_ids"] == []
        assert historical_overlay["contract_deltas"] == []
        assert historical_overlay["resolved_model_identity"] in prompt
        assert "family=LUNA" in historical_overlay["resolved_model_identity"]
        assert "reasoning=medium" in historical_overlay["resolved_model_identity"]

        if historical_resource_leases is None:
            historical_resource_leases = historical_overlay["resource_leases"]
        else:
            assert historical_overlay["resource_leases"] == historical_resource_leases

        for path in core["write_domain"]:
            for other_task, other_path in owned:
                assert not (
                    path.rstrip("/") == other_path.rstrip("/")
                    or path.rstrip("/").startswith(other_path.rstrip("/") + "/")
                    or other_path.rstrip("/").startswith(path.rstrip("/") + "/")
                ), (other_task, other_path, task_id, path)
            owned.append((task_id, path))

    assert historical_resource_leases is not None
    counts = {}
    for entry in pack["entries"]:
        counts[entry["resource_class"]] = counts.get(entry["resource_class"], 0) + 1
    for resource_class, count in counts.items():
        assert count <= historical_resource_leases[resource_class]


def test_batch_004_reconciliation_overlay_refs_match_manifest():
    reconciliation_path = (
        ROOT
        / ".orchestration/remaining-work/reconciliation/batch-003-reconciliation-20261003.json"
    )
    manifest_path = (
        ROOT / ".orchestration/remaining-work/launch-packs/batch-004/manifest.json"
    )
    reconciliation = json.loads(reconciliation_path.read_text())
    manifest = json.loads(manifest_path.read_text())

    reconciliation_entries = {
        entry["task_id"]: entry for entry in reconciliation["batch_004"]["entries"]
    }
    for manifest_entry in manifest["entries"]:
        task_id = manifest_entry["task_id"]
        assert reconciliation_entries[task_id]["overlay_ref"] == manifest_entry["overlay_ref"]

def test_real_frozen_core_structured_read_scope_contains_common_authority_files():
    atlas = json.loads(
        (ROOT / ".orchestration/remaining-work/atlas/atlas.json").read_text()
    )
    required = {
        "AGENTS.md",
        ".orchestration/remaining-work/CONTROLLER_START_HERE.md",
        ".orchestration/remaining-work/atlas/atlas.json",
    }
    for node in atlas["nodes"]:
        if node.get("level") != "H3" or not node.get("prompt_core_ref"):
            continue
        meta_path = (ROOT / node["prompt_core_ref"]).with_name("core.json")
        meta = json.loads(meta_path.read_text())["prompt_core"]
        assert required <= set(meta["read_scope"]), node["id"]


def test_launch_pack_schema_requires_bootstrap_binding():
    schema = json.loads(
        (ROOT / "schemas/orchestration/remaining-work-launch-pack.schema.json").read_text()
    )
    assert "launch_bootstrap" in schema["required"]
    props = schema["properties"]["launch_bootstrap"]["properties"]
    assert {"version", "sha256", "ref", "metadata_ref", "preflight_script_ref"} <= set(props)


def test_first_real_launch_pack_binds_bootstrap_v2_and_copy_ready_prompts():
    pack_path = ROOT / ".orchestration/remaining-work/launch-packs/batch-001/manifest.json"
    pack = json.loads(pack_path.read_text())
    bootstrap = pack["launch_bootstrap"]
    assert bootstrap["version"] == "launch-bootstrap-v2.0.2"
    assert bootstrap["metadata_ref"].endswith("launch-bootstrap-v2.0.2.json")
    bootstrap_text = (ROOT / bootstrap["ref"]).read_text()
    assert hashlib.sha256((ROOT / bootstrap["ref"]).read_bytes()).hexdigest() == bootstrap["sha256"]
    for entry in pack["entries"]:
        prompt = (pack_path.parent / entry["prompt_ref"]).read_text()
        assert "## Launch Bootstrap v2" in prompt
        assert bootstrap_text in prompt
        assert prompt.index("## Launch Bootstrap v2") < prompt.index("## Launch Overlay")

def test_launch_pack_verifier_rejects_bootstrap_hash_mismatch(tmp_path):
    a = valid_atlas(tmp_path)
    write_json(tmp_path, ATLAS_REL, a)
    template = tmp_path / ".orchestration/remaining-work/prompts/_template"
    template.mkdir(parents=True)
    bootstrap_text = "# Launch Bootstrap v2\n"
    bootstrap_ref = ".orchestration/remaining-work/prompts/_template/launch-bootstrap-v2.md"
    (tmp_path / bootstrap_ref).write_text(bootstrap_text)
    meta_ref = ".orchestration/remaining-work/prompts/_template/launch-bootstrap-v2.json"
    write_json(tmp_path, meta_ref, {
        "schema_version": "remaining-work-launch-bootstrap.v2",
        "version": "launch-bootstrap-v2.0.3",
        "sha256": "0" * 64,
        "ref": bootstrap_ref,
        "preflight_script_ref": "scripts/preflight-remaining-work-launch.py",
        "verified_superpowers_skills": ["using-superpowers"],
    })
    lp = write_json(
        tmp_path,
        ".orchestration/remaining-work/launch-packs/batch-bootstrap/manifest.json",
        {
            "schema_version": "remaining-work-launch-pack.v1",
            "batch_id": "batch-bootstrap",
            "generated_at_head": "c" * 40,
            "launch_bootstrap": {
                "version": "launch-bootstrap-v2.0.3",
                "sha256": "0" * 64,
                "ref": bootstrap_ref,
                "metadata_ref": meta_ref,
                "preflight_script_ref": "scripts/preflight-remaining-work-launch.py",
            },
            "entries": [{"task_id": "H3-A"}],
        },
    )
    p = run_verify(tmp_path, "--launch-pack", str(lp))
    assert p.returncode == 2
    assert "launch bootstrap hash mismatch" in p.stderr


def _write_exact_overlay_for_launch_prompt(root: Path, task_id: str, base_sha: str):
    ref = f".orchestration/remaining-work/prompts/{task_id}/overlay.json"
    payload = {
        "schema_version": "remaining-work-launch-overlay.v1",
        "task_id": task_id,
        "version": f"{task_id.lower()}-overlay-v1",
        "base_sha": base_sha,
        "dependency_heads": {},
        "branch": f"execution/{task_id.lower()}",
        "worktree": None,
        "open_problem_ids": [],
        "contract_deltas": [],
        "resource_leases": {"LIGHTWEIGHT_CPU_TEST": 16},
        "resolved_model_identity": "gpt-5.6-luna | reasoning=medium | family=LUNA",
        "reconciled_at_head": base_sha,
    }
    write_json(root, ref, payload)
    return ref, payload


def _write_launch_prompt_fixture(root: Path, *, stale_core=False, stale_overlay=False):
    a = valid_atlas(root)
    write_json(root, ATLAS_REL, a)
    bootstrap = write_test_launch_bootstrap(root)
    node_a = a["nodes"][1]
    core_ref = node_a["prompt_core_ref"]
    core_text = (root / core_ref).read_text()
    overlay_ref, overlay = _write_exact_overlay_for_launch_prompt(root, "H3-A", "c" * 40)
    node_a["overlay_ref"] = overlay_ref
    write_json(root, ATLAS_REL, a)
    embedded_core = core_text + ("STALE\n" if stale_core else "")
    embedded_overlay = dict(overlay)
    if stale_overlay:
        embedded_overlay["branch"] = "execution/stale"
    prompt_rel = "prompts/01-H3-A.md"
    pack_dir = root / ".orchestration/remaining-work/launch-packs/batch-exact"
    prompt_path = pack_dir / prompt_rel
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    bootstrap_text = (root / bootstrap["ref"]).read_text()
    prompt_path.write_text(
        "# H3-A\n\n"
        "## Launch Bootstrap v2\n\n"
        + bootstrap_text.rstrip()
        + "\n\n## Launch Overlay\n\n"
        + json.dumps(embedded_overlay, indent=2, sort_keys=True)
        + "\n\n## Frozen Core\n\n"
        + embedded_core
    )
    pack = write_json(
        root,
        ".orchestration/remaining-work/launch-packs/batch-exact/manifest.json",
        {
            "schema_version": "remaining-work-launch-pack.v1",
            "batch_id": "batch-exact",
            "generated_at_head": "c" * 40,
            "launch_bootstrap": bootstrap,
            "entries": [{
                "task_id": "H3-A",
                "label": "H3-A",
                "lane": "BUILD",
                "state": "READY",
                "write_mode": "WRITE",
                "prompt_ref": prompt_rel,
                "core_ref": core_ref,
                "overlay_ref": overlay_ref,
                "executor_mode": "PARALLEL_PORTFOLIO",
                "resource_class": "LIGHTWEIGHT_CPU_TEST",
            }],
        },
    )
    return pack


def test_launch_pack_verifier_rejects_stale_embedded_core(tmp_path):
    lp = _write_launch_prompt_fixture(tmp_path, stale_core=True)
    p = run_verify(tmp_path, "--launch-pack", str(lp))
    assert p.returncode == 2
    assert "launch prompt core mismatch for H3-A" in p.stderr


def test_launch_pack_verifier_rejects_stale_embedded_overlay(tmp_path):
    lp = _write_launch_prompt_fixture(tmp_path, stale_overlay=True)
    p = run_verify(tmp_path, "--launch-pack", str(lp))
    assert p.returncode == 2
    assert "launch prompt overlay mismatch for H3-A" in p.stderr
