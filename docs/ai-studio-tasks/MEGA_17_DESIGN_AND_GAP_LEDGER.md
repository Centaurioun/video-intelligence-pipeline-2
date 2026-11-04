# MEGA-17 — Design and Gap Ledger (`LAB-MEGA-17-v1.0.0`)

## 1. Baseline & Environment Identity

- **Program Version:** `LAB-MEGA-17-v1.0.0`
- **Implementation Target:** `https://github.com/Centaurioun/video-intelligence-pipeline-2` (`LAB` repository ONLY)
- **Canonical Reference Repository (Read-Only):** `https://github.com/Centaurioun/video-intelligence-pipeline` (`main@592952daf475b1bbae2eebdee64d992c1a744f08`)
- **Declared LAB Baseline Reference:** `85a4190925fbb2c6ca11c4b354ad9f1296daf82f` (LAB PR #1 repair head / CI run `41875647638`)
- **Workspace Git SHA (`workspace_git_sha`):** `NOT_OBSERVED` (AI Studio imported container has no `.git` directory)
- **Six `src/gate0/media/` Modules Present & Intact:**
  1. `src/gate0/media/__init__.py`
  2. `src/gate0/media/decode.py`
  3. `src/gate0/media/probe.py`
  4. `src/gate0/media/proc.py`
  5. `src/gate0/media/source_guard.py`
  6. `src/gate0/media/tool_identity.py`
- **Existing LAB Infrastructure Present (`MEGA-03..MEGA-16`):**
  - `src/vip_lab/common.py`, `src/vip_lab/integration.py`, `src/vip_lab/cli.py`
  - `src/vip_lab/mega03` through `src/vip_lab/mega16` (including `src/vip_lab/mega16/cli.py` with argv forbidden-token scanning, atomic exclusive `O_NOFOLLOW` output creation, and bounded regular-file input verification)
  - `tests/vip_lab/test_mega03.py` through `tests/vip_lab/test_mega16.py`, `test_mega08_14_end_to_end.py`, `test_mega15_16_end_to_end.py`
- **AI Studio Container Snapshot Delta Note (Important Publication Guardrail):**
  - In this persistent AI Studio container, `src/gate0/media/*.py` and `src/vip_lab/mega16/cli.py` are present and intact, while `/.gitignore` (which is read-only under MEGA-17 rules) still reflects the pre-PR #1 container line `media/` and `docs/ai-studio-tasks/MEGA_15_16_PROGRESS.md` reflects the pre-PR #1 push state.
  - Because MEGA-17 is strictly additive (`src/vip_lab/mega17/**`, `tests/vip_lab/test_mega17_*.py`, `docs/ai-studio-tasks/MEGA_17_*`) and modifies zero existing files, publication to `Centaurioun/video-intelligence-pipeline-2` MUST add only the new MEGA-17 files onto the post-PR #1 `main` branch (`85a4190925fbb2c6ca11c4b354ad9f1296daf82f` or descendant) and must NEVER perform a wholesale ZIP overwrite of `.gitignore` or existing files.

---

## 2. Workstream Classification Ledger (Workstreams A through E)

Every item is classified using the six mandatory MEGA-17 categories:
- `ALREADY_IMPLEMENTED`
- `REUSE_EXISTING`
- `MISSING_AND_AUTHORIZED`
- `BLOCKED_BY_OWNER_DECISION`
- `BLOCKED_BY_EXTERNAL_EVIDENCE`
- `NOT_OBSERVED`

### Workstream A — LAB-to-Canonical Integration Readiness (Roadmap Step 2)

| Capability / Requirement | Classification | Existing Source / Contract | MEGA-17 Action |
|---|---|---|---|
| Static AST symbol & file SHA-256 inspection over allowlisted paths | `REUSE_EXISTING` | `src/vip_lab/mega08/capability_inventory.py` (`inspect_module_symbols_ast`, `validate_allowlisted_relative_path`) | Reuse directly in `src/vip_lab/mega17/canonical_integration.py` without reimplementing AST walkers |
| Complete source-backed inventory of `MEGA-03` through `MEGA-16` modules & tests | `MISSING_AND_AUTHORIZED` | `src/vip_lab/mega03..16`, `tests/vip_lab/test_mega03..16.py` | Build deterministic `CanonicalIntegrationReadinessPacket` enumerating all `MEGA-03..16` modules, tests, and `src/gate0/media/*` safeguard files |
| Classification into additive / overlapping / incompatible / synthetic-only / owner-gated | `MISSING_AND_AUTHORIZED` | `docs/project/01_CURRENT_STATE_AND_HANDOFF.md`, `src/vip_lab/mega08` | Classify every LAB module into `ADDITIVE_SAFE`, `OVERLAPPING_REQUIRES_RECONCILIATION`, `INCOMPATIBLE_WITHOUT_AMENDMENT`, `SYNTHETIC_ONLY_LAB_HARNESS`, or `OWNER_GATED_CANONICAL_DECISION` |
| Transplant conflict detector (duplicate module paths, symbol collisions, PR #258 / PR #259 overlap, `.gitignore` `media/` hazard) | `MISSING_AND_AUTHORIZED` | `src/vip_lab/mega03/a7_s5_audit.py`, `src/gate0/media/*` | Implement deterministic conflict detector flagging PR #258 (`S5-T1` admission), PR #259 (continuity handoff), unanchored `media/` `.gitignore` pattern, and forbidden canonical overwrites |
| Non-destructive canonical integration sequence proposal | `MISSING_AND_AUTHORIZED` | `docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md` | Emit ordered, dependency-safe candidate integration wave plan (`WAVE_1_PURE_LAB_NAMESPACE` -> `WAVE_2_SYNTHETIC_TESTS` -> `WAVE_3_OWNER_GATED_RECONCILIATION`) |
| Actual canonical repository (`video-intelligence-pipeline`) mutation or merge | `BLOCKED_BY_OWNER_DECISION` | Section 6 (`canonical_integration_executed = false`, `canonical_main_modified = false`, `canonical_adoption_authorized = false`) | Fail closed if any caller requests canonical execution or claims canonical adoption |

### Workstream B — Source Identity, Custody, Rights, and D-2 Readiness (Roadmap Step 3)

| Capability / Requirement | Classification | Existing Source / Contract | MEGA-17 Action |
|---|---|---|---|
| 30-field Gate-0 D-2 intake validation (`G0-D2-01..G0-D2-30`) | `REUSE_EXISTING` | `src/gate0/d2_intake.py` (`evaluate_d2_package`, `D2_FIELDS`, `D2_BASELINE_STATES`), `src/vip_lab/mega04/d2_readiness.py` (`inspect_d2_readiness`) | Reuse `inspect_d2_readiness` and `D2_FIELDS` directly |
| Closed synthetic D-2 readiness fixture exercising all 7 `EVIDENCE` validators (`G0-D2-01`, `10`, `11`, `12`, `14`, `17`, `26`) while keeping 21 `RULING` rows `BLOCKED` and 2 `OBSERVATION` rows `NOT_OBSERVED` | `MISSING_AND_AUTHORIZED` | `src/gate0/d2_intake.py`, `src/gate0/labels.py` | Build deterministic synthetic D-2 fixture builder and validator in `src/vip_lab/mega17/source_readiness.py` |
| Strict separation of 8 identity layers: occurrence vs revision vs content vs locator vs stream vs derived artifact vs policy decision vs run/attempt | `MISSING_AND_AUTHORIZED` | `docs/architecture/CANONICAL_CONTRACTS.md` §2–3, `docs/architecture/LOCATOR_SOURCE_OBSERVATION_SEMANTICS_V1.md` | Model explicit `SourceIdentityCustodyMatrix` verifying that duplicate SHA-256 occurrences keep distinct `occurrence_id` and `revision_id` and never collapse or auto-skip |
| Identical filename / locator without byte verification refused as content identity | `MISSING_AND_AUTHORIZED` | `docs/architecture/LOCATOR_SOURCE_OBSERVATION_SEMANTICS_V1.md` | Enforce fail-closed refusal (`LOCATOR_EQUALITY_IS_NOT_BYTE_IDENTITY`) when two entries claim content equivalence from filename/locator alone |
| Seven distinct permission boundaries (discover, inspect local bytes, create derived artifacts, run authentic models, provider/cloud egress, retain outputs, export outputs) | `MISSING_AND_AUTHORIZED` | `docs/architecture/CANONICAL_CONTRACTS.md`, `docs/gate0/D2_OWNER_INPUT_INTAKE_CHECKLIST_2026-10-25.md` | Implement 7-permission boundary matrix where discovering a path never grants byte inspection, derived artifact creation, model execution, egress, retention, or export |
| Source-disjoint `DEVELOPMENT` vs `EVALUATION` partition check | `MISSING_AND_AUTHORIZED` | `src/gate0/d2_intake.py` (`_check_corpus_designation`), `src/gate0/labels.py` | Verify zero session/revision/content/query overlap between `DEVELOPMENT` and `EVALUATION` partitions |
| Real archive discovery, real byte hashing, verified legal rights, D-3 grant | `BLOCKED_BY_OWNER_DECISION` / `NOT_OBSERVED` | Section 7 (`real_source_inventory_executed = false`, `real_source_bytes_observed = false`, `real_source_rights_verified = false`, `d3_authorized_local_execution = false`) | Report all four flags `False` and emit structured Owner-input requirements packet |

### Workstream C — Gate-0 Diagnostic Retrieval Experiment Readiness (Roadmap Step 4)

| Capability / Requirement | Classification | Existing Source / Contract | MEGA-17 Action |
|---|---|---|---|
| 40-query protocol (24 positive across 4 families × 6, 8 absent, 8 development), ranking-input label firewall, dual-reviewer rational gold events, blinded reviewer envelope | `REUSE_EXISTING` | `src/gate0/labels.py`, `src/gate0/reviewer_envelope.py`, `src/vip_lab/mega04/query_review_preflight.py`, `src/vip_lab/mega04/experiment_readiness.py` | Reuse `inspect_query_review_preflight`, `inspect_gate0_entry`, `gate0.evaluation.evaluate` |
| Closed Gate-0 experiment-preflight receipt covering all 12 Gate-0 contract artifacts (`source_manifest`, `sample_manifest`, `queries`, `gold_events`, `reviewer_judgments`, `run_manifest`, `benchmark_metrics`, `failure_taxonomy`, `decision_record`, `experiment_ledger`, `gate_verdict`, `audit_log`) | `MISSING_AND_AUTHORIZED` | `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md`, `src/gate0/evaluation.py` | Implement `Gate0ExperimentReadinessReceipt` verifying schema/contract readiness for all 12 artifacts while keeping real run state `NOT_RUN` |
| 4-second non-overlapping half-open window (`[start, end)`) and 2-FPS presentation-frame sampling specification check | `MISSING_AND_AUTHORIZED` | `config/gate0/default.json`, `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md` | Validate canonical segmentation (`window_duration_s = 4`, `window_overlap_s = 0`, `endpoint_semantics = "HALF_OPEN"`, `sampling_fps = 2`) and refuse overlapping or closed-interval windows |
| Deterministic synthetic scoring & verdict separation (`INVALID_PROTOCOL`, `NOT_RUN`, `BLOCKED_PREREQUISITE`, `FAIL`, `PASS`) under exact thresholds (`Hit@10 >= 20/24`, `paired_lift >= 5/24`, `family_hit_at_10 >= 3/6` in all 4 families) | `MISSING_AND_AUTHORIZED` | `src/gate0/evaluation.py` (`evaluate`) | Build deterministic synthetic scoring fixtures proving threshold boundaries while keeping real Gate-0 status `NOT_RUN` |
| Gate-0 vs Gate-1 boundary enforcement (SigLIP V1 Base vs SigLIP2 V2 Base vs SigLIP2 SO400M) | `REUSE_EXISTING` / `MISSING_AND_AUTHORIZED` | `src/vip_fvs/synthetic_profiles.py`, `src/vip_lab/mega05` | Enforce that Gate-1 multi-profile comparisons never substitute for Gate-0 diagnostic baseline lift |
| Authentic Gate-0 model inference, human labels, D-3 execution, Gate-0 promotion | `BLOCKED_BY_EXTERNAL_EVIDENCE` / `NOT_OBSERVED` | Section 8 (`gate0_authentic_experiment_status = NOT_RUN`, `gate0_d3_authorized = false`, `gate0_real_model_execution = NOT_OBSERVED`, `gate0_real_human_labels = NOT_OBSERVED`, `gate0_promotion = false`) | Enforce hard invariant values and refuse synthetic promotion claims |

### Workstream D — Gate-3 Native Temporal and Editorial Workflow Readiness (Roadmap Step 6)

| Capability / Requirement | Classification | Existing Source / Contract | MEGA-17 Action |
|---|---|---|---|
| Candidate review queue, temporal refinement request, PTS diagnostic, editorial proposals (`v1->v2->v3`), and MEGA-15 offline Gate-3 preparation packet | `REUSE_EXISTING` | `src/vip_lab/mega09`, `mega10`, `mega11`, `mega13`, `mega14`, `mega15` (`build_gate3_offline_preparation_packet`, `audit_mega15_lineage`) | Consume `CandidateReviewQueue`, `TemporalRefinementRequest`, `PtsFixtureDiagnostic`, `Gate3OfflinePreparationPacket`, and `Mega15LineageReceipt` directly without duplicating MEGA-15 builders |
| Strict 5-way coordinate separation: semantic candidate timestamps (`SEMANTIC_SECONDS`), synthetic PTS diagnostics, source-native PTS measurements (`SOURCE_PTS`/`SOURCE_FRAME`), approved human editorial decisions, output timeline coordinates (`TIMELINE_TIME`) | `MISSING_AND_AUTHORIZED` | `src/gate3/refinement.py`, `src/gate3/editorial.py`, `src/gate3/plan.py`, `src/vip_lab/mega15` | Implement `EditorialWorkflowReadinessPacket` verifying coordinate domain separation and refusing any cross-domain conflation or `seconds * nominal_fps` derivation |
| Reviewer-handoff `REQUIREMENTS` packet (never a completed human review) separating technical measurement readiness from editorial judgment readiness | `MISSING_AND_AUTHORIZED` | `src/vip_fvs/review_bundle.py`, `src/vip_fvs/human_decision.py`, `src/vip_lab/mega15/editorial_handoff.py` | Build structured `ReviewerHandoffRequirementsPacket` specifying exact required inputs for future `ReviewBundle` + `HumanDecisionArtifact` without fabricating human approval |
| A-7 stream namespace ambiguity refusal & IT-6 terminal-tail duration mismatch refusal | `REUSE_EXISTING` | `src/gate3/stream_identity.py`, `src/gate3/refinement.py`, `src/vip_lab/mega15/temporal_preflight.py` | Exercise and verify fail-closed refusal codes (`REFUSAL_STREAM_NAMESPACE_UNMAPPED`, `REFUSAL_IT6_TAIL_MISMATCH`, `REFUSAL_NOMINAL_FPS_DERIVATION_FORBIDDEN`, `REFUSAL_B_FRAME_DTS_REORDER_UNPROVEN`, `REFUSAL_EDIT_LIST_UNSUPPORTED`) |
| Real source-native PTS measurement, real human editorial decision, binding-eligible real edit, authoritative edit plan | `BLOCKED_BY_EXTERNAL_EVIDENCE` / `NOT_OBSERVED` | Section 9 (`real_source_native_pts_evidence = NOT_OBSERVED`, `human_editorial_decision = NOT_OBSERVED`, `binding_eligible_real_edit = false`, `authoritative_edit_plan_created = false`) | Report exact required states and refuse any synthetic promotion to `EditPlanRevision(plan_scope="REAL")` or `is_binding_eligible == True` |

### Workstream E — Render, Export, QC, and Release Readiness (Roadmap Step 7)

| Capability / Requirement | Classification | Existing Source / Contract | MEGA-17 Action |
|---|---|---|---|
| MEGA-16 render preflight specification, QC requirements bundle, release refusal certificate, and `Mega1516OfflineReport` | `REUSE_EXISTING` | `src/vip_lab/mega16` (`run_mega15_16_offline_pipeline`, `verify_mega15_16_offline_report`, `build_render_preflight_specification`, `build_qc_requirements_bundle`, `build_release_refusal_certificate`), `src/vip_lab/mega13`, `src/gate3/qc.py` | Consume `Mega1516OfflineReport` and `gate3.qc.bare_pass_is_insufficient` directly |
| Strict 7-stage separation: (1) permitted local preview, (2) render preparation, (3) actual rendering, (4) technical post-render QC, (5) visual/editorial QC, (6) audio/sync QC, (7) final release/export authorization | `MISSING_AND_AUTHORIZED` | `docs/architecture/CANONICAL_CONTRACTS.md`, `src/gate3/qc.py`, `src/vip_lab/mega16` | Implement `ReleaseReadinessVerificationPacket` modeling all 7 stages distinctly so preview or render preflight never implies render execution, QC observation, or release authorization |
| Provenance non-upgrade guard (derived output receipt never upgrades source provenance or replaces upstream measurement/decision evidence) | `MISSING_AND_AUTHORIZED` | `src/gate3/qc.py` (`may_consume_for_binding_origin`), `src/vip_lab/mega16` | Enforce fail-closed refusal (`DERIVED_RECEIPT_CANNOT_UPGRADE_PROVENANCE`) if any derived/render receipt claims to satisfy upstream source/PTS/human authority |
| Inert dry-run render intent vs executed FFmpeg command distinction | `REUSE_EXISTING` / `MISSING_AND_AUTHORIZED` | `src/vip_lab/mega16/render_preflight.py` | Verify `execution_mode == "DRY_RUN_SPECIFICATION_ONLY"`, `subprocess_invoked == False`, and refuse executable FFmpeg flags (`-y`, `filter_complex`, output `.mp4`/`.mov`) |
| All 12 mandatory E12 negative refusal checks (missing source hash, unmapped stream index, semantic-only boundaries, unapproved human decision, stale edit plan revision, missing technical QC, missing visual QC, missing audio QC, forged sensory observation, bare PASS QC, synthetic input marked real, unauthorized export request) | `MISSING_AND_AUTHORIZED` | `src/vip_lab/mega16/release_refusal.py`, `src/vip_lab/mega13/qc_readiness.py` | Implement explicit deterministic refusal evaluator covering all 12 E12 failure conditions with machine-readable refusal codes |
| Preview execution, render execution, technical/visual/audio QC observation, production export | `BLOCKED_BY_OWNER_DECISION` / `NOT_OBSERVED` | Section 10 (`preview_executed = false`, `render_executed = false`, `technical_qc_observed = NOT_OBSERVED`, `visual_editorial_qc_observed = NOT_OBSERVED`, `audio_editorial_qc_observed = NOT_OBSERVED`, `production_export_authorized = false`, `export_status = REFUSED_NOT_AUTHORIZED`) | Enforce exact required output fields on every report |

---

## 3. Architecture & Design Comparison (Option A vs Option B)

### Option A — Thin Composition & Readiness Verification Layer Over Existing `vip_lab` + `gate0`/`gate3`/`vip_fvs` Contracts (SELECTED)
- **Structure:**
  - `src/vip_lab/mega17/canonical_integration.py` (Workstream A — reuses `mega08` AST symbol inspector)
  - `src/vip_lab/mega17/source_readiness.py` (Workstream B — reuses `gate0.d2_intake` & `mega04.d2_readiness`)
  - `src/vip_lab/mega17/gate0_readiness.py` (Workstream C — reuses `mega04`, `gate0.labels`, `gate0.evaluation`, `gate0.config_freeze`)
  - `src/vip_lab/mega17/editorial_readiness.py` (Workstream D — consumes `mega14` & `mega15` artifacts and `gate3` predicates)
  - `src/vip_lab/mega17/release_readiness.py` (Workstream E — consumes `mega16` offline report & `gate3.qc` predicates)
  - `src/vip_lab/mega17/orchestrator.py` & `src/vip_lab/mega17/verification.py` (End-to-end single-arm & three-arm product-readiness chain producing and verifying `Mega17ProductReadinessReport`)
- **Advantages:**
  - Zero duplication of existing `MEGA-03..16`, `gate0`, `gate3`, or `vip_fvs` logic.
  - Preserves one canonical lineage spine from synthetic source manifest -> retrieval -> candidate queue -> temporal request -> MEGA-15 offline preparation -> MEGA-16 render/QC/release refusal -> MEGA-17 five-workstream product-readiness report.
  - Strictly additive: modifies zero existing files and keeps `src/gate0/media/*` untouched.

### Option B — Standalone Parallel Pipeline Re-implementing D-2, Query Evaluation, Temporal Preparation, and Render/QC Bundles Inside `mega17` (REJECTED)
- **Why Rejected:**
  - Violates Section 0 ("A smaller correct implementation is better than a larger duplicate system") and Section 9 ("Do not reimplement MEGA-15. Consume or verify MEGA-15 artifacts").
  - Creates schema drift risk between `gate0`/`gate3`/`mega04..16` and `mega17`.

### Reconsideration Triggers
- If any upstream `mega04`, `mega08`, `mega14`, `mega15`, or `mega16` public function signature were missing or broken in the workspace, we would stop and report `BLOCKED_STALE_OR_INCOMPLETE_LAB_BASELINE`. Cycle 1 verified all upstream functions are present and intact.
