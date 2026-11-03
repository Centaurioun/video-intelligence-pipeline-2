# Gate-3 C′ Strict-V1 Temporal Authority Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use Superpowers subagent-driven-development where independent work warrants it, or executing-plans under the repository's rolling-frontier/exclusive-writer rules. Execute task-by-task with RED→GREEN TDD; a plan does not certify or authorize real/archive execution.

**Goal:** Make REAL-scope Gate-3 editorial timestamp claims cite a single versioned, exact, verified, source- and stream-bound temporal authority composed from FFprobe presentation evidence and retained ISO-BMFF source-native bytes, while preserving current V1 refusal for nonzero edit-list origin.

**Architecture:** Owner-approved **C′**: per-fact authority ownership (B) in a narrow composed evidence object (C) with exact bidirectional corroboration (A). A composed artifact is mandatory for REAL plan-scope exact endpoints, validated both at creation and consumption. For V1, `elst.media_time != 0`, unproven probe-index ↔ track-ordinal mapping, unresolvable timing differences and unsupported container facts **refuse** rather than normalize.

**Tech Stack:** Existing Python 3.11/3.14 codebase, integer rational PTS/timebases, FFprobe/FFmpeg on locally **generated** disposable MP4s, ISO-BMFF `stts/ctts/elst/mdhd` parsing, pytest, current `SourceSnapshotStore` and `gate3.refinement` interfaces.

**Spec:** `docs/superpowers/specs/2026-10-25-gate3-dual-temporal-authority-composition-design.md` from design PR #165 at immutable head `91461b69f24461540235cddb49a7d176f2180bbf`, §§1–19, especially §17. **Owner-approved design direction:** C′ with strict origin-zero V1. The PR discussion contains an initial proposed interpretation (comment 6391314845); the subsequent scope clarification governs: approval of the architectural direction does **not** automatically decide every A-1…A-12 low-level change. Treat undetermined spec deltas as `PENDING_DECISION` until disposition is recorded.

## Global Constraints

- Plan branch is based on `main@4144733cc3de04e928bff0c862693474a0a04c11`. Re-fetch current `main`; this SHA is an observation, never a stale fixed write base. Before writing product code, integrate the approved design spec in the controlled main path and refresh the execution worktree.
- Keep pre-integration backup **untouched**: `backup/OWNER-DO-NOT-MODIFY-main-20261024-17edacbe@17edacbe64983ae284f09a8386377200bf538ec3`. No hard reset, git clean, force push or destructive branch/worktree operations.
- Source bytes are immutable; verify no-follow source snapshots, quotas and digests. Measured presentation PTS/timebase, not semantic seconds or nominal FPS, determines exact edit endpoints. Distinguish `MEASURED`, `MATCHED`, `NOT_OBSERVED`, `AUDIO_OBSERVED`, `EDITORIAL_INFERENCE`.
- `src/gate3/container.py`, `src/gate3/refinement.py` (Root G T1–T11) and historic decisions remain unchanged **for strict V1**. No `elst` V2 normalize-and-admit code. Preserve preexisting v1 evidence verification and non-production fake/fixture behavior.
- No protected/real archive source, authentic model inference/download, provider/cloud/egress, real preview or production export, Gate promotion, new SOURCE-AUTH grant framework. Generated test containers only; no implied Owner media operation grant.
- Require exact source-revision SHA/byte count, snapshot manifest, probe digest, selected stream, stream-count, FFprobe version, integer timebase and endpoint membership before publishing composed `MEASURED` claims.
- Superpowers: systematic-debugging for unexpected failures, TDD for every behavior change, exclusive worktrees/writers, independent review and verification before completion. Rolling-frontier task parallelism follows `AGENTS.md` and resource policy; no agent count quota.

## Review Focus: mandatory negative tests

1. **FFprobe 9.x merged `packets_and_frames`** mixed with legacy keys must not silently double count, silently skip frame rows or admit contradictory layouts → Task 1.
2. **Selected global FFprobe stream index** differs from the ISO-BMFF video-track selector in a mixed audio/video/multitrack container → Task 3 refuses unless verified exact mapping.
3. **Nonzero or unsupported `elst` origin, B-frame reorder and VFR** → Task 2/3/4 strict-origin refusal and exact presentation-/decode-order separation.
4. **Tampered evidence/source swap after seal** or old `v1` sealed evidence upgraded to `v2` without a new proof → Task 5 re-verifies at plan/preview consumption.
5. **Terminal endpoint without measured `duration_ts`, complete count and consistent tail** or duplicate presentation ticks → Task 6/7 refuses; no synthesized FPS frame.

## File ownership and task DAG

