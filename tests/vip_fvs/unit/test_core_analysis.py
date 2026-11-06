"""Unit tests for single-video query-driven semantic analysis orchestration (core_analysis.py)."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sqlite3
from types import SimpleNamespace
from typing import Any
import unittest

try:
    import pytest
except ImportError:  # pragma: no cover

    class _RaisesContext:
        def __init__(self, exc_type):
            self.exc_type = exc_type
            self.value = None

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, _tb):
            if exc_type is None:
                raise AssertionError(
                    f"Expected {self.exc_type}, but no exception was raised"
                )
            if not issubclass(exc_type, self.exc_type):
                return False
            self.value = exc_val
            return True

    class _PytestShim:
        @staticmethod
        def raises(exc_type):
            return _RaisesContext(exc_type)

    pytest = _PytestShim()  # type: ignore[assignment]

try:
    import numpy as _np  # noqa: F401
    from PIL import Image as _pil_img  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover
    import sys
    import types

    if "numpy" not in sys.modules:
        _stub_np = types.ModuleType("numpy")
        _stub_np.ndarray = object  # type: ignore[attr-defined]
        _stub_np.float32 = float  # type: ignore[attr-defined]
        _stub_np.float64 = float  # type: ignore[attr-defined]
        _stub_np.dtype = lambda *_a, **_kw: types.SimpleNamespace(itemsize=4)  # type: ignore[attr-defined]
        sys.modules["numpy"] = _stub_np
    if "PIL" not in sys.modules:
        _stub_pil = types.ModuleType("PIL")
        _stub_pil.Image = types.SimpleNamespace(Image=object, open=lambda *_a, **_kw: None)  # type: ignore[attr-defined]
        sys.modules["PIL"] = _stub_pil
        sys.modules["PIL.Image"] = _stub_pil.Image  # type: ignore[assignment]

from vip_fvs.core_analysis import (
    CoreAnalysisRefusal,
    CoreAnalysisRequest,
    analyze_local_video,
    _invoke_engine_index_source,
    _invoke_engine_query,
)
from vip_fvs.core_report import (
    NOT_OBSERVED,
    compute_core_report_digest,
    validate_core_semantic_report,
)
from vip_fvs.real_source_probe import RealSourceProbeBinding


@dataclass(frozen=True)
class _StubSpace:
    model_identity: str = "vip-fvs-fake-embedder"
    frozen_revision: str = "synthetic-v1"
    weights_sha256: str = "0" * 64
    processor_digest: str = "0" * 64
    image_preprocessing_digest: str = "0" * 64
    text_preprocessing_contract: str = "padding=max_length"
    embedding_dim: int = 768
    dtype: str = "float32"
    normalization: str = "l2"
    space_id: str = "b" * 64
    model_family: str = "synthetic_fake"


@dataclass(frozen=True)
class _StubSpec:
    schema_version: int = 1
    generation_id: str = "c" * 64
    space: _StubSpace = _StubSpace()
    space_id: str = "b" * 64
    sampling_policy_id: str = "coarse-pts-4.5s"
    sampling_policy_version: int = 1
    sampling_interval_seconds: float = 4.5
    selected_stream_policy: str = "first-video-stream"


@dataclass(frozen=True)
class _StubHit:
    query: str
    rank: int
    score: float
    row_id: int
    source_path: str
    source_sha256: str
    pts: int
    timebase_num: int
    timebase_den: int
    timestamp_human: str
    thumbnail_path: str | None = None
    thumbnail_status: str = "NOT_OBSERVED"
    stream_index: int | None = None


def _make_source_file(path: Path, content: bytes = b"synthetic-video-bytes-v1") -> tuple[str, int]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return hashlib.sha256(content).hexdigest(), len(content)


def _make_probe_fn(
    *,
    selected_stream_index: int = 1,
    timebase_num: int = 1001,
    timebase_den: int = 30000,
    counter: list[int] | None = None,
):
    def _probe(
        source_path: str | Path,
        *,
        executable: str | Path = "/usr/bin/ffprobe",
        timeout_seconds: float | None = 600.0,
        selected_stream_index: int | None = selected_stream_index,
        source_revision_id: str = "rev-001",
        policy_identity: str = "vip_fvs.core_analyze_local.v1",
        run_dir: str | Path | None = None,
        runner: Any = None,
        source_locator: str | None = None,
        snapshot_evidence: Any = None,
    ) -> RealSourceProbeBinding:
        if counter is not None:
            counter.append(1)
        p = Path(source_path)
        raw = p.read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        eff_stream = (
            selected_stream_index
            if selected_stream_index is not None
            else 1
        )
        return RealSourceProbeBinding(
            source_path=p,
            source_revision_id=source_revision_id,
            source_sha256=sha,
            source_byte_count=len(raw),
            selected_stream_index=eff_stream,
            timebase_num=timebase_num,
            timebase_den=timebase_den,
            ffprobe_json={"streams": [{"index": eff_stream, "codec_type": "video"}]},
            probe_digest="d" * 64,
            probe_artifact_ref=f"probe:{sha[:12]}",
            raw_probe_artifact_ref=f"raw:{sha[:12]}",
            canonical_probe_artifact_ref=f"canon:{sha[:12]}",
            policy_identity=policy_identity,
            source_locator=source_locator,
            snapshot_evidence=snapshot_evidence,
        )

    return _probe


class _SqliteBackedStubEngine:
    """Stub engine that populates the real persistent_local_index SQLite tables for deterministic tests."""

    def __init__(
        self,
        *,
        spec: _StubSpec | None = None,
        sample_rows: list[tuple[int, int, float]] | None = None,
        stream_index: int = 1,
        timebase: tuple[int, int] = (1001, 30000),
        omit_sample_verification_record: bool = False,
        return_empty_hits: bool = False,
        extra_foreign_hit_sha: str | None = None,
        index_counter: list[int] | None = None,
    ) -> None:
        self._spec = spec or _StubSpec()
        self._sample_rows = (
            sample_rows
            if sample_rows is not None
            else [(0, 0, 0.42), (1, 45045, 0.91), (2, 90090, 0.77)]
        )
        self._stream_index = stream_index
        self._timebase = timebase
        self._omit_sample_verification_record = omit_sample_verification_record
        self._return_empty_hits = return_empty_hits
        self._extra_foreign_hit_sha = extra_foreign_hit_sha
        self._index_counter = index_counter

    def build_generation_spec(self, space: Any) -> _StubSpec:
        return self._spec

    def index_source(
        self,
        input_path: Path,
        index_root: Path,
        spec: Any,
        image_embedder: Any,
    ) -> dict[str, int]:
        if self._index_counter is not None:
            self._index_counter.append(1)
        raw = Path(input_path).read_bytes()
        sha = hashlib.sha256(raw).hexdigest()
        gen_dir = Path(index_root) / "generations" / str(spec.generation_id)
        gen_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = gen_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "generation_id": str(spec.generation_id),
                    "space_id": str(spec.space_id),
                    "schema_version": 1,
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        db_path = gen_dir / "index.sqlite"
        conn = sqlite3.connect(str(db_path))
        try:
            with conn:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS generation_state (
                        generation_id TEXT PRIMARY KEY,
                        schema_version INTEGER NOT NULL,
                        space_id TEXT NOT NULL,
                        sampling_policy_id TEXT NOT NULL,
                        sampling_policy_version INTEGER NOT NULL,
                        sampling_interval_seconds REAL NOT NULL,
                        committed_row_count INTEGER NOT NULL,
                        committed_vector_bytes INTEGER NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS source_objects (
                        source_sha256 TEXT PRIMARY KEY,
                        source_revision TEXT,
                        size_bytes INTEGER NOT NULL,
                        stream_index INTEGER NOT NULL,
                        codec TEXT NOT NULL,
                        width INTEGER NOT NULL,
                        height INTEGER NOT NULL,
                        timebase_num INTEGER NOT NULL,
                        timebase_den INTEGER NOT NULL,
                        duration_seconds REAL NOT NULL,
                        state TEXT NOT NULL,
                        row_start INTEGER,
                        row_end INTEGER,
                        indexed_at TEXT NOT NULL,
                        active INTEGER NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS source_locations (
                        path TEXT PRIMARY KEY,
                        source_sha256 TEXT NOT NULL,
                        last_observed_size INTEGER NOT NULL,
                        last_observed_mtime_ns INTEGER NOT NULL,
                        last_observed_at TEXT NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS samples (
                        row_id INTEGER PRIMARY KEY,
                        source_sha256 TEXT NOT NULL,
                        stream_index INTEGER NOT NULL,
                        pts INTEGER NOT NULL,
                        timebase_num INTEGER NOT NULL,
                        timebase_den INTEGER NOT NULL,
                        pts_time REAL NOT NULL,
                        timestamp_human TEXT NOT NULL,
                        thumbnail_relpath TEXT NOT NULL,
                        active INTEGER NOT NULL
                    );
                    """
                )
                already_exists = (
                    conn.execute(
                        "SELECT 1 FROM source_objects WHERE source_sha256 = ?",
                        (sha,),
                    ).fetchone()
                    is not None
                )
                if not already_exists:
                    conn.execute(
                        "INSERT OR REPLACE INTO generation_state VALUES (?, 1, ?, ?, ?, ?, ?, ?)",
                        (
                            str(spec.generation_id),
                            str(spec.space_id),
                            str(spec.sampling_policy_id),
                            int(spec.sampling_policy_version),
                            float(spec.sampling_interval_seconds),
                            len(self._sample_rows),
                            len(self._sample_rows) * 3072,
                        ),
                    )
                    conn.execute(
                        "INSERT INTO source_objects VALUES (?, NULL, ?, ?, 'h264', 320, 240, ?, ?, 10.0, 'COMPLETE', 0, ?, '2026-11-05T00:00:00Z', 1)",
                        (
                            sha,
                            len(raw),
                            self._stream_index,
                            self._timebase[0],
                            self._timebase[1],
                            len(self._sample_rows),
                        ),
                    )
                    conn.execute(
                        "INSERT OR REPLACE INTO source_locations VALUES (?, ?, ?, 100, '2026-11-05T00:00:00Z')",
                        (str(input_path), sha, len(raw)),
                    )
                    if not self._omit_sample_verification_record:
                        for row_id, pts, _score in self._sample_rows:
                            conn.execute(
                                "INSERT INTO samples VALUES (?, ?, ?, ?, ?, ?, ?, '00:00:01.501', ?, 1)",
                                (
                                    row_id,
                                    sha,
                                    self._stream_index,
                                    pts,
                                    self._timebase[0],
                                    self._timebase[1],
                                    (pts * self._timebase[0]) / self._timebase[1],
                                    f"thumbnails/{sha}/{pts}.jpg",
                                ),
                            )
                    return {"indexed": 1, "skipped": 0, "reused": 0, "failed": 0}
                return {"indexed": 0, "skipped": 1, "reused": 0, "failed": 0}
        finally:
            conn.close()

    def query(
        self,
        index_root: Path,
        spec: Any,
        texts: list[str],
        text_embedder: Any,
        *,
        top_k: int,
    ) -> dict[str, tuple[_StubHit, ...]]:
        q = texts[0]
        if self._return_empty_hits:
            return {q: ()}
        gen_dir = Path(index_root) / "generations" / str(spec.generation_id)
        conn = sqlite3.connect(str(gen_dir / "index.sqlite"))
        try:
            sha_row = conn.execute(
                "SELECT source_sha256 FROM source_objects LIMIT 1"
            ).fetchone()
            sha = str(sha_row[0])
        finally:
            conn.close()

        hits: list[_StubHit] = []
        for idx, (row_id, pts, score) in enumerate(self._sample_rows, start=1):
            hits.append(
                _StubHit(
                    query=q,
                    rank=idx,
                    score=score,
                    row_id=row_id,
                    source_path="/tmp/source.mp4",
                    source_sha256=(
                        self._extra_foreign_hit_sha
                        if self._extra_foreign_hit_sha is not None and idx == 1
                        else sha
                    ),
                    pts=pts,
                    timebase_num=self._timebase[0],
                    timebase_den=self._timebase[1],
                    timestamp_human="00:00:01.501",
                )
            )
        return {q: tuple(hits[:top_k])}


