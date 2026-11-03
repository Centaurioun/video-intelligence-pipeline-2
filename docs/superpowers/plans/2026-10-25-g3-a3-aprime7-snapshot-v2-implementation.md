# Gate-3 A-3 A′-7 Snapshot Temporal Evidence v2 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans for controlled single-writer execution (or subagent-driven-development only when real independent ownership exists). Steps use checkbox syntax; follow repository rolling-frontier rules rather than spawning artificial parallel writers.

**Goal:** Implement an additive 21-key v2 snapshot temporal evidence with seven new retained-byte/derived facts, presentation-based VFR classification, v1 historical compatibility, and safe dual-version verification.

**Architecture:** Keep `SourceSnapshotStore.bind_temporal_authority()` as the exact V1 entry point. Add `bind_temporal_authority_v2()`, a V2 typed binding/evidence projection and version-aware verifier; both derive from retained snapshot bytes via the existing single materialization and ISO-BMFF parser. Correct VFR basis only for V2; never silently change legacy V1 creation/verification.

**Tech Stack:** Python 3.11/3.14, pytest, `gate3.fixturegen.build_mp4`, `gate3.container.parse_iso_bmff_timing_bytes`, hashlib/canonical JSON, AST for static guard checks.

**Spec:** `docs/decisions/2026-10-25-g3-a3-aprime7-bounded-owner-decision.md`; background `docs/superpowers/specs/2026-10-25-gate3-dual-temporal-authority-composition-design.md` and `docs/agent-runs/2026-10-25-g3-temporal-binding-wave3/a3-decision-proposal.md`.

## Global Constraints

- Frozen planning base: `main@cb5468b320f554aa08cc767c5cfe45e63126416a`; re-fetch main and compare exact tree/ownership before starting; never assume it has not moved.
- This decision/plan lives on the isolated `docs/g3-a3-a-prime-7-decision-plan-20261025` branch until reviewed/integrated. If absent on current `main`, the executor must fetch it **read-only from a controller-pinned immutable planning commit**, verify its two blobs/contents, and implement on a separate clean source branch from current approved main. Do not silently merge the planning branch as setup.
- Owned production path: **only** `src/vip_fvs/source_snapshot.py`. Owned tests: new `tests/vip_fvs/unit/test_source_snapshot_temporal_v2.py`; focused modifications to `tests/vip_fvs/adversarial/test_temporal_vfr_basis_divergence.py`, `test_source_snapshot_temporal_safety.py`, and when strictly necessary `test_temporal_evidence_v1_matrix.py`. Coordinate other test writers; do not edit shared Gate-3 verifier/producer files.
- Do not touch `src/gate3/container.py`, `src/gate3/refinement.py`, `src/gate3/temporal.py`, `src/vip_fvs/real_source_service.py`, preview/verifier, Gate-0, frozen reference packs, or canonical main.
- No archive, real/protected media, model/provider/network/MPS work, real preview/export, Gate promotion, backup mutation, unsafe cleanup or force operations.
- Preserve ADR-0003 `DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT=DISABLED_BY_OWNER` rather than recreating administrative development grants.
- v1 exact body (13 keys + digest = 14) and original method signature remain; already-authorized A-9 strict nonzero-origin refusal is not rolled back.
- v2 exact body (13 existing keys + seven additions = 20) plus digest = 21. `composition_offsets` is decode-order-aligned and negative integers are allowed.
- New v2 VFR predicate uses consecutive sorted presentation `pts_ticks` deltas only; no tail or nominal FPS. Existing reordering predicate remains unchanged, despite recorded limitations. Do not change A-7 stream namespace or A-12 duration/tail acceptance.
- Existing strict duration mismatch `xfail` remains **xfail**: v2 seals `duration_consistency="MISMATCH"` but producer does not reject solely for that status.
- No new stable `TEMPORAL_AUTHORITY_*` code names; future v2-requiring consumers remain outside this task.

## Review Focus — five most dangerous negative cases

