# Single-Video Semantic Retrieval Spike — Findings, Failures, Fixes, Performance, and Next Design

**Date:** 2026-09-15  
**Repository:** `Centaurioun/video-intelligence-pipeline`  
**Canonical-main anchor before this record:** `7dadc24b47daf1ad806a710a64bcaa0b367ee58f`  
**Remote experiment branch:** `experiment/single-video-semantic-spike-v1`  
**Remote experiment head:** `0c14fce1fa979d466292fbd5cfd1e876bfacee92`  
**Experiment classification:** `THROWAWAY_SPIKE_PROTOTYPE_WITH_REMOTE_PRESERVATION`  
**Gate effect:** none; no Gate maturity or promotion is implied by this document.

---

## 1. Purpose of this record

This document preserves the complete evidence trail from the first real-media semantic-retrieval spike: what was attempted, what failed, what succeeded, what changed, why it changed, what was measured, what remains uncertain, and which follow-up design direction was selected for further study.

The goal of the spike was deliberately narrower than the full project:

> Can the existing local-first project take an ordinary local video, sample real source-native frames, embed them with a local visual-text model, accept natural-language queries, and return useful moments with attributable source-native PTS/timebase evidence?

This was **not** a Gate-0 completion run, Gate-1 benchmark, Gate-2 reliability study, Gate-3 editing/QC run, production-readiness test, cloud/provider test, or archive-scale indexing run.

The source media was always read-only. Semantic/model retrieval timestamps remain **candidate retrieval evidence**, never exact edit boundaries.

---

## 2. Source video and fixed test conditions

### 2.1 Authorized real source

- Path: `/Users/yusuf/Movies/kolaj-1-uzun.mp4`
- SHA-256: `3834a376ecdb0358377fbc62f914f651a21e8486f9a23c179b22a1b889fae139`
- Duration: `265.333333 s`
- Selected stream: HEVC, `1440x2560`, nominal `60/1`, `15920` frames
- Source timebase: `1/600`
- Source mutation: **none**; before/after SHA-256 matched in all real runs.

### 2.2 Frozen local model/runtime

- Model: `google/siglip-base-patch16-224`
- Frozen revision: `7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed`
- `model.safetensors` SHA-256: `2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8`
- Model root: `/Users/yusuf/.codex/model-acquisition/gate0/google--siglip-base-patch16-224/7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed`
- Historical Python runtime: `/Users/yusuf/.codex/runtime-roots/run-20260913-macos-stage-a-py314-continuation/venv`
- FFmpeg/ffprobe: local existing installation, no download during the spike.
- Network/provider/cloud use: **none**.

### 2.3 Fixed semantic queries

The real-video quality runs used the same seven English queries without post-hoc rewriting:

1. `two young women taking a selfie inside a shopping mall`
2. `a line of ballet students standing in a dance studio`
3. `a group of dancers rehearsing together in front of mirrors`
4. `a male dance instructor leading a group dance rehearsal`
5. `three women taking a selfie outdoors in front of a historic castle and fountain`
6. `a large Gothic cathedral in a city square`
7. `a poster showing a male ballet dancer leaping through the air`

Human-observed rough anchors, used only for post-hoc evaluation and never as retrieval inputs:

- Q1 ≈ `00:03`
- Q2 ≈ `00:57`
- Q3 ≈ `02:14`
- Q4 ≈ `02:37`
- Q5 ≈ `02:54`
- Q6 ≈ `03:24`
- Q7 ≈ `03:40`

These anchors are approximate editorial observations, not measured edit boundaries.

---

## 3. Chronological experiment log

## 3.1 Preflight false negative: model/runtime initially reported missing

The first preflight stopped with:

`SINGLE_VIDEO_SPIKE_BLOCKED_LOCAL_MODEL_MISSING`

and also reported that the ML runtime was missing.

