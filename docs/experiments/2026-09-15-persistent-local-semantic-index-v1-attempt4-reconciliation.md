# Persistent Local Semantic Index v1 — Attempt 4 Metadata/Result Materialization Reconciliation

**Date:** 2026-09-15  
**Canonical-main parent before this record:** `6d9818b7025ba2dd8f40dc357d195ff8ca7b8b7d`  
**Planning authority:** `planning/persistent-local-semantic-index-v1@0a84753148938fccf3f786b070723dd57ca5a3fc`  
**Implementation branch:** `experiment/persistent-local-semantic-index-v1@93f5d362091555937bf00ed221bb8dc24d656573`  
**Attempt-4 start SHA:** `1f00bcde74fa9c94fc0243393bf9c7c2fb329e73`  
**Disposition:** `EXACT_METADATA_OPTIMIZATION_MATERIAL_SUCCESS — EXACT_OUTPUTS_PRESERVED`  
**Gate effect:** none. This remains a repository-level experimental vertical slice and is not merged into Gate authority or canonical runtime code.

## 1. Reconciliation scope

Attempt 3 established that the exact float32 vector scan itself was cheap at the intended ~320k-row design scale while full SQLite metadata materialization plus Python result-object construction dominated latency and memory. Attempt 4 was a bounded, behavior-preserving optimization of that measured bottleneck only.

The branch-local detailed source of truth remains:

`docs/experiments/2026-09-15-persistent-local-semantic-index-v1-evidence.md`

at `experiment/persistent-local-semantic-index-v1@93f5d362091555937bf00ed221bb8dc24d656573`.

## 2. Independent GitHub verification

Independent reconciliation confirmed:

- remote `experiment/persistent-local-semantic-index-v1` is exactly at `93f5d362091555937bf00ed221bb8dc24d656573`;
- its parent is `1f00bcde74fa9c94fc0243393bf9c7c2fb329e73`, so Attempt 4 is a fast-forward continuation of Attempt 3;
- the commit message records the bounded exact-search metadata/result materialization refactor, 16 new tests, 180 persistent-index tests passing, 4 inherited spike regressions passing, and no real-media access;
- no schema, vector format, model, sampling, calibration, or query wording was changed;
- no ANN/vector database/daemon was introduced;
- the experimental implementation remains isolated from canonical Gate-0 authority.

The runtime/performance measurements below are grounded in the DeepSeek terminal report and branch evidence ledger; they were not independently re-executed by ChatGPT during this reconciliation.

## 3. Measured baseline from Attempt 3

At 320,000 rows:

- core exact vector scoring + realistic Top-K selection: ~41.99 ms median;
- full metadata + search path: ~3,043.62 ms median;
- full committed-metadata load alone: ~2,117.58 ms median;
- fresh one-text process: ~6.967 s;
- fresh seven-text process: ~11.932 s;
- peak RSS: ~3,509 MB;
- RSS after index open: ~282.5 MB.

The measured root cause was one `SampleMeta` per committed row plus one `SearchHit` per active row on every query, with nearly all objects discarded after Top-K.

## 4. Behavior-preserving implementation change

The optimized production query path now:

1. validates generation and semantic-space identity as before;
2. memory-maps the committed vector prefix as before;
3. loads only a compact active-row mask instead of full metadata for all rows;
4. scores the exact committed vector prefix with the same float32 exact-search arithmetic;
5. selects winning rows plus all boundary ties using score + activity state only;
6. fetches full metadata only for the union of winning candidate row IDs;
7. constructs `SearchHit` objects only for returnable results.

The frozen reference `exact_top_k` semantics were retained as an equivalence oracle; the all-rows production metadata loader was removed rather than left as a duplicate production path.

No persistent schema migration was introduced.

## 5. RED / debugging evidence

Two meaningful RED states were preserved:

1. initial import RED because the new indexed exact-search API did not yet exist;
2. a genuine implementation defect after the first refactor attempt: `np.argpartition(active_scores, top_k - 1)` selected the wrong order statistic, causing the candidate threshold to include almost the full active set. Results happened to remain correct but the optimization silently failed.

The second issue was diagnosed by direct reproduction and fixed with the non-negative k-th-largest index `active_scores.size - top_k`.

The bounded-materialization tests are specifically designed to catch that failure mode, rather than only checking final ranking correctness.

Rejected shortcuts included:

- limiting candidates without tie expansion, which would have changed existing tie semantics;
- modifying the frozen reference path in place, which would have weakened equivalence evidence;
- metadata `LIMIT` paging, which was unnecessary after measured primary-key fetches were already sub-millisecond.

## 6. Test evidence

Reported targeted suite:

`test_search_materialization.py` -> **16 passed**.

Reported complete persistent-index suite:

`experiments/persistent_local_index/tests` -> **180 passed**.

Reported inherited spike regressions:

- SigLIP max-length-padding regression;
- CFR/VFR one-pass measured-PTS protections;

-> **4 passed**.

Coverage includes all-active ordering, mixed active/inactive rows, inactive exact-query-vector exclusion, tie order, boundary ties, Top-K bounds, missing thumbnails, input validation, full-generation reference equivalence, and bounded `SampleMeta`/`SearchHit` construction.

