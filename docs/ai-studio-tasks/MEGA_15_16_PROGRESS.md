# MEGA-15 + MEGA-16 Progress, Post-CI Repair & Six-Cycle Engineering Ledger (`LAB-MEGA-15-16-v1.0.0`)

- **Program Version:** `LAB-MEGA-15-16-v1.0.0` (Post-CI Critical Repair & Hosted CI Recovery)
- **Governing Specification:** `docs/ai-studio-tasks/MEGA_15_16_GATE3_OFFLINE_PREPARATION_PROGRAM.md`
- **Target Repository:** `Centaurioun/video-intelligence-pipeline-2` (`LAB` repository, branch `main`)
- **Original Canonical Baseline (READ ONLY):** `Centaurioun/video-intelligence-pipeline` `main@592952daf475b1bbae2eebdee64d992c1a744f08`
- **Last Known Successful LAB Baseline:** `e5974d9730d0ef85af5dc6fa16445e93b8c9941d` (building on `MEGA-08..14` reference `9bdd810bf14c93ed1f77243325beaa6b37b3e97d`)
- **Diagnosed Failing LAB Commit:** `2d7605c3169e78503fe3908ad251e79171b1e142` (GitHub Actions Run ID `41856186752` failed on Python 3.11 and Python 3.14)
- **AI Studio Workspace Git Metadata:** `workspace_git_sha=NOT_OBSERVED` (ZIP-imported workspace without `.git`)
- **Local Verification Status:**
  - `python3 -m compileall -q src experiments tests` -> `PASS`
  - Exact Git blob SHA check for 6 `src/gate0/media/*.py` files -> `PASS` (all 6 match `e5974d9730d0ef85af5dc6fa16445e93b8c9941d` byte-for-byte)
  - In-process `unittest`/module verification (`PYTHONPATH=src python3` executing all test functions in `tests/vip_lab/test_mega08..16`) -> `PASS` (`59/59` test functions across 10 modules)
  - Hosted GitHub Actions CI (`Python 3.11` & `Python 3.14`) -> `PENDING_NEXT_GITHUB_PUSH`

---

## 1. Root Cause Analysis of Failed GitHub Actions Run `41856186752` (`2d7605c3169e78503fe3908ad251e79171b1e142`)

### Finding A — Six `src/gate0/media/*` Files Missing from Published Git Trees
- **Verified:** The LAB `.gitignore` line 26 has the unanchored `media/` pattern, and `git check-ignore --no-index` matches `src/gate0/media/decode.py`. The published commit `7ea814d5c4626ed6b371c01f282c8a9b0138ffa0` deletes all six paths; the intact reference `e5974d9730d0ef85af5dc6fa16445e93b8c9941d` contains the expected blobs listed below.
- **Not established:** Whether Google's ZIP export/publisher evaluates `.gitignore` without the Git index, or whether that mechanism caused the deletions. Files present in an AI Studio workspace, files ignored by a pattern, files exported, and paths in the GitHub commit tree are separate states. The publisher's exact behavior remains `NOT_OBSERVED`.
- **Workspace/Reference Blob Verification:** The six blobs in the intact Git reference match the required IDs:
  - `src/gate0/media/__init__.py`: `b1198560f5c8582b8be8725fed9412597ca08e96`
  - `src/gate0/media/decode.py`: `a3c7efad5fdc0c24e7f592512ef176e10e95f128`
  - `src/gate0/media/probe.py`: `d95b15505550f54263463e6bcbb9681f00620f17`
  - `src/gate0/media/proc.py`: `244706e9c198ab25afad5894a977cc1a31b39755`
  - `src/gate0/media/source_guard.py`: `9b0a7a64e7b163c94ad5ed62ba16bfedda99c398`
  - `src/gate0/media/tool_identity.py`: `056447631d477f57776c4db5e75cb8bad25b8ebd`
- **Narrow Safeguard:** This repair explicitly unignores only these six source files under `src/gate0/media/`, leaving `media/` ignored everywhere else. CI still needs the commit tree and the regression workflow to detect omissions; `.gitignore` cannot prevent a publisher from explicitly deleting tracked paths.

### Findings B–F — Upstream Contract, Import, Signature, and Lineage Repairs
1. **`gate3.rational` & `gate3.pts` (`src/vip_lab/mega15/temporal_preflight.py`):**
   - `TimeBase` and `Rational` are imported from `gate3.rational` (not `Timebase` from `gate3.pts`).
   - `PtsTable(time_base=tb, ticks=pts_ticks)` is constructed with its exact keyword signature.
   - Duplicate PTS disambiguation uses `table.ordinal_of(tick, occurrence=occurrence)` rather than passing an unsupported `occurrence=` keyword to `resolve_start` / `resolve_end`.