def _make_stub_runtime(space: _StubSpace | None = None, *, fake: bool = True) -> Any:
    sp = space or _StubSpace()
    return SimpleNamespace(
        semantic_space=sp,
        runtime_identity="vip-fvs-fake-runtime/v1" if fake else "google/siglip-base-patch16-224",
        fake=fake,
        image_embedder=lambda paths: None,
        text_embedder=lambda texts: None,
    )


def test_positive_multi_hit_fewer_hits_and_zero_match_runs(tmp_path: Path) -> None:
    source_path = tmp_path / "ballet.mp4"
    source_sha, source_bytes = _make_source_file(source_path)
    before_mtime = source_path.stat().st_mtime_ns

    # 1. Positive multi-hit with fewer eligible hits than top_k (3 hits < top_k=5, no dummy padding)
    index_root = tmp_path / "idx1"
    out_root = tmp_path / "out1"
    engine = _SqliteBackedStubEngine(
        sample_rows=[(0, 0, 0.42), (1, 45045, 0.91), (2, 90090, 0.77)],
        stream_index=1,
        timebase=(1001, 30000),
    )
    outcome = analyze_local_video(
        CoreAnalysisRequest(
            source_path=source_path,
            query="  swan   lake  adagio ",
            index_root=index_root,
            output_root=out_root,
            attempt_id="att-pos-1",
            source_revision_id="rev-pos-1",
            top_k=5,
            fake_embedder=True,
            selected_stream_index=1,
            runtime=_make_stub_runtime(),
            engine=engine,
            probe_fn=_make_probe_fn(selected_stream_index=1),
        )
    )
    assert outcome.report["stage_status"] == "SUCCEEDED"
    assert outcome.report["result_kind"] == "MATCHES_FOUND"
    assert outcome.report["top_k"] == 5
    assert outcome.report["returned_candidate_count"] == 3
    assert outcome.report["total_eligible_matches"] == 3
    assert [m["row_id"] for m in outcome.report["matches"]] == [1, 2, 0]
    assert [m["rank"] for m in outcome.report["matches"]] == [1, 2, 3]
    assert outcome.report["matches"][0]["selected_stream_index"] == 1
    assert outcome.report["matches"][0]["sampled_timing"]["rational_seconds"] == {
        "num": 3006003,
        "den": 2000,
        "canonical": "3006003/2000",
    }
    assert (
        outcome.report["matches"][0]["sampled_timing"][
            "display_only_not_frame_authority"
        ]
        is True
    )
    assert outcome.report["runtime_mode"] == "SYNTHETIC"
    assert outcome.report["model"]["authentic_inference_observed"] is False
    assert outcome.report_path.is_file()
    validate_core_semantic_report(
        json.loads(outcome.report_path.read_text(encoding="utf-8"))
    )

    # Source immutability preserved
    assert source_path.read_bytes() == b"synthetic-video-bytes-v1"
    assert source_path.stat().st_size == source_bytes
    assert source_path.stat().st_mtime_ns == before_mtime

    # 2. Zero-match run
    out_zero = tmp_path / "out_zero"
    zero_engine = _SqliteBackedStubEngine(return_empty_hits=True, stream_index=1)
    zero_outcome = analyze_local_video(
        CoreAnalysisRequest(
            source_path=source_path,
            query="unmatched movement phrase",
            index_root=tmp_path / "idx_zero",
            output_root=out_zero,
            attempt_id="att-zero-1",
            source_revision_id="rev-pos-1",
            top_k=5,
            fake_embedder=True,
            selected_stream_index=1,
            runtime=_make_stub_runtime(),
            engine=zero_engine,
            probe_fn=_make_probe_fn(selected_stream_index=1),
        )
    )
    assert zero_outcome.report["stage_status"] == "SUCCEEDED"
    assert zero_outcome.report["result_kind"] == "ZERO_MATCH"
    assert zero_outcome.report["returned_candidate_count"] == 0
    assert zero_outcome.report["total_eligible_matches"] == 0
    assert zero_outcome.report["matches"] == []


