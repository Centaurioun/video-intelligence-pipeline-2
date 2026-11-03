# Root G Real-Source Temporal + Revision Closure Implementation Plan

> For agentic workers: REQUIRED SUB-SKILL: use subagent-driven development or executing-plans; all behavior changes use TDD.

**Goal:** Close D-PROV-1 (real-source temporal authority) and D-REALPLAN-1 (decision-to-plan revision binding) in the two Root-G reserved product surfaces, with fail-closed behavior, no second container parser, and no duplicate measurement authority.

**Architecture:** Two independent bounded closures in one milestone.
- *Temporal:* `real_source_service.py` gains a locator-timebase admissibility gate, a frame-presentation-only authoritative endpoint projection, and a pre-publication measured-timebase cross-check that publishes the authoritative Gate-3 timebase. It never parses the container itself.
- *Revision:* `real_plan.py` gains an exact new-decision revision predicate, immediate same-plan prior-revision lineage routed through the existing `gate3.plan.new_revision`, and lineage-preserving save/load.

**Tech Stack:** Python 3.11+, `pytest`, stdlib `json`/`hashlib`. Existing in-repo modules only: `gate3.plan`, `gate3.pts`, `gate3.refinement`, `persistent_local_index.search.SearchHit`. No third-party addition.

**Spec:** `docs/superpowers/specs/2026-09-25-root-g-real-source-temporal-revision-closure-design.md` (frozen; governs this plan).

**Global Constraints:**

- `IMPLEMENTATION_AUTHORIZED=false` at plan time:

```
PLAN_APPROVAL_DOES_NOT_AUTHORIZE_IMPLEMENTATION.
A separate explicit owner implementation authorization is mandatory.
The five-path test authority must be remotely durable before any test write.
```

- **Writable product paths are exactly two, and only after separate explicit implementation authorization:**
  - `src/vip_fvs/real_source_service.py`
  - `src/vip_fvs/real_plan.py`

  No other product path is contemplated and no `src/**` wildcard is granted or implied.
- **Writable test paths are exactly the five enumerated in spec §9.1** (two new files plus three purpose-limited existing fixture files, all allocated by `root-g-test-path-scope-amendment-20260925-v1`). Nothing else in `tests/**` may be created or edited.
- **Never** edit: `src/vip_fvs/cli.py`, `src/gate3/**`, `src/vip_fvs/human_decision.py`, `schemas/vip_fvs/human_decision.json`, `src/vip_fvs/editorial_plan.py`, `tests/vip_fvs/unit/test_real_plan.py`, `tests/vip_fvs/unit/test_real_source_service.py`, `tests/vip_fvs/unit/test_local_preview.py`.
- No float timebase comparison, no nominal FPS, no `seconds × FPS`, no second `parse_iso_bmff_timing` call in `real_source_service.py`.
- No provider/model/network calls, no model or dependency download, no protected/archive media, no real-media execution, no render/export.
- No `main` mutation, no merge, no force push, no destructive Git, no Gate promotion.
- `_observed_pts` keeps its current body and semantics (diagnostic inventory only). `unit/test_real_source_service.py` must stay green and unedited.
- The REAL plan envelope's top-level keys must not change (spec §6.1).
- Every task ends with a bounded commit whose message names the task.
- Implementation must not begin before Task 0 passes.

**Review Focus:** fail-closed behavior over convenience; no silent equivalence between tick domains; no evidence-class promotion; lineage continuity across save/load; no unauthorized path touched.

---

## Interpreter and test-command convention

There is no root pytest configuration in this repository; tests import `vip_fvs`, `gate3`, and `persistent_local_index`, so both `src` and `experiments` must be importable. Resolve the interpreter in Task 0 and then use it consistently as `$PY` in every command below.

```
cd /Users/yusuf/Repos/video-intelligence-pipeline/.worktrees/execution-portfolio-20260924-v1/real-source-editorial-contract-closure
PY=<resolved interpreter>            # see Task 0
export PYTHONPATH="src:experiments"
```

Task 0 records the exact resolved interpreter and the environment-recovery evidence. Do not install anything into a shared project environment; prefer a Goal-local environment if a prerequisite is genuinely missing (repository rule 52–57).

---

## Task 0 — Preflight: authority, base, ownership, environment

**Files:** none written. Read-only gate.

**Interface consumed:** authority records A4/A5, task packet A3, spec §1.3, §1.4, §10.

**Three-anchor model (do not collapse these into one SHA):**

```
ROOT_BASE_SHA=d3b477db97541d7cd2775e7c42381eb4875de519
    immutable historical base; never mutated, never rebased

AUTHORIZED_IMPLEMENTATION_START_SHA=<named by the later explicit owner implementation authorization>
    the exact corrected remote Root-G head the implementation run must start from

APPROVED_SPEC_PLAN_BLOBS=<named by the later explicit owner implementation authorization>
    the exact spec and plan blob SHAs approved for that run
```

**Root-G HEAD is deliberately NOT expected to equal `ROOT_BASE_SHA`.** The authorized documentation-only spec/plan commit legitimately advanced the branch, so at plan time the remote head is `743d1415c7de80c8a3e9ceff980a31f2b17a4acc` with parent `d3b477db…`. A future run MUST NOT stop merely because HEAD has moved past the historical base.

**Steps:**

1. Require that the owner implementation authorization names `AUTHORIZED_IMPLEMENTATION_START_SHA` and `APPROVED_SPEC_PLAN_BLOBS`, then confirm current head equals the named start SHA:

```
git -C /Users/yusuf/Repos/video-intelligence-pipeline/.worktrees/execution-portfolio-20260924-v1/real-source-editorial-contract-closure rev-parse HEAD
```
   Expected: exactly `$AUTHORIZED_IMPLEMENTATION_START_SHA`. If it differs, **HARD STOP** — do not rebase, reset, or cherry-pick to force a match.

2. Confirm `ROOT_BASE_SHA` is an ancestor of the start SHA (documentation commits are expected and permitted between them):

```
git -C <worktree> merge-base --is-ancestor d3b477db97541d7cd2775e7c42381eb4875de519 HEAD && echo ANCESTOR_OK || echo ANCESTOR_VIOLATION
```
   Expected: `ANCESTOR_OK`. Anything else is a **HARD STOP**.

3. Confirm the approved spec/plan blobs at the start SHA equal the owner-approved blobs exactly:

```
git -C <worktree> rev-parse HEAD:docs/superpowers/specs/2026-09-25-root-g-real-source-temporal-revision-closure-design.md
git -C <worktree> rev-parse HEAD:docs/superpowers/plans/2026-09-25-root-g-real-source-temporal-revision-closure-implementation-plan.md
```
   Expected: exactly the blob SHAs named in `APPROVED_SPEC_PLAN_BLOBS`. A mismatch means the approved plan is not what would be executed: **HARD STOP**.

4. Confirm the two product blobs still equal the frozen product baselines (spec §13 trigger):

```
git -C <worktree> rev-parse HEAD:src/vip_fvs/real_source_service.py   # expect 7840268a5cd7775aeb7c64d09cbdd9a1cfe66058
git -C <worktree> rev-parse HEAD:src/vip_fvs/real_plan.py             # expect 02a5798d97b4133f82b69183137fd052f9717bc6
```
   Any difference is `STATUS=ROOT_G_PLAN_CORRECTION_BLOCKED_STALE_PRODUCT_TARGET` equivalent for the implementation run: **HARD STOP**.

5. Confirm the worktree is clean:

```
git -C <worktree> status --porcelain
```
   Expected: empty. Preserve unrelated pre-existing untracked state; never clean, stash, or reset to make this pass.

6. Confirm the five-path test authority is remotely durable:

```
git -C /Users/yusuf/Repos/video-intelligence-pipeline fetch --prune origin
git -C /Users/yusuf/Repos/video-intelligence-pipeline show \
  origin/execution/execution-portfolio-20260924-v1/bootstrap:.orchestration/portfolios/execution-portfolio-20260924-v1/authority/root-g-test-path-scope-amendment-20260925-v1.json | grep -n "total_contemplated_root_g_test_paths"
```
   Expected: `5`. The amendment was introduced at bootstrap `fc21dc587321ba73b82b3cfe3644ce4fcc7c68fe`; later bootstrap commits (for example Root-H allocations) do not invalidate it. If the amendment cannot be resolved, treat the run as blocked on ownership rather than proceeding.