| Unit | Principal files | Predecessors | Exclusive-writer notes |
|---|---|---|---|
| IT-0 / Task 1 | `src/vip_fvs/real_source_service.py`, `real_preview_verifier.py`, `local_preview.py`, `cli.py`, focused tests | approved design | serialize with IT-7/8; exact reader inventory |
| IT-1/2 / Task 2 | `src/vip_fvs/source_snapshot.py` + snapshot tests | approved design | one owner for v2 shape and VFR basis |
| IT-3 / Task 3 | NEW `src/gate3/composed_temporal.py`, own tests | Task 2's frozen v2 contract | independent of IT-0/preview files |
| IT-4 / Task 4 | `real_source_service.py`, `refinement_adapter.py` + tests | Tasks 1–3 | owns service composition; no shared writes |
| IT-5 / Task 5 | `real_plan.py`, `real_preview_receipt.py` and relevant consumption points + tests | Task 4 | backward-compatible verified v1 receipts |
| IT-6 / Task 6 | `real_preview_verifier.py` + tests | Tasks 2,4,5 | serial after verifier Tasks 1/7/8 |
| IT-7/8 / Task 7 | `real_preview_verifier.py`, `local_preview.py`, tests | Task 1 | can be independent conceptual reviews, **not simultaneous file writers** |
| IT-9 / Task 8 | Gate-3 pilot documentation | approved strict V1 | parallel with code, no shared contracts |

Dependency graph: Task 1 and Task 2 begin independently; Task 3 after Task 2's interface freeze; Task 4 after Tasks 1/2/3; Task 5 after Task 4; Task 6 after Task 5; Task 7 can run after Task 1 but must serialize verifier writes; Task 8 can run independently. A separate pilot corpus-separation mechanism and audio-capable preview **are not included**.

## Task 0 — Fresh main/spec integration and owned worktree (serialized)

**Files:** No product-code changes.

- [ ] **Step 1:** Fetch `origin/main`; read approved design from PR #165 immutable SHA and Owner decision; verify current backup head equals expected hash. Record `BASE_SHA` and all current file ownership before work.
- [ ] **Step 2:** Ensure design/plan are available as immutable references in the implementation worktree; if spec is not merged, request controlled integration first, **do not implement from an unsigned handoff copy**. Review §17 A-1…A-12 against the Owner's *actual* C′/strict-V1 approval and explicitly log which detailed choices are already dictated by higher authority versus require further Owner/contract decisions.
- [ ] **Step 3:** Create isolated branch/worktree through Superpowers using-git-worktrees, and assign exactly one writer per touched module. Confirm no pending unrelated local changes.
- [ ] **Step 4:** Reproduce baseline `PYTHONPATH=src:experiments:scripts python -m pytest tests/gate3 tests/vip_fvs -q` and capture actual count/environment. Do not assume historic 1072 is the current baseline.

## Task 1 — IT-0 FFprobe merged-payload normalization

**Files:** Create `src/vip_fvs/ffprobe_frame_rows.py` if the existing path has no shared internal helper; modify `real_source_service.py`, `real_preview_verifier.py`, `local_preview.py`, `cli.py`; add focused `tests/vip_fvs/unit/test_ffprobe_frame_rows.py` and existing reader regression tests.

**Interfaces:** `def normalized_frame_rows(payload: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]` produces ordered **frame-only** records from either legacy `frames` or `packets_and_frames` with `type=="frame"`. Packet rows never become presentation frame members; preserve occurrence count and alias precedence.

- [ ] **Step 1 (RED):** Test legacy layout 60 rows, merged layout 60 rows, mixed packet/frame payload 60 frames, both-layout agreement and disagreement; assert duplicate frame PTS remain duplicates, malformed entries refuse. Run focused tests and capture actual failures.
- [ ] **Step 2:** Implement the single canonical extractor with stable refusal codes and bounded payload processing, then migrate **all** known readers: `_observed_pts`, `_frame_presentation_pts`, `_evidence_facts`, `local_preview` and `cli`. Do not change current precedence `best_effort_timestamp` → `pts` → `pkt_pts`.
- [ ] **Step 3 (GREEN):** Run focused tests and synthetic ffprobe 9.x fixtures; compare 60/45/40 expected presentation members where applicable, never assert DTS from frame `pkt_dts`.
- [ ] **Step 4:** Run relevant preview/real-source tests, review and commit only task-owned changes.

## Task 2 — IT-1/IT-2 snapshot temporal binding v2

**Files:** Modify `src/vip_fvs/source_snapshot.py`, snapshot unit tests. Do not touch `src/gate3/container.py` or `refinement.py`.