1. Historical valid v1 receipt with presentation/decode divergence must still verify with *legacy predicate*; v1 relabelled to 2 must fail with the historically pinned binding-mismatch code. Covered Task 1/3.
2. Synthetic VFR where `stts` decode deltas disagree with sorted PTS deltas must be classified **only** by presentation on new v2 creation, in both directions; v1 remains unchanged. Covered Task 4.
3. Signed `ctts` offsets must preserve decode-index association, multiplicity and exact integer equality `sort(dts+ctts)==pts`; invalid offset length/type/mismatch must refuse. Covered Task 2.
4. Snapshot source/revision/digest tamper, bogus evidence SHA, wrong track handler/stream ordinal and nonzero edit-list origins must fail closed. Covered Task 2/3/5.
5. A static `duration_ts` test amendment must accept legitimate evidence-key serialization but reject nominal-FPS positioning and unprovenance; behavioral negative cases, not comments/names, prove source identity. Covered Task 5.

---

## Task 0 — Baseline and exclusive writer verification

**Files:** No source edits.

- [ ] Step 1: Read `AGENTS.md`, decision/spec/plan, original `src/vip_fvs/source_snapshot.py` and pinned tests at the exact base. Confirm A-7 and Gate-0 in-flight lane ownership does not overlap; bind own isolated clean worktree and unique branch.
- [ ] Step 2: Run `PYTHONPATH=src:experiments:scripts python -m pytest tests/gate3 tests/vip_fvs -q` on the clean base. Capture actual exit, pass/xfail counts. This is baseline evidence, not an implementation result.
- [ ] Step 3: Confirm v1 signature and 14-key evidence using tests, and record two VFR strict-xfails and one A-12 duration strict-xfail. Do not dismiss these as accidental failures.

## Task 1 — Pin v1 historical replay and add V2 public contract (TDD)

**Files:**
- Create `tests/vip_fvs/unit/test_source_snapshot_temporal_v2.py`
- Modify `src/vip_fvs/source_snapshot.py`

**Interfaces:**
- Consume `VerifiedSourceSnapshot`, existing `VerifiedSourceTemporalBinding`.
- Produce new `VerifiedSourceTemporalBindingV2` with `.as_evidence() -> dict[str, Any]`.
- Produce `SourceSnapshotStore.bind_temporal_authority_v2(snapshot, *, selected_stream_index: int, declared_vfr: bool, declared_reordering: bool) -> VerifiedSourceTemporalBindingV2`.

- [ ] Step 1 (RED): In new tests assert `bind_temporal_authority_v2` exists; for origin-zero `build_mp4(sample_deltas=(40,40,40,40), media_timescale=1000)`, its evidence has exactly the seven additional names and `schema_version==2`, `len(evidence)==21`; expected initial failure is missing method, not fixture failure. Assert V1 old signature and historical output stay exactly 14 keys.
- [ ] Step 2: Run `PYTHONPATH=src:experiments:scripts python -m pytest tests/vip_fvs/unit/test_source_snapshot_temporal_v2.py -q`. Capture actual RED.
- [ ] Step 3 (GREEN): Implement additive frozen V2 binding class and V2 method. Use `self.verify(snapshot)` before and after; existing `_read_snapshot_bytes`, box bounds, and one `parse_iso_bmff_timing_bytes` call. Never accept input PTS/duration/CTTS from caller; preserve digest domain (`json.dumps(...,sort_keys=True,separators=(',',':'),ensure_ascii=False)`). Shared private helpers allowed only if V1 exact behavior/shape/error precedence remains pinned by tests.
- [ ] Step 4: Run new focused tests and existing `test_source_snapshot_temporal_single_read.py` + `test_source_snapshot_temporal_origin_refusal.py`. Confirm GREEN, verify V1 14-key and V2 21-key shapes.
- [ ] Step 5: Commit one focused source+test slice on isolated branch.