That conclusion was **not final**. The search had checked repository-local paths, Hugging Face cache, and ordinary interpreters, but the earlier Gate-0 work had intentionally stored the actual model and runtime under `~/.codex`.

A targeted re-preflight checked the exact durable historical locations and found:

- the frozen SigLIP bundle present with the expected weights digest;
- the historical venv present;
- imports for torch, transformers, tokenizers, sentencepiece, safetensors, PIL, and numpy working.

### Lesson

A future preflight must search durable project-recorded external runtime/model roots before concluding that an asset is absent. Repository-local-only discovery can create a false blocker.

---

## 3.2 Initial synthetic vertical slice

A disposable single-video semantic retrieval runner was created on the isolated experiment branch.

The runner established the following minimal path:

`video -> source-native PTS/timebase -> sampled frame pixels -> local SigLIP image embeddings -> local SigLIP text embedding -> cosine ranking -> JSON/report/thumbnails`

Synthetic E2E result:

- 30 s synthetic clip
- 900 enumerated source frames
- 7 coarse samples at ~4.5 s spacing
- 3 text queries
- `results.json`, `report.md`, and thumbnails produced
- source remained byte-identical
- real local SigLIP image embedding passed
- real local SigLIP text embedding passed
- ordinal/PTS binding checks passed

Two mechanical compatibility issues were encountered and corrected in the spike:

1. FFmpeg 9 had removed the previously used `-vsync 0`; the spike used `-fps_mode passthrough` instead.
2. `LocalSiglipEmbeddingAdapter.embed` expected `("pixels", <bytes>)`, not `("image", <path>)`; the runner was corrected to pass PNG bytes.

These were mechanical integration issues, not model-quality findings.

---

## 3.3 First real-video run: 7/7 MISS

The first honest real-video run used:

- 59 sampled images, approximately one every 4.5 s;
- each sampled image embedded once;
- all seven fixed queries ranked against the same cached image embeddings;
- Top-K = 5.

### First-run result

- STRONG: `0`
- USEFUL: `0`
- WEAK: `0`
- MISS: `7`

Observed behavior:

- only four distinct frames occupied Top-1 across seven unrelated queries;
- `00:04:07.500` was Top-1 for three different queries;
- image/text similarity values clustered near zero, often marginally negative;
- Top-5 lists heavily overlapped across semantically distinct queries.

Representative failures:

- cathedral query did not retrieve the cathedral anchor;
- ballet-poster query did not retrieve the poster anchor;
- selfie, dance-studio, and architecture queries were poorly separated.

Initial spike conclusion:

`REAL_VIDEO_SEMANTIC_RETRIEVAL_POOR`

A tentative collage/multi-panel-dilution hypothesis was mentioned, but this was later rejected as unsupported by visual inspection: the supplied screenshots showed a sequential full-frame video rather than simultaneous multi-panel collage frames.

### Performance complication in the first real run

The earliest extraction method used one `select=eq(n,N)` decode per requested ordinal, effectively re-decoding from frame 0 for every sample. On this 265 s, 1440x2560 HEVC source the attempt exceeded a 600 s foreground cap and was killed.

The spike was changed to one summed/select extraction pass. This reduced the extraction behavior to one sequential decode for the selected ordinals. The retrieval logic, model, queries, sampling density, and scores were not tuned as part of that mechanical correction.

---

## 3.4 Root-cause diagnostic: SigLIP text preprocessing bug

A seven-anchor diagnostic was performed using independently extracted source frames nearest the seven rough human anchors.

### Current adapter behavior

The text branch called the processor without max-length padding:

`processor(text=value, return_tensors="pt")`

Current-adapter text-text cosine summary:

- minimum off-diagonal cosine: `0.5913`
- maximum off-diagonal cosine: `0.7727`
- mean off-diagonal cosine: `0.6945`

Current-adapter expected-anchor ranks:

`Q1=1, Q2=4, Q3=3, Q4=2, Q5=5, Q6=7, Q7=5`

Only 1/7 expected anchor images ranked first.

