# MEGA-08 through MEGA-14 Durable Progress Ledger (`LAB-MEGA-08-14-v1.0.0`)

## 1. Program & Environment Metadata

- **`spec_version`:** `LAB-MEGA-08-14-v1.0.0` (Remediated under `LAB-MEGA-08-14-REMEDIATION-v1.0` + Phase B Addendum `ecc873794cb49ad0d79e4bf97bc0e13fc8938cbf` + Final CI Correction against `4076e59e4dfd1f758e82b10fbbaaf2d4b69fe630`)
- **`workspace_git_sha`:** `NOT_OBSERVED (GIT_DIR_ABSENT / ZIP_IMPORTED_WORKSPACE)`
- **`declared_lab_baseline_revision`:** `22f1ffa7064f697d4049e39587945b1decabec4e`
- **`verified_lab_main_ci_commit`:** `4076e59e4dfd1f758e82b10fbbaaf2d4b69fe630` (GitHub Actions run `41846684517`)
- **`canonical_vip_reference_sha`:** `592952daf475b1bbae2eebdee64d992c1a744f08`
- **`baseline_ci_status`:** `342 PASS / 8 FAIL` per Python 3.11 and Python 3.14 on GitHub Actions run `41846684517` (`307` prior baseline + `MEGA-08` `10 PASS` + `MEGA-09` `6 PASS` + `MEGA-10` `6 PASS` + `MEGA-11` `5 PASS` + `MEGA-12` `3 PASS / 3 FAIL` + `MEGA-13` `4 PASS` + `MEGA-14` `1 PASS / 5 FAIL`).
- **`AI_STUDIO_PYTEST`:** `NOT_EXECUTED_BY_DESIGN`
- **`AI_STUDIO_IMPORT_SMOKE`:** `NOT_EXECUTED_BY_DESIGN`
- **`GITHUB_ACTIONS_STATUS`:** `MEGA-08/09/10/11/13 CI_VERIFIED (41846684517); MEGA-12/14 REMEDIATED_PENDING_SELECTIVE_CI_RERUN`

---

## 2. Section 1 Baseline Hard Gate & Verified Source Contracts

All eight Section 1 baseline checks passed prior to writing or remediating any Python code:

1. **`docs/ai-studio-tasks/MEGA_03_07_PROGRESS.md`:** Present; records CI remediation and 307-test baseline (`41756150902` / `41756377930`).
2. **`src/gate0/media/`:** All 6 required files present and preserved untouched (`__init__.py`, `decode.py`, `probe.py`, `proc.py`, `source_guard.py`, `tool_identity.py`).
3. **`src/vip_lab/mega05/model_assets.py`:** Verified `semantic_space_id(semantic_space)` from `persistent_local_index.model_space` and `MODEL_PROFILE_SEMANTIC_SPACE_ID_MISMATCH`.
4. **`src/vip_lab/mega06/recovery_matrix.py`:** Verified `FaultClass`, `capability(fc).value`, `job.job_index`, `len(job.stages)`, and `outcome["post_state_digest"]`.
5. **`src/vip_lab/mega07/candidate_temporal_gate.py`:** Verified `refinement_status: "SYNTHETIC_DIAGNOSTIC_ONLY"`, `refinement_evidence_state: NOT_OBSERVED`, and `binding_eligible: False`.
6. **`src/vip_fvs/`:** Verified `query_batch.py`, `synthetic_profiles.py`, `batch_retrieval.py`, `three_arm_batch.py`, `batch_report.py`, `multi_source_retrieval.py`, `source_adapter.py`, `semantic_index.py`, `review_bundle.py`, `human_decision.py`, `real_plan.py`.
7. **`tests/vip_lab/`:** Verified `test_mega03.py` through `test_mega07.py`, `test_cross_gate_integration.py`, and `test_lab_cli.py`.
8. **`.github/workflows/vip-ai-studio-synthetic-ci.yml`:** Present and untouched.

### Verified Producer Symbol & Signature Matrix

