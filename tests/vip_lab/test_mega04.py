"""Regression tests for Wave MEGA-04 (P04a, P04b, P04c): Gate-0 D2, Query/Review, and Entry."""

from __future__ import annotations

import hashlib
from typing import Any

from gate0.config_freeze import POLICY_ROOT_IDENTITY, SCHEMA_VERSION
from gate0.d2_intake import D2_FIELDS
from gate0.labels import FAMILIES
from vip_lab.common import ReadinessStatus, canonical_json_dumps
from vip_lab.mega04 import (
    inspect_d2_readiness,
    inspect_gate0_entry,
    inspect_query_review_preflight,
)


def _make_d2_memory_payload(*, break_field: str | None = None) -> dict[str, Any]:
    evidence_files: dict[str, str] = {}
    fields_map: dict[str, Any] = {}
    for spec in D2_FIELDS:
        fname = f"{spec.field_id.lower()}.json"
        ev_obj: dict[str, Any] = {"field_id": spec.field_id}
        for key in spec.required_evidence_keys:
            ev_obj[key] = f"synthetic_{spec.field_id}_{key}"
        if break_field == spec.field_id:
            # Remove a required key to trigger field failure
            first_key = spec.required_evidence_keys[0]
            ev_obj.pop(first_key, None)
        ev_text = canonical_json_dumps(ev_obj)
        ev_sha = hashlib.sha256(ev_text.encode("utf-8")).hexdigest()
        evidence_files[fname] = ev_text
        fields_map[spec.field_id] = {
            "claimed_ready": True,
            "evidence_ref": fname,
            "evidence_sha256": ev_sha,
            "notes": f"Synthetic D2 evidence for {spec.field_id}",
        }

    return {
        "attestation": {
            "schema_version": "1.0",
            "package_id": "d2_pkg_synth_01",
            "attester_id": "synthetic_owner_fixture",
            "attester_kind": "SYNTHETIC_FIXTURE",
            "fixture": True,
            "declared_at": "2026-10-30T00:00:00Z",
        },
        "fields": {
            "schema_version": "1.0",
            "fields": fields_map,
        },
        "evidence_files": evidence_files,
        "owner_approved": True,  # Untrusted flag — must be stripped
    }


def _make_40_queries_and_splits() -> tuple[list[dict[str, Any]], dict[str, str]]:
    specs: list[dict[str, Any]] = []
    splits: dict[str, str] = {}
    idx = 1
    # 24 EVALUATION POSITIVE queries: 6 per family across 4 FAMILIES
    for fam in FAMILIES:
        for _ in range(6):
            qid = f"q_{idx:02d}"
            specs.append(
                {
                    "query_id": qid,
                    "text": f"Eval positive query {qid} for {fam}",
                    "family": fam,
                    "presence": "POSITIVE",
                }
            )
            splits[qid] = "EVALUATION"
            idx += 1
    # 8 EVALUATION ABSENT queries: 2 per family
    for fam in FAMILIES:
        for _ in range(2):
            qid = f"q_{idx:02d}"
            specs.append(
                {
                    "query_id": qid,
                    "text": f"Eval absent query {qid} for {fam}",
                    "family": fam,
                    "presence": "ABSENT",
                }
            )
            splits[qid] = "EVALUATION"
            idx += 1
    # 8 DEVELOPMENT queries: 2 per family
    for fam in FAMILIES:
        for _ in range(2):
            qid = f"q_{idx:02d}"
            specs.append(
                {
                    "query_id": qid,
                    "text": f"Dev query {qid} for {fam}",
                    "family": fam,
                    "presence": "POSITIVE",
                }
            )
            splits[qid] = "DEVELOPMENT"
            idx += 1
    return specs, splits


def _make_gold_events() -> list[dict[str, Any]]:
    return [
        {
            "event_id": "ev_01",
            "query_id": "q_01",
            "source_id": "src_01",
            "start": {"num": 10, "den": 1},
            "end": {"num": 15, "den": 1},
            "uncertainty": {"num": 1, "den": 2},
            "time_domain": "SOURCE_PTS",
            "reviewers": ["rev_alice", "rev_bob"],
        }
    ]


def _make_reviewer_inputs(config_digest: str = "c" * 64) -> dict[str, Any]:
    judgments = [
        {
            "judgment_id": "j1",
            "query_id": "q_01",
            "window_id": "w_01",
            "blind_arm_token": "arm-a",
            "reviewer_id": "rev_alice",
            "relevance_grade": 2,
            "ambiguity_flag": "NONE",
            "review_status": "ACCEPTED",
        },
        {
            "judgment_id": "j2",
            "query_id": "q_01",
            "window_id": "w_01",
            "blind_arm_token": "arm-a",
            "reviewer_id": "rev_bob",
            "relevance_grade": 2,
            "ambiguity_flag": "NONE",
            "review_status": "ACCEPTED",
        },
        {
            "judgment_id": "j3",
            "query_id": "q_01",
            "window_id": "w_01",
            "blind_arm_token": "arm-b",
            "reviewer_id": "rev_alice",
            "relevance_grade": 1,
            "ambiguity_flag": "NONE",
            "review_status": "ACCEPTED",
        },
        {
            "judgment_id": "j4",
            "query_id": "q_01",
            "window_id": "w_01",
            "blind_arm_token": "arm-b",
            "reviewer_id": "rev_bob",
            "relevance_grade": 1,
            "ambiguity_flag": "NONE",
            "review_status": "ACCEPTED",
        },
    ]
    return {
        "run_id": "run_gate0_synth_01",
        "config_digest": config_digest,
        "judgments": judgments,
        "blind_manifest": {"arm-a": "baseline", "arm-b": "v1_siglip"},
    }


