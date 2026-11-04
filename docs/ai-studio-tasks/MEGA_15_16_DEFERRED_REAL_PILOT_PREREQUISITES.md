# MEGA-15 + MEGA-16 Deferred Real-Pilot & Canonical Integration Prerequisites (`LAB-MEGA-15-16-v1.0.0`)

- **Document Role:** Read-only evidence and prerequisite mapping for deferred roadmap steps **2**, **3**, and **4** referenced in `docs/ai-studio-tasks/MEGA_15_16_GATE3_OFFLINE_PREPARATION_PROGRAM.md`.
- **Authority Notice:** This document is a technical readiness and prerequisite map only. It **grants no execution authority**, **activates no Gate**, **approves no real media or model access**, and **authorizes no push or merge into canonical `Centaurioun/video-intelligence-pipeline`**.

---

## 1. Roadmap Overview & Boundary Separation

| Roadmap Step | Scope | Status after `MEGA-15 + MEGA-16` | Execution Venue |
| --- | --- | --- | --- |
| **Step 1** | Complete all remaining offline synthetic Gate-3 preparation, editorial handoff, lineage, render/export/QC preflight, and release-refusal lab modules (`MEGA-15 + MEGA-16`). | `IMPLEMENTED_UNVERIFIED` in AI Studio (ready for hosted GitHub Actions CI on `Centaurioun/video-intelligence-pipeline-2` across Python 3.11 and 3.14). | Google AI Studio (`LOCAL WORKSPACE CHANGES ONLY`) -> `Centaurioun/video-intelligence-pipeline-2` (`main`) |
| **Step 2** | Selectively review and integrate proven `vip_lab` waves into the canonical repository (`Centaurioun/video-intelligence-pipeline`) via isolated branch/PR workflow. | `DEFERRED` / `BLOCKED_ON_OWNER_AND_CANONICAL_REVIEW` | Local Git/Codex controller with full Git history, PR workflow, and canonical branch reconciliation |
| **Step 3** | Execute authorized local real-media pilot and Gate-0 D-2 / D-3 diagnostic retrieval experiment on the designated macOS M4 Max host. | `DEFERRED` / `BLOCKED_ON_D2_INPUTS_AND_D3_AUTHORIZATION` | Owner-designated local macOS M4 Max host (`authorized_local` mode after D-2 & D-3) |
| **Step 4** | Execute Gate-1 authentic representation benchmark (`SigLIP V1 Base`, `SigLIP2 V2 Base`, `SigLIP2 V2 SO400M`), Gate-2 real-archive workload measurement, and Gate-3 real-source temporal refinement, human editorial decision, preview, export, and QC. | `DEFERRED` / `BLOCKED_ON_UPSTREAM_GATES_AND_OWNER_DECISIONS` | Owner-designated local host after Gate-0 acceptance and Gate-1/2/3 specific authorizations |

---

## 2. Step 2 Prerequisites — Selective Canonical Repository Integration

Before any code from `Centaurioun/video-intelligence-pipeline-2` (`src/vip_lab/mega03..16`, `tests/vip_lab/**`) is proposed for integration into `Centaurioun/video-intelligence-pipeline`:

1. **Hosted Dual-Python CI Green on LAB `main`:**
   - GitHub Actions workflow `.github/workflows/vip-ai-studio-synthetic-ci.yml` must pass all `MEGA-03..16` and B08 synthetic suites on both **Python 3.11** and **Python 3.14**, with zero regressions and intact `src/gate0/media/` modules.
2. **Canonical `main` Head & Open PR Reconciliation:**
   - Fetch live `origin/main` on `Centaurioun/video-intelligence-pipeline` (do not assume the historical ZIP baseline `592952daf475b1bbae2eebdee64d992c1a744f08` is current).
   - Reconcile against known post-snapshot canonical work, specifically:
     - **PR #258** (Gate-3 A-7 S5-T1 bounded admission candidate)
     - **PR #259** (ChatGPT continuity handoff)
     - Adopted H3 contract cores (`H3-C05 v1.0.2`, `H3-A04 v1.0.1 Option B`)
     - Gate-3 A-7 S5 owner adoptions (`docs/decisions/2026-10-28-a7-s5-shared-admission-owner-adoption.md`, `docs/decisions/2026-10-29-a7-s5-scoped-synthetic-tdd-plan-owner-adoption.md`)