7. **HARD STOP unless an explicit owner implementation authorization exists.** Allocation, reservation, spec approval and plan approval are all explicitly *not* write authority. Record the authorization reference verbatim (its commit/ref and the two anchor values from step 1). If it is absent, stop and report the blocker.

8. Resolve the interpreter and record evidence:

```
python3 -c "import sys; print(sys.version)"
python3 -c "import numpy, PIL, pytest; print('ok')" 2>&1 || echo "MISSING_PREREQ: record exact command/error/runtime and recover per repository rules 52-57"
```
   Record the resolved absolute path as `$PY`, and record the exact `PYTHONPATH` (`src:experiments`) needed for `vip_fvs`, `gate3` and `persistent_local_index` imports.

9. Baseline the authorized suite (read-only):

```
PYTHONPATH="src:experiments" $PY -m pytest tests/vip_fvs -q -p no:cacheprovider
```
   Expected: all currently-collected tests pass (265 at plan time). Any failure here is a pre-existing environment/state issue, **not** TDD RED; diagnose before proceeding.

**Commit:** none (preflight writes nothing).

---

## Task 1 — Temporal locator contract tests (RED)

**Files:**
- Create: `tests/vip_fvs/unit/test_real_source_temporal_authority.py`

**Interface consumed:**
- `vip_fvs.real_source_service.RealSourceRequest`, `RealSourcePreparationRefusal`, `prepare_real_source`
- `vip_fvs.real_source_service._source_pts_interval` (module-private helper, exercised directly for RED)
- `vip_fvs.real_source_probe.RealSourceProbeBinding`
- `persistent_local_index.search.SearchHit`

**Interface produced:** none (test file only).

**Why this is RED:** `_source_pts_interval` currently ignores the locator timebase entirely and selects endpoints from a set that unions frame and packet `pts`. Every case below asserts the post-implementation contract.

**Test body (write exactly this skeleton, filling only marked helpers):**