2. **`gate3.temporal` (`src/vip_lab/mega15/temporal_preflight.py`):**
   - `resolve_start(table, req_start)` and `resolve_end(table, req_end)` are called with 2 positional arguments and unpacked via `.requested_ticks`, `.resolved_ticks`, and `.policy`.
   - `classify_vfr(table, declared_rate=declared_rate)` is unpacked as a 4-tuple `(is_vfr_flag_str, period_rational, basis_str, deviation)`.
   - `subdivide_on_discontinuity(table, start_ticks, end_ticks)` is unpacked as `(parts_tuple, gaps_list)`.
   - `tail_end(table, last_delta_ticks=..., rate_regime="uniform")` is called with required keyword arguments and unpacked via `TailEnd.end_ticks` and `TailEnd.basis`.
3. **`gate3.refinement_request` (`src/vip_lab/mega15/temporal_preflight.py`):**
   - `RefinementRequest` is constructed with its exact fields: `(request_id, candidate_assertion_ref, source_revision_id, source_locator, expected_source_sha256, selected_stream_index, requested_start_pts, requested_end_pts, producer_attempt_id, idempotency_key, expected_timebase=(num, den))`.
4. **`gate3.editorial` & `gate3.plan` (`src/vip_lab/mega15/editorial_handoff.py`):**
   - `EditorialDecision` raises `ModelToolPrincipalError` (a subclass of `TypeError`) for non-human principals (`"MODEL"`, `"TOOL"`) and requires `principal_kind in ("human", "SYNTHETIC_HUMAN")` with `principal_id`, `review_bundle_id`, `action`, `created_at_utc`, and `rationale`. `validate_principal_boundary` catches `(ModelToolPrincipalError, TypeError, ValueError)` and wraps into `VipLabError("ERR_MEGA15_INVALID_PRINCIPAL", ...)`.
   - `EditPlanRevision` is constructed with its exact signature `(plan_id, plan_revision, placements, pinned_refinements, pinned_decisions)` to verify `plan_probe.export_eligible is False`.
5. **`vip_fvs.real_preview_receipt`, `gate3.qc`, & `vip_lab.mega13` (`src/vip_lab/mega16/*.py`):**
   - `src/vip_fvs/real_preview_receipt.py` exports `_FIELDS`, `SCHEMA`, and `SCOPE` (aliased in `render_preflight.py` as `REAL_PREVIEW_RECEIPT_REQUIRED_FIELDS`, `RECEIPT_SCHEMA_VERSION`, `PREVIEW_NON_PRODUCTION_MARKER`).
   - `src/gate3/qc.py` exports `QCReport` and `bare_pass_is_insufficient` (used in `qc_requirements.py` instead of non-existent `TechnicalQcReport` / `EditorialQcReport`).
   - `src/vip_lab/mega13` exports `CANONICAL_RELEASE_BLOCKER_CODES` and `build_release_blocker_summary` (which returns a `dict[str, Any]` containing `"release_blockers"`, `"summary_digest"`, `"export_status"`, `"production_export_authorized"`, and `"preview_eligible"`).
6. **`vip_lab.common` (`VipLabError`, `SyntheticContextMarker`, `ReadinessPacket`):**
   - Every `VipLabError(code, message)` call supplies both required positional arguments `(code, message)`.
   - `SyntheticContextMarker.create()` is used consistently.
   - `ReadinessPacket` is constructed with `(packet_id, stage_id, status=ReadinessStatus.BLOCKED, summary=..., blockers=..., evidence_state="NOT_OBSERVED", synthetic_only=True, execution_authorized=False)` and accessed via `.summary`, `.status.value`, `.blockers`, `.synthetic_only`, and `.execution_authorized`.
7. **Truthful Duplicate Preservation (`src/vip_lab/mega15/lineage.py`):**
   - Removed the false-positive `or len(queue.items) >= 1` condition. `duplicate_occurrence_paths_preserved` is `True` if and only if the upstream candidate queue actually contains at least one content digest with `>= 2` distinct `source_locator` paths AND all distinct paths are preserved 1-to-1 downstream (`False` when no duplicate occurrences exist). Similarly, `duplicate_query_texts_preserved` is `True` if and only if at least one normalized `query_text` appears across `>= 2` distinct `query_id`s upstream AND all distinct `query_id`s are preserved downstream (`False` when all query texts are unique).