### Reference padded path

The identical model/processor/scoring path was repeated with:

`padding="max_length"`

Padded text-text cosine summary:

- minimum: `0.2163`
- maximum: `0.7760`
- mean: `0.4605`

Expected-anchor ranks became:

`Q1=1, Q2=1, Q3=1, Q4=1, Q5=1, Q6=1, Q7=1`

The official SigLIP joint forward path also produced 7/7 correct corresponding top-1 anchors.

### Root-cause classification

- `H1_CONFIRMED`
- `TEXT_EMBEDDING_COLLAPSE = YES`
- `IMAGE_EMBEDDING_COLLAPSE = NO`
- `SCORING_PATH_MISMATCH = YES`, with the divergence at the **text preprocessing call**, not at cosine-vs-logits scoring.

The sharpest individual diagnostic was Q6: the cathedral anchor ranked **last** under the unpadded path and **first** under both padded/reference paths.

### Fix

The authorized semantic fix was exactly one line:

```python
inputs = self.processor(text=value, padding="max_length", return_tensors="pt")
```

No query templates, truncation changes, normalization changes, score calibration, threshold tuning, or model change were introduced.

TDD evidence:

- RED: regression test failed because `padding` was `None` rather than `max_length`;
- GREEN: same test passed after the one-line change;
- fixed-adapter seven-anchor check: 7/7 expected anchors Top-1.

---

## 3.5 Apple GPU / MPS investigation

The original Gate-0 SigLIP adapter had been intentionally CPU-only for its earlier Stage-A feasibility boundary. CPU-only behavior was therefore a historical contract choice, not a fundamental SigLIP limitation.

### MPS capability

- MPS built: `YES`
- MPS available: `YES`
- silent CPU fallback used: `NO`
- CPU-vs-MPS semantic equivalence: `PASS`
- seven corrected anchor queries remained 7/7 Top-1 on MPS.

### 59-image throughput measurements

CPU serial:

- `3.086 s`
- `19.12 images/s`

CPU batched, best tested batch size 32:

- `2.419 s`
- `24.39 images/s`
- `1.28x` vs CPU serial

MPS batched, best tested batch size 8:

- `0.740 s`
- `79.73 images/s`
- `4.17x` vs CPU serial
- `3.27x` vs CPU batched

Larger tested MPS batches were slightly worse:

- bs 8: `79.73 images/s`
- bs 16: `78.67 images/s`
- bs 32: `68.37 images/s`

### Interpretation

MPS materially improved image embedding throughput while preserving retrieval semantics. GPU inference was therefore adopted for the spike.

However, MPS was **not** the main end-to-end scaling bottleneck.

---

## 3.6 Corrected + MPS full real-video run

After the semantic fix and MPS path were validated, the same seven queries were rerun without wording changes or quality tuning.

### Quality

- STRONG: `5`
- USEFUL: `2`
- WEAK: `0`
- MISS: `0`

Per-query summary:

| Query | Expected rough anchor | Best result classification |
|---|---:|---|
| Q1 mall selfie | ~3 s | STRONG |
| Q2 ballet-student line | ~57 s | STRONG |
| Q3 mirrored rehearsal | ~134 s | USEFUL |
| Q4 male instructor/group rehearsal | ~157 s | USEFUL |
| Q5 outdoor selfie/historic architecture | ~174 s | STRONG |
| Q6 Gothic cathedral | ~204 s | STRONG |
| Q7 leaping male ballet dancer poster | ~220 s | STRONG |

This transformed the real-video result from `0/0/0/7` to `5/2/0/0` with the semantic change limited to the verified one-line text-padding fix. Device choice did not alter ranking semantics.

### End-to-end timing before PTS optimization

- total wall: `313 s`
- source duration: `265.333 s`
- real-time factor: `1.18`

Breakdown:

- frame enumeration: `271.612 s`
- one-pass selected-frame extraction: `35.947 s`
- model cold load: `1.899 s`
- MPS image embedding: ~`0.74 s` in the microbenchmark; full-run recorded image-embedding work remained small relative to enumeration/decode
- text embedding: ~`0.12 s` in the earlier measured path

### Critical finding

The dominant cost was not AI inference. It was full per-frame PTS enumeration through ffprobe.

The 271.6 s enumeration represented roughly 87% of the then-measured run.

A naive linear extrapolation at RTF 1.18 gave approximately:

- 1 h source -> 1.18 h processing
- 100 h -> 118 h
- 400 h -> 472 h (~19.7 days)

This estimate was later superseded by the one-pass PTS optimization below.

---

## 3.7 PTS-enumeration bottleneck removal

The expensive structure was:

`full ffprobe frame enumeration -> choose 59 frames -> second decode/extraction pass`

The optimized spike changed this to:

`cheap stream metadata probe -> one sequential FFmpeg decode/select pass -> selected pixels + measured PTS from the same decoded frame`

The hard project rule was preserved:

- no `seconds × nominal FPS` frame inference;
- selected images retained actually observed source-native presentation timestamps;
- PTS and image pixels came from the same decode pass.

### Temporal tests

- CFR temporal test: `PASS`
- VFR temporal test: `PASS`
- no-full-enumeration spy: `PASS`
- full-frame `ffprobe -show_frames`: removed from the optimized path.

For the VFR fixture, every emitted timestamp matched a source-native `pts_time` from a reference enumeration rather than ordinal/nominal-FPS arithmetic.

### Extraction performance

New stream metadata probe:

- `0.022 s`

New one-pass sample extraction:

- real run: `35.878 s`
- isolated benchmark: `36.167 s`

Historical sample path:

- enumeration `271.612 s`
- extraction `35.947 s`
- combined ~`307.56 s`

Optimized sample path:

- ~`36.19 s`

Improvement:

- about `8.5x` for the sample path.

### PTS sample comparison with historical 59-sample run

- exact matches: `8`
- neighboring-frame differences: `51`
- maximum absolute delta: `0.05 s`
- mean absolute delta: `0.0353 s`

All differences were 1–3 real frames at ~60 fps and were attributable to the new selector anchoring on actual filter presentation time rather than the old nearest-enumerated-ordinal policy.

The differences were not hidden or forced to match.

---

## 3.8 Final optimized real-video run

Final optimized run conditions:

- same source video;
- same seven queries;
- same ~4.5 s sampling interval;
- same Top-K;
- corrected `padding="max_length"`;
- Apple MPS;
- validated MPS batch size 8;
- one-pass PTS-bound extraction;
- no query tuning;
- no model change;
- no source mutation.

### Final measured performance

- source duration: `265.333 s`
- total wall: `44.839 s`
- real-time factor: `0.169`

Breakdown:

- metadata probe: `0.022 s`
- sample extraction/decode: `35.878 s`
- model cold load: `1.903 s`
- MPS image embedding: `6.359 s`
- text embedding: `0.029 s`
- ranking/reporting: `0.016 s`

### Final quality

Quality remained unchanged relative to the corrected pre-optimization run:

- STRONG: `5`
- USEFUL: `2`
- WEAK: `0`
- MISS: `0`

Selected results retained measured PTS on timebase `1/600`.

Representative final results:

| Q | Rough anchor | Top-1 timestamp | Best expected rank | Classification |
|---|---:|---:|---|---|
| Q1 | 3 s | 4.500 s | Top-1 | STRONG |
| Q2 | 57 s | 58.517 s | Top-1 | STRONG |
| Q3 | 134 s | 139.550 s | Top-2 (135.1 s also in Top-3) | USEFUL |
| Q4 | 157 s | 162.050 s | Top-2 (157.6 s also in Top-3) | USEFUL |
| Q5 | 174 s | 175.550 s | Top-1 | STRONG |
| Q6 | 204 s | 202.550 s | Top-1 | STRONG |
| Q7 | 220 s | 220.550 s | Top-1 | STRONG |