```python
"""D-PROV-1 temporal-authority closure tests for the REAL preparation boundary."""
from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from vip_fvs.real_source_probe import RealSourceProbeBinding
from vip_fvs.real_source_service import RealSourcePreparationRefusal, _source_pts_interval

PROBE_TB = (1, 1000)

# Sentinel: distinguishes "field omitted entirely" from "field present but None".
_MISSING = object()


def _source(tmp_path: Path) -> Path:
    path = tmp_path / "generated-source.mp4"
    path.write_bytes(b"generated fixture bytes")
    return path


def _probe(source: Path, run_dir: Path, *, frames=(), packets=(), pts_ticks=None) -> RealSourceProbeBinding:
    payload: dict = {
        "streams": [{"index": 0, "codec_type": "video", "time_base": "1/1000"}],
        "stream_index": 0,
        "frames": [
            {"stream_index": 0, "best_effort_timestamp": str(t)} for t in frames
        ],
        "packets": [
            {"stream_index": 0, "pts": str(t)} for t in packets
        ],
    }
    if pts_ticks is not None:
        payload["pts_ticks"] = list(pts_ticks)
    return RealSourceProbeBinding(
        source_path=source,
        source_revision_id="rev-tb-1",
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        source_byte_count=source.stat().st_size,
        selected_stream_index=0,
        timebase_num=PROBE_TB[0],
        timebase_den=PROBE_TB[1],
        ffprobe_json=payload,
        probe_digest="c" * 64,
        probe_artifact_ref=str(run_dir / "probe-canonical.json"),
        raw_probe_artifact_ref=str(run_dir / "probe-raw.json"),
        canonical_probe_artifact_ref=str(run_dir / "probe-canonical.json"),
        policy_identity="policy-real-source-test",
    )


def _hit(*, pts: int, tb_num=_MISSING, tb_den=_MISSING) -> SimpleNamespace:
    fields = {
        "source_sha256": None, "source_path": None, "rank": 1, "score": 0.9,
        "pts": pts, "timestamp_human": "00:00:00.040",
    }
    if tb_num is not _MISSING:
        fields["timebase_num"] = tb_num
    if tb_den is not _MISSING:
        fields["timebase_den"] = tb_den
    return SimpleNamespace(**fields)


def test_locator_timebase_equal_to_probe_is_admissible(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    interval = _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)
    assert interval["start"] == 40 and interval["end"] == 80
    assert interval["time_domain"] == "source_pts"
    assert interval["endpoint_semantics"] == "half_open"


def test_locator_timebase_rationally_equivalent_but_unreduced_is_admissible(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    interval = _source_pts_interval(_hit(pts=40, tb_num=2, tb_den=2000), probe)
    assert (interval["start"], interval["end"]) == (40, 80)


def test_locator_timebase_mismatch_refuses_before_reinterpretation(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    with pytest.raises(RealSourcePreparationRefusal, match="SOURCE_LOCATOR_TIMEBASE_MISMATCH"):
        _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=2000), probe)


@pytest.mark.parametrize("tb_num,tb_den,expected", [
    (_MISSING, 1000, "SOURCE_LOCATOR_TIMEBASE_INVALID"),
    (1, _MISSING, "SOURCE_LOCATOR_TIMEBASE_INVALID"),
    (None, 1000, "SOURCE_LOCATOR_TIMEBASE_INVALID"),
    (True, 1000, "SOURCE_LOCATOR_TIMEBASE_INVALID"),
    (0, 1000, "SOURCE_LOCATOR_TIMEBASE_INVALID"),
    (1, -1000, "SOURCE_LOCATOR_TIMEBASE_INVALID"),
])
def test_locator_timebase_invalid_refuses(tmp_path: Path, tb_num, tb_den, expected: str) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    with pytest.raises(RealSourcePreparationRefusal, match=expected):
        _source_pts_interval(_hit(pts=40, tb_num=tb_num, tb_den=tb_den), probe)


def test_packet_only_tick_cannot_be_an_endpoint(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80), packets=(120,))
    interval = _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)
    assert interval["end"] == 80


def test_packet_only_hit_tick_is_not_admissible(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80), packets=(120,))
    with pytest.raises(RealSourcePreparationRefusal, match="SOURCE_PTS_NOT_OBSERVED"):
        _source_pts_interval(_hit(pts=120, tb_num=1, tb_den=1000), probe)


def test_same_tick_in_frame_and_packet_is_eligible_via_frame(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80), packets=(80,))
    interval = _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)
    assert interval["end"] == 80


def test_top_level_pts_ticks_never_confers_endpoint_authority(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", pts_ticks=(40, 80))
    with pytest.raises(RealSourcePreparationRefusal, match="SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED"):
        _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)


def test_alias_fallback_skips_malformed_earlier_alias(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run")
    probe = RealSourceProbeBinding(**{
        **probe.__dict__,
        "ffprobe_json": {
            "streams": [{"index": 0, "codec_type": "video", "time_base": "1/1000"}],
            "stream_index": 0,
            "frames": [
                {"stream_index": 0, "best_effort_timestamp": "40.5", "pts": "40"},
                {"stream_index": 0, "best_effort_timestamp": None, "pts": "80"},
            ],
            "packets": [],
        },
    })
    interval = _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)
    assert (interval["start"], interval["end"]) == (40, 80)


def test_no_authoritative_frame_evidence_refuses_distinctly(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", packets=(40, 80))
    with pytest.raises(RealSourcePreparationRefusal, match="SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED"):
        _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)


def test_duplicate_presentation_ticks_are_preserved_in_the_authoritative_projection(tmp_path: Path) -> None:
    """§3.2(7): duplicates are evidence and must survive the projection itself.

    An interval-only assertion cannot discharge this: a set-collapsing
    implementation would still yield start=40, end=80.
    """
    from vip_fvs.real_source_service import _frame_presentation_pts

    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 40, 80))
    assert _frame_presentation_pts(probe) == (40, 40, 80)
    interval = _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)
    assert (interval["start"], interval["end"]) == (40, 80)


def test_endpoint_selection_consumes_the_multiplicity_preserving_projection() -> None:
    """Guard: interval coordinates must be derived from the projection helper.

    If interval selection kept its own set-collapsing path, duplicate evidence
    would be dropped even though the projection preserved it.
    """
    import inspect
    import vip_fvs.real_source_service as service

    assert "_frame_presentation_pts" in inspect.getsource(service._source_pts_interval)


def test_non_selected_stream_frames_are_ignored(tmp_path: Path) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    probe = RealSourceProbeBinding(**{
        **probe.__dict__,
        "ffprobe_json": {
            **probe.ffprobe_json,
            "frames": list(probe.ffprobe_json["frames"]) + [
                {"stream_index": 1, "best_effort_timestamp": "999"}
            ],
        },
    })
    interval = _source_pts_interval(_hit(pts=40, tb_num=1, tb_den=1000), probe)
    assert interval["end"] == 80


def test_no_rate_field_is_consulted_for_endpoint_selection() -> None:
    import inspect
    import vip_fvs.real_source_service as service
    source_text = inspect.getsource(service)
    for forbidden in ("r_frame_rate", "avg_frame_rate", "nb_frames", "duration_ts"):
        assert forbidden not in source_text, f"nominal-rate field consulted: {forbidden}"


# --------------------------------------------------------------------------
# D-PROV-1.C — pre-publication authoritative-refinement / probe timebase gate
# These exercise the full preparation path with deterministic synthetic bytes
# and a fake refinement adapter. No container parser is duplicated and no real
# media is touched: the adapter is injected, so the source is never parsed.
# --------------------------------------------------------------------------

def _runtime():
    import numpy as np
    from vip_fvs.local_semantic import checked_runtime
    from vip_fvs.retrieval_adapter import fake_semantic_space

    return checked_runtime(
        image_embedder=lambda paths: np.ones((len(paths), 768), dtype=np.float32),
        text_embedder=lambda texts: np.ones((len(texts), 768), dtype=np.float32),
        semantic_space=fake_semantic_space(), fake=False, runtime_identity="tb-gate-runtime",
    )


def _authorization(source: Path, index: Path, output: Path, runtime, query: str = "target") -> dict:
    import json as _json
    from persistent_local_index.model_space import semantic_space_id

    space = runtime.semantic_space
    return {
        "authorization_id": "auth-tb", "source_path": str(source.resolve()),
        "source_revision_id": "rev-tb-1",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "query_digest": hashlib.sha256(_json.dumps(query).encode()).hexdigest(),
        "model_identity": space.model_identity, "model_revision": space.frozen_revision,
        "weights_sha256": space.weights_sha256, "semantic_space_id": semantic_space_id(space),
        "index_root": str(index.resolve()),
        "index_digest": hashlib.sha256(_json.dumps(str(index)).encode()).hexdigest(),
        "output_root": str(output.resolve()),
        "allowed_stages": ["decode", "embed", "index", "probe", "retrieve", "refine"],
        "local_only": True, "discovery_policy_ref": "discover-tb", "refinement_policy_ref": "refine-tb",
        "policy_digest": "1" * 64, "scope_digest": "2" * 64,
    }


def _prepare(monkeypatch, tmp_path: Path, *, probe, measured: dict):
    """Run one full preparation with an injected measured refinement.

    ``measured`` must already carry the keys the service cross-checks
    (``source_revision_id``, ``stream_index``, ``source_content_digest``,
    ``start_ticks``, ``end_ticks``) and may or may not carry ``time_base``.
    """
    from persistent_local_index.model_space import semantic_space_id as _space_id

    from vip_fvs.real_source_service import RealSourceRequest, prepare_real_source

    runtime = _runtime()
    index, output = tmp_path / "index", tmp_path / "out"
    monkeypatch.setattr("vip_fvs.real_source_service.probe_real_source", lambda *a, **k: probe)
    monkeypatch.setattr(
        "vip_fvs.real_source_service.retrieve_local_semantic",
        lambda *a, **k: SimpleNamespace(
            space_id=_space_id(runtime.semantic_space),
            generation_id="tb-generation",
            hits=(SimpleNamespace(
                source_sha256=probe.source_sha256, source_path=str(probe.source_path),
                rank=1, score=0.9, pts=40, timebase_num=1, timebase_den=1000,
                timestamp_human="00:00:00.040",
            ),),
        ),
    )
    monkeypatch.setattr(
        "vip_fvs.real_source_service.refine_retrieval_candidate",
        lambda *a, **k: SimpleNamespace(measured_refinement=dict(measured), binding_eligible=True),
    )
    request = RealSourceRequest(
        source_path=probe.source_path, query="target",
        authorization=_authorization(probe.source_path, index, output, runtime),
        runtime=runtime, index_root=index, output_root=output, run_dir=tmp_path / "run",
        source_revision_id=probe.source_revision_id, attempt_id="attempt-tb-1",
        selected_stream_index=0,
    )
    return prepare_real_source(request)


def _measured_base(source: Path, *, time_base) -> dict:
    record = {
        "refinement_id": "ref-tb-1", "evidence_digest": "d" * 64,
        "source_revision_id": "rev-tb-1", "stream_index": 0,
        "source_content_digest": hashlib.sha256(source.read_bytes()).hexdigest(),
        "start_ticks": 40, "end_ticks": 80,
        "produced_by_gate3_refinement_attempt": True,
        "evidence_class": "MEASURED", "time_domain": "source_pts", "precision": "source-pts",
    }
    if time_base is not _MISSING:
        record["time_base"] = time_base
    return record


def test_missing_measured_timebase_refuses_and_publishes_nothing(tmp_path: Path, monkeypatch) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base=_MISSING)
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_TIMEBASE_NOT_MEASURED"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()


@pytest.mark.parametrize("bad", [True, 1.5, "1/1000", None, {"num": 1, "den": 0}, {"num": 1}, {"num": 0, "den": 1000}])
def test_invalid_measured_timebase_refuses_and_publishes_nothing(tmp_path: Path, monkeypatch, bad) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base=bad)
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_TIMEBASE_NOT_MEASURED"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()


def test_measured_timebase_mismatch_refuses_and_publishes_nothing(tmp_path: Path, monkeypatch) -> None:
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 2000})
    with pytest.raises(RealSourcePreparationRefusal, match="AUTHORITATIVE_REFINEMENT_TIMEBASE_MISMATCH"):
        _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    assert not (tmp_path / "out" / "review-bundle.json").exists()


def test_matching_measured_timebase_is_published_as_authority(tmp_path: Path, monkeypatch) -> None:
    """POSITIVE_GUARD, not a RED case.

    Against pre-change code this passes vacuously: with measured and probe both
    ``1/1000``, the current implementation publishes the *probe* tuple and the
    values happen to match. Its role is to ensure the GREEN implementation still
    publishes successfully and that both published tuples equal the authoritative
    measured tuple. It is not evidence that the measured-timebase gate exists.

    The genuine D-PROV-1.C RED evidence is the missing / invalid / mismatch cases
    plus their no-publication assertions. Because a value-equality assertion
    cannot distinguish "published from the measured record" from "published from
    the probe", Task 7 carries an explicit code-review item for that distinction;
    no brittle source-string test is invented to manufacture RED here.
    """
    source = _source(tmp_path)
    probe = _probe(source, tmp_path / "run", frames=(40, 80))
    measured = _measured_base(source, time_base={"num": 1, "den": 1000})
    result = _prepare(monkeypatch, tmp_path, probe=probe, measured=measured)
    payload = result.bundle.payload
    assert payload["source"]["timebase"] == {"num": 1, "den": 1000}
    assert payload["refinement"]["timebase"] == {"num": 1, "den": 1000}
    assert (tmp_path / "out" / "review-bundle.json").exists()
    assert result.bundle.payload["refinement"]["status"] == "MEASURED"
```

**Exact pytest command:**

```
PYTHONPATH="src:experiments" $PY -m pytest tests/vip_fvs/unit/test_real_source_temporal_authority.py -q -p no:cacheprovider
```

**Expected RED reason:** two distinct causes, both genuine.

