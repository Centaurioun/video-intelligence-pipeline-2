# Gate-3 Dual Temporal Authority Composition — Design

- **Date:** 2026-10-25
- **Instance:** `VIP-G3-DUAL-TEMPORAL-AUTHORITY` / `VIP-20261025-G3-WAVE2-TIMELINE-DESIGN`
- **Status:** `DESIGNED_PENDING_APPROVAL` — **no implementation authority is granted by this document.**
- **Base:** `4144733cc3de04e928bff0c862693474a0a04c11` (verified `origin/main`, matches mission checkpoint)
- **Branch:** `design/g3-dual-temporal-authority-20261025`
- **Gap:** G-3 (`docs/agent-runs/2026-10-25-four-gate-first-wave/gate3-pilot-input-spec.md:305`)
- **Supersedes:** nothing. **Extends / partially renegotiates:** `docs/superpowers/specs/2026-09-25-root-g-real-source-temporal-revision-closure-design.md` (Status: APPROVED, `IMPLEMENTATION_AUTHORIZED=false`) — see the Root-G deltas D-1..D-4 and approval items A-1..A-12, both in §17.
- **Sibling decisions in this run:** `docs/agent-runs/2026-10-25-g3-dual-temporal-authority/03-corpus-separation-decision.md` (Lane B), `.../04-stream-tail-and-audio-policy.md` (Lane C), `.../02-temporal-measurements.md` (synthetic evidence).

---

## 1. Problem statement (what G-3 actually is)

**Evidence scope.** Every claim in this document is one of three kinds, and the kind is stated at each use: (a) *code-verified* — read at the cited `path:line` on base `4144733cc`; (b) *measured* — reproduced with the locally installed `ffmpeg`/`ffprobe` 9.0.2 and Python 3.14.9, no network, no provider, no archive (§14); (c) *NOT_OBSERVED* — stated as such. No claim is a projection of another document's intent.

G-3 is **not** "nobody wrote the call". It is a **composition gap across four divergent measured-temporal routes**, each of which measures a *different projection* of the same source bytes, and only two of which are cross-checked against each other — on two facts out of ~ten.

### 1.1 The four measured temporal routes

| Route | Site | What it measures | What consumes it |
|---|---|---|---|
| **R1** probe-frame presentation PTS | `src/vip_fvs/real_source_service.py:301` `_frame_presentation_pts`, used by `:364` `_source_pts_interval` | `ffprobe -show_frames` `best_effort_timestamp` → `pts` → `pkt_pts`, presentation order, duplicates preserved | **endpoint authority** for the editorial edit interval (Root G §3.2) |
| **R2** re-probe + probe-artifact JSON | `src/vip_fvs/real_preview_verifier.py:111` `_evidence_facts`, `:135-152` `_probe_source`, verifier `:350-395` | re-reads the sealed probe artifact **and** re-runs ffprobe; `tuple(sorted(set(values)))` — **multiplicity collapsed** | preview verification only |
| **R3** ISO-BMFF byte measurement (named path) | `src/gate3/container.py:202` `parse_iso_bmff_timing` called from `src/vip_fvs/refinement_adapter.py:182`, and again inside `src/gate3/refinement.py:66-68` `_resolve_byte_authority` and `:353-355` `_byte_authority_covers` | `mdhd` timescale, `stts` decode deltas, `ctts` composition offsets, `elst` origin (reported, **not applied**), `duration_ts`, `tail_duration_ticks`, `nb_frames`, `duration_consistency` | Gate-3 binding eligibility + T7 VFR classification |
| **R4** snapshot-bound verified temporal authority | `src/vip_fvs/source_snapshot.py:547` `SourceSnapshotStore.bind_temporal_authority` (`parse_iso_bmff_timing_bytes` at `:574` over the **retained snapshot bytes**, bounds-validated at `:571`, declaration-checked at `:602-605`) | same ISO-BMFF facts, but reduced to: `pts_ticks`, `dts_ticks`, `timebase=(1,mdhd.timescale)`, `stream_count`, `declared_vfr`, `declared_reordering` | **no product caller** (only `verify_temporal_authority` `:642` and tests) |

### 1.2 The exact missing composition path

`prepare_real_source` already proves **identity** composition between R1 and R3/R4:

- the probe is run **against the retained snapshot path**, not the original (`real_source_service.py:485-486`), and
- `SOURCE_PROBE_SNAPSHOT_BINDING_MISMATCH` (`:496-500`) enforces `probe.source_path == snapshot.snapshot_path`, `probe.source_sha256 == snapshot.sha256`, `probe.source_byte_count == snapshot.byte_count`, and `probe.snapshot_evidence == snapshot.as_evidence()`, and source re-hash before/after (`assert_source_unchanged`, `:502`).

What is **not** composed is the **measurement**:

1. R1's endpoint interval (`_source_pts_interval`) is compared to the refinement record only at the two boundary ticks (`AUTHORITATIVE_REFINEMENT_INTERVAL_MISMATCH`) and the timebase tuple (`AUTHORITATIVE_REFINEMENT_TIMEBASE_MISMATCH`). The **full presentation enumeration** of R1 is never compared to R3's `pts_ticks`.
2. R4 is never instantiated in any product path, so the **snapshot-bound** projection — the only one that is single-read, bounds-validated, digest-bound, manifest-bound, and declaration-checked — never participates in the published authority.
3. R2 collapses duplicate presentation ticks (`sorted(set(...))`), so the preview verification route cannot detect a duplicate-tick source that R1/R4 preserve. Root G §3.2(7) required multiplicity preservation at the *projection*; R2 violates the same invariant at the *verification* boundary.
4. There is no single artifact that a pilot can cite as "the probe-derived cut and the snapshot-derived cut agree for this revision".

**Consequence for the pilot:** the claim in `gate3-pilot-input-spec.md:305` remains true after this design's base commit: *the pilot cannot yet prove that the probe-derived cut and the snapshot-derived cut agree for the same revision.*

### 1.3 Divergences found while verifying interfaces (static, from source)

These are the substantive reasons a naive "call both and compare" would be wrong.

| # | Divergence | Evidence |
|---|---|---|
| **Dv-1** | **Edit-list admissibility disagrees between routes.** R3 refuses a source whose `elst` media_time ≠ 0 at binding time (`EDIT_LIST_ORIGIN_NOT_APPLIED`). R4 **accepts** it and silently drops the origin from the evidence body. | `src/gate3/refinement.py` `_resolve_byte_authority`: `presentation_origin_ticks` non-None and != 0 → blocked `EDIT_LIST_ORIGIN_NOT_APPLIED`; `src/vip_fvs/source_snapshot.py:608-620` evidence body has **no** `presentation_origin_ticks` field; `container.py` computes `origin` and only reports it |
| **Dv-2** | **VFR declaration basis disagrees.** R4 derives `observed_vfr` from **DTS** deltas + tail (`source_snapshot.py:600`: `durations = tuple(b - a for a,b in zip(dts,dts[1:])) + (tail,)`; `observed_vfr = len(set(durations)) > 1`). R3's T7/`classify_vfr` derives VFR from the **presentation** table (`gate3/temporal.py` `classify_vfr(table)`), i.e. R3 and R4 can validate a `declared_vfr=True` claim against different bases. | `source_snapshot.py:600-601`; `gate3/temporal.py:39-70` |
| **Dv-3** | **Reordering detection is coarse.** R4 uses `observed_reordering = pts != dts` where `pts` is the **sorted** composition tuple and `dts` is decode order; `container.py` uses the same comparison for `has_b_frames`. Sorted-vs-decode comparison is sufficient to *detect* reordering but destroys the decode↔presentation association needed to prove "this presentation tick is carried by this decode sample", so it can neither confirm nor refute an `elst` interpretation. | `source_snapshot.py:601`; `container.py` `reordered = tuple(pts) != tuple(dts)` |
| **Dv-4** | **R4 drops the tail facts it just validated.** `duration_ts`, `nb_frames`, `duration_consistency`, `tail_duration_ticks`, `presentation_origin_ticks`, `composition_offsets`, `has_b_frames`, `stream_handler`, `derivation` are all read/validated at `:587-594` and then omitted from the evidence body (`:608-620`) and the binding dataclass. This is the direct cause of G-4's `MISSING_PLUMBING` verdict (Lane C). | as cited |
| **Dv-5** | **Stream identity derivation is not carried.** `stream_count` survives; `stream_handler`, `stream_identity_derivation` (`SOLE_VIDEO_DERIVATION` vs explicit selector) do not. A binding therefore cannot prove *which* video track was selected when `stream_count > 1`. | `container.py` `_select_stream`; `source_snapshot.py:608-620` |
| **Dv-6** | **A third producer of a Gate-3 measurement exists outside the refinement path**: the fake CLI seam measures a freshly generated MP4 with `parse_iso_bmff_timing` at `src/vip_fvs/coordinator.py:350-351`. Any composed-authority contract must state whether it is in scope (see §13: out of V1 scope). | `coordinator.py:350-351` |
| **Dv-7** | **`elst` is never applied anywhere.** `parse_iso_bmff_timing_bytes` computes `dts` from `stts` and `pts = dts + ctts_offset`; the `elst` media_time is reported as `presentation_origin_ticks` and never shifts any tick. `ffprobe`'s `best_effort_timestamp` for an `elst`-bearing MOV/MP4 is produced by libavformat's edit-list handling, so R1 and R3/R4 are measuring **different timelines** for such sources. Whether they differ by exactly `media_time` is an empirical question answered in §14. | `container.py:155-201`; §14 |