3. **Isolated Branch & PR Governance:**
   - Never push AI Studio ZIP snapshots directly to canonical `main`.
   - Land curated, exclusiva-path diffs in isolated branches/PRs with independent code review and full canonical verifier (`scripts/verify-workspace.sh`) + full-suite CI verification.

---

## 3. Step 3 Prerequisites — Authorized Real-Media Pilot & Gate-0 Diagnostic Experiment

Executing Gate 0 (`G0.1.5`, `G0.2.2`, `G0.2.3`, `G0.3.*`, `G0.4.*`) on real performing-arts media requires all of the following currently `NOT_OBSERVED` / `PENDING` prerequisites:

| Category | Required Evidence / Artifact | Current State | Governing Contract / Checker |
| --- | --- | --- | --- |
| **Source Rights & Custody (`D-2`)** | Owner-approved rights/retention attestation and `authorized-corpus.json` covering 60–120 minutes, `>= 3` sessions, `>= 6` source revisions, and visual-family distribution. | `PENDING` / `NOT_OBSERVED` (`0 VERIFIED / 7 PENDING / 21 BLOCKED / 2 NOT_OBSERVED`) | `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md`, `src/gate0/d2_intake.py`, `docs/gate0/D2_OWNER_INPUT_INTAKE_CHECKLIST_2026-10-25.md` |
| **Immutable Source Inventory & No-Follow Hashing** | Descriptor-relative (`O_NOFOLLOW`) read-only admission, SHA-256 content digests, FFprobe stream/PTS probe artifacts, and nonleaking development/evaluation partition freeze. | `NOT_OBSERVED` on real archive corpus | `src/gate0/media/source_guard.py`, `src/gate0/media/probe.py`, `docs/architecture/CANONICAL_CONTRACTS.md` |
| **Human Queries (`G0.2.2`)** | 24 positive editor-authored queries (6 per visual family), 8 plausible-absent queries, and 8 development queries frozen before viewing held-out rankings. | `NOT_OBSERVED` (synthetic loaders verified only) | `src/gate0/labels.py`, `src/gate0/d2_intake.py` |
| **Independent Human Ground Truth (`G0.2.3`)** | Two independent human reviewers grading revision/interval events under blinded mapping bound to canonical `config_digest`, plus adjudicated gold labels. | `NOT_OBSERVED` | `src/gate0/reviewer_envelope.py`, `src/gate0/evaluation.py` |
| **Authentic Local Model & Host Lock (`G0.3.1`)** | Pinned local `SigLIP V1 Base` weights digest, offline-reproducible `torch`/`transformers` lockfile, and macOS Stage-B host/entitlement attestation. | `BLOCKED_DEPENDENCY_VERIFICATION` / `NOT_OBSERVED` | `src/gate0/config_freeze.py`, `requirements/gate0.lock` |
| **Explicit `D-3` Execution Grant** | Separate Repository Owner decision authorizing `authorized_local` execution (`authorized_local_execution_gate_open() -> True`). | `NOT_AUTHORIZED` (hard-coded `False`) | `src/gate0/execution.py`, `docs/decisions/2026-10-25-gate0-d1-source-only-preparation-approved.md` |

---

## 4. Step 4 Prerequisites — Gate-1 Benchmark, Gate-2 Scale, and Gate-3 Real Editing / Export / QC

### 4.1 Gate-1 Authentic Three-Profile Benchmark (`ADR-0002`)
- **Upstream Gate Dependency:** Validated Gate-0 experiment outcome (`PASS` or explicit Owner benchmark directive) and frozen held-out evaluation protocol.
- **Model & Runtime Prerequisites:**
  - Explicit Owner approval to load/execute authentic weights for `siglip_v1_base` (768-D), `siglip2_v2_base` (768-D, incompatible space), and `siglip2_v2_so400m` (1152-D).
  - Resolution of provisional tokenizer/processor/pooling evidence (`docs/migrations/siglip2-post-completion/32_PROVISIONAL_SIGLIP2_TOKENIZER_PROCESSOR_POOLING_CONTRACT.md`) and native Task-4/5 execution exception (`Gate B` currently `NO_GO_BLOCKED`).
  - If any external/cloud provider arm (`DeepSeek`, `Gemini`, `TwelveLabs`) is evaluated, a separate policy/egress decision (`ALLOW` with manifest digest, spend/byte limits, and retention rule) is required per `CANONICAL_CONTRACTS.md` §5.

