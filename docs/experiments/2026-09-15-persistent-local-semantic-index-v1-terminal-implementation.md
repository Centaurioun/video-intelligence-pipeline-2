# Persistent Local Semantic Index v1 — Terminal Implementation Reconciliation

**Date:** 2026-09-15  
**Canonical-main parent before this record:** `ed20fd62852f1f776b7058bcb8dd83be3d2cc79c`  
**Planning authority:** `planning/persistent-local-semantic-index-v1@0a84753148938fccf3f786b070723dd57ca5a3fc`  
**Implementation base:** `experiment/single-video-semantic-spike-v1@0c14fce1fa979d466292fbd5cfd1e876bfacee92`  
**Implementation branch:** `experiment/persistent-local-semantic-index-v1@bced5d2c5f0506ba6a41e434fb837569ce83d85e`  
**Disposition:** `PERSISTENT_LOCAL_INDEX_READY_FOR_OWNER_REAL_MEDIA_SMOKE`  
**Gate effect:** none; this remains a repository-level experimental vertical slice and is not merged into Gate authority.

## 1. What was independently verified

GitHub reconciliation after the DeepSeek terminal report confirmed:

- remote `experiment/persistent-local-semantic-index-v1` exists at exactly `bced5d2c5f0506ba6a41e434fb837569ce83d85e`;
- that branch is nine commits ahead of the preserved spike base `0c14fce1fa979d466292fbd5cfd1e876bfacee92` and has that exact merge base;
- the implementation diff adds the isolated `experiments/persistent_local_index/` package, its test suite, and its branch-local evidence ledger; it does not modify canonical Gate contracts;
- remote `controller/gate0/portfolio-v1` remains exactly `eaf11479279eb54480d36b926a0d16f0a3c77730`;
- canonical `main` remained `ed20fd62852f1f776b7058bcb8dd83be3d2cc79c` before this docs-only reconciliation;
- the implementation branch's detailed evidence ledger preserves Attempt 0 (context-budget clean non-start) and Attempt 1 (full implementation), including failures and rejected attempts.

The following test/runtime claims are grounded in the branch evidence ledger and DeepSeek's terminal report; they were not independently re-executed by ChatGPT in this reconciliation.

## 2. Implemented scope

All seven approved plan tasks are recorded COMPLETE:

1. semantic-space identity and generation manifest — task commit `67b8ac2`;
2. SQLite lifecycle store, vector file, crash-tail recovery — `7391486`;
3. one-pass measured-PTS sampler plus thumbnails — `7e97a7e`;
4. local SigLIP embedding seam — `bf4f583`;
5. incremental, duplicate-aware, restartable indexer — `e009848`;
6. read-only exact semantic search with deterministic Top-K — `fbaf897`;
7. CLI + synthetic end-to-end proof — task-code commit `c860b92`, evidence refinements through `ca2f9c9` and terminal branch head `bced5d2`.

The package consists of focused modules for semantic-space identity, storage, media sampling, embedding, indexing, exact search, CLI orchestration, and dedicated tests. The implementation remains isolated under `experiments/persistent_local_index/`.

## 3. Verified design properties reported by the implementation session

### Persistent storage and lifecycle

- dense vectors are append-only, row-major `float32` in `vectors.f32`;
- current SigLIP row width is 768 values = 3072 bytes;
- vectors are L2-normalized before persistence;
- SQLite is authoritative for committed row count and committed vector byte length;
- `manifest.json` mirrors generation identity and committed row count;
- a longer vector file is interpreted as an uncommitted tail and may be truncated by the controlled writer-resume path;
- a vector file shorter than committed bytes fails closed;
- single-writer concurrency uses `fcntl.flock` and fails closed on a competing writer.

### Source identity / incremental behavior

Reported passing behaviors include:

- unchanged source digest skips sampler and image embedder;
- exact duplicate bytes at a second path reuse the existing row range without re-embedding;
- changed bytes at the same path append new rows and move the location only after the new source object is COMPLETE;
- an old digest remains active while another location still references it;
- an old digest is superseded only when the tested lifecycle path determines no remaining location references it;
- stale `IN_PROGRESS` work is redone without exposing partial searchable rows;
- per-source failure does not invalidate prior COMPLETE sources;
- uncommitted vector tails recover on the next writer invocation;
- synthetic source bytes remain unchanged through indexing.

