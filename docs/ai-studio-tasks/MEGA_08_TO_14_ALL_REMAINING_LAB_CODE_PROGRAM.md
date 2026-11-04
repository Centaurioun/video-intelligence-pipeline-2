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


## 5. Evidence, provenance and no-side-effects invariants (all waves)

The five canonical assertion evidence classes are MEASURED, MATCHED, VISUALLY_OBSERVED, AUDIO_OBSERVED and EDITORIAL_INFERENCE. NOT_OBSERVED is a state marker, NOT a sixth assertion class.

Never infer VFR frame ordinal with seconds multiplied by nominal FPS. Semantic/model timestamps are CANDIDATE evidence only; preserve source_sample_pts as exact integer and source_timebase_num/source_timebase_den as a rational locator, not exact clip cut endpoints. Do not choose an ambiguous duplicate PTS occurrence without source-native ordinal evidence. End boundary uses existing half-open policy; never change gate3.temporal.

Keep source media immutable. No opening, stat-ing, hashing, probing, decoding, transcoding, exporting or uploading source files. Manifest paths in generated fixtures are opaque synthetic identifiers, even when ending .mp4. No model assets or PyTorch sessions. No network or provider access.

Inputs are untrusted: a declared source SHA is not a rehashed source; a report_digest is self-consistency not independent observation; a user-provided owner_signed/approved/MEASURED/QC_PASS flag grants nothing. Stream FFprobe index, BMFF track index/ID and source revision have distinct identities.

Model spaces are separate: V1 SigLIP Base 768D (cpu/v1-float32), V2 SigLIP2 Base 768D, SO400M SigLIP2 1152D (4608-byte float32 rows). V1 and V2 Base are incompatible despite equal dimensions. Never compare fake cosine scores cross-arm to select a winner.

No success report may assert real human acceptance, measured edit boundaries, model winner, authenticated Owner, production export or four-Gate promotion. On invalid identity/sha/model-space/timing/query/candidate/report, fail the whole atomic result; do not drop corrupt rows while reporting SUCCESS.

Suggested lab readiness report fields: exact version, stage_id, synthetic_only=true, execution_authorized=false, evidence_state=NOT_OBSERVED where appropriate, upstream digest identities, ordered entries, limitations, stable refusal reasons, canonical JSON SHA-256. Reuse the existing ReadinessPacket/canonical serializer; do not create a second general framework.

Every test wave must include at least one positive generated-only case, one adversarial refusal and one spy ensuring no forbidden side effects. Correct API calls matter more than the length of the code.

## 6. Existing verified producer contracts to inspect and REUSE

Before each new function, inspect complete source definitions, dataclass fields and corresponding existing tests. These are actual LAB/source seams, but signatures must be reverified in the imported workspace.

- src/vip_fvs/query_batch.py: QueryCatalog, QueryCatalogItem, catalog digest, ordered distinct_texts, bounded top_k.
- src/vip_fvs/synthetic_profiles.py: CLOSED_SYNTHETIC_PROFILE_IDS, make_synthetic_profile, build_synthetic_profile_runtime and closed identities.
- src/vip_fvs/batch_retrieval.py: BatchCandidateRecord, BatchQueryResult, SingleArmBatchResult, run_batch_retrieval.
- src/vip_fvs/three_arm_batch.py: ThreeArmBatchResult and run_three_arm_batch.
- src/vip_fvs/batch_report.py: build_single_arm_batch_report, build_three_arm_batch_report, verify_batch_report, serialize_batch_report.
- src/vip_fvs/multi_source_retrieval.py: retrieve_multi_source (text sequence support), exact manifest locator+digest binding.
- src/vip_fvs/source_adapter.py: MultiSourceManifest and SourceManifestEntry.
- src/vip_fvs/semantic_index.py: SemanticIndexEngine, persisted generation identities, read-only query. No indexing during the query stage.
- experiments/persistent_local_index/model_space.py: semantic_space_id(SemanticSpace) returns canonical semantic identity; SemanticSpace is NOT a dictionary.
- src/vip_lab/common.py: ReadinessPacket, ReadinessFinding, canonical JSON and strict lab JSON loading.
- src/vip_lab/mega03/: S5 metadata-only refusal, stream namespace refusal, ReviewBundle check. Never activate S5 source-byte admission.
- src/vip_lab/mega04/: D-2 Owner-input/40-query/reviewer/freeze readiness. No fake genuine editor authorship.
- src/vip_lab/mega05/: three-profile model assets and runtime permission state. No authentic model.
- src/vip_lab/mega06/: WorkloadSpec, FaultClass capabilities, RecoveryHarness/Measurement generated-only reporting.
- src/vip_lab/mega07/: inspect_candidate_temporal, inspect_editorial_lineage, inspect_qc_export_readiness.
- src/vip_lab/integration.py, src/vip_lab/cli.py: existing MEGA-03–07 summary and CLI; do not rewrite.
- src/gate3/pts.py: PtsTable(TimeBase(num, den), ticks); ordinal_of(tick, occurrence=...), is_ambiguous(tick).
- src/gate3/temporal.py: resolve_start, resolve_end (first tick strictly after requested end), classify_vfr, detect_discontinuity.
- src/gate3/rational.py: Rational(numerator, denominator), TimeBase(num, den).
- src/vip_fvs/review_bundle.py, human_decision.py, real_plan.py: authority-bearing consumers; read-only study, NOT permissive synthetic output producers.
- src/gate3/qc.py: bare_pass_is_insufficient(record); do NOT invoke source-bound may_consume_for_binding_origin without real attestation.
- src/gate2/workload.py, recovery.py, faults.py and measure.py: generated-only helpers with exact constructors, enums and capability guards.