| **Dv-8** | **`duration_consistency` is computed without the `elst` origin**, so it reports `MISMATCH` on exactly the sources where ffmpeg compensated a positive composition shift with an `elst` media_time — i.e. ordinary B-frame H.264 MP4s from ffmpeg defaults. The correct identity is `duration_ts == max(pts) + tail_duration_ticks − presentation_origin_ticks`; measured on 11/11 ISO-BMFF synthetic cases (§14): `MISMATCH` occurs iff `origin != 0`, and the origin-corrected identity holds in every case. Because `duration_consistency == "MATCH"` gates the tail path (`gate3/temporal.py:39-46`, `gate3/refinement.py` tail facts), this makes G-4's terminal interval unreachable for those sources even after edit-list handling. | `container.py:155-201` (`computed=presentation[-1]+tail`); §14 |
| **Dv-9** | **The "source-native presentation PTS" R1 route cannot read the JSON emitted by the installed `ffprobe`.** `probe_real_source` requests `-show_frames` **and** `-show_packets` in one invocation (`src/vip_fvs/real_source_probe.py` argv). `ffprobe 9.0.2` then emits a single merged `packets_and_frames` array (entries discriminated by `"type": "frame" \| "packet"`), and **no** `frames` / `packets` keys. `_frame_presentation_pts` reads `payload["frames"]` ⇒ **0 presentation ticks**; `_observed_pts` ⇒ **0 ticks**; `real_preview_verifier._evidence_facts` reads the same keys and therefore raises `SOURCE_PTS_EVIDENCE_INVALID` (it does not silently return 0); two further readers of `payload["frames"]` are affected outside the endpoints path — `local_preview.py:872-889` and `cli.py:167-199`, the latter failing as `FIXTURE_SOURCE_PROBE_FAILED` — so IT-0's write scope must include them. Measured on all 10 synthetic inputs (merged payload, `has_frames_key=False`, `has_packets_key=False`), and the legacy split payload (synthesised from the same merged entries) yields the full 60/45/40 ticks. Nothing in the repo pins a `ffprobe` version: CI installs no ffmpeg and the suite uses fake runners only. | `real_source_service.py:252,301`; `real_preview_verifier.py:111`; §14 |
| **Dv-10** | **The preview verifier's three evidence-provenance checks are inert for real probe payloads.** It tests `evidence.get("source_bytes_sha256")`, `.get("stream_index")`, `.get("media_timescale")` (`real_preview_verifier.py`, the three `if ... : raise` guards after `_evidence_facts`), but the canonical probe payload is `{streams, format, frames/packets}` (`real_source_probe.py:198-206` writes `json.dumps(payload)` verbatim) and contains none of those keys, so every guard short-circuits to "skip". Combined with `_evidence_facts`'s `sorted(set(...))` collapse this makes the verifier's byte/stream/timebase corroboration **vacuous in production while passing in tests** (tests feed payloads that do carry the keys). | `real_preview_verifier.py:361-372`; `real_source_probe.py:198-206` |
| **Dv-11** | **The two verification surfaces disagree about what they admit.** `local_preview.py:874-889` and `real_preview_verifier.py:112-129` both collapse to `tuple(sorted(set(...)))` over frame **and** packet aliases (spec-forbidden), yet their stream-row admission rules differ (preview skips a silent row; verifier raises), so evidence admitted at render time can be refused at verify time. | as cited; lane-refine map §6 |
| **Dv-12** | **Gate-3 authority is a seal-time fact.** `is_binding_eligible` is re-checked at plan build (`real_plan.py:269-270`), but plan load, preview and the verifier never re-run `_byte_authority_covers`/`_resolve_byte_authority` and never re-measure the named bytes; the sealed decode-order and composition evidence (`refinement.py:577-593`) is only partly consumed downstream: `dts_ticks` *are* re-compared against re-measured facts inside `is_binding_eligible` at plan build (`refinement.py:446`), while `composition_offsets` and the `ctts`/`elst` provenance are consumed by nothing. A composed authority must therefore be **re-verifiable at consumption**, or it inherits the same decay. | lane-refine map §5 |
| **Dv-13** | **Silent endpoint reinterpretation inside `refine()`.** A requested end that is not a boundary member is reinterpreted as `end_is_stream_tail` (`refinement.py:532`) and then validated against `mdhd duration_ts` — a different claim. Composition must never hand `refine()` a non-member end, or the tail reinterpretation fires silently instead of the intended `TEMPORAL_AUTHORITY_ENDPOINT_NOT_IN_COMPOSED_ENUMERATION`. | `refinement.py:532`; §8.8 |

**Net statement of G-3 (exact):** the product composes *source identity* between the probe and the snapshot, and composes *two ticks and one timebase* between the probe and the refinement; it never composes *presentation enumeration, decode order, edit-list interpretation, declaration basis, stream-identity derivation, or tail facts* between the probe path and the verified snapshot authority. That missing composition is G-3.

**Blocking prerequisite (Dv-9):** until the R1 extractor understands the merged `packets_and_frames` layout, R1 measures nothing on a current `ffprobe`, so *no* composition can be observed end-to-end and every real preparation fails closed at `SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED`. Dv-9 is therefore IT-0 in §15 and item A-10 in §17 — it is the first thing to fix, and it is a fail-closed capability defect rather than a data-integrity defect.

---

## 2. Requirements and invariants

R-1..R-10 are binding on any accepted design.

- **R-1 Exact arithmetic only.** All comparisons are on Python `int` ticks and `(num, den)` integer pairs. No `float`, no `math.isclose`, no nominal FPS, no seconds.
- **R-2 No silent normalization.** Every accepted equality is one of the enumerated rules in §7. Any other difference is an attributable refusal.
- **R-3 No order coercion.** `ffprobe` frame-list order is presentation order and **must never** be treated as decode order (`dts`). ISO-BMFF `dts_ticks` is the sole decode-order evidence.
- **R-4 Multiplicity is evidence.** Duplicate presentation ticks must be preserved on every route that carries an enumeration (R1, R3, R4) and must not be collapsed (fixes Dv-2/R2).
- **R-5 Fail closed with attribution.** Disagreement is a stable refusal code with the disagreeing fact named; never a warning, never a downgrade to "unverified but proceed".
- **R-6 Identity precedes measurement.** Composition refuses unless source revision, content digest, byte count, snapshot manifest digest and selected stream identity are exactly equal. Existing `SOURCE_PROBE_SNAPSHOT_BINDING_MISMATCH` semantics are preserved and are not weakened.
- **R-7 Snapshot guarantees unchanged.** Single read, `O_NOFOLLOW`, `0o700`/`0o400`, retention bounds, digest-bound manifest: unchanged. The composition may read snapshot bytes only through `SourceSnapshotStore`.
- **R-8 Bounded resources.** Composition adds at most one additional pass over an already-retained snapshot (bounded by `max_source_bytes`) and no additional `ffprobe` process. No second full-source parse outside the snapshot store.
- **R-9 No evidence upgrade.** A composed binding asserts only what was measured. `extent_state`, `NOT_OBSERVED`, and `UNCERTAIN` remain exactly as the underlying routes report them.
- **R-10 Additive compatibility.** Existing refinement records, plan receipts, preview receipts and QC outputs keep their schemas; composition is a new, separately-versioned evidence object plus optional additive fields.

