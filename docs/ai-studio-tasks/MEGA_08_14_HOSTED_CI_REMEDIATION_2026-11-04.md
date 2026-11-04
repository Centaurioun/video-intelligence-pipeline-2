# MEGA-08–14 — HOSTED CI REMEDIATION

**Version:** LAB-MEGA-08-14-REMEDIATION-v1.0
**Date:** 2026-11-04
**Target:** Centaurioun/video-intelligence-pipeline-2 LAB ONLY
**Restored main:** ddde7df49d2abe46a482d291cc38ece1ddcb40b3
**Real failed CI:** https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/41763786941
**Protected canonical original:** Centaurioun/video-intelligence-pipeline (READ ONLY)

## 1. Verified situation

Google AI Studio's 38 new MEGA-08–14 files ARE ALREADY ON LAB MAIN. AI Studio claimed its local changes were not published, but GitHub commit 59958b91987b89da8a495d50086e198aade4ae4b added all 38 files and inadvertently deleted six source dependency files at src/gate0/media/. The controller restored EXACTLY these six blobs, without reset, force push, changing the new code or deleting anything, in commit ddde7df49d2abe46a482d291cc38ece1ddcb40b3. The diff from prior verified baseline b55b148 to restored main now shows 38 additions and ZERO deletions.

**Observed real CI, each Python 3.11 and 3.14:**

| Group | Actual result |
|---|---|
| Prior baseline / MEGA-02–07 | 307 PASS |
| MEGA-08 | 5 PASS, 5 FAIL |
| MEGA-09 | 6 PASS |
| MEGA-10 | 6 PASS |
| MEGA-11 | 5 PASS |
| MEGA-12 | 4 FAIL |
| MEGA-13 | 4 FAIL |
| MEGA-14 / cross-wave E2E | 2 collection ERRORS; behavior NOT_EXECUTED |
| Overall | FAILED |

MEGA-08–14 path completeness check passed. The final CI step correctly FAILED. Do not classify MEGA-08–14 as verified or completed.

## 2. Authorized repair boundaries

Apply **systematic debugging**: read actual canonical constructor/return shape, isolate root cause, add/correct regression first, minimal compatible code, inspect hosted CI result. Do not merely change expected assertions to match broken code.