**Interfaces:** Preserve `SourceSnapshotStore.bind_temporal_authority(snapshot, *, selected_stream_index:int, declared_vfr:bool, declared_reordering:bool)` and `verify_temporal_authority(snapshot,evidence)` calls. Add additive **schema_version 2** binding fields and compatible v1 read/verify path. Data fields: `nb_frames`, `duration_ts`, `duration_consistency`, `tail_duration_ticks`, `composition_offsets`, `has_b_frames`, `presentation_origin_ticks`, `stream_handler`, `stream_identity_derivation`.

- [ ] **Step 1 (RED):** Old schema-v1 bound evidence verifies without upgrade; v2 fields are validated and sealed; absent, mismatched or tampered fields refuse; nonzero origin refuses; preverified snapshot path is covered.
- [ ] **Step 2:** Add v2 evidence and exact own-fact VFR validation from presentation intervals; distinguish decode-order evidence from presentation ordering and reject unsupported claims. Strict origin-zero means no new `elst` admission.
- [ ] **Step 3 (GREEN):** Locally generated no-B, VFR, zero-origin B-frame and nonzero-origin negative fixtures; unit and integration regressions verify v1 compatibility and precise refusal.
- [ ] **Step 4:** Commit reviewed source/tests and publish the frozen v2 interface contract to Task 3.

## Task 3 — IT-3 pure composed temporal authority

**Files:** Create `src/gate3/composed_temporal.py`, `tests/gate3/unit/test_composed_temporal.py`.

**Interfaces:** Define `compose_temporal_authority(...)` accepting *verified* probe and snapshot-binding facts, explicit mapping evidence, exact selected stream/revision and declarations. Produces sealed `vip_fvs.composed_temporal_authority.v1` record and deterministic `evidence_sha256`; implement `verify_composed_temporal_authority(...)` consuming the same source-linked inputs. Do not construct `MEASURED` claims from caller assertions.

- [ ] **Step 1 (RED):** Each of the 20 spec §11 `TEMPORAL_AUTHORITY_*` reason codes has one constructive refusal test; acceptance tests prove exact PTS multiset, order, timebase, byte/source/stream and zero-origin equality.
- [ ] **Step 2:** Implement per-fact `owner`, `state`, `value`, `corroboration`; explicit `NOT_APPLICABLE` and `NOT_OBSERVED` states; source-to-track mapping only with evidence, otherwise refusal. No float normalization, nominal-FPS math, or silent missing-record acceptance.
- [ ] **Step 3 (GREEN):** Run pure-unit tests and synthetic container playback-independent measurements; verify deterministic digest and tamper refusal.
- [ ] **Step 4:** Review and commit the pure module before wiring service code.

## Task 4 — IT-4 mandatory composition at REAL source preparation

**Files:** Modify `src/vip_fvs/real_source_service.py`, `refinement_adapter.py` and focused tests.

**Interfaces:** `prepare_real_source(request: RealSourceRequest) -> RealSourcePreparationResult` remains public. Compose **after** bounded snapshot capture/verification and FFprobe source-digest binding, **before** the published exact endpoint/refinement claim. Preserve existing Root-G 2-boundary/1-timebase checks and add full-stream corroboration.

- [ ] **Step 1 (RED):** A REAL path where probe/refinement share endpoints but diverge internally must now refuse; unproved mixed-stream selector, wrong source SHA/revision or timebase, and nonzero edit origin must refuse *before* a genuine REAL measured receipt.
- [ ] **Step 2:** Wire mandatory composition, requiring source/revision/stream identity and full enumeration match; ensure source binding happens before using any exact interval. Preserve synthetic/fixture paths and source immutability.
- [ ] **Step 3 (GREEN):** Focused tests + bounded generated-MP4 no-B/VFR cases; assert resulting evidence digest and unchanged original V1 source behavior where legally accepted.
- [ ] **Step 4:** Independent security/reliability review and commit.

## Task 5 — IT-5 consumption-time evidence re-verification

**Files:** `src/vip_fvs/real_plan.py`, `real_preview_receipt.py`, applicable load/preview consumption call sites + tests.

**Interfaces:** Additive composed-authority ref and digest in the REAL plan/receipt record; exact v1 plans remain readable **as historic evidence only**, not automatically newly eligible for REAL claims. At plan build, load, preview and receipt consumption, verify canonical seal and remeasure/bind the named retained source where claim eligibility requires it.

- [ ] **Step 1 (RED):** Change `pts_ticks`, source SHA, stream, `snapshot_manifest_sha256`, or provenance after seal; reusing stale plan or different source must refuse before any render. Historical v1 fixture receipt remains readable, but cannot masquerade as composed REAL proof.
- [ ] **Step 2:** Add the bounded evidence field, verify it at plan creation and all downstream eligibility boundaries; prevent nonmember-end `refine()` silent tail reinterpretation via explicit enumeration membership precondition.
- [ ] **Step 3 (GREEN):** Tests for canonical digest, tamper/no-output, cross-scope refusal, v1 read-only historic compatibility; no production eligibility escalation.
- [ ] **Step 4:** Independent reviewer checks output and source immutability; commit.