### Diagnostic single-machine extrapolation

Using measured RTF `0.169`:

- 1 h source -> ~608 s processing (~0.17 h)
- 100 h -> ~16.9 h
- 400 h -> ~67.6 h

Excluding one-time model cold-load overhead:

- ~64.7 h for 400 h under the same diagnostic assumptions.

These are **linear single-machine diagnostic extrapolations**, not production benchmarks. They should be treated as order-of-magnitude planning evidence, not promises.

### Current remaining performance bottleneck

Software HEVC decode/sample extraction now dominates:

- ~35.9 s of a 44.8 s run (~80%)
- MPS embedding is no longer the dominant cost.

Because RTF 0.169 is already below the spike's practical diagnostic threshold of 0.25, VideoToolbox hardware decode was **not** started.

---

## 4. Positive findings

1. **Real semantic retrieval works on real user media.**
   - The final run produced 5 strong and 2 useful hits with no misses on the seven fixed queries.

2. **The initial 7/7 failure was diagnosable and not evidence that SigLIP was unsuitable.**
   - The dominant semantic bug was a single incorrect text preprocessing seam.

3. **Max-length padding is load-bearing for the frozen SigLIP setup.**
   - 1/7 expected Top-1 became 7/7 on the controlled anchor diagnostic.

4. **Image embeddings were healthy.**
   - The collapse was query-side rather than image-side.

5. **Apple MPS is viable.**
   - Semantic equivalence with CPU passed.
   - Image throughput improved ~4.17x vs CPU serial.

6. **GPU inference is not the archive-scaling bottleneck at the current sample density.**
   - At 320,000 images, pure embedding was estimated from measured MPS throughput at roughly 1.1 h.

7. **Source-native temporal discipline survived optimization.**
   - The final sampler did not rely on seconds × nominal FPS and passed a VFR fixture.

8. **Full-frame PTS enumeration was unnecessary for this retrieval spike.**
   - Removing it reduced real wall time from ~313 s to ~44.8 s while retaining retrieval quality.

9. **The source remained immutable.**
   - Before/after SHA-256 matched.

10. **The experiment is remotely preserved.**
    - `experiment/single-video-semantic-spike-v1@0c14fce1fa979d466292fbd5cfd1e876bfacee92`.

---

## 5. Negative findings / failure modes / pitfalls

1. **Asset discovery can be wrong if it ignores external durable roots.**
   - The first preflight falsely concluded model/runtime were absent.

2. **The original text preprocessing silently destroyed retrieval quality.**
   - Basic “model loads and returns vectors” smoke tests were insufficient to detect semantic collapse.

3. **Raw similarity magnitude alone was misleading.**
   - Near-zero scores and overlapping Top-K lists were symptoms; controlled correspondence tests were needed to locate the failure.

4. **Whole-run timing can be misleading without stage decomposition.**
   - The first impression was “CPU inference is too slow”; measured breakdown showed ffprobe enumeration dominated instead.

5. **Per-sample ordinal extraction by re-decoding from frame zero does not scale.**
   - It exceeded the foreground timeout on a short real video.

6. **Full `ffprobe -show_frames` enumeration is extremely expensive for this source.**
   - 271.6 s for a 265.3 s video.

7. **CPU-only feasibility contracts should not be mistaken for hardware impossibility.**
   - The historical adapter intentionally rejected non-CPU operation, while MPS worked well in the experiment.

8. **Batch size is hardware/workload dependent.**
   - MPS batch 8 outperformed 16 and 32 in the bounded test.

9. **The final remaining bottleneck is software HEVC decode.**
   - Hardware decode may later help, but has not yet been tested and should not be assumed to improve the total path.

10. **One-video success is not a benchmark.**
    - Query set was designed around known visible scenes.
    - There was no held-out query set, no multi-video recall study, no false-positive corpus, and no archive-scale validation.

