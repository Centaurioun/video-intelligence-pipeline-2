"""Minimal local-only ``index`` / ``query`` command surface.

The command requires an explicit input for indexing and explicit model
identity/weights provenance.  Querying consumes the persisted generation's
pinned sampling policy and embeds text only; it never decodes or re-embeds
source media.  ``--fake-embedder`` is test-only orchestration support and does
not represent a measurement or evidence run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Sequence

from persistent_local_index.embedding import embed_images as _embed_images
from persistent_local_index.embedding import embed_texts as _embed_texts
from persistent_local_index.embedding import load_session, require_device
from persistent_local_index.local_model import LocalModelSpec, open_local_model
from persistent_local_index.indexer import index_inputs
from persistent_local_index.model_space import (
    EMBEDDING_DIM,
    GenerationSpec,
    SemanticSpace,
    TEXT_PREPROCESSING_CONTRACT,
    assert_same_space,
    build_generation_spec,
    digest_processor_assets,
    generation_spec_from_manifest,
    load_manifest,
)
from persistent_local_index.search import query_generation

FIXED_SAMPLING_INTERVAL_SECONDS = 4.5


def _build_space(model_root: Path, weights_sha256: str, model_identity: str, model_revision: str) -> SemanticSpace:
    """Derive a semantic-space identity from explicit local assets."""
    model_root = Path(model_root)
    processor_digest = digest_processor_assets(model_root)
    preprocessing_asset = model_root / "preprocessor_config.json"
    if not preprocessing_asset.is_file():
        raise ValueError("PROCESSOR_ASSET_MISSING:preprocessor_config.json")
    image_digest = hashlib.sha256(preprocessing_asset.read_bytes()).hexdigest()
    return SemanticSpace(
        model_identity=model_identity,
        # Synthetic compatibility retains the historical digest-derived space;
        # real mode rejects an omitted revision before this helper is reached.
        frozen_revision=model_revision or weights_sha256,
        weights_sha256=weights_sha256,
        processor_digest=processor_digest,
        image_preprocessing_digest=image_digest,
        text_preprocessing_contract=TEXT_PREPROCESSING_CONTRACT,
        embedding_dim=EMBEDDING_DIM,
        dtype="float32",
        normalization="l2",
    )


def _build_image_embedder(model_root: Path, weights_sha256: str, device: str,
                          model_revision: str | None = None):
    session = _open_validated_session(Path(model_root), weights_sha256, device, model_revision)
    return lambda paths: _embed_images(session, paths)


def _build_text_embedder(model_root: Path, weights_sha256: str, device: str,
                         model_revision: str | None = None):
    session = _open_validated_session(Path(model_root), weights_sha256, device, model_revision)
    return lambda texts: _embed_texts(session, texts)


def _open_validated_session(model_root: Path, weights_sha256: str, device: str,
                            model_revision: str | None = None):
    """Open the real session only through the checked local-model boundary."""
    root = Path(model_root)
    revision = model_revision if model_revision is not None else _revision_required(root)
    processor_digest = digest_processor_assets(root)
    spec = LocalModelSpec(root.resolve(), weights_sha256, processor_digest, revision, device=device)
    handle = open_local_model(
        spec,
        loader=lambda checked_root, checked_device: load_session(
            checked_root, weights_sha256, device=checked_device
        ),
    )
    return handle.runtime


def _revision_required(root: Path) -> str:
    """Compatibility helper retained only for direct test seam callers."""
    for name in ("revision.txt", "revision", "model_revision"):
        path = root / name
        if path.is_file() and path.read_text(encoding="utf-8").strip():
            return path.read_text(encoding="utf-8").strip()
    raise ValueError("MODEL_REVISION_REQUIRED")


def _fake_image_embedder():
    import numpy as np
    def embedder(paths):
        rows = []
        for path in paths:
            digest = hashlib.sha256(Path(path).read_bytes()).digest()
            rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
            vector = rng.standard_normal(EMBEDDING_DIM).astype(np.float32)
            rows.append(vector / np.linalg.norm(vector))
        return np.stack(rows).astype(np.float32)
    return embedder


def _fake_text_embedder():
    import numpy as np
    def embedder(texts):
        rows = []
        for text in texts:
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
            vector = rng.standard_normal(EMBEDDING_DIM).astype(np.float32)
            rows.append(vector / np.linalg.norm(vector))
        return np.stack(rows).astype(np.float32)
    return embedder


def _existing_generations(index_root: Path) -> list[tuple[Path, GenerationSpec]]:
    directory = Path(index_root) / "generations"
    if not directory.is_dir():
        return []
    found = []
    for candidate in sorted(directory.iterdir()):
        manifest = candidate / "manifest.json"
        if manifest.is_file():
            found.append((candidate, generation_spec_from_manifest(load_manifest(manifest))))
    return found


def _cmd_index(args) -> int:
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"INPUT_NOT_FOUND:{input_path}", file=sys.stderr)
        return 2
    device = require_device(args.device)
    if not args.fake_embedder and (not args.model_identity or not args.model_revision):
        raise ValueError("REAL_MODEL_IDENTITY_AND_REVISION_REQUIRED")
    space = _build_space(Path(args.model_root), args.weights_sha256, args.model_identity or Path(args.model_root).name, args.model_revision)
    spec = build_generation_spec(space, sampling_interval_seconds=FIXED_SAMPLING_INTERVAL_SECONDS)
    embedder = (_fake_image_embedder() if args.fake_embedder else
                _build_image_embedder(Path(args.model_root), args.weights_sha256, device,
                                      args.model_revision))
    summary = index_inputs(input_path, Path(args.index_root), spec, embedder)
    print(json.dumps({
        "ok": summary.failed == 0, "generation_id": summary.generation_id,
        "indexed": summary.indexed, "skipped": summary.skipped,
        "reused": summary.reused, "failed": summary.failed, "device": device,
        "results": [{"path": r.path, "source_sha256": r.source_sha256,
                     "disposition": r.disposition, "row_start": r.row_start,
                     "row_end": r.row_end, "error": r.error} for r in summary.results],
    }, indent=2))
    return 0


def _cmd_query(args) -> int:
    device = require_device(args.device)
    if not args.fake_embedder and (not args.model_identity or not args.model_revision):
        raise ValueError("REAL_MODEL_IDENTITY_AND_REVISION_REQUIRED")
    space = _build_space(Path(args.model_root), args.weights_sha256, args.model_identity or Path(args.model_root).name, args.model_revision)
    candidates = _existing_generations(Path(args.index_root))
    if not candidates:
        print(f"NO_GENERATION_FOUND:{args.index_root}", file=sys.stderr)
        return 2
    spec = None
    for _root, candidate in candidates:
        try:
            assert_same_space(space, candidate.space)
        except ValueError:
            continue
        spec = candidate
        break
    if spec is None:
        assert_same_space(space, candidates[0][1].space)
        print("NO_COMPATIBLE_GENERATION", file=sys.stderr)
        return 2
    texts = list(args.query)
    if not texts:
        print("NO_QUERY_SUPPLIED", file=sys.stderr)
        return 2
    embedder = (_fake_text_embedder() if args.fake_embedder else
                _build_text_embedder(Path(args.model_root), args.weights_sha256, device,
                                     args.model_revision))
    results = query_generation(Path(args.index_root), spec, texts, embedder, top_k=args.top_k)
    print(json.dumps({
        "ok": True, "generation_id": spec.generation_id, "device": device,
        "top_k": args.top_k,
        "queries": {query: {"hits": [
            {"rank": hit.rank, "score": hit.score, "row_id": hit.row_id,
             "source_sha256": hit.source_sha256, "source_path": hit.source_path,
             "pts": hit.pts, "timebase_num": hit.timebase_num,
             "timebase_den": hit.timebase_den, "timestamp_human": hit.timestamp_human,
             "thumbnail_path": hit.thumbnail_path, "thumbnail_status": hit.thumbnail_status}
            for hit in hits]} for query, hits in results.items()},
    }, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="persistent_local_index")
    subcommands = parser.add_subparsers(dest="command", required=True)
    index = subcommands.add_parser("index", help="index authorized local video")
    index.add_argument("--input", required=True); index.add_argument("--index-root", required=True)
    index.add_argument("--model-root", required=True); index.add_argument("--weights-sha256", required=True)
    index.add_argument("--model-identity", default=""); index.add_argument("--model-revision", default="")
    index.add_argument("--device", default="cpu", choices=["cpu", "mps"])
    index.add_argument("--fake-embedder", action="store_true", help=argparse.SUPPRESS); index.set_defaults(handler=_cmd_index)
    query = subcommands.add_parser("query", help="search persisted vectors")
    query.add_argument("--index-root", required=True); query.add_argument("--model-root", required=True)
    query.add_argument("--weights-sha256", required=True); query.add_argument("--model-identity", default="")
    query.add_argument("--model-revision", default=""); query.add_argument("--query", action="append", required=True)
    query.add_argument("--top-k", type=int, default=5); query.add_argument("--device", default="cpu", choices=["cpu", "mps"])
    query.add_argument("--fake-embedder", action="store_true", help=argparse.SUPPRESS); query.set_defaults(handler=_cmd_query)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return int(args.handler(args))
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr); return 3
    except ValueError as exc:
        print(str(exc), file=sys.stderr); return 4


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