1. *Endpoint authority.* `_source_pts_interval` has no locator-timebase predicate and unions packet ticks, so the mismatch / invalid / packet-only / top-level-`pts_ticks` cases fail.
2. *Pre-publication measured-timebase gate.* No comparison of the authoritative measured `time_base` against the probe timebase exists in the service, so the missing / invalid / mismatch cases reach publication instead of refusing, and therefore also fail. The invalid-timebase case additionally fails because no validation of the measured tuple exists at all.

Currently **passing** (guards, not RED): `test_no_rate_field_is_consulted_for_endpoint_selection`, `test_locator_timebase_equal_to_probe_is_admissible`, the rationally-equivalent case, `test_same_tick_in_frame_and_packet_is_eligible_via_frame`, `test_alias_fallback_skips_malformed_earlier_alias`, `test_non_selected_stream_frames_are_ignored`, and the two multiplicity tests (which fail only on the missing `_frame_presentation_pts` symbol until Task 2 adds it).

**`test_matching_measured_timebase_is_published_as_authority` is a `POSITIVE_GUARD`, not RED.** Against current code it passes vacuously: with measured and probe both `1/1000`, the present implementation publishes the *probe* tuple and the asserted values coincide. It exists to ensure GREEN preserves successful publication and output equality. The genuine D-PROV-1.C RED evidence is the missing / invalid / mismatch refusals and their no-publication assertions. Provenance ("published from the measured record, not the probe") is verified by the Task 7 code-review item, because no value-equality assertion can establish it and no brittle source-string test is invented for it.

`_frame_presentation_pts`, `SOURCE_LOCATOR_TIMEBASE_*`, `SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED` and `AUTHORITATIVE_REFINEMENT_TIMEBASE_*` do not exist yet; tests referencing them fail with `ImportError`/`AttributeError` or `DID NOT RAISE`, which is the intended RED shape.

**Minimal GREEN change:** Task 2. Do not weaken any assertion to reach GREEN.

**Verification command (after Task 2):** same pytest command; expect all pass.

**Commit:**

```
git add tests/vip_fvs/unit/test_real_source_temporal_authority.py
git commit -m "test(root-g): RED temporal-authority contract for D-PROV-1 locator/frame/packet authority"
```
*(Commit only after Task 2 makes it GREEN, or commit RED first per local TDD convention — either is acceptable provided the final state is GREEN and the history shows RED before GREEN.)*

---

## Task 2 — Temporal production implementation (minimal GREEN)

**Files:**
- Modify: `src/vip_fvs/real_source_service.py`

**Interface consumed:** `probe.ffprobe_json`, `probe.selected_stream_index`, `probe.timebase_num/den`, the authoritative refinement record returned by the refinement adapter, existing `_refuse`.

**Interface produced (module-internal):**
- a locator-timebase admissibility predicate;
- **`_frame_presentation_pts(probe: RealSourceProbeBinding) -> tuple[int, ...]`** — the authoritative frame-presentation-only tick projection. Module-private; it is *not* a public API and does not alter the frozen external interface or `__all__`;
- a measured-timebase cross-check result used before publication.

**`_frame_presentation_pts` exact contract** (frozen here so it can be asserted directly):

- input: only `ffprobe_json["frames"]` entries whose `stream_index` equals `probe.selected_stream_index`;
- per frame, aliases in the order `best_effort_timestamp` → `pts` → `pkt_pts`; take the **first** alias whose value is a valid lossless presentation tick (exact non-boolean `int`, or a `str` of optional `-` plus digits only); skip malformed/invalid aliases and continue to the next; never coerce floats or DTS;
- exactly one tick contributed per qualifying frame;
- frames with no valid alias contribute nothing;
- **return type is `tuple[int, ...]` preserving input encounter order and duplicate multiplicity**: frame ticks `(40, 40, 80)` MUST project to `(40, 40, 80)`, never `(40, 80)`. No `set()`, no `sorted({...})`, no deduplication;
- an empty result is the signal for `SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED` at the call site, not inside the helper.

Implementation-independent requirements (spec §3): exact-integer locator equivalence by cross-multiplication; frame-only projection with the alias order and first-valid rule above; duplicates preserved; distinct refusal when no frame yields a tick; post-refinement tuple-equal measured-timebase check; publication of the authoritative measured timebase; no `parse_iso_bmff_timing` call.

**Minimal GREEN steps:**

1. Add the locator-timebase predicate and call it at the top of `_source_pts_interval` before the locator `pts` is interpreted. Read the locator timebase from the hit using the existing `_value` helper.
2. Add `_frame_presentation_pts(probe)` implementing the frozen contract above.
3. Rewrite `_source_pts_interval` to obtain its tick sequence by calling `_frame_presentation_pts(probe)` (it must reference that helper, so interval coordinates and the preserved multiplicity can never diverge), then select `start`/`end` from that sequence only. Keep the existing `SOURCE_PTS_NOT_OBSERVED` / `SOURCE_PTS_INTERVAL_NOT_OBSERVED` codes for membership and no-greater-member failures, and raise `SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED` when the sequence is empty.
4. Leave `_observed_pts` **unchanged** in body and semantics.
5. After `authoritative = dict(getattr(refined, "measured_refinement", {}) or {})` and the existing binding-eligibility/scope/digest/interval checks, add: read `authoritative.get("time_base")`; refuse `AUTHORITATIVE_REFINEMENT_TIMEBASE_NOT_MEASURED` unless it is a mapping whose `num` and `den` are both exact non-boolean integers and both `> 0`; refuse `AUTHORITATIVE_REFINEMENT_TIMEBASE_MISMATCH` if the integer tuple differs from `(probe.timebase_num, probe.timebase_den)`. Both refusals must be raised **before** any `review-bundle.json` write.
6. Publish `tb = {"num": authoritative["time_base"]["num"], "den": authoritative["time_base"]["den"]}` instead of the probe declaration, and keep the existing refinement-summary `"timebase": tb` and bundle `source` timebase consistent.
7. Update the stale comment in `_observed_pts` that implies packets are presentation authority, so it states the inventory-only role. Do not change the code path.

**Exact verification commands:**

```
PYTHONPATH="src:experiments" $PY -m pytest tests/vip_fvs/unit/test_real_source_temporal_authority.py -q -p no:cacheprovider
PYTHONPATH="src:experiments" $PY -m pytest tests/vip_fvs/unit/test_real_source_service.py tests/vip_fvs/adversarial/test_real_source_probe_boundaries.py -q -p no:cacheprovider
```
   Expected: new file all GREEN; `test_real_source_service.py` and the probe-boundary tests unchanged and GREEN.

**Commit:**

```
git add src/vip_fvs/real_source_service.py
git commit -m "feat(root-g): close D-PROV-1 locator/frame endpoint authority and pre-publication measured timebase check"
```

---

## Task 3 — Generated fixture alignment (three existing paths only)

**Files (exactly these three, nothing else):**
- Modify: `tests/vip_fvs/integration/test_real_source_prepare.py`
- Modify: `tests/vip_fvs/adversarial/test_real_prepare_plan_authority_v3.py`
- Modify: `tests/vip_fvs/integration/test_real_preview_cli.py`

**Interface consumed:** `persistent_local_index.search.SearchHit`; the §3.2 frame-presentation contract.

**Interface produced:** none (fixtures only).

**Purpose limit (authority A5 — do not exceed):** align fake semantic hits with the real `SearchHit` temporal contract, replace successful exact-boundary dependence on injected top-level `pts_ticks` with explicit frame presentation evidence, and update assertions only insofar as they verify D-PROV-1 behavior. No refactor, no cleanup, no reformatting, no unrelated assertions, no deletion/rename/split.

**Steps:**

