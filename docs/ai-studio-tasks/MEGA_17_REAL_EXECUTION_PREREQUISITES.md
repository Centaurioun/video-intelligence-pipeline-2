# MEGA-17 — Real Execution Prerequisites & Owner Handoff (`LAB-MEGA-17-v1.0.0`)

This document enumerates every external decision, Owner input, real-media authorization, human review artifact, and runtime prerequisite required to advance the Video Intelligence Pipeline beyond `M3_HOSTED_SYNTHETIC_VERIFIED` into `M4_AUTHORIZED_LOCAL_VALIDATED` and `M5_GATE_EVIDENCE_COMPLETE`.

---

## 1. Immediate GitHub Hosted CI Verification Prerequisite (`M2 -> M3` for MEGA-17)

1. **Selective Additive Publication to `Centaurioun/video-intelligence-pipeline-2`:**
   - Commit and push **ONLY** the 19 newly created `MEGA-17` files (`src/vip_lab/mega17/**`, `tests/vip_lab/test_mega17_*.py`, `docs/ai-studio-tasks/MEGA_17_*`) onto the post-PR #1 `main` branch (`85a4190925fbb2c6ca11c4b354ad9f1296daf82f` or descendant).
   - **CRITICAL:** Do NOT overwrite `.gitignore` or existing repository files from a full AI Studio container ZIP export, so that anchored `/media/` in `.gitignore` and all six `src/gate0/media/*.py` modules remain tracked in Git.
2. **Hosted GitHub Actions Execution (`vip-ai-studio-synthetic-ci.yml`):**
   - Run `pytest` across `tests/vip_lab/test_mega17_*.py` and the full repository regression suite on GitHub-hosted Ubuntu runners (`Python 3.11` and `Python 3.12`).

---

## 2. Workstream A Prerequisites — LAB-to-Canonical Integration (Roadmap Step 2)

1. **Owner Canonical Integration Grant:**
   - Explicit Owner authorization to open a pull request on `https://github.com/Centaurioun/video-intelligence-pipeline`.
2. **External PR Reconciliation (`PR #258` and `PR #259`):**
   - Inspect live Git history of `PR #258` (`Gate-3 A-7 S5-T1` bounded descriptor admission) and `PR #259` (continuity handoff) on canonical `main` before integrating `src/vip_lab/mega03/`.
3. **Wave-Ordered Non-Destructive Adoption:**
   - Execute `WAVE_1_PURE_LAB_PACKAGE` -> `WAVE_2_LAB_SYNTHETIC_TEST_SUITE` -> `WAVE_3_CI_AND_DOC_LEDGER_REVIEW` -> `WAVE_4_OWNER_GATED_CANONICAL_RECONCILIATION`.

---

## 3. Workstream B Prerequisites — Source Identity, Custody, Rights, and D-2/D-3 (Roadmap Step 3)

1. **Authenticated Owner Evidence for the 7 D-2 `EVIDENCE` Fields:**
   - `G0-D2-01`: Real corpus designation (`60–120` minutes, `>=3` sessions, `>=6` revisions, all 4 query families covered, source-disjoint `DEVELOPMENT` and `EVALUATION` splits).
   - `G0-D2-10`, `G0-D2-11`, `G0-D2-12`: Authentic human-authored 40-query set (`24` positive across 4 families, `8` plausible-absent, `8` development).
   - `G0-D2-14`: Appointment of 2 distinct named human reviewers.
   - `G0-D2-17`: Frozen blinding token map (`arm-a`, `arm-b`) and hidden/visible field scope.
   - `G0-D2-26`: Bound non-placeholder `gate_owner_id` across config and manifest.