---

## 3. Candidate architectures

### A. Mutual independent checkers (two full measurements, bidirectional)

Both routes fully enumerate and each cross-validates the other; either may veto; no fact ownership.

**Evaluation.** Strongest theoretical checking, but it has no answer to Dv-1/Dv-2/Dv-7: the routes measure different projections, so "equality" is only meaningful after declaring ownership and normalization. Without an ownership map it produces false mismatches on every `ctts`/`elst`/VFR source, and the only ways to make it pass are (a) normalize by declaring facts, which is option B, or (b) weaken to interval-only, which is today. It also doubles parser cost and lets two parsers disagree about *admissibility* with no tiebreak. **Rejected as a standalone architecture; retained as the comparison procedure inside C.**

### B. Per-fact single authority + corroboration

Declare, for each measured fact, exactly one owning measurement; the other route must corroborate where it is capable of doing so, and its inability to corroborate is recorded as `NOT_APPLICABLE`, not as agreement.

**Evaluation.** This is the only architecture that survives Dv-1..Dv-7, because disagreement is defined per fact instead of globally. It is also the honest one: R1 genuinely cannot measure decode order or `tail_duration_ticks`. Risk: an ownership table that is wrong in one row silently legitimizes a bad fact, and "NOT_APPLICABLE" can become a loophole if it is allowed to cover facts that *are* measurable. **Accepted as the fact-ownership layer of the recommendation.**

### C. Narrow composed authority object behind the existing refinement interface

Introduce one object — `ComposedSourceTemporalAuthority` — that is produced from an already-captured `VerifiedSourceSnapshot` **and** an already-sealed `RealSourceProbeBinding`, holds both projections, the per-fact ownership map, the comparison results and the evidence digest, and is passed *into* the existing refinement call and *cited by* the plan/preview receipts. It replaces neither `SourceSnapshotStore` nor `RealSourceProbeBinding` nor `parse_iso_bmff_timing`; it composes them.

**Evaluation.** Satisfies R-10 by construction (nothing existing changes shape except additive fields), satisfies R-6/R-7 (identity is already proven before composition; snapshot bytes are re-read only through the store), satisfies R-8 (no new process), and yields exactly the artifact the pilot needs (§1.2 item 4). Its risks: (i) an extra object to thread through `prepare_real_source` → refinement adapter → receipt; (ii) if the composition is *optional*, it degrades to decoration; (iii) it must not become a third independent parser.

### C′. C with mandatory composition for exact claims (recommended)

C, with three hard additions:

1. **Composition is mandatory for `plan_scope="REAL"`** exact-interval claims. Absence of a composed authority is `TEMPORAL_AUTHORITY_REQUIRED`, a refusal at the same place `AUTHORITATIVE_REFINEMENT_*` refusals live. There is no "unverified but proceed" mode.
2. **The refinement call receives the composed authority**, not a bare `PtsTable`: the adapter sources its enumeration from the composed authority's owned projection (which is R3, unchanged) while *requiring* the composed authority's corroboration results to be `COMPOSED` for the facts R3 owns.
3. **Semantics of `bind_temporal_authority` are corrected for the two divergences it owns** (Dv-2 VFR basis, Dv-4 dropped tail facts, Dv-5 dropped stream identity) — as a versioned successor evidence shape, not an in-place mutation (`schema_version: 1 → 2`), so persisted v1 evidence remains verifiable.

**Why C′ and not A or B alone:** A cannot resolve Dv-1/Dv-7 without an ownership table; B cannot produce a single citable artifact and can be satisfied by a comparison that is never recorded; C alone can be bypassed. C′ is B's ownership discipline inside C's object, with A's bidirectional comparison as the procedure and a fail-closed mandatory gate.

---

## 4. Requirement satisfaction matrix (C′)

| Criterion (mission) | C′ answer |
|---|---|
| CFR correctness | presentation enumeration equality + exact timebase; no FPS anywhere |
| VFR correctness | VFR declared on the **presentation** basis only (Dv-2 corrected); per-frame deltas preserved |
| B-frame presentation vs decode | decode order owned solely by R3/R4 `dts_ticks`; R1 order never used as decode order (R-3); `has_b_frames`/`composition_offsets` carried (Dv-4) |
| Edit-list offsets | v1: any nonzero `elst` media_time is a refusal on *both* routes (closes Dv-1); v2 (future, §13) may admit a single-segment `elst` only with an explicitly applied and recorded origin |
| Timebase conversion | none. Composition requires exact equality of the integer pair; locator rational cross-multiplication (Root G §3.1) is untouched |
| Stream-selection ambiguity | `selected_stream_index` + `stream_count` + `stream_handler` + `stream_identity_derivation` all carried; multi-video without explicit selector refuses (existing `_select_stream` behaviour, now provable from the binding) |
| Missing / conflicting identities | existing `SOURCE_PROBE_SNAPSHOT_BINDING_MISMATCH` retained; composed authority re-verifies digest before publication |
| Unsupported containers | `TEMPORAL_AUTHORITY_NOT_OBSERVED` (§9); no container-agnostic fallback for exact claims |
| Failure semantics | single `ComposedTemporalAuthorityRefusal` with stable code + failing fact + both measured values |
| Memory / I/O | one bounded re-read of retained snapshot bytes; no new subprocess |
| Preview / plan receipt compatibility | additive `composed_temporal_authority` block + digest; schemas versioned |

---

## 5. Inputs and verified source identity

Composition inputs (all already available at `real_source_service.py:485-500`):

1. `VerifiedSourceSnapshot` — `snapshot_path`, `sha256`, `byte_count`, `manifest_sha256`, `source_revision_id`, `source_locator`, `authorization_id`.
2. `RealSourceProbeBinding` — `ffprobe_json` (streams/format/frames/packets), `probe_digest`, `probe_artifact_ref`, `raw_probe_artifact_ref`, `canonical_probe_artifact_ref`, `selected_stream_index`, `timebase_num`, `timebase_den`, `policy_identity`, `snapshot_evidence`.
3. Declarations: `declared_vfr: bool`, `declared_reordering: bool` — **supplied by the caller**, never inferred, matching the existing `bind_temporal_authority` contract.
4. Optional `container_path` (the retained snapshot path) for R3.

Identity equality required before any measurement comparison (exact types, no coercion): `source_sha256`, `source_byte_count`, `source_revision_id`, `snapshot_manifest_sha256`, `selected_stream_index`, `timebase=(num,den)` vs `(1, media_timescale)`.

**Verified identity is the existing `SOURCE_PROBE_SNAPSHOT_BINDING_MISMATCH` check plus R4's own `self.verify(snapshot)` before and after measurement. Composition does not re-implement it; it re-asserts it and refuses `TEMPORAL_AUTHORITY_IDENTITY_MISMATCH` if it ever fails.**

---

## 6. Selected video-stream binding

- The selector is `selected_stream_index` on the request; `None` means "sole video track" and is resolved **only** by `container.py::_select_stream` from the ISO-BMFF `trak` list.
- When the container has ≥2 timing-bearing `vide` traks and no explicit selector: refuse (`TEMPORAL_AUTHORITY_STREAM_AMBIGUOUS`), preserving `container.py`'s existing message contract.
- When `ffprobe` reports the selected stream index: it must equal the container-resolved index. `ffprobe` stream indices include non-video streams, so equality is on the *ffprobe stream index of a `codec_type=="video"` stream*, and the container index is the *N-th timing-bearing `trak`*. These coincide for the current synthetic corpus but are **not logically the same namespace**; the design therefore requires the composed authority to record both derivations (`stream_identity_derivation` from R4, `ffprobe_stream_index` from R1) and refuses `TEMPORAL_AUTHORITY_STREAM_IDENTITY_DIVERGENCE` when a mapping cannot be established. *(This is the one open sub-question in the design — see §15 OQ-1.)*

---

## 7. Fact ownership (the load-bearing table)

`OWNER` = the only route whose value may be published for this fact. `CHECK` = must be present and equal. `CORROBORATE` = compared when the route can express it, otherwise recorded `NOT_APPLICABLE`. `—` = not carried.