8. **Safe Dry-Run CLI (`src/vip_lab/mega16/cli.py`):**
   - Fixed `main(argv=None)` so `sys.argv[1:]` is parsed when `argv is None` instead of iterating over `sys.argv[0]`.
   - Enforced parent-traversal refusal (`..`), media extension refusal (`.mp4`, `.mov`, `.mkv`, `.avi`, `.webm`, `.wav`, `.mp3`, `.aac`, `.flac`, `.m4a`, `.mxf`, `.ts`), symlink refusal, existing-file refusal, and atomic `os.open(..., os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)` write.

---

## 2. Six-Cycle Repair Summary

| Cycle | Focus | Outcome |
| --- | --- | --- |
| **Cycle 1** | Root-cause inventory & 6-file `src/gate0/media/*` SHA verification | Confirmed all 6 `src/gate0/media/*` files match exact Git blob SHAs from `e5974d9730d0ef85af5dc6fa16445e93b8c9941d`; identified `.gitignore` `media/` export trap and cataloged all upstream signature mismatches. |
| **Cycle 2** | `MEGA-15` temporal, PTS, VFR, discontinuity, stream-tail (`IT-6`), and stream-identity (`A-7`) repair | Aligned `temporal_preflight.py` with `gate3.rational`, `gate3.pts`, `gate3.temporal`, `gate3.refinement_request`, `gate3.refinement`, and `gate3.stream_identity`. |
| **Cycle 3** | `MEGA-15` editorial principal, revision chain (`v1 -> v2 -> v3`), and lineage repair | Aligned `editorial_handoff.py` and `lineage.py` with `gate3.editorial`, `gate3.plan`, `vip_lab.mega09..13`; fixed duplicate-occurrence and duplicate-query-text boolean reporting to be strictly truthful. |
| **Cycle 4** | `MEGA-16` declarative render preflight, QC requirement manifest, release refusal & CLI repair | Aligned `render_preflight.py`, `qc_requirements.py`, `release_refusal.py`, and `cli.py` with `vip_fvs.real_preview_receipt`, `gate3.qc`, `vip_lab.mega13`, and `vip_lab.common`. |
| **Cycle 5** | End-to-end `MEGA-09 -> 10 -> 11 -> 13 -> 14 -> 15 -> 16` integration & test repair | Updated `tests/vip_lab/test_mega15.py`, `tests/vip_lab/test_mega16.py`, and `tests/vip_lab/test_mega15_16_end_to_end.py` to test real repository contracts, including positive and negative duplicate-preservation cases and CLI safety refusals. |
| **Cycle 6** | Compilation, regression suite (`test_mega08..16`), and contract boundary audit | `python3 -m compileall -q src experiments tests` passed; all 59 test functions across `test_mega08..16` passed in-process; zero read-only files modified. |

---

## 3. Deliverable Matrix

| Wave / Deliverable | Files Repaired / Verified | Test Suite | Local Verification | Hosted CI Status (Python 3.11 & 3.14) |
| --- | --- | --- | --- | --- |
| **Gate-0 Media Substrate (6 files)** | `src/gate0/media/{__init__,decode,probe,proc,source_guard,tool_identity}.py` | `tests/gate0/` (in CI) + SHA verification | `VERIFIED_EXACT_BLOB_SHAS` (`6/6`) | `PENDING_NEXT_GITHUB_PUSH` |
| **MEGA-15:** Gate-3 Source-Native Temporal Preparation, Editorial Handoff & Lineage Validation | `src/vip_lab/mega15/__init__.py`<br>`src/vip_lab/mega15/temporal_preflight.py`<br>`src/vip_lab/mega15/editorial_handoff.py`<br>`src/vip_lab/mega15/lineage.py` | `tests/vip_lab/test_mega15.py` (`12/12 PASS`) | `PASS` (`compileall` + in-process test execution) | `PENDING_NEXT_GITHUB_PUSH` |
| **MEGA-16:** Render/Export/QC Preflight Infrastructure, Release Refusal & CLI | `src/vip_lab/mega16/__init__.py`<br>`src/vip_lab/mega16/render_preflight.py`<br>`src/vip_lab/mega16/qc_requirements.py`<br>`src/vip_lab/mega16/release_refusal.py`<br>`src/vip_lab/mega16/cli.py` | `tests/vip_lab/test_mega16.py` (`4/4 PASS`)<br>`tests/vip_lab/test_mega15_16_end_to_end.py` (`2/2 PASS`) | `PASS` (`compileall` + in-process test execution) | `PENDING_NEXT_GITHUB_PUSH` |
| **Upstream Regressions (`MEGA-08..14`)** | Preserved untouched (`src/vip_lab/mega08..14/**`) | `tests/vip_lab/test_mega08..14` (`41/41 PASS`) | `PASS` (`59/59` total across `test_mega08..16`) | `PENDING_NEXT_GITHUB_PUSH` |