2. **Closure of the 21 D-2 Contract Rulings (`R-01` through `R-18`):**
   - Includes rights/ownership statement format (`R-03`), retention policy (`R-04`), egress policy (`R-05`), offline model licence & weights digest (`R-06`), sandbox attestation (`R-07`/`R-08`), discovery vs processing purpose-scoped `ALLOW` (`R-09`/`R-10`), freeze approval format (`R-11`), exclusion & split rules (`R-14`), promotion record (`R-15`), sensitivity/relation enums (`R-16`), and post-run blinded audit (`R-18`).
3. **Explicit D-3 Local Execution Grants (`D-3-AUTH-1`, `D-3-AUTH-2`, `D-3-AUTH-3`):**
   - Separate permissions for (1) source path discovery, (2) local byte inspection & SHA-256 hashing, (3) derived artifact creation, (4) authentic local model execution, (5) strict no-egress enforcement, and (6) retention/cleanup.

---

## 4. Workstream C Prerequisites — Gate-0 Diagnostic Retrieval Experiment (Roadmap Step 4)

1. **Authentic Dual-Reviewer Gold Event Cataloging (`G0-D2-18`):**
   - Two independent human reviewers grade evaluation intervals (`0/1/2`) with explicit rational uncertainty bounds (`{numerator, denominator}`) and adjudicate any disagreements.
2. **Frozen Offline Model & Sandbox Environment (`G0-D2-20..24`):**
   - Approved local SigLIP V1 weights SHA-256, processor digest, bubblewrap (`bwrap`) sandbox attestation, and pinned dependency lockfile with zero network egress.
3. **Authentic Gate-0 Run & Post-Ranking Blinded Top-10 Union Audit (`G0-D2-19`, `G0-D2-27`):**
   - Execute both `metadata-floor` and `offline-development-arm` over the held-out evaluation split, verify `Hit@10 >= 20/24`, paired lift `>= 5/24`, and per-family `Hit@10 >= 3/6`, and obtain signed Owner promotion (`G0-D2-27`).

---

## 5. Workstream D Prerequisites — Gate-3 Native Temporal & Editorial Workflow (Roadmap Step 6)

1. **A-7 Positive Stream Mapping & S5-T1 Admission:**
   - Adopt positive ffprobe-to-ISO-BMFF track identity mapping (`gate3.stream_identity.StreamIdentityEvidence.state == "PROVEN"`) and bounded descriptor-relative source admission.
2. **Byte-Bound Source-Native PTS / Frame Measurement (`FR-01` / `FR-02`):**
   - Measure actual container bytes via `gate3.refinement.refine` to produce `is_binding_eligible == True` records with verified `dts_ticks` reorder evidence (`T8`) and `duration_consistency == "MATCH"` tail evidence (`IT-6`).
3. **Authenticated Human Editorial Decision (`gate3.editorial.EditorialDecision`):**
   - Real human editor inspects the sealed `ReviewBundle` and records a non-fixture `EditorialDecision` (`principal_kind == "human"`, `real_authority_eligible == True`) pinned to the measured refinement digest.

---

## 6. Workstream E Prerequisites — Render, Export, QC, and Release (Roadmap Step 7)

1. **Explicit Render & Local Preview Authorization:**
   - Separate authorization to invoke local `ffmpeg` over byte-verified source media and an approved `EditPlanRevision(plan_scope="REAL")`.
2. **Three Independent Post-Render QC Observations:**
   - **Technical Post-Render QC (`MEASURED`):** Independent verifier attestation (`is_verifier_produced == True`, `agreement == "AGREE"`, `independent_of_producer == True`) re-measuring rendered output bytes and stream indices.
   - **Visual Editorial QC (`VISUALLY_OBSERVED`):** Human visual inspection of rendered cut boundaries, framing, and transitions.
   - **Audio / Sync Editorial QC (`AUDIO_OBSERVED`):** Human audio inspection of musical phrasing, lip/footfall sync, and splice continuity.
3. **Final Owner Production Export Grant:**
   - Evidence-backed principal authority capability satisfying `EditPlanRevision.export_eligible == True` and explicit Owner release sign-off.