Previous AI Studio bugs to prevent: nonexistent CLOSED_PROFILE_IDS, ModelProfile.model_family, profile_semantic_space()["space_id"], incorrect IndexSummary fields, Rational.num, extra PtsTable stream arg, Measurement(status=...), nonexistent FaultClass members, incorrect keyword-only reviewer envelope args, missing gate0.media from destructive ZIP sync. Use tests and source AST to verify these before coding.

## 7. MEGA-08 — CAPABILITY AND GAP INVENTORY

Goal: produce a small, executable LAB capability map so future integration never assumes missing features or silently promotes model-free lab evidence to canonical Gate completion.

New files (only where a real gap is proved):
- src/vip_lab/mega08/__init__.py
- src/vip_lab/mega08/capability_inventory.py
- src/vip_lab/mega08/contract_gate.py
- src/vip_lab/mega08/gap_digest.py
- tests/vip_lab/test_mega08.py

Design:
1. Accept a closed input manifest of desired LAB capabilities and explicit trusted source-code path identifiers; do not scan arbitrary working-tree paths, video archives or network.
2. Classify each capability into IMPLEMENTED_IN_SOURCE, COVERED_SYNTHETIC, GAP_CODE_CAPABLE, BLOCKED_BY_AUTHORITY, NOT_OBSERVED; distinguish a source symbol from a behavioral CI observation.
3. Read only allowlisted Python source text via safe bounded path APIs or AST where needed. Never import source modules during static inventory (avoid accidental side effects).
4. Validate exact producer symbols, module identities and optional contract shape; no fabricated success from the presence of a named Python file alone.
5. Include a source-referenced explanation, declared authority limitations and stable deterministic SHA-256 of the gap report.
6. Reject unsupported paths, unknown capabilities, duplicate IDs, forged accepted PR/status flags and self-issued Gate grants.
7. Provide a read-only relationship table to canonical H3 nodes as ADVISORY only; no updates to Atlas/WBS/PRs or implicit source write authorization.
8. If existing code already produces an equivalent truthful inventory, prefer a thin additive checker/test or NOT_NEEDED with precise source evidence; no generic new plugin framework.

Tests: stable source identity, missing reference, forbidden path, duplicate capability, deterministic sorting, forged source-authorization input, zero model/media/network I/O, no hidden import-time execution.

Deliverable value is a real mismatch detector, not a report that merely echoes supplied user JSON.

## 8. MEGA-09 — BATCH RETRIEVAL TO NONBINDING REVIEW QUEUE

Goal: connect the existing query/catalog/batch-report producer to a human-review candidate intake without inventing human decisions.

New files:
- src/vip_lab/mega09/__init__.py
- src/vip_lab/mega09/candidate_queue.py
- src/vip_lab/mega09/queue_validation.py
- src/vip_lab/mega09/review_intake.py
- tests/vip_lab/test_mega09.py

