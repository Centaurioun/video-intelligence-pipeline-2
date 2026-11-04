# VIDEO INTELLIGENCE PIPELINE — Comprehensive ChatGPT New-Session Handoff

**Date:** 2026-11-04, Europe/Istanbul  
**Version:** VIP-CHATGPT-HANDOFF-2026-11-04-v1.0  
**Function:** Dated, independently repo-checked continuity. This is NOT a Gate grant, source permission, design adoption, real-video authorization, source-code certification or permission to merge protected original main.  
**Canonical original:** https://github.com/Centaurioun/video-intelligence-pipeline  
**Active synthetic LAB:** https://github.com/Centaurioun/video-intelligence-pipeline-2  
**Original main verified before writing:** \`592952daf475b1bbae2eebdee64d992c1a744f08\`  
**LAB main verified before writing:** \`f0d06caa7ce1fd04c36d3edb1eb4df7e805f5eb7\` (this documentation-only commit will advance LAB main, not the verified code snapshot).

> **READ THIS FIRST.** The Owner wants to continue in Turkish without recounting the preceding months of VIP work. The project has a separately maintained original canonical repository and a Google AI Studio-driven LAB mirror. The LAB has reached **350/350 selected synthetic tests PASSED on each of Python 3.11 and 3.14**, confirmed by actual GitHub CI logs at immutable commit \`9bdd810bf14c93ed1f77243325beaa6b37b3e97d\` and run [41850619259](https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/41850619259). Latest LAB \`main\` \`f0d06ca...\` also has a new **MEGA-15 + MEGA-16** generated-only, offline Gate-3 preparation specification and conditional CI. Its **three new test groups are SKIPPED/NOT_SUBMITTED**, not passing or implemented. Original VIP \`main\` is unchanged; original draft PR #258 and #259 remain unmerged. The Owner expressly wants to defer real-video work, human evaluation and benchmarks until later, while developing MEGA-15/16 preparatory code together as one large Google AI Studio task.

---

## 0. EXACT NEXT-CHAT RESUME INSTRUCTIONS

1. Read this entire handoff; then **re-fetch live GitHub** original and LAB \`main\` SHAs, PRs, CI runs/jobs, and changed files. The SHAs in this dated document MUST NOT be used as live-state assumptions.
2. Read canonical original \`AGENTS.md\`, \`docs/INDEX.md\`, and the four required current handoff files on **original \`main\`**:
   - \`docs/project/00_PROJECT_CHARTER.md\`
   - \`docs/project/01_CURRENT_STATE_AND_HANDOFF.md\`
   - \`docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md\`
   - \`docs/project/STATE_MAINTENANCE_PROTOCOL.md\`
   Then read \`docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md\`, \`docs/architecture/CANONICAL_CONTRACTS.md\`, and the LAB specification \`docs/ai-studio-tasks/MEGA_15_16_GATE3_OFFLINE_PREPARATION_PROGRAM.md\`.
3. If user sends a Google AI Studio completion, check whether actual \`src/vip_lab/mega15/**\`, \`mega16/**\`, test suites, progress and deferred-prerequisites docs have reached LAB GitHub; read exact diff and CI. **Do not assume prompt submission or static compilation implies completed code.**
4. Inspect all six \`src/gate0/media\` Python dependency files after any AI Studio push. ZIP-to-main synchronization has deleted them repeatedly despite the AI Studio report saying they existed locally. If absent, do narrow, exact verified blob restoration without hard reset/force push or touching new code.
5. Check MEGA-08–14's pending **independent final Codex acceptance** separately from CI; earlier Phase B source review was on an old failing candidate.
6. Check original GitHub Projects #2 items #260–262 only when the Owner provides the separate Codex result. Issues exist, but Projects V2 item membership has not been verified via the current connector.
7. Reply **in Turkish**, remain skeptical, avoid redundant authorization questions and avoid creating MEGA-17 or new prompts reflexively. **When the Owner explicitly asks for a Codex prompt, deliver it only inside a Markdown codeblock.** The prior exact prompts are archived in Section 8.

### Expected next Owner update
Likely a MEGA-15/16 Google AI Studio completion, a Codex Projects V2 response, or a question about remaining work. Answer from live evidence rather than repeating the old task.

---

## 1. MISSION & UNBREAKABLE EVIDENCE / AUTHORITY RULES

**User goal:** Build a local-first/selectively hybrid system for a large ballet/dance/music/performing-arts video archive:

\`\`\`text
source/archive
  -> deterministic inventory + provenance
  -> semantic useful-moment retrieval
  -> source-native temporal refinement
  -> measured PTS/frame/timebase evidence
  -> actual human editorial decision
  -> versioned edit plan
  -> authorized render/export
  -> technical AND editorial QC
\`\`\`

Not a generic Gemini video analyzer. Source media remains immutable unless separately authorized; paths/provider IDs/vectors/UI IDs are not source identity. Keep both exact **source occurrence** and source **revision/bytes digest**. Identical bytes at different paths may represent distinct custody occurrences. Retrieval indexes and model embeddings are derived, replaceable projections, never the provenance/source-of-truth.

Five canonical assertion classes: \`MEASURED\`, \`MATCHED\`, \`VISUALLY_OBSERVED\`, \`AUDIO_OBSERVED\`, \`EDITORIAL_INFERENCE\`. \`NOT_OBSERVED\` is a marker, NOT a sixth evidence class. Do not silently upgrade an assertion's evidence strength.

**Temporal:** model/semantic/provider timestamps are candidate locators only, not edit boundaries. Exact cuts require measured native PTS/timebase/frame evidence. For VFR never infer frame with \`seconds × nominal FPS\`. The ISO-BMFF \`tkhd.track_ID\` and \`ffprobe selected_stream_index\` namespaces must not be equated by ordinal position. A-7 positive stream mapping and IT-6 terminal-tail unresolved cases stay fail-closed.

**Editorial:** generated candidate, review queue, proposal or fabricated PTS fixture is NOT authentic \`HumanDecisionArtifact\`, approved EditPlan, video render, editorial QC, source-native measured PTS or product outcome. Fixture numeric measurements can be internally \`MEASURED\` if explicitly \`SYNTHETIC_FIXTURE_ONLY\`, but real archive metrics and Gate promotion remain NOT_OBSERVED / NOT_AUTHORIZED.

**Four Gates**:
- Gate 0 — bounded diagnostic semantic retrieval vs metadata baseline; real protected archive, authentic editor queries, labels and human evaluation **deferred**.
- Gate 1 — representation/model/provider benchmark; LAB supports V1 SigLIP Base 768D, SigLIP2 Base 768D and SigLIP2 SO400M 1152D fake profile test semantics. **No authentic SigLIP2 benchmark/winner; tokenizer/processor/pooling and actual assets require independent proof and permission.**
- Gate 2 — reliability/scale mechanisms only from measured real bottlenecks. Generated recovery passes are not proof that distributed queue, ANN, Qdrant or cache is needed. Qdrant/LanceDB remain candidates.
- Gate 3 — measured source-native PTS → genuine human editor decision → plan → separately authorized render → technical + visual/audio editorial QC. Prepared synthetic refusal paths do NOT certify real Gate 3.

**Authority chain:** current explicit Owner instructions > governing verified canonical contracts/GitHub state > adopted architecture/specifications > approved design > plan > task packet > controller > worker. Prior chat summaries/handoffs are orientation. Do not manufacture permissions for real/protected source stat/read/hash/probe, video processing, model downloads, provider/API/egress, original code merges, production rendering/export or Gate promotion. No hard reset, git clean, force push, branch/worktree destruction or recovery-object pruning without express current approval.

---

## 2. TWO REPOS / BRANCHES — DO NOT CONFLATE THEM

### Original canonical repo (protected product authority)

\`https://github.com/Centaurioun/video-intelligence-pipeline\`  
\`main@592952daf475b1bbae2eebdee64d992c1a744f08\` independently verified before this handoff.

- This repo owns frozen Gate contracts, WBS/Atlas, rights/authorization, source/media policies and real release decisions. LAB cannot silently replace its \`main\` or broaden existing authority.
- **PR #258** \`S5-T1: bounded descriptor-based synthetic admission\`: \`OPEN / DRAFT / UNMERGED\`; HEAD \`5a60cd8e0abc021767b05c87ca50202822c049d0\`; current base \`592952...\`. A historical source review was \`COMMENTED\`, not \`APPROVED\`, no merge authorization. Its four Actions workflows/eight jobs on 2026-10-29 reported GitHub billing/spending restriction **before any test step**, so \`NOT_EXECUTED\`, not source-test failures. Owner reported exhausted Actions allowance. That historic billing blocker does not contradict later successful LAB CI.
- **PR #259** Oct-29 continuity handoff: \`OPEN / DRAFT / UNMERGED\`; HEAD \`e08382db65dcde703aadecc6ab329741f3c4b24c\`. Initial handoff from previous long conversation lives at \`docs/project/2026-10-29_CHATGPT_HANDOFF_POST_S5_T1_CANDIDATE.md\` on this unmerged SHA, NOT canonical main.
- **PR #231** Gate-3 G3.2.1 cross-corpus separation contract draft \`OPEN / DRAFT / UNMERGED\`; HEAD \`67a6e9ba91b401bf39b342d046ae678bdd2a5b97\`. Before using it, verify current base and shared-contract ownership.
- Adopted **H3-C05 v1.0.2** and **H3-A04 Option B v1.0.1** are *contract interpretations* from merged #222–225, NOT general product-source approval or completed Atlas nodes. Never ask Owner to re-adopt those exact decisions; never self-authorize H3 product implementations.
- Original main may contain historic experimental one-source real-media and ~320k-row generated-scale reports. They are bounded historical observations, NOT real full-archive Gate outcomes.
- The prototype \`prototypes/google-video-analyzer/\` is a preserved research/UI reference, not an accepted production Gemini/web server.

### LAB experimental repo (AI Studio current coding)

\`https://github.com/Centaurioun/video-intelligence-pipeline-2\`
- LAB \(not original\) is where Google AI Studio pushes new synthetic modules. AI Studio imports reduced ZIP without \`.git\`, so \`workspace_git_sha=NOT_OBSERVED\`; may lack pytest, pip/numpy or required Python versions. It writes tests but **does not execute pytest**, install packages, open real video, call models/FFmpeg/providers/cloud.
- GitHub Actions executes Python **3.11** and **3.14** regression suites. A model's static AST pass is NOT a behavioral CI PASS.
- AI Studio can only publish to LAB main. It has repeatedly deleted **six** \`src/gate0/media\` dependency files. Verify all:
  \`__init__.py\`, \`decode.py\`, \`probe.py\`, \`proc.py\`, \`source_guard.py\`, \`tool_identity.py\`.
  These are present in the verified latest pre-handoff LAB main. If subsequently deleted, compare exact old blob SHA and add the SIX originals only; never invent stubs or erase the new implementation with whole-tree rollback.
- Concurrent Codex work uses isolated worktree + exclusive audit branch writer. The audit branch \`codex/audit-mega08-14-20261104\` at remote \`ecc873794cb49ad0d79e4bf97bc0e13fc8938cbf\` contains **pre-remediation Phase B CHANGES_REQUESTED**, not final repaired acceptance. The next independent review must inspect the exact post-remediation code SHA.

---

## 3. VERIFIED RESULTS: MEGA-08–14 LAB TESTS GREEN, MEGA-15/16 NOT SUBMITTED

**MEGA-08–14 code certification reference:**
- Commit \`9bdd810bf14c93ed1f77243325beaa6b37b3e97d\`.
- GitHub Actions run \`41850619259\`: https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/41850619259
- Job logs: **350 selected tests PASS** separately on Python 3.11 and 3.14; sums verified from 16 actual suite step summaries per interpreter. No assertion about real videos or authentic models.
- Prior 307 baseline (MEGA-02 through MEGA-07 and existing suites) retained. MEGA-08 through MEGA-14 added candidate gap inventory, deterministic review queue, nonbinding PTS requests, unapproved proposal revision chain, generated-only recovery, QC refusal, and integrated single-/three-arm fake E2E.

**Historical debugging, do not repeat old prompts:**
- Wrong \`WorkloadSpec\` kwargs, wrong \`RecoveryHarness\` construction and nonexistent \`SimulatedCrash\`; invalid \`MeasurementSet.as_dict\`, forged \`MEASURED\` readiness, wrong \`FaultClass\` payload shapes and \`concurrency >1\` valid-round-trip fixtures; repeatedly missing six media dependencies after ZIP sync.
- GitHub-hosted CI and Codex diagnosis drove focused repairs. MEGA-08, 09, 10, 11, 12, 13, 14 later passed together. **MEGA-08–14 FINAL INDEPENDENT CODEX ACCEPTANCE has not been verified** and still should be arranged on exact immutable repaired SHA.
- Do not extrapolate \`350 PASS\` from \`9bdd810...\` to an arbitrary later commit without seeing that commit's test jobs.

**Present LAB task baseline:**
- LAB \`main@f0d06caa7ce1fd04c36d3edb1eb4df7e805f5eb7\` contains specification \`docs/ai-studio-tasks/MEGA_15_16_GATE3_OFFLINE_PREPARATION_PROGRAM.md\` (\`LAB-MEGA-15-16-v1.0.0\`, 126 lines) and \`.github/workflows/vip-ai-studio-synthetic-ci.yml\` three conditional new suites.
- Latest Actions \`41852069691\` https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/41852069691: Python 3.11 and 3.14 jobs **SUCCESS** for previous selected 350. **MEGA-15, MEGA-16, and MEGA-15/16 E2E test steps SKIPPED/NOT_SUBMITTED.** Green old checks do not certify new feature.
- As of this check, \`src/vip_lab/mega15/**\`, \`mega16/**\`, \`tests/vip_lab/test_mega15.py\`, \`test_mega16.py\`, \`test_mega15_16_end_to_end.py\` absent from LAB main. Do not claim they were created. Re-fetch after Owner's next AI Studio result.

**Four maturity layers:** \`AUTHORING_DELIVERED\` (code+tests present), \`HOSTED_SYNTHETIC_VERIFIED\` (exact SHA with named tests actually executed on both Python versions), \`INDEPENDENTLY_REVIEWED\` (fresh Codex source review of exact candidate), \`CANONICAL_ACCEPTED\` (separate explicit Owner adoption / original contract reconciliation). Never collapse these into "project finished."

---

## 4. CURRENT OWNER CHOICE: TWO MEGA WAVES, ONE ENGINEERING ASSIGNMENT

Owner expressly wants **MEGA-15 and MEGA-16 combined** as one large Google AI Studio task, following previous success with long prompts. **No human grading/evaluation/real source runs yet.** Real roadmap tasks 2–4 are postponed to the end; document their prerequisites only. Do not autonomously start UI, Gemini, provider, new backend, full ingestion, archive benchmark, production edit/export or new MEGA-17.

Source-of-truth specification: https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/main/docs/ai-studio-tasks/MEGA_15_16_GATE3_OFFLINE_PREPARATION_PROGRAM.md

**MEGA-15**: additive source-native temporal and editorial PRE-REVIEW software, closed hash-bound \`Gate3PreparationPacket\` or equivalent; consumes actual MEGA-09 CandidateReviewQueue, MEGA-10 TemporalRefinementRequest and MEGA-11 EditorialProposal. Reuse existing \`src/gate3\` PTS/timebase/temporal/refinement and \`src/vip_fvs\` contracts. Preserve occurrence/revision, generation, query, stream namespace, VFR/half-open end/tail ambiguity; reject forged human authority and false MEASURED proof. No actual PTS binding-eligible real edit or true HumanDecisionArtifact.

Expected new code: \`src/vip_lab/mega15/{__init__,temporal_preflight,editorial_handoff,lineage}.py\`; test: \`tests/vip_lab/test_mega15.py\`.

**MEGA-16**: generated-only render/export/QC **PREFLIGHT**, declarative \`ExportReadinessPacket\`, \`QCRequirementManifest\`, refusal report/CLI; consumes MEGA-15, MEGA-13, existing Gate-3 and vip_fvs. No FFmpeg, real preview/render, no fake QC PASS or human visual/audio findings; default \`production_export_authorized=false\`, \`export_status=REFUSED_NOT_AUTHORIZED\`. CLI rejects \`--real/--render/--export/--provider/--download/--upload\`, source URLs and forged evidence. E2E report verifies MEGA-09→10→11→13→15→16 provenance without status upgrades.

Expected new code: \`src/vip_lab/mega16/{__init__,render_preflight,qc_requirements,release_refusal,cli}.py\`; tests \`tests/vip_lab/test_mega16.py\`, \`test_mega15_16_end_to_end.py\`.

**Remaining preparation docs:** new \`docs/ai-studio-tasks/MEGA_15_16_PROGRESS.md\`, new \`MEGA_15_16_DEFERRED_REAL_PILOT_PREREQUISITES.md\`. The latter describes the future approvals for authentic original/LAB integration, rights/identity/source intake, Gate-0 D2/D3 human queries/labels, model assets, native PTS and human editor decision, render and QC. None executed now.

**Allowed writes:** only those new MEGA-15/16 modules/tests and two new task docs. Existing Gate modules, vip_fvs, MEGA-03–14, CI workflow, original VIP main are READ ONLY. If a real shared API defect is found, record it for Owner ruling; don't modify producer code to greenwash.

**Spec-mandated six refinement cycles:** 1 source/API inventory; 2 temporal/stream adversarial cases; 3 editorial identity/lineage; 4 export/QC/consent/privacy; 5 end-to-end producer/consumer integrity; 6 static, negative tests and readiness audit. Google AI Studio must write **test source first**, not execute pytest; CI after real LAB push checks three suites on both versions.

---

## 5. BACKLOG & GITHUB PROJECTS #2 — THREE ISSUES VERIFIED, BOARD ITEMS NOT VERIFIED

Board https://github.com/users/Centaurioun/projects/2  
Original setup Issue #236 https://github.com/Centaurioun/video-intelligence-pipeline/issues/236 is CLOSED; its latest triage comment records the desired field mapping, but closure is not proof that the new cards are linked.

Three **OPEN issues created and verified** on the original canonical repository:
- [#260](https://github.com/Centaurioun/video-intelligence-pipeline/issues/260): **Backlog / P2 / Orchestration / PENDING**. Design trustworthy structured processing logs, actual stage status, attributable progress/receipt. Avoid duplicating existing deferred watchdog Issue [#235](https://github.com/Centaurioun/video-intelligence-pipeline/issues/235).
- [#261](https://github.com/Centaurioun/video-intelligence-pipeline/issues/261): **Backlog (deferred) / P3 / Ideas / NOT_OBSERVED**. Local-first video review dashboard, file/source selector, stage visualization, real status/candidate time uncertainty. No mock progress, no new Express/backend until approved design.
- [#262](https://github.com/Centaurioun/video-intelligence-pipeline/issues/262): **Backlog (conditional) / P3 / Security/Policy / NOT_OBSERVED**. Provider-neutral secure credentials; Gemini is optional, never required to boot a local pipeline. Check env presence offline; actual key validity/network usage requires explicit provider authorization.

Original 17 Google AI Studio suggestions were triaged/deduplicated: keep legitimate observability, later UI, optional provider secrets; defer URL video intake until source rights/SSRF/egress/retention policy; reject new parallel Node Express backend, \`src/components/services/utils\` re-scaffold, direct mandatory Gemini frame-sampler or \`fluent-ffmpeg\` duplicate FFmpeg path, fake upload/queue/progress.

**Outstanding bookkeeping:** whether #260–262 are actual GitHub Projects V2 items with verified custom field values is \`NOT_OBSERVED / PENDING\` in this connector. A separate local Codex CLI/GraphQL prompt exists in the prompt archive below. No evidence yet that Owner sent it or Codex completed it. Do NOT assert cards are added from Issue creation alone.

---

## 6. DEFERRED WORK / PRODUCT COMPLETION — NO SYNTHETIC SHORTCUTS

The previously discussed large workstreams were: 1 synthetic LAB; 2 LAB-original selective integration; 3 source rights/inventory; 4 real Gate-0 semantic benchmark/human labeling; 5 authentic Gate-1 model comparison if justified; 6 PTS/editoryal Gate-3; 7 render/export/QC; 8 real Gate-2 scale; 9 product UI. Owner requests **software-only infrastructure** for 6+7 now via MEGA-15+16, and explicitly puts **2+3+4** actual operations/evaluation later; 5+8 conditional. No benchmark, human judgment, real source processing or production editing in this development round.

**The final real product remains NOT_COMPLETE even when MEGA-15/16 CI is green.** To cut usable real clips: authentic source rights/identity, measured PTS/timebase, model capability/outcome, actual reviewer decision, versioned plan, authorized renderer/export, technical+visual/audio editorial QC must all occur under their own grants. Do not claim approximate project completion from percentage of written Python files. Earlier informal estimate "5–7 more major blocks for pilot, 8–12 for polished product" was only conversational planning and may change with measured real outcomes.

---

## 7. HOW TO COLLABORATE (OWNER PREFERENCES & SUPERPOWERS)

- Speak with Owner in **Turkish**. The user prefers direct, critical, technically rigorous responses and large bounded tasks over dozens of artificial one-step prompts. Challenge unsupported AI Studio success claims. Do not repeat questions already answered in this handoff.
- When asked to generate a future **Codex** prompt, only Markdown codeblock (English engineering instructions unless new Owner preference changes). The old Codex reports generally use English technical artifacts while Turkish chat summaries are appropriate; verify current AGENTS.md language constraints.
- Use **Superpowers** skills as needed, not as a ceremonial list: brainstorming for new architecture/behavior design; writing-plans after design approval; using-git-worktrees for isolated implementation; test-driven-development for code changes; systematic-debugging before fixes; requesting/receiving-code-review; verification-before-completion for success claims. No manufactured agents just to fill slots.
- Useful dependency-safe parallelism: AI Studio owns LAB main implementation; independent Codex owns separate audit worktree and original Projects bookkeeping. Only one integration owner; verify immutable candidate SHA and GitHub CI before promotion.
- GitHub source authority always supersedes this documentation. If the Owner pastes an agent response, compare actual before/after GitHub diff, CI jobs/logs and source API; distinguish \`VERIFIED\`, \`SOURCE_INSPECTED\`, \`OWNER_REPORTED\`, \`NOT_OBSERVED\`, \`BLOCKED\`, \`NOT_AUTHORIZED\`.
- Read-only documentation planning does not grant original source modifications. Do not update original canonical \`main\` simply to synchronize LAB narrative; separate decision and Owner approval needed.

---

## 8. SIX CYCLE ITERATIVE HANDOFF REFINEMENT (DOCUMENTATION SELF-AUDIT)

1. **Baseline reconnaissance:** compared GitHub original \`main@592952...\` and LAB \`main@f0d06ca...\`, original canonical handoffs/WBS and current MEGA-15/16 task spec instead of trusting prior summaries.
2. **Provenance & scope:** pinned genuine 350/350 hosted CI to \`9bdd810...\`, distinguished later docs/CI-only main; separated draft PRs from adopted contracts and real production authority.
3. **Dependency and capability:** kept MEGA-15/16 as thin consumers of existing PTS/edit/QC engines; no new invented renderer, model or scheduler. Preserved separate Projects task.
4. **Adversarial safety:** checked repeated six-file ZIP deletions, real source/media restrictions, incomplete positive A-7 mapping, false reviewer/gate/MEASURED upgrades and skipped CI steps.
5. **Handoff usability:** included two executable prior prompts verbatim in a later section, with exact links/SHA and fast-start instructions; user will not need to recount prior chat.
6. **False-completion challenge:** kept MEGA-08–14 CI PASS separate from not-yet-done independent review; MEGA-15/16 NOT_SUBMITTED distinct from latest successful CI; Issues verified distinct from unobserved GitHub Projects item status.

This is a Superpowers-informed self-review, **not** a claim that an independent Codex or subagent reviewed this handoff, or that MEGA-15/16 were executed. The Owner's explicit request was to write a durable handoff now; this is a **documentation artifact only**. New architecture/work implementation still requires normal approval gates.

---

## 9. PRIMARY SOURCE LINKS

Original canonical:
- https://github.com/Centaurioun/video-intelligence-pipeline
- https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/project/00_PROJECT_CHARTER.md
- https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/project/01_CURRENT_STATE_AND_HANDOFF.md
- https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md
- https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/project/STATE_MAINTENANCE_PROTOCOL.md
- https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md
- https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/architecture/CANONICAL_CONTRACTS.md
- https://github.com/Centaurioun/video-intelligence-pipeline/pull/258
- https://github.com/Centaurioun/video-intelligence-pipeline/pull/259
- https://github.com/Centaurioun/video-intelligence-pipeline/pull/231
- https://github.com/Centaurioun/video-intelligence-pipeline/blob/e08382db65dcde703aadecc6ab329741f3c4b24c/docs/project/2026-10-29_CHATGPT_HANDOFF_POST_S5_T1_CANDIDATE.md

LAB:
- https://github.com/Centaurioun/video-intelligence-pipeline-2
- https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/41850619259
- https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/41852069691
- https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/main/docs/ai-studio-tasks/MEGA_15_16_GATE3_OFFLINE_PREPARATION_PROGRAM.md
- https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/main/docs/ai-studio-tasks/MEGA_08_14_PROGRESS.md

Projects:
- https://github.com/users/Centaurioun/projects/2
- https://github.com/Centaurioun/video-intelligence-pipeline/issues/236
- https://github.com/Centaurioun/video-intelligence-pipeline/issues/235
- https://github.com/Centaurioun/video-intelligence-pipeline/issues/260
- https://github.com/Centaurioun/video-intelligence-pipeline/issues/261
- https://github.com/Centaurioun/video-intelligence-pipeline/issues/262

Superpowers:
- https://github.com/obra/superpowers
- https://github.com/openai/plugins/tree/main/plugins/superpowers

---

## 10. PROMPT ARCHIVE AND NEW-SESSION ENTRYPOINT

See the **next appended sections** for the two exact latest prepared prompts: combined Google AI Studio MEGA-15/16 implementation and local Codex Projects V2 issue linking. Their presence in GitHub is only an archival copy; there is **no confirmed evidence they were sent or executed**.

**Next ChatGPT first answer should be a short live-state verification in Turkish and then proceed with the Owner's new message. No reflexive new MEGA task.**


## 11. LAST PREPARED GOOGLE AI STUDIO PROMPT — MEGA-15 + MEGA-16

**Historical prompt status:** prepared for the Owner; actual delivery/execution by Google AI Studio NOT_OBSERVED at this checkpoint. Version and SHA below were verified at prompt authoring. Recheck live main before reissuing; if already submitted, do NOT duplicate work.

\`\`\`text
VIDEO INTELLIGENCE PIPELINE — MEGA-15 + MEGA-16

Execute the complete engineering program:

docs/ai-studio-tasks/MEGA_15_16_GATE3_OFFLINE_PREPARATION_PROGRAM.md

Required version: LAB-MEGA-15-16-v1.0.0

Verified starting LAB main:
f0d06caa7ce1fd04c36d3edb1eb4df7e805f5eb7

Implement MEGA-15 and MEGA-16 as ONE comprehensive assignment.

Primary objectives

MEGA-15: Gate-3 source-native temporal preparation, editorial handoff, lineage validation and fail-closed refusal boundaries.

MEGA-16: Render/export/QC preflight infrastructure, readiness reports, technical and editorial evidence requirements, and synthetic end-to-end integration.

Reuse existing Gate-3 and vip_fvs implementations. Do not duplicate established PTS, human-decision, edit-plan, FFmpeg or QC engines.

Explicitly deferred

Do not perform real video processing, real source inventory, real model inference, benchmark evaluation, human editorial evaluation, actual render/export or Gate promotion.

Prepare only the prerequisites for roadmap steps 2, 3 and 4. Preserve every missing human or source measurement as NOT_OBSERVED.

Development requirements

Follow the full specification, six refinement cycles, test-first source authoring, adversarial tests, exact source contracts and strict authorization boundaries.

Do not modify the original VIP repository, canonical Gate modules, existing MEGA-03–14 code, or GitHub Actions.

Write all required MEGA-15/16 Python modules, tests, cross-wave integration and progress documents.

Do not run pytest or access real media, FFmpeg, models, providers or network services in AI Studio.

When publishing to LAB main, preserve all existing files, especially the six src/gate0/media dependency modules. Report any unexpected deletion.

Do not claim completion until the new suites actually pass hosted CI on Python 3.11 and 3.14.

At the end, respond in Turkish with implemented capabilities, tests authored, reused source contracts, unresolved blockers and exact continuation point.

Begin the complete assignment now.
\`\`\`

## 12. LAST PREPARED LOCAL CODEX PROMPT — GITHUB PROJECTS V2

**Historical prompt status:** prepared for the Owner, not independently confirmed to have been executed. Requires a local authenticated GitHub CLI/GraphQL environment with Projects V2 permissions. Only Project items/fields are in scope, not source code.

\`\`\`text
Update the existing GitHub Projects V2 board:

https://github.com/users/Centaurioun/projects/2

Repository:
Centaurioun/video-intelligence-pipeline

Read Issue #236 and its latest project-triage comment.

Add the following existing issues to Project #2, only if not already linked:

- #260 — Backlog, P2, Orchestration, PENDING
- #261 — Backlog, P3, Ideas, NOT_OBSERVED
- #262 — Backlog, P3, Security/Policy, NOT_OBSERVED

Use authenticated GitHub CLI / GraphQL Projects V2 functionality.

Do not duplicate project items, create new issues, modify application code, change canonical Gate states or modify project configuration beyond the specified items and fields.

Verify the three actual project item IDs, statuses and field values.

If your authentication lacks project permissions, report the exact blocker without claiming success.

Respond briefly in Turkish.
\`\`\`

## 13. INDEPENDENT REVIEW AND HISTORICAL PROMPT SAFETY

Prior MEGA-12/14 bugfix prompts about \`SimulatedCrash\`, \`WorkloadSpec\`, \`FaultClass\`, fake \`Measurement\` promotion and \`concurrency\` are **historical/superseded** after the 350/350 genuine hosted CI at \`9bdd810...\`. Their authoritative remediation design/progress texts are in \`docs/ai-studio-tasks/MEGA_08_14_HOSTED_CI_REMEDIATION_2026-11-04.md\` and \`MEGA_08_14_PROGRESS.md\`. Do NOT run old remediation prompts merely because they are preserved.

**Independent Codex MEGA-08–14 Phase C remains pending,** and it must verify the final 350-test SHA and actual code diff, not reapply old pre-remediation findings. **MEGA-15/16 has no authored code** at this handoff. Never treat docs-only commits or old CI runs as evidence of a future task.

### Suggested minimal prompt for the next NEW ChatGPT instance

\`\`\`text
Video Intelligence Pipeline projesine bu GitHub handoff'unu eksiksiz okuyarak devam et:
https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/main/docs/project/2026-11-04_CHATGPT_HANDOFF_POST_MEGA14_PRE_MEGA15_16.md

Önce orijinal VIP ve LAB depolarının güncel main, açık PR, GitHub Actions ve Projects durumlarını bağımsız doğrula. Handoff'taki çalışma şeklini, MEGA-08–14 kanıt sınırlarını, MEGA-15/16 planını, Google AI Studio/Codex iş bölüşümünü ve tüm yetki kurallarını koru. Benimle Türkçe konuş; önceki soruları tekrar sorma. Şimdilik yeni Codex promptu üretme. Bir sonraki sonucumu verdiğimde kaldığımız noktadan devam et.
\`\`\`

**End of dated handoff. The next model must verify live mutable facts again.**