1. `test_real_source_prepare.py` — the retrieval monkeypatch hit currently supplies `pts, rank, score, source_path, source_sha256, timestamp_human`. Add `timebase_num=1, timebase_den=1000` (or construct a real `SearchHit`). The probe payload currently injects `pts_ticks` and no frames; add explicit frames with `best_effort_timestamp` `"40"` and `"80"` for `stream_index 0`. Keep the existing `start == 40` / `end == 80` / `timebase == {"num": 1, "den": 1000}` assertions.
2. `test_real_prepare_plan_authority_v3.py` — add locator `timebase_num=1, timebase_den=1000`; replace `pts_ticks: [40, 80]` with frames at `40` and `80`. The existing assertion `calls[0]["requested_pts"] == (40, 80)` must keep passing **from frame evidence**, not from `pts_ticks`.
3. `test_real_preview_cli.py` — add locator `timebase_num=1, timebase_den=25` (the generated media uses `build_mp4(media_timescale=25, ...)`). Its probe already supplies explicit frames (`0, 13, 25, 38`), so no `pts_ticks` migration is needed. Keep existing assertions that the hit tick `0` yields the intended interval.
4. Remove the now-unnecessary top-level `pts_ticks` injection from paths 1 and 2. Do not add `pts_ticks` anywhere else.
5. Do not touch `tests/vip_fvs/unit/test_real_source_service.py`, `tests/vip_fvs/unit/test_real_plan.py`, or `tests/vip_fvs/integration/test_local_preview_real_tools_generated.py`.

**Scope precision (verified):**

- The second test in `test_real_source_prepare.py` (`test_prepare_real_source_fails_closed_on_retrieval_error`) refuses at the retrieval stage, before the endpoint projection runs. It therefore needs no frame change; leave its `pts_ticks` injection as-is unless the new locator gate is reached, in which case only add the locator timebase. Do not add frames to it gratuitously.
- `test_real_preview_cli.py` uses a **real** generated container (`build_mp4(media_timescale=25, sample_deltas=(13, 12, 13, 12))`) and a real measured refinement, and its probe payload already declares `time_base: "1/25"`. The fixture's media timescale and the probe timebase therefore already agree, so `1/25` is the correct locator timebase and the measured-timebase cross-check passes without any probe change.
- `test_real_source_prepare.py` and `test_real_prepare_plan_authority_v3.py` are fully synthetic (the "source" is a non-media byte string) with declared probe timebase `1/1000`; their frames must be expressed in that same 1/1000 tick domain (`40`, `80`), which is exactly what the existing expected intervals require.

**Exact verification command:**

```
PYTHONPATH="src:experiments" $PY -m pytest tests/vip_fvs/integration/test_real_source_prepare.py tests/vip_fvs/adversarial/test_real_prepare_plan_authority_v3.py tests/vip_fvs/integration/test_real_preview_cli.py -q -p no:cacheprovider
```

**Expected before the edit:** RED with `SOURCE_LOCATOR_TIMEBASE_INVALID` (all three; paths 1–2 additionally with `SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED`).

**Expected after the edit:** all three GREEN, with no production rule relaxed.

**Commit:**

```
git add tests/vip_fvs/integration/test_real_source_prepare.py \
        tests/vip_fvs/adversarial/test_real_prepare_plan_authority_v3.py \
        tests/vip_fvs/integration/test_real_preview_cli.py
git commit -m "test(root-g): align three real-preparation fixtures with the SearchHit + frame-presentation contract"
```

---

## Task 4 — Revision-binding tests (RED)

**Files:**
- Create: `tests/vip_fvs/unit/test_real_plan_revision_binding.py`

**Interface consumed:**
- `vip_fvs.real_plan.build_real_edit_plan`, `save_real_plan`, `load_real_plan`
- `vip_fvs.human_decision.create_human_decision`
- `gate3.plan.EditPlanRevision`

**Interface produced:** asserts the frozen signature `build_real_edit_plan(..., prior_revision: EditPlanRevision | None = None)`.

**Why this is RED:** `build_real_edit_plan` has no `prior_revision` parameter and performs no decision/revision equality check; `load_real_plan` restores no lineage.

**Test skeleton (reuse the existing REAL-plan fixture builders so evidence binding stays real):**