### 4.2 Gate-2 Real-Archive Workload & Recovery Justification
- **Workload Observation Prerequisite:** Measured latency, memory, restart/recovery, and index-size telemetry on authorized real archive workloads (`G2.1.3` real archive counts currently `NOT_OBSERVED`; synthetic `BR-1` result does not generalize to real archive scale).

### 4.3 Gate-3 Real-Source Temporal Refinement, Editorial Decision, Render & QC
Before `ExportReadinessPacket.export_status` can transition from `"REFUSED_NOT_AUTHORIZED"` in a real Gate-3 workflow, the following independent gates and evidence items must be satisfied:

| Requirement | Current State in `MEGA-15 + MEGA-16` | Required Real-Pilot / Production Prerequisite |
| --- | --- | --- |
| **Source-Native PTS / Timebase Evidence** | `source_pts_evidence_state = "NOT_OBSERVED"`, `gate3.refinement.is_binding_eligible == False` | Byte-bound ISO-BMFF container measurement and FFprobe frame/packet PTS observation on immutable source bytes (`MEASURED`), with origin-zero edit-list check and VFR presentation-delta classification. |
| **Stream Identity Mapping (`A-7`)** | Refused when unproven (`REFUSAL_STREAM_NAMESPACE_UNPROVEN`) | Contract-owner/Owner adoption and byte-bound verification of positional `P2` (`probe_streams[i].id == traks[i].tkhd.track_ID` for all `i`, pairwise unique in `1..0xFFFFFFFE`) per `docs/decisions/2026-10-25-g3-a7-stream-namespace-positive-mapping-disposition.md` and `2026-10-28-a7-s5-shared-admission-owner-adoption.md`. |
| **Terminal Stream-Tail Policy (`IT-6`)** | Refused for exact cut (`REFUSAL_TERMINAL_TAIL_UNCERTAIN`, `P3` interim deferral) | Explicit Owner + Gate-3 contract-owner `IT-6` ruling (`P2m` pinned-certification or `P2r` re-measurement with R-8/A-11 grants) per `docs/decisions/2026-10-25-g3-g4-terminal-tail-disposition.md`. |
| **Human Editorial Decision** | `real_human_decision_state = "NOT_OBSERVED"`, `human_decision_artifact_minted = False` | Authenticated human reviewer decision (`principal_kind == "human"` with non-null `principal_authority_evidence` once human authority verification is enabled) bound to exact `ReviewBundle` and measured refinement digest. |
| **Authoritative Edit Plan** | `authoritative_edit_plan_created = False`, `EditPlanRevision.export_eligible == False` | Versioned `EditPlanRevision` pinning byte-bound certified refinements (`is_binding_eligible == True`) and verified human editorial decisions. |
| **Non-Production Local Preview vs Production Export** | `preview_policy_authorized = False`, `render_executed = False`, `production_export_authorized = False` | Separate authorization for bounded local preview (`vip_fvs.local_preview`) versus production export; a passing non-production preview never authorizes production export. |
| **Independent Technical & Editorial Sensory QC** | `technical_qc_observed = "NOT_OBSERVED"`, `visual_editorial_qc_observed = "NOT_OBSERVED"`, `audio_editorial_qc_observed = "NOT_OBSERVED"` | Post-render container/PTS/duration re-measurement (`MEASURED`), human/grounded visual QC (`VISUALLY_OBSERVED`), and audio/sync QC (`AUDIO_OBSERVED`) with non-empty `qc_scope` and `supporting_evidence_refs` (`gate3.qc.bare_pass_is_insufficient == False`). |
