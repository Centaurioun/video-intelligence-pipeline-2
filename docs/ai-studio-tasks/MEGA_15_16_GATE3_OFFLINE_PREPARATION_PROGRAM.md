# VIP LAB — MEGA-15 + MEGA-16: Gate-3 Offline Preparation Program

Version: LAB-MEGA-15-16-v1.0.0
Date: 2026-11-04
Target: Centaurioun/video-intelligence-pipeline-2 ONLY.
Original canonical (READ ONLY): Centaurioun/video-intelligence-pipeline main@592952daf475b1bbae2eebdee64d992c1a744f08.
LAB verified code baseline: 9bdd810bf14c93ed1f77243325beaa6b37b3e97d.
Hosted synthetic CI: https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/41850619259 — 350 PASS on EACH Python 3.11 and 3.14.
Owner instruction: Work on roadmap steps 6 and 7 together as one large task, WITHOUT human evaluation, authentic video/model operations, or production render/export. Defer real execution of roadmap 2, 3 and 4; document prerequisites only.

## A. Authority and exact scope

Deliver source-backed, generated-only PREPARATION software for (6) precise Gate-3 temporal and editorial handoff, and (7) preview/render/export/QC preflight and refusal controls. Do not claim a real human decision, production EditPlan, authentic MEASURED PTS, actual preview/render/export, successful human editorial QC or Gate promotion.

The final real product chain is semantic candidate -> measured native source PTS/timebase -> authentic HUMAN editorial decision -> versioned edit plan -> separately authorized render -> technical AND editorial QC. The user has expressly deferred all real corpus and human work; those transitions MUST stay blocked.

Do not open/read/stat/hash any real source files. Source media immutable. No model downloads, embeddings, providers, Gemini/API calls, network/cloud, URL fetch, real FFmpeg/ffprobe, production render, or export. Do not modify original VIP main, owner-frozen policies or source contracts.

Canonical assertion evidence classes: MEASURED, MATCHED, VISUALLY_OBSERVED, AUDIO_OBSERVED, EDITORIAL_INFERENCE. NOT_OBSERVED is a marker, not an evidence class. Never convert semantic candidate seconds to exact frame coordinates; NEVER seconds x nominal FPS. Use actual source-native PTS/timebase only for future real measurement. A generated fixture PTS table is a synthetic diagnostic, not real source MEASURED evidence.

## B. Mandatory preflight

