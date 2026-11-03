import re

import pytest

from gate2.measure import (
    CANONICAL_EVIDENCE_CLASSES,
    NOT_OBSERVED,
    Measurement,
    MeasurementSet,
)
from gate2.preregistration import FrozenPreregistration, Preregistration, PreregistrationError
from gate0.identity import digest_json


def test_evidence_classes_are_exactly_the_canonical_five():
    assert CANONICAL_EVIDENCE_CLASSES == {
        "MEASURED", "MATCHED", "VISUALLY_OBSERVED",
        "AUDIO_OBSERVED", "EDITORIAL_INFERENCE",
    }


def test_measurement_requires_evidence_and_derivation():
    m = Measurement.measured(metric_id="duration", value=2.5, unit="s", derivation="PTS delta")
    assert m.evidence_class == "MEASURED"
    with pytest.raises(ValueError):
        Measurement.measured(metric_id="duration", value=2.5, unit="s", derivation="", evidence_class="NOT_OBSERVED")


def test_not_observed_is_status_without_class_and_requires_non_decision_reason():
    m = Measurement.not_observed(metric_id="duration", reason="stream unavailable")
    assert m.value is NOT_OBSERVED
    assert m.evidence_class is None
    item = MeasurementSet([m]).to_dict()["not_observed"][0]
    assert item["status"] == "NOT_OBSERVED"
    assert "evidence_class" not in item
    with pytest.raises(ValueError):
        Measurement.not_observed(metric_id="duration", reason="C3")
    with pytest.raises(ValueError):
        Measurement.not_observed(metric_id="duration", reason="C3 selected")
    with pytest.raises(ValueError):
        Measurement.not_observed(metric_id="duration", reason="")


@pytest.mark.parametrize("reason", ["KC3", "ſBR-C1", "İT1"])
def test_unicode_casefold_characters_do_not_hide_ascii_decision_labels(reason):
    with pytest.raises(ValueError, match="decision label"):
        Measurement.not_observed(metric_id="duration", reason=reason)


def test_decision_label_cannot_be_recorded_as_measurement():
    with pytest.raises(ValueError):
        Measurement.measured(metric_id="decision", value="C3", unit="label", derivation="copied")
    with pytest.raises(ValueError):
        Measurement.measured(metric_id="duration", value=True, unit="s", derivation="copied")


def test_single_sample_summary_does_not_claim_distribution():
    values = MeasurementSet([Measurement.measured(metric_id="fps", value=24, unit="fps", derivation="frame count / duration")])
    summary = values.summarize("fps")
    assert summary["n"] == 1
    assert summary["is_distribution"] is False


def test_serialization_is_deterministic_and_digest_bearing():
    m = Measurement.measured(metric_id="fps", value=24, unit="fps", derivation="frame count / duration")
    values = MeasurementSet([m])
    doc = values.to_dict()
    assert doc["schema_version"] == "gate2.measurement.v1"
    digest = doc.pop("measurement_set_digest")
    assert re.fullmatch(r"[0-9a-f]{64}", digest)
    assert digest == digest_json(doc)
    assert values.to_dict()["measurement_set_digest"] == digest


def test_descriptive_identity_is_permitted():
    m = Measurement.measured(metric_id="scene-17-duration", value=2.0, unit="s", derivation="PTS delta")
    assert m.metric_id == "scene-17-duration"


@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_metric_id_rejects_trimmed_ascii_case_insensitive_whole_token_placeholders(placeholder):
    for candidate in (placeholder.upper(), f"  {placeholder.title()}  "):
        with pytest.raises(ValueError, match="metric identity"):
            Measurement.measured(metric_id=candidate, value=1, unit="count", derivation="counted")
        with pytest.raises(ValueError, match="metric identity"):
            Measurement.not_observed(metric_id=candidate, reason="source unavailable")


@pytest.mark.parametrize("placeholder", [
    "null", "none", "todo", "tbd", "xxx", "placeholder", "changeme", "unknown", "example",
])
def test_metric_id_accepts_embedded_ascii_case_insensitive_placeholder_words(placeholder):
    candidate = f"metric-{placeholder.upper()}-v1"
    measured = Measurement.measured(metric_id=candidate, value=1, unit="count", derivation="counted")
    missing = Measurement.not_observed(metric_id=candidate, reason="source unavailable")
    assert measured.metric_id == candidate
    assert missing.metric_id == candidate


def test_gate2_package_exports_its_current_measurement_and_preregistration_seam():
    import gate2

    assert gate2.Measurement is Measurement
    assert gate2.MeasurementSet is MeasurementSet
    assert gate2.NOT_OBSERVED is NOT_OBSERVED
    assert gate2.Preregistration is Preregistration
    assert gate2.PreregistrationError is PreregistrationError
    assert gate2.FrozenPreregistration is FrozenPreregistration
