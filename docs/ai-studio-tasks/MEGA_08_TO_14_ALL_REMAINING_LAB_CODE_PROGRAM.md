# VIDEO INTELLIGENCE PIPELINE — GOOGLE AI STUDIO LAB
# MEGA-08 → MEGA-14: ONE-TURN REMAINING CODE-CAPABLE PRODUCT PROGRAM

**Version:** LAB-MEGA-08-14-v1.0.0
**Date:** 2026-11-04
**Target:** Centaurioun/video-intelligence-pipeline-2, LAB main only
**Protected:** Centaurioun/video-intelligence-pipeline, canonical main
**Verified lab starting commit:** 22f1ffa7064f697d4049e39587945b1decabec4e
**Historical GitHub CI:** run 41756569162, 307 tests PASS per Python 3.11 and Python 3.14
**Mode:** Google AI Studio writes code + test source but does NOT execute pytest or Git pushes
**Parallel:** local Codex audits immutable commits in a separate worktree/branch, never writes LAB main

## 0. Mission and explicit authorization boundary

The Owner wants ONE very large AI Studio task spanning all remaining **code-capable, dependency-safe laboratory integration**. Attempt MEGA-08, 09, 10, 11, 12, 13 and 14 in one authoring request. Proceed independently when another wave is genuinely blocked. The measure of success is inspectable, source-backed code, NOT the count of generated files.

Target long-term chain:

source/archive -> inventory and provenance -> semantic useful-moment retrieval -> source-native temporal refinement -> measured PTS/frame evidence -> human editorial decision -> versioned edit plan -> render/export -> technical/editorial QC.

The LAB may only build model-free, media-free, generated-only integration seams and refusal checks for that chain. It may not create real source permissions, authentic model weights, human decisions, measured video evidence, render or production output.

**The seven waves:**

- MEGA-08: source capability matrix, genuine-gap/duplicate filter and contract boundaries.
- MEGA-09: retrieval report -> exact-provenance candidate review queue.
- MEGA-10: review candidate -> source-native temporal refinement *request*, with synthetic PTS diagnostics only.
- MEGA-11: candidate + temporal request -> versioned, unapproved editorial *proposal*; never an actual human decision or edit plan.
- MEGA-12: generated-only fault, replay and stage-digest consistency.
- MEGA-13: QC evidence-completeness and release/export refusal.
- MEGA-14: real integration of the preceding LAB modules and existing product query seams into one synthetic-only CLI/report and adversarial end-to-end test.

Do not automatically start an eighth wave. Conditional remaining-code work appears in Section 15: only implement verified, safe, genuinely missing functionality; classify blocked real-Gate work as blocked, not completed.

**What counts as success:** per-wave useful implementation and regression test source -> IMPLEMENTED_UNVERIFIED. Actual green GitHub-hosted pytest and separate Codex review happen after Owner-controlled push. No LAB package promotes an original four-Gate checklist.

## 1. Baseline hard gate: do not work on obsolete ZIP

The LAB main was safely fast-forwarded without force to verified feature head 22f1ffa7064f697d4049e39587945b1decabec4e prior to creating this document. Previous work on older LAB main produced incorrect source assumptions and lost required files. The current workspace MUST contain the latest verified code, NOT just an old ZIP with this new document copied into it.

Before writing ANY code, inspect ALL these:

1. docs/ai-studio-tasks/MEGA_03_07_PROGRESS.md contains CI evidence for 307 tests, run 41756569162 and the verified remediation commit.
2. All six source dependency files exist under src/gate0/media/: __init__.py, decode.py, probe.py, proc.py, source_guard.py, tool_identity.py.
3. src/vip_lab/mega05/model_assets.py uses model_space.semantic_space_id(SemanticSpace), not dict-style indexing into the result of profile_semantic_space.
4. src/vip_lab/mega06/recovery_matrix.py uses actual gate2.faults FaultClass and capability states; nonexistent enum names were removed.
5. src/vip_lab/mega07/candidate_temporal_gate.py keeps generated-only PTS evidence NOT_OBSERVED and binding_eligible false.
6. src/vip_fvs/query_batch.py, synthetic_profiles.py, batch_retrieval.py, three_arm_batch.py and batch_report.py are present.
7. Existing 03–07 tests and tests/vip_lab/test_cross_gate_integration.py and test_lab_cli.py are present.
8. The remote GitHub LAB main still has .github/workflows/vip-ai-studio-synthetic-ci.yml. Never delete this workflow during ZIP synchronization.

If any condition 1–7 is false: STOP without implementing code and report TASK_BASELINE_NOT_SYNCED with paths. The Owner must reimport the current LAB main ZIP. If .git is absent, report SHA as NOT_OBSERVED locally; code-signature checks can establish compatibility but cannot magically prove a Git commit identity. Never recreate the missing old source using imagination.

Historical exact baseline evidence on the cited commit: 267 original synthetic tests, MEGA-03 13, MEGA-04 6, MEGA-05 5, MEGA-06 6, MEGA-07 6, cross-gate/CLI 4, totaling 307 per Python version. These figures are NOT results for your future edits.

## 2. Governing authority and original-repo blockers

Read the currently imported AGENTS.md and these project files where present:

- docs/project/00_PROJECT_CHARTER.md
- docs/project/01_CURRENT_STATE_AND_HANDOFF.md
- docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md
- docs/project/STATE_MAINTENANCE_PROTOCOL.md
- docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md
- docs/decisions/2026-10-29-a7-s5-scoped-synthetic-tdd-plan-owner-adoption.md
- docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md
- docs/migrations/siglip2-post-completion/32_PROVISIONAL_SIGLIP2_TOKENIZER_PROCESSOR_POOLING_CONTRACT.md

Canonical original main at this plan's creation: 592952daf475b1bbae2eebdee64d992c1a744f08. The original repo is protected and must not be changed here.

Do NOT try to silently resolve these higher-authority prerequisites:

- Original PR #258 S5-T1 bounded-admission implementation is OPEN/DRAFT. No parallel duplicate S5 admission in this LAB. Further S5 T2 parser/caller source writes need exact separate grants; T3 E01 budget decisions may block subsequent implementation.
- A-7 positive FFprobe-global index vs ISO-BMFF track mapping is not adopted. Do not infer identity from matching ordinals.
- H3-C05 versioned successor and H3-A04 signer interpretation are proposals; a LAB success does not grant frozen core implementation.
- Gate-0 D-2 lacks real Owner/corpus/editor/reviewer/model/host evidence; D-3 protected execution NOT_AUTHORIZED.
- Gate-1 actual SigLIP2 tokenizer/processor/pooling and native runtime NOT_OBSERVED; Gate B NO_GO_BLOCKED.
- Gate-2 representative real archive workload NOT_OBSERVED; no measured justification for ANN/cache/queue or persistence mechanisms.
- Gate-3 source-native measured media timing, actual editorial judgment, real render and production QC require separate approvals.
- H3-A03–A07, B04/B05, C05, D02/D05 and G01–G03 statuses remain canonical decisions, not LAB report fields.

If code cannot be written without one of these authority events, mark BLOCKED_SCOPE with the exact dependency and proceed to another independent wave. Never fabricate a grant.

## 3. Superpowers-inspired method: one prompt, independent packets

Use Superpowers skills only when triggered:

- Brainstorming: inspect existing source, question need, list duplication/authority alternatives and choose smallest useful new contract.
- Writing-plans: each wave must have a known producer, new consumer, typed output and positive/negative tests.
- Test-driven-development: author intended regression tests first; because the Owner forbids AI Studio pytest execution, mark RED and GREEN as NOT_EXECUTED locally. True execution takes place in GitHub Actions afterward.
- Systematic-debugging: when a source mismatch appears, inspect call chain and exact signatures before changing code, never change tests only to hide a real defect.
- Using-git-worktrees, dispatching-parallel-agents and subagent-driven-development: only when genuine independent local workers are available, and never fake Git history/agents in the ZIP environment.
- Requesting-code-review, receiving-code-review and verification-before-completion: local Codex later reviews exact immutable LAB commits on a separate branch; CI and review are separate conditions.

One-turn authoring order: verify baseline -> prepare progress ledger -> P08 -> P09 -> P10 -> P11 -> P12 -> P13 -> P14 -> conditional stretch gaps -> static review -> Turkish report. P12 can proceed if an earlier wave is blocked. Do not ask the Owner to repeat already-known preferences or turn this into seven separate initial prompts.

**No pytest, no unittest runner, no package install, no network, no actual model, no media, no FFmpeg/FFprobe, no GitHub push, no canonical repo write.** Offline ast.parse / compile syntax-only checks are allowed and NEVER count as runtime PASS.

## 4. Write ownership and tests

Only these new paths may be written:

- src/vip_lab/mega08/ through src/vip_lab/mega14/ (new lab-only subpackages, each __init__.py).
- tests/vip_lab/test_mega08.py through test_mega14.py (seven per-wave suites).
- tests/vip_lab/test_mega08_14_end_to_end.py (cross-wave integration test).
- docs/ai-studio-tasks/MEGA_08_14_PROGRESS.md (durable new progress ledger).

Optional existing LAB edit ONLY if exact necessity is source-proven and defended by regression: src/vip_lab/integration.py or src/vip_lab/cli.py. Prefer an isolated new src/vip_lab/mega14/cli.py so previous 03–07 code stays intact.

Forbidden edits: all .github/**; all src/gate0/**, gate1/**, gate2/**, gate3/**, vip_fvs/**; existing src/vip_lab/common.py and mega03/** through mega07/**; existing 03–07 tests; experiments/**; schemas/**; config/**; requirements/**; docs/project/**; docs/decisions/**; original WBS/Atlas and protected repo; source/media and model assets.

The new wave names are LAB engineering labels, not official canonical WBS IDs. If a proposed subpackage would only duplicate an existing well-tested function, record NOT_NEEDED with exact path/symbol and do not manufacture filler source.

**Atomic packet ownership:** one writer per file, one test suite per wave. P14 is sole writer of its CLI/report. No new generic shared framework that undermines src/vip_lab/common.py. Never import all new wave packages eagerly in src/vip_lab/__init__.py; each wave must collect tests independently if a downstream wave fails.