Read current source before implementation:
- Original: docs/project/00_PROJECT_CHARTER.md, 01_CURRENT_STATE_AND_HANDOFF.md, 02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md, STATE_MAINTENANCE_PROTOCOL.md, docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md Gate-3 section, docs/architecture/CANONICAL_CONTRACTS.md, src/gate3/AGENTS.md.
- LAB: src/gate3/pts.py, temporal.py, refinement.py, refinement_request.py, stream_identity.py, plan.py, editorial.py, render_adapter.py, qc.py, authority.py.
- LAB: src/vip_fvs/refinement_adapter.py, review_bundle.py, human_decision.py, editorial_plan.py, real_plan.py, local_preview.py, real_preview_qc.py, real_preview_verifier.py, real_preview_receipt.py, stream_identity_gate.py.
- LAB: src/vip_lab/mega09/**, mega10/**, mega11/**, mega13/**, mega14/**, common.py, tests/vip_lab/test_mega08_14_end_to_end.py and progress ledger.
- Verify all SIX existing src/gate0/media dependency files: __init__.py, decode.py, probe.py, proc.py, source_guard.py, tool_identity.py. If absent STOP TASK_BASELINE_NOT_SYNCED. Do NOT recreate dummy versions.
- Verify current original Gate-3 blockers. Original PR #258 S5-T1 admission is draft/unmerged; original #231 G3.2.1 cross-corpus separation proposal is draft/unmerged at this checkpoint. Positive A-7 mapping of FFprobe selected_stream_index to ISO-BMFF tkhd.track_ID is not globally adopted; IT-6 terminal-tail admission remains pending. Do not invent positive mapping, terminal-tail policy or decision authority.
- ZIP workspaces may lack .git: record workspace_git_sha=NOT_OBSERVED, report declared source baseline versus observed source, do not invent a verified local SHA. If workspace differs from the verified 350-test source snapshot, STOP and explain exact missing files.

## C. Source-aware design and rejection of duplicate implementations

Before editing, write a six-cycle design/inventory and gap ledger to docs/ai-studio-tasks/MEGA_15_16_PROGRESS.md. Cycles:
1 verified API and source inventory;
2 temporal/stream identity adversarial checks;
3 editorial principal and revision/lineage;
4 render/export/QC refusal and privacy;
5 cross-wave functional integration;
6 source code static review, negative tests and acceptance readiness.

For each proposed feature mark ALREADY_IMPLEMENTED, REUSE, MISSING_LAB_CODE_ALLOWED, BLOCKED_BY_AUTHORITY, or NOT_OBSERVED with exact source path and public API. Explicitly reject parallel duplicate PTS engine, frame conversion by nominal FPS, fake stream-ID mapping, second human decision engine, second edit-plan builder, second FFmpeg renderer, second QC truth engine, second scheduler, Express/Node backend, mock queue or synthetic-to-real certification. Prefer thin, pure-Python LAB adapters consuming existing contracts.

If a NEW SHARED ARCHITECTURE decision is required, record a proposal and stop that subtask pending Owner approval; never self-adopt. Only additive LAB preparatory code is authorized.

## D. MEGA-15: Gate-3 temporal + editorial handoff

Deliver a deterministic generated-only Gate3PreparationPacket or equivalent closed, digest-bound record. Build it from existing MEGA-09 CandidateReviewQueue, MEGA-10 TemporalRefinementRequest/PTS fixture diagnostics, MEGA-11 EditorialProposal revision chain. Use actual Gate3 PtsTable and temporal contracts; do not duplicate arithmetic.

Expected NEW files:
- src/vip_lab/mega15/__init__.py
- src/vip_lab/mega15/temporal_preflight.py
- src/vip_lab/mega15/editorial_handoff.py
- src/vip_lab/mega15/lineage.py
- tests/vip_lab/test_mega15.py

Requirements:
1. Closed schema, deterministic canonical digests, bounded input length and identity pins. Preserve source occurrence path distinct from source_sha256, source_revision, query_id, selected_stream_index, generation, timebase, parent proposal digest.
2. Preserve duplicate source digest across distinct occurrences and repeated query string with distinct query_id; do not collapse them by path or content digest.
3. Half-open rational PTS diagnostic checks, ambiguous repeated PTS, VFR/discontinuity, stream-tail uncertainty and selected stream namespace differences; selected_stream_index != arbitrary tkhd.track_ID. Any unresolved A-7/IT-6 condition must produce refusal/blocker, not invented values.
4. Any fixture PTS proves only generated-test arithmetic. Without verified named source bytes, the authoritative predicate gate3.refinement.is_binding_eligible must remain false/unproven; source_pts_evidence_state=NOT_OBSERVED; no exact real edit boundary.
5. Produce pre-review candidate packet: ranked semantic moment, source provenance, requested interval, requirements for real measurement, proposed editorial rationale, missing reviewer identity/decision and hard blockers. Do NOT create a HumanDecisionArtifact, ReviewBundle pretending real MEASURED, EditPlanRevision, approval or export.
6. Proposal revisions v1/v2/v3 must preserve parent proposal digest and closed lineage; stale revision, source SHA/stream mismatch, false human approval, fabricated measured PTS, tampered digest all fail closed.
7. Explicit overall flags: real_human_decision_state=NOT_OBSERVED, source_native_exact_edit_eligible=false, authoritative_edit_plan_created=false, production_export_authorized=false.

Regression cases: valid generated-only pre-review packet, duplicate occurrence/query preservation, boundary rules, VFR and repeated PTS, missing tail, stream index/trak ID confusion, stale revisions, injected false MEASURED and fake reviewer, no media or provider side effects.

## E. MEGA-16: Render/export/QC PRE-EXECUTION readiness, not rendering

From MEGA-15 preparation + existing MEGA-13 release blockers and actual gate3/vip_fvs APIs, produce pure declarative ExportReadinessPacket + QCRequirementManifest. Never execute a renderer. Reuse existing policy/source truth; no alternate rendering/QC engine.

Expected NEW files:
- src/vip_lab/mega16/__init__.py
- src/vip_lab/mega16/render_preflight.py
- src/vip_lab/mega16/qc_requirements.py
- src/vip_lab/mega16/release_refusal.py
- src/vip_lab/mega16/cli.py
- tests/vip_lab/test_mega16.py
- tests/vip_lab/test_mega15_16_end_to_end.py

Requirements:
1. Declare requirements for future authorized preview/export: source revision and no-follow digest pins, source-native measured PTS, selected video/audio streams, timebase, rational timeline, versioned human decision/edit plan, tool identities, output lineage/receipt/identity, technical QC, separate visual and audio/editorial QC, consent/rights/egress/retention, export policy. Format/codec profiles are proposed placeholders, not adopted production profiles.
2. Independent status vocabulary: preview_policy_authorized, render_executed, technical_qc_observed, visual_editorial_qc_observed, audio_editorial_qc_observed, production_export_authorized. All default false or NOT_OBSERVED; no user JSON flag can upgrade them without verified external authority, which this task does NOT possess.
3. Overall export_status=REFUSED_NOT_AUTHORIZED. Do not claim QC PASS if media was not measured/observed. Call or reuse gate3.qc.bare_pass_is_insufficient where appropriate. Do not synthesize human visual/audio evidence.
4. Do not call render_synthetic or LocalPreviewAdapter on real media, and do NOT execute FFmpeg/ffprobe or write video output even in AI Studio. Emit descriptive requirements and an inert dry-run intent only, never an executable command with assumed verified source.
5. CLI may create/verify a bounded, generated-only JSON report; never read source media. Explicitly reject --real, --render, --export, --provider, --download, --upload, source URLs and untrusted input that claims real source measurements or actual human approval.
6. Cross-wave report should verify digests and foreign keys across MEGA-09→10→11→13→15→16, with no false Gate acceptance or real export.

Adversarial tests: 3-arm and single-arm generated-only intake, modified report digest, tampered stage lineage, forged measured PTS, bogus real human approval, spoofed QC PASS, false source stream, missing terminal-tail evidence, unapproved export, unknown CLI flags, not touching any source media or subprocess, deterministic serialization, all release blockers retained.

## F. Deferred only: roadmap items 2, 3 and 4

Create NEW docs/ai-studio-tasks/MEGA_15_16_DEFERRED_REAL_PILOT_PREREQUISITES.md as READ-ONLY evidence mapping. No actual canonical LAB integration, no protected archive access/inventory, no real query benchmark or human labels. Explain exact future Owner approvals for:
- Canonical code integration decision with reviewed SHA and shared-contract reconciliation;
- Source permission/rights, identity/manifest and no-follow hash policy;
- Gate-0 D2 real editor queries, reviewer labels, protocol validity, D3 approval;
- Authentic model assets and provider egress/host/cost approvals;
- Gate-3 source-native measured PTS/frame, human decision, A-7/IT-6 ruling, non-production preview, production export and independent technical/editorial QC.
Existing synthetic fixtures are NOT completion evidence for these.

## G. Source ownership, test-first, CI, safety

Allowed changes ONLY:
- NEW src/vip_lab/mega15/** and mega16/**
- NEW tests/vip_lab/test_mega15.py, test_mega16.py, test_mega15_16_end_to_end.py
- NEW docs/ai-studio-tasks/MEGA_15_16_PROGRESS.md and MEGA_15_16_DEFERRED_REAL_PILOT_PREREQUISITES.md

Everything previously verified (MEGA-03..14, gate0..3, vip_fvs, existing tests, existing docs, .github, protected original repo) is READ ONLY. For a proven existing API defect, record exact blocker and await separate owner scope; don't modify producer APIs to greenwash.

Author tests BEFORE new feature code. AI Studio must not execute pytest, install packages, download/run models, call network/provider, open video, invoke ffmpeg/ffprobe, or perform real media operation. Static ast.parse is allowed. Report IMPLEMENTED_UNVERIFIED, not CI_VERIFIED.

Host CI Owner/controller separately selects three NEW test suites on Python 3.11 and 3.14. Keep the existing 350 suite PASS. Tests must include no-side-effect refusals, not merely happy path. No submitted wave may be certified from SKIPPED steps.

The AI Studio ZIP-to-main publisher repeatedly deletes six gate0/media dependencies. If selective changed-file publishing is unavailable, report exactly what was removed and STOP unsafe publication if possible. Do not invent fake substitutes, git reset --hard, force push, destructive cleanup or declare a deletion harmless. The controller may selectively restore exact audited blobs after a reported sync. Publication to LAB main is permitted by Owner only within this described source ownership; canonical original remains read-only.

## H. Completion and report

Produce ONE deterministic generated-only preparation chain:
candidate queue → nonbinding temporal diagnostic → editorial pre-review proposal → dry-run render/QC requirements → release refusal report.

The software may be suitable for a LATER separately approved real pilot, but has not actually run that pilot, rendered, exported, measured real PTS, or obtained a real human decision.

At completion report in Turkish: exact changed files, six source-review cycles, existing APIs reused, authored tests (NOT_EXECUTED_BY_DESIGN in AI Studio), genuine missing requirements, blocked/NOT_OBSERVED authorities, publication behavior and exact next GitHub CI + independent Codex review checkpoints.

Do not start MEGA-17, UI/dashboard, cloud/Gemini, real benchmark, source inventory, actual edit/export, or GitHub Projects operations in this development task.
