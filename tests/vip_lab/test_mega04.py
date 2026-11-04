"""Regression tests for Wave MEGA-04 (P04a, P04b, P04c): Gate-0 D2, Query/Review, and Entry."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from gate0.canonical_json import canonical_bytes
from gate0.d2_intake import D2_FIELD_IDS, D2_PACKAGE_SCHEMA_VERSION
from gate0.identity import digest_bytes, digest_json
from gate0.labels import FAMILIES
from vip_lab.common import ReadinessStatus
from vip_lab.mega04 import (
    inspect_d2_readiness,
    inspect_gate0_entry,
    inspect_query_review_preflight,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config/gate0/default.json"


def _artifact_digest(doc: Mapping[str, Any] | dict[str, Any]) -> str:
    return hashlib.sha256(canonical_bytes(doc)).hexdigest()


def _make_d2_artifacts() -> dict[str, dict[str, Any]]:
    queries = []
    for family in FAMILIES:
        for index in range(6):
            queries.append(
                {
                    "query_id": f"q_eval_{family.lower()}_{index}",
                    "text": f"editor query {family} {index}",
                    "family": family,
                    "presence": "POSITIVE",
                    "split": "EVALUATION",
                }
            )
    for index in range(8):
        queries.append(
            {
                "query_id": f"q_eval_absent_{index}",
                "text": f"editor absent query {index}",
                "family": FAMILIES[index % 4],
                "presence": "ABSENT",
                "split": "EVALUATION",
            }
        )
    for index in range(8):
        queries.append(
            {
                "query_id": f"q_dev_{index}",
                "text": f"editor development query {index}",
                "family": FAMILIES[index % 4],
                "presence": "POSITIVE",
                "split": "DEVELOPMENT",
            }
        )

    sessions = 4
    revisions = 6
    total_minutes = 90
    corpus_designation = {
        "schema_version": "gate0.d2-corpus-designation.v1",
        "sessions": [
            {
                "session_id": f"sess_{idx}",
                "duration_minutes": total_minutes // sessions,
            }
            for idx in range(sessions)
        ],
        "revisions": [
            {
                "revision_id": f"rev_{idx}",
                "session_id": f"sess_{idx % sessions}",
                "duration_minutes": total_minutes // revisions,
                "split": "DEVELOPMENT" if idx == revisions - 1 else "EVALUATION",
                "families": [FAMILIES[idx % 4]],
            }
            for idx in range(revisions)
        ],
        "family_coverage": list(FAMILIES),
    }

    return {
        "corpus-designation.json": corpus_designation,
        "editor-queries.json": {
            "schema_version": "gate0.editor-queries.v1",
            "query_version": "editor-v1",
            "queries": queries,
        },
        "reviewers.json": {
            "schema_version": "gate0.d2-reviewers.v1",
            "reviewer_ids": ["reviewer_a", "reviewer_b"],
            "appointment_authority": "gate0-owner appointment decision (text-only)",
        },
        "blinding.json": {
            "schema_version": "gate0.d2-blinding.v1",
            "token_map": [
                {"blind_arm_token": "arm-a", "arm_id": "metadata-floor"},
                {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"},
            ],
            "reviewer_visible_fields": ["blind_arm_token"],
            "reviewer_hidden_fields": ["arm_id"],
        },
        "owner-binding.json": {
            "schema_version": "gate0.d2-owner-binding.v1",
            "config_gate_owner_id": "owner_alpha",
            "manifest_gate_owner_id": "owner_alpha",
        },
    }


def _make_d2_memory_payload(*, break_field: str | None = None) -> dict[str, Any]:
    artifacts = _make_d2_artifacts()
    evidence_field_to_artifact = {
        "G0-D2-01": "corpus-designation.json",
        "G0-D2-10": "editor-queries.json",
        "G0-D2-11": "editor-queries.json",
        "G0-D2-12": "editor-queries.json",
        "G0-D2-14": "reviewers.json",
        "G0-D2-17": "blinding.json",
        "G0-D2-26": "owner-binding.json",
    }
    fields_map: dict[str, Any] = {}
    for field_id in D2_FIELD_IDS:
        if field_id in evidence_field_to_artifact and field_id != break_field:
            art_name = evidence_field_to_artifact[field_id]
            fields_map[field_id] = {
                "declared_status": "COMPLETE",
                "evidence": [
                    {
                        "artifact": art_name,
                        "digest": _artifact_digest(artifacts[art_name]),
                    }
                ],
            }
        else:
            fields_map[field_id] = {"declared_status": "ABSENT"}

    return {
        "schema_version": D2_PACKAGE_SCHEMA_VERSION,
        "package_id": "d2p_synth_lab_01",
        "fixture": True,
        "attestation": {
            "attester_id": "gate0-owner",
            "attester_kind": "SYNTHETIC_FIXTURE",
        },
        "fields": fields_map,
        "artifacts": artifacts,
        "owner_approved": True,  # Untrusted flag — must be stripped
    }


def _make_40_queries_and_splits() -> tuple[
    list[tuple[str, str, tuple[str, str]]], dict[str, str]
]:
    specs: list[tuple[str, str, tuple[str, str]]] = []
    splits: dict[str, str] = {}
    idx = 1
    # 24 EVALUATION POSITIVE queries: 6 per family across 4 FAMILIES
    for fam in FAMILIES:
        for _ in range(6):
            qid = f"q_{idx:02d}"
            specs.append(
                (qid, f"Eval positive query {qid} for {fam}", (fam, "POSITIVE"))
            )
            splits[qid] = "EVALUATION"
            idx += 1
    # 8 EVALUATION ABSENT queries: 2 per family
    for fam in FAMILIES:
        for _ in range(2):
            qid = f"q_{idx:02d}"
            specs.append((qid, f"Eval absent query {qid} for {fam}", (fam, "ABSENT")))
            splits[qid] = "EVALUATION"
            idx += 1
    # 8 DEVELOPMENT queries: 2 per family
    for fam in FAMILIES:
        for _ in range(2):
            qid = f"q_{idx:02d}"
            specs.append((qid, f"Dev query {qid} for {fam}", (fam, "POSITIVE")))
            splits[qid] = "DEVELOPMENT"
            idx += 1
    return specs, splits


def _make_gold_events() -> list[dict[str, Any]]:
    base_event = {
        "query_id": "q_01",
        "revision_id": "rev_01",
        "grade": 2,
        "rationale": "Clear visual observation of ballet leap entrance",
        "stream_index": 0,
        "start": {"numerator": 10, "denominator": 1},
        "end": {"numerator": 15, "denominator": 1},
        "uncertainty": {
            "start": {"numerator": 1, "denominator": 2},
            "end": {"numerator": 1, "denominator": 2},
        },
    }
    return [
        {**base_event, "reviewer_id": "rev_alice"},
        {**base_event, "reviewer_id": "rev_bob"},
    ]


def _make_reviewer_inputs(config_digest: str = "c" * 64) -> dict[str, Any]:
    rows = [
        {
            "query_id": "q_01",
            "window_id": "w_01",
            "blind_arm_token": "arm-a",
            "reviewer_id": "rev_alice",
            "grade": 2,
            "rationale": "Exact match in window",
            "ambiguity": "RESOLVED",
            "review_status": "FINAL",
            "adjudication_ref": None,
            "evidence_class": "VISUALLY_OBSERVED",
        },
        {
            "query_id": "q_01",
            "window_id": "w_01",
            "blind_arm_token": "arm-a",
            "reviewer_id": "rev_bob",
            "grade": 2,
            "rationale": "Confirmed match in window",
            "ambiguity": "RESOLVED",
            "review_status": "FINAL",
            "adjudication_ref": None,
            "evidence_class": "VISUALLY_OBSERVED",
        },
        {
            "query_id": "q_01",
            "window_id": "w_01",
            "blind_arm_token": "arm-b",
            "reviewer_id": "rev_alice",
            "grade": 1,
            "rationale": "Partial relevance",
            "ambiguity": "RESOLVED",
            "review_status": "FINAL",
            "adjudication_ref": None,
            "evidence_class": "VISUALLY_OBSERVED",
        },
        {
            "query_id": "q_01",
            "window_id": "w_01",
            "blind_arm_token": "arm-b",
            "reviewer_id": "rev_bob",
            "grade": 1,
            "rationale": "Agreed partial relevance",
            "ambiguity": "RESOLVED",
            "review_status": "FINAL",
            "adjudication_ref": None,
            "evidence_class": "VISUALLY_OBSERVED",
        },
    ]
    return {
        "rows": rows,
        "token_map": [
            {"blind_arm_token": "arm-a", "arm_id": "metadata-floor"},
            {"blind_arm_token": "arm-b", "arm_id": "offline-development-arm"},
        ],
        "mapping_version": "gate0-v1",
        "config_digest": config_digest,
    }


def _synth_digest(label: str) -> str:
    return digest_json({"synthetic_metadata": label})


def _make_gate0_config() -> tuple[dict[str, Any], dict[str, str]]:
    config: dict[str, Any] = json.loads(DEFAULT_CONFIG_PATH.read_text(encoding="utf-8"))
    config["corpus"]["source_root"] = "/synthetic-input-root-that-must-not-be-opened"
    config["corpus"]["source_manifest_digest"] = _synth_digest("source-manifest-rev-1")
    config["model"].update(
        {
            "model_identity": "synthetic-local-model-identity",
            "weights_digest": _synth_digest("weights"),
            "processor_digest": _synth_digest("processor"),
            "space_id": "synthetic-embedding-space",
            "dimension": 64,
        }
    )
    config["policy"]["egress_manifest_digest"] = _synth_digest("egress-manifest")
    config["sandbox"].update(
        {
            "bwrap_version": "synthetic-bwrap-1.0",
            "bwrap_digest": _synth_digest("bwrap"),
            "interpreter_digest": _synth_digest("interpreter"),
        }
    )
    config["blinding"]["blind_mapping_digest"] = _synth_digest("blind-mapping")

    observed = {
        "post_inventory:corpus.source_manifest_digest": config["corpus"][
            "source_manifest_digest"
        ],
        "model:model.weights_digest": config["model"]["weights_digest"],
        "model:model.processor_digest": config["model"]["processor_digest"],
        "policy:policy.egress_manifest_digest": config["policy"][
            "egress_manifest_digest"
        ],
        "sandbox:sandbox.bwrap_digest": config["sandbox"]["bwrap_digest"],
        "sandbox:sandbox.interpreter_digest": config["sandbox"]["interpreter_digest"],
        "blinding:blinding.blind_mapping_digest": config["blinding"][
            "blind_mapping_digest"
        ],
        "policy:policy.review_input.authorized_root": digest_bytes(
            config["policy"]["review_input"]["authorized_root"].encode("utf-8")
        ),
    }
    return config, observed


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
        assert pkt.summary["pending_count"] == 7
        assert pkt.summary["blocked_count"] == 21
        assert pkt.summary["not_observed_count"] == 2
        assert pkt.summary["execution_authorized"] is False
        assert pkt.summary["owner_approval_claimed"] is False
        assert pkt.summary["d3_status"] == "NOT_AUTHORIZED"
        assert "UNTRUSTED_AUTHORITY_FLAGS_IGNORED" in pkt.reasons

    def test_incomplete_d2_field_blocks_readiness(self) -> None:
        broken_payload = _make_d2_memory_payload(break_field="G0-D2-14")
        pkt = inspect_d2_readiness(broken_payload)
        assert pkt.status == ReadinessStatus.BLOCKED
        assert "G0-D2-14" in pkt.summary["evidence_intake_blockers"]


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
        assert pkt.summary["ranking_input_count"] == 40
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
        bad_gold[1]["query_id"] = "q_35"
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
        bad_observed["model:model.weights_digest"] = "9" * 64
        pkt = inspect_gate0_entry(
            {
                "config": cfg,
                "observed_digests": bad_observed,
            }
        )
        assert pkt.status == ReadinessStatus.BLOCKED
        assert "MODEL_ASSET_MISMATCH:model.weights_digest" in pkt.blockers