## 7. 320k before/after latency

Progressive measured medians:

| Rows | Old metadata+search | New metadata+search | Speedup |
| ---: | ---: | ---: | ---: |
| 10,000 | 71.63 ms | 2.18 ms | 32.8x |
| 80,000 | 692.70 ms | 12.33 ms | 56.2x |
| 160,000 | 1,449.94 ms | 23.77 ms | 61.0x |
| 320,000 | 3,043.62 ms | 47.69 ms | **63.8x** |

At 320k the optimized p95 was ~48.52 ms. The exact vector scan remained ~39–42 ms and therefore became the dominant variable search cost, as expected.

The former ~2.1 s all-row metadata load disappeared. Top-K metadata fetch measured ~0.56 ms.

## 8. Fresh-process end-to-end effect

Reported 320k fresh-process timings:

- one text: 6.967 s -> **3.126 s** (~2.23x faster);
- seven texts: 11.932 s -> **~3.036 s** (~3.93x faster).

A decomposed seven-text invocation after model load reported approximately:

- text embedding: 0.095 s;
- active-state load: 0.075 s;
- exact vector scoring: 0.275 s for seven queries;
- candidate selection: 0.026 s;
- winning-row metadata fetch: 0.0009 s;
- result construction: 0.013 s;
- measured invocation total: 0.459 s.

The now-dominant fixed cost is the frozen model cold load, reported around 2.6–2.7 s for a fresh process.

## 9. Memory effect

Reported 320k memory changes:

- RSS after index open: 282.5 MB -> **33.6 MB** (~88% reduction at open);
- RSS after first full matvec: 1,221.1 MB -> **~973.3 MB**;
- full CLI peak RSS: ~3,509 MB -> **~3,165 MB** (~10% reduction, ~350 MB).

The mapped vector prefix remains 937.5 MiB and is still correctly distinguished from resident memory. No swap/memory-pressure event was observed.

Peak RSS is now dominated by the model/MPS runtime plus the resident vector prefix rather than a 320k-entry Python metadata/result object graph.

## 10. Exact-output equivalence

Attempt 4 reported zero field mismatches against the frozen Attempt-3 output for both one-text and seven-text invocation shapes.

Preserved fields include:

- rank;
- exact reported score for same invocation shape;
- row ID;
- source SHA/path;
- measured PTS and timebase;
- derived timestamp;
- thumbnail path/status.

Inactive-row exclusion remained PASS, including a case where an inactive row held the exact query vector. Existing tie behavior and boundary-tie expansion remained PASS.

The prior MPS batch-shape-dependent ~1e-8 text-embedding variation remains a model-side observation; Attempt 4 did not treat it as search nondeterminism or attempt to alter it.

## 11. Query purity / safety boundary

Reported optimized query behavior:

- FFmpeg calls: 0;
- ffprobe calls: 0;
- source-media opens: 0;
- image re-embedding: NO;
- index mutation: NO;
- real user media touched: NO;
- network/download/cloud: NO;
- canonical main modified by execution session: NO;
- Gate-0 controller modified: NO.

Attempt 4 used the existing synthetic 320k benchmark state; no real-media execution was authorized or performed.

## 12. Advantages newly established

- Exact brute-force search remains viable at the ~320k-row design scale after removing avoidable metadata/object work.
- No ANN/vector database is needed merely to eliminate the previously measured ~3 s exact-query path.
- Full metadata is fetched only after exact Top-K row selection.
- The performance gain preserves the existing exact-ranking and provenance contract.
- The architecture remains local-file based and serverless.

## 13. Remaining costs / disadvantages

- Fresh-process UX is now dominated by ~2.6–2.7 s frozen-model cold load.
- The exact full-prefix matvec remains O(N), although only tens of milliseconds at 320k on the measured machine.
- An activity mask still requires a one-time row-state load per fresh invocation (~75 ms at 320k).
- Peak RSS remains ~3.1 GiB due mainly to model/MPS runtime plus resident vector pages; the refactor improves but does not eliminate query-process memory cost.
- Model lifetime/process lifetime optimization would introduce a new design question and was deliberately not attempted here.

## 14. Non-claims

Attempt 4 does **not** establish:

- archive-wide semantic quality;
- production latency or concurrency;
- ANN superiority or inferiority outside the measured 320k exact-search case;
- larger-than-320k scale behavior;
- production model-serving architecture;
- Gate completion/promotion;
- exact edit boundaries;
- real-directory reliability;
- generalized speedups on other hardware.

## 15. Current experimental interpretation

`EXACT_METADATA_OPTIMIZATION_MATERIAL_SUCCESS`

At the intended coarse-sampling design scale, the measured search bottleneck moved from all-row metadata/result materialization to the fixed model cold-load plus the expected exact vector scan. Exact search semantics remained intact.

The next measured UX frontier is therefore model/process lifetime, not ANN/vector indexing.

Any move to a persistent model process, daemon, local service, or other model-lifetime mechanism should be treated as a separate architecture/design turn rather than silently folded into this bounded refactor.