---

## 6. What was deliberately not done

The experiment did **not** perform:

- Gate-0 Stage-B completion;
- Gate-0 promotion;
- Gate-1 model/provider benchmark;
- Gate-2 reliability/scale qualification;
- Gate-3 real-media editing/QC;
- protected/archive-media execution beyond the explicitly authorized test video;
- cloud GPU use;
- provider inference;
- CUDA/NVIDIA testing;
- VideoToolbox hardware decode;
- model comparison;
- alternate sampling-density tuning;
- automatic refinement around coarse hits;
- query rewriting to improve results;
- threshold tuning;
- production hardening;
- persistent archive indexing;
- vector-database deployment;
- production UI/API/server/queue/scheduler.

---

## 7. Remote experiment preservation

The experimental implementation was pushed to:

`experiment/single-video-semantic-spike-v1`

Verified remote head:

`0c14fce1fa979d466292fbd5cfd1e876bfacee92`

The preserved experiment includes the spike runner, temporal sampler tests, text-padding regression test, and the one-line SigLIP padding correction on the experiment branch.

The Gate-0 controller remained at:

`controller/gate0/portfolio-v1@eaf11479279eb54480d36b926a0d16f0a3c77730`

during the spike work.

The successful spike is **not** evidence that the experimental branch should be merged wholesale into Gate-0. Promotion/retention of any part requires a separate owner-approved design decision.

---

## 8. Local result artifacts from the successive real runs

The following local output roots were reported:

1. Initial poor run:
   - `/Users/yusuf/Movies/kolaj-1-uzun-semantic-spike-results/run-batched`

2. Corrected padding + MPS run:
   - `/Users/yusuf/Movies/kolaj-1-uzun-semantic-spike-results/run-mps-corrected`

3. Final one-pass PTS + MPS run:
   - `/Users/yusuf/Movies/kolaj-1-uzun-semantic-spike-results/run-onepass-mps`

Typical artifacts include:

- `results.json`
- `report.md`
- `evaluation.json`
- `contact_sheet.html`
- sampled thumbnails

These local outputs were not automatically committed to Git and should not be assumed durable unless separately archived.

---

## 9. Persistent local semantic-index design brainstorm

After the spike was remotely preserved, a design-only brainstorming pass considered how to avoid re-decoding/re-embedding media for every future query.

### 9.1 Desired next capability

One-time indexing path:

`video archive -> source identity -> one-pass sampled frames -> measured PTS/timebase -> local SigLIP/MPS image embeddings -> persistent local index`

Later query path:

`query text -> local SigLIP text embedding -> search persisted vectors -> ranked source/PTS/thumbnail results`

Ordinary query-time behavior should require:

- no source-video decode;
- no image re-embedding.

### 9.2 Scale estimate at current sampling density

At ~one sample every 4.5 s:

- 400 h = ~320,000 samples
- 768-dimensional float32 embeddings
- raw contiguous matrix size ≈ 937 MiB

This suggests exact brute-force cosine search over a contiguous local matrix is plausibly adequate before introducing ANN/vector-database complexity.

The “tens of milliseconds” query-latency expectation is a design-time estimate, not yet measured.

### 9.3 Compared approaches

#### Approach A — contiguous local matrix + simple metadata

- contiguous float32 matrix, one row per sample;
- metadata manifest/table;
- source digest -> row ranges;
- memory-map compatible;
- brute-force cosine as one matrix-vector operation.

Advantages:

- simple;
- auditable;
- no new dependency;
- efficient scan path.

Disadvantages:

- append/rewrite/sharding needs care;
- metadata lifecycle needs a robust companion mechanism.

#### Approach B — SQLite-centric lifecycle

- SQLite for sources, samples, provenance, resume state;
- vectors either as BLOBs or companion matrix.

Advantages:

- transactional;
- crash-safe metadata lifecycle;
- straightforward resume/source-change state.

Disadvantages:

- vectors-as-BLOBs are not attractive for high-throughput brute-force scanning;
- embedding matrix is still preferable as a separate contiguous artifact.

#### Approach C — specialized ANN / FAISS-like index

Advantages:

- lower asymptotic query cost at very large N.

Disadvantages:

- new dependency and lifecycle;
- approximate recall becomes a new quality variable;
- unnecessary complexity at the currently estimated 320k-row scale unless measurement proves otherwise.

### 9.4 Recommended design direction

Hybrid of A + metadata-only B:

- `vectors.npy`: contiguous float32 `[N, 768]`, preferably L2-normalized;
- `index.sqlite`: source/sample provenance, lifecycle, resume state;
- `thumbs/<row>.jpg`: retained small thumbnails;
- `manifest.json`: generation/model/preprocessing/sampling/schema identity.

The vector matrix remains simple and scan-friendly; SQLite supplies transactional lifecycle semantics without turning vectors into row-by-row BLOB scans.

### 9.5 Proposed compatibility rule

Each index generation should pin at least:

- model identity;
- weights SHA-256;
- processor identity;
- preprocessing contract, including `padding="max_length"`;
- embedding dimension;
- dtype;
- sampling policy identity/version.

At query time, any mismatch between current query embedding identity and the generation manifest should fail closed rather than mix embedding spaces.

A model or preprocessing change should create a new generation rather than silently reusing old vectors.

### 9.6 Proposed source-change rule

- source SHA-256 is the source-content identity;
- unchanged digest -> skip source;
- changed digest -> re-index that source into a new range;
- path alone is not identity;
- old rows may be marked superseded rather than overwritten in place.

### 9.7 Resume/interruption rule

Design recommendation:

- per-source atomic indexing;
- prior COMPLETE sources survive interruption;
- IN_PROGRESS source is discarded/restarted;
- matrix append is block-oriented;
- torn tail blocks are ignored/rebuilt;
- source media is always read-only.

### 9.8 Thumbnail policy

Recommended:

- retain one small thumbnail per sample, roughly 128–160 px longest side, JPEG around q70;
- estimated 2–3 GB for ~320k samples, highly dependent on content/encoding;
- treat thumbnails as regenerable cache rather than evidence;
- rationale: visual query inspection without reopening source video.

The storage estimates are approximate design values, not measured archive outputs.

### 9.9 Query flow

Expected minimal future query flow:

1. load generation manifest;
2. fail-closed validate model/preprocessing identity;
3. load local SigLIP once;
4. embed text with `padding="max_length"`;
5. normalize query vector;
6. exact cosine/matrix-vector search;
7. Top-K join to source/PTS/timebase metadata;
8. return source identity, score, candidate PTS/timebase, readable timestamp, thumbnail.

Expected ordinary query-time video decode: `NO`  
Expected ordinary query-time image re-embed: `NO`

### 9.10 Ownership recommendation

Keep the persistent-index work initially as a **repository-level experimental vertical slice** rather than silently widening Gate-0 authority.

Gate-0 remains the diagnostic retrieval gate with its frozen evidence discipline. The persistent index adds storage/lifecycle/query-surface concerns that should earn their keep experimentally before any later promotion into a Gate contract.

---

## 10. Advantages and disadvantages of the current direction

### Advantages

- Proven real-video retrieval path exists.
- No provider/cloud dependency is required.
- Apple MPS is adequate for current embedding density.
- Exact semantic query quality improved dramatically with a minimal verified fix.
- PTS/timebase provenance can be preserved while removing expensive full-frame enumeration.
- Current single-machine indexing estimate is measured in days rather than weeks/months.
- A persistent index could make subsequent query latency dominated by vector search rather than media decode.
- The projected 320k-vector index is small enough to attempt simple exact search first.

### Disadvantages / risks