def test_deterministic_tie_breaking_on_equal_scores(tmp_path: Path) -> None:
    source_path = tmp_path / "ties.mp4"
    _make_source_file(source_path)
    engine = _SqliteBackedStubEngine(
        sample_rows=[
            (4, 9000, 0.800000),
            (2, 3000, 0.800000),
            (1, 3000, 0.800000),
            (0, 1000, 0.950000),
        ],
        stream_index=2,
        timebase=(1, 90000),
    )
    outcome = analyze_local_video(
        CoreAnalysisRequest(
            source_path=source_path,
            query="pirouette",
            index_root=tmp_path / "idx_ties",
            output_root=tmp_path / "out_ties",
            attempt_id="att-ties",
            source_revision_id="rev-ties",
            top_k=4,
            fake_embedder=True,
            selected_stream_index=2,
            runtime=_make_stub_runtime(),
            engine=engine,
            probe_fn=_make_probe_fn(
                selected_stream_index=2, timebase_num=1, timebase_den=90000
            ),
        )
    )
    assert [(m["row_id"], m["sampled_timing"]["pts"]) for m in outcome.report["matches"]] == [
        (0, 1000),
        (1, 3000),
        (2, 3000),
        (4, 9000),
    ]


def test_near_equal_scores_keep_exact_score_order(tmp_path: Path) -> None:
    source_path = tmp_path / "near-ties.mp4"
    _make_source_file(source_path)
    engine = _SqliteBackedStubEngine(
        sample_rows=[(1, 3000, 0.5000000000003), (2, 9000, 0.5000000000004)],
        stream_index=1,
        timebase=(1, 90000),
    )
    outcome = analyze_local_video(CoreAnalysisRequest(
        source_path=source_path, query="near tie", index_root=tmp_path / "idx",
        output_root=tmp_path / "out", attempt_id="att-near-tie",
        source_revision_id="rev-near-tie", top_k=2, fake_embedder=True,
        selected_stream_index=1, runtime=_make_stub_runtime(), engine=engine,
        probe_fn=_make_probe_fn(selected_stream_index=1, timebase_num=1, timebase_den=90000),
    ))
    assert [m["row_id"] for m in outcome.report["matches"]] == [2, 1]


