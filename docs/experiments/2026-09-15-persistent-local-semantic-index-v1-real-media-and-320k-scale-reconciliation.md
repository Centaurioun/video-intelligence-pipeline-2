# Persistent Local Semantic Index v1 — Real-Media + 320k Scale Reconciliation

**Date:** 2026-09-15  
**Canonical-main parent before this record:** `1026a790d6b85d88f38036fee4cd6decfe31c439`  
**Implementation branch:** `experiment/persistent-local-semantic-index-v1`  
**Attempt-2 branch head:** `01ff6a0d9238c8bf443d067d3fcd46e0bb65f70a`  
**Attempt-3 branch head:** `1f00bcde74fa9c94fc0243393bf9c7c2fb329e73`  
**Planning authority:** `planning/persistent-local-semantic-index-v1@0a84753148938fccf3f786b070723dd57ca5a3fc`  
**Gate effect:** none. This is experimental vertical-slice evidence only; the implementation branch is not merged into Gate authority or canonical runtime code.

## 1. Reconciliation scope

This record reconciles the two terminal evidence turns after the synthetic implementation was completed:

1. **Attempt 2 — one-file real-media persistent-index smoke** on the single explicitly authorized source `/Users/yusuf/Movies/kolaj-1-uzun.mp4`.
2. **Attempt 3 — synthetic 320,000-row target-scale exact-search benchmark** with no real-media access and no implementation change.

The branch-local detailed source of truth remains:

`docs/experiments/2026-09-15-persistent-local-semantic-index-v1-evidence.md`

at `experiment/persistent-local-semantic-index-v1@1f00bcde74fa9c94fc0243393bf9c7c2fb329e73`.

This canonical-main reconciliation preserves the material positive findings, negative findings, measurement caveats, rejected interpretations, and next-design implications without merging the experimental implementation itself.

## 2. Independent GitHub verification

Independent GitHub reconciliation confirmed:

- remote `experiment/persistent-local-semantic-index-v1` is exactly at `1f00bcde74fa9c94fc0243393bf9c7c2fb329e73`;
- `01ff6a0d9238c8bf443d067d3fcd46e0bb65f70a` is the direct parent of `1f00bcde...`;
- the `01ff6a0d... -> 1f00bcde...` change is exactly one documentation/evidence commit: `+454 / -0` in `docs/experiments/2026-09-15-persistent-local-semantic-index-v1-evidence.md`;
- no implementation code changed in Attempt 3;
- the implementation branch remains isolated from canonical Gate-0 authority;
- the canonical Gate-0 controller was not modified by these attempts.

The runtime/performance measurements below are grounded in the DeepSeek terminal reports and branch evidence ledger; they were not independently re-executed by ChatGPT during this reconciliation.

---

# Part I — Attempt 2: one-file real-media persistent-index smoke

## 3. Authorization boundary

The owner explicitly authorized exactly one source for read-only persistent indexing and query smoke:

`/Users/yusuf/Movies/kolaj-1-uzun.mp4`

No other real media or directory was authorized. The execution report records no sibling-directory enumeration and no other real-media access.

Source identity before and after:

`3834a376ecdb0358377fbc62f914f651a21e8486f9a23c179b22a1b889fae139`

Source size and mtime were also reported unchanged. Therefore:

`SOURCE_MUTATED = NO`

## 4. Real-media index result

Fresh index root:

`/Users/yusuf/Movies/kolaj-1-uzun-persistent-index-smoke-20260915-bced5d2`

Observed source/runtime facts:

- stream: HEVC, stream index 0;
- dimensions: 1440x2560;
- duration: 265.333333 s;
- source-native timebase: `1/600`;
- device: Apple MPS;
- sampling interval: 4.5 s;
- selected samples: 59;
- committed rows: 59;
- embedding dimension: 768 float32;
- vector bytes: 181,248 = `59 x 768 x 4`;
- thumbnails: 59, all present;
- generation ID: `648dd7391ec2a92e51aacdd20d11c4bd5c1a5c3ce88755066c819e0faa852508`;
- semantic-space ID: `3840a0f423fa3ef6c273e61160131dd8c698c83873e9db99ee1917750e5cfe5a`;
- fresh persistent index wall time: **51.30 s**.

All 59 persisted samples were reported to retain source SHA, integer measured PTS, `1/600` timebase, derived readable timestamp, and thumbnail reference/status. The temporal path therefore preserves the project invariant:

`sampled pixels <-> same decoded frame <-> measured PTS <-> source-native timebase`

No exact frame evidence was inferred from nominal 60 fps.

## 5. Persistent query result

Seven previously frozen natural-language queries were executed against the persisted vectors in separate processes.

Observed wall times:

- first seven-query process: **3.07 s**;
- second seven-query process: **2.58 s**;
- third confirmation: **2.57 s**.

The normalized search results were reported byte-identical between equivalent seven-query invocations: 35/35 Top-5 hits matched in row ID, source SHA, measured PTS, timebase, timestamp, and thumbnail identity, with zero score delta for the same invocation shape.

Dynamic purity evidence:

- query-time FFmpeg calls: 0;
- query-time ffprobe calls: 0;
- process-spawn audit events for media work: 0;
- source-media opens: 0;
- index mutation: 0;
- image re-embedding: structurally absent from the query surface.

The no-decode claim was dynamically checked with fail-fast FFmpeg/ffprobe PATH traps after correcting an initial shell-observability mistake. The image-re-embedding claim remains structurally/observationally grounded rather than falsely upgraded to a stronger dynamic evidence class.

## 6. Real-media retrieval quality

Attempt 2 returned the same underlying scene retrieval behavior as the corrected non-persistent spike. The terminal classification used a slightly more scene-oriented rubric and reported:

- STRONG: 7
- USEFUL: 0
- WEAK: 0
- MISS: 0

Important qualification: this **must not be interpreted as a new semantic-model improvement over the earlier 5 STRONG + 2 USEFUL result**. Q3 and Q4 still had the anchor-nearest sampled frame at rank 2; the new rubric counted Top-1 as STRONG because it was the same visually appropriate scene a few seconds later. The persisted implementation did not change model, queries, scoring, or sampling.

Key examples:

- Q1: 00:00:04.500, Top-1, score ~0.0722;
- Q2: 00:00:58.517, Top-1, score ~0.1596;
- Q3: Top-1 00:02:19.550; anchor-nearest expected frame at Top-2, +1.05 s;
- Q4: Top-1 00:02:42.050; anchor-nearest expected frame at Top-2, +0.55 s;
- Q5: Top-1 00:02:55.550; wider castle view beats the closer group-selfie frame at rank 2 on a narrow margin;
- Q6: 00:03:22.550, Top-1;
- Q7: 00:03:40.550, Top-1.

Absolute cosine scores remained modest. Ranking quality, not a fixed absolute threshold, carried the retrieval.

## 7. Unchanged-source re-index behavior

A second index invocation against the exact same source and generation returned:

`SKIPPED_UNCHANGED`

Observed wall time: **2.74 s**.

Verified unchanged:

- vector SHA-256;
- vector byte size;
- committed row count `59 -> 59`;
- source row range `[0,59)`;
- index-state snapshot;
- staging state;
- thumbnail count.

No new vector rows, image embeddings, or thumbnails were produced.

One friction point remained: the CLI still loads the frozen model before discovering that all inputs are unchanged, so a no-op re-index pays roughly 2.6–2.7 s of avoidable startup cost. This is not currently a correctness defect.

## 8. Real-media performance interpretation

The previous non-persistent corrected single-video run was ~44.839 s because it included media decode plus image embedding plus search in one operation.

The persistent search path answered the same query set in ~2.6–3.1 s from a fresh process, without source decode or image re-embedding.

This establishes the intended architectural separation for one real source:

`one-time media indexing -> persistent vectors/metadata -> repeated cheap text queries`

It does **not** establish archive-wide indexing duration, archive-wide retrieval quality, or production latency.

---

# Part II — Attempt 3: synthetic 320k target-scale exact-search benchmark

## 9. Purpose and target scale

The intended coarse-sampling design scale for ~400 hours is approximately:

`400 h x 3600 / 4.5 s = 320,000 samples`

At 768 float32 values per row:

`320,000 x 768 x 4 = 983,040,000 bytes = 937.5 MiB raw vectors`

Attempt 3 therefore constructed a synthetic 320,000-row index through the real storage contract to measure exact-query scale without touching real media.

No real media was decoded, hashed, or opened. No user media directory was enumerated.

## 10. Synthetic index construction

Synthetic shape:

- 400 fake source objects;
- 800 samples per source;
- 320,000 active sample rows total;
- deterministic normalized float32 vectors;
- dimension 768;
- deterministic fake source SHA-256 values;
- synthetic nonexistent source namespace;
- deterministic PTS-like integer/timebase metadata;
- no thumbnails created;
- no FFmpeg/ffprobe invocation.

Artifact measurements:

- `vectors.f32`: **983,040,000 bytes**;
- `index.sqlite`: **71,217,152 bytes**;
- total synthetic index: **1,054,291,534 bytes** (~1005.5 MiB);
- committed rows: 320,000;
- vector physical bytes == committed bytes;
- no uncommitted tail;
- synthetic build wall time: **2.139 s**.

The 2.139 s construction is **not** a media-indexing benchmark; no video decode or image embedding occurred.

## 11. Progressive exact-search benchmark

Measured one warm-up plus seven timed repetitions per size:

| Rows | Core exact search median | Core p95 | Real metadata+search median | Metadata+search p95 | Metadata load median |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10,000 | 0.90 ms | 1.03 ms | 71.63 ms | 92.04 ms | 56.15 ms |
| 80,000 | 9.31 ms | 9.38 ms | 692.70 ms | 725.23 ms | 537.53 ms |
| 160,000 | 19.03 ms | 19.18 ms | 1,449.94 ms | 1,636.71 ms | 1,054.78 ms |
| 320,000 | **41.99 ms** | **44.23 ms** | **3,043.62 ms** | **3,179.71 ms** | **2,117.58 ms** |

The first core-search measurement had used `argpartition` and reported ~22.62 ms at 320k. That was judged too optimistic for the current engine's realistic Top-K selection, so the benchmark was rerun with `argsort(-scores)[:5]`, yielding the retained 41.99 ms figure. Both measurements were preserved rather than hiding the first attempt.

## 12. Main scale finding: vector arithmetic is not the bottleneck

At 320,000 rows:

- float32 matrix-vector scoring + realistic Top-5 selection: ~42 ms;
- full metadata+search engine path: ~3,044 ms;
- metadata load alone: ~2,118 ms.

Therefore only ~1.4% of the measured exact-search path is the raw vector arithmetic.

The dominant work is:

1. materializing ~320,000 SQLite sample metadata rows into Python objects;
2. constructing/sorting a large `SearchHit` object population.

This means the measurement **does not justify jumping to ANN/FAISS/vector DB**. The first measured optimization target is metadata/result materialization while preserving exact-search semantics.

## 13. Full real-SigLIP query timings at 320k

Using the frozen local SigLIP model on MPS and synthetic vectors:

- one-text fresh process: **6.967 s** first recorded run; observed range 5.770–6.967 s;
- seven-text fresh process: **11.932 s** first recorded run; observed range 11.441–11.932 s;
- best-effort cache-pressured seven-text run: 11.697 s.

Decomposed seven-text observation:

- metadata load: ~2.095 s;
- text embedding: ~0.103 s total for seven texts;
- exact vector search/result path: ~1.082 s total for seven searches;
- model cold load inferred at ~5.70 s.

Interpretation:

- fresh-process model startup is the largest fixed cost;
- scale-dependent metadata/result work is the largest archive-size-dependent cost;
- exact vector arithmetic itself remains small.

The 7-text invocation amortizes fixed costs strongly; six extra texts add only about three seconds rather than multiplying the entire fresh-process cost by seven.

## 14. Memory measurements

At the 320k target shape:

- vector mapping length: 937.5 MiB;
- RSS after index open with metadata materialized: ~282.5 MB;
- after first full vector pass: ~1,221 MB;
- subsequent passes plateaued around ~1,221 MB;
- peak process RSS across full query processes: ~3.51 GiB;
- observed swap growth: 0;
- observed swapouts delta: 0;
- compressor remained effectively flat.

Important distinction preserved:

`mapped bytes != resident bytes`

Opening the mmap did not immediately page in all 937.5 MiB. The vector pages became resident when scanned. Much of the ~3.5 GiB peak is attributed to per-query Python metadata/result objects and runtime overhead, not to the vector file alone.

This was measured on a ~24 GiB Apple Silicon machine; it must not be treated as a universal memory guarantee.

## 15. Query purity at target scale

At 320k synthetic rows:

