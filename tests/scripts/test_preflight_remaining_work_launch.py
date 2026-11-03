from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "preflight-remaining-work-launch.py"


def load_mod():
    spec = importlib.util.spec_from_file_location("preflight_remaining_work_launch", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(repo: Path, *args: str, check=True):
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        capture_output=True,
        check=check,
    )


def make_packet_repo(tmp_path, *, open_problems=None, bad_contract=False, relevant_delta=False):
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test User")

    core_ref = ".orchestration/remaining-work/prompts/H3-X01/core.md"
    core = repo / core_ref
    core.parent.mkdir(parents=True)
    core_text = "# H3-X01\nDo bounded work.\n"
    core.write_text(core_text)
    digest = hashlib.sha256(core_text.encode()).hexdigest()
    prompt_core = {
        "version": "h3-x01-core-v1.0.0",
        "sha256": digest,
        "goal": "Do bounded work.",
        "dependencies": [],
        "expected_deliverables": ["bounded result"],
        "read_scope": [
            "AGENTS.md",
            ".orchestration/remaining-work/CONTROLLER_START_HERE.md",
            ".orchestration/remaining-work/atlas/atlas.json",
            "src/task.py",
        ],
        "write_domain": ["src/task.py"],
        "consumed_contracts": [{"id": "contract_x", "fingerprint": "a" * 40}],
        "prohibited_scope": ["canonical-main integration"],
        "focused_tests": ["pytest -q"],
        "verification_hooks": ["verification-before-completion"],
        "h4_decomposition_guidance": ["one writer"],
        "parallelism_contract": [
            "DISPATCH_INDEPENDENT_H4_CONCURRENTLY",
            "ROOT_IS_CONTROL_PLANE",
            "RECYCLE_TERMINAL_CHILD_SLOTS",
            "EXCLUSIVE_WRITER_OWNERSHIP",
            "ASYNC_FEATURE_REVIEW_ON_VERIFY_FRONTIER",
            "VERIFY_DOES_NOT_BLOCK_UNRELATED_BUILD",
            "NO_STOCK_SUBAGENT_DRIVEN_DEVELOPMENT_DEFAULT",
        ],
        "failure_policy": {"systematic_debugging_on_unexpected_failure": True},
        "receipt_contract": {"required_fields": ["TASK"]},
        "executor_mode": "PARALLEL_PORTFOLIO",
        "resource_class": "LIGHTWEIGHT_CPU_TEST",
    }
    core.with_name("core.json").write_text(json.dumps({
        "schema_version": "remaining-work-frozen-core.v1",
        "task_id": "H3-X01",
        "prompt_core": prompt_core,
    }))

    (repo / "src").mkdir()
    (repo / "src/task.py").write_text("VALUE=1\n")
    (repo / "AGENTS.md").write_text("authority\n")
    (repo / ".orchestration/remaining-work").mkdir(parents=True, exist_ok=True)
    (repo / ".orchestration/remaining-work/CONTROLLER_START_HERE.md").write_text("controller\n")
    (repo / ".orchestration/remaining-work/atlas").mkdir(parents=True, exist_ok=True)
    atlas = {
        "schema_version": "remaining-work-atlas.v1",
        "resource_leases": {"LIGHTWEIGHT_CPU_TEST": 16},
        "nodes": [{
            "id": "H3-X01",
            "level": "H3",
            "title": "X",
            "state": "READY",
            "dependencies": [],
            "candidate_generation": None,
            "problem_ids": open_problems or [],
            "write_domain": ["src/task.py"],
            "consumed_contracts": [{"id": "contract_x", "fingerprint": "a" * 40}],
            "executor_mode": "PARALLEL_PORTFOLIO",
            "resource_class": "LIGHTWEIGHT_CPU_TEST",
            "prompt_core_ref": core_ref,
            "prompt_core_sha256": digest,
            "overlay_ref": ".orchestration/remaining-work/prompts/H3-X01/overlay.json",
        }],
    }
    (repo / ".orchestration/remaining-work/atlas/atlas.json").write_text(json.dumps(atlas))
    fingerprint = "b" * 40 if bad_contract else "a" * 40
    (repo / ".orchestration/remaining-work/atlas/contract-registry.json").write_text(json.dumps({
        "entries": [{"id": "contract_x", "fingerprint": fingerprint, "kind": "GIT_COMMIT", "source": "test"}]
    }))
    (repo / ".orchestration/remaining-work/prompts/index.json").write_text(json.dumps({
        "entries": [{"task_id": "H3-X01", "sha256": digest}]
    }))

    git(repo, "add", ".")
    git(repo, "commit", "-m", "base")
    base = git(repo, "rev-parse", "HEAD").stdout.strip()

    if relevant_delta:
        (repo / "src/task.py").write_text("VALUE=2\n")
        git(repo, "add", "src/task.py")
        git(repo, "commit", "-m", "relevant change")

    overlay = core.with_name("overlay.json")
    overlay.write_text(json.dumps({
        "schema_version": "remaining-work-launch-overlay.v1",
        "task_id": "H3-X01",
        "version": "x-overlay-v1",
        "base_sha": base,
        "dependency_heads": {},
        "branch": "execution/h3-x01",
        "worktree": None,
        "open_problem_ids": open_problems or [],
        "contract_deltas": [],
        "resource_leases": {"LIGHTWEIGHT_CPU_TEST": 16},
        "resolved_model_identity": "gpt-5.6-luna | reasoning=medium | family=LUNA",
        "reconciled_at_head": base,
    }))
    git(repo, "add", str(overlay.relative_to(repo)))
    git(repo, "commit", "-m", "overlay")
    return repo, overlay.relative_to(repo), base


