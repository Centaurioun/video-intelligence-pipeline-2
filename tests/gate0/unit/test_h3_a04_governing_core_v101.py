"""Synthetic-only governing A04 Option B core integrity tests; never execute codesign."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROMPTS = ROOT / ".orchestration/remaining-work/prompts/H3-A04"
DECISION = ROOT / "docs/decisions/2026-10-26-h3-a04-option-b-owner-adoption-v101.md"
OLD_SHA = "39c408208c547b03c2b997310c573e748a2bf285b3fc24aa473d99b5eadf5eca"

def test_a04_old_frozen_core_remains_byte_identical():
    assert hashlib.sha256((PROMPTS / "core.md").read_bytes()).hexdigest() == OLD_SHA
    assert json.loads((PROMPTS / "core.json").read_text())["prompt_core"]["version"] == "h3-a04-core-v1.0.0"

def test_a04_option_b_core_integrity_and_exact_one_shot_semantics():
    content = (PROMPTS / "v1.0.1/core.md").read_bytes()
    meta = json.loads((PROMPTS / "v1.0.1/core.json").read_text())
    assert meta["task_id"] == "H3-A04"
    assert meta["prompt_core"]["version"] == "h3-a04-core-v1.0.1"
    assert meta["prompt_core"]["sha256"] == hashlib.sha256(content).hexdigest()
    core = content.decode()
    for predicate in ("_run_codesign_entitlements(application)", "CompletedProcess[bytes]",
                      "exactly once", "N4ABoundaryPrimitive", "signer_entitlements_octets",
                      "renderer_input_octets", "N4ASealHandoff.measured_primitive",
                      "N4AProductionResult.primitive", "same Python object",
                      "No second primitive constructor"):
        assert predicate.lower() in core.lower()
    assert "sole primitive producer and executes exactly once" not in core

def test_a04_owner_adopted_contract_but_did_not_authorize_source_execution():
    decision = DECISION.read_text()
    assert "ADOPTED — GOVERNING CONTRACT INTERPRETATION ONLY" in decision
    assert "TASK-6 IMPLEMENTATION NOT_AUTHORIZED" in decision
    assert "single boundary measurement-and-primitive-production flow" in decision
    assert "Task-3" in decision