```python
"""D-REALPLAN-1 revision-binding closure tests."""
from __future__ import annotations

from pathlib import Path

import pytest

from vip_fvs.human_decision import create_human_decision
from vip_fvs.real_plan import (
    build_real_edit_plan,
    load_real_plan,
    save_real_plan,
)
from tests.vip_fvs.unit.test_real_plan import _bundle, _binding_fixture   # existing fixture builders


def _accept(bundle, revision: int):
    return create_human_decision(
        bundle=bundle, decision_id=f"decision-{revision}", principal_kind="human",
        principal_ref="human:editor-1", decision_class="ACCEPT",
        rationale="Reviewed measured source interval.", target_plan_revision=revision,
    )


def test_revision_1_with_no_prior_succeeds(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    artifacts = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    assert artifacts.plan.supersedes is None
    assert list(artifacts.plan.derived_from_refs) == []
    assert artifacts.plan.prior_revision is None


def test_revision_1_with_prior_refuses(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    with pytest.raises(ValueError, match="PLAN_REVISION_1_CANNOT_HAVE_PRIOR_REVISION"):
        build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1,
                             prior_revision=first.plan)


def test_mismatched_decision_revision_refuses(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    with pytest.raises(ValueError, match="PLAN_REVISION_MUST_MATCH_DECISION_REVISION"):
        build_real_edit_plan(bundle, _accept(bundle, 3), plan_id="plan-1", plan_revision=1)


def test_revision_2_without_prior_refuses(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    with pytest.raises(ValueError, match="PLAN_REVISION_AFTER_1_REQUIRES_IMMEDIATE_PRIOR_REVISION"):
        build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2)


def test_revision_2_with_immediate_prior_succeeds_with_lineage(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    second = build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2,
                                  prior_revision=first.plan)
    assert second.plan.plan_revision == 2
    assert second.plan.supersedes == first.plan.digest
    assert list(second.plan.derived_from_refs) == [first.plan.digest]
    assert second.plan.prior_revision is first.plan


def test_revision_2_with_target_1_decision_refuses(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    with pytest.raises(ValueError, match="PLAN_REVISION_MUST_MATCH_DECISION_REVISION"):
        build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=2,
                             prior_revision=first.plan)


def test_skipped_revision_refuses(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    with pytest.raises(ValueError, match="PRIOR_REVISION_MUST_IMMEDIATELY_PRECEDE_THIS_REVISION"):
        build_real_edit_plan(bundle, _accept(bundle, 3), plan_id="plan-1", plan_revision=3,
                             prior_revision=first.plan)


def test_different_plan_id_refuses(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    with pytest.raises(ValueError, match="PRIOR_REVISION_MUST_SHARE_PLAN_ID"):
        build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-2", plan_revision=2,
                             prior_revision=first.plan)


def test_save_load_preserves_lineage(monkeypatch, tmp_path: Path):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    second = build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2,
                                  prior_revision=first.plan)
    path = save_real_plan(second, tmp_path / "real-plan.json")
    loaded = load_real_plan(path)
    assert loaded.plan.plan_revision == 2
    assert loaded.plan.supersedes == first.plan.digest
    assert list(loaded.plan.derived_from_refs) == [first.plan.digest]


def test_load_then_extend_to_next_revision(monkeypatch, tmp_path: Path):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    second = build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2,
                                  prior_revision=first.plan)
    loaded = load_real_plan(save_real_plan(second, tmp_path / "real-plan.json"))
    third = build_real_edit_plan(bundle, _accept(bundle, 3), plan_id="plan-1", plan_revision=3,
                                 prior_revision=loaded.plan)
    assert third.plan.plan_revision == 3
    assert third.plan.supersedes == loaded.plan.digest


def test_export_eligibility_is_never_granted(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    second = build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2,
                                  prior_revision=first.plan)
    assert second.plan.export_eligible is False


# --------------------------------------------------------------------------
# Adversarial lineage cases required by spec §9.4.
# Both use real EditPlanRevision values (never duck-typed stand-ins), because
# the accepted prior_revision type is frozen to EditPlanRevision.
# --------------------------------------------------------------------------

def test_incompatible_prior_plan_scope_refuses(monkeypatch):
    """A structurally valid immediate predecessor with a non-REAL scope refuses.

    Derived from a genuinely built revision 1 so the predecessor is a real,
    already-valid ``EditPlanRevision`` (pinned refinements remain the real
    binding-eligible ones); only the scope and its matching synthetic principal
    are substituted, so the ONLY failing predicate is scope compatibility.
    """
    from dataclasses import replace

    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    rid = next(iter(first.plan.pinned_decisions))
    fixture_decision = replace(
        first.plan.pinned_decisions[rid],
        principal_kind="SYNTHETIC_HUMAN",
        fixture_scope="SYNTHETIC_FIXTURE",
    )
    synthetic_prior = replace(
        first.plan,
        plan_scope="SYNTHETIC_FIXTURE",
        pinned_decisions={rid: fixture_decision},
    )
    assert synthetic_prior.plan_scope == "SYNTHETIC_FIXTURE"
    assert synthetic_prior.plan_revision == 1 and synthetic_prior.plan_id == "plan-1"
    with pytest.raises(ValueError, match="PRIOR_REVISION_MUST_HAVE_COMPATIBLE_PLAN_SCOPE"):
        build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2,
                             prior_revision=synthetic_prior)


def test_forged_lineage_with_extra_derived_ref_refuses(tmp_path: Path, monkeypatch):
    def mutate(plan):
        plan["derived_from_refs"] = list(plan["derived_from_refs"]) + ["e" * 64]

    with pytest.raises(ValueError, match="REAL_PLAN_LINEAGE_READBACK_MISMATCH"):
        load_real_plan(_forge_revision2(tmp_path, monkeypatch, mutate=mutate))


def test_forged_lineage_missing_supersedes_link_refuses(tmp_path: Path, monkeypatch):
    def mutate(plan):
        plan["derived_from_refs"] = []

    with pytest.raises(ValueError, match="REAL_PLAN_LINEAGE_READBACK_MISMATCH"):
        load_real_plan(_forge_revision2(tmp_path, monkeypatch, mutate=mutate))


def test_revision1_with_forged_lineage_refuses(tmp_path: Path, monkeypatch):
    """Revision 1 must carry no lineage at all."""
    import json

    from vip_fvs.real_plan import _canonical, _digest

    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    path = save_real_plan(first, tmp_path / "sealed.json")
    record = json.loads(path.read_bytes()[:-1].decode("utf-8"))
    record["plan"]["derived_from_refs"] = ["f" * 64]
    record.pop("record_digest", None)
    record["record_digest"] = _digest(record)
    forged = tmp_path / "forged.json"
    forged.write_bytes(_canonical(record) + b"\n")
    with pytest.raises(ValueError, match="REAL_PLAN_LINEAGE_READBACK_MISMATCH"):
        load_real_plan(forged)


def _forge_revision2(tmp_path: Path, monkeypatch, *, mutate) -> Path:
    """Seal a valid revision 2, then rewrite raw plan lineage and re-seal the envelope.

    Only the outer ``record_digest`` is recomputed. ``plan_digest`` is deliberately
    NOT recomputed, so these records prove that raw lineage classification happens
    before the plan-digest comparison AND before Gate-3 construction.
    """
    import json

    from vip_fvs.real_plan import _canonical, _digest

    _binding_fixture(monkeypatch)
    bundle = _bundle()
    first = build_real_edit_plan(bundle, _accept(bundle, 1), plan_id="plan-1", plan_revision=1)
    second = build_real_edit_plan(bundle, _accept(bundle, 2), plan_id="plan-1", plan_revision=2,
                                  prior_revision=first.plan)
    path = save_real_plan(second, tmp_path / "sealed.json")
    record = json.loads(path.read_bytes()[:-1].decode("utf-8"))
    mutate(record["plan"])
    record.pop("record_digest", None)
    record["record_digest"] = _digest(record)
    forged = tmp_path / "forged.json"
    forged.write_bytes(_canonical(record) + b"\n")
    return forged


def test_forged_lineage_missing_supersedes_key_refuses(tmp_path: Path, monkeypatch):
    """Revision >1 with no supersedes at all: raw-lineage classification, not Gate-3."""
    def mutate(plan):
        plan.pop("supersedes", None)

    with pytest.raises(ValueError, match="REAL_PLAN_LINEAGE_READBACK_MISMATCH"):
        load_real_plan(_forge_revision2(tmp_path, monkeypatch, mutate=mutate))


def test_forged_lineage_malformed_supersedes_refuses(tmp_path: Path, monkeypatch):
    """Revision >1 with a non-lowercase-hex supersedes.

    ``derived_from_refs`` is kept consistent with the malformed value so the ONLY
    failing predicate is digest-shape validity — not list equality. Without the
    raw pre-construction check, Gate-3 would raise its own
    'supersedes must name a prior revision digest' and mask this code.
    """
    def mutate(plan):
        plan["supersedes"] = "NOT-LOWERCASE-HEX"
        plan["derived_from_refs"] = ["NOT-LOWERCASE-HEX"]

    with pytest.raises(ValueError, match="REAL_PLAN_LINEAGE_READBACK_MISMATCH"):
        load_real_plan(_forge_revision2(tmp_path, monkeypatch, mutate=mutate))


def test_invalid_prior_revision_type_refuses(monkeypatch):
    _binding_fixture(monkeypatch)
    bundle = _bundle()
    with pytest.raises(ValueError, match="PRIOR_REVISION_MUST_BE_AN_EDIT_PLAN_REVISION"):
        build_real_edit_plan(
            bundle,
            _accept(bundle, 2),
            plan_id="plan-1",
            plan_revision=2,
            prior_revision=object(),
        )
```

**Exact pytest command:**

```
PYTHONPATH="src:experiments" $PY -m pytest tests/vip_fvs/unit/test_real_plan_revision_binding.py -q -p no:cacheprovider
```