Requirements:
1. Accept a previously verified batch report or actual BatchCandidateRecord/SingleArmBatchResult data; use current types and verify upstream digest, profile identity and generation ID before queueing.
2. Preserve exact query_id, arm ID, ranked order, candidate source_path/source_sha256, revision_id, source_sample_pts, source_timebase_num and source_timebase_den. Use actual current producer fields.
3. Derive deterministic candidate ID from query ID + arm ID + source occurrence identity + revision + sample PTS/timebase + upstream report identity. Same content bytes at two distinct paths remain two occurrences. Two query IDs containing identical text remain separate reviews.
4. Keep evidence_class=MATCHED, binding_eligible=false, review_state=NOT_REVIEWED, human_decision_state=NOT_OBSERVED.
5. Never add a reranker, cross-arm score normalization or synthetic model winner.
6. Refuse missing query/arm, stale generation ID, wrong manifest binding, duplicate candidate ID, rank inconsistency, NaN scores, forged source digest or tampered batch report.
7. Do not execute index_source or modify source/index; only read validated existing results. No synthetic source path dereference.
8. Emit canonical, versioned, digest-bound ordered queue; test serialization round-trip and byte-identical replay.

Tests: 1/2/64 query records (bounded), duplicate text with distinct query IDs, two byte-identical source occurrences, distinct 768D model spaces, 1152D SO400M, exact rational PTS, source revision swap, bad digest, no-media/no-index-write spies.

## 9. MEGA-10 — CANDIDATE TEMPORAL REQUEST AND SOURCE-NATIVE DIAGNOSTIC

Goal: separate a semantic useful-moment candidate from any future exact source-native cut. This LAB provides a request and generated-only PTS-policy diagnostics, not measured edit boundaries.

New files:
- src/vip_lab/mega10/__init__.py
- src/vip_lab/mega10/temporal_request.py
- src/vip_lab/mega10/pts_fixture_diagnostics.py
- src/vip_lab/mega10/measurement_boundary.py
- tests/vip_lab/test_mega10.py

Requirements:
1. Consume MEGA-09 candidate ID and exact upstream queue/source revision/stream identity, never a free-floating timestamp.
2. Produce temporal_refinement_request with measurement_needed=true, source_pts_evidence_state=NOT_OBSERVED and binding_eligible=false.
3. For generated numeric fixture PTS only, call existing PtsTable(TimeBase(num, den), ticks), resolve_start/end and rational conversions. Keep diagnostic status SYNTHETIC_DIAGNOSTIC_ONLY, NOT MEASURED.
4. Half-open end: if request is tick 180000 and fixture has ticks 180000 and 183000, resolved end is 183000, not 180000.
5. Duplicate PTS without occurrence/ordinal proof is ambiguous and must refuse binding. Nonmonotonic PTS or invalid timebase refuse. Preserve nonzero and unusual origin ticks.
6. Never calculate frame ordinal as seconds times nominal FPS, including VFR or misleading nominal-rate inputs.
7. Distinguish ffprobe global index, ISO-BMFF track ordinal/ID and source-bound stream identity; no invented positive mapping.
8. A missing measured source snapshot or rev mismatch blocks actual refinement and next editorial binding; no fallback to an inferred seconds interval.
9. No source bytes, probe, decode, human decision or real plan writes.

Tests: PTS 1001/30000, duplicate/nonmonotonic, nonzero start, half-open end, source/stream swap, candidate ID tamper, generated-only NOT_OBSERVED evidence, no downstream edit/render calls.

## 10. MEGA-11 — VERSIONED EDITORIAL PROPOSAL, NOT AN EDIT PLAN

Goal: create an editor-readable inert proposal and immutable revision lineage; keep actual human editorial decisions separate and unforgeable.

New files:
- src/vip_lab/mega11/__init__.py
- src/vip_lab/mega11/editorial_proposal.py
- src/vip_lab/mega11/proposal_revisions.py
- src/vip_lab/mega11/decision_boundary.py
- tests/vip_lab/test_mega11.py

