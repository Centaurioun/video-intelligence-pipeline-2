from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest


def _query_modality_api():
    from vip_fvs import query_modality

    return query_modality


def test_text_envelope_normalizes_round_trips_and_legacy_text_retrieval_remains_compatible(
    monkeypatch, tmp_path
):
    api = _query_modality_api()
    from vip_fvs import retrieval_adapter as adapter

    envelope = api.QueryEnvelope.from_text("  harbor\n  lights  ")
    assert envelope.modality is api.QueryModality.TEXT
    assert envelope.text == "harbor lights"
    assert envelope.capability is api.CapabilityLevel.EXECUTABLE
    assert envelope.availability is api.ModalityAvailability.AVAILABLE
    assert api.QueryEnvelope.from_dict(envelope.to_dict()) == envelope

    hit = SimpleNamespace(query="harbor lights", rank=0, score=0.75)
    calls = []

    class Engine:
        def build_generation_spec(self, space):
            calls.append(("build", space))
            return SimpleNamespace(generation_id="g", space_id="s")

        def index_source(self, path, root, spec, image_embedder):
            calls.append(("index", Path(path), Path(root)))

        def query(self, root, spec, texts, text_embedder, *, top_k):
            calls.append(("query", tuple(texts), top_k))
            return {text: (hit,) for text in texts}

    binding = {"source_path": tmp_path / "source.mp4", "source_sha256": "a" * 64}
    result = adapter.retrieve(
        binding, envelope, tmp_path / "index", fake_embedder=True, engine=Engine()
    )
    assert result.hits == (hit,)
    assert calls[-1] == ("query", ("harbor lights",), 5)

    legacy = adapter.retrieve(
        binding, "harbor lights", tmp_path / "index", fake_embedder=True, engine=Engine()
    )
    assert legacy.hits == (hit,)


@pytest.mark.parametrize("modality", ["IMAGE_REFERENCE", "VIDEO_REFERENCE"])
def test_reference_envelopes_require_opaque_identity_and_provenance_and_round_trip(modality):
    api = _query_modality_api()
    selected = api.QueryModality[modality]
    reference = api.ReferenceQuery(
        reference_id="asset-ref:clip-17",
        provenance_ref="ingest-run:run-9",
        source_revision_ref="source-revision:rev-2",
        interval=api.CoarseReferenceInterval(1.25, 4.5),
    )
    envelope = api.QueryEnvelope.from_reference(selected, reference)

    assert envelope.reference == reference
    assert envelope.capability is api.CapabilityLevel.DECLARED
    assert envelope.availability is api.ModalityAvailability.NOT_AVAILABLE
    assert api.QueryEnvelope.from_dict(envelope.to_dict()) == envelope

    with pytest.raises((TypeError, ValueError)):
        api.ReferenceQuery(reference_id="/private/media/clip.mp4", provenance_ref="p", source_revision_ref="r")
    with pytest.raises((TypeError, ValueError)):
        api.ReferenceQuery(reference_id="C:clip.mp4", provenance_ref="p", source_revision_ref="r")
    with pytest.raises((TypeError, ValueError)):
        api.ReferenceQuery(reference_id=b"embedded-media", provenance_ref="p", source_revision_ref="r")
    with pytest.raises((TypeError, ValueError)):
        api.ReferenceQuery(reference_id="asset-ref:x", provenance_ref="", source_revision_ref="r")


@pytest.mark.parametrize("modality", ["IMAGE_REFERENCE", "VIDEO_REFERENCE"])
def test_unsupported_reference_execution_fails_before_embed_query_or_index_mutation(
    modality, tmp_path
):
    api = _query_modality_api()
    from vip_fvs import retrieval_adapter as adapter

    envelope = api.QueryEnvelope.from_reference(
        api.QueryModality[modality],
        api.ReferenceQuery("asset-ref:x", "ingest-run:y", "source-revision:z"),
    )
    effects = []

    class Engine:
        def build_generation_spec(self, space):
            effects.append("build_generation_spec")
            return SimpleNamespace(generation_id="g", space_id="s")

        def index_source(self, *args):
            effects.append("index_source")

        def query(self, *args, **kwargs):
            effects.append("query")

    def image_embedder(paths):
        effects.append("image_embed")
        raise AssertionError("unsupported modality must fail before image embedding")

    def text_embedder(texts):
        effects.append("text_embed")
        raise AssertionError("unsupported modality must not fall back to text")

    with pytest.raises(adapter.UnsupportedModalityError):
        adapter.retrieve(
            {"source_path": tmp_path / "source.mp4", "source_sha256": "a" * 64},
            envelope,
            tmp_path / "index",
            image_embedder=image_embedder,
            text_embedder=text_embedder,
            semantic_space=adapter.fake_semantic_space(),
            engine=Engine(),
        )
    assert effects == []
    assert not (tmp_path / "index").exists()


def test_declared_capability_is_not_executable_even_with_matching_vector_dimensions():
    api = _query_modality_api()
    reference = api.ReferenceQuery("asset-ref:x", "ingest-run:y", "source-revision:z")
    declared = api.QueryEnvelope.from_reference(api.QueryModality.IMAGE_REFERENCE, reference)

    assert declared.capability is api.CapabilityLevel.DECLARED
    assert declared.availability is api.ModalityAvailability.NOT_AVAILABLE
    # An equal vector dimension is deliberately irrelevant to whether the
    # image-reference seam is executable.
    text_embedding_dim = image_embedding_dim = 768
    assert text_embedding_dim == image_embedding_dim
    with pytest.raises((TypeError, ValueError)):
        api.QueryEnvelope(
            modality=api.QueryModality.IMAGE_REFERENCE,
            reference=reference,
            capability=api.CapabilityLevel.EXECUTABLE,
            availability=api.ModalityAvailability.AVAILABLE,
        )


def test_coarse_reference_interval_is_nonbinding_provenance_not_measured_source_pts_authority():
    api = _query_modality_api()
    interval = api.CoarseReferenceInterval(2.0, 6.0)
    envelope = api.QueryEnvelope.from_reference(
        api.QueryModality.VIDEO_REFERENCE,
        api.ReferenceQuery("asset-ref:x", "ingest-run:y", "source-revision:z", interval),
    )
    payload = envelope.to_dict()["reference"]["interval"]

    assert payload == {"start_seconds": 2.0, "end_seconds": 6.0, "timebase": "seconds"}
    assert not {"evidence_class", "source_pts", "binding_eligible", "edit_boundary"} & set(payload)
    with pytest.raises((TypeError, ValueError)):
        api.CoarseReferenceInterval(-0.1, 1.0)
    with pytest.raises((TypeError, ValueError)):
        api.CoarseReferenceInterval(2.0, 2.0)