### Query behavior

The reported query surface:

- opens the persisted generation;
- validates semantic-space identity fail-closed;
- embeds text only, preserving `padding="max_length"`;
- memory-maps the committed vector prefix;
- performs exact cosine search;
- masks inactive rows;
- returns source digest/location, measured PTS/timebase, derived timestamp, score, and thumbnail status/path.

Reported query-time media work:

- video decode: **NO**;
- ffmpeg/ffprobe invocation: **NO** under subprocess spy;
- image re-embedding: **NO**; structurally absent from the query API.

## 4. Temporal evidence discipline preserved

The implementation reports preservation of the key spike invariant:

```text
persisted sampled pixels
<-> same decoded frame
<-> measured decoder/source-native PTS
<-> recorded timebase
```

The operational sampler does not restore full per-frame `ffprobe -show_frames` enumeration and does not infer exact frame locations via `seconds * nominal_fps`. CFR and VFR regression tests are reported passing. Semantic timestamps remain candidate retrieval evidence only; no exact edit-boundary claim is introduced.

## 5. Test and synthetic smoke evidence

Reported fresh terminal suite:

```text
PYTHONPATH=experiments:src pytest -q experiments/persistent_local_index/tests
164 passed, 0 failed, 0 skipped
```

Reported per-file counts:

- model-space: 39;
- storage: 24;
- media/PTS: 16;
- embedding: 19;
- source lifecycle: 21;
- indexer: 11;
- search: 21;
- CLI E2E: 13.

Inherited spike regression command was reported as:

```text
PYTHONPATH=src pytest -q \
  experiments/single-video-semantic-spike/test_text_padding_regression.py \
  experiments/single-video-semantic-spike/test_one_pass_sampler.py
```

Result: `4 passed`.

Synthetic real-model smoke used only generated local colour clips plus the frozen local SigLIP model on MPS. Reported observations:

- three 10-second synthetic clips indexed in ~2.49 s;
- two text queries answered in ~0.80 s;
- 9 committed rows = 27,648 vector bytes = 9 x 3072;
- 9 retained thumbnails;
- query-time ffmpeg/ffprobe calls: 0;
- query-time image re-embeddings: 0;
- synthetic source SHA-256 unchanged;
- query `a solid red scene` ranked red first;
- query `a solid blue scene` ranked blue first.

These synthetic colour checks establish plumbing/orchestration only; they are not real-media semantic-quality evidence.

## 6. Failures found and fixed during implementation

The implementation evidence deliberately preserves defects and test-oracle mistakes instead of presenting a success-only history.

### Real implementation defects fixed

1. **Memmap cleanup `UnboundLocalError`.** A closure attempted `del array`, creating a local-binding error. Cleanup ownership was reworked.
2. **Semantic-space change could silently create an unreachable sibling generation.** This violated fail-closed intent; incompatible sibling-space detection was added.
3. **`thumbnail_status` was hard-coded `PRESENT`.** Missing thumbnail cache state could be hidden; status is now propagated from measured state.
4. **Row-alignment operator-precedence bug.** `committed_bytes % dim * 4` was corrected to `committed_bytes % (dim * 4)`.
5. **Semantic-space mismatch was misreported as `MANIFEST_MISSING`.** Query now identifies and names the incompatible semantic-space field.
6. **CLI semantic model identity depended on the local directory name.** Identity was made explicit/artifact-bound rather than path-bound.

### Test/oracle defects corrected

1. A stray placeholder caused a syntax error before intended RED.
2. `sqlite3.Row` was incorrectly compared directly with a tuple.
3. A test incorrectly assumed a huge interval could produce zero samples, despite the proven sampler selecting frame zero by construction.
4. A row/vector test initially hashed thumbnails instead of the actual full-resolution embedded frame bytes and used an over-complicated ordering oracle.
5. Pretty-printed JSON was incorrectly parsed as one line.
6. Some test signatures were not updated when a model-root fixture was introduced.
7. Fake-embedder tests initially failed to provide synthetic processor assets even though semantic-space derivation correctly still requires them.