Allowed edits:
- src/vip_lab/mega08/**, mega12/**, mega13/**, mega14/**
- tests/vip_lab/test_mega08.py, test_mega12.py, test_mega13.py, test_mega14.py, test_mega08_14_end_to_end.py
- docs/ai-studio-tasks/MEGA_08_14_PROGRESS.md

Previously green MEGA-09/10/11 modules and tests are read-only unless a specific reproducible defect absolutely requires a narrow exception. Also read-only: src/vip_lab/common.py, MEGA-03–07 modules and tests, src/vip_fvs/**, src/gate0..3/**, experiments/**, .github/**, canonical original repository and frozen WBS.

No protected media, model download/run, network/provider call, real FFprobe/FFmpeg, export, Gate promotion, or self-issued human approval. In AI Studio, write tests and code but DO NOT run pytest or install dependencies. Only hosted Actions or a separately authorized local Codex run provides behavioral execution evidence.

**CRITICAL:** The last TWO ZIP→GitHub syncs accidentally deleted the same six src/gate0/media files. NEVER mirror a reduced ZIP onto LAB main with delete semantics again. Changed-path-only safe publication or isolated local selective integration is required. If your publisher cannot guarantee no unrelated deletions, DO NOT PUBLISH.

## 3. MEGA-08 root cause — self-contradictory path trust model

Source: src/vip_lab/mega08/capability_inventory.py.

- Line ~41 ALLOWED_INVENTORY_PREFIXES permits selected source Python paths and docs/ai-studio-tasks/.
- Line ~694 its OWN default capability inventory refers to docs/decisions/2026-10-29-a7-s5-scoped-synthetic-tdd-plan-owner-adoption.md.
- Line ~790 build_capability_inventory() feeds all source_paths through the same validator.
- Result: INVENTORY_PATH_NOT_ALLOWLISTED for a legitimate *advisory governance reference*. This causes 4 direct failures, plus a fifth forged-authorization negative test fails prematurely with INVALID rather than reaching intended gate refusal.

Repair source model rather than loosening all paths: distinguish bounded Python AST module inspection from non-executable, closed/allowlisted governance document references. Or represent the document as an opaque advisory citation and use an already-allowed source module for the executable symbol check. Keep traversal, unknown path, symlink and arbitrary file refusal. Ensure negative tests start from a valid baseline inventory. No PR #258 or Gate acceptance is permitted.

## 4. MEGA-12 root cause — wrong canonical WorkloadSpec AND RecoveryHarness

Actual CI test fixture: tests/vip_lab/test_mega12.py line ~24:
TypeError: WorkloadSpec.__init__() got an unexpected keyword argument 'workload_id'.

Canonical src/gate2/workload.py actually defines:

    WorkloadSpec(
        jobs:int, stages:int, artifact_bytes:int, cost_units:int,
        fault_position:int, seed:int,
        f01_sha:str, c04_sha:str, e05_sha:str, config_digest:str,
        concurrency:int=1, repetitions:int=2
    )

NO workload_id, job_count, stages_per_job or payload_bytes on canonical WorkloadSpec.

**Not just bad tests:** new MEGA-12 production code also assumes nonexistent fields:
- src/vip_lab/mega12/replay_graph.py: workload_spec.workload_id, job_count, stages_per_job, payload_bytes; RecoveryBinding(generation_id=..., semantic_space_id=...) with incomplete fields; RecoveryHarness(binding); harness.run_job(...).
- src/vip_lab/mega12/fault_scenarios.py: same nonexistent workload fields.
- src/vip_lab/mega12/consistency_review.py: wrong WorkloadSpec constructor and possible guessed MeasurementSet return shape.

Canonical src/gate2/recovery.py has a **10-field RecoveryBinding**, RecoveryHarness.open(checkpoint_path,binding,adapter), harness.run(crash_point=...). There is no canonical run_job(). Inspect source and existing verified src/vip_lab/mega06/recovery_matrix.py for a safe generated-only adapter pattern. Never make a fake RecoveryHarness compatibility shim with a permissive method.

Choose a LAB-owned workload_id as a separate field or derive it from validated canonical spec digest; do not add fields to gate2.WorkloadSpec. Inspect actual generate(spec) fixture/job/stage fields. Rebuild replay and tests around **real** generated deterministic workload and real recovery contract; preserve true idempotence/commit ordering and reject invalid receipts. Inspect actual MeasurementSet.to_dict() rather than inventing as_dict().

Must test: positive replay, duplicate handling, wrong generation/space, truncated JSONL, unsupported FaultClass capability, NO real scale claim.

## 5. MEGA-13 — inherited fixture defect, then genuine QC validation

All four tests currently fail at tests/vip_lab/test_mega13.py around line 106 from the same invalid WorkloadSpec(workload_id=...). Use repaired M12 canonical generated fixture. THEN execute M13 tests to expose real lineage/QC issues. Do not stop after making the fixture constructible.

Preserve source revision/candidate/queue/replay/proposal lineage, explicit human decision NOT_OBSERVED, no fake VISUALLY_OBSERVED/AUDIO_OBSERVED, no bare QC PASS, binding_consumable=false and production_export_authorized=false. Do not forge output hashes or source-native MEASURED status.

## 6. MEGA-14 — wrong spec import, then end-to-end WorkloadSpec defect

Collection errors:
ImportError: cannot import name MEGA_08_14_SPEC_VERSION from vip_lab.mega08.gap_digest.

Verified:
- MEGA_08_14_SPEC_VERSION is defined in src/vip_lab/mega08/capability_inventory.py around line 36.
- gap_digest.py does NOT define that constant.
- src/vip_lab/mega14/__init__.py wrongly imports it from gap_digest.py.
- Review orchestrator imports and circular import possibilities; use one authoritative version source.

Further bad code will surface after collection:
- src/vip_lab/mega14/scenario.py default and parsed workload dict use workload_id, job_count, stages_per_job, payload_bytes as if canonical WorkloadSpec fields.
- src/vip_lab/mega14/orchestrator.py around lines 329–335 creates WorkloadSpec with these non-existent keywords.
- M14 consumes M12 replay and M13 QC, so fix the entire producer→consumer contract, not only import.

Actually test full generated-only chain: QueryCatalog + validated batch retrieval, candidate queue, temporal request (nonbinding rational PTS), unapproved editorial proposal, canonical generated recovery, QC export refusal and digest-checked final report. No canned success. Verify CLI rejects --real/--render/--provider/--download before side effects and never prints real production PASS.

## 7. Required execution order

1. Verify that current LAB tree has all 38 new files, six restored src/gate0/media source dependencies and the existing workflow.
2. Fix M14 import collection so tests can import.
3. Repair M12 canonical WorkloadSpec + RecoveryHarness and its tests, preserving actual regression intent.
4. Repair M13's shared generated fixture; discover and address subsequent genuine QC errors.
5. Repair M08 self-contradictory advisory-source allowlist without weakening source trust.
6. Repair M14 scenario/producer mapping, full E2E and report verifier.
7. Perform source-symbol/constructor static audit across new code, check no unauthorized operations.
8. Update docs/ai-studio-tasks/MEGA_08_14_PROGRESS.md with exact fixes, actual previous failed CI and next step.
9. PUBLISH ONLY changed authorized files with ZERO unrelated deletions, then inspect actual hosted CI logs and per-wave test counts for Python 3.11 and 3.14. AI Studio local pytest remains NOT_EXECUTED_BY_DESIGN.
10. Require independent local Codex review on the exact immutable candidate SHA; do not merge/crosswrite audit and development branches without Owner direction.

Stop after this repair. Do not invent another MEGA feature batch.

## 8. Final disposition

\`IMPLEMENTED_UNVERIFIED\` until the named new tests genuinely run and PASS on both hosted Python versions. \`HOSTED_SYNTHETIC_VERIFIED\` requires all seven wave suites actually executed, prior 307 test baseline retained, no unrelated deletions and independent review separately recorded. Neither status implies authentic model performance, actual real-media source measurements, human decision, production export or canonical Gate acceptance.

Report in Turkish with exact changed paths, real source API assumptions corrected, positive/refusal tests, any remaining blocker, CI run SHA and status, and safe continuation.
