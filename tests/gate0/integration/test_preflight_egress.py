from __future__ import annotations

from pathlib import Path

import pytest

from gate0.egress import EgressGuard, EgressRequestContext
from gate0.policy import PolicyDecision, PolicyDenied, PolicyUseContext, require_allow
from gate0.stages.preflight import SandboxAttestation, observe_sandbox, preflight


NOW = "2026-09-12T12:00:00Z"
DIGEST = "a" * 64


def _decision(purpose: str, artifacts: tuple[str, ...], *, decision="ALLOW") -> PolicyDecision:
    return PolicyDecision("policy_" + purpose.lower(), ("rev_1",), purpose,
        "PUBLIC", artifacts, "local_only", "DERIVED_REPLAYABLE",
        "2026-09-13T00:00:00Z", None, DIGEST, decision, True)


def test_processing_requires_distinct_processing_authorization():
    discovery = _decision("DISCOVER", ("source_manifest", "discovery_authorization"))
    context = PolicyUseContext("rev_1", "PROCESS", "PROCESS", "window_sample_manifest",
                               "local_only", "DERIVED_REPLAYABLE", NOW, DIGEST,
                               discovery, None)
    with pytest.raises(PolicyDenied):
        require_allow(context)
    processing = _decision("PROCESS", ("window_sample_manifest",))
    context = PolicyUseContext("rev_1", "PROCESS", "PROCESS", "window_sample_manifest",
                               "local_only", "DERIVED_REPLAYABLE", NOW, DIGEST,
                               discovery, processing)
    assert require_allow(context) is None


def test_egress_denial_is_zero_byte_and_payload_free():
    guard = EgressGuard()
    decision = guard.request(EgressRequestContext(
        "run_1", "attempt_1", "policy_process", DIGEST, "dns-sentinel",
        "https://user:secret@example.invalid/", "DNS", 37, NOW))
    assert decision.decision == "DENY"
    assert decision.outcome == "BLOCKED"
    assert decision.attempted_bytes == 37
    assert decision.transmitted_bytes == 0
    assert decision.payload is None
    assert "secret" not in decision.destination


def test_child_network_sentinel_denies_dns_proxy_provider_and_loopback():
    guard = EgressGuard()
    events = guard.child_network_sentinel("run_1", "attempt_sentinel", "policy_process", DIGEST, NOW)
    assert {event.protocol for event in events} == {"DNS", "HTTP_PROXY", "PROVIDER", "LOOPBACK"}
    assert all(event.decision == "DENY" and event.outcome == "BLOCKED" for event in events)
    assert all(event.transmitted_bytes == 0 and event.payload is None for event in events)
    assert all(event.attempt_id == "attempt_sentinel" and event.policy_decision_id == "policy_process" for event in events)


def test_preflight_blocks_without_sandbox_attestation(tmp_path: Path):
    result = preflight(revision_id="rev_1", discovery_decision=_decision(
        "DISCOVER", ("source_manifest", "discovery_authorization")),
        processing_decision=_decision("PROCESS", ("window_sample_manifest",)),
        expected_egress_manifest_digest=DIGEST, sandbox=None,
        output_root=tmp_path)
    assert result.exit_code == 20
    assert result.preflight_status == "BLOCKED_PREREQUISITE"
    assert "SANDBOX_ATTESTATION" in result.failure_refs


def test_authorized_synthetic_preflight_is_reproducible():
    sandbox = SandboxAttestation.synthetic(DIGEST)
    kwargs = dict(revision_id="rev_1", discovery_decision=_decision(
        "DISCOVER", ("source_manifest", "discovery_authorization")),
        processing_decision=_decision("PROCESS", ("window_sample_manifest",)),
        expected_egress_manifest_digest=DIGEST, sandbox=sandbox)
    first, second = preflight(**kwargs), preflight(**kwargs)
    assert first.exit_code == second.exit_code == 0
    assert first.decision_digests == second.decision_digests