- **`vip_lab.common`:** `LAB_PROGRAM_VERSION`, `SYNTHETIC_CONTEXT_TOKEN`, `MAX_LAB_JSON_BYTES`, `CANONICAL_EVIDENCE_CLASSES`, `NOT_OBSERVED`, `FORBIDDEN_EXTERNAL_AUTHORITY_KEYS`, `VipLabError`, `ReadinessStatus`, `SyntheticContextMarker`, `ReadinessFinding`, `ReadinessPacket`, `canonical_json_dumps`, `canonical_json_bytes`, `canonical_sha256`, `parse_strict_json_text`, `parse_strict_json_bytes`, `load_bounded_json_file`, `validate_hex_digest`, `sanitize_untrusted_authority_claims`.
- **`vip_fvs.query_batch`:** `QUERY_CATALOG_SCHEMA_VERSION`, `QueryCatalog`, `QueryCatalogItem`, `parse_query_catalog_mapping`, `parse_query_catalog_bytes`, `load_query_catalog`, `compute_query_catalog_digest`, `validate_lab_top_k`.
- **`vip_fvs.synthetic_profiles`:** `CLOSED_SYNTHETIC_PROFILE_IDS`, `V1_PROFILE_ID`, `V2_BASE_PROFILE_ID`, `V2_SO400M_PROFILE_ID`, `SyntheticProfileBundle`, `make_synthetic_profile`, `make_synthetic_profile_payload`, `build_synthetic_profile_runtime`, `parse_model_profile_mapping`, `load_model_profile_json`, `load_synthetic_profile_bundle`.
- **`vip_fvs.batch_retrieval`:** `BatchCandidateRecord`, `BatchQueryResult`, `SingleArmBatchResult`, `run_batch_retrieval`.
- **`vip_fvs.three_arm_batch`:** `THREE_ARM_MAP_SCHEMA_VERSION`, `ARM_VIP_V1_BASE`, `ARM_VIP_V2_BASE`, `ARM_VIP_V2_SO400M`, `DECLARED_ARM_ORDER`, `ARM_TO_PROFILE_ID`, `PROFILE_ID_TO_ARM`, `ThreeArmConfigEntry`, `ThreeArmConfigMap`, `ThreeArmBatchArmResult`, `ThreeArmBatchResult`, `parse_three_arm_map_mapping`, `run_three_arm_batch`.
- **`vip_fvs.batch_report`:** `BATCH_REPORT_SCHEMA_VERSION`, `KIND_SINGLE_ARM`, `KIND_THREE_ARM`, `REPORT_STATUS_SYNTHETIC_ONLY`, `BENCHMARK_STATUS_NOT_RUN`, `MODEL_EVIDENCE_NOT_OBSERVED`, `GATE_DECISION_NOT_AUTHORIZED`, `REPORT_LIMITATIONS`, `build_single_arm_batch_report`, `build_three_arm_batch_report`, `compute_batch_report_digest`, `serialize_batch_report`, `verify_batch_report`.
- **`vip_fvs.source_adapter`:** `SourceBinding`, `SourceManifestEntry`, `MultiSourceManifest`, `build_multi_source_manifest`, `save_multi_source_manifest`, `load_multi_source_manifest`.
- **`vip_fvs.review_bundle`:** `ReviewBundle`, `V1_SCHEMA_VERSION`, `V2_SCHEMA_VERSION`, `V3_SCHEMA_VERSION`, `dependency_digest`, `record_digest`.
- **`vip_fvs.human_decision`:** `HumanDecisionArtifact`, `create_human_decision`, `load_human_decision`, `resolve_human_decision_resume`.
- **`vip_fvs.real_plan`:** `SourceTimelineMapping`, `RealPlanArtifacts`, `RealPlanLineage`, `RealPlanSelection`, `build_real_edit_plan`, `build_fixture_plan_artifacts`.
- **`gate3.pts` / `gate3.temporal` / `gate3.rational` / `gate3.qc`:** `PtsTable(time_base, ticks)`, `TimeBase(num, den)`, `Rational(numerator, denominator)`, `SnapResult`, `resolve_start(table, requested_ticks)`, `resolve_end(table, requested_ticks)`, `classify_vfr(table, declared_rate=None)`, `detect_discontinuity(table, start_ticks, end_ticks)`, `subdivide_on_discontinuity(table, start_ticks, end_ticks)`, `tail_end`, `QCReport`, `bare_pass_is_insufficient(record)`, `may_consume_for_binding_origin(record, attestation, *, source_content_digest)`.
- **`gate2.workload` / `gate2.recovery` / `gate2.faults` / `gate2.measure`:**
  - `WorkloadSpec(jobs, stages, artifact_bytes, cost_units, fault_position, seed, f01_sha, c04_sha, e05_sha, config_digest, concurrency=1, repetitions=2)`; `_LIMITS["concurrency"] = (1, 1)`; `WorkloadSpec.to_dict()` emits nested `{"dimensions": {...}, "seed": ..., "identity": {...}, "workload_digest": ...}`
  - `generate(spec: WorkloadSpec) -> SyntheticFixture` (`jobs: tuple[SyntheticJob, ...]`, `stages: tuple[SyntheticStage, ...]`, `stage.artifact: bytes`, `stage.artifact_digest: str`, `fixture.fixture_digest: str`)
  - `RecoveryBinding(f01_sha, c04_sha, e05_sha, workload_digest, configuration_digest, previous_manifest_digest, current_manifest_digest, generation_id, semantic_space_id, receipt_identity)`
  - `RecoveryHarness.open(checkpoint_path, binding, adapter) -> RecoveryHarness` and `harness.run(crash_point=None)`; `crash_point="after_side_effect_before_completion"` raises `RuntimeError("synthetic crash after side effect before completion")` (no `SimulatedCrash` class exists in `gate2.recovery`)
  - `FaultClass` (`A_BEFORE_STAGE_START = "a"` through `M_REFERENTIAL_DIVERGENCE = "m"`), `capability(fc)`, `inject(fc, payload: Mapping[str, Any]) -> InjectionResult` (non-mutating detector returning `InjectionResult(fault_class, capability, detected, disposition, details)`)
  - `Measurement.measured(metric_id=..., value=..., unit=..., derivation=..., evidence_class="MEASURED")`, `Measurement.not_observed(metric_id=..., reason=...)`, `MeasurementSet.to_dict()`.