### Rejected approaches / deliberate compromises

- A two-decode-pass media implementation was rejected because it contradicted the one-pass pixel<->PTS invariant and doubled decode work.
- Silently allowing an incompatible sibling semantic generation under the same v1 root was rejected; fail-closed behavior was preferred.
- The sampler was not weakened to satisfy a mistaken `NO_SAMPLES` test belief; the test was corrected.
- A hidden fake-embedder seam exists only to test CLI orchestration without loading the 812 MB model; it is not used for semantic/performance claims.
- Thumbnail status was added to sample metadata because the approved design requires missing thumbnails to be reported without query-time decode.

## 7. Important remaining v1.x finding

One lifecycle gap is explicitly retained rather than hidden:

> old-digest activity is recomputed inside the per-source commit path. Removing the **last** location referencing a digest without indexing a new source in that same invocation is not currently reconciled.

The current CLI does not expose location deletion, so this state is not reachable through the present v1 command surface. The documented changed-source/duplicate lifecycle tests pass. Nevertheless this is a real candidate for a later v1.x reconciliation pass if explicit location deletion or broader archive inventory reconciliation is added.

## 8. Advantages observed

- Indexing and querying are now cleanly separated; repeated text search does not pay decode/image-embedding cost again.
- Fail-closed semantic-space identity is cheap and happens before query embedding on mismatch.
- SQLite-as-authority plus append-only vector bytes gives a simple crash-tail recovery model.
- Source-native temporal provenance survives persistence.
- Duplicate-byte reuse and unchanged-source skip reduce unnecessary work.
- Query operates over ordinary local artifacts with no server/vector database/cloud requirement.

## 9. Disadvantages / unmeasured risks

- Source-location lifecycle logic is the most intricate part of the prototype and deserves additional real-directory evidence before archive-scale use.
- `fcntl.flock` is only the v1 local single-writer mechanism; this is not distributed coordination.
- Thumbnail publication happens after semantic/source commit; a crash in between can leave a valid vector/sample with a missing thumbnail. This is accepted cache loss and is surfaced as `MISSING`.
- Exact search currently materializes committed metadata rows in memory; behavior at the design target of ~320k rows has not yet been measured.
- Real-media persistent-index retrieval quality has not yet been tested.
- Archive-scale throughput, thumbnail storage, long-run restart behavior, and 400-hour operational feasibility remain unmeasured.

## 10. Safety / scope boundary

Reported implementation execution used:

- network/provider/cloud: NO;
- downloads/package install/model acquisition: NO;
- CUDA/VideoToolbox/ANN/vector DB: NO;
- real user media: NO;
- canonical main modification by the implementation session: NO;
- Gate-0 controller modification: NO;
- Gate maturity/shared contract modification: NO.

`/Users/yusuf/Movies/kolaj-1-uzun.mp4` was explicitly not touched by the persistent-index implementation session.

## 11. Non-claims

This terminal state does **not** establish:

- real-media persistent-index semantic quality;
- 400-hour indexing completion time;
- archive-wide retrieval quality;
- ~320k-row exact-query latency/RAM behavior;
- thumbnail-storage average size;
- production reliability;
- multi-machine/distributed writer safety;
- exact edit boundaries;
- Gate completion/promotion;
- production architecture approval.

The correct state is experimental readiness for a separately authorized bounded real-media smoke.

## 12. Durable next action

Required next authorization:

```text
OWNER_EXPLICITLY_AUTHORIZES_EXACT_REAL_VIDEO_OR_DIRECTORY_FOR_INDEXING
```

A sensible first bounded smoke is the already-understood test source, but the persistent-index operation itself requires fresh explicit owner authorization naming the exact file or directory. No archive-wide authorization is implied.

Do not merge the implementation branch into `main` or a Gate controller merely because this terminal implementation passed synthetic verification.
