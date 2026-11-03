"""Synthetic-only governing C05 successor contract integrity tests; no media/model work."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROMPTS = ROOT / ".orchestration/remaining-work/prompts/H3-C05"
DECISION = ROOT / "docs/decisions/2026-10-26-h3-c05-owner-adoption-v102.md"
OLD_SHA = "f1bf779439bb640a2411e73b11bbd35958371504922b4089e68495e196e38843"
FINGERPRINTS = {
    "vip_fvs_retrieval_adapter": "0f0268d83da4ff6c06c45ad54d85070071d6e155",
    "vip_fvs_coordinator": "1696b31afc58d83269389f025759b2ef7dba7670",
    "vip_fvs_semantic_index": "e81fd15ee243b59b02bace14131c9d6b39b66701",
    "canonical_contracts": "c0b665d70b311dd98b7ff9f4f564b2d5750ed17b",
}

def test_c05_old_frozen_core_remains_byte_identical():
    assert hashlib.sha256((PROMPTS / "v1.0.1/core.md").read_bytes()).hexdigest() == OLD_SHA
    assert json.loads((PROMPTS / "v1.0.1/core.json").read_text())["prompt_core"]["version"] == "h3-c05-core-v1.0.1"

def test_c05_adopted_core_is_digest_bound_and_consistent_with_producers():
    content = (PROMPTS / "v1.0.2/core.md").read_bytes()
    meta = json.loads((PROMPTS / "v1.0.2/core.json").read_text())
    assert meta["task_id"] == "H3-C05"
    assert meta["prompt_core"]["version"] == "h3-c05-core-v1.0.2"
    assert meta["prompt_core"]["sha256"] == hashlib.sha256(content).hexdigest()
    assert {entry["id"]: entry["fingerprint"] for entry in meta["prompt_core"]["consumed_contracts"]} == FINGERPRINTS

def test_c05_read_only_contract_and_restricted_authority():
    core = (PROMPTS / "v1.0.2/core.md").read_text()
    decision = DECISION.read_text()
    for condition in ("SemanticIndexEngine.query", "retrieve_multi_source", "retrieval_adapter.retrieve",
                      "source locator", "MATCHED", "binding_eligible=False",
                      "No source implementation", "No model timestamp promotion"):
        assert condition.lower() in (core + decision).lower()
    assert "SOURCE EXECUTION NOT_AUTHORIZED" in decision
    assert "NOT_OBSERVED" in core
    assert "C05 READY" in core or "C05 READY" in decision
