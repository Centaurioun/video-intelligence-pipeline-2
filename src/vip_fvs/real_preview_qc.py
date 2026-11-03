"""Technical QC for independently verified REAL previews."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .real_preview_verifier import PreviewVerification


@dataclass(frozen=True)
class TechnicalQCReport:
    status: str
    verification_artifact_id: str
    reason_codes: tuple[str, ...]
    checks: tuple[dict[str, Any], ...]
    evidence_class: str = "MEASURED"
    production_eligible: bool = False
    export_eligible: bool = False
    attempt_id: str = ""

    def to_record(self) -> dict[str, Any]:
        return {"status": self.status, "verification_artifact_id": self.verification_artifact_id,
                "attempt_id": self.attempt_id,
                "reason_codes": list(self.reason_codes), "checks": list(self.checks),
                "evidence_class": "MEASURED",
                "production_eligible": False, "export_eligible": False,
                "NOT_OBSERVED": ["visual editorial suitability", "production render correctness",
                                  "audio observation", "provider/cloud inference"]}


class TechnicalQC:
    @staticmethod
    def evaluate(verification: PreviewVerification, *, measured_output_streams: int | None = None,
                 attempt_id: str | None = None) -> TechnicalQCReport:
        if not isinstance(verification, PreviewVerification):
            raise ValueError("VERIFICATION_REQUIRED")
        reasons: list[str] = []
        bound_attempt = verification.attempt_id if attempt_id is None else attempt_id
        if (not isinstance(bound_attempt, str) or not bound_attempt.strip()
                or bound_attempt != verification.attempt_id):
            reasons.append("ATTEMPT_MISMATCH")
        if verification.status != "PASS":
            reasons.append("VERIFIER_NOT_PASS")
        if verification.independent_of_producer is not True:
            reasons.append("VERIFIER_NOT_INDEPENDENT")
        if verification.production_eligible or verification.export_eligible:
            reasons.append("INVALID_SCOPE")
        observed_streams = verification.measured_output_streams if measured_output_streams is None else measured_output_streams
        if (isinstance(observed_streams, bool) or not isinstance(observed_streams, int)
                or observed_streams != 1):
            reasons.append("OUTPUT_STREAM_NOT_OBSERVED")
        if verification.measured_output_timebase is None or verification.measured_output_duration_ticks is None:
            reasons.append("OUTPUT_TIMING_NOT_OBSERVED")
        elif verification.expected_output_duration_ticks is None:
            reasons.append("EXPECTED_DURATION_NOT_BOUND")
        elif verification.measured_output_duration_ticks != verification.expected_output_duration_ticks:
            reasons.append("OUTPUT_TIMING_CONTRADICTION")
        status = "PASS" if not reasons else "BLOCKED"
        checks = tuple(
            {"check": name, "result": "BLOCKED" if blocked else "PASS", "evidence_class": "MEASURED"}
            for name, blocked in (
                ("independent_verification", any(r in reasons for r in ("VERIFIER_NOT_PASS", "VERIFIER_NOT_INDEPENDENT"))),
                ("output_stream_identity", "OUTPUT_STREAM_NOT_OBSERVED" in reasons),
                ("output_timing", any(r in reasons for r in ("OUTPUT_TIMING_NOT_OBSERVED", "EXPECTED_DURATION_NOT_BOUND", "OUTPUT_TIMING_CONTRADICTION"))),
                ("nonproduction_scope", "INVALID_SCOPE" in reasons),
                ("attempt_identity", "ATTEMPT_MISMATCH" in reasons),
            )
        )
        return TechnicalQCReport(status, verification.artifact_id, tuple(reasons), checks, attempt_id=bound_attempt if isinstance(bound_attempt, str) else "")


evaluate_technical_qc = TechnicalQC.evaluate

__all__ = ["TechnicalQC", "TechnicalQCReport", "evaluate_technical_qc"]
