# Gate-3 A-7 Stream Identity Mapping — RED→GREEN Implementation Plan (rev. 2, proposed)

> **For agentic workers:** REQUIRED SUB-SKILL: `superpowers:executing-plans` for controlled single-writer execution. Steps use checkbox syntax. Follow repository rolling-frontier rules; never spawn parallel writers on the same path and never manufacture work to fill slots.
> **This plan is not authorized by itself.** It becomes executable only after a contract-owner record adopts `docs/decisions/2026-10-25-g3-a7-cross-contract-integration-readiness.md` §3 and prerequisites `P-1 … P-12` in that packet's §6 are dispositioned.

**Goal:** Turn the proposed rule — FFprobe `streams[i].id` equals the `tkhd.track_ID` of the `i`-th direct `moov/trak`, positionally, fail-closed otherwise, for multi-`trak` containers — into a minimal implemented, RED-then-GREEN verified predicate with exactly one fact owner, one shared invocation policy, and two invoking consumers, changing no sealed evidence, schema, probe argv, receipt, or preview artifact.

**Architecture:** One new Gate-3 module owns the `tkhd` fact **and** the cross-namespace comparison and is pure (no I/O). One new tiny FVS module owns the invocation policy, the artifact file-digest check, and the container-side `trak` count. Two existing FVS surfaces invoke it: bind (`refinement_adapter`) and bundle validation (`review_bundle`). Nothing is serialized; the verifier, `container.py`, `source_snapshot.py`, `schemas/**` and the probe argv are untouched.

**Tech Stack:** Python ≥3.11 (suites run on CPython 3.14.9 at `/Users/yusuf/Repos/video-intelligence-pipeline/.venv/bin/python`), pytest 8.3.3, stdlib only (`struct`, `hashlib`, `json`), `gate3.fixturegen`, `gate3.container`, existing `vip_fvs` byte-authority helpers. **No test executes ffmpeg/ffprobe.**

**Spec:** `docs/decisions/2026-10-25-g3-a7-cross-contract-integration-readiness.md` (rev. 2); background PR #203's packet and `docs/superpowers/specs/2026-10-25-gate3-dual-temporal-authority-composition-design.md` §6/§7/§11.1/§18. Rev. 2 folds 30 adversarial findings; see the packet's §12.

## Global constraints

- Planning base: `813f1982416fda7cb5619c903a607df148df2140`. Re-fetch and compare before starting.
- Implement on an isolated source branch/worktree off then-current approved `main`; never commit to canonical `main`.
- **Never edit:** `src/gate3/container.py`, `src/gate3/refinement.py`, `src/gate3/temporal.py`, `src/vip_fvs/source_snapshot.py`, `src/vip_fvs/real_source_probe.py`, `src/vip_fvs/local_preview.py`, `src/vip_fvs/real_preview_verifier.py`, `schemas/**`, `src/gate0/**`, the canonical WBS, any pinned reference pack.
- **Never add:** a probe flag or `-select_streams`; a sealed evidence key; a new refusal-code namespace; a plan/review-bundle/receipt field; a `TEMPORAL_AUTHORITY_*` name; a literal diagnostic string pinned in a test.
- **Never weaken:** the refusal-only protection. Never accept a mapping on count equality, box-order plausibility, handler heuristics, or `media_timescale`.
- **Never add an edit-list refusal.** Edit lists stay exactly as A-9 approved them (origin-zero admitted; nonzero `elst.media_time` refuses `EDIT_LIST_ORIGIN_NOT_APPLIED`).
- No real/protected media, no network, no provider/model calls, no downloads, no render/export, no Gate promotion, no merge.
- Every behaviour change: **observed RED first** at the acting base, then minimal GREEN, then regression. A test that cannot be shown RED before implementation is not evidence. A collection/`ImportError` RED counts only where the plan says so.
- Each slice closes with a written "what this slice does **not** prove" statement in the PR body.

## Slice map, dependencies, merge order

