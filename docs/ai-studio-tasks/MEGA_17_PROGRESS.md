# MEGA-17 Progress & Compaction Recovery Ledger (`LAB-MEGA-17-v1.0.0`)

## Current Checkpoint

- `CYCLE_1_COMPLETE`
- `CYCLE_2_COMPLETE`
- `CYCLE_3_COMPLETE`
- `CYCLE_4_COMPLETE`
- `CYCLE_5_COMPLETE`
- `CYCLE_6_COMPLETE`

## 1. Baseline & Repository Identity

- **Target Repository:** `https://github.com/Centaurioun/video-intelligence-pipeline-2` (`LAB` repository ONLY)
- **Canonical Reference Repository (Read-Only):** `https://github.com/Centaurioun/video-intelligence-pipeline` (`main@592952daf475b1bbae2eebdee64d992c1a744f08`)
- **Declared LAB Baseline Reference:** `85a4190925fbb2c6ca11c4b354ad9f1296daf82f` (LAB PR #1 repair head / CI run `41875647638`)
- **Workspace Git SHA (`workspace_git_sha`):** `NOT_OBSERVED` (ZIP-based AI Studio container without `.git`)
- **Verification Status:** `TESTS_AUTHORED_NOT_HOSTED_VERIFIED`
- **Final Delivery Status:** `MEGA17_AUTHORING_DELIVERED_UNVERIFIED`
- **Six `src/gate0/media` Modules Verified Present & Untouched:**
  - `src/gate0/media/__init__.py`
  - `src/gate0/media/decode.py`
  - `src/gate0/media/probe.py`
  - `src/gate0/media/proc.py`
  - `src/gate0/media/source_guard.py`
  - `src/gate0/media/tool_identity.py`
- **Container Snapshot Delta Note:**
  - All `MEGA-03` through `MEGA-16` source modules, tests, and `src/vip_lab/mega16/cli.py` security hardening are present on disk.
  - Because AI Studio does not automatically pull GitHub PR #1 back into the persistent container and `.gitignore` is read-only under MEGA-17 rules, `/.gitignore` line 26 in this container still shows unanchored `media/`.
  - **Publication Requirement:** Publish ONLY the 19 new MEGA-17 files (`src/vip_lab/mega17/**`, `tests/vip_lab/test_mega17_*.py`, `docs/ai-studio-tasks/MEGA_17_*`) onto post-PR #1 `main`. Never overwrite `.gitignore` or existing files from a raw container ZIP export.

## 2026-11-04 Independent Recovery Addendum

- Reconciled current LAB `main@6694b79f3da98d467f96dbc7287e282019401133` with existing repair PR #1; it remains an open PR and its branch must retain the six exact media restoration blobs.
- Failed run `41889181778` failed during MEGA-04 and cross-gate collection because `gate0.media` was absent from that run's LAB `main`. It did not run the six MEGA-17 pytest files. Earlier successful run `41875647638` is on PR #1 head `85a4190925fbb2c6ca11c4b354ad9f1296daf82f`, before MEGA-17 was added to LAB main.
- Independent review found that `run_mega17_product_readiness_chain(scenario=...)` called the hardcoded default three-arm MEGA-15/16 producer. `run_mega15_16_offline_pipeline` now accepts optional `scenario: SyntheticLabScenario | Mapping[str, Any] | None`. With no scenario and no seed, it retains legacy `seed=20261102` behavior; existing callers and output structure remain compatible. MEGA-17 passes the selected scenario and checks arm count plus source/query membership against the returned MEGA-15 occurrence/query identities.
- A second independent review found set-based lineage checks could hide a dropped repeated candidate occurrence. MEGA-17 now joins query, source occurrence, and arm identities by queue item and compares full query/source/arm multiplicities against the selected scenario. A tampered-packet regression covers the dropped-occurrence case.
- Final review also found the arm-name set was derived from the upstream packet. MEGA-17 now checks the single-arm profile through MEGA-14's `PROFILE_ID_TO_ARM` mapping and the three-arm set against MEGA-14's canonical arm constants; the public-chain regression rejects foreign arm labels.
- Additional review repairs: report verification no longer creates missing input directories; generated DEVELOPMENT/EVALUATION partitions are checked across sessions, revisions, content, query IDs, and query text; the editorial packet retains MEGA-15's occurrence identity tuple and reports its absent canonical occurrence ID as `NOT_OBSERVED` instead of deriving one from a revision.
- Source-admission status: generated D-2 and custody prerequisites only. No direct calls to the four admission/sealing APIs listed in the acceptance addendum. No protected media bytes or hashes were read.
- Canonical Gate-0 comparison used original VIP `main@592952daf475b1bbae2eebdee64d992c1a744f08`; the code, manifest, and tests use the correct 40-query / Hit@10 protocol. The false 50-video / Hit@5 / 0.20 / four-arm claims are an external reporting error, not a repository contract or code defect.
- Local Python 3.14 evidence: after the queue-multiplicity and canonical arm-ID checks, all six MEGA-17 suites passed with 37 cases and zero skips; `tests/vip_lab` passed 143/143. Gate-0 tests excluding only the media-generation integration and nine checks requiring absent frozen Git objects or `.orchestration` prompt files passed 1,036/1,036 with zero skips. Those nine environment-bound failures were reproduced in the combined available-tree run. The prior hosted MEGA-17 run on PR #2 head `80f022231cc1b1569f8ae75073e43af4d782bdec` passed Python 3.11 and 3.14 with 35 cases per run; the final candidate needs new hosted verification.

## 2. Cycle Log

### Cycle 1 — Reconnaissance (`CYCLE_1_COMPLETE`)
- Inspected `src/gate0/media/*`, `src/vip_lab/common.py`, `src/vip_lab/integration.py`, `src/vip_lab/mega03..16`, `src/gate0/d2_intake.py`, `src/gate0/labels.py`, `src/gate0/evaluation.py`, `src/gate0/config_freeze.py`, `src/gate3/stream_identity.py`, `src/gate3/refinement.py`, `src/gate3/editorial.py`, `src/gate3/plan.py`, `src/gate3/qc.py`, and existing test suites.

### Cycle 2 — Design and Gap Ledger (`CYCLE_2_COMPLETE`)
- Authored `docs/ai-studio-tasks/MEGA_17_DESIGN_AND_GAP_LEDGER.md` classifying Workstreams A–E using the six canonical MEGA-17 categories and selecting Option A (thin composition & verification layer reusing `mega04`, `mega08`, `mega14`, `mega15`, `mega16`, `gate0`, `gate3`, and `vip_fvs`).

### Cycle 3 — Workstreams A, B, and C Implementation (`CYCLE_3_COMPLETE`)
- Authored `tests/vip_lab/test_mega17_integration_readiness.py`, `tests/vip_lab/test_mega17_source_readiness.py`, and `tests/vip_lab/test_mega17_gate0_readiness.py`.
- Implemented `src/vip_lab/mega17/canonical_integration.py`, `src/vip_lab/mega17/source_readiness.py`, and `src/vip_lab/mega17/gate0_readiness.py`.

### Cycle 4 — Workstreams D and E Implementation (`CYCLE_4_COMPLETE`)
- Authored `tests/vip_lab/test_mega17_editorial_readiness.py` and `tests/vip_lab/test_mega17_release_readiness.py`.
- Implemented `src/vip_lab/mega17/editorial_readiness.py` and `src/vip_lab/mega17/release_readiness.py`.

### Cycle 5 — End-to-End Integration, Verification & Adversarial Suite (`CYCLE_5_COMPLETE`)
- Authored `tests/vip_lab/test_mega17_end_to_end.py` covering all 30 required test categories across single-arm and three-arm LAB configurations.
- Implemented `src/vip_lab/mega17/orchestrator.py`, `src/vip_lab/mega17/verification.py`, and `src/vip_lab/mega17/__init__.py`.

### Cycle 6 — Self-Review, Documentation & Final Delivery (`CYCLE_6_COMPLETE`)
- Authored `docs/ai-studio-tasks/MEGA_17_CROSS_WORKSTREAM_ACCEPTANCE.md`, `docs/ai-studio-tasks/MEGA_17_REAL_EXECUTION_PREREQUISITES.md`, and `docs/ai-studio-tasks/MEGA_17_TEST_MANIFEST.json`.
- Completed self-review verifying zero read-only file mutations and full compliance with Section 1–23 guardrails.