def test_index_summary_without_disposition_is_refused(tmp_path: Path) -> None:
    source_path = tmp_path / "empty-summary.mp4"
    _make_source_file(source_path)
    engine = _SqliteBackedStubEngine(stream_index=1)
    engine.index_source = lambda *_args, **_kwargs: {}  # type: ignore[method-assign]
    with pytest.raises(CoreAnalysisRefusal, match="INDEX_SUMMARY_INVALID"):
        analyze_local_video(CoreAnalysisRequest(
            source_path=source_path, query="query", index_root=tmp_path / "idx",
            output_root=tmp_path / "out", attempt_id="att-empty-summary",
            source_revision_id="rev-empty-summary", fake_embedder=True,
            selected_stream_index=1, runtime=_make_stub_runtime(), engine=engine,
            probe_fn=_make_probe_fn(selected_stream_index=1),
        ))


def test_index_summary_rejects_malformed_counts() -> None:
    class Engine:
        def __init__(self, summary: Any) -> None:
            self.summary = summary
        def index_source(self, *_args: Any, **_kwargs: Any) -> Any:
            return self.summary

    for summary in (
        {"indexed": True, "skipped": 0, "reused": 0, "failed": 0},
        {"indexed": -1, "skipped": 0, "reused": 0, "failed": 0},
        {"indexed": 0, "skipped": 0, "reused": 0, "failed": 0},
    ):
        with pytest.raises(CoreAnalysisRefusal, match="INDEX_SUMMARY_INVALID"):
            _invoke_engine_index_source(
                Engine(summary), source_path=Path("synthetic"),
                index_root=Path("index"), spec=object(), runtime=object(),
            )