| Fact | Owner | Check / Corroborate | Notes |
|---|---|---|---|
| source revision, digest, byte count, manifest digest | snapshot | both | R-6 |
| selected stream index / count | R3/R4 | R1 (`ffprobe` video index) | Dv-5; OQ-1 |
| stream handler + identity derivation | R3/R4 | — | new carried field |
| `mdhd` timescale | R3/R4 | R1 (`timebase_num/den`) exact pair | Root G §3.4 unchanged in effect |
| decompressed sample count `nb_frames` | R3/R4 | R2 (`len(frames)`) | additive |
| **decode timestamps `dts_ticks`** | R3/R4 (`stts`) | — | **R1 has no decode-order evidence; R-3** |
| **presentation timestamps `pts_ticks`** | R3/R4 (`stts+ctts`, sorted) | **R1 full multiset** | the G-3 comparison proper |
| presentation ticks **as an ordered sequence** | R1 (probe frame order) | — | must be non-decreasing; a decrease is `TEMPORAL_AUTHORITY_PRESENTATION_ORDER_INVALID` |
| `ctts` composition offsets | R3/R4 | — | carried (Dv-4) |
| `has_b_frames` | R3/R4 | — | derived; carried |
| `elst` media_time / `presentation_origin_ticks` | R3/R4 | — | **v1: must be 0, else refuse on both routes** |
| `duration_ts` | R3/R4 (`mdhd`) | R1 (`format.duration` × timescale, exact rational) | corroboration only; owner is the byte measurement |
| `tail_duration_ticks` (last `stts` delta) | R3/R4 | — | terminal-interval basis (G-4) |
| `duration_consistency` | R3/R4 | — | `MATCH` required for any terminal interval |
| `declared_vfr` ↔ observed VFR | R3/R4 on **presentation** basis | R1 (presentation deltas) | **Dv-2 correction: not DTS-based.** Note the two existing predicates also differ in form: Gate-3 `classify_vfr` (`temporal.py:22-31`) tests a within-one-tick deviation from the mean span, whereas the snapshot binding uses `len(set(durations)) > 1`; §8.6 fixes one basis and one predicate |
| `declared_reordering` ↔ observed reordering | R3/R4 | R1 (order strictly increasing + duplicates ⇒ reordering impossible) | |
| frame-presentation interval endpoints | **R1** (Root G §3.2, unchanged) | R3 boundary membership; R4 membership | endpoint authority is not moved |
| terminal-frame extent | R3/R4 | — | `DERIVED_NOT_OBSERVED`, never `OBSERVED` |

**Asymmetry that makes this safe:** every fact R1 owns (endpoints, ordered presentation sequence) is one that R3/R4 can also express and therefore check; every fact only R3/R4 can express (decode order, sample counts, tail, `ctts`, `elst`) is *not* claimed by R1 at all. No fact is owned by a route that cannot express it.

---

## 8. Comparison procedure

Composition returns one of three states per fact: `AGREES`, `NOT_APPLICABLE` (route cannot express it — recorded with reason), or a refusal.

### 8.1 Identity stage (exact)
`source_sha256`, `source_byte_count`, `source_revision_id`, `snapshot_manifest_sha256`, `selected_stream_index` → else `TEMPORAL_AUTHORITY_IDENTITY_MISMATCH`.

### 8.2 Timebase stage (exact pair)
`(probe.timebase_num, probe.timebase_den) == (1, media_timescale)` → else `TEMPORAL_AUTHORITY_TIMEBASE_MISMATCH`. **No rational cross-multiplication here**: Root G §3.1's cross-multiplication applies to the *locator*, and §3.4 requires tuple equality for the measured refinement. Composition keeps tuple equality and additionally requires reduced `1/den` form, refusing `TEMPORAL_AUTHORITY_TIMEBASE_NOT_REDUCED` if `num != 1`.

### 8.3 Presentation enumeration stage (the G-3 comparison)
Let `A = _frame_presentation_pts(probe)` (ordered, duplicates preserved) and `B = binding.pts_ticks` (sorted presentation tuple from `stts+ctts`).

1. If `len(A) != len(B)` → `TEMPORAL_AUTHORITY_ENUMERATION_LENGTH_MISMATCH`.
2. If `tuple(sorted(A)) != tuple(B)` → `TEMPORAL_AUTHORITY_ENUMERATION_MISMATCH` (report first differing index and both tick values).
3. If `list(A) != sorted(A)` → `TEMPORAL_AUTHORITY_PRESENTATION_ORDER_INVALID` (ffprobe frame order must be non-decreasing presentation order; a decrease means the alias selection is not presentation order).
4. Duplicate ticks in `A` are counted and required to equal the duplicate count in `B` → `TEMPORAL_AUTHORITY_MULTIPLICITY_MISMATCH`.

No normalization is applied in this stage. In particular there is **no** "subtract the origin" rule: an `elst`-bearing source is refused at §8.4 before this comparison can be reached.

### 8.4 Edit-list stage

`elst` is the one fact where the two routes provably measure different timelines (§14): `ffprobe` applies the edit list, `container.py` does not.