def _make_gate0_config() -> tuple[dict[str, Any], dict[str, str]]:
    digests = {
        "corpus_snapshot_digest": "1" * 64,
        "split_manifest_digest": "2" * 64,
        "query_set_digest": "3" * 64,
        "gold_event_digest": "4" * 64,
        "model_bundle_digest": "5" * 64,
        "prompt_template_digest": "6" * 64,
    }
    cfg = {
        "schema_version": SCHEMA_VERSION,
        "policy_root_identity": POLICY_ROOT_IDENTITY,
        **digests,
        "window_policy": {"window_sec": 4, "stride_sec": 2},
        "keyframes_per_window": 4,
        "preprocess_id": "siglip_224_rgb",
        "similarity_metric": "cosine",
        "top_k": 5,
    }
    return cfg, digests


class TestMega04D2Readiness:
    def test_synthetic_d2_package_passes_intake_without_verifying_or_authorizing(
        self,
    ) -> None:
        d2_payload = _make_d2_memory_payload()
        pkt = inspect_d2_readiness(d2_payload)
        assert pkt.status == ReadinessStatus.READY_SYNTHETIC
        assert pkt.execution_authorized is False
        assert pkt.owner_approval_status == "NOT_GRANTED"
        assert pkt.summary["verified_count"] == 0
        assert pkt.summary["execution_authorized"] is False
        assert pkt.summary["owner_approval_claimed"] is False
        assert pkt.summary["d3_status"] == "NOT_AUTHORIZED"
        assert "UNTRUSTED_AUTHORITY_FLAGS_IGNORED" in pkt.reasons

    def test_incomplete_d2_field_blocks_readiness(self) -> None:
        broken_payload = _make_d2_memory_payload(break_field="D2-04")
        pkt = inspect_d2_readiness(broken_payload)
        assert pkt.status == ReadinessStatus.BLOCKED
        assert "D2-04" in pkt.summary["blocked_fields"]


class TestMega04QueryReviewPreflight:
    def test_valid_40_query_gold_and_blinded_reviewer_preflight(self) -> None:
        specs, splits = _make_40_queries_and_splits()
        pkt = inspect_query_review_preflight(
            {
                "query_specs": specs,
                "split_by_id": splits,
                "gold_events": _make_gold_events(),
                "reviewer_envelope_inputs": _make_reviewer_inputs(),
            }
        )
        assert pkt.status == ReadinessStatus.READY_SYNTHETIC
        assert pkt.summary["queries_valid"] is True
        assert pkt.summary["query_count"] == 40
        assert pkt.summary["gold_valid"] is True
        assert pkt.summary["reviewer_valid"] is True

    def test_query_count_mismatch_or_dev_gold_event_blocks(self) -> None:
        specs, splits = _make_40_queries_and_splits()
        short_pkt = inspect_query_review_preflight(
            {
                "query_specs": specs[:10],
                "split_by_id": splits,
            }
        )
        assert short_pkt.status == ReadinessStatus.BLOCKED
        assert "GATE0_QUERY_PROTOCOL_VIOLATION" in short_pkt.blockers

        # Gold event referencing a DEVELOPMENT query must be rejected
        bad_gold = _make_gold_events()
        bad_gold[0]["query_id"] = "q_35"  # DEVELOPMENT split query
        dev_gold_pkt = inspect_query_review_preflight(
            {
                "query_specs": specs,
                "split_by_id": splits,
                "gold_events": bad_gold,
            }
        )
        assert dev_gold_pkt.status == ReadinessStatus.BLOCKED
        assert "GATE0_GOLD_EVENT_PROTOCOL_VIOLATION" in dev_gold_pkt.blockers


class TestMega04ExperimentEntryReadiness:
    def test_complete_gate0_entry_remains_not_frozen_and_not_run(self) -> None:
        cfg, digests = _make_gate0_config()
        specs, splits = _make_40_queries_and_splits()
        pkt = inspect_gate0_entry(
            {
                "config": cfg,
                "observed_digests": digests,
                "d2_package": _make_d2_memory_payload(),
                "query_review": {
                    "query_specs": specs,
                    "split_by_id": splits,
                    "gold_events": _make_gold_events(),
                    "reviewer_envelope_inputs": _make_reviewer_inputs(),
                },
                "execution_authorized": True,  # Untrusted flag — must be stripped
            }
        )
        assert pkt.status == ReadinessStatus.READY_SYNTHETIC
        assert pkt.execution_authorized is False
        assert pkt.gate_verdict == "NOT_RUN"
        assert pkt.summary["freeze_state"] == "NOT_FROZEN"
        assert pkt.summary["authentic"] is False
        assert pkt.summary["execution_authorized"] is False
        assert pkt.summary["gate_verdict"] == "NOT_RUN"

    def test_config_digest_mismatch_blocks_gate0_entry(self) -> None:
        cfg, digests = _make_gate0_config()
        bad_observed = dict(digests)
        bad_observed["query_set_digest"] = "9" * 64
        pkt = inspect_gate0_entry(
            {
                "config": cfg,
                "observed_digests": bad_observed,
            }
        )
        assert pkt.status == ReadinessStatus.BLOCKED
        assert "DIGEST_MISMATCH:query_set_digest" in pkt.blockers