def test_sandbox_attestation_contains_digests_and_exact_policy():
    sandbox = SandboxAttestation.synthetic(DIGEST)
    expected = sandbox.to_dict() | {"argv_digest": DIGEST, "mount_policy_digest": DIGEST}
    observed = SandboxAttestation.from_mapping(expected)
    assert observed.matches(expected)
    broken = dict(expected, net_unshared=False)
    assert not observed.matches(broken)


def test_preflight_observes_and_validates_canonical_sandbox_config(tmp_path: Path):
    # The injectable observer lets this test remain local-only while requiring
    # preflight to own the comparison and carry the evidence forward.
    sandbox = SandboxAttestation.synthetic(DIGEST)
    expected = sandbox.to_dict()
    result = preflight(revision_id="rev_1", discovery_decision=_decision(
        "DISCOVER", ("source_manifest", "discovery_authorization")),
        processing_decision=_decision("PROCESS", ("window_sample_manifest",)),
        expected_egress_manifest_digest=DIGEST, sandbox=None,
        sandbox_config=expected, sandbox_observer=lambda config: sandbox)
    assert result.exit_code == 0
    assert result.sandbox_attestation == sandbox


def test_preflight_publishes_joinable_child_sentinel_receipts():
    sandbox = SandboxAttestation.synthetic(DIGEST)
    guard = EgressGuard()
    result = preflight(revision_id="rev_1", discovery_decision=_decision(
        "DISCOVER", ("source_manifest", "discovery_authorization")),
        processing_decision=_decision("PROCESS", ("window_sample_manifest",)),
        expected_egress_manifest_digest=DIGEST, sandbox=sandbox,
        egress_guard=guard)
    assert result.exit_code == 0
    assert len(result.egress_events) == 4
    assert all(event.attempt_id == result.attempt_id for event in result.egress_events)
    assert all(event.transmitted_bytes == 0 for event in result.egress_events)


def test_preflight_converts_malformed_policy_mapping_to_named_block():
    sandbox = SandboxAttestation.synthetic(DIGEST)
    malformed = {"policy_decision_id": "bad", "revision_scope": ["rev_1"],
                 "purpose": "PROCESS", "sensitivity_consent": "PUBLIC",
                 "allowed_artifact_types": ["window_sample_manifest"],
                 "provider_model_boundary": "local_only", "retention_class": "DERIVED_REPLAYABLE",
                 "expires_at": "not-a-timestamp", "revocation_ref": None,
                 "egress_manifest_digest": DIGEST, "decision": "ALLOW", "effective_at_use": True}
    result = preflight(revision_id="rev_1", discovery_decision=None,
                       processing_decision=malformed,
                       expected_egress_manifest_digest=DIGEST, sandbox=sandbox)
    assert result.exit_code == 20
    assert result.preflight_status == "BLOCKED_POLICY"


def test_missing_runtime_sandbox_is_blocked_without_fallback(tmp_path: Path):
    observed, reason = observe_sandbox({"bwrap_path": str(tmp_path / "missing-bwrap"),
                                        "interpreter_path": str(tmp_path / "missing-python")})
    assert observed is None
    assert reason == "SANDBOX_ATTESTATION"


def test_malformed_or_naive_clock_input_is_fail_closed():
    sandbox = SandboxAttestation.synthetic(DIGEST)
    result = preflight(revision_id="rev_1", discovery_decision=_decision(
        "DISCOVER", ("source_manifest", "discovery_authorization")),
        processing_decision=_decision("PROCESS", ("window_sample_manifest",)),
        expected_egress_manifest_digest=DIGEST, sandbox=sandbox, now="2026-09-12T12:00:00")
    assert result.exit_code == 20
    assert result.failure_refs == ("POLICY_DENIED",)


def test_launcher_is_literal_bwrap_no_network_contract():
    launcher = Path(__file__).parents[3] / "scripts/gate0-run.sh"
    text = launcher.read_text()
    for token in ("/usr/bin/bwrap", "--die-with-parent", "--unshare-net", "--clearenv",
                  "--ro-bind", "--bind", "--dev /dev", "--proc /proc",
                  "/usr/bin/python3.11", "--setenv PATH /usr/bin:/bin"):
        assert token in text
    assert "fallback" not in text.lower()