Requirements:
1. Accept only validated MEGA-09 queue and MEGA-10 request, retaining their exact digests, source revisions, candidate IDs, stream identity and model spaces.
2. Produce deterministic proposal_id/version/parent_digest, ordered candidate sets, declared editorial intent and accepted_authority=false.
3. proposal_status=PROPOSED_NOT_APPROVED; human_decision_state=NOT_OBSERVED. Not a real ReviewBundle, HumanDecisionArtifact or EditPlan.
4. Preserve each prior/rejected proposal revision. Reject missing/stale/contradictory parent, nonmonotonic revision IDs, duplicate proposal ID or tampering.
5. Reject caller-provided approved=true, signed_by, editor_decision=ACCEPT or reviewer name as real authority; a generated TEST_ONLY_FAKE choice is allowed only in tests and never as a real decision.
6. Do not create cut intervals, FFmpeg commands, render recipes, export eligibility or source-source joins absent legitimate provenance.
7. Do not bypass existing vip_fvs human_decision and real_plan contracts; study them, reuse only safe immutable records if the actual API supports source-independent test fixtures.
8. Whole-proposal refusal on wrong candidate/manifest/generation/temporal digest. Produce a canonical digest for each revision.

Tests: proposal revision transitions, preserved prior alternatives, stale parent, candidate swap, fake human approval, unauthorized edit-plan promotion, exact same inputs -> same digest, no protected I/O.


## 11. MEGA-12 — GENERATED-ONLY RECOVERY AND REPLAY CONSISTENCY

Goal: test coherent behavior after simulated interruptions without introducing a second production queue, persistence system or real source workload.

New files:
- src/vip_lab/mega12/__init__.py
- src/vip_lab/mega12/replay_graph.py
- src/vip_lab/mega12/fault_scenarios.py
- src/vip_lab/mega12/consistency_review.py
- tests/vip_lab/test_mega12.py

Requirements:
1. Accept explicit bounded synthetic stage events, identities and upstream packet digests; keep immutable stage-input and stage-output hashes.
2. Reuse gate2.workload, gate2.recovery, gate2.faults and vip_lab.mega06 where exact existing APIs can do the job. Do not reimplement RecoveryHarness or its journal.
3. Generated fixture events can model prepared -> running -> interrupted -> resumable or terminal rejection; never use actual index/media roots.
4. Commit a generated-only stage once; repeat replay must not duplicate accepted results. Crash after side effect but before committed record must follow actual existing idempotency contract.
5. Reject truncated JSONL/synthetic receipt, wrong generation, wrong semantic-space ID, corrupted digest, duplicate commitment, missing ancestor and invalid event ordering.
6. Use only ACTUAL FaultClass values and respect HARNESSED vs NOT_YET_HARNESSED; unsupported faults are NOT_EXECUTED, not simulated as accepted behavior.
7. Record synthetic counters separately from real workload/host/model observations, which remain NOT_OBSERVED. Do not justify ANN, cache, persistent broker, daemon, queue or greater concurrency.
8. Resource bounds: small generated-only jobs/events, count/size caps, no unbounded replay or hidden network calls.
9. Do not open original source files, model assets or protected archives, and never overwrite existing index generations.

Tests: interrupted/repeated deterministic replay, idempotence, metadata tamper, sequence truncation, wrong upstream, unsupported fault, no work outside tmp_path, no spurious production-scale claim.

## 12. MEGA-13 — QC EVIDENCE COMPLETENESS AND EXPORT REFUSAL

Goal: determine what actual technical/editorial observations would be needed, without asserting they happened.

New files:
- src/vip_lab/mega13/__init__.py
- src/vip_lab/mega13/qc_readiness.py
- src/vip_lab/mega13/lineage_audit.py
- src/vip_lab/mega13/release_blockers.py
- tests/vip_lab/test_mega13.py

Requirements:
1. Consume validated candidate queue, temporal request, editorial proposal and generated-only replay receipt. Bind exact source occurrence, model space, revision, stream/timebase and upstream report digests.
2. Distinguish measured technical output identity, real video/audio editorial observation, human edit approval, preview-only QC and production-export eligibility. None is externally observed in this LAB.
3. Set qc_state=NOT_OBSERVED, preview_eligible=false, production_export_authorized=false and export_status=REFUSED_NOT_AUTHORIZED.
4. Reject plain QC PASS, attacker-controlled visual/audio observation labels and self-signed reviewer fields. Do not invent technical output/frame hash or human signed acceptance.
5. Reuse gate3.qc.bare_pass_is_insufficient(record) only with the verified actual record shape. Never call may_consume_for_binding_origin without valid source-bound attestation and fresh authority.
6. Fail closed on wrong candidate, stream, revision, ReviewBundle linkage, edit-plan origin or source snapshot authority. Do not silently repair or auto-approve.
7. Report per-missing-evidence prerequisites and refusal reasons, with precise ownership and honest NOT_OBSERVED states.
8. Make the QC readiness result deterministic and digest-bound. No render, preview subprocess, FFmpeg, media decoder or provider calls.
9. Report what is missing rather than manufacturing measurable results.