- Evidence is still based on one real video and seven intentionally interpretable queries.
- Current sample interval can miss short events between samples.
- Software HEVC decode remains the major indexing cost.
- 400 h time estimates assume roughly similar codec/resolution/workload and linear scaling.
- Archive heterogeneity may change decode cost substantially.
- A flat matrix must handle append/rebuild/generation semantics carefully.
- Thumbnail retention adds several GB at the estimated scale.
- Model/preprocessing upgrades invalidate vector-space compatibility and require generation management.
- Persistent index correctness/restart behavior has not yet been implemented or tested.
- No archive-scale recovery, corruption, or concurrent-writer behavior has been measured.

---

## 11. Important non-claims

This record does **not** establish:

- that SigLIP is the best representation for the archive;
- that 4.5 s is the best sampling interval;
- that 5 STRONG / 2 USEFUL generalizes to other videos;
- that 400 h will take exactly 64–68 h;
- that software decode is acceptable across all codecs/resolutions;
- that VideoToolbox would or would not improve future throughput;
- that a brute-force matrix search will meet a final latency SLA;
- that persistent indexing is already implemented;
- that semantic timestamps are edit-safe boundaries;
- that Gate 0, 1, 2, or 3 is promoted by this spike;
- that real/protected archive execution has been broadly authorized.

---

## 12. Recommended next experimental sequence

Subject to explicit owner approval and current repository authority:

1. Implement the smallest persistent local index as an isolated experimental vertical slice.
2. Index one small directory or a handful of ordinary test videos, not the protected archive.
3. Verify skip-if-unchanged, source-change detection, interruption/resume, generation compatibility, and exact query-time provenance.
4. Measure brute-force query latency before adding ANN/vector-database complexity.
5. Keep exact temporal refinement separate from semantic candidate retrieval.
6. Only if indexing throughput becomes operationally inadequate after broader measurement, evaluate VideoToolbox or additional parallel/local hardware.
7. Only if local hardware remains inadequate should NVIDIA/CUDA/cloud options be reconsidered.

---

## 13. Condensed evidence table

| Stage | Quality | Wall time / throughput | Main lesson |
|---|---|---|---|
| Initial real run | 0 STRONG / 0 USEFUL / 0 WEAK / 7 MISS | slow; earlier extraction even hit 600 s cap | Retrieval broken; do not assume model is bad |
| Seven-anchor diagnostic, unpadded | 1/7 corresponding Top-1 | small diagnostic | Text embeddings collapsed |
| Seven-anchor diagnostic, padded | 7/7 corresponding Top-1 | small diagnostic | `padding="max_length"` is load-bearing |
| CPU serial image embedding | semantics healthy after fix | 19.12 img/s | CPU works but is slower |
| CPU batched | semantics healthy | 24.39 img/s | batching helps modestly |
| MPS batched bs=8 | semantic equivalence PASS | 79.73 img/s | Apple GPU is useful and sufficient for current embedding load |
| Corrected full run before PTS optimization | 5 STRONG / 2 USEFUL / 0 MISS | 313 s, RTF 1.18 | ffprobe enumeration, not AI, dominates |
| Final one-pass PTS + MPS run | 5 STRONG / 2 USEFUL / 0 MISS | 44.839 s, RTF 0.169 | full-frame enumeration removed; decode now dominates |
| 400 h diagnostic extrapolation | not a quality claim | ~67.6 h, ~64.7 h excl. cold load | order-of-magnitude single-Mac planning estimate only |
| Persistent-index design | not implemented | ~320k rows, ~937 MiB vectors | exact local search likely worth trying before ANN |

---

## 14. Durable references

- Experiment branch: `experiment/single-video-semantic-spike-v1`
- Experiment head: `0c14fce1fa979d466292fbd5cfd1e876bfacee92`
- Gate-0 controller remained separate: `controller/gate0/portfolio-v1@eaf11479279eb54480d36b926a0d16f0a3c77730`
- This document is a historical/experimental evidence record on canonical `main`; it is not an execution authorization or Gate promotion record.