## Task 2 — Seal seven facts and ensure exact CTTS↔DTS pairing (TDD)

**Files:**
- Modify `src/vip_fvs/source_snapshot.py`
- Extend `tests/vip_fvs/unit/test_source_snapshot_temporal_v2.py`

**Interfaces:** Existing V2 method/binding from Task 1; no extra API.

- [ ] Step 1 (RED): Generate fixtures with signed offsets (including negative values and duplicate sorted PTS) using `gate3.fixturegen.build_mp4`. Assert `len(v2.composition_offsets)==len(v2.dts_ticks)`; `sorted(d+o for d,o in zip(dts, offsets)) == list(v2.pts_ticks)`. Assert signed negatives preserved, evidence JSON serializable, seven exact field types, strict origin-zero.
- [ ] Step 2: Add parser-result monkeypatch negative controls: absent/wrong-typed `duration_ts`, missing/invalid `duration_consistency`, nonpositive tail, bool offset, wrong offset length, offset/PTS disagreement, wrong `stream_handler`, absent/invalid `stream_identity_derivation`, selected ordinal mismatch, wrong source SHA. Assert existing appropriate `SNAPSHOT_*` refusals or `EDIT_LIST_ORIGIN_NOT_APPLIED` rather than inventing new namespace.
- [ ] Step 3: Run RED new test selections; implement strict `type(x) is int`/`type(x) is str` guards and exact array equality. For `duration_consistency`, validate allowed `MATCH/MISMATCH` and exact consistency with `duration_ts == pts_ticks[-1]+tail_duration_ticks`; **do not require MATCH to bind**.
- [ ] Step 4: Run focused tests GREEN; check single source-byte materialization; commit.

## Task 3 — Dual-version verifier, legacy refusal precedence, serialization replay (TDD)

**Files:**
- Modify `src/vip_fvs/source_snapshot.py`
- Extend `tests/vip_fvs/unit/test_source_snapshot_temporal_v2.py`

**Interfaces:** `verify_temporal_authority(snapshot, evidence: Any) -> VerifiedSourceTemporalBinding | VerifiedSourceTemporalBindingV2`; unchanged parameters.

- [ ] Step 1 (RED): Persist v1+v2 evidence through `json.dumps/loads`, re-verify each against retained bytes. Test v1 only rebinds v1, v2 only rebinds v2, and an unknown/mixed key set refuses.
- [ ] Step 2 (RED): Pin previously observed refusal codes: v1 plus one V2 field ⇒ `SNAPSHOT_TEMPORAL_EVIDENCE_FIELDS_INVALID`; unchanged 14-key V1 evidence with `schema_version:2` only ⇒ `SNAPSHOT_TEMPORAL_EVIDENCE_BINDING_MISMATCH`. Tamper source bytes/manifest/revision/PTS/offsets, recompute evidence digest without changing measured bytes, or change timebase ⇒ exact refusal.
- [ ] Step 3: Implement version dispatch **before** version-specific field-set gate, with a narrow compatibility branch for the pinned relabelled-V1-only case. Verify each version against its own remeasured retained-byte binding and exact canonical body/digest. Reject unknown versions and mixed key sets; never auto-upgrade V1.
- [ ] Step 4: Run focused integration/safety/successor tests and new tests GREEN; commit.

## Task 4 — IT-2 presentation VFR only in v2; consume existing RED (TDD)

**Files:**
- Modify `src/vip_fvs/source_snapshot.py`
- Modify `tests/vip_fvs/adversarial/test_temporal_vfr_basis_divergence.py` (sole writer for this test file)
- Extend `tests/vip_fvs/unit/test_source_snapshot_temporal_v2.py`

**Interfaces:** `bind_temporal_authority_v2`, unchanged v1 entry point.