Tests: fake PASS, fake human QC, mismatched lineage, invalid report digest, MEASURED escalation attempt, absent audio/visual observations, no source/model subprocesses.

## 13. MEGA-14 — REAL END-TO-END SYNTHETIC INTEGRATION, CLI AND REPORT

Goal: one demonstrable integrated, fully generated-only flow. The source-index/query path must really be called through existing production-facing LAB seams rather than returning canned test objects.

New files:
- src/vip_lab/mega14/__init__.py
- src/vip_lab/mega14/scenario.py
- src/vip_lab/mega14/orchestrator.py
- src/vip_lab/mega14/report.py
- src/vip_lab/mega14/cli.py
- tests/vip_lab/test_mega14.py
- tests/vip_lab/test_mega08_14_end_to_end.py

Design a closed versioned generated-only scenario input with stable ID/seed, small query catalog, one explicit multi-source manifest, one or three existing fake model profiles, separate existing-generation index identities, top_k, and optional numerical PTS fixture. Do not create actual MP4, source probe, model asset, reviewer judgment or renderer.

Required true integration chain:

scenario validation
-> vip_fvs QueryCatalog and source-bound generated-only manifest
-> existing batch_retrieval / three_arm_batch read-only retrieval over injected fake or tmp_path precommitted synthetic index
-> strict verified batch report with query/arm/generation/source attribution
-> MEGA-09 review queue
-> MEGA-10 temporal request/diagnostic
-> MEGA-11 unapproved proposal
-> MEGA-12 generated-only replay identity
-> MEGA-13 QC/export refusal
-> canonical report + verifier.

Rules:
1. Use actual run_batch_retrieval, run_three_arm_batch and verify_batch_report interfaces. Do not implement a second search algorithm.
2. Reuse or instantiate source-independent fake engines with verified existing constructor semantics. A generated SQLite/vectors.f32 fixture under tmp_path is allowed when source code already supports it. The query stage must not run index_source.
3. Single-arm V1 Base 768D, V2 Base 768D and SO400M 1152D; three-arm separate generations. Reject 768D cross-model generation reuse.
4. Preserve two byte-identical occurrences from different exact synthetic paths; preserve repeated query text under separate query IDs.
5. Preserve nonzero integer PTS and rational timebase exactly. No automatic edit interval, no MEASURED evidence and no nominal-FPS frame calculation.
6. Provide a canonical report showing which source, model, query, candidate and proposal identities were present, which real evidence is missing, and why export remains not authorized.
7. Full report verifier must detect tampered field/digest, forged human authority, unknown status, duplicate JSON key, nonfinite score and forbidden extra fields.
8. Expose a separate CLI: PYTHONPATH=src:experiments python -m vip_lab.mega14.cli --help; provide run-synthetic-scenario and verify-report only if actual output contract supports safe execution.
9. Explicit real/--render/--export/--provider/--download attempts must refuse before side effects, with nonzero CLI exit and one non-success JSON object.
10. If a required producer wave is absent or BLOCKED, return a structured failure; never print an incomplete successful E2E result.
11. Repeat identical scenario with identical fake indexes -> byte-identical report; change bound source revision/catalog/model-space -> distinct output identity or fail closed.
12. No real media/model network, no daemon, no server, no production edit planning, no actual preview/export.

Tests: all real seams with generated fixtures; 1/2/64 bounded queries, duplicate texts, two occurrences, exact PTS/timebase, versioned proposals, fault/refusal propagation, one-arm failure, no source opens, no model/FFmpeg calls, stable report, CLI status and old 307-suite non-regression.

## 14. Implementation packet map and dependency-safe scheduling

Each wave is a reviewable packet, not seven unrelated giant rewrites:

| Packet | Code owner | Test owner | Depends on |
|---|---|---|---|
| P08 | mega08/ capability and source-contract map | test_mega08.py | baseline |
| P09 | mega09/ review queue | test_mega09.py | existing MEGA-02 |
| P10 | mega10/ source-native temporal request | test_mega10.py | P09 |
| P11 | mega11/ versioned editorial proposal | test_mega11.py | P09 + P10 |
| P12 | mega12/ generated recovery | test_mega12.py | baseline; independent |
| P13 | mega13/ QC evidence completeness | test_mega13.py | P10 + P11 + P12 |
| P14 | mega14/ orchestrator/CLI/report | test_mega14.py + test_mega08_14_end_to_end.py | compatible completed producers |