---

## 3. Hosted CI Run `41846684517` Diagnostics & Final `MEGA-12/14` Corrections

### 3.1 Observed Hosted CI Results on Run `41846684517` (`4076e59e4dfd1f758e82b10fbbaaf2d4b69fe630`)

- **Prior baseline + `MEGA-02..07`:** `307 PASS` (Python 3.11 and Python 3.14)
- **`MEGA-08`:** `10 PASS` (`CI_VERIFIED` — preserved untouched)
- **`MEGA-09`:** `6 PASS` (`CI_VERIFIED` — preserved untouched)
- **`MEGA-10`:** `6 PASS` (`CI_VERIFIED` — preserved untouched)
- **`MEGA-11`:** `5 PASS` (`CI_VERIFIED` — preserved untouched)
- **`MEGA-12`:** `3 PASS / 3 FAIL`
- **`MEGA-13`:** `4 PASS` (`CI_VERIFIED` — preserved untouched)
- **`MEGA-14` (including E2E):** `1 PASS / 5 FAIL`
- **Total Passing / Failing:** `342 PASS / 8 FAIL` per Python version

### 3.2 Exact Root Causes & Corrections Executed for the 8 Remaining Failures

1. **Task 1 — Canonical `FaultClass` Injection Payloads & Non-Mutating Detection Semantics (`src/vip_lab/mega12/fault_scenarios.py`, `tests/vip_lab/test_mega12.py`, `tests/vip_lab/test_mega08_14_end_to_end.py`):**
   - **Root Cause (6 failures across `test_mega12.py`, `test_mega14.py`, `test_mega08_14_end_to_end.py`):** `src/gate2/faults.py:inject(fault_class, payload)` is a non-mutating detector over structured `Mapping[str, Any]` payloads. `FaultClass.L_CONCURRENT_WRITER` passed `"writers": 2`, causing `tuple(str(w) for w in payload.get("writers", ()))` to raise `TypeError: 'int' object is not iterable`. In addition, several other `HARNESSED` classes (`E`, `F`, `H`, `J`, `K`, `M`) passed non-canonical keys that would have returned `detected=False` (`disposition="NOT_TRIGGERED"`).
   - **Correction:** Updated `_build_canonical_fault_payload()` in `src/vip_lab/mega12/fault_scenarios.py` to provide exact canonical trigger payloads for all 9 `HARNESSED` classes (`A`: `predecessor_succeeded=False`; `E`: `second_submission=True`; `F`: differing `decision_vector_a`/`decision_vector_b`; `H`: `interruption_observed=True`, `recovery_swallowed=False`; `I`: invalid JSON `'{"payload": "{"}'`; `J`: illegal transition `["AVAILABLE", "CLEANED"]`; `K`: differing `sealed_digest`/`observed_digest`; `L`: `writers=["writer-b", "writer-a"]`; `M`: `attempts`/`referenced_attempt_ids` with missing attempt `"att-missing-001"`).
   - **Non-Mutating Verification & Fail-Closed Enforcement:** Replaced misleading `"mutated_differs_from_input"` with `"input_mutated": False` (verified via deep-copy equality before/after `inject()`), added `"harnessed_detected_count": 9` to the matrix output, and enforced fail-closed `VipLabError("HARNESSED_FAULT_NOT_DETECTED", ...)` if any `HARNESSED` fault is not detected (`detected is True` and `disposition == "PASS"`). Preserved `NOT_YET_HARNESSED` (`B`, `C`) and `UNREACHABLE` (`D`, `G`).