**V1 (this design's approval unit): require `presentation_origin_ticks == 0`.**
If `presentation_origin_ticks` is not `0` (or `media_time_offset != 0`) → `TEMPORAL_AUTHORITY_EDIT_LIST_ORIGIN_NOT_APPLIED`, on **both** routes (R3 already refuses at `_resolve_byte_authority`; R4 gains the same refusal, closing Dv-1). Rationale for v1: admitting an edit list requires changing the Gate-3 `PtsTable` projection (the decode↔presentation association is destroyed by `presentation = sorted(pts)`) and the `gate3/refinement.py` origin contract — i.e. a *second* approved-architecture delta that should not ride along with G-3's first approval unit.

**V2 (measured, designed, not authorized here): the exact edit-list projection rule.**

Measured rule **E** on 11/11 ISO-BMFF synthetic cases (single-segment `elst`, `media_time = m ≥ 0`):

- `presented enumeration` `A = [t − m for t in B if t − m >= 0]` — i.e. shift by the origin and **drop** leading samples that would be negative (no clamping, no interpolation);
- `presented duration = duration_ts − m`;
- `duration_ts == max(B) + tail_duration_ticks − m`, equivalently `presented_duration == max(A) + tail_duration_ticks`.

Measured evidence (§14): case 3 / 4 / 6b (`m = 1024`, nothing dropped, `A = B − 1024` exactly), case 8a (`m = 67`, `A = B − 67`), case 5b (`m = 7680`, 15 of 60 samples dropped, `A = (B − 7680)[15:]` exactly), case 5c / 5a / 1 / 2 / 6a / 7 (`m = 0`, `A = B`). In all four nonzero-origin cases the origin-corrected identity `duration_ts == max(B) + tail − m` holds, which is precisely why Dv-8's uncorrected identity reports `MATCH` for `m = 0` and `MISMATCH` otherwise.

**Safety argument for admitting rule E (why it is fail-closed, not an invented tolerance):** rule E is used only to *predict* `A` from `B`; the prediction is then compared to the measured `A` by exact multiset equality (§8.3). If a file from a different muxer follows a different edit-list convention, the prediction differs, the comparison fails, and composition refuses. A wrong hypothesis can therefore only cause a refusal, never a false `MEASURED`. This is why E is admissible in principle — but it still requires: per-sample decode↔presentation pairs in `container.py` (currently discarded by sorting), the origin-corrected `duration_consistency` (Dv-8), an explicit `elst_applied` record (`media_time`, `dropped_leading_samples`, `segment_count`), and a `gate3/refinement.py` origin-contract change. Hence V2 is a separate approval, item **A-9**.

**Refusals retained in both V1 and V2:** `elst` with >1 segment, negative `media_time`, or an empty edit (segment with `media_time == -1`) — `container.py::_parse_elst` already refuses the first two; the third is `TEMPORAL_AUTHORITY_NOT_OBSERVED`.

### 8.5 Decode / reordering stage
`dts_ticks` strictly increasing (R4 already enforces `SNAPSHOT_DECODE_TIMESTAMPS_INVALID`); `observed_reordering = (sorted(pts) != dts)` must equal `declared_reordering`, else `TEMPORAL_AUTHORITY_REORDERING_DECLARATION_MISMATCH`. R1 cannot express decode order → `NOT_APPLICABLE` recorded. **R1's frame order is never used as `dts`.**

### 8.6 VFR stage (corrected basis)
`observed_vfr` is computed from **presentation** deltas: `deltas = [b-a for a,b in zip(pts, pts[1:])]`; `observed_vfr = len(set(deltas)) > 1`. `duration_ts` and `tail_duration_ticks` are *not* folded into the VFR basis (they are tail facts, §8.7). Declaration mismatch → `TEMPORAL_AUTHORITY_VFR_DECLARATION_MISMATCH`. R1 corroboration: compute the same predicate from `A`; if it differs → `TEMPORAL_AUTHORITY_VFR_BASIS_DIVERGENCE`. This is a **behaviour change** to `bind_temporal_authority` (Dv-2) and is the highest-risk item in the design (Dv-2; approval item A-2 in §17).

### 8.7 Tail stage (G-4 enabler)
Carry `duration_ts`, `nb_frames`, `duration_consistency`, `tail_duration_ticks`. Terminal interval is admissible iff `nb_frames == len(pts)`, `duration_consistency == "MATCH"`, `duration_ts > pts[-1]`, and the requested end equals `duration_ts`; `extent_state = "DERIVED_NOT_OBSERVED"`. Any other state → `TEMPORAL_AUTHORITY_TAIL_NOT_MEASURED` (never synthesize a following tick, never use nominal FPS — `gate3/temporal.py:39-46` already implements this; the design only requires the facts to survive the binding).

### 8.8 Endpoint stage (unchanged authority)
R1's `_source_pts_interval` result must be a member pair of `B` (`start ∈ B`, `end == least member of B strictly greater than start`), else `TEMPORAL_AUTHORITY_ENDPOINT_NOT_IN_COMPOSED_ENUMERATION`. Existing `SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED` / `SOURCE_PTS_INTERVAL_NOT_OBSERVED` refusals remain first.

---

## 9. Accepted equality / normalization rules (exhaustive for v1)

Only these are accepted; nothing else may be silently reconciled.

1. **Exact integer equality** of ticks, digests, byte counts, stream indices.
2. **Exact integer pair equality** of `(num, den)` timebase, with `num == 1` required.
3. **Sorted-multiset equality** of the presentation enumeration (`sorted(A) == B`), with multiplicity preserved and equality of duplicate counts.
4. **Ordered-sequence monotonicity** of the probe presentation sequence (non-decreasing) — a *validity* condition, not a normalization.
5. That is all. There is **no** clock-offset normalization, **no** origin subtraction, **no** frame-rate arithmetic, **no** rounding, **no** tolerance, **no** `set()` collapse, **no** resampling, **no** "close enough" case.

Under V2 only, one further rule may be admitted — the measured edit-list **prediction** (`A = [t − m for t in B if t − m >= 0]`, §8.4), which is not a normalization: it generates a *predicted* enumeration that must still match the measured one by exact multiset equality, so it cannot loosen the comparison.

---

## 10. Unsupported-container behaviour

- Non-ISO-BMFF source (parser raises: no `moov`/`mdhd`/`stts`, or no timing-bearing `vide` trak): R3/R4 raise; composition state is `TEMPORAL_AUTHORITY_NOT_OBSERVED(reason=<stable parser reason>)`.
- For **exact-interval (`REAL`) claims** this is the refusal `TEMPORAL_AUTHORITY_NOT_OBSERVED`. The pilot must record it as a refused scenario, not as a passing one.
- The existing container-agnostic capability is **not removed**: the fake/fixture and non-pilot paths continue to work exactly as today, but they cannot emit a composed authority, and their receipts record `composed_temporal_authority: NOT_OBSERVED`.
- `elst` with >1 segment or negative `media_time`, `ctts` version >1, negative v0 offsets: already refused by `container.py`; surfaced as `TEMPORAL_AUTHORITY_NOT_OBSERVED` with the parser's reason preserved verbatim.
- Widening container support (e.g. Matroska) is explicitly **out of scope** and requires a new owner decision (Root G §12/§13 already rejects non-ISO-BMFF expansion).

---

## 11. Refusal codes (stable)

New namespace `TEMPORAL_AUTHORITY_*`; every code names the failing fact.

| Code | Condition | Fail-closed |
|---|---|---|
| `TEMPORAL_AUTHORITY_REQUIRED` | exact claim attempted without a composed authority | yes |
| `TEMPORAL_AUTHORITY_NOT_OBSERVED` | container unsupported / parser refused / facts unmeasurable | yes |
| `TEMPORAL_AUTHORITY_IDENTITY_MISMATCH` | any of source sha/bytes/revision/manifest differ | yes |
| `TEMPORAL_AUTHORITY_STREAM_AMBIGUOUS` | ≥2 timing-bearing video traks, no explicit selector | yes |
| `TEMPORAL_AUTHORITY_STREAM_IDENTITY_DIVERGENCE` | probe video index cannot be mapped to the container trak selector | yes |
| `TEMPORAL_AUTHORITY_TIMEBASE_MISMATCH` | `(num,den) != (1, media_timescale)` | yes |
| `TEMPORAL_AUTHORITY_TIMEBASE_NOT_REDUCED` | `num != 1` | yes |
| `TEMPORAL_AUTHORITY_ENUMERATION_LENGTH_MISMATCH` | `len(A) != len(B)` | yes |
| `TEMPORAL_AUTHORITY_ENUMERATION_MISMATCH` | sorted multiset differs | yes |
| `TEMPORAL_AUTHORITY_MULTIPLICITY_MISMATCH` | duplicate-count differs | yes |
| `TEMPORAL_AUTHORITY_PRESENTATION_ORDER_INVALID` | probe presentation sequence decreases | yes |
| `TEMPORAL_AUTHORITY_EDIT_LIST_ORIGIN_NOT_APPLIED` | `elst` media_time ≠ 0 | yes |
| `TEMPORAL_AUTHORITY_REORDERING_DECLARATION_MISMATCH` | declared ≠ observed reordering | yes |
| `TEMPORAL_AUTHORITY_VFR_DECLARATION_MISMATCH` | declared ≠ observed VFR (presentation basis) | yes |
| `TEMPORAL_AUTHORITY_VFR_BASIS_DIVERGENCE` | R1 vs R3 VFR predicates differ | yes |
| `TEMPORAL_AUTHORITY_DECODE_ORDER_INVALID` | `dts` not strictly increasing | yes |
| `TEMPORAL_AUTHORITY_DURATION_INCONSISTENT` | `duration_consistency != MATCH` | yes |
| `TEMPORAL_AUTHORITY_TAIL_NOT_MEASURED` | terminal interval requested without tail facts | yes |
| `TEMPORAL_AUTHORITY_ENDPOINT_NOT_IN_COMPOSED_ENUMERATION` | endpoint not in composed enumeration | yes |
| `TEMPORAL_AUTHORITY_EVIDENCE_DIGEST_MISMATCH` | composed evidence digest fails re-verification | yes |

Pre-existing codes (`SOURCE_*`, `SNAPSHOT_*`, `AUTHORITATIVE_REFINEMENT_*`, `EDIT_LIST_ORIGIN_NOT_APPLIED`, `TIME_BASE_DOES_NOT_MATCH_NAMED_BYTES`, `ENUMERATION_DOES_NOT_MATCH_NAMED_BYTES`, `BYTE_BOUND_SOURCE_AUTHORITY_REQUIRED`, `STREAM_TAIL_NOT_SUPPORTED`) are unchanged. `STREAM_TAIL_NOT_SUPPORTED` may be *replaced* by `TEMPORAL_AUTHORITY_TAIL_NOT_MEASURED` in the preview verifier only under a separate approved change (Lane C item A-1).

### 11.1 The six required disagreement classes vs today

The mission requires that every *silent* tolerance become an attributable refusal. Mapping (from the call-path map in `docs/agent-runs/2026-10-25-g3-dual-temporal-authority/01-refinement-composition-map.md` §8):

| Disagreement class | Today | Under this design |
|---|---|---|
| differing source revision | **covered** (`SOURCE_PROBE_SNAPSHOT_BINDING_MISMATCH`, `AUTHORITATIVE_REFINEMENT_SOURCE_*`) | retained, plus `TEMPORAL_AUTHORITY_IDENTITY_MISMATCH` |
| differing stream identity | index-level only; `ffprobe` global stream index vs `moov` `trak` ordinal is **unasserted** (`container.py:166-171`) | `TEMPORAL_AUTHORITY_STREAM_IDENTITY_DIVERGENCE` (OQ-1 decides the mapping rule) |
| differing edit-list interpretation | only generic `EDIT_LIST_ORIGIN_NOT_APPLIED` at the refinement layer, and **silently dropped** by the snapshot binding (Dv-1) | `TEMPORAL_AUTHORITY_EDIT_LIST_ORIGIN_NOT_APPLIED` on both routes |
| unexplained timing offset | **none** | `TEMPORAL_AUTHORITY_ENUMERATION_MISMATCH` (any offset not produced by an accepted rule is a refusal) |
| VFR declaration vs observation | only the **uncalled** `SNAPSHOT_VFR_DECLARATION_MISMATCH` | `TEMPORAL_AUTHORITY_VFR_DECLARATION_MISMATCH` + `..._VFR_BASIS_DIVERGENCE` on the presentation basis |
| reordering declaration vs observation | only the **uncalled** `SNAPSHOT_REORDERING_DECLARATION_MISMATCH` | `TEMPORAL_AUTHORITY_REORDERING_DECLARATION_MISMATCH` |

No declaration (`declared_vfr`, `declared_reordering`) is carried by any bundle, authorization, plan or receipt today; under this design the composed evidence carries both, and the receipt carries the evidence digest.

---

## 12. Evidence classes and NOT_OBSERVED states

Per `AGENTS.md` item 6, `NOT_OBSERVED` is an availability/status condition, not an evidence class.

- Composed authority facts are `MEASURED` when both routes measured them and they agreed, `MEASURED` (single-route) when only one route can express the fact, with the owning route named.
- Corroboration that a route cannot express is recorded `NOT_APPLICABLE` with a reason, **not** `MEASURED`.
- The composed authority never introduces `MATCHED`, `VISUALLY_OBSERVED`, `AUDIO_OBSERVED`, or `EDITORIAL_INFERENCE`.
- `extent_state` for terminal intervals stays `DERIVED_NOT_OBSERVED`; `last_frame_extent` stays `null`.
- `TEMPORAL_AUTHORITY_NOT_OBSERVED` covers: unsupported container, parse refusal, absent snapshot, absent probe binding, `elst` not applied, audio facts (out of scope).
- The composed authority carries `audio_observed: NOT_OBSERVED` verbatim from the existing preview policy context — it makes no audio claim (Lane C).

---

## 13. Compatibility with existing refinement / plan / preview APIs

**Additive only.**

1. **New evidence object** `ComposedSourceTemporalAuthority` (schema `vip_fvs.composed_temporal_authority.v1`) with `schema_version`, identity block, `timebase`, `pts_ticks`, `dts_ticks`, `composition_offsets`, `has_b_frames`, `nb_frames`, `duration_ts`, `duration_consistency`, `tail_duration_ticks`, `presentation_origin_ticks`, `stream_index`, `stream_count`, `stream_handler`, `stream_identity_derivation`, `declared_vfr`, `declared_reordering`, `facts: {name: {owner, state, value}}`, `corroboration: [...]`, `snapshot_manifest_sha256`, `probe_digest`, `evidence_sha256`.
2. **`bind_temporal_authority` v2** gains the tail/stream/edit-list/`composition_offsets` fields and the corrected VFR basis; `schema_version: 1` evidence remains verifiable through `verify_temporal_authority` (v1 body accepted, v2 body accepted, mixed refused). No existing v1 test loses meaning.
3. **Refinement** (`gate3.refinement.refine`) is **unchanged in V1**: still byte-bound via `_resolve_byte_authority`, still owns binding eligibility, still refuses `EDIT_LIST_ORIGIN_NOT_APPLIED`. The composed authority is passed alongside (new optional kwarg) and its enumeration is required to equal the refinement's `byte_authority.pts_ticks` before the refinement may be published. Composition must never pass a non-member `end` (Dv-13), so `refine()`'s `end_is_stream_tail` reinterpretation is never reached accidentally. V2 would change the origin contract — a separate approval (A-9).
4. **Plan / preview receipts** gain one additive field `source.composed_temporal_authority = {evidence_sha256, schema_version}` and (preview) the same. `ReviewBundle.source.timebase` publication is unchanged (Root G §3.4 preserved in effect: the timebase published is still the measured refinement timebase, now additionally required to equal the composed and probe timebases). Both consume-time sites **re-verify the digest** (Dv-12), which today they do not.
5. **`src/vip_fvs/coordinator.py:350-351`** (fake CLI seam) is **out of scope** for v1: it measures a freshly generated container, has no snapshot, and must record `composed_temporal_authority: NOT_OBSERVED`. Its behaviour is unchanged.
6. **Preview verifier** (R2): three latent defects — `sorted(set(...))` multiplicity collapse in both preview and verifier surfaces (Dv-11), divergent stream-row admission rules (Dv-11), and vacuous provenance checks on real probe payloads (Dv-10). Tasks IT-7/IT-8; separately approvable (A-11) and independent of the composition.
7. **`src/gate0/**`** untouched. **`src/gate3/temporal.py` (T1–T11)** untouched; the design *consumes* it (`classify_vfr`, `tail_end`) rather than modifying it. **`src/gate3/refinement.py` and `container.py` are untouched in V1** — which is why V1 needs no new Gate-3 authority; V2 does (A-9).

---

## 14. Synthetic measurements and negative evidence

Measurements were produced with the local toolchain only (ffmpeg/ffprobe 9.0.2, `/opt/homebrew/bin`); no network, no provider call, no real archive. Full transcript and generator script: `docs/agent-runs/2026-10-25-g3-dual-temporal-authority/02-temporal-measurements.md` (+ `measurements/`). **Measured** facts are separated from **proposed expectations** there and summarised here.

### 14.1 Measured cases

All files generated in `/tmp/g3-measure-scratch` (395,283 B, outside the worktree; not committed). `A` = R1 `ffprobe` frame presentation PTS (measured via a mirror of `_frame_presentation_pts` reading the merged layout's frame records). `B` = R3/R4 `pts_ticks`. `origin` = `presentation_origin_ticks` (`elst` media_time).

| Case | Content | ts | `len(A)` | `len(B)` | origin | `duration_consistency` | `A == [t−origin for t in B if ≥0]` |
|---|---|---|---|---|---|---|---|
| 1 `cfr_nob` | CFR, no B-frames | 15360 | 60 | 60 | 0 | MATCH | **exact** |
| 2 `vfr` | VFR, deltas {33333,33334,66666,66667} | 1000000 | 45 | 45 | 0 | MATCH | **exact** |
| 3 `bframes` | B-frames, ctts, ffmpeg default mux | 15360 | 60 | 60 | 1024 | **MISMATCH** | **exact** |
| 4 `positive_ctts` | positive composition offsets | 15360 | 60 | 60 | 1024 | **MISMATCH** | **exact** |
| 5a `elst_makezero` | `-avoid_negative_ts make_zero`, elst(30720, 0) | 15360 | 60 | 60 | 0 | MATCH | **exact** |
| 5b `elst_trim` | `-ss` stream-copy, elst(23040, 7680) | 15360 | **45** | **60** | 7680 | MATCH | **exact** (15 leading samples dropped) |
| 5c `negative_ctts` | ctts v1, min −1024 | 15360 | 60 | 60 | 0 | MATCH | **exact** |
| 6a `terminal_cfr` | CFR terminal case | 15360 | 60 | 60 | 0 | MATCH | **exact** |
| 6b `terminal_bframes` | same bytes as 3 | 15360 | 60 | 60 | 1024 | **MISMATCH** | **exact** |
| 7 `multi_video` | 2 video traks | 10240 | 40 | 40 | 0 | MATCH | **exact** (needs selector: `ambiguous container: 2 timing-bearing video traks`) |
| 8a `timescale1000` | ts=1000, B-frames, origin 67 | 1000 | 60 | 60 | 67 | **MISMATCH** | **exact** |
| 8b `mpegts` | negative control: MPEG-TS | — | 60 | — | — | — | R3 refuses: `invalid box` for every selector |

### 14.2 Findings

- **F-1 (payload layout, Dv-9).** `ffprobe 9.0.2` emits one merged `packets_and_frames` array; the repo's extractors read `frames`/`packets` and therefore measured **0** presentation ticks and **0** observed ticks on all 10 inputs. The same merged entries reshaped into the legacy split layout give 60/45/40/60 ticks, so the extractor logic is correct and only the *payload shape adapter* is missing. Frame records carry **no `dts`** on this version (decode timestamps exist only on packet records) — an independent confirmation of R-3: `dts` cannot be obtained from the frame list at all.
- **F-2 (edit list, Dv-1/Dv-7).** `B` never applies `elst`; `A` always does. The measured rule E holds exactly in **11/11** ISO-BMFF cases including a sample-dropping trim. Every case with `origin != 0` is a case where `A != B`; every case with `origin == 0` is a case where `A == B` exactly.
- **F-3 (duration consistency, Dv-8).** `duration_consistency` is `MATCH` for all six `origin == 0` ISO-BMFF cases and `MISMATCH` for all four nonzero-origin cases; the origin-corrected identity `duration_ts == max(B) + tail − origin` holds in every one, and `ffprobe`'s `last_packet_pts + packet_duration == duration_ts` also holds. The `MISMATCH` is an artifact of the missing `−origin`, not a real duration defect.
- **F-4 (ctts correctness).** `B`'s `composition_offsets` match an independent byte-level ISO parse including signed v1 negative offsets (`case5c`), and `B`'s `pts_ticks` equal the independent reconstruction. R3's expansion is **correct**; its defects are the origin omission and the missing per-sample association.
- **F-5 (decode order).** `B`'s `dts` equals sorted packet `dts` shifted by `origin` (`case3`: `sorted_packet_dts + 1024 == B.dts`), consistent with the media-timeline reading of `stts`. No case was found where `B`'s `dts` is non-monotonic.
- **F-6 (stream ambiguity).** case 7 is measurable per-stream, but a `None` selector always raises `ambiguous container: 2 timing-bearing video traks require an explicit selected stream selector` — the refusal works, but `ffprobe` stream indices and container `trak` indices are different namespaces (OQ-1).
- **F-7 (MPEG-TS).** R3 refuses with `invalid box` for every selector; `ffprobe` measures fine (`1/90000`, `start_pts 126000`). Unsupported container ⇒ `TEMPORAL_AUTHORITY_NOT_OBSERVED`, per §10.
- **F-8 (what was *not* observed).** Non-integer presentation PTS: **NOT_OBSERVED** — MP4/TS presentation ticks are integral in every produced case (only non-uniform *integer* deltas in VFR). A distinct terminal packet duration: **NOT_OBSERVED** — the last packet's duration always equals the uniform `stts` delta. `ffprobe` metadata-only (non-decoding) frame order: **NOT_OBSERVED** (OQ-2). Multi-segment `elst`, negative `media_time`, empty edit: not producible with the pinned libavformat → **NOT_OBSERVED**; `container.py` refuses them by inspection.
- **F-9 (pilot corpus consequence).** With V1 (origin must be 0), ordinary `ffmpeg` B-frame MP4 output (`origin = one frame`) is **not admissible**; `-avoid_negative_ts make_zero` produces `origin = 0`, `A == B`, `duration_consistency = MATCH` and *is* admissible (case 5a). The pilot input spec must state this explicitly rather than discover it at run time.

**Interpretation rules used when reading §14.1:** a difference is only called a *defect* when the two routes claim to measure the same fact; differences between facts neither route claims (e.g. R1 having no decode order) are recorded as `NOT_APPLICABLE`.

---

## 15. Minimal implementation tasks (all gated on approval)

Each task is a narrow TDD slice: observed RED first, minimal GREEN, refactor with regression. No task may be started from this document alone.

| ID | Task | Write scope | RED test |
|---|---|---|---|
| **IT-0** | **R1 payload-layout adapter (Dv-9, blocking).** Accept `ffprobe_json["frames"]` *and* a merged `packets_and_frames` array (select `type=="frame"`, preserve entry order, keep the existing alias order `best_effort_timestamp → pts → pkt_pts`), in `_frame_presentation_pts` / `_observed_pts` and in `real_preview_verifier._evidence_facts`, plus the two other readers of the same payload shape (`local_preview.py:872-889`, `cli.py:167-199`). Purely shape-normalising: no alias change, no dedupe, no tolerance, and when **both** layouts are present they must agree or refuse. | `src/vip_fvs/real_source_service.py`, `src/vip_fvs/real_preview_verifier.py`, tests | merged-layout fixture ⇒ today 0 ticks; must yield 60. Legacy fixture unchanged. Merged-vs-legacy disagreement ⇒ refusal |
| **IT-1** | `bind_temporal_authority` v2: carry `nb_frames`, `duration_ts`, `duration_consistency`, `tail_duration_ticks`, `composition_offsets`, `has_b_frames`, `presentation_origin_ticks`, `stream_handler`, `stream_identity_derivation`; refuse nonzero `presentation_origin_ticks`; `verify_temporal_authority` accepts v1 and v2 | `src/vip_fvs/source_snapshot.py`, `tests/vip_fvs/unit/test_source_snapshot_*` | v2 fields absent ⇒ `SNAPSHOT_TEMPORAL_FACTS_INVALID`; `elst` source ⇒ `TEMPORAL_AUTHORITY_EDIT_LIST_ORIGIN_NOT_APPLIED` |
| **IT-2** | Correct VFR/reordering basis to presentation deltas; add basis divergence guard | same | DTS-only VFR source (uniform dts, varying cts) must be `VFR`; today R4 says CFR |
| **IT-3** | New `src/gate3/composed_temporal.py`: `compose_temporal_authority(...)`, state machine, refusal codes, evidence digest | `src/gate3/composed_temporal.py`, `tests/gate3/unit/test_composed_temporal*.py` | each of the 20 codes reachable by an independent unit test |
| **IT-4** | Wire composition into `prepare_real_source` (mandatory for REAL scope) and require composed enumeration == refinement `pts_ticks` | `src/vip_fvs/real_source_service.py`, `src/vip_fvs/refinement_adapter.py`, tests | endpoint/refinement succeeds while enumeration differs ⇒ must refuse |
| **IT-5** | Receipt additive field + digest re-verification at plan and preview (**consumption-time** re-verification, Dv-12) | `src/vip_fvs/real_plan.py`, `src/vip_fvs/real_preview_receipt.py`, tests | tampered composed evidence ⇒ `TEMPORAL_AUTHORITY_EVIDENCE_DIGEST_MISMATCH`; byte swap after seal ⇒ refusal at load |
| **IT-6** | Terminal-interval plumb (G-4): thread tail facts from composed authority into `gate3.refinement` tail path and remove the unconditional `STREAM_TAIL_NOT_SUPPORTED` refusal in the verifier **only** when tail facts are present and consistent | `src/vip_fvs/real_preview_verifier.py`, tests (tail facts reach `gate3.refinement` through its existing `container_path`/`_container_facts_binding` arguments, so `src/gate3/refinement.py` needs no edit in V1) | tail request without facts still refuses; with facts ⇒ `DERIVED_NOT_OBSERVED` binding record |
| **IT-7** | Preview/verifier multiplicity preservation (`sorted(set(...))` → multiset) **and** unify the two stream-row admission rules (Dv-11) | `src/vip_fvs/real_preview_verifier.py`, `src/vip_fvs/local_preview.py`, tests | duplicate-tick source: today passes, must fail until fixed; render-admitted evidence must be verify-admissible |
| **IT-8** | Make the verifier's provenance checks non-vacuous (Dv-10): derive byte/stream/timescale facts from the *measured* container or require them explicitly, and refuse when the evidence object cannot supply them | `src/vip_fvs/real_preview_verifier.py`, tests | canonical probe payload (no `source_bytes_sha256` key) ⇒ today silently passes; must refuse or measure |
| **IT-9** | Pilot scenario list + refusal matrix update (admits `origin == 0` sources only; states the `-avoid_negative_ts make_zero` recipe; lists `NOT_OBSERVED` cases) | docs only | review |

**Cross-lane dependency:** IT-0 blocks every end-to-end verification (Dv-9). IT-1/IT-2 must land before IT-3/IT-4; IT-6 depends on IT-1; IT-7/IT-8 are independent of the composition and can proceed in parallel.

---

## 16. Rejected alternatives and reconsideration conditions

| Rejected | Why | Reconsider when |
|---|---|---|
| **A — mutual checkers only** | Cannot resolve different projections without an ownership table; produces false disagreement on every `ctts`/`elst`/VFR source | a *third* independent measurement source (e.g. a second demuxer) is admitted and can measure the same projection |
| **Drop R4, promote R1 to sole authority** | Loses decode order, sample counts, tail facts, bounds validation, declaration checking; contradicts the pilot spec's stated requirement to prove agreement | never (would make G-3 unprovable by definition) |
| **Drop R3/R1 and use only R4** | R4 (and `bind_temporal_authority`) is byte-bound and immutable-source-bound; the *editorial* endpoint still needs an observed presentation table cross-checked against the probe that produced the retrieved hit; also `retain_enumeration` and T7/T8 validation live on the refinement side | only if the FVS retrieval layer stops consuming ffprobe |
| **Rational equivalence (cross-multiplication) for the measured-timebase comparison** | Root G §3.4 selected exact tuple equality; changing it reopens an approved decision for no observed benefit | a measured source is found whose `mdhd` timescale is unreduced w.r.t. the probe timebase and equality blocks a legitimate case (Root G §13 trigger) |
| **Apply `elst` origin as a normalization offset in v1** | `elst` semantics are now measured (rule E, 11/11 exact), but admitting them requires changing the frozen Gate-3 projection and the `gate3/refinement.py` origin contract — a second architecture delta that must not ride along with G-3's first approval unit | owner approves V2 (A-9) after V1 is in place; measured rule E remains the evidence base |
| **Nominal-FPS or float tolerance for "close" enumerations** | Forbidden by AGENTS.md item 7 and Root G §3.5 | never |
| **Wire composition only into the preview verifier (R2)** | Verification-time-only composition cannot bind the *published* cut; the pilot needs the authority at plan-publication time | never for exact claims |
| **Make composition optional with a warning** | R-5; produces `MEASURED`-looking receipts without proof | never |

---

## 17. Owner approval items

Deltas against the approved Root G design (each requires explicit owner approval before implementation):

- **A-1 (D-1):** Root G §3.4 says the measured timebase is read **from the authoritative refinement record** and forbids a second container parser inside `real_source_service.py`. C′ keeps §3.4's *outcome* but requires the timebase to be a **three-way** equality (probe == composed snapshot binding == refinement), and locates the composition in `prepare_real_source`. Confirm this does not violate §3.4 or §12's "cross-check-only closure" rejection.
- **A-2 (D-2):** `bind_temporal_authority`'s VFR basis changes from DTS-deltas+tail to presentation-deltas. This is a semantic change to an approved-evidence producer (v2). Confirm.
- **A-3 (D-3):** `bind_temporal_authority` carries new fields under evidence `schema_version` 2. Confirm this versioning approach (v1 evidence remains verifiable) is acceptable rather than a hard break. The `elst` admissibility rule itself is A-9's decision, not this one.
- **A-4 (D-4):** Mandatory composition for `plan_scope="REAL"` exact claims, with `TEMPORAL_AUTHORITY_REQUIRED` refusal ⇒ behaviour change for existing REAL-scope callers. Confirm, including whether any existing non-pilot REAL path must be exempted.
- **A-5:** Approve the `TEMPORAL_AUTHORITY_*` refusal-code namespace and the 20 codes in §11 as stable names.
- **A-6:** Approve `src/gate3/composed_temporal.py` as a new Gate-3 module (T1–T11 untouched).
- **A-7:** Decide OQ-1 (stream index namespace) — see §18.
- **A-8:** Decide *when* the preview verifier multiplicity / row-rule fix (IT-7) lands: now as a standalone correctness repair, or bundled with this design's approval. Its *content* is not in question; A-11 covers the separate provenance repair (IT-8).
- **A-9 (edit-list admission, V1 vs V2):** approve **V1** (composition requires `elst media_time == 0`; nonzero-origin sources ⇒ `TEMPORAL_AUTHORITY_EDIT_LIST_ORIGIN_NOT_APPLIED`, so ordinary `ffmpeg` B-frame MP4 output is inadmissible until muxed with `-avoid_negative_ts make_zero`), or authorise preparation of **V2** (measured projection rule E, §8.4, with `container.py` per-sample pairs, origin-corrected `duration_consistency`, and a `gate3/refinement.py` origin-contract change). V1 is recommended as the first approval unit: it needs no change to the frozen Gate-3 surface, and rule E's exact equality check means V2 can be added later without weakening anything.
- **A-10 (Dv-9, blocking):** authorise **IT-0**, the merged `packets_and_frames` payload adapter. Without it, R1 measures zero presentation ticks on the installed `ffprobe` and no end-to-end G-3 evidence can be produced at all. This is a fail-closed capability defect, not a data-integrity defect; it changes no alias rule, no dedupe rule and no tolerance.
- **A-11 (Dv-10):** authorise the non-vacuous provenance-check repair (IT-8) as a standalone repair, or defer it behind the composition. (The IT-7 multiplicity/row-rule repair is A-8.)
- **A-12 (Dv-12 / Dv-13):** approve consumption-time re-verification of composed evidence (IT-5) and the explicit rule that composition never hands `refine()` a non-member end (so `end_is_stream_tail` is never reached by accident).

---

## 18. Open questions (NOT_OBSERVED / undecided)

- **OQ-1** *Stream index namespace.* `ffprobe`'s `index` counts all streams; `container.py`'s selector counts timing-bearing `vide` traks. Mapping is unambiguous only when all preceding streams are video. Needs either (a) an explicit probe→trak mapping rule, or (b) a refusal whenever a non-video stream precedes the selected video stream. **Not resolved here.**
- **OQ-2** Whether `ffprobe` `best_effort_timestamp` is presentation order in *all* supported cases, or only when the decoder runs (it runs here because `-show_frames` implies decode). If a probe mode without decode is ever admitted, §8.3 step 3 must be revisited. **NOT_OBSERVED for non-decoding modes.**
- **OQ-3** Whether `mtimescale`-vs-`mdhd` `duration_ts` corroboration against `ffprobe format.duration` should be mandatory or corroborative-only (design currently: corroborative, refusal only on `duration_consistency != MATCH`).
- **OQ-4** Interaction with `preverified_snapshot` (`real_source_service.py:471-483`): composition must still hold for a caller-supplied verified snapshot; no reason it should not, but no test exists today. **NOT_OBSERVED.**

---

## 19. Status summary

| Item | Status |
|---|---|
| G-3 exact missing composition path | **IDENTIFIED AND REPRODUCED** (§1.2, §1.3, §14) |
| Composed temporal authority contract | **DESIGNED_PENDING_APPROVAL** |
| Implementation of any change | **NOT STARTED** (blocked on §17 approval) |
| Root-G §3.4 semantics | **PRESERVED IN EFFECT, RELOCATED (D-1)** — pending A-1 |
| Dv-9 `ffprobe` payload shape (R1 measures 0 ticks) | **REPRODUCED — BLOCKING**, fix designed (IT-0), pending A-10 |
| Dv-8 `duration_consistency` missing `−origin` | **REPRODUCED** (11/11 cases), fix folded into A-9/V2 |
| Dv-10 verifier vacuous provenance checks | **CONFIRMED BY INSPECTION**, fix designed (IT-8), pending A-11 |
| Dv-11 multiplicity collapse / row-rule divergence | **CONFIRMED BY INSPECTION**, fix designed (IT-7), pending A-11 |
| Dv-12 seal-time-only authority | **CONFIRMED BY INSPECTION**, fix designed (IT-5), pending A-12 |
| G-4 stream tail | **PLUMBING GAP CONFIRMED**; enabler designed (IT-1/IT-6); Lane C owns the memo |
| Corpus separation (Lane B) | **DESIGNED_PENDING_APPROVAL** (no approved executable contract) |
| Audio policy (Lane C) | **NOT_OBSERVED**; minimum requirement set documented; no subsystem proposed |
| Non-integer presentation PTS | **NOT_OBSERVED** (not producible locally) |
| Non-decoding `ffprobe` frame order | **NOT_OBSERVED** (OQ-2) |
| Multi-segment / negative / empty-edit `elst` | **NOT_OBSERVED** (refused by inspection) |