def test_packet_preflight_passes_descendant_main_with_only_launch_metadata(tmp_path):
    m = load_mod()
    repo, overlay, base = make_packet_repo(tmp_path)
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "PASS"
    assert got["base_sha"] == base
    assert got["workspace_action"] == "CREATE_ISOLATED_WORKTREE"


def test_packet_preflight_rejects_task_relevant_main_delta_as_stale(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path, relevant_delta=True)
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "STALE_IN_FLIGHT"
    assert any("task_relevant_main_delta" in p for p in got["problems"])


def test_packet_preflight_rejects_contract_fingerprint_drift(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path, bad_contract=True)
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "DIRTY_BY_CONTRACT_DELTA"


def test_packet_preflight_requires_node_overlay_ref(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    atlas["nodes"][0].pop("overlay_ref")
    atlas_path.write_text(json.dumps(atlas))
    git(repo, "add", ".orchestration/remaining-work/atlas/atlas.json")
    git(repo, "commit", "-m", "drop overlay ref")

    got = m.packet_preflight(repo, "H3-X01", overlay)

    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "BLOCKED"
    assert "overlay_ref_mismatch" in got["problems"]


def test_packet_preflight_requires_supplied_overlay_to_match_atlas_overlay_ref(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    other_overlay = repo / ".orchestration/remaining-work/prompts/H3-X01/overlay-other.json"
    other_overlay.write_text((repo / overlay).read_text())
    git(repo, "add", str(other_overlay.relative_to(repo)))
    git(repo, "commit", "-m", "add alternate overlay")

    got = m.packet_preflight(repo, "H3-X01", other_overlay.relative_to(repo))

    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "BLOCKED"
    assert "overlay_ref_mismatch" in got["problems"]


def _authorize_fixture_transition(repo: Path, overlay_ref: Path, base: str, *, bad_output=False):
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    node = atlas["nodes"][0]
    candidate_blob = git(repo, "rev-parse", f"{base}:src/task.py").stdout.strip()
    node.update({
        "state": "VERIFY_READY",
        "candidate_generation": {
            "sha": base,
            "tree": git(repo, "rev-parse", f"{base}^{{tree}}").stdout.strip(),
            "prompt_core_version": "h3-x01-core-v1.0.0",
            "overlay_version": "x-overlay-v1",
            "contract_fingerprints": {"contract_x": "a" * 40},
        },
        "produced_contracts": [{
            "id": "contract_x",
            "fingerprint": ("c" * 40) if bad_output else candidate_blob,
        }],
    })
    atlas_path.write_text(json.dumps(atlas))
    registry_path = repo / ".orchestration/remaining-work/atlas/contract-registry.json"
    registry_path.write_text(json.dumps({
        "entries": [{
            "id": "contract_x",
            "fingerprint": candidate_blob,
            "kind": "GIT_BLOB",
            "source": f"src/task.py@{base}",
        }]
    }))
    return candidate_blob


def test_packet_preflight_accepts_exact_producer_self_transition(tmp_path):
    m = load_mod()
    repo, overlay, base = make_packet_repo(tmp_path)
    _authorize_fixture_transition(repo, overlay, base)
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "PASS"
    assert got["checks"]["contract_fingerprints"] == "MATCH"


def test_packet_preflight_rejects_producer_claim_not_matching_candidate_blob(tmp_path):
    m = load_mod()
    repo, overlay, base = make_packet_repo(tmp_path)
    _authorize_fixture_transition(repo, overlay, base, bad_output=True)
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "DIRTY_BY_CONTRACT_DELTA"
    assert "produced_contract_fingerprint_mismatch" in got["problems"]


def test_packet_preflight_rejects_open_problem_before_build(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path, open_problems=["P-1"])
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "BLOCKED"
    assert "open_problems_present" in got["problems"]


def _require_fixture_authority(
    repo: Path, overlay_ref: Path, *, authorized_task_id="H3-X01"
):
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    node = atlas["nodes"][0]
    node["implementation_authorization_required"] = True
    record_rel = "docs/agent-runs/run-test/owner-implementation-authorization.json"
    record_path = repo / record_rel
    record_path.parent.mkdir(parents=True, exist_ok=True)
    core_path = repo / node["prompt_core_ref"]
    core_json = json.loads(core_path.with_name("core.json").read_text())
    authority_paths = {
        "task4_amendment": "docs/superpowers/specs/2026-10-02-g0-task4-post-task3-successor-amendment.md",
        "successor_spec": "docs/superpowers/specs/2026-09-27-g0-v7-task9-projection-dataflow-successor-spec.md",
        "successor_implementation_plan": "docs/superpowers/plans/2026-09-27-g0-v7-task9-projection-dataflow-successor-implementation-plan.md",
    }
    authority_refs = {}
    authority_blobs = {}
    for key, rel in authority_paths.items():
        source = repo / rel
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(f"historical authority {key}\n")
        blob = git(repo, "hash-object", "-w", str(source)).stdout.strip()
        authority_blobs[key] = blob
    git(repo, "add", *authority_paths.values())
    git(repo, "commit", "-m", "test authority source blobs")
    verified_at_commit = git(repo, "rev-parse", "HEAD").stdout.strip()
    authority_refs = {
        key: {"path": rel, "blob": authority_blobs[key], "verified_at_commit": verified_at_commit}
        for key, rel in authority_paths.items()
    }
    governing = {
        "gate0_task4_successor_amendment": authority_blobs["task4_amendment"],
        "gate0_projection_successor_spec": authority_blobs["successor_spec"],
        "gate0_projection_successor_plan": authority_blobs["successor_implementation_plan"],
    }
    node["consumed_contracts"].extend(
        {"id": key, "fingerprint": value} for key, value in governing.items()
    )
    core_json["prompt_core"]["consumed_contracts"] = node["consumed_contracts"]
    core_json_path = core_path.with_name("core.json")
    core_json_path.write_text(json.dumps(core_json))
    registry_path = repo / ".orchestration/remaining-work/atlas/contract-registry.json"
    registry = json.loads(registry_path.read_text())
    registry["entries"].extend(
        {"id": key, "fingerprint": value, "kind": "GIT_COMMIT", "source": "test"}
        for key, value in governing.items()
    )
    registry_path.write_text(json.dumps(registry))
    record = {
        "schema_version": "owner-implementation-authorization.v1",
        "effective_date": "2026-10-03",
        "status": "AUTHORIZED_FOR_IMPLEMENTATION_AND_TEST_EXECUTION",
        "historical_state": "Tasks 4–12 were PARKED / NOT AUTHORIZED before this ruling.",
        "supersession": {
            "forward_only": True,
            "non_retroactive": True,
            "does_not_rewrite_historical_records": True,
        },
        "authority_inputs": authority_refs,
        "scope": {
          "operation_classes": ["IMPLEMENTATION_AND_TEST_EXECUTION"],
          "frozen_cores": {
            authorized_task_id: {
                "version": core_json["prompt_core"]["version"],
                "core_md_sha256": hashlib.sha256(core_path.read_bytes()).hexdigest(),
                "core_json_sha256": hashlib.sha256(core_json_path.read_bytes()).hexdigest(),
            }
          },
        },
        "exclusions": ["PROTECTED_MEDIA", "PROVIDER", "PRODUCTION", "GATE_PROMOTION"],
    }
    record_path.write_text(json.dumps(record, sort_keys=True) + "\n")
    auth_ref = {
        "path": record_rel,
        "sha256": hashlib.sha256(record_path.read_bytes()).hexdigest(),
    }
    node["implementation_authorization_ref"] = auth_ref
    atlas_path.write_text(json.dumps(atlas))
    overlay_path = repo / overlay_ref
    overlay = json.loads(overlay_path.read_text())
    overlay["implementation_authorization_ref"] = auth_ref
    overlay["requested_operation_class"] = "IMPLEMENTATION_AND_TEST_EXECUTION"
    overlay_path.write_text(json.dumps(overlay))
    return record_path


def test_packet_preflight_refuses_historical_no_authorization(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    atlas["nodes"][0]["implementation_authorization_required"] = True
    atlas["nodes"][0]["historical_implementation_authority"] = "PARKED / NOT AUTHORIZED"
    atlas_path.write_text(json.dumps(atlas))
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "BLOCKED"
    assert "implementation_authorization_ref_missing" in got["problems"]


def test_packet_preflight_accepts_later_exact_task_core_authorization(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    _require_fixture_authority(repo, overlay)
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "PASS"
    assert got["checks"]["implementation_authority"] == "MATCH"


def test_packet_preflight_rejects_semantically_changed_frozen_core(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    _require_fixture_authority(repo, overlay)
    core_path = repo / ".orchestration/remaining-work/prompts/H3-X01/core.md"
    core_path.write_text(core_path.read_text() + "Changed authority scope.\n")
    digest = hashlib.sha256(core_path.read_bytes()).hexdigest()
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    atlas["nodes"][0]["prompt_core_sha256"] = digest
    atlas_path.write_text(json.dumps(atlas))
    idx_path = repo / ".orchestration/remaining-work/prompts/index.json"
    idx = json.loads(idx_path.read_text())
    idx["entries"][0]["sha256"] = digest
    idx_path.write_text(json.dumps(idx))
    core_json_path = core_path.with_name("core.json")
    core_json = json.loads(core_json_path.read_text())
    core_json["prompt_core"]["sha256"] = digest
    core_json_path.write_text(json.dumps(core_json))
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "BLOCKED"
    assert "implementation_authorization_core_mismatch" in got["problems"]


def test_packet_preflight_does_not_extend_authority_to_unrelated_task(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    _require_fixture_authority(repo, overlay, authorized_task_id="H3-B01")
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert "implementation_authorization_task_not_covered" in got["problems"]


def test_packet_preflight_does_not_extend_authority_to_excluded_operation(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    _require_fixture_authority(repo, overlay)
    got = m.packet_preflight(
        repo, "H3-X01", overlay, operation_class="PROTECTED_MEDIA_EXECUTION"
    )
    assert got["status"] == "FAIL"
    assert "implementation_authorization_operation_not_covered" in got["problems"]


def test_packet_preflight_leaves_historical_amendment_unchanged(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    _require_fixture_authority(repo, overlay)
    historical = repo / "docs/superpowers/specs/2026-10-02-g0-task4-post-task3-successor-amendment.md"
    before = historical.read_bytes()
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "PASS"
    assert historical.read_bytes() == before


@pytest.mark.parametrize(
    ("path", "malformed"),
    [
        (("supersession",), "invalid"),
        (("authority_inputs", "task4_amendment"), ["invalid"]),
    ],
)
def test_packet_preflight_structures_malformed_authority_records_as_blocked(
    tmp_path, path, malformed
):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    record_path = _require_fixture_authority(repo, overlay)
    record = json.loads(record_path.read_text())
    target = record
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = malformed
    record_path.write_text(json.dumps(record, sort_keys=True) + "\n")
    auth_ref = {
        "path": str(record_path.relative_to(repo)),
        "sha256": hashlib.sha256(record_path.read_bytes()).hexdigest(),
    }
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    atlas["nodes"][0]["implementation_authorization_ref"] = auth_ref
    atlas_path.write_text(json.dumps(atlas))
    overlay_data = json.loads((repo / overlay).read_text())
    overlay_data["implementation_authorization_ref"] = auth_ref
    (repo / overlay).write_text(json.dumps(overlay_data))

    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "BLOCKED"
    assert "implementation_authorization_record_invalid" in got["problems"]


def test_workspace_preflight_rejects_dirty_isolated_worktree_without_cleanup(tmp_path):
    m = load_mod()
    repo, overlay, base = make_packet_repo(tmp_path)
    wt = tmp_path / "wt"
    git(repo, "worktree", "add", "-b", "execution/h3-x01", str(wt), base)
    (wt / "dirty.txt").write_text("do not delete")
    got = m.workspace_preflight(repo, "H3-X01", overlay, wt)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "BLOCKED"
    assert "worktree_not_clean" in got["problems"]
    assert (wt / "dirty.txt").exists()


def test_bootstrap_metadata_names_exact_verified_superpowers_skills():
    meta = json.loads(
        (ROOT / ".orchestration/remaining-work/prompts/_template/launch-bootstrap-v2.json").read_text()
    )
    text = (
        ROOT / ".orchestration/remaining-work/prompts/_template/launch-bootstrap-v2.md"
    ).read_text()
    expected = {
        "using-superpowers",
        "using-git-worktrees",
        "dispatching-parallel-agents",
        "test-driven-development",
        "systematic-debugging",
        "verification-before-completion",
        "requesting-code-review",
        "receiving-code-review",
    }
    assert set(meta["verified_superpowers_skills"]) == expected
    for skill in expected:
        assert skill in text
    assert meta["forbidden_default_skill"] == "subagent-driven-development"
    assert "PER_TASK_REVIEW_REQUIRED" in text


def test_packet_preflight_rejects_core_hash_drift_before_build(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    core = repo / ".orchestration/remaining-work/prompts/H3-X01/core.md"
    core.write_text(core.read_text() + "drift\n")
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "DIRTY_BY_CONTRACT_DELTA"
    assert "core_hash_mismatch" in got["problems"]


def test_packet_preflight_rejects_overlay_contract_delta_before_build(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    overlay_path = repo / overlay
    payload = json.loads(overlay_path.read_text())
    payload["contract_deltas"] = [{"contract_id": "contract_x", "reason": "changed"}]
    overlay_path.write_text(json.dumps(payload))
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "DIRTY_BY_CONTRACT_DELTA"
    assert "contract_deltas_present" in got["problems"]


def test_packet_preflight_rejects_valid_nonancestor_base_as_stale(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    tree = git(repo, "write-tree").stdout.strip()
    other = subprocess.run(
        ["git", "-C", str(repo), "commit-tree", tree],
        input="unrelated root\n",
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    overlay_path = repo / overlay
    payload = json.loads(overlay_path.read_text())
    payload["base_sha"] = other
    payload["reconciled_at_head"] = other
    overlay_path.write_text(json.dumps(payload))
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "STALE_IN_FLIGHT"
    assert "base_not_ancestor_of_current_main" in got["problems"]


def test_packet_preflight_rejects_dependency_head_mismatch_as_stale(tmp_path):
    m = load_mod()
    repo, overlay, base = make_packet_repo(tmp_path)
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    dep = {
        "id": "H3-Y01",
        "level": "H3",
        "title": "Y",
        "state": "BUILD_GREEN",
        "dependencies": [],
        "candidate_generation": {
            "sha": base,
            "tree": "b" * 40,
            "prompt_core_version": "y-core-v1",
            "overlay_version": "y-overlay-v1",
            "contract_fingerprints": {},
        },
        "write_domain": ["src/y.py"],
        "consumed_contracts": [],
        "executor_mode": "PARALLEL_PORTFOLIO",
        "resource_class": "LIGHTWEIGHT_CPU_TEST",
        "prompt_core_ref": None,
        "prompt_core_sha256": None,
    }
    atlas["nodes"].append(dep)
    atlas["nodes"][0]["dependencies"] = [
        {"node_id": "H3-Y01", "kind": "HARD_BUILD_DEPENDENCY"}
    ]
    atlas_path.write_text(json.dumps(atlas))
    core_meta_path = repo / ".orchestration/remaining-work/prompts/H3-X01/core.json"
    core_meta = json.loads(core_meta_path.read_text())
    core_meta["prompt_core"]["dependencies"] = atlas["nodes"][0]["dependencies"]
    core_meta_path.write_text(json.dumps(core_meta))
    overlay_path = repo / overlay
    payload = json.loads(overlay_path.read_text())
    payload["dependency_heads"] = {"H3-Y01": "0" * 40}
    overlay_path.write_text(json.dumps(payload))
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "STALE_IN_FLIGHT"
    assert "dependency_head_mismatch:H3-Y01" in got["problems"]


def test_packet_preflight_rejects_unsatisfied_dependency_state_before_build(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    atlas["nodes"].append({
        "id": "H3-Y01",
        "level": "H3",
        "title": "Y",
        "state": "PLANNED",
        "dependencies": [],
        "candidate_generation": None,
        "write_domain": ["src/y.py"],
        "consumed_contracts": [],
        "executor_mode": "PARALLEL_PORTFOLIO",
        "resource_class": "LIGHTWEIGHT_CPU_TEST",
        "prompt_core_ref": None,
        "prompt_core_sha256": None,
    })
    atlas["nodes"][0]["dependencies"] = [
        {"node_id": "H3-Y01", "kind": "HARD_BUILD_DEPENDENCY"}
    ]
    atlas_path.write_text(json.dumps(atlas))
    core_meta_path = repo / ".orchestration/remaining-work/prompts/H3-X01/core.json"
    core_meta = json.loads(core_meta_path.read_text())
    core_meta["prompt_core"]["dependencies"] = atlas["nodes"][0]["dependencies"]
    core_meta_path.write_text(json.dumps(core_meta))
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "BLOCKED"
    assert "dependency_not_ready:H3-Y01:HARD_BUILD_DEPENDENCY" in got["problems"]


def test_packet_preflight_rejects_atlas_problem_missing_from_overlay(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    atlas["nodes"][0]["problem_ids"] = ["P-current"]
    atlas_path.write_text(json.dumps(atlas))
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "BLOCKED"
    assert "problem_set_mismatch" in got["problems"]


def test_packet_preflight_rejects_resource_lease_drift(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    atlas["resource_leases"]["LIGHTWEIGHT_CPU_TEST"] = 8
    atlas_path.write_text(json.dumps(atlas))
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "BLOCKED"
    assert "resource_lease_mismatch:LIGHTWEIGHT_CPU_TEST" in got["problems"]


def test_packet_preflight_prefers_fresh_origin_main_when_local_main_is_behind(tmp_path):
    m = load_mod()
    repo, overlay, _ = make_packet_repo(tmp_path)
    local_main = git(repo, "rev-parse", "main").stdout.strip()
    tree = git(repo, "write-tree").stdout.strip()
    remote_main = subprocess.run(
        ["git", "-C", str(repo), "commit-tree", tree, "-p", local_main],
        input="remote metadata descendant\n",
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    git(repo, "update-ref", "refs/remotes/origin/main", remote_main)
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "PASS"
    assert got["checks"]["current_main_ref"] == "origin/main"
    assert got["current_main_sha"] == remote_main


def test_workspace_preflight_rechecks_packet_state_after_worktree_creation(tmp_path):
    m = load_mod()
    repo, overlay, base = make_packet_repo(tmp_path)
    wt = tmp_path / "wt-recheck"
    git(repo, "worktree", "add", "-b", "execution/h3-x01", str(wt), base)
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    atlas["nodes"][0]["problem_ids"] = ["P-after-packet"]
    atlas_path.write_text(json.dumps(atlas))
    got = m.workspace_preflight(repo, "H3-X01", overlay, wt)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "BLOCKED"
    assert "problem_set_mismatch" in got["problems"]


def _add_materializable_dependency(repo: Path, overlay: Path, base: str, *, candidate_sha: str | None = None):
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    if candidate_sha is None:
        tree = git(repo, "rev-parse", f"{base}^{{tree}}").stdout.strip()
        candidate_sha = subprocess.run(
            ["git", "-C", str(repo), "commit-tree", tree, "-p", base],
            input="dependency candidate\n",
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
    else:
        tree = "b" * 40
    dep = {
        "id": "H3-Y01",
        "level": "H3",
        "title": "Y",
        "state": "BUILD_GREEN",
        "dependencies": [],
        "candidate_generation": {
            "sha": candidate_sha,
            "tree": tree,
            "prompt_core_version": "y-core-v1",
            "overlay_version": "y-overlay-v1",
            "contract_fingerprints": {},
        },
        "problem_ids": [],
        "write_domain": ["src/y.py"],
        "consumed_contracts": [],
        "executor_mode": "PARALLEL_PORTFOLIO",
        "resource_class": "LIGHTWEIGHT_CPU_TEST",
        "prompt_core_ref": None,
        "prompt_core_sha256": None,
    }
    atlas["nodes"].append(dep)
    atlas["nodes"][0]["dependencies"] = [
        {"node_id": "H3-Y01", "kind": "HARD_BUILD_DEPENDENCY"}
    ]
    atlas_path.write_text(json.dumps(atlas))
    core_meta_path = repo / ".orchestration/remaining-work/prompts/H3-X01/core.json"
    core_meta = json.loads(core_meta_path.read_text())
    core_meta["prompt_core"]["dependencies"] = atlas["nodes"][0]["dependencies"]
    core_meta_path.write_text(json.dumps(core_meta))
    overlay_path = repo / overlay
    payload = json.loads(overlay_path.read_text())
    payload["dependency_heads"] = {"H3-Y01": candidate_sha}
    overlay_path.write_text(json.dumps(payload))
    return candidate_sha


def test_packet_preflight_rejects_dependency_commit_missing_locally(tmp_path):
    m = load_mod()
    repo, overlay, base = make_packet_repo(tmp_path)
    missing = "d" * 40
    _add_materializable_dependency(repo, overlay, base, candidate_sha=missing)
    got = m.packet_preflight(repo, "H3-X01", overlay)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "BLOCKED"
    assert "dependency_commit_missing:H3-Y01" in got["problems"]


def test_workspace_preflight_requires_exact_dependency_head_materialized(tmp_path):
    m = load_mod()
    repo, overlay, base = make_packet_repo(tmp_path)
    dependency_sha = _add_materializable_dependency(repo, overlay, base)
    wt = tmp_path / "wt-dependency"
    git(repo, "worktree", "add", "-b", "execution/h3-x01", str(wt), base)

    before = m.workspace_preflight(repo, "H3-X01", overlay, wt)
    assert before["status"] == "FAIL"
    assert before["recommended_state"] == "STALE_IN_FLIGHT"
    assert "dependency_not_materialized:H3-Y01" in before["problems"]

    git(wt, "merge", "--no-ff", "--no-edit", dependency_sha)
    after = m.workspace_preflight(repo, "H3-X01", overlay, wt)
    assert after["status"] == "PASS"
    assert after["checks"]["dependency_materialization"] == {"H3-Y01": dependency_sha}


def _promote_fixture_to_verify(repo: Path, candidate_sha: str):
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    atlas["nodes"][0]["state"] = "VERIFY_READY"
    atlas["nodes"][0]["candidate_generation"] = {
        "sha": candidate_sha,
        "tree": git(repo, "rev-parse", f"{candidate_sha}^{{tree}}").stdout.strip(),
        "prompt_core_version": "h3-x01-core-v1.0.0",
        "overlay_version": "x-overlay-v1",
        "contract_fingerprints": {"contract_x": "a" * 40},
    }
    atlas_path.write_text(json.dumps(atlas))


def _make_diverged_verify_topology(repo: Path, overlay: Path, initial_base: str):
    """Build canonical-main/base and candidate histories with a shared ancestor."""
    # The overlay base is advanced on canonical main, while a dependency and
    # its candidate are committed on a sibling history from the shared ancestor.
    (repo / "src/task.py").write_text("VALUE=2\n")
    git(repo, "add", "src/task.py")
    git(repo, "commit", "-m", "canonical main overlay base")
    overlay_base = git(repo, "rev-parse", "HEAD").stdout.strip()

    dependency_tree = git(repo, "rev-parse", f"{initial_base}^{{tree}}").stdout.strip()
    dependency_sha = subprocess.run(
        ["git", "-C", str(repo), "commit-tree", dependency_tree, "-p", initial_base],
        input="dependency candidate\n",
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    candidate_sha = subprocess.run(
        ["git", "-C", str(repo), "commit-tree", dependency_tree, "-p", dependency_sha],
        input="verify candidate\n",
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()

    dependency = {
        "id": "H3-Y01",
        "level": "H3",
        "title": "Y",
        "state": "BUILD_GREEN",
        "dependencies": [],
        "candidate_generation": {
            "sha": dependency_sha,
            "tree": dependency_tree,
            "prompt_core_version": "y-core-v1",
            "overlay_version": "y-overlay-v1",
            "contract_fingerprints": {},
        },
        "problem_ids": [],
        "write_domain": ["src/y.py"],
        "consumed_contracts": [],
        "executor_mode": "PARALLEL_PORTFOLIO",
        "resource_class": "LIGHTWEIGHT_CPU_TEST",
        "prompt_core_ref": None,
        "prompt_core_sha256": None,
    }
    dependency_edge = [{"node_id": "H3-Y01", "kind": "HARD_BUILD_DEPENDENCY"}]
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    atlas["nodes"][0]["dependencies"] = dependency_edge
    atlas["nodes"].append(dependency)
    atlas_path.write_text(json.dumps(atlas))

    core_meta_path = repo / ".orchestration/remaining-work/prompts/H3-X01/core.json"
    core_meta = json.loads(core_meta_path.read_text())
    core_meta["prompt_core"]["dependencies"] = dependency_edge
    core_meta_path.write_text(json.dumps(core_meta))

    payload = json.loads((repo / overlay).read_text())
    payload["base_sha"] = overlay_base
    payload["dependency_heads"] = {"H3-Y01": dependency_sha}
    (repo / overlay).write_text(json.dumps(payload))
    _promote_fixture_to_verify(repo, candidate_sha)

    # Persist only launch-control metadata on canonical main after the frozen base.
    git(repo, "add", ".orchestration/remaining-work")
    git(repo, "commit", "-m", "record verify candidate metadata")
    return overlay_base, dependency_sha, candidate_sha


def test_workspace_preflight_verify_accepts_detached_exact_candidate(tmp_path):
    m = load_mod()
    repo, overlay, base = make_packet_repo(tmp_path)
    _promote_fixture_to_verify(repo, base)
    wt = tmp_path / "wt-verify-exact"
    git(repo, "worktree", "add", "--detach", str(wt), base)
    got = m.workspace_preflight(repo, "H3-X01", overlay, wt)
    assert got["status"] == "PASS"
    assert got["lane"] == "VERIFY"
    assert got["head_sha"] == base
    assert got["checks"]["candidate_generation"] == base


def test_workspace_preflight_verify_accepts_exact_candidate_diverged_from_overlay_base(tmp_path):
    m = load_mod()
    repo, overlay, initial_base = make_packet_repo(tmp_path)
    overlay_base, dependency_sha, candidate_sha = _make_diverged_verify_topology(
        repo, overlay, initial_base
    )

    assert git(repo, "merge-base", "--is-ancestor", overlay_base, "main", check=False).returncode == 0
    assert git(repo, "merge-base", "--is-ancestor", candidate_sha, overlay_base, check=False).returncode != 0
    assert git(repo, "merge-base", "--is-ancestor", dependency_sha, candidate_sha, check=False).returncode == 0

    wt = tmp_path / "wt-verify-diverged-exact"
    git(repo, "worktree", "add", "--detach", str(wt), candidate_sha)
    got = m.workspace_preflight(repo, "H3-X01", overlay, wt)

    assert got["status"] == "PASS", got
    assert got["lane"] == "VERIFY"
    assert got["head_sha"] == candidate_sha
    assert got["checks"]["candidate_generation"] == candidate_sha
    assert got["checks"]["dependency_materialization"] == {"H3-Y01": dependency_sha}


def test_workspace_preflight_verify_rejects_exact_candidate_missing_dependency_ancestry(tmp_path):
    m = load_mod()
    repo, overlay, base = make_packet_repo(tmp_path)
    dependency_sha = _add_materializable_dependency(repo, overlay, base)
    _promote_fixture_to_verify(repo, base)
    wt = tmp_path / "wt-verify-missing-dependency"
    git(repo, "worktree", "add", "--detach", str(wt), base)

    got = m.workspace_preflight(repo, "H3-X01", overlay, wt)

    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "STALE_IN_FLIGHT"
    assert f"dependency_not_materialized:H3-Y01" in got["problems"]
    assert dependency_sha != base


def _create_sibling_commit(repo: Path, base: str) -> str:
    tree = git(repo, "rev-parse", f"{base}^{{tree}}").stdout.strip()
    return subprocess.run(
        ["git", "-C", str(repo), "commit-tree", tree],
        input="sibling candidate\n",
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def test_workspace_preflight_build_still_requires_overlay_base_ancestry(tmp_path):
    m = load_mod()
    repo, overlay, base = make_packet_repo(tmp_path)
    sibling = _create_sibling_commit(repo, base)
    wt = tmp_path / "wt-build-wrong-base"
    git(repo, "worktree", "add", "-b", "execution/h3-x01", str(wt), sibling)

    got = m.workspace_preflight(repo, "H3-X01", overlay, wt)

    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "STALE_IN_FLIGHT"
    assert "workspace_head_not_descendant_of_base" in got["problems"]


def test_workspace_preflight_repair_still_requires_overlay_base_ancestry(tmp_path):
    m = load_mod()
    repo, overlay, base = make_packet_repo(tmp_path)
    sibling = _create_sibling_commit(repo, base)
    atlas_path = repo / ".orchestration/remaining-work/atlas/atlas.json"
    atlas = json.loads(atlas_path.read_text())
    atlas["nodes"][0]["state"] = "REPAIRING"
    atlas["nodes"][0]["candidate_generation"] = {"sha": sibling}
    atlas_path.write_text(json.dumps(atlas))
    wt = tmp_path / "wt-repair-wrong-base"
    git(repo, "worktree", "add", "-b", "execution/h3-x01", str(wt), sibling)

    got = m.workspace_preflight(repo, "H3-X01", overlay, wt)

    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "STALE_IN_FLIGHT"
    assert "workspace_head_not_descendant_of_base" in got["problems"]


def test_workspace_preflight_verify_rejects_noncandidate_head(tmp_path):
    m = load_mod()
    repo, overlay, base = make_packet_repo(tmp_path)
    _promote_fixture_to_verify(repo, base)
    wrong = git(repo, "rev-parse", "HEAD").stdout.strip()
    assert wrong != base
    wt = tmp_path / "wt-verify-wrong"
    git(repo, "worktree", "add", "--detach", str(wt), wrong)
    got = m.workspace_preflight(repo, "H3-X01", overlay, wt)
    assert got["status"] == "FAIL"
    assert got["recommended_state"] == "STALE_IN_FLIGHT"
    assert "verify_head_not_exact_candidate" in got["problems"]