2. **Task 2 — Canonical `WorkloadSpec` `concurrency=1` Domain & Negative Rejection Tests (`tests/vip_lab/test_mega12.py`, `tests/vip_lab/test_mega14.py`):**
   - **Root Cause (2 failures in `test_mega12.py` and `test_mega14.py`):** Canonical `src/gate2/workload.py` defines `_LIMITS["concurrency"] = (1, 1)`. The round-trip tests in `test_mega12.py` (`concurrency=5`) and `test_mega14.py` (`concurrency=4`) violated this invariant and raised `WorkloadError: concurrency must be an integer in [1, 1]`.
   - **Correction:** Preserved `src/gate2/workload.py` untouched, updated the valid round-trip fixtures in `tests/vip_lab/test_mega12.py` and `tests/vip_lab/test_mega14.py` to use `concurrency=1` alongside nondefault valid values (`jobs=4..5`, `stages=5..6`, `artifact_bytes=128..256`, `cost_units=17..23`, `fault_position=2..3`, `seed=777..999`, `repetitions=3..4`, and distinct identity digests), and added explicit negative assertions confirming that `concurrency=4`, `concurrency=5`, and `concurrency=True` are rejected.

---

## 4. Wave Status Table

| Wave | Packet ID | Scope | Status | Production Files | Test Files | Blockers / Notes |
|---|---|---|---|---|---|---|
| Wave 1 | `P08` (`MEGA-08`) | Capability & Gap Inventory + Stretch S1/S4/S5 Advisory Crosswalks | `CI_VERIFIED` | `src/vip_lab/mega08/{__init__,capability_inventory,contract_gate,gap_digest}.py` | `tests/vip_lab/test_mega08.py` | `10 PASS` on GitHub Actions run `41846684517` (Python 3.11 & 3.14); untouched. |
| Wave 2 | `P09` (`MEGA-09`) | Batch Retrieval to Nonbinding Review Queue | `CI_VERIFIED` | `src/vip_lab/mega09/{__init__,candidate_queue,queue_validation,review_intake}.py` | `tests/vip_lab/test_mega09.py` | `6 PASS` on GitHub Actions run `41846684517` (Python 3.11 & 3.14); untouched. |
| Wave 3 | `P10` (`MEGA-10`) | Candidate Temporal Request & Source-Native Diagnostic | `CI_VERIFIED` | `src/vip_lab/mega10/{__init__,temporal_request,pts_fixture_diagnostics,measurement_boundary}.py` | `tests/vip_lab/test_mega10.py` | `6 PASS` on GitHub Actions run `41846684517` (Python 3.11 & 3.14); untouched. |
| Wave 4 | `P11` (`MEGA-11`) | Versioned Editorial Proposal (Not an Edit Plan) | `CI_VERIFIED` | `src/vip_lab/mega11/{__init__,editorial_proposal,proposal_revisions,decision_boundary}.py` | `tests/vip_lab/test_mega11.py` | `5 PASS` on GitHub Actions run `41846684517` (Python 3.11 & 3.14); untouched. |
| Wave 5 | `P12` (`MEGA-12`) | Generated-Only Recovery & Replay Consistency + Stretch S3 | `REMEDIATED_UNVERIFIED` | `src/vip_lab/mega12/{__init__,replay_graph,fault_scenarios,consistency_review}.py` | `tests/vip_lab/test_mega12.py` | `3 PASS / 3 FAIL` on run `41846684517`; remediated all 9 `HARNESSED` `FaultClass` payloads (`detected=True`, `input_mutated=False`) in `fault_scenarios.py` and `concurrency=1` fixture + negative `concurrency=4/5` checks in `test_mega12.py`. |
| Wave 6 | `P13` (`MEGA-13`) | QC Evidence Completeness & Export Refusal | `CI_VERIFIED` | `src/vip_lab/mega13/{__init__,lineage_audit,qc_readiness,release_blockers}.py` | `tests/vip_lab/test_mega13.py` | `4 PASS` on GitHub Actions run `41846684517` (Python 3.11 & 3.14); untouched. |
| Wave 7 | `P14` (`MEGA-14`) | Real End-to-End Synthetic Integration, CLI & Report + Stretch S2 | `REMEDIATED_UNVERIFIED` | `src/vip_lab/mega14/{__init__,scenario,report,orchestrator,cli}.py` | `tests/vip_lab/test_mega14.py`, `tests/vip_lab/test_mega08_14_end_to_end.py` | `1 PASS / 5 FAIL` on run `41846684517`; unblocked by `MEGA-12` `fault_scenarios.py` fix and `concurrency=1` fixture + negative `concurrency=4/5` checks in `test_mega14.py`. |