Workflow: inspect existing source call signatures -> author targeted tests BEFORE code -> implement only missing LAB contract -> static name/signature review -> optionally AST compile -> update progress ledger -> next wave.

P08 and P12 are independently buildable. P09->P10->P11 is a dependency chain. P13 and P14 follow their actual producer interfaces. If an earlier wave is blocked, continue independent P12 and negative tests, but do not pretend the blocked wave was delivered.

No two writers own the same file. The user can ask for continuation by pointing to the progress ledger. Do not fabricate subagents or worktrees inside the ZIP.

## 15. Conditional remaining-code stretch queue

After P08–P14, inspect remaining opportunities; write additional code only when a specific, source-backed gap has a legitimate use within the existing allowed paths. Prefer extending one of the new test files over creating a new unused subsystem.

**S1 — Gate-0 preflight:** if an actual gap remains in generated-only editorial query/metadata conformance, extend P08 or P14. Respect 24 editor-positive, 8 absent, 8 development, two distinct reviewers and true human labels still NOT_OBSERVED. Never create fake genuine labels or run D-3.

**S2 — Gate-1 safety:** add only missing model-free V1/V2/SO400M cross-space refusal regression to new tests. No model download, no invented tokenizer/pooling, no real benchmark/winner.

**S3 — Gate-2 replay:** if existing mega06 misses a real synthetic integrity edge, cover it in P12 through actual RecoveryHarness. No new production index architecture, queue/cache/ANN, or scale claim.

**S4 — Gate-3 timing/stream-tail:** document A-7 positive mapping, IT-6 terminal duration and audio/dual-authority policy as BLOCKED_BY_CANONICAL_DECISION. Only negative synthetic tests are permitted. No new source parsing or production render.

**S5 — H3 WBS/Atlas gap classification:** generate an ADVISORY mapping of LAB code and source-backed tests to H3-A03–A07, B04/B05, C05, D02/D05, G01–G03 and open WBS parents. No editing canonical Atlas, checkboxes, branch records, PRs or Gate status.

**Stop** if extra work would be duplicate boilerplate, require permission for real archive/model/provider/media, or silently widen a frozen contract. The Owner requested all code-capable work, not artificial implementation of human and operational prerequisites.

## 16. CI execution and direct-to-main safeguards

Google AI Studio must write Python code and pytest test source ONLY. Do not run pytest, unittest, CLI, installations, downloads, network, real models, real/protected media or FFmpeg; do not push GitHub from the AI Studio agent; do not edit the workflow. Syntax-only ast.parse/compile permitted, label it STATIC_ONLY.

The Owner's LAB GitHub integration may direct files to main. Publication is a separately controlled human action. Preserve .github/ and all preexisting paths, particularly src/gate0/media/. NEVER mirror a reduced ZIP to remote with delete semantics. If the integration cannot upload changed files only, STOP and ask the Owner to use a safe selective upload before any push.

The LAB controller will configure conditional MEGA-08–14 CI with Python 3.11/3.14. Every submitted wave must run its new test file and any missing expected sibling file must fail completeness. A not-submitted wave may be SKIPPED but cannot be counted as completed. A partially submitted wave should FAIL rather than be hidden by an empty placeholder.

CI SUCCESS on previous 307 tests alone is NOT a success of P08–P14. Actual progress requires exact submitted SHA, test step names, selected counts and failures. The local Codex auditing worktree must not write or merge into LAB main. It may fetch and inspect immutable main commits as they appear and report findings in its own branch.

Approval layers:
1. AUTHORING_DELIVERED — source and tests present, unexecuted.
2. HOSTED_SYNTHETIC_VERIFIED — named new tests actually ran and passed on both Python versions at exact commit.
3. INDEPENDENTLY_REVIEWED — Codex checked exact diff against source contracts and threat boundaries.
4. CANONICAL_ACCEPTED — requires separate explicit Owner adoption/grant plus Gate-specific evidence. NOT authorized in this task.

Do not collapse the four layers.

## 17. Progress ledger and safe continuation contract

Create and maintain docs/ai-studio-tasks/MEGA_08_14_PROGRESS.md before writing the first Python file. Update after every complete or blocked wave.