- [ ] Step 1: Preserve the existing measured fixture vectors in `test_temporal_vfr_basis_divergence.py`. Move the **two corrected expectations** to call `bind_temporal_authority_v2`; retain separate explicit green assertions that legacy V1 still follows DTS+tail. Initially run V2 assertions RED (or fail because missing V2 predicate), not `XPASS(strict)`.
- [ ] Step 2: Implement v2 `observed_vfr = len(set(b-a for a,b in zip(pts,pts[1:])))>1` on exact measured presentation ticks, without folding in terminal tail. Keep v1's `dts`+tail code/predicate unchanged. Keep existing `observed_reordering` predicate unchanged in this scope.
- [ ] Step 3: Convert the two satisfied IT-2 strict-xfails to ordinary passing V2 assertions **only after observing RED and GREEN**; do not delete the associated divergence evidence. The third duration-policy strict-xfail stays strict-xfail.
- [ ] Step 4: Run focus and Gate-3/VIP-FVS suites; commit.

## Task 5 — D-4 structural + behavioral guard; final adversarial check (TDD)

**Files:**
- Modify `tests/vip_fvs/adversarial/test_source_snapshot_temporal_safety.py`
- Extend `tests/vip_fvs/unit/test_source_snapshot_temporal_v2.py`
- `src/vip_fvs/source_snapshot.py` only if actually needed to address a demonstrable failed negative test.

**Interfaces:** No new exported API.

- [ ] Step 1 (RED): Write structural/AST tests to permit exactly the measured-result lookup and closed evidence-key emission positions for `duration_ts`, while retaining `r_frame_rate`/`avg_frame_rate` ban and forbidding nominal-FPS position calculations. Keep `nb_frames` ban in unchanged surfaces. Add synthetic source-mutation tests that defeat superficial line/comment/variable-name allowlists.
- [ ] Step 2 (RED): Run targeted mutation controls for fabricated `duration_ts` or offsets, forged evidence hashes, tampered snapshot bytes, bool-as-int, unverified stream handler, and one-sample/duplicate PTS boundaries. Make the existing static guard fail for forbidden source forms and pass legal serialization; do not claim AST alone proves actual provenance.
- [ ] Step 3: Change **only** the relevant source-token invariant for `vip_fvs.source_snapshot`, with no broad test weakenings; correct minimal product issues revealed by legitimate negatives. Re-run all targeted tests.
- [ ] Step 4: Full `PYTHONPATH=src:experiments:scripts python -m pytest tests/gate3 tests/vip_fvs -q` and `bash scripts/verify-workspace.sh`; compare any environmental failures with the base instead of hiding them. Secret scan, clean worktree and exact diff review. Verify Python 3.11/3.14 via GitHub CI once PR exists. Do not claim this selected smoke implies full-suite coverage.
- [ ] Step 5: Commit, request bounded code review, open an implementation PR against current main with exact tests/logs/candidate SHA, flag any stale-base/overlap. **Do not merge** without the usual separate integration authorization.

## Scope/decision handoff

- D-5 imposes future *consumer* refusal responsibility but the stable refusal-code name remains A-5 PENDING; do not fake readiness by adding a guessed code.
- A-7 from the separate Owner-launched task is refusal-only; a source proof of FFprobe global stream→ISO-BMFF trak ordinal is still a separate contract decision.
- IT-8 remains PARKED_BLOCKED on mapping and fixture-chain snapshot custody, not on missing `duration_ts` or v2 provenance duplications.
- Duration-tail `MISMATCH` acceptance/refusal remains pending A-12 and its strict-xfail intentionally persists; no production eligibility escalation.
- If review finds V1 behavior, frozen code names, source snapshot shape or cross-file ownership must change to satisfy this plan: **STOP** and request narrow contract-owner disposition rather than silently widening scope.

## Six-Cycle execution acceptance

1. Pin live `BASE_SHA` and baseline tests; 2. audit authority and owned paths; 3. select minimal dual-version mechanism; 4. execute test-first single-writer tasks; 5. adversarial negative/compatibility review; 6. independently verify GitHub candidate head/CI and record next dependency frontier. Only verified Git evidence qualifies for implementation/merge statements.