| Slice | Writer | Depends on | Merge position |
|---|---|---|---|
| `S1` fixture conformance + named byte-pin re-baseline | `W-FIXTURE` | `P-3`, `P-8` | 1 |
| `S2` fact + predicate module (pure) | `W-FACT` | `P-1`, `P-2`, `P-8`, `S1` | 2 |
| `S3` shared invocation policy (I/O + digest) | `W-GATE` | `P-4`, `P-5`, `P-7`, `S2` | 3 |
| `S4` bind-time enforcement | `W-BIND` | `P-12`, `S3` | 4a |
| `S5` consumption-time enforcement | `W-BUNDLE` | `P-11`, `S3` | 4b (parallel with 4a) |
| `S6` verifier hardening | — | A-11 scope confirmation | **NOT AUTHORIZED — deferred** |
| `S7` probe self-binding (`B-11`) | — | `P-6` grant | **NOT AUTHORIZED — deferred** |

Write sets are disjoint; `S4`/`S5` may run concurrently because both depend only on `S3`.

---

## S1 — `W-FIXTURE`: conformant `tkhd`, the shapes the RED matrix needs, and two named re-baselines

**Exclusive write paths**
- `src/gate3/fixturegen.py`
- `tests/gate3/test_fixturegen_tkhd_conformance.py` (new)
- `tests/vip_fvs/unit/test_source_snapshot_temporal_single_read.py` — **exactly** `_FROZEN_PARSE["source_bytes_sha256"]` (`:55`) and `_FROZEN_BINDING["source_sha256"]` (`:70`), nothing else

**Current state (MEASURED):** `_tkhd` (`fixturegen.py:21`) writes `struct.pack(">II", 0, track)` then four zero bytes then the duration — i.e. the track ordinal lands in **`modification_time`**, **`track_ID` stays 0**, the declared duration lands in **`reserved`**, and `duration` is 0. Box length is spec-correct (92). Every generated MP4 therefore reports `id = "0x0"` and ffprobe warns `Sample size … is too large`.

