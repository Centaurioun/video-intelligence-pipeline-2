> **SUPERSEDED ENTRYPOINT — 2026-10-26:** The complete latest onboarding handoff is [2026-10-26_CHATGPT_HANDOFF_POST_H3_CONTRACT_ADOPTION.md](2026-10-26_CHATGPT_HANDOFF_POST_H3_CONTRACT_ADOPTION.md). This 2026-10-25 record remains a preserved dated snapshot; its `main`, open-PR and next-task claims are historical. Verify current GitHub before continuing; do not revert already adopted H3-C05 v1.0.2 or H3-A04 v1.0.1 to `NOT_ADOPTED`.

# ChatGPT Continuity — START HERE: Video Intelligence Pipeline

**Snapshot date:** 2026-10-25 (Europe/Istanbul)  
**Purpose:** durable first-read handoff for a completely new ChatGPT conversation. Resume the existing Owner/ChatGPT collaborative project without asking the Owner to repeat its history.  
**Primary repository:** https://github.com/Centaurioun/video-intelligence-pipeline (Owner: `Centaurioun`; private — use the authenticated GitHub connector)  
**Status:** evidence-backed *dated snapshot*, not an authority that supersedes a newer GitHub commit or the Owner.  
**GitHub main independently checked immediately before this handoff:** `f5366ef226a01c6e919350abb9947746e55b8dd2` (merged PR #179).  
**Main synthetic CI at this checkpoint:** https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/40177693603 — completed successfully on Python 3.11 and 3.14; **this is selected smoke, not a complete Gate test or authentic media/model certification**.  
**Open pull requests at this checkpoint:** only **#169**, a Dependabot Next.js change inside a frozen historical reference-pack; unrelated to the four-Gate product frontier.  
**Immutable Owner backup:** `backup/OWNER-DO-NOT-MODIFY-main-20261024-17edacbe` at **`17edacbe64983ae284f09a8386377200bf538ec3`**. It was independently re-read and unchanged immediately before creating this handoff. **Do not change, rename, reset, delete, rebase, merge into, force-push or otherwise touch this branch.** Owner warning: https://github.com/Centaurioun/video-intelligence-pipeline/issues/149.

> **FIRST ACTION IN THE NEW CHAT:** Re-read live `main`, open PRs, status checks, current governing documents and this file via GitHub, then report the verified present-tense state. Treat all SHAs and statuses below as dated observations. Do not blindly assume the previous assistant's or DeepSeek's success claims.

---

## 1. How to collaborate with the Owner

- Converse in **Turkish** by default. The Owner is comfortable with **English technical specs, DeepSeek/Codex prompts and WBS task trees**.
- The Owner's priority is **finish the working Gate 0–3 product, not endless review, bureaucracy, small Gemini optimizations, unrelated tests, ancient PR cleanup, or synthetic task inflation**. Genuine product correctness and evidence discipline take priority over the number of launched agents.
- Be proactively useful: independently inspect GitHub, compare the Owner's supplied DeepSeek deliverable to actual PR head/code/diff/CI, identify true blockers versus harmless residuals, and propose the next shortest dependency-safe route. Avoid making the Owner repeat known context or answer broad questionnaires.
- The normal rhythm has been: ChatGPT drafts **self-contained English Goal prompts**, the Owner launches 2–4 **DeepSeek Flash LOW** coding sessions in separate local threads/worktrees, sends back their reports, and ChatGPT independently verifies GitHub, reviews findings, integrates truly accepted PRs in safe dependency order when the Owner has authorized the integration workflow, updates the four-Gate WBS and proposes the next READY wave.
- Do not claim to launch local DeepSeek/Codex agents through GitHub; ChatGPT's GitHub connector can inspect/edit PRs but is not a local process runner. If execution needs the local Mac, provide ready-to-paste Goal prompts with precise ownership.
- Use Superpowers **trigger-based**: new architecture/interface `brainstorming`; approved design `writing-plans`; isolated implementation `using-git-worktrees`; actual behavior change `test-driven-development`; unexpected failure `systematic-debugging`; independent features `dispatching-parallel-agents` under repository rolling frontier; before merge `requesting-code-review`; all success claims `verification-before-completion`. The repository's `AGENTS.md` and current executor policy outrank generic stock workflow defaults.
- The Owner likes **Six-Cycle Iterative Refinement**: (1) live evidence and scope, (2) gap/authority/dependency audit, (3) alternatives and smallest solution, (4) executable branch/task plan, (5) adversarial reviews and tests, (6) independently verified integration + next frontier. Preserve what was rejected and what would cause reconsideration.
- Explicit high-level design approval does **not** silently authorize every detailed schema/contract change or real-world operation. Route undecided exact items for a narrow Owner/contract-owner decision; continue other independent READY tasks meanwhile.

## 2. Startup order and authority precedence

Read **in this order** after this handoff:
1. `AGENTS.md` and `docs/INDEX.md`.
2. `docs/project/00_PROJECT_CHARTER.md`.
3. `docs/project/01_CURRENT_STATE_AND_HANDOFF.md` — chronological overlays can contain very old "current" assertions; newest live ref/evidence wins.
4. `docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md` — some earlier Atlas/branch-recovery portions are historical for this product-completion wave.
5. `docs/project/STATE_MAINTENANCE_PROTOCOL.md`.
6. **Canonical Owner-approved Gate 0–3 execution tree:** [Four-Gate WBS](12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md).
7. Gate-specific frozen contracts, ADRs, latest plans, actual code and tests **only for the next task**. Do not exhaustively ingest the entire legacy repository, reference packs or archived branches.

Authority sequence: **explicit current Owner instruction > frozen governing contracts/decisions > Owner-approved design > approved implementation plan > task packet > controller ruling > child implementation choice**. Project uploads, older summaries, historical PR descriptions and agent report assertions cannot independently grant new authority. Use **VERIFIED**, **PENDING**, **BLOCKED**, **NOT_OBSERVED**, **IMPLEMENTED** and **VERIFIED_NO_CHANGE** precisely.

Source of truth is current GitHub and independently checked source; if private GitHub connection is missing, request an authenticated connection before claiming live repo status. Do not substitute public web search for private repository files.

## 3. Mission, architecture, hard invariants

Mission: a local-first/selectively hybrid video-intelligence and editing pipeline for a large **dance, ballet, music and performing-arts archive**:

`source/archive → deterministic inventory/provenance → semantic useful-moment retrieval → source-native temporal refinement → measured PTS/frame evidence → human editorial decision → versioned edit plan → render/export → technical/editorial QC`.

The **four Gate questions**:
- **Gate 0 — Diagnostic Retrieval:** can a bounded local semantic visual arm improve useful-moment discovery versus an explicit metadata floor?
- **Gate 1 — Representation/Capability:** which local/provid­er representation or modality merits genuine comparative selection?
- **Gate 2 — Reliability/Scale:** which restart, recovery, caching, queueing, persistence or index mechanisms are justified by **measured** workload failures?
- **Gate 3 — Editing/QC:** can candidates be deterministically refined into attributable human editorial plans, renders and valid QC evidence?

Hard invariants:
- Source bytes immutable by default. Paths, vector IDs and provider IDs are not canonical content identity.
- Evidence classes: `MEASURED`, `MATCHED`, `VISUALLY_OBSERVED`, `AUDIO_OBSERVED`, `EDITORIAL_INFERENCE`. `NOT_OBSERVED` is a *state marker*, not a sixth class; do not silently upgrade it.
- A semantic timestamp is a retrieval **candidate**, not an exact cut. Use exact measured source-native presentation **PTS/timebase** and stream/source identity; **never use seconds × nominal FPS for VFR frames** and never silently substitute DTS for presentation PTS.
- Human editorial selection is authoritative and distinct from a model match. Technical QC PASS does not imply production or export eligibility.
- No protected/archive execution; no authentic model download/load or MPS inference; no provider/network calls; no real-media edit/export, Gate promotion, destructive cleanup, or production deployment **without fresh, exact Owner operational authorization**. Locally generated disposable **synthetic** fixtures and approved source-only code work have their own narrow scope.
- `ADR-0003` removed ordinary *development* SOURCE-AUTH enforcement by Owner decision: `DISABLED_BY_OWNER`, **not** PASS. Do not recreate an administrative Owner-Witness/grant bureaucracy for ordinary code work. This does **not** grant access to protected source media.
- Use isolated branches/worktrees, exclusive writers, immutable input/candidate SHAs, rolling-frontier scheduling, adaptive resource policy v5. Never hard reset, git clean, force push, delete worktrees/branches or prune recovery objects without explicit instruction.

## 4. Exact current integrated milestone and verification level

**At 2026-10-25 checkpoint (all verified GitHub merged status):**
- [#178](https://github.com/Centaurioun/video-intelligence-pipeline/pull/178) → merge `ee588e0f3768e3827d41400f3563b6d621744b5b` — Gate 0 F2/F3/F4 evidence-integrity fixes.
- [#176](https://github.com/Centaurioun/video-intelligence-pipeline/pull/176) → merge `86d281101db1e29506a4692e52b3e937500ba3c1` — Gate 3 **strict-V1 origin-zero** enforcement.
- [#177](https://github.com/Centaurioun/video-intelligence-pipeline/pull/177) → merge `43f6faf9333673b9495483e52c9557fe0a93c896` — Gate 3 A-3 decision proposal, IT-2 RED evidence and adversarial test matrix; **not v2 code**.
- [#179](https://github.com/Centaurioun/video-intelligence-pipeline/pull/179) → merge `f5366ef226a01c6e919350abb9947746e55b8dd2` — current Gate 0/3 WBS and repository handoff reconciliation.
- At the last main SHA, **GitHub two-Python selected synthetic smoke is green**. This verifies only that selected workflow, not every test or actual Gate acceptance.
- DeepSeek/local reports at the corresponding approved candidate heads: Gate 0 **806 local tests passed** + generated MP4 13/13 schema payloads, FK + manifest closure and 17/17 expected mutation results; Gate 3 **1150 passed and 3 strict-xfail** in one developer integration worktree. These figures are *agent-reported local verification with code/log evidence*; **not a fresh independent full-suite rerun by ChatGPT on latest main**. The three strict xfails capture missing v2 behaviors and are deliberately **NOT implemented success**.
- The protected backup SHA above is unchanged. PR #169, a frozen reference-pack Dependabot update, is open and unrelated; do not let it interrupt Gate product completion.

**Earlier accepted milestones (read their PRs for exact file changes if needed):**
- #154 four-Gate English WBS; #155–#158 parallel readiness audits; #159 active-handoff/launch packet; #125 bounded Gate-0 S8 accepted with recorded R-11/R-12 limitations; #160 Gate-1 model-free storage/search source; #161 measured Gate-2 synthetic journal workload; #162 Gate-3 synthetic FVS/fixture preview; #163 Gate-0 ten-stage synthetic dispatcher; #164 WBS update.
- #165 Owner-reviewed C′ Gate-3 design; #167 detailed Gate-3 plan; #168 Gate-0 schema/media closure plan; #170 FFprobe 9.x packet/frame reconciliation; #171 exact Gate-3 A-1…A-12 authority matrix; #172 PTS multiplicity/stream admission; #173 D1–D9 Gate-0 closed payloads and generated MP4; #174 reconciliation; #175 D8 milestone bookkeeping.
- #166 old Gate-0 partial base closed **without merge** as fully ancestral to #173; historic small Gemini PRs #99–#120 and seven stale V2/orchestration proposals were closed without merge, useful insights saved in [issue #152](https://github.com/Centaurioun/video-intelligence-pipeline/issues/152); their branch/history preservation does not constitute approval.

## 5. Gate-by-Gate current capabilities and remaining actual product work

### Gate 0 — Diagnostic retrieval

**IMPLEMENTED/VERIFIED IN SYNTHETIC SCOPE:**
- Existing ten-stage CLI: `prepare → inventory → split → label → preflight → extract → embed → rank → evaluate → report` with deterministic 13-artifact output/closure. Generated disposable MP4 on local FFprobe/decoder path supplies **MEASURED** source PTS (including CFR/VFR/B-frame cases), exact rational sampling, stable source digests, byte quotas and no-follow regular-file access.
- `report` intentionally exits **20**, returns `benchmark_status=NOT_RUN` and `gate_decision=NOT_RUN` for generated fixtures. Fake embeddings/labels are `SYNTHETIC_FIXTURE`, not real benchmark truth. No valid Gate-0 outcome claim.
- Source-only D1–D9 corrections, closed schemas **13/13**, metadata `representation_kind=metadata_floor` vs embedding-arm registry, non-fictional metadata representation semantics, legitimate failed-vector status rows.
- Gate-0 F2 (ranked and judgment `window_id` resolve to canonical `window_sample_manifest.jsonl` sample targets even when sampling failed; representation revision to source inventory FK), F3 (both declared arms must have ranked rows when rankings are nonempty, with valid pre-ranking and failed rows), and F4 (standalone `--manifest-closure` now executes, refuses missing candidate root and broken graph, and remains separate from `--foreign-keys` semantic checks and `--schema-payloads` structural checks). These are in #178.

**REMAINING / NOT_OBSERVED:**
- Actual approved 60–120 minute / ≥3-session / ≥6-revision corpus with exact source rights; editor-frozen 24 positive/8 absent queries across four visual families, two independent blinded human reviewers; real licensed offline embedding weights and approved runtime; Gate-0 Stage-B host/`bwrap` attestation; authentic ffprobe/decoder pilot on admitted real sources; real paired experimental run and thresholds.
- Frozen acceptance thresholds: semantic Hit@10 ≥ **20/24**, paired improvement ≥ **5/24**, every family ≥ **3/6**. Synthetic illustrative figures cannot satisfy these.
- Narrow post-#178 open issues: `DR-F2-c` revision↔window identity schema affordance; `DR-F2-d` FINITE vs successful decoded sample rule; `DR-F3-judgments` whether judgments require each arm; orphan unranked representation-window FK; declared digest **reference closure vs actual artifact-byte rehash**; D2 typed-interval producer and D3 gold-event schema materialization. Do **not** autonomously amend frozen contract for these; prioritize only blockers to actual product experiment. A task checkbox may mean synthetic capability, not true Gate acceptance.
- Priority after current Gate-3 decision work: choose the smallest missing real-experiment prerequisite and prepare a concrete Owner permission/input packet rather than repeatedly polishing tests.

### Gate 1 — Representation/Capability

**IMPLEMENTED model-free:** V1 preserved (V1 baseline preservation ref `preservation/vip-v1-post-v2-design-20261009@3586eeaa904fc5a2e6a2745078611886f482f3de`). Closed profile identities, width-aware V2-Base 768D / SO400M 1152D storage and query geometry, correct fail-closed committed-prefix reads, guarded `open_siglip2_session` interface that **has no authentic default loader**. Fake-injected `siglip2_native.py` is **NOT an authentic SigLIP2 runtime**. Gate-1 synthetic harness/benchmarks do not prove comparative quality. Evidence: [#160](https://github.com/Centaurioun/video-intelligence-pipeline/pull/160) and [execution report](../agent-runs/2026-10-25-gate1-v2-representation-execution/README.md).

**PENDING:** ADR-0002/Gate-B or exact Owner exception on Task 4/5 native source, actual tokenizer/processor/weights provenance and model acceptance on local MPS, genuine V1 vs V2 Base vs SO400M three-arm benchmark only after eligible Gate-0 evidence, source-native CLI handshake/real adapter. Do not treat proposed native source-only exception as adopted, invent BOS/EOS tokenizer IDs or download weights silently.

### Gate 2 — Reliability/Scale

**IMPLEMENTED/MEASURED local synthetic:** PR [#161](https://github.com/Centaurioun/video-intelligence-pipeline/pull/161) ran frozen six-job / four-stage / 65,536-byte-per-stage workload, three repetitions, journal interruption/resume, source commit binding, byte/recovery verification and real host timing/RSS/disk measurements. Two reproducible runs on an Apple M5 Pro development host reported no integrity mismatches or duplicate writes. The measured same-run decision **BR-1** is only **"this bounded simpler architecture met its frozen synthetic bounds"**, not archive-scale proof. Developer reports **829 Gate-2 tests passed**; independently re-check before any stronger claim.

**PENDING:** bounded owner-designated representative real V1 workload and exact source/host authorization, then scale and selected model representation data. No cache/Redis/queue/ANN/complex scheduler without real measured deficit. Some mechanism classes are unresolved at BR-8, not a reason to prematurely implement more infrastructure.

### Gate 3 — Editing/QC

**IMPLEMENTED synthetic/non-production:**
- Gate-3 source snapshot/retained-byte identity and temporal binding infrastructure; synthetic FVS `candidate → source binding → source-native refinement → human-decision placeholder → versioned edit plan → generated fixture preview → QC receipts` via [#162](https://github.com/Centaurioun/video-intelligence-pipeline/pull/162). `preview-fixture` on generated MP4/AAC drops audio by `VIDEO_ONLY_DROP_AUDIO_V1` and maintains `export_eligible=false`. `SYNTHETIC_HUMAN` is never authentic human editorial acceptance.
- IT-0 FFprobe 9.x `packets_and_frames` parsing with correct frame-only multiplicity ([#170](https://github.com/Centaurioun/video-intelligence-pipeline/pull/170)), IT-7 preserved duplicate presentation PTS and consistent stream-row admission ([#172](https://github.com/Centaurioun/video-intelligence-pipeline/pull/172)).
- Owner **APPROVED HIGH-LEVEL DIRECTION ONLY**: **C′** composed temporal authority: per-fact ownership, exact bidirectional comparison of FFprobe vs ISO-BMFF source-native timing, source/stream identity and re-verification. **Strict V1:** `elst.media_time == 0`; any nonzero offset refuses (`EDIT_LIST_ORIGIN_NOT_APPLIED`), as implemented in [#176](https://github.com/Centaurioun/video-intelligence-pipeline/pull/176). No edit-list offset-normalizing V2 was approved.
- [#177](https://github.com/Centaurioun/video-intelligence-pipeline/pull/177) **merged only documentation + adversarial tests**, captured presentation-vs-decode VFR divergences and duration inconsistency; **3 intentional strict-xfail RED cases** remain. It **did not implement** a schema-v2 snapshot binder or C′ composition.

**CRITICAL PENDING DECISION: A-3 / IT-1 — the immediate design decision to resume.**
Read:
- [C′ architecture spec](../superpowers/specs/2026-10-25-gate3-dual-temporal-authority-composition-design.md)
- [Gate-3 implementation plan](../superpowers/plans/2026-10-25-g3-cprime-v1-temporal-authority-implementation.md)
- [A-1…A-12 authority disposition matrix](../agent-runs/2026-10-25-g3-cprime-v1/authority-disposition-matrix.md)
- **[A-3 / D-1…D-5 exact decision proposal](../agent-runs/2026-10-25-g3-temporal-binding-wave3/a3-decision-proposal.md)**
- [Measured v1 compatibility](../agent-runs/2026-10-25-g3-temporal-binding-wave3/v1-evidence-baseline.md)
- [IT-8 provenance blockers](../agent-runs/2026-10-25-g3-temporal-binding-wave3/it8-provenance-handoff.md)
- [Adversarial independent review](../agent-runs/2026-10-25-g3-temporal-binding-wave3/independent-review.md)

The implementation controller recommended **Option A′** in the merged #177 proposal, but its status is **`DECISION_REQUEST_PENDING` — NOT Owner-approved**. A′ proposes:
1. **D-1:** additive snapshot temporal **`schema_version: 2`**; retain v1 exact shape/verification.
2. **D-2:** exactly **six** additional verified retained-byte facts: `duration_ts` (measured), `duration_consistency` (DERIVED from measured inputs, not independent measurement), `tail_duration_ticks`, `presentation_origin_ticks`, `stream_handler`, `stream_identity_derivation`. Do not automatically adopt the old nine-field list or duplicate `nb_frames` / `has_b_frames` / `composition_offsets`.
3. **D-3:** keep existing v1 `bind_temporal_authority(...)` creation signature and legacy VFR predicate unchanged for historic v1 receipts; introduce additive `bind_temporal_authority_v2(...)`; `verify_temporal_authority(...)` branches on version **before** closed field-set validation and rebinds separately. No v1-to-v2 silent upgrade.
4. **D-4:** v2 `duration_ts` key requires replacing a **frozen source-token safety assertion** in `tests/vip_fvs/adversarial/test_source_snapshot_temporal_safety.py` with a **well-tested, narrow AST/provenance rule**. The sketch in the proposal is **not production code and may still be overstrict or incomplete**; inspect the AST semantics with actual negative controls before accepting an amendment. Absolutely forbid duration/FPS arithmetic masquerading as measured PTS.
5. **D-5:** a consumer requiring v2 facts must refuse a v1-only receipt; error-name freeze under A-5 is separately **PENDING**.

Alternatives described in the source: B = separate composed temporal artifact, requiring unapproved new module A-6 and extra parse/seal; C = narrow v1 derive/refuse, cannot carry VFR-basis correction or measured stream-tail facts. The recommendation is A′ for smaller source-only v2 change, preserving historic v1 exact semantics. **But ask for exact Owner/contract-owner disposition on D-1…D-4 before shipping new schema behavior** (D-5 as required for v2 consumers). The earlier Owner approval of C′/strict V1 is **not** A-3 approval.

**Other Gate-3 decision and engineering blockers:**
- **A-1** exact composition placement conflicts with frozen Root-G `3.4 no second parser inside `real_source_service.py`; decide one admitted snapshot-binding read or separate composition point before REAL output claim.
- **A-5** stable `TEMPORAL_AUTHORITY_*` reason-code namespace; **A-6** new composition module path/object identifier vs historic Root-G no-delta rules; both require exact disposition.
- **A-7:** FFprobe **global stream index** and ISO-BMFF `trak` **ordinal** are different namespaces; same integer ≠ proven match. Only explicit source-backed correspondence may admit; otherwise **fail-closed refusal**. A-7 refusal-only path can be prepared independently where contract permits.
- **IT-8 / A-11:** remaining provenance issue **does not disappear if A-3 ships**. Three needed source byte SHA, stream ordinal and media timescale facts **already exist in v1/`gate3.refinement`**. The actual problem is the mapping namespace and the fixture preview pipeline not capturing/binding a snapshot. Earlier strict IT-8 implementation left four e2e chains red and was PARKED, not falsely merged.
- **A-12 / IT-6:** measured stream-tail policy still PENDING; a measured duration does not automatically authorize terminal edit extent or `DERIVED_NOT_OBSERVED` upgrade. Audio-capable preview, real nonproduction pilot and production export each require separate scope/permission.
- IT-2 presentation-order VFR fix remains RED and **blocked behind A-3** so it cannot silently retroactively invalidate v1 receipts. IT-3…IT-6 and full Gate-3 REAL composition are **NOT IMPLEMENTED**.

## 6. Best next dependency-safe course of action (do not confuse planning with authority)

**Primary immediate task for new ChatGPT session:** independently assess the merged **A-3 proposal D-1…D-5** with the approved C′/strict-V1 design, pinned v1 tests and actual `source_snapshot.py` code; present a **specific concise recommendation**, including any need to repair D-4 AST safety checks, and ask the Owner for the outstanding schema/contract decision. **Do not state A′ was already approved** or ask to rerun the just-completed readiness analysis. This is a real Gate-3 product prerequisite, not miscellaneous optimization.

**Parallel READY actions after verifying live main:** run distinct source-only / design lanes where exact contract already supports them, such as A-7 **refusal-only** negative tests with no guessed mapping, a carefully bounded A-11 provenance-source/consumer analysis, and (if genuinely on the Gate-0 path to product completion) prepare the exact real-experiment corpus/editor/weight/host authorization bundle. Stop any action that would change a frozen schema/contract without a narrow decision. Need not launch extra children just to occupy slots.

**Once A-3 is accepted and scope frozen:** Superpowers writing-plans → isolated worktree TDD for snapshot v2 + presentation-basis VFR under `src/vip_fvs/source_snapshot.py` and focused tests; preserve v1 creation and v1 historical verification byte-for-byte except already adopted strict nonzero edit-origin refusal. Gate-3 IT-8 still requires a separate A-7/snapshot capture decision. Then resume C′ composition in the dependency order IT-3/4/5/6 with fresh Owner dispositions for A-1/5/6/7/12.

**Later actual product finish line:** Gate-0 authenticated corpus + editor query freeze + blinded human labels + measured local semantic model ⇒ real diagnostic decision; Gate-1 authentic representation acceptance and valid three-arm quality benchmark; Gate-2 measured representative local/archive workload and justified mechanisms; Gate-3 pilot with human editorial evidence, measured temporal authority, non-production render/QC and separately authorized production export/QC.

**Don't confuse major open Gates with generic code coverage:** User explicitly deferred optional optimization/testing polish until actual pipeline product development is nearer completion. Still run essential regression/negative tests for any changed behavior.

## 7. Exact GitHub operations and handoff discipline

1. Use a GitHub-linked authenticated account for `Centaurioun/video-intelligence-pipeline`. Independently fetch ``refs/heads/main`, open PR list, check runs and the frozen backup ref; ensure current SHA reflects any PRs merged since this snapshot. Avoid assuming an assistant's old local checkout reflects remote.
2. Read only task-relevant files and verify old file path/line claims against latest tree. The persistent Google/DeepSeek local Mac worktree is separate from ChatGPT's remote GitHub file interface.
3. For local tasks provide precise English DeepSeek Flash LOW Goal prompts: `GOAL_ID`; scope; governing docs; immutable `BASE_SHA`; exact owned paths and dependencies; Superpowers triggers; RED/GREEN tests; prohibition on model/archive/provider/export; deliver PR URLs, committed SHAs and actual evidence. Independent READY roots parallel; shared writers serial, resource v5 leases.
4. On submitted PR: independently compare actual diff, base/head and commit ancestry, CI check run conclusion, agent-reported full test logs, accepted vs unapproved contract changes and hidden false-green paths; request repairs where blocking; merge in dependency order **only when current Owner instruction/authorization covers that merge**, main protection allows it and the frozen backup remains unchanged. Never silently merge Gate/production promotion.
5. Update `docs/project/01_CURRENT_STATE_AND_HANDOFF.md` and WBS only for verified substantive progress. Prefer succinct newest overlays/pointers; do not rewrite historical rejected decisions or overwrite old handoffs. Main SHA will move when a documentation PR merges — record the accepted execution candidate and latest merge SHA separately.
6. If a local result exists only in DeepSeek's message and you cannot inspect/run it, distinguish **agent-reported/local** versus **independently confirmed GitHub**. A green 3.11/3.14 smoke is not a full Python compatibility proof; strict `xfail` is a visible unmet expectation, not completed implementation.
7. Absolutely never modify the preserved backup. No branch deletions or destructive Git operations without explicit Owner authorization.

## 8. Six-Cycle Iterative Refinement of *this handoff*

This is a documentation-only retrospective quality record; it neither changes Gate authority nor claims a new software-test run.

1. **Current truth:** Independently fetched `main@f5366ef...`, open PRs, frozen backup, latest GitHub jobs, recent merged PR #176–#179 and canonical handoff/WBS; source-backed status outranks the earlier conversation where these PRs had been OPEN.
2. **Gap/conflict review:** Flagged stale earlier `#173 OPEN` and `#176/#177/#178 OPEN` overlays, distinguished Gate 0 synthetic PASS versus real `NOT_RUN`, differentiated local full-suite reports from main smoke, and identified real IT-8 dependency separate from A-3.
3. **Three candidate handoff designs:** A = only append to enormous dated `01` file (hard to scan); B = **single stable START HERE file + small link in `01`** (chosen); C = duplicate four Gate plans/specs into a new mega-authoritative set (unmaintainable and risks changing authority).
4. **Structure:** Designed this self-contained orientation → verified status → four-Gate assessment → Owner decision ledger → READY frontier → operations/continuity sequence, with exact clickable repository pointers rather than reproduced full code.
5. **Adversarial self-check:** No protected media, model, cloud, export, Gate promotion or backup modification authorized; no fabricated xfail success, v2 implementation, real benchmark, model winner or production proof; distinguishes A′ **proposed** from C′/strict V1 **approved direction**.
6. **Completion verification standard:** Read this file back from GitHub at its immutable PR head, confirm link from `01` and path existence, run/check GitHub workflows where applicable, verify resulting main and backup SHA, and report only what those observations prove. Future fresh sessions must re-fetch current state and must not treat this retrospective as an autonomous certification.

---

## 9. Compact opening instruction for the next ChatGPT conversation

"Read this `CHATGPT_CONTINUITY_START_HERE.md` at current GitHub main, follow its bootstrap and verify live repository state. We are continuing the Owner-approved four-Gate Video Intelligence Pipeline toward actual product completion. Focus first on the pending Gate-3 A-3/D-1…D-5 temporal-evidence contract decision and independently READY product work; preserve all authority, source and evidence boundaries. Reply in Turkish and do not ask me to repeat the prior chat."

**This file is the continuity entry point, not a higher-priority policy or permission grant.**