- FFmpeg calls: 0;
- ffprobe calls: 0;
- source-media opens: 0;
- image re-embedding: no query surface;
- vector/index mutation: none;
- missing thumbnails did not trigger decode.

The persistence invariant therefore held at target row count as well as at the one-file real-media smoke.

## 16. Determinism and MPS batch-shape qualification

Repeated same-shape invocations were byte-identical in output and preserved identical Top-5 row ordering.

A small but genuine model-side numerical observation was diagnosed:

- embedding the same text alone versus inside a seven-text batch on MPS changes vector elements at approximately `8e-08` maximum;
- resulting score differences were at most ~`3e-08`;
- ranking remained stable;
- the effect was isolated to the MPS text embedding batch shape, not exact search.

Therefore:

- same invocation shape: bitwise-repeatable in the measured runs;
- different batch shapes: treat scores as numerically equivalent within normal float tolerance, not bitwise identical;
- ranking stability was preserved here but is not a universal proof for arbitrarily tiny score margins.

## 17. Target-scale status

Recorded classification:

`EXACT_SEARCH_USABLE_BUT_COSTLY_AT_320K`

Why not `COMFORTABLE`:

- ~3 s/query-scale work is being spent on avoidable metadata/result materialization;
- peak RSS is ~3.5 GiB per fresh query process;
- both costs grow with row count.

Why not `NEEDS_FURTHER_DESIGN`:

- correctness held;
- exact vector arithmetic is only ~42 ms at 320k;
- no swap was observed on the measured machine;
- the system remains usable for interactive/experimental work;
- the measured first optimization target is straightforward and orthogonal to ANN.

## 18. Attempt-3 failures/tooling corrections

No implementation defect was found and no implementation/test code changed.

Measurement tooling corrections were preserved:

1. an initial `argpartition` core benchmark understated realistic Top-K work; retained final comparison uses full argsort;
2. the first memory probe did not sufficiently distinguish mapping from physical footprint; it was rewritten to report mapped and resident memory separately;
3. a `Path.with_suffix` use briefly hid one stdout capture by replacing rather than appending an extension.

A separate model-side MPS batch-shape numerical variance was diagnosed rather than dismissed as noise.

## 19. Current best next optimization target

Measured priority order for query latency at ~320k rows:

1. **avoid loading every sample's full metadata into Python for every query invocation**;
2. **avoid constructing/sorting 320k `SearchHit` objects when only Top-K rows are needed**;
3. optionally consider model-session persistence later if cold-start UX becomes important;
4. do **not** introduce ANN/vector database merely to optimize a 42 ms exact vector scan.

A promising exact-semantics-preserving shape is:

`validate index -> mmap vectors -> score all active rows -> select Top-K row IDs -> fetch metadata only for those row IDs -> construct K SearchHit objects`

However, this is an implementation/design change and requires its own TDD/verification turn before adoption. This reconciliation does not implement it.

## 20. Safety / scope

Attempt 2:

- exactly one owner-authorized real source;
- source read-only and hash-stable;
- no network/download/provider/cloud;
- no other real media.

Attempt 3:

- no real-media read/decode/hash;
- no media-directory enumeration;
- no FFmpeg/ffprobe;
- synthetic index only;
- no implementation change;
- no ANN/vector DB/cloud.

Neither attempt modifies Gate maturity or shared contracts.

## 21. Standing non-claims

These attempts do not establish:

- archive-wide semantic quality;
- production readiness;
- exact edit boundaries;
- real 400-hour indexing duration;
- real thumbnail storage cost at archive scale;
- real 320k-row metadata distribution;
- concurrency/multi-user performance;
- ANN superiority or inferiority beyond the measured exact-search arithmetic;
- distributed writer reliability;
- Gate promotion;
- production architecture approval.

## 22. Durable state after reconciliation

Persistent-index experimental branch evidence head:

`experiment/persistent-local-semantic-index-v1@1f00bcde74fa9c94fc0243393bf9c7c2fb329e73`

The implementation remains experimental and unmerged. The strongest current evidence is:

- one authorized real video can be indexed persistently with measured PTS/timebase;
- repeat queries can execute without source decode or image re-embedding;
- unchanged source is skipped;
- retrieval is stable across separate equivalent query processes;
- exact vector scoring itself remains cheap at the intended ~320k-row sample count;
- metadata/result materialization, not ANN-worthy vector arithmetic, is the measured scale bottleneck.
