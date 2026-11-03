"""Shared deterministic fixtures for the persistent index test suite.

Real video generation uses FFmpeg on tiny synthetic sources only.  No real user
media, no network, no model download.  Embedding is always injected as a
deterministic fake so lifecycle tests assert index behaviour, not model quality.
"""
from __future__ import annotations

import hashlib
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest

from persistent_local_index.model_space import SemanticSpace, build_generation_spec

ROW_WIDTH = 768 * 4
FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")

requires_ffmpeg = pytest.mark.skipif(
    FFMPEG is None or FFPROBE is None, reason="ffmpeg/ffprobe not available"
)


def make_semantic_space(**overrides) -> SemanticSpace:
    base = dict(
        model_identity="google/siglip-base-patch16-224",
        frozen_revision="7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
        weights_sha256="2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8",
        processor_digest="proc",
        image_preprocessing_digest="image",
        text_preprocessing_contract="padding=max_length",
        embedding_dim=768,
        dtype="float32",
        normalization="l2",
    )
    base.update(overrides)
    return SemanticSpace(**base)


def make_spec(**overrides):
    return build_generation_spec(make_semantic_space(**overrides))


def deterministic_vector(seed: str) -> np.ndarray:
    """Stable pseudo-embedding for a seed string — reproducible across runs."""
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
    vector = rng.standard_normal(768).astype(np.float32)
    return (vector / np.linalg.norm(vector)).astype(np.float32)


def make_image_embedder(counter: dict | None = None):
    """Deterministic fake image embedder bound to the embedded file's bytes.

    Records, per call, the byte digest of every image actually embedded, so a
    test can assert that persisted row ``i`` holds the embedding of row ``i``'s
    own image rather than merely "some" embedding.
    """
    calls: list[list[str]] = []
    digests: list[list[str]] = []

    def embedder(paths) -> np.ndarray:
        names = [Path(p).name for p in paths]
        calls.append(names)
        row_digests: list[str] = []
        rows = []
        for path in paths:
            payload = Path(path).read_bytes()
            digest = hashlib.sha256(payload).hexdigest()
            row_digests.append(digest)
            rows.append(deterministic_vector(digest))
        digests.append(row_digests)
        return np.stack(rows).astype(np.float32)

    embedder.calls = calls  # type: ignore[attr-defined]
    embedder.digests = digests  # type: ignore[attr-defined]
    if counter is not None:
        counter["image_embed_calls"] = calls
    return embedder


def make_text_embedder(mapping: dict[str, np.ndarray] | None = None):
    mapping = mapping or {}

    def embedder(texts) -> np.ndarray:
        rows = []
        for text in texts:
            rows.append(mapping.get(text, deterministic_vector(text)))
        return np.stack(rows).astype(np.float32)

    return embedder


def synth_video(
    path: Path,
    *,
    seconds: float = 10.0,
    fps: int = 10,
    size: str = "64x48",
    colour: str = "red",
    vfr: bool = False,
) -> Path:
    """Generate a tiny synthetic video.  Deterministic, offline, tiny."""
    if FFMPEG is None:
        pytest.skip("ffmpeg not available")
    path.parent.mkdir(parents=True, exist_ok=True)
    if vfr:
        cmd = [
            FFMPEG, "-v", "error", "-y",
            "-f", "lavfi", "-i", f"color=c={colour}:s={size}:d={seconds}:r={fps}",
            "-vf", "select='not(mod(n\\,3))+not(mod(n\\,5))'",
            "-fps_mode", "vfr", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path),
        ]
    else:
        cmd = [
            FFMPEG, "-v", "error", "-y",
            "-f", "lavfi", "-i", f"color=c={colour}:s={size}:d={seconds}:r={fps}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path),
        ]
    subprocess.run(cmd, check=True, capture_output=True)
    return path


@pytest.fixture()
def two_synth_videos(tmp_path: Path) -> tuple[Path, Path]:
    a = synth_video(tmp_path / "media" / "a.mp4", colour="red", seconds=10.0)
    b = synth_video(tmp_path / "media" / "b.mp4", colour="blue", seconds=10.0)
    return a, b


PROCESSOR_ASSET_NAMES = (
    "config.json",
    "preprocessor_config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
    "spiece.model",
)


def make_model_root(root: Path) -> Path:
    """Create a local model root with the required processor assets.

    Only the small text/config assets are needed to derive semantic-space
    identity; the large weights file is never fabricated or downloaded.  Tests
    that exercise real loading pass an explicit weights digest instead.
    """
    root.mkdir(parents=True, exist_ok=True)
    for name in PROCESSOR_ASSET_NAMES:
        (root / name).write_bytes(f"synthetic-asset::{name}".encode("utf-8"))
    return root


def canonical_cli_identity(model_root: Path) -> dict:
    """The exact space identity the CLI derives from ``model_root``.

    Tests index with this identity so the query CLI resolves the same
    generation instead of asserting a self-inconsistent space.
    """
    import hashlib

    from persistent_local_index.model_space import digest_processor_assets

    weights_sha = hashlib.sha256((Path(model_root) / "model.safetensors").read_bytes()).hexdigest()
    return {
        "processor_digest": digest_processor_assets(Path(model_root)),
        "image_preprocessing_digest": hashlib.sha256(
            (Path(model_root) / "preprocessor_config.json").read_bytes()
        ).hexdigest(),
        "weights_sha256": weights_sha,
        "model_identity": "google/siglip-base-patch16-224",
        "frozen_revision": "7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed",
        "text_preprocessing_contract": "padding=max_length",
        "embedding_dim": 768,
        "dtype": "float32",
        "normalization": "l2",
    }


@pytest.fixture()
def synthetic_model_root(tmp_path: Path) -> Path:
    root = make_model_root(tmp_path / "model")
    # A synthetic weights blob so the CLI's digest check has a stable target.
    (root / "model.safetensors").write_bytes(b"synthetic-weights-blob")
    return root