## Task 6 — IT-6 measured terminal interval (G-4 plumbing)

**Files:** `src/vip_fvs/real_preview_verifier.py` + tests; v2 binding supplied from Tasks 2–5.

- [ ] **Step 1 (RED):** Terminal `end==duration_ts` with full frame count, positive tail, origin zero and consistency MATCH is eligible with explicit `DERIVED_NOT_OBSERVED` extent; missing/inconsistent facts still refuse; last-frame extent remains unknown.
- [ ] **Step 2:** Carry measured snapshot tail metadata through composed evidence; replace unconditional `STREAM_TAIL_NOT_SUPPORTED` only for valid strict-V1 terminal paths.
- [ ] **Step 3 (GREEN):** Generated no-B and zero-origin B-frame cases; VFR, wrong duration, wrong count, nonmember end and contradictory tail rejection.
- [ ] **Step 4:** Run applicable regressions, review, commit.

## Task 7 — IT-7/IT-8 independent correctness fixes (serialize verifier writer)

**Files:** `real_preview_verifier.py`, `local_preview.py` + tests; no shared writes alongside Tasks 1/6.

- [ ] **Step 1 (RED):** duplicate PTS or stream-row discrepancies previously admitted by render but rejected by verifier must consistently fail; zero/absent canonical payload provenance fields must never be skipped.
- [ ] **Step 2:** Preserve multiplicity (no `sorted(set(...))`), unify explicit stream admission and make provenance checks load measured source/container facts or refuse.
- [ ] **Step 3 (GREEN):** Legacy + merged-layout fixtures, mixed-track refusal, tampered source digest, synthetic preview acceptance and negative branches.
- [ ] **Step 4:** Run focused/full Gate-3 and vip_fvs suites and commit once verifier ownership is exclusive.

## Task 8 — IT-9 pilot-spec and final integration certification

**Files:** Update Gate-3 pilot spec/readiness memo only; create result report under `docs/agent-runs/`. Do not alter frozen historic design.

- [ ] **Step 1:** Document strict zero-origin admissibility; generated fixture `-avoid_negative_ts make_zero` examples as reproducibility guidance, not a universal editor-export requirement.
- [ ] **Step 2:** Verify test plan and exact evidence from Tasks 1–7, including 20 refusal cases, v1 preservation, no protected sources, no actual human/audio observation, no Gate promotion.
- [ ] **Step 3:** Run `PYTHONPATH=src:experiments:scripts python -m pytest tests/gate3 tests/vip_fvs -q` on integration candidate; run existing smoke checks; capture command, exit, test count, Python version and full source/commit hash.
- [ ] **Step 4:** Request independent code review, resolve blocking findings, publish immutable candidate + PR targeting current main; **do not merge automatically**. Update the WBS only on independently verified claims after controlled integration.

## Approval and result discipline

- **APPROVED DESIGN DIRECTION:** C′ composed authority, exact per-fact corroboration, and **strict origin-zero V1**. The earlier Owner-facing recommendation also prioritized addressing FFprobe 9.x shape defects, proven stream mapping or refusal, and consumption-time verification. These are design goals, **not** blanket authority for every implementation signature, failure-code name, evidence-schema version or cross-contract change in §17.
- **DETAILED DECISION GATE:** Before implementing a task that changes an existing frozen Root-G contract or evidence schema, resolve the applicable §17 A-1…A-12 item through an explicit owner/contract-owner disposition. In particular A-1 (scope/placement), A-2/3 (v2 semantics/schema), A-4/5/6 (mandatory path, codes/module), A-7 (mapping basis), A-8/11 (standalone verifier fixes) and A-12 (consumption-time semantics) must not be silently marked owner-approved solely from the user's high-level C′/V1 acceptance. A-9's **strict V1 vs origin-shifting V2 choice** is settled in favor of strict V1; V2 remains outside scope. If a detailed item follows unambiguously from preexisting higher-authority spec, cite that authority explicitly.
- **NOT APPROVED:** origin-shifting V2 `elst`, real media/model/provider/export, Gate promotion, unproven track mapping, corpus-separation registry, audio rendering subsystem.
- **PENDING:** any detailed A-item still needing a decision, newly encountered deviation from this design, specific production/pilot operations, and Gate-independent corpus/audio policy decisions. Do not convert PENDING to DONE merely to unblock a slot.
- Distinguish `IMPLEMENTED`, `VERIFIED_NO_CHANGE`, `DESIGNED_PENDING_APPROVAL`, `BLOCKED`, `NOT_OBSERVED`. One PR may contain independent owner-approved source tasks only with exact owner/test/evidence boundaries.