---

## 5. Conditional Stretch Tasks (`S1`–`S5`) Disposition

| Stretch ID | Scope | Host Wave / Module | Status |
|---|---|---|---|
| `S1` | Gate-0 D-2 30-Field Readiness Crosswalk (`0 VERIFIED`, `7 PENDING`, `21 BLOCKED`, `2 NOT_OBSERVED`, `DECLARED_NOT_AUTHENTICATED`) | `MEGA-08` (`src/vip_lab/mega08/capability_inventory.py`) | `CI_VERIFIED` (`41846684517`) |
| `S2` | Cross-Artifact Digest & Foreign-Key Report Verifier (`verify_e2e_lab_report`) | `MEGA-14` (`src/vip_lab/mega14/report.py`) | `REMEDIATED_UNVERIFIED` |
| `S3` | Gate-2 `MeasurementSet` & `NOT_OBSERVED` Discipline (`build_synthetic_recovery_measurement_set`) | `MEGA-12` (`src/vip_lab/mega12/consistency_review.py`) | `CI_VERIFIED` (`41846684517`) |
| `S4` | Gate-1 SigLIP2 3-Profile & Provisional Tokenizer Crosswalk (`GATE_B_NO_GO_BLOCKED`) | `MEGA-08` (`src/vip_lab/mega08/capability_inventory.py`) | `CI_VERIFIED` (`41846684517`) |
| `S5` | Gate-3 A-7 S5 Test-Only Resource Profile Crosswalk (`4096 B` / `8 MiB` / `20,000` samples; `PENDING_EVIDENCE`) | `MEGA-08` (`src/vip_lab/mega08/capability_inventory.py`) | `CI_VERIFIED` (`41846684517`) |

---

## 6. Exact Continuation Point

- **Current State:** `FINAL_MEGA_12_14_CI_CORRECTIONS_COMPLETE_LOCAL` (`342 PASS / 8 FAIL` observed on GitHub Actions run `41846684517` at commit `4076e59e4dfd1f758e82b10fbbaaf2d4b69fe630`; all 8 failures remediated locally across 5 files).
- **Next Action:** Publish only the 5 modified files (`src/vip_lab/mega12/fault_scenarios.py`, `tests/vip_lab/test_mega12.py`, `tests/vip_lab/test_mega14.py`, `tests/vip_lab/test_mega08_14_end_to_end.py`, `docs/ai-studio-tasks/MEGA_08_14_PROGRESS.md`) onto `Centaurioun/video-intelligence-pipeline-2` `main` (`4076e59e4dfd1f758e82b10fbbaaf2d4b69fe630`), ensuring all 6 `src/gate0/media/` files (`__init__.py`, `decode.py`, `probe.py`, `proc.py`, `source_guard.py`, `tool_identity.py`) are preserved untouched, and run `.github/workflows/vip-ai-studio-synthetic-ci.yml` on GitHub Actions (`Python 3.11` and `Python 3.14`) to verify `350/350 PASS`.