## 4. Independent LAB Repair and Acceptance Record — 2026-11-04

- **Observed LAB base:** `origin/main@7ea814d5c4626ed6b371c01f282c8a9b0138ffa0`; the original canonical VIP repository was not accessed or modified.
- **Intact restoration reference:** `e5974d9730d0ef85af5dc6fa16445e93b8c9941d`. All six restored paths were checked against the exact Git blob IDs in §1. Restoration used only those paths; MEGA-15/16 content was preserved.
- **Publication diagnosis:** the second repair commit's tree omits the six paths and Git reproduces the `.gitignore` match. The external ZIP publisher's evaluation and staging behavior was not observed, so its causal role remains a hypothesis. The `.gitignore` exception covers only the six source `.py` paths under `src/gate0/media/`; real-media `media/` directories remain ignored elsewhere. Tree inspection and CI remain the publication-loss detection checkpoints.
- **Confirmed defects reproduced before repair:** (1) a symlinked ancestor directory allowed output creation through the symlink; (2) a short `os.write` returned CLI success with truncated JSON; (3) a write error could leave an incomplete report; (4) `verify-report` read a media-suffixed path before rejecting its content. Regression tests were added first and showed the first two behaviors and malformed output; the error-cleanup and media-read tests now verify fail-closed behavior.
- **Minimal code changes:** `src/vip_lab/mega16/cli.py` now opens each output/input parent component without following symlinks, restricts report files to `.json`, checks input file type and size, retries partial writes, removes partial output after write failure, and turns filesystem errors into CLI refusals. No renderer, provider, source media, or subprocess is invoked.
- **Independent contract review:** generated PTS remains `NOT_OBSERVED`, candidate evidence remains `MATCHED`, authoritative measurement and binding eligibility remain false; nominal-FPS frame conversion is explicitly refused; repeated PTS require occurrence selection; duplicate source content at distinct paths and identical query text with distinct query IDs are retained through lineage checks. Proposal revisions bind parent digests. Synthetic context parsing re-creates a sealed synthetic marker and rejects authority keys. Model/tool principals are refused; synthetic proposals cannot produce authoritative edit plans. QC states remain `NOT_OBSERVED` with canonical blockers. A-7 mapping and IT-6 tail authorization remain unresolved; no mapping or real terminal-tail evidence is invented. MEGA-16 remains declarative and export-refused.
- **CLI boundary:** input/output is confined to the fixed `outputs/vip_lab/synthetic-reports` root; relative names are resolved beneath it and arbitrary absolute paths are refused before filesystem access or directory creation. `.json` sizing, media/URI refusal, no-clobber, traversal, symlink protections, forbidden execution/authority flags, descriptor-relative `O_NOFOLLOW`, complete-write loops, and partial-output cleanup remain in force. Pytest substitutes only the private root constant through `monkeypatch`; the CLI exposes no root override.
- **2026-11-04 trusted-root regression:** before implementation, valid absolute input outside the configured root verified successfully and absolute output outside it was created (both new negative tests failed with `0 == 2`). The fixed root is anchored to the repository's ignored generated-output convention; relative paths are rooted there. New tests also assert out-of-root target metadata/read access is not attempted, and successful in-root verification leaves report bytes unchanged.
- **Local verification (Python 3.14.9):** `compileall` passed; the prior-import regression group passed **10/10**; the requested MEGA-15/16 suites passed **22/22**; the full `tests/vip_lab` suite passed **105/105**; the workflow's bounded Gate-1/product-path suites passed **146/146**. The 10 and 22 tests overlap the 105-test run and are not additive. No tests were skipped. Python 3.11 local execution was unavailable; both interpreter results require hosted CI.
- **Hosted PR CI:** PR #1 run `41875246950` completed successfully on Python 3.11 and 3.14 for repair commit `561bd6d189ccad586fe7c52dc748709ace3cee3a`; every workflow step, including Gate-0 media imports and submitted MEGA-15/16 suites, passed. A follow-up ledger-only commit is being submitted separately and requires its own exact-head workflow run before final PR-head acceptance.
- **Deferred real prerequisites:** real source-native PTS, A-7 and IT-6 rulings, authenticated human editorial decisions, model benchmarks, observed technical/visual/audio QC, and export authority remain `NOT_OBSERVED` or separately gated. This repair does not start the next development program or complete a canonical VIP gate.
