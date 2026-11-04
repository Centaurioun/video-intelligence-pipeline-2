"""Regression tests for Wave MEGA-06 (P06a, P06b, P06c): Gate-2 Workload Plan,
Recovery Matrix, and Measurement/Mechanism Review.
"""

from __future__ import annotations

from typing import Any

from vip_lab.common import ReadinessStatus
from vip_lab.mega06 import (
    inspect_measurement_review,
    inspect_recovery_scenario,
    inspect_workload_plan,
)


def _make_workload_spec_dict() -> dict[str, Any]:
    return {
        "seed": 11,
        "jobs": 3,
        "stages": 2,
        "artifact_bytes": 64,
        "f01_sha": "1" * 40,
        "c04_sha": "2" * 40,
        "e05_sha": "3" * 40,
        "config_digest": "a" * 64,
    }


class TestMega06WorkloadPlan:
    def test_valid_workload_plan_is_deterministic(self) -> None:
        pkt1 = inspect_workload_plan(_make_workload_spec_dict())
        pkt2 = inspect_workload_plan(_make_workload_spec_dict())
        assert pkt1.status == ReadinessStatus.READY_SYNTHETIC
        assert pkt1.summary["valid_spec"] is True
        assert pkt1.summary["deterministic"] is True
        assert pkt1.summary["fixture_digest"] == pkt2.summary["fixture_digest"]
        assert pkt1.summary["total_steps"] == 6
        assert pkt1.summary["real_archive_workload_observed"] is False

    def test_workload_plan_rejects_out_of_bounds_or_invalid_shas(self) -> None:
        bad_jobs = _make_workload_spec_dict()
        bad_jobs["jobs"] = 101
        pkt = inspect_workload_plan(bad_jobs)
        assert pkt.status == ReadinessStatus.INVALID
        assert "WORKLOAD_SPEC_INVALID" in pkt.blockers

        bad_sha = _make_workload_spec_dict()
        bad_sha["f01_sha"] = "not-a-40-hex-sha"
        pkt2 = inspect_workload_plan(bad_sha)
        assert pkt2.status == ReadinessStatus.INVALID


class TestMega06RecoveryMatrix:
    def test_interrupted_recovery_converges_without_recomputation(self) -> None:
        pkt = inspect_recovery_scenario(
            {
                "workload": _make_workload_spec_dict(),
                "interrupt_at_step": 2,
                "fault_class": "PARTIAL_WRITE",
            }
        )
        assert pkt.status == ReadinessStatus.READY_SYNTHETIC
        assert pkt.summary["refused_fail_closed"] is False
        assert pkt.summary["initial_run"]["completed_count"] == 2
        assert pkt.summary["resume_run"]["completed_count"] == 6
        assert pkt.summary["resume_run"]["recomputed_count"] == 0
        assert pkt.summary["resume_run"]["corrupted_count"] == 0
        assert pkt.summary["fault"]["fault_class"] == "PARTIAL_WRITE"

    def test_tampered_binding_or_corrupt_artifact_refused_fail_closed(self) -> None:
        tampered_pkt = inspect_recovery_scenario(
            {
                "workload": _make_workload_spec_dict(),
                "interrupt_at_step": 2,
                "tamper_binding_on_resume": True,
            }
        )
        assert tampered_pkt.status == ReadinessStatus.BLOCKED
        assert "RECOVERY_REFUSED_FAIL_CLOSED" in tampered_pkt.blockers
        assert tampered_pkt.summary["refused_fail_closed"] is True

        corrupt_pkt = inspect_recovery_scenario(
            {
                "workload": _make_workload_spec_dict(),
                "interrupt_at_step": 2,
                "corrupt_artifact_on_resume": True,
            }
        )
        assert corrupt_pkt.status == ReadinessStatus.BLOCKED
        assert "RECOVERY_REFUSED_FAIL_CLOSED" in corrupt_pkt.blockers


class TestMega06MeasurementReview:
    def test_synthetic_measurements_never_justify_scaling_mechanisms(self) -> None:
        pkt = inspect_measurement_review(
            {
                "measurements": [
                    {
                        "metric_id": "query_p95_latency_ms",
                        "unit": "ms",
                        "value": 12.5,
                        "evidence_class": "MEASURED",
                        "status": "OBSERVED",
                        "provenance_digest": "b" * 64,
                    },
                    {
                        "metric_id": "real_archive_throughput",
                        "unit": "clips_per_sec",
                        "value": None,
                        "evidence_class": "NOT_OBSERVED",
                        "status": "NOT_OBSERVED",
                        "provenance_digest": "c" * 64,
                    },
                ]
            }
        )
        assert pkt.status == ReadinessStatus.READY_SYNTHETIC
        assert pkt.summary["real_workload_evidence"] == "NOT_OBSERVED"
        assert pkt.summary["model_runtime_provenance"] == "NOT_OBSERVED"
        assert pkt.summary["threshold_suitability"] == "NOT_OBSERVED"
        assert pkt.summary["mechanism_needed"] == "NOT_DETERMINED"
        assert pkt.summary["approved_mechanisms"] == []

    def test_claiming_mechanism_justification_or_bad_evidence_class_rejected(
        self,
    ) -> None:
        claim_pkt = inspect_measurement_review(
            {
                "measurements": [],
                "claim_production_mechanism_justified": True,
            }
        )
        assert claim_pkt.status == ReadinessStatus.BLOCKED
        assert "SYNTHETIC_WORKLOAD_CANNOT_JUSTIFY_MECHANISM" in claim_pkt.blockers

        bad_ev_pkt = inspect_measurement_review(
            {
                "measurements": [
                    {
                        "metric_id": "m1",
                        "unit": "ms",
                        "value": 1.0,
                        "evidence_class": "INVENTED_EVIDENCE_CLASS",
                        "status": "OBSERVED",
                        "provenance_digest": "d" * 64,
                    }
                ]
            }
        )
        assert bad_ev_pkt.status == ReadinessStatus.INVALID
        assert "MEASUREMENT_SCHEMA_VIOLATION" in bad_ev_pkt.blockers