**Expected RED reason:** `build_real_edit_plan` rejects the unknown `prior_revision` keyword (`TypeError`), so every case that passes it fails immediately. The decision/revision mismatch case fails because no equality predicate exists. The forged-lineage cases currently fail with `"plan readback mismatch"` (because `load_real_plan` does not yet restore `derived_from_refs`/`supersedes`), which is a genuine failure but not yet the intended code; after Task 5 they must fail specifically with `REAL_PLAN_LINEAGE_READBACK_MISMATCH`, and the two malformed-`supersedes` cases additionally prove that raw lineage is classified before Gate-3 construction (otherwise Gate-3's own `"supersedes must name a prior revision digest"` would surface instead).

**Note:** `_bundle`, `_accept` and `_binding_fixture` are existing helpers in `tests/vip_fvs/unit/test_real_plan.py` and are already imported cross-module the same way by `tests/vip_fvs/adversarial/test_real_plan_authority.py`. Import them; do **not** edit that file. (The local `_accept` in this new test file deliberately differs by taking an explicit `revision` argument.)

**Commit:** with Task 5 (RED then GREEN).

---

## Task 5 — Revision production implementation (minimal GREEN)

**Files:**
- Modify: `src/vip_fvs/real_plan.py`

**Interface produced (frozen, spec §5):**

```python
def build_real_edit_plan(
    bundle: ReviewBundle,
    decision: HumanDecisionArtifact,
    *,
    plan_id: str,
    plan_revision: int,
    pinned_evidence_digests: Mapping[str, str] | None = None,
    policy_decision_ref: str | None = None,
    prior_revision: EditPlanRevision | None = None,
) -> RealPlanArtifacts:
    ...
```

**Minimal GREEN steps:**

1. Add `prior_revision: EditPlanRevision | None = None` as a keyword-only parameter (after `policy_decision_ref`). Keep the existing `policy_decision_ref` refusal intact.
2. Add the exact decision predicate: after computing `projected`, refuse `PLAN_REVISION_MUST_MATCH_DECISION_REVISION` unless `projected.decided_on_revision == plan_revision`.
3. Add the lineage guards, mirroring Root D's accepted `build_edit_plan` semantics:
   - `prior_revision is not None` and not an `EditPlanRevision` → `PRIOR_REVISION_MUST_BE_AN_EDIT_PLAN_REVISION`;
   - `plan_revision == 1` and `prior_revision is not None` → `PLAN_REVISION_1_CANNOT_HAVE_PRIOR_REVISION`;
   - `plan_revision > 1` and `prior_revision is None` → `PLAN_REVISION_AFTER_1_REQUIRES_IMMEDIATE_PRIOR_REVISION`;
   - `plan_revision > 1` and `prior_revision.plan_revision != plan_revision - 1` → `PRIOR_REVISION_MUST_IMMEDIATELY_PRECEDE_THIS_REVISION`;
   - `plan_revision > 1` and `prior_revision.plan_id != plan_id` → `PRIOR_REVISION_MUST_SHARE_PLAN_ID`;
   - `plan_revision > 1` and `prior_revision.plan_scope != "REAL"` → `PRIOR_REVISION_MUST_HAVE_COMPATIBLE_PLAN_SCOPE`.
4. Extend the internal `_construct_real_plan` with optional keyword-only `supersedes`, `derived_from_refs`, `prior_revision`, forwarded to `EditPlanRevision`; defaulting so revision-1 behavior is byte-identical.
5. For `plan_revision > 1`, construct via `from gate3.plan import new_revision` and `new_revision(prior_revision, placements=[placement], pinned_refinements={...}, pinned_decisions={...}, source_revision_ids=[...], policy_decision_ref=None, pinned_evidence_digests={...})`. Do **not** call `new_revision` with a non-`None` `policy_decision_ref` (the existing refusal forbids it). Return that object as the plan.
6. In `load_real_plan`, restructure the plan-readback path into this **exact order**. The order is load-bearing, not stylistic.

   **6a. Obtain the raw sealed plan record.** After the canonical-JSON, envelope-key, schema-version and outer `record_digest` checks have passed, take `pr = record["plan"]` and read the raw values:

   ```
   raw_revision = pr["plan_revision"]
   raw_supersedes = pr.get("supersedes")
   raw_derived = list(pr.get("derived_from_refs", []))
   ```

   **6b. Validate the raw Root-G lineage invariant BEFORE constructing anything**, using only those raw values:

   - `raw_revision == 1` ⇒ `raw_supersedes is None` **and** `raw_derived == []`;
   - `raw_revision > 1` ⇒ `isinstance(raw_supersedes, str)` and `re.fullmatch(r"[0-9a-f]+", raw_supersedes)` **and** `raw_derived == [raw_supersedes]` exactly;
   - anything else raises `REAL_PLAN_LINEAGE_READBACK_MISMATCH` immediately.

   **Why before construction:** `gate3.plan.EditPlanRevision.__post_init__` already rejects a malformed `supersedes` with `ValueError("supersedes must name a prior revision digest")` (`gate3/plan.py:68-70`, shape `_DIGEST_SHAPE = re.compile(r"\A[0-9a-f]+\Z")`). If raw lineage were handed to `_construct_real_plan` first, that constructor-side generic error would be raised before Root G could classify the condition, masking the frozen Root-G refusal code. Root G therefore classifies the raw sealed lineage at its own readback boundary **first**, and lets Gate-3 keep validating what actually reaches it. Do **not** catch and relabel arbitrary Gate-3 constructor failures as `REAL_PLAN_LINEAGE_READBACK_MISMATCH`.

   **6c. Only after 6b passes**, construct the `EditPlanRevision` via `_construct_real_plan`, passing `supersedes=raw_supersedes` and `derived_from_refs=raw_derived`. Do not synthesize `prior_revision`.

   **6d. Then** retain `plan.to_record() == record["plan"]`.

   **6e. Then** retain `record["plan_digest"] == plan.digest`.

   **6f.** Retain every other existing readback/link check (placement, mapping and record digests, plan/placement/mapping/decision cross-links) unchanged.

   Rationale for placing lineage before the plan-digest check: `plan.digest` is computed over `supersedes`, so a record whose lineage was rewritten and then canonically re-sealed (recomputing only the outer `record_digest`) would otherwise fail `plan_digest` with a less precise `"plan digest mismatch"` and mask the cause. The forged-lineage tests in Task 4 assert the specific lineage code and will fail if this ordering is wrong.
7. Do **not** add or remove any top-level record key; `_RECORD_FIELDS` stays as-is. `prior_revision` remains intentionally unserialized.

**Exact verification commands:**

```
PYTHONPATH="src:experiments" $PY -m pytest tests/vip_fvs/unit/test_real_plan_revision_binding.py -q -p no:cacheprovider
PYTHONPATH="src:experiments" $PY -m pytest tests/vip_fvs/unit/test_real_plan.py tests/vip_fvs/adversarial/test_real_plan_authority.py tests/vip_fvs/unit/test_local_preview.py -q -p no:cacheprovider
```
   Expected: new file GREEN; the three existing revision-1 consumers unchanged and GREEN.

**Commit:**

```
git add tests/vip_fvs/unit/test_real_plan_revision_binding.py src/vip_fvs/real_plan.py
git commit -m "feat(root-g): close D-REALPLAN-1 exact decision revision binding with immediate-prior lineage and load/readback preservation"
```

---

## Task 6 — Focused regression and full authorized suite

**Files:** none written.

**Steps and exact commands:**

```
PYTHONPATH="src:experiments" $PY -m pytest tests/vip_fvs -q -p no:cacheprovider
PYTHONPATH="src:experiments" $PY -m pytest tests/gate3 -q -p no:cacheprovider
```
   Expected: no regressions. The `tests/vip_fvs` count must be the Task 0 baseline **plus** the two new test files' collected cases. Any pre-existing failure is reported as pre-existing, not silently fixed.

2. Confirm no unauthorized path changed:

```
git -C <worktree> diff --name-only d3b477db97541d7cd2775e7c42381eb4875de519..HEAD
```
   Expected set is exactly: `src/vip_fvs/real_source_service.py`, `src/vip_fvs/real_plan.py`, the two new test files, the three aligned fixtures, plus the two documentation paths from this planning turn. Anything else is a scope violation to revert, not to justify.

3. Confirm the CLI limitation holds (read-only, no execution of real flow):

```
PYTHONPATH="src:experiments" $PY -m pytest tests/vip_fvs/integration/test_real_preview_cli.py -q -p no:cacheprovider
```
   Expected GREEN; a CLI `--plan-revision > 1` request without a prior plan fails closed at the constructor.

4. Run the workspace verifier and treat its result independently:

```
bash scripts/verify-workspace.sh
```
   Record the exact output. A pre-existing unrelated failure (for example the known stale source allowlist) is **not** to be engineered to `EXIT 0`; it is reported as-is and is outside Root G.

**Commit:** none (verification only). If a verification-only ledger is required by local convention, keep it out of the five product/test paths.

---

## Task 7 — Review and completion gates

**Files:** none written.

**Steps:**

1. **Request code review before integration** (Superpowers `requesting-code-review`). Provide: base/head SHAs, the changed-path set, the spec path, the two new test paths, and the evidence commands from Task 6. Reviewer checks specifically: fail-closed ordering before publication; no weakened production rule; no `pts_ticks` authority; exactly one tick per frame; no second parser; lineage continuity; no unauthorized path; no interface change beyond `G-REALPLAN-LINEAGE-INPUT-1`.
2. **Mandatory code-review item — authoritative timebase provenance.** Verify by reading the GREEN diff that the published `tb` is assigned **from the validated authoritative measured refinement record**, and only **after** exact tuple equality against the probe timebase has been proven — not from `probe.timebase_num/den`. This is required because `test_matching_measured_timebase_is_published_as_authority` is a value-equality guard that a probe-sourced assignment would also satisfy; provenance cannot be established by that assertion, and no brittle source-string test is used instead. The same item applies to the refinement summary's `"timebase"` and the bundle's `source.timebase`.
3. **Mandatory code-review item — raw-lineage ordering.** Verify by reading the GREEN diff that `load_real_plan` classifies raw sealed lineage (`plan_revision`, `supersedes`, `derived_from_refs`) **before** calling `_construct_real_plan`, so malformed/missing `supersedes` yields `REAL_PLAN_LINEAGE_READBACK_MISMATCH` rather than Gate-3's `"supersedes must name a prior revision digest"`, and before the `plan_digest` comparison.
4. **Verification before completion** (Superpowers `verification-before-completion`): re-run the Task 6 commands and quote actual output; no completion claim without observed output.
5. **Remote durability:** fetch, confirm a fast-forward-safe push, push the execution branch, then independently re-read the remote refs and blob SHAs. Never force push. Confirm `main` is untouched.
6. **No merge, no Gate promotion:** do not merge to `main`; do not promote any gate; do not produce `export_eligible` authority.
7. Report: `START_ROOT_G_SHA`, `FINAL_REMOTE_ROOT_G_SHA`, changed paths, the two new blob SHAs, focused verification output, and any produced contract delta (`G-REALPLAN-LINEAGE-INPUT-1`).

---

## Self-review checklist (run before the final report)

This checklist is **mechanical**, not aspirational. Each line names the evidence that discharges it; a line that cannot be discharged with a concrete test name or command is a defect to fix, not a box to tick.

**Spec §3 predicate → Task 1 RED test (or an explicitly justified guard)**

- [ ] §3.1 locator validity + rational equivalence → `test_locator_timebase_equal_to_probe_is_admissible` (guard), `test_locator_timebase_rationally_equivalent_but_unreduced_is_admissible` (guard), `test_locator_timebase_mismatch_refuses_before_reinterpretation` (RED), `test_locator_timebase_invalid_refuses[...]` (RED, 6 params).
- [ ] §3.2(1)-(6) frame-only projection, alias order, first-valid, malformed-alias skip, no `pts_ticks`, no packet authority → `test_alias_fallback_skips_malformed_earlier_alias`, `test_packet_only_tick_cannot_be_an_endpoint`, `test_packet_only_hit_tick_is_not_admissible` (RED), `test_same_tick_in_frame_and_packet_is_eligible_via_frame`, `test_top_level_pts_ticks_never_confers_endpoint_authority` (RED), `test_non_selected_stream_frames_are_ignored`, `test_no_authoritative_frame_evidence_refuses_distinctly` (RED).
- [ ] §3.2(7) duplicate **multiplicity preserved in the projection** → `test_duplicate_presentation_ticks_are_preserved_in_the_authoritative_projection` (RED; asserts `(40,40,80)`), discharged only because Task 2 freezes `_frame_presentation_pts` to return a multiplicity-preserving `tuple`. Supplemented by `test_endpoint_selection_consumes_the_multiplicity_preserving_projection` (guard, ensures interval selection cannot keep a private collapsing path).
- [ ] §3.3 evidence-class discipline / `_observed_pts` non-authority → `test_no_rate_field_is_consulted_for_endpoint_selection` (guard) plus the unchanged `tests/vip_fvs/unit/test_real_source_service.py` diagnostic test, which must remain green and unedited.
- [ ] §3.4 pre-publication measured-timebase gate → **RED**: `test_missing_measured_timebase_refuses_and_publishes_nothing`, `test_invalid_measured_timebase_refuses_and_publishes_nothing[...]` (7 params), `test_measured_timebase_mismatch_refuses_and_publishes_nothing` (each also asserts no `review-bundle.json` is published). **POSITIVE_GUARD (not RED)**: `test_matching_measured_timebase_is_published_as_authority` — it passes vacuously pre-change because measured and probe tuples are equal, so it cannot evidence the gate. Publication *provenance* is discharged by the Task 7 mandatory code-review item, not by an assertion or a source-string test.
- [ ] §3.5 no nominal FPS / no `seconds × FPS` → `test_no_rate_field_is_consulted_for_endpoint_selection` (structural guard over the module source).
- [ ] §3.6 source immutability/provenance → existing probe/service digest and scope assertions are unchanged and must stay green (Task 6); no new test required, because no predicate changes.

**Spec §4/§6 lineage predicate → Task 4 RED test**

- [ ] §4.1 exact new-decision binding → `test_mismatched_decision_revision_refuses` (RED), `test_revision_2_with_target_1_decision_refuses` (RED).
- [ ] §4.2(1) rev-1 no prior / §4.2(2) rev-1 with prior refuses → `test_revision_1_with_no_prior_succeeds`, `test_revision_1_with_prior_refuses` (RED).
- [ ] §4.2(2) N>1 requires immediate prior → `test_revision_2_without_prior_refuses` (RED).
- [ ] §4.2(2) immediate-prior + same plan → `test_revision_2_with_immediate_prior_succeeds_with_lineage` (RED).
- [ ] §4.2(2) skipped revision → `test_skipped_revision_refuses` (RED).
- [ ] §4.2(2) different `plan_id` → `test_different_plan_id_refuses` (RED).
- [ ] §4.2(2) incompatible prior `plan_scope` → `test_incompatible_prior_plan_scope_refuses` (RED, real `EditPlanRevision` predecessor).
- [ ] §4.3 load → `.plan` → N+1 → `test_save_load_preserves_lineage`, `test_load_then_extend_to_next_revision` (RED).
- [ ] §4.4 unsupported caller fails closed → `test_revision_2_without_prior_refuses` plus the unchanged `test_real_preview_cli.py` path; the CLI itself is never edited.
- [ ] §4.5 no authority created → `test_export_eligibility_is_never_granted` (guard).
- [ ] §5 invalid `prior_revision` runtime type → `test_invalid_prior_revision_type_refuses` (RED; new public-input validation path pinned before GREEN).
- [ ] §6.3 exact loaded-lineage coherence → `test_forged_lineage_with_extra_derived_ref_refuses` (RED), `test_forged_lineage_missing_supersedes_link_refuses` (RED), `test_revision1_with_forged_lineage_refuses` (RED), `test_forged_lineage_missing_supersedes_key_refuses` (RED), `test_forged_lineage_malformed_supersedes_refuses` (RED).
- [ ] Raw sealed lineage is classified **before** `_construct_real_plan` and before the `plan_digest` comparison — proven by `test_forged_lineage_missing_supersedes_key_refuses` and `test_forged_lineage_malformed_supersedes_refuses`, whose forged records recompute only the outer `record_digest` (never `plan_digest`) and which assert the `REAL_PLAN_LINEAGE_READBACK_MISMATCH` code specifically. Verified against current code: `gate3.plan.EditPlanRevision.__post_init__` raises `"supersedes must name a prior revision digest"` for a malformed value, so this ordering is required, not cosmetic.

**Scope / authority / hygiene**

- [ ] Scope mismatch and forged lineage are each covered by a named RED test (see the rows above) — this line was previously claimed without coverage and is now discharged.
- [ ] Malformed and missing raw `supersedes` each have a named RED test, and raw-lineage validation is stated to run before `_construct_real_plan`.
- [ ] Invalid `prior_revision` runtime type has a named RED test.
- [ ] No test is mislabelled as RED when it passes against pre-change code; `test_matching_measured_timebase_is_published_as_authority` is explicitly classified `POSITIVE_GUARD`.
- [ ] No test path outside the exact five-path allocation is written (Task 3 enumerates three; Tasks 1 and 4 create two; Task 6 changes none).
- [ ] No implementation step touches an unauthorized product surface (exactly `real_source_service.py` and `real_plan.py`).
- [ ] `prior_revision` is consistently `EditPlanRevision | None` in spec, plan and tests; no union type and no path parameter.
- [ ] Task 0 does **not** expect HEAD to equal `ROOT_BASE_SHA`; it uses the three-anchor model and requires `AUTHORIZED_IMPLEMENTATION_START_SHA`, ancestry, and approved spec/plan blobs.
- [ ] No task grants or infers implementation authority; `IMPLEMENTATION_AUTHORIZED=false` appears verbatim.
- [ ] The two mandatory Task 7 code-review items are present (published-timebase provenance from the measured record; raw-lineage ordering before construction).
- [ ] No placeholders/TBD remain.
- [ ] All referenced names exist in current code (`_source_pts_interval`, `_observed_pts`, `_refuse`, `_value`, `_construct_real_plan`, `_canonical`, `_digest`, `_RECORD_FIELDS`, `build_real_edit_plan`, `save_real_plan`, `load_real_plan`, `gate3.plan.new_revision`, `gate3.plan.EditPlanRevision.__post_init__` supersedes validation, `SearchHit`); the only *new* name is `_frame_presentation_pts`.
- [ ] `git diff --check` clean; changed-path audit equals the expected set.