Fields:
- spec_version = LAB-MEGA-08-14-v1.0.0
- workspace_git_sha = NOT_OBSERVED if ZIP
- baseline_revision = 22f1ffa... declared reference, not locally verified without Git
- per-wave status: NOT_STARTED / IMPLEMENTED_UNVERIFIED / PARTIAL_BLOCKED / BLOCKED_SCOPE / NOT_NEEDED
- exact files read and source symbols validated
- actual new paths, positive/refusal/side-effect test cases
- source-schema/constructor assumption corrections
- source/media/model/network invariants retained
- AI_STUDIO_PYTEST = NOT_EXECUTED_BY_DESIGN
- optional AST result = actual checked scope, not pytest PASS
- hosted_ci = NOT_OBSERVED until a GitHub run is independently fetched
- next_safe_packet and explicit unresolved blockers.

If AI Studio reaches context/response limits, save completed coherent code and an exact checkpoint, do not redo previous waves. It may stop with PARTIAL_BLOCKED; the Owner can invoke a later continuation using the ledger. No background processing promise.

Continuation prompt for a future user-issued request:
Read docs/ai-studio-tasks/MEGA_08_TO_14_ALL_REMAINING_LAB_CODE_PROGRAM.md and MEGA_08_14_PROGRESS.md. Verify source, continue from next_safe_packet, preserve completed paths, write code + tests, no local pytest/install/model/media/CI edits/GitHub push, update ledger, report Turkish status.

## 18. Review and evidence discipline — final failure checklist

Reject any of:
1. "Three-arm benchmark winner" inferred from fake cosine scores.
2. Source SHA asserted from user metadata as if bytes measured.
3. Generated PTS frames promoted to MEASURED or binding_eligible.
4. Nominal FPS used to infer VFR frame ordinal.
5. Duplicate source occurrence collapsed by content hash alone.
6. Two 768D model spaces treated as identical.
7. ISO-BMFF track ordinal guessed from FFprobe global index.
8. Self-declared Owner signature, E01 token, human approval or QC PASS accepted as authority.
9. Actual HumanDecisionArtifact, EditPlan, preview or export synthesized without source/Owner evidence.
10. Model/network/provider access or actual/protected video decoding/rendering.
11. Reimplementing existing batch retrieval, profile embeddings, Gate-2 recovery journal, Gate-3 temporal engine.
12. Editing existing canonical producer code, protected repository or original WBS/Atlas.
13. Git reset/clean/force push or deleting files while syncing ZIP.
14. Swallowing unknown exceptions to print READY_SYNTHETIC.
15. Deleting/skipping/xfailing failing tests to greenwash CI.
16. Reporting syntax-only compilation as runtime integration PASS.
17. Reporting all remaining B00–B11/Gate tasks as completed from these LAB waves.
18. Calling an independent local Codex review passed before a reviewer actually examined exact SHA.

## 19. Required Turkish final report

A. Baseline preflight — all required source files and verified code facts, ZIP/.git uncertainty.

B. Gaps by wave — which behavior already existed, which is genuinely missing, rejected duplication and authority-limited items.

C. Changed paths — every created/modified file; no vague claims.

D. Implemented behavior — P08 through P14, actual producer/consumer, test-first assertion, negative path and no-effect boundary.

E. Tests written — list individual suites/functions, positive and hostile cases, no fabricated test count.

F. Verification — print AI_STUDIO_PYTEST=NOT_EXECUTED_BY_DESIGN; static syntax only if actually executed; hosted CI NOT_OBSERVED before a real run.

G. Protected decisions — PR #258, A-7/S5, H3-C05/A04, D-3 Gate-0, authentic SigLIP2 Gate B, real scale Gate-2 and real Gate-3 edit/export remain separate.

H. Ledger — MEGA_08_14_PROGRESS.md exact current wave, next_safe_packet and source API rulings.

I. Delivery — only changed files published selectively to LAB main; preserve .github and six gate0/media dependencies. Local Codex auditor uses separate branch/worktree without writing main.

J. Per-wave status and total: IMPLEMENTED_UNVERIFIED, PARTIAL_BLOCKED, BLOCKED_SCOPE, NOT_NEEDED, NOT_IMPLEMENTED; no false VERIFIED_COMPLETE before CI and review.

STOP after this comprehensive assignment. No unapproved real operations or production deployment.