def test_engine_internal_typeerror_is_not_retried() -> None:
    class Engine:
        calls = 0
        def index_source(self, *args: Any, **kwargs: Any) -> Any:
            self.calls += 1
            raise TypeError("backend bug")
    engine = Engine()
    with pytest.raises(TypeError, match="backend bug"):
        _invoke_engine_index_source(engine, source_path=Path("x"), index_root=Path("i"), spec=object(), runtime=object())
    assert engine.calls == 1

    class QueryEngine:
        calls = 0
        def query(self, *args: Any, **kwargs: Any) -> Any:
            self.calls += 1
            raise TypeError("query backend bug")
    query_engine = QueryEngine()
    with pytest.raises(TypeError, match="query backend bug"):
        _invoke_engine_query(query_engine, index_root=Path("i"), spec=SimpleNamespace(generation_id="g"), query_text="q", runtime=object(), top_k=1)
    assert query_engine.calls == 1


def test_probe_internal_typeerror_is_not_retried(tmp_path: Path) -> None:
    source_path = tmp_path / "probe-typeerror.mp4"
    _make_source_file(source_path)
    calls: list[int] = []
    def probe(*_args: Any, **_kwargs: Any) -> Any:
        calls.append(1)
        raise TypeError("probe backend bug")
    with pytest.raises(TypeError, match="probe backend bug"):
        analyze_local_video(CoreAnalysisRequest(
            source_path=source_path, query="query", index_root=tmp_path / "idx",
            output_root=tmp_path / "out", attempt_id="att-probe-typeerror",
            source_revision_id="rev-probe-typeerror", fake_embedder=True,
            selected_stream_index=1, runtime=_make_stub_runtime(),
            engine=_SqliteBackedStubEngine(stream_index=1), probe_fn=probe,
        ))
    assert calls == [1]