**Required changes**
1. `_tkhd(track, d)` writes spec order: `creation_time = 0`, `modification_time = 0`, `track_ID = track`, `reserved = 0`, `duration = d`, then 60 zero bytes. Payload stays 80 / box stays 92, so no other box offset in the generator moves and `source_byte_count` is unchanged.
2. `_trak_bytes(...)` accepts an optional `track_id`; `build_multi_trak_mp4` keeps `track = i + 1`, giving distinct ids `1 … n` with no other call-site change.
3. New builders returning bytes only: `build_no_tkhd_mp4`, `build_short_tkhd_mp4` (box 80 < 92), `build_zero_size_tkhd_mp4` (`size` word `0`), `build_large_size_tkhd_mp4` (`size == 1`, legal `track_ID`), `build_tkhd_version_2_mp4`, `build_duplicate_track_id_mp4`, `build_reversed_track_ids_mp4` (video `track_ID 2` first, audio `track_ID 1` second), `build_timingless_trak_mp4` (a `trak` with no `stts`, but with a `tkhd`).
4. `RECIPES` gains these shapes and **at least one test consumes a `RECIPES` entry through the public builder** (PR #203 `G-9`/`E-M5`).
5. Re-baseline exactly the two constants named in the write set. Why they move: both pin the digest of `build_mp4(_REORDER_BYTES)`; the `tkhd` fix changes those bytes. Measured pre-existing full-suite effect of the fix: **2 failed, 1221 passed**.

**RED predicates**

| Row | Predicate on the *pre-fix* generator | Pre-fix result |
|---|---|---|
| R-F1 | `structure_track_id(build_mp4(...)) == 1` | FAIL (`0`) |
| R-F2 | `structure_modification_time(build_mp4(...)) == 0` | FAIL (`1`) |
| R-F3 | `structure_duration(build_mp4(... declared_duration=120)) == 120` | FAIL (`0`) |
| R-F4 | `build_multi_trak_mp4(2 traks)` yields `track_ID == (1, 2)` | FAIL (`(0, 0)`) |
| R-F5 | each new builder produces its declared shape | FAIL (builder absent; **the only row where `AttributeError` is acceptable RED**) |
| R-F6 | the two re-baselined constants equal the digests of the post-fix fixture | FAIL (old digests) — capture the failure **after** step 1 and before step 5 |

`structure_*` helpers are new test-local parsers that walk boxes with the same header-aware rule the production reader uses. They live in the new test file only.

**Stop guard (REQUIRED).** Stop and report if any of these occurs: a third test file needs a digest/`byte_count` change; a test asserts `id == "0x0"`, `modification_time != 0`, or `duration == 0` and cannot be re-baselined by editing that assertion alone; a real-ffprobe-derived assertion changes; or any expectation changes that this plan does not name. **Do not "fix" an unrelated assertion to make the suite pass.**

**GREEN:** R-F1…R-F6 pass; full suite `PYTHONPATH=experiments:src:. python -m pytest tests/gate3 tests/vip_fvs -q` returns **1223 passed, 1 xfailed** or better; the single `xfail` (`DC-BIND`, `tests/vip_fvs/adversarial/test_temporal_evidence_v1_matrix.py:376-400`) is untouched.

**Does not prove:** that any generated container is decodable media. The `stsd` sample entry is synthetic by design.

---

## S2 — `W-FACT`: the `tkhd` fact and the cross-namespace predicate (pure module)

**Exclusive write paths**
- `src/gate3/stream_identity.py` (new)
- `tests/gate3/test_stream_identity_mapping.py` (new)

**Module contract (exact)**

```python
POSITIONAL_IDENTITY_DERIVATION = "positional_tkhd_track_id_equals_probe_stream_id"

REASON_BOUND_EVIDENCE_UNAVAILABLE = "BOUND-EVIDENCE-UNAVAILABLE"
REASON_NO_TKHD                    = "NO-TKHD"
REASON_TKHD_HEADER_UNSUPPORTED    = "TKHD-HEADER-UNSUPPORTED"
REASON_TRACK_ID_UNUSABLE          = "TRACK-ID-UNUSABLE"
REASON_TRACK_ID_DUPLICATE         = "TRACK-ID-DUPLICATE"
REASON_COUNT_MISMATCH             = "COUNT-MISMATCH"
REASON_PROBE_ID_UNUSABLE          = "PROBE-ID-UNUSABLE"
REASON_POSITIONAL_MISMATCH        = "POSITIONAL-MISMATCH"
REASON_SELECTED_NOT_VIDEO         = "SELECTED-NOT-VIDEO"
REASON_SELECTION_AMBIGUOUS        = "SELECTION-AMBIGUOUS"

@dataclass(frozen=True)
class StreamIdentityEvidence:
    state: str                     # "PROVEN" | "REFUSED"
    reason: str | None             # one of the REASON_* constants
    derivation: str | None         # POSITIONAL_IDENTITY_DERIVATION when PROVEN
    selected_position: int | None
    track_ids: tuple[int, ...] | None
    probe_ids: tuple[int, ...] | None
    container_sha256: str
    probe_digest: str
    probe_provenance: str          # caller-named artifact path/ref; recorded, not trusted
    probe_source_binding: str      # "PRODUCER_SEALED"
    demuxer_build_state: str       # "NOT_OBSERVED" (transient; never persisted)

class StreamIdentityUnproven(ValueError):
    reason: str
    evidence: StreamIdentityEvidence

def evaluate_stream_identity(*, container_bytes, container_sha256, probe_streams,
                             probe_digest, probe_provenance,
                             selected_stream_index) -> StreamIdentityEvidence: ...

def require_stream_identity(**kwargs) -> StreamIdentityEvidence: ...  # raises StreamIdentityUnproven
```

**Evaluation order — one order only, mirroring the packet's §3 fail-closed list**

1. `container_sha256 == sha256(container_bytes)` → else `BOUND-EVIDENCE-UNAVAILABLE`.
2. `probe_digest` is 64 lowercase hex; `probe_streams` is a non-empty sequence of mappings; `probe_provenance` is a non-empty string → else `BOUND-EVIDENCE-UNAVAILABLE`.
3. Direct `moov` `trak` children enumerated in box order; each must have exactly one direct `tkhd` → else `NO-TKHD`.
4. Per `tkhd`: re-read the **raw size word** at the yielded `box_start`; refuse `0` and `1`; require length `>= 92` (v0) / `>= 104` (v1), version ∈ {0,1}, `track_ID` field inside the box → else `TKHD-HEADER-UNSUPPORTED`.
5. `0 < track_ID < 0xFFFFFFFF` for all → else `TRACK-ID-UNUSABLE`; pairwise distinct → else `TRACK-ID-DUPLICATE`.
6. `len(probe_streams) == len(traks)` → else `COUNT-MISMATCH`.
7. Every row has `index`, `codec_type`, `id`; `id` canonical lowercase `0x` hex with `0 < int(id,16) < 0xFFFFFFFF`; `index == position` → else `PROBE-ID-UNUSABLE`.
8. `int(probe_streams[i]["id"],16) == track_ids[i]` for **every** `i` → else `POSITIONAL-MISMATCH`.
9. Selected position `k` is an exact `int` (not `bool`, not `float`), `0 <= k < len(traks)`, `handler(Tk) == b"vide"`, `probe_streams[k]["codec_type"] == "video"`, `probe_streams[k]["index"] == k` → else `SELECTED-NOT-VIDEO` / `SELECTION-AMBIGUOUS`.

There is no fragmentation, edit-list, timing, or `CONTAINER-UNSUPPORTED` branch: this module reads box headers and `tkhd` payloads only. Timing admission stays with the container/refinement paths; edit lists stay with A-9.

**Hard constraints (each gets its own test)**
- Imports `gate3.container` and stdlib only. No `vip_fvs` import, no `subprocess`, no `os.environ`, no clock, no filesystem, no network.
- Never invokes `ffprobe`.
- Accepts `bytes`/`bytearray`/`memoryview`; never mutates the buffer.
- Reads boxes with `container._boxes` only; no local box walker; **no `box_start + 20` arithmetic**.
- `probe_source_binding` is always `"PRODUCER_SEALED"`; the module never claims to have verified the pairing itself.

**RED predicates**

| Row | Shape / input | Expected |
|---|---|---|
| R-01 | single video, `track_ID 1`, probe `["0x1"]`, `k=0` | `PROVEN` |
| R-02 | audio(`track_ID 1`) then video(`track_ID 2`), `k=1` | `PROVEN` |
| R-03 | reversed: video(`track_ID 2`) first, audio(`track_ID 1`), `k=0` | `PROVEN`, `track_ids == (2,1)` — defeats `id == k` |
| R-04 | two video traks ids `(1,2)`, `k=0` and `k=1` | `PROVEN` on both |
| R-05 | one container byte mutated after the digest is captured | `REFUSED / *_BOUND_EVIDENCE_UNAVAILABLE` |
| R-06 | `probe_digest` absent / 63-hex / uppercase / empty `provenance` | `REFUSED / *_BOUND_EVIDENCE_UNAVAILABLE` |
| R-07 | `trak` without `tkhd` | `REFUSED / *_NO_TKHD` |
| R-08 | short `tkhd` (box 80) | `REFUSED / *_TKHD_HEADER_UNSUPPORTED` |
| R-09 | `size` word `0` | `REFUSED / *_TKHD_HEADER_UNSUPPORTED` |
| R-10 | large-size `tkhd` (`size == 1`, legal `track_ID`) | `REFUSED / *_TKHD_HEADER_UNSUPPORTED` — a naive `box+20` reader would "find" a plausible integer |
| R-11 | `tkhd` version 2 | `REFUSED / *_TKHD_HEADER_UNSUPPORTED` |
| R-12 | `track_ID == 0`; `track_ID == 0xFFFFFFFF` | `REFUSED / *_TRACK_ID_UNUSABLE` |
| R-13 | duplicate `track_ID` | `REFUSED / *_TRACK_ID_DUPLICATE` |
| R-14 | probe rows one short / one extra | `REFUSED / *_COUNT_MISMATCH` |
| R-15 | probe `id` missing / `"1"` / `"0x0"` / `"0xFFFFFFFF"` / `index != position` | `REFUSED / *_PROBE_ID_UNUSABLE` |
| R-16 | one position swapped (`0x1`↔`0x2`) | `REFUSED / *_POSITIONAL_MISMATCH` |
| R-17 | `k` at the audio position | `REFUSED / *_SELECTED_NOT_VIDEO` |
| R-18 | `k = -1`, `k = len(traks)`, `k` as `bool` / `float` | `REFUSED / *_SELECTION_AMBIGUOUS` |
| R-19 | probe row says `video` at a `soun` trak position | `REFUSED / *_SELECTED_NOT_VIDEO` |
| R-20 | a `trak` with no `stts` but with a valid `tkhd` | `PROVEN` — the predicate does not require timing |
| R-21 | static guard: module source contains `subprocess`, `time.time`, `+20`, `vip_fvs`, or `open(` | FAIL (after the module exists, before the corrective edit) |
| R-22 | evidence object: `state/PROVEN` carries `probe_source_binding == "PRODUCER_SEALED"` and `demuxer_build_state == "NOT_OBSERVED"` for every PROVEN row | FAIL before implementation |

For R-01…R-20, create the test file first with imports inside the test bodies so each row's RED is an `ImportError` **and** record that fact explicitly; after the module exists, re-run and record the pre-implementation failures as RED where the row then fails for the *expected* reason. A row that passes as soon as the module exists with a blanket-refusal stub is not demonstrated RED — R-01/R-02/R-03/R-04/R-20 are the rows that defeat such a stub, so capture their behaviour against a stub before implementing the real body.

**GREEN:** all rows pass; suite grows by the row count; no other suite changes.

**Does not prove:** that any real demuxer produces the positional correspondence (the probe rows are test-constructed); that the probe artifact corresponds to the container bytes (that is `PRODUCER_SEALED`); or anything about timing.

---

## S3 — `W-GATE`: the shared invocation policy

**Exclusive write paths**
- `src/vip_fvs/stream_identity_gate.py` (new)
- `tests/vip_fvs/test_stream_identity_gate.py` (new)

**Why a second module:** both consumers must apply the same policy, and neither may import the other (`review_bundle` is imported widely; `refinement_adapter` is the creation path). One function, one place.

**Contract (exact)**

```python
def require_bound_stream_identity(
    *, container_path, container_sha256,
    probe_artifact_path, probe_digest,
    selected_stream_index,
) -> StreamIdentityEvidence: ...
```

Steps, in this order:
1. **Read the container bytes** from `container_path`; if unreadable → refusal. Hash them; mismatch with `container_sha256` → refusal. **Derive `len(traks)` from those bytes** (never from a caller argument).
2. **Single-`trak` branch:** if `len(traks) == 1`, return a `PROVEN`-equivalent legacy result *without* requiring the probe artifact (no namespace ambiguity exists; this preserves the pre-`P2` behaviour exactly). This branch is taken only after counting from real bytes.
3. **Read the probe artifact file bytes** and require `sha256(bytes) == probe_digest`. The producer digests canonical JSON **including its trailing newline** (`real_source_probe.py:198-199`), so hash the file as written; do not re-serialize. Then parse the JSON and take the `streams` list.
4. Call `require_stream_identity(...)` with `container_bytes`, the computed sha, the rows, `probe_digest`, `probe_provenance=str(probe_artifact_path)`, and `selected_stream_index`.
5. Return the evidence, or propagate `StreamIdentityUnproven` unchanged.

**RED predicates**

| Row | Predicate | Expected before S3 |
|---|---|---|
| R-G1 | valid two-`trak` audio-then-video fixture + genuine artifact → `PROVEN` with `probe_source_binding == "PRODUCER_SEALED"` | FAIL (`ImportError`) |
| R-G2 | artifact JSON re-serialized **without** the trailing newline while `probe_digest` is the producer's → refusal (this row is the anti-W2F-2 regression) | FAIL |
| R-G3 | artifact file one byte tampered → refusal, distinct reason/state | FAIL |
| R-G4 | container file mutated after `container_sha256` captured → refusal | FAIL |
| R-G5 | `len(traks) == 1` and **no** artifact provided → legacy success, no exception | FAIL |
| R-G6 | `len(traks) == 2` and no artifact provided → refusal (caller cannot supply evidence) | FAIL |
| R-G7 | valid three-`trak` video/soun/video with correct rows → `PROVEN` (defeats a blanket-refusal stub) | FAIL |
| R-G8 | a caller-supplied `stream_count` argument no longer exists: the signature has no such parameter | FAIL (signature assertion) |

**GREEN:** all R-G rows pass; the module imports `gate3.stream_identity` and stdlib only; no `subprocess`; no writes.

**Does not prove:** which artifact belongs to which source. It proves the artifact file matches the declared digest and the container matches the declared digest; the pairing is `PRODUCER_SEALED` by construction.

---

## S4 — `W-BIND`: bind-time enforcement

**Exclusive write paths**
- `src/vip_fvs/refinement_adapter.py` — the guard in `refine_requested_candidate` (`:144-217`) and the forwarder `refine_retrieval_candidate` (`:281`)
- `src/vip_fvs/real_source_service.py` — lines `540-552` only
- `tests/gate3/test_stream_namespace_safety.py` — only if a pin legitimately changes (report first)
- `tests/vip_fvs/test_stream_identity_bind.py` (new)

**Changes**
1. `refine_requested_candidate(..., probe_artifact_path=None, probe_digest=None)`; `refine_retrieval_candidate` forwards both. Historical positional signature and `RefinementResult` shape unchanged.
2. Replace the guard at `:194-217` with a call to `require_bound_stream_identity`. **Deletion and replacement are one commit.**
3. `real_source_service.py:540-552` passes `probe.canonical_probe_artifact_ref` and `probe.probe_digest`. No parser call is added to that file.
4. When both keywords are absent, the gate is called with no artifact and refuses multi-`trak` containers, preserving the current message prefix `stream identity is unproven: `. **Run the five existing pins first and report whether any needs amendment; do not amend silently** (expected: none, since they assert only the prefix).
5. `selected_stream_index` / `stream_index` semantics unchanged: the published value stays the FFprobe integer.
6. No edit-list behaviour change anywhere.

**RED predicates**

| Row | Predicate | Expected at `S3` base |
|---|---|---|
| R-B1 | two-`trak` audio-then-video + genuine artifact → refinement **binds** (`binding_eligible is True`) | FAIL (still refuses) |
| R-B2 | same fixture, one position swapped → refuses with a reason **distinguishable** from the no-evidence refusal | FAIL (only the generic refusal exists) |
| R-B3 | two-`trak`, no artifact → refuses with the existing prefix | PASS before and after (regression) |
| R-B4 | duplicate-`track_ID` fixture + matching artifact → refuses with the duplicate reason, not the generic one | FAIL (generic only) |
| R-B5 | all 5 rows of `tests/gate3/test_stream_namespace_safety.py` unchanged | PASS (regression) |
| R-B6 | provenance: the adapter passes the binding's own artifact ref + digest (marker test asserting equality with the probe binding) | FAIL |
| R-B7 | `git diff --stat` shows no change to `container.py`, `refinement.py`, `source_snapshot.py`, probe argv | FAIL only if the slice misbehaves (guard row) |

**GREEN:** R-B1/R-B2/R-B4/R-B6 pass; R-B3/R-B5/R-B7 green.

**Does not prove:** that the FVS renders the right frames. It proves the integer handed to `-map 0:{stream_index}` addresses a stream whose ISO-BMFF track has been positionally identified (`PRODUCER_SEALED` pairing).

---

## S5 — `W-BUNDLE`: consumption-time enforcement

**Exclusive write paths**
- `src/vip_fvs/review_bundle.py`
- `tests/vip_fvs/test_review_bundle_stream_identity.py` (new)

**Changes**
1. At the existing cross-namespace gate (`review_bundle.py:356-364`), before accepting `artifact["stream_index"] == refinement["selected_stream_index"]`, call `require_bound_stream_identity` with: `container_path = binding["byte_authority"]["container_path"]`, `container_sha256 = payload["source"]["source_sha256"]`, `probe_artifact_path = payload["source"]["probe_artifact_ref"]`, `probe_digest = payload["source"]["probe_digest"]`, `selected_stream_index = refinement["selected_stream_index"]`.
2. **If `container_path` is `None`** (artifact-only byte authority), refuse. This is a coverage rule: a bundle that names no resolvable container cannot prove the correspondence.
3. Existing digest revalidation and `is_binding_eligible` run **before** the gate.
4. No new field, no schema change, no new token.
5. The gate performs a **metadata-only** read: box headers plus `tkhd` fields. It must not call `parse_iso_smff_timing` and must not import `stts`/`ctts`/`mdhd` parsers — pinned by a static guard test.

**RED predicates**

| Row | Predicate | Expected at `S3` base |
|---|---|---|
| R-U1 | bundle whose refinement names a swapped position: validates today, must refuse after | FAIL (validates today — the live gap; the reproduction digest `465f60ab…` from lane F is the fixture to regenerate) |
| R-U2 | `payload.source.probe_artifact_ref` missing on disk → refuse | FAIL |
| R-U3 | probe artifact content mismatched to `payload.source.probe_digest` → refuse | FAIL |
| R-U4 | named container file mutated → refuse (existing byte-authority path fires first; assert that same refusal) | PASS (regression) |
| R-U5 | fully valid single-`trak` bundle → still validates | PASS (regression) |
| R-U6 | golden bundle still passes schema v3 validation; `schemas/vip_fvs/review_bundle.v3.json` byte-identical | PASS (regression) |
| R-U7 | `byte_authority.container_path is None` → refuse (no silent degradation) | FAIL |
| R-U8 | static guard: the changed code imports no timing parser and the suite still reports the same timing-parser call count as before (a wrapper counter in the test) | FAIL |

**GREEN:** R-U1/R-U2/R-U3/R-U7/R-U8 pass; R-U4/R-U5/R-U6 green.

**Does not prove:** that the bundle's source is the media the operator intended. It proves the refinement's stream integer denotes a positionally identified track in the same bytes the bundle names, with a `PRODUCER_SEALED` probe pairing.

---

## Acceptance evidence contract (per slice, in the PR body)

1. Acting base SHA, `git rev-parse`/`git diff --stat` before and after.
2. RED transcript per row **before** implementation, from a real run, naming the row id and the actual failure.
3. GREEN transcript after, same command and interpreter.
4. Refusal assertions in terms of `state` / `REASON_*` constants — **never** a pinned diagnostic literal.
5. Full suite with counts, compared to the `813f1982` baseline **1223 passed, 1 xfailed**; the `DC-BIND` `xfail` unchanged.
6. `git diff --stat` proving no forbidden path was touched.
7. The slice's **"does not prove"** statement.
8. Which of `P-1 … P-12` were satisfied by which record.

## Stop conditions (any hit → stop and report, do not work around)

- A forbidden path would need an edit.
- A sealed evidence key, receipt field, schema file, or probe argv would need a change.
- A third test file needs a digest/`byte_count` re-baseline, or a stop-guard row from S1 fires.
- A pin outside the documented rows changes.
- The suite shows a failure not explainable by the slice's own RED/GREEN rows.
- `origin/main` moved and this plan's anchors no longer resolve.
- Someone proposes handing the verifier a new derivation — that is `S6`, **not authorized**.
- Someone proposes labelling the proof "independent" — it is `PRODUCER_SEALED` until `S7` lands.

## Deferred, not dropped

- **S6 verifier hardening** (IT-8 / A-11): blocked on a scope confirmation that "derive a mapping and refuse" is inside the `(b)` refusal subset. `a3:47` also names the shared preview/verifier; the A-11/A-12 records govern it.
- **S7 probe self-binding** (`B-11`): persist the source digest **and** the demuxer executable digest with the probe artifact so the pairing becomes self-proving and `demuxer_build_state` can become `OBSERVED`. Needs its own grant on `src/vip_fvs/real_source_probe.py`.
- **Seal vocabulary tightening** at `source_snapshot.py:811`: refuses nothing that binds today; frozen-file delta for no safety gain now.
- **`P2u`/`B-6`**: needs a `video_trak_count`-over-all-traks fact; revisit only if a real corpus shows a case `P2` refuses but `P2u` admits safely.

## Task packets

### Packet `W-FIXTURE` (S1)

> Worktree: isolated source branch off current approved `main`. Exclusive write paths: `src/gate3/fixturegen.py`; `tests/gate3/test_fixturegen_tkhd_conformance.py`; and **only** the two named constants in `tests/vip_fvs/unit/test_source_snapshot_temporal_single_read.py`.
> Prerequisites: `P-3` and `P-8` recorded. If either is missing, stop and report.
> Task: implement S1 exactly. Reproduce the `_tkhd` defect first and capture R-F1…R-F5 RED; then the field-order fix, the optional `track_id`, the eight builders, the `RECIPES` consumer; then re-baseline the two constants and capture R-F6. Touch nothing else. Never re-baseline an unrelated assertion.
> Report: base/head SHAs; changed paths; RED and GREEN transcripts; full-suite counts; `git diff --stat`; the "does not prove" sentence; any stop-guard hit.

### Packet `W-FACT` (S2)

> Worktree: isolated source branch. Exclusive write paths: `src/gate3/stream_identity.py`, `tests/gate3/test_stream_identity_mapping.py`.
> Prerequisites: `P-1`, `P-2`, `P-8`; `S1` merged.
> Task: implement S2 exactly to the contract and the single evaluation order. No `vip_fvs` import, no `subprocess`, no second box walker, no `+20` arithmetic, no timing or edit-list branch. Land the test file first; capture R-01…R-22 RED (including the stub-behaviour capture for R-01/R-02/R-03/R-04/R-20); then implement.
> Report: as S1, plus the implemented evaluation order and any place the rule text was ambiguous (stop and report rather than inventing a branch).

### Packet `W-GATE` (S3)

> Worktree: isolated source branch. Exclusive write paths: `src/vip_fvs/stream_identity_gate.py`, `tests/vip_fvs/test_stream_identity_gate.py`.
> Prerequisites: `P-4`, `P-5`, `P-7`; `S2` merged.
> Task: implement S3 exactly, including counting `traks` from bytes before the single-`trak` branch, hashing the artifact file as written, and the trailing-newline regression R-G2.
> Report: as S1, plus a statement of what the gate can and cannot prove about artifact↔source attribution.

### Packet `W-BIND` (S4)

> Worktree: isolated source branch. Exclusive write paths: `src/vip_fvs/refinement_adapter.py`; `src/vip_fvs/real_source_service.py` lines 540-552 only; `tests/gate3/test_stream_namespace_safety.py` (report before editing); `tests/vip_fvs/test_stream_identity_bind.py`.
> Prerequisites: `P-12`; `S3` merged.
> Task: implement S4 exactly. Guard replacement is one commit. Run the five existing pins before editing and report whether any needs amendment.
> Report: as S1, plus the before/after behaviour of each of the five pins, and the provenance-equality evidence for R-B6.

### Packet `W-BUNDLE` (S5)

> Worktree: isolated source branch. Exclusive write paths: `src/vip_fvs/review_bundle.py`, `tests/vip_fvs/test_review_bundle_stream_identity.py`.
> Prerequisites: `P-11`; `S3` merged.
> Task: implement S5 exactly at the existing cross-namespace gate. No new field, no schema change, no new token, no timing parse. Capture R-U1 passing **before** the change.
> Report: as S1, plus the R-U1 before/after transcript and the R-U8 timing-parser call-count evidence.
