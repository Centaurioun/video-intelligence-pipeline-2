"""Synthetic local-semantic acceptance seams.

This is deliberately an integration-test skeleton for the injected-embedder
boundary.  It uses no media decoder, model loader, network, or provider; the
index/query calls are replaced with deterministic in-memory sentinels.  The
test is expected to remain useful while the coordinator wiring is integrated.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from gate0.policy import PolicyDecision, PolicyDenied
from vip_fvs import retrieval_adapter as adapter
from vip_fvs.source_adapter import inventory_source


def _discovery_policy(revision: str = "rev-synthetic") -> PolicyDecision:
    return PolicyDecision(
        policy_decision_id="policy_synthetic_local_semantic",
        revision_scope=(revision,),
        purpose="DISCOVER",
        sensitivity_consent="SYNTHETIC",
        allowed_artifact_types=("source_manifest", "discovery_authorization"),
        provider_model_boundary="local_only",
        retention_class="SOURCE_REFERENCE",
        expires_at="2099-01-01T00:00:00Z",
        revocation_ref=None,
        egress_manifest_digest="a" * 64,
        decision="ALLOW",
        effective_at_use=True,
    )


def test_injected_embedder_synthetic_query_is_explicitly_non_fake(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Injected deterministic vectors prove the seam without model/media I/O."""
    source = tmp_path / "synthetic.source.json"
    source.write_bytes(b'{"synthetic": true, "frames": [0, 1]}')
    binding = inventory_source(
        source, tmp_path / "inventory", _discovery_policy(), revision_id="rev-synthetic"
    )
    calls: dict[str, object] = {}
    expected = adapter.SearchHit(
        query="needle", rank=0, score=1.0, row_id=0,
        source_path=str(source), source_sha256=b"synthetic".hex().ljust(64, "0"),
        pts=0, timebase_num=1, timebase_den=1, timestamp_human="00:00:00",
        thumbnail_path=None, thumbnail_status="NOT_REQUESTED",
    )

    def injected_image(paths):
        calls["image_paths"] = tuple(paths)
        return np.ones((len(paths), 768), dtype=np.float32)

    def injected_text(texts):
        calls["texts"] = tuple(texts)
        return np.ones((len(texts), 768), dtype=np.float32)

    def no_media_index(path, root, spec, image_embedder):
        calls["index"] = (Path(path), Path(root), spec)
        # The injected function is exercised, but no decoder or media bytes
        # are touched by this acceptance seam.
        image_embedder((Path("synthetic-frame-placeholder"),))

    def in_memory_query(root, spec, texts, text_embedder, *, top_k):
        text_embedder(texts)
        calls["query"] = (Path(root), spec, tuple(texts), top_k)
        return {texts[0]: (expected,)}

    monkeypatch.setattr(adapter, "index_inputs", no_media_index)
    monkeypatch.setattr(adapter, "query_generation", in_memory_query)

    result = adapter.retrieve(
        binding,
        "needle",
        tmp_path / "index",
        fake_embedder=False,
        image_embedder=injected_image,
        text_embedder=injected_text,
        semantic_space=adapter.fake_semantic_space(),
        invocation_ref="synthetic-local/attempt-1",
    )

    assert result.fake_embedder_used is False
    assert result.invocation_ref == "synthetic-local/attempt-1"
    assert result.hits == (expected,)
    assert calls["image_paths"] == (Path("synthetic-frame-placeholder"),)
    assert calls["texts"] == ("needle",)
    assert calls["index"][0] == source  # type: ignore[index]
    assert calls["query"][3] == 5  # type: ignore[index]


def test_processing_authorization_cannot_be_used_for_synthetic_discovery(
    tmp_path: Path,
) -> None:
    """A missing/incorrect discovery authorization fails before retrieval."""
    source = tmp_path / "synthetic.source.json"
    source.write_bytes(b'{"synthetic": true}')
    processing_policy = PolicyDecision(
        policy_decision_id="policy_processing_only",
        revision_scope=("rev-synthetic",),
        purpose="PROCESS",
        sensitivity_consent="SYNTHETIC",
        allowed_artifact_types=("source_manifest",),
        provider_model_boundary="local_only",
        retention_class="SOURCE_REFERENCE",
        expires_at="2099-01-01T00:00:00Z",
        revocation_ref=None,
        egress_manifest_digest="a" * 64,
        decision="ALLOW",
        effective_at_use=True,
    )
    with pytest.raises(PolicyDenied, match="discovery policy purpose mismatch"):
        inventory_source(
            source,
            tmp_path / "inventory-denied",
            processing_policy,
            revision_id="rev-synthetic",
        )