def test_audio_first_stream_misbinding_and_unverified_search_hit_rejected(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "audio_first.mp4"
    _make_source_file(source_path)

    # Probe sees video on absolute stream 2, but index recorded stream 1 -> refused
    mismatched_engine = _SqliteBackedStubEngine(stream_index=1)
    with pytest.raises(CoreAnalysisRefusal) as exc_info:
        analyze_local_video(
            CoreAnalysisRequest(
                source_path=source_path,
                query="coda",
                index_root=tmp_path / "idx_mismatch",
                output_root=tmp_path / "out_mismatch",
                attempt_id="att-stream-err",
                source_revision_id="rev-stream",
                fake_embedder=True,
                selected_stream_index=2,
                runtime=_make_stub_runtime(),
                engine=mismatched_engine,
                probe_fn=_make_probe_fn(selected_stream_index=2),
            )
        )
    assert exc_info.value.code == "INDEX_STREAM_IDENTITY_MISMATCH"

    # SearchHit without independently verified sample stream record in SQLite or engine -> refused
    unverified_hit_engine = _SqliteBackedStubEngine(
        sample_rows=[(0, 1001, 0.9)],
        stream_index=1,
        omit_sample_verification_record=True,
    )
    # Also test custom in-memory engine returning a bare SearchHit without verified_sample_records
    bare_hit = _StubHit(
        query="coda",
        rank=1,
        score=0.9,
        row_id=7,
        source_path=str(source_path),
        source_sha256=hashlib.sha256(source_path.read_bytes()).hexdigest(),
        pts=1001,
        timebase_num=1001,
        timebase_den=30000,
        timestamp_human="00:00:00.033",
    )
    bare_engine = SimpleNamespace(
        build_generation_spec=lambda _sp: _StubSpec(),
        index_source=lambda *_a, **_kw: {"indexed": 1, "skipped": 0, "reused": 0, "failed": 0},
        query=lambda *_a, **_kw: {"coda": (bare_hit,)},
        single_source_verified=True,
    )
    with pytest.raises(CoreAnalysisRefusal) as exc_bare:
        analyze_local_video(
            CoreAnalysisRequest(
                source_path=source_path,
                query="coda",
                index_root=tmp_path / "idx_bare",
                output_root=tmp_path / "out_bare",
                attempt_id="att-bare-hit",
                source_revision_id="rev-stream",
                fake_embedder=True,
                selected_stream_index=1,
                runtime=_make_stub_runtime(),
                engine=bare_engine,
                probe_fn=_make_probe_fn(selected_stream_index=1),
            )
        )
    assert exc_bare.value.code == "HIT_STREAM_METADATA_UNVERIFIED"


def test_multi_source_index_and_occurrence_revision_collisions_refused(
    tmp_path: Path,
) -> None:
    source_a = tmp_path / "dir_a" / "clip.mp4"
    source_b_same_bytes = tmp_path / "dir_b" / "clip_copy.mp4"
    _make_source_file(source_a, b"identical-media-bytes")
    _make_source_file(source_b_same_bytes, b"identical-media-bytes")

    idx_root = tmp_path / "shared_idx"
    engine = _SqliteBackedStubEngine(stream_index=1)

    # First run indexes source_a under rev-A
    analyze_local_video(
        CoreAnalysisRequest(
            source_path=source_a,
            query="arabesque",
            index_root=idx_root,
            output_root=tmp_path / "out_a",
            attempt_id="att-a",
            source_revision_id="rev-A",
            fake_embedder=True,
            selected_stream_index=1,
            runtime=_make_stub_runtime(),
            engine=engine,
            probe_fn=_make_probe_fn(selected_stream_index=1),
        )
    )

    # Same source_a with mismatched revision rev-B -> refused
    with pytest.raises(CoreAnalysisRefusal) as exc_rev:
        analyze_local_video(
            CoreAnalysisRequest(
                source_path=source_a,
                query="arabesque",
                index_root=idx_root,
                output_root=tmp_path / "out_rev_mismatch",
                attempt_id="att-rev-mismatch",
                source_revision_id="rev-B",
                fake_embedder=True,
                selected_stream_index=1,
                runtime=_make_stub_runtime(),
                engine=engine,
                probe_fn=_make_probe_fn(selected_stream_index=1),
            )
        )
    assert exc_rev.value.code == "SOURCE_REVISION_MISMATCH"

    # Different occurrence path source_b_same_bytes with identical SHA -> refused
    with pytest.raises(CoreAnalysisRefusal) as exc_occ:
        analyze_local_video(
            CoreAnalysisRequest(
                source_path=source_b_same_bytes,
                query="arabesque",
                index_root=idx_root,
                output_root=tmp_path / "out_occ_mismatch",
                attempt_id="att-occ-mismatch",
                source_revision_id="rev-A",
                fake_embedder=True,
                selected_stream_index=1,
                runtime=_make_stub_runtime(),
                engine=engine,
                probe_fn=_make_probe_fn(selected_stream_index=1),
            )
        )
    assert exc_occ.value.code == "SOURCE_OCCURRENCE_MISMATCH"

    # Different source with different SHA in same generation -> MULTI_SOURCE_INDEX_UNSUPPORTED
    source_other = tmp_path / "other.mp4"
    _make_source_file(source_other, b"completely-different-video-bytes")
    with pytest.raises(CoreAnalysisRefusal) as exc_multi:
        analyze_local_video(
            CoreAnalysisRequest(
                source_path=source_other,
                query="arabesque",
                index_root=idx_root,
                output_root=tmp_path / "out_multi",
                attempt_id="att-multi",
                source_revision_id="rev-other",
                fake_embedder=True,
                selected_stream_index=1,
                runtime=_make_stub_runtime(),
                engine=engine,
                probe_fn=_make_probe_fn(selected_stream_index=1),
            )
        )
    assert exc_multi.value.code == "MULTI_SOURCE_INDEX_UNSUPPORTED"


def test_semantic_space_mismatch_across_v1_v2_base_and_so400m_refused(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "video.mp4"
    _make_source_file(source_path)

    v1_space = _StubSpace(
        model_identity="google/siglip-base-patch16-224",
        embedding_dim=768,
        space_id="1" * 64,
        model_family="siglip",
    )
    v2_base_space = _StubSpace(
        model_identity="google/siglip2-base-patch16-224",
        embedding_dim=768,
        space_id="2" * 64,
        model_family="siglip2",
    )
    so400m_space = _StubSpace(
        model_identity="google/siglip2-so400m-patch14-384",
        embedding_dim=1152,
        space_id="3" * 64,
        model_family="siglip2",
    )

    # Engine spec built for V1 cannot be used with V2 Base or SO400M runtime
    v1_engine = _SqliteBackedStubEngine(spec=_StubSpec(space=v1_space, space_id="1" * 64))
    for mismatched_space in (v2_base_space, so400m_space):
        with pytest.raises(CoreAnalysisRefusal) as exc_space:
            analyze_local_video(
                CoreAnalysisRequest(
                    source_path=source_path,
                    query="leap",
                    index_root=tmp_path / "idx_space",
                    output_root=tmp_path / f"out_{mismatched_space.space_id[:4]}",
                    attempt_id="att-space",
                    source_revision_id="rev-space",
                    fake_embedder=True,
                    selected_stream_index=1,
                    runtime=_make_stub_runtime(mismatched_space),
                    engine=v1_engine,
                    probe_fn=_make_probe_fn(selected_stream_index=1),
                )
            )
        assert exc_space.value.code == "INDEX_SPEC_SEMANTIC_SPACE_MISMATCH"


def test_real_mode_authorization_enforced_before_source_probe_or_index(
    tmp_path: Path,
) -> None:
    source_path = tmp_path / "protected.mp4"
    source_sha, _ = _make_source_file(source_path)
    probe_calls: list[int] = []
    index_calls: list[int] = []
    engine = _SqliteBackedStubEngine(index_counter=index_calls)
    probe_fn = _make_probe_fn(counter=probe_calls)

    # 1. Missing authorization in real mode -> refused before probe or index
    with pytest.raises(CoreAnalysisRefusal) as exc_missing:
        analyze_local_video(
            CoreAnalysisRequest(
                source_path=source_path,
                query="solo variation",
                index_root=tmp_path / "idx_real",
                output_root=tmp_path / "out_real1",
                attempt_id="att-real-1",
                source_revision_id="rev-real-1",
                fake_embedder=False,
                runtime=_make_stub_runtime(fake=False),
                engine=engine,
                probe_fn=probe_fn,
            )
        )
    assert exc_missing.value.code == "AUTHORIZATION_REQUIRED_BEFORE_REAL_SOURCE_ACCESS"
    assert probe_calls == []
    assert index_calls == []

    # 2. Revoked / expired authorization in real mode -> refused before probe or index
    auth_payload = {
        "source_path": str(source_path.resolve()),
        "source_sha256": source_sha,
        "purpose": "local pilot test",
        "model_root": str((tmp_path / "model").resolve()),
        "model_revision": "rev-model",
        "weights_sha256": "0" * 64,
        "runtime_root": str(tmp_path.resolve()),
        "index_root": str((tmp_path / "idx_real").resolve()),
        "output_root": str((tmp_path / "out_real2").resolve()),
        "allowed_stages": ["decode", "embed", "index", "query"],
        "authorization_id": "auth-1",
        "source_revision_id": "rev-real-1",
        "model_identity": "google/siglip-base-patch16-224",
        "query_digest": hashlib.sha256(b'"solo variation"').hexdigest(),
        "semantic_space_id": "b" * 64,
        "index_digest": "e" * 64,
        "local_only": True,
        "expires_at": "2020-01-01T00:00:00Z",
        "revoked": True,
        "selected_stream_index": 1,
        "policy_digest": "1" * 64,
        "scope_digest": "2" * 64,
    }
    auth_payload["record_digest"] = hashlib.sha256(
        json.dumps(auth_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    auth_file = tmp_path / "revoked_auth.json"
    auth_file.write_text(json.dumps(auth_payload), encoding="utf-8")

    with pytest.raises(CoreAnalysisRefusal) as exc_revoked:
        analyze_local_video(
            CoreAnalysisRequest(
                source_path=source_path,
                query="solo variation",
                index_root=tmp_path / "idx_real",
                output_root=tmp_path / "out_real2",
                attempt_id="att-real-2",
                source_revision_id="rev-real-1",
                fake_embedder=False,
                pilot_authorization_path=auth_file,
                model_root=tmp_path / "model",
                model_identity="google/siglip-base-patch16-224",
                model_revision="rev-model",
                weights_sha256="0" * 64,
                source_snapshot_root=tmp_path / "snaps",
                max_source_bytes=1024 * 1024,
                max_store_bytes=10 * 1024 * 1024,
                runtime=_make_stub_runtime(fake=False),
                engine=engine,
                probe_fn=probe_fn,
            )
        )
    assert exc_revoked.value.code == "PILOT_AUTHORIZATION_REVOKED"
    assert probe_calls == []
    assert index_calls == []


def test_fake_real_ambiguity_and_invalid_query_or_top_k_refused(tmp_path: Path) -> None:
    source_path = tmp_path / "clip.mp4"
    _make_source_file(source_path)

    # Fake + real model flag ambiguity
    with pytest.raises(CoreAnalysisRefusal) as exc_amb:
        analyze_local_video(
            CoreAnalysisRequest(
                source_path=source_path,
                query="ensemble",
                index_root=tmp_path / "idx",
                output_root=tmp_path / "out1",
                attempt_id="att-amb",
                source_revision_id="rev-1",
                fake_embedder=True,
                model_root=tmp_path / "model",
            )
        )
    assert exc_amb.value.code == "FAKE_AND_REAL_MODE_INPUTS_ARE_AMBIGUOUS"

    # Empty/whitespace query
    with pytest.raises(CoreAnalysisRefusal) as exc_q:
        analyze_local_video(
            CoreAnalysisRequest(
                source_path=source_path,
                query="   \t\n  ",
                index_root=tmp_path / "idx",
                output_root=tmp_path / "out2",
                attempt_id="att-q",
                source_revision_id="rev-1",
                fake_embedder=True,
            )
        )
    assert exc_q.value.code == "TEXT_QUERY_REQUIRED"

    # Invalid top_k <= 0
    with pytest.raises(CoreAnalysisRefusal) as exc_topk:
        analyze_local_video(
            CoreAnalysisRequest(
                source_path=source_path,
                query="valid query",
                index_root=tmp_path / "idx",
                output_root=tmp_path / "out3",
                attempt_id="att-topk",
                source_revision_id="rev-1",
                top_k=0,
                fake_embedder=True,
            )
        )
    assert exc_topk.value.code == "INVALID_TOP_K"


class CoreAnalysisStdlibTestCase(unittest.TestCase):
    """Stdlib unittest runner wrapper for test_core_analysis.py."""

    def test_all_core_analysis_scenarios(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            test_positive_multi_hit_fewer_hits_and_zero_match_runs(root / "s1")
            test_deterministic_tie_breaking_on_equal_scores(root / "s2")
            test_audio_first_stream_misbinding_and_unverified_search_hit_rejected(
                root / "s3"
            )
            test_multi_source_index_and_occurrence_revision_collisions_refused(
                root / "s4"
            )
            test_semantic_space_mismatch_across_v1_v2_base_and_so400m_refused(
                root / "s5"
            )
            test_real_mode_authorization_enforced_before_source_probe_or_index(
                root / "s6"
            )
            test_fake_real_ambiguity_and_invalid_query_or_top_k_refused(root / "s7")


if __name__ == "__main__":
    unittest.main()
