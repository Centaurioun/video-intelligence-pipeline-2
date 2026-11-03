# VIDEO INTELLIGENCE PIPELINE — ChatGPT new-session handoff (post-H3 contract adoption)

**Authoritative snapshot date:** 2026-10-26, Europe/Istanbul. **Repository:** https://github.com/Centaurioun/video-intelligence-pipeline (private — use authenticated GitHub connection). **Independently verified main at authoring:** `5b3330407fbb4c03fe953fb3d03c5aff11bc4360` (merged PR #225). **A merge of this handoff will change main again; never treat this SHA as the latest without re-fetching.**

**Intended next-session experience:** Speak with the Repository Owner in Turkish, as in the prior chat. Continue the same four-Gate WBS and evidence-based parallel Codex work; do not ask the Owner to recount prior history or approve routine steps repeatedly. This is a navigational and evidentiary handoff, not a new source-execution grant.

> **MOST IMPORTANT STATUS:** The Owner has ALREADY explicitly adopted **H3-C05 v1.0.2** and **H3-A04 Option B v1.0.1** as versioned governing *interpretations*, and PRs #222, #223, #224 and #225 are already MERGED. Their product **source implementations remain unapproved** and both Atlas nodes remain `PLANNED`. Never ask for those exact contract interpretations again or mistakenly mark Gate/Product complete.

## 1. Bootstrap sequence — mandatory in the fresh ChatGPT conversation

1. Fetch live `main`, open PRs, PR/commit CI, source blobs, and the protected backup from GitHub **before** claiming current state. Old Codex/DeepSeek summaries, cached local refs, old WBS overlays and this file are dated.
2. Read the live repository handoff authority in order:
   - `docs/project/00_PROJECT_CHARTER.md` (stable orientation)
   - `docs/project/01_CURRENT_STATE_AND_HANDOFF.md` (chronological living state)
   - `docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md` (condensed interpretation, early historical headings can be stale)
   - `docs/project/STATE_MAINTENANCE_PROTOCOL.md`
   - this document and `docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md`
   - `AGENTS.md`, `.orchestration/remaining-work/atlas/atlas.json`, `atlas/progress.json`, `.orchestration/remaining-work/prompts/index.json`, the exact task Core and its dependency/Owner grant.
3. Independently verify the new adopted C05/A04 Core hashes, Atlas/prompt registry pointers, open historical drafts, current HEAD/CI and Owner backup, then report live state in Turkish.
4. Resume a **dependency-safe rolling frontier**; do not redo completed analyses, historical candidate branches or already adopted versioned Core changes. Give a new Codex prompt only when actual next work is supported by live dependency/authorization evidence (or user explicitly asks).
5. If the Owner next pastes a Codex result, independently verify its PRs, diff, exact SHAs and GitHub checks before integration, update WBS solely for demonstrably finished work.

Direct pointers: [canonical four-Gate WBS](12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md); [living handoff](01_CURRENT_STATE_AND_HANDOFF.md); [state protocol](STATE_MAINTENANCE_PROTOCOL.md); [old continuity snapshot](CHATGPT_CONTINUITY_START_HERE.md); [native Codex thread runbook](../architecture/CODEX_NATIVE_THREAD_OPERATIONS_RUNBOOK.md); [throughput-first design](../architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md); [Superpowers](https://github.com/obra/superpowers).

## 2. Purpose, authority and safety invariants

Product is a **local-first / selectively hybrid performing-arts video-intelligence/editing support pipeline** for ballet, dance, music, and performing-arts archives. Target:

`source/archive → deterministic inventory/provenance → semantic useful-moment search → source-native temporal refinement → measured PTS/frame evidence → human editorial decision → versioned edit plan → render/export → technical+editorial QC`.

Technical hard rules:

- **Source media immutable** unless independently approved source-use policy says otherwise. Filename/provider/vector/UI key is not the canonical source content/revision identity.
- **Semantic/model/provider timestamp = candidate hint only**, never an exact cut. For true temporal decisions use native PTS, timebase, measured frames and fail-closed ambiguity; NEVER compute VFR frame index via seconds × nominal FPS.
- Canonical **assertion evidence classes**: `MEASURED`, `MATCHED`, `VISUALLY_OBSERVED`, `AUDIO_OBSERVED`, `EDITORIAL_INFERENCE`. `NOT_OBSERVED` is a state marker, NOT a sixth evidence class. Synthetic D-2 `attestation_state` is also not assertion proof.
- Exact Owner permission hierarchy: **current explicit Owner instruction > frozen contracts/governing decisions > approved design > implementation plan > task packet > controller ruling > worker choice**. Lower levels never expand higher authorization.
- **NOT AUTHORIZED BY THIS HANDOFF:** real/protected archive enumeration, path stat/read/hash/probe/decode, authentic model download/load/inference, network/provider/cloud, real macOS codesign/build, real media editing/preview/export, production actions, Gate promotion, or unapproved Git destruction.
- Do not `git reset --hard`, `git clean`, delete branches/worktrees, force-push, rewrite history or expire reflogs/prune recovery objects without exact current authorization.
- Protected immutable branch `backup/OWNER-DO-NOT-MODIFY-main-20261024-17edacbe` is at `17edacbe64983ae284f09a8386377200bf538ec3`; independently verified **behind main=0** at handoff bootstrap. Do not update/delete/merge into/rename it.

## 3. Source-verified current milestone ledger

| Work | Independently verified status |
| --- | --- |
| `main` | `5b3330407fbb4c03fe953fb3d03c5aff11bc4360` after PR #225 (snapshot SHA, refresh on entry). |
| **#222 C05 v1.0.2** | **MERGED** as `9aa9d56aebb435ed3e1915bb8e0498f1ffe80019`. New `.orchestration/remaining-work/prompts/H3-C05/v1.0.2/core.md` SHA-256 `2cb46d97623d344504d290e880b3c90c7a608b34fb6f2dbe0b8a4d14b421e466`, `core.json`, Owner decision, synthetic checksum tests. Original v1.0.1 Frozen Core preserved. |
| **#223 A04 Option B v1.0.1** | **MERGED** as `a7bc80b4945357520cb626e88d4826c5ef65772f`. New `.orchestration/remaining-work/prompts/H3-A04/v1.0.1/core.md` SHA-256 `04e13d9659a389d3ee32e8de308aeebb86435c4c68da771745c136fcfdc2df`, `core.json`, Owner decision, synthetic checksum tests. Old v1.0.0 preserved. |
| **#224 registry reconciliation** | **MERGED** as `137077f2301879ca282e86b488b3e0a648adf9f9`. Updated ONLY C05/A04 entries in `atlas.json` and `prompts/index.json`. New cross-registry regression; test-first stale pointer RED `1 failed / 1165 passed / 64 skipped`, then broad Gate-0 dual Python green `1166 passed / 64 skipped` per interpreter; **9/9 checks successful**. |
| **#225 WBS and global handoff** | **MERGED** as `5b3330407fbb4c03fe953fb3d03c5aff11bc4360`. Two supporting CONTRACT adoption checkmarks `[x]`, but **post-adoption implementation readiness remains `[ ]`**, both H3 states `PLANNED`, no Gate completion. **9/9 checks successful**. |
| Open historical drafts | **#214** Batch-007/controller audit; **#215** B05 stacked old candidate; **#216** B04 old candidate with conflicts; **#217** five-lane design. All OPEN DRAFT, none merged. **DO NOT MERGE** without independent current-main reconciliation. |
| Other open PRs | **#182** historical Gate-0 Owner inputs/authorization packet (partially stale after D-1; not genuine submitted inputs). **#169** Dependabot Next.js change in historical frozen reference pack (unrelated). |
| Owner backup | `17edacbe64983ae284f09a8386377200bf538ec3`, unchanged (separate compare verified). |
| CI | Nine check runs on #224 and #225 successful: Gate-0 broad (3.11, 3.14), Gate-0 D1 (3.11, 3.14), Gate-2 report/receipt (3.11, 3.14), synthetic smoke (3.11, 3.14), GitGuardian. Success certifies those **synthetic** scopes only. |

Old reports/overlays calling C05 v1.0.2 or A04 Option B `NOT_ADOPTED` (for example #220 and #221) were correct **at their earlier SHA/date** but are **superseded as current authority by Owner decision + #222/#223**. Retain these records historically, do not erase/rewire provenance. The PR #224/#225 merges similarly supersede previous instructions to "ask Owner to adopt" or "update Atlas pointers".

Actual new task status: in the current Atlas, **H3-C05 = PLANNED** and **H3-A04 = PLANNED**, each `candidate_generation=null`, `overlay_ref=null`; neither has product code authorization simply because the Core version is adopted.

## 4. Latest Owner decision, precisely bounded

The Owner explicitly approved **H3-C05 PR #220 v1.0.2 consumed-contract successor** and **H3-A04 PR #220 Option B primitive-producer interpretation**. **Only** new versioned governing contracts/Cores, matching Atlas/prompt references, synthetic contract tests and independent validation were permitted. This has been fully exercised by #222–#225. No product behavior edit, real signing/media/model/provider run, production export or Gate promotion was included. Do not ask for identical adoption again; DO require separate scoped source-write authority for any future genuine C05/A04 implementation.

### H3-C05 — Adopted read-only multi-source query behavior

- Current main already implements `index-local`, `query-local`, `query-multi`, source snapshot and authorization/refusal foundations. Old B04/B05 candidate source must **not** be transplanted wholesale.
- `query-multi`: read-only query of existing generation via `SemanticIndexEngine.build_generation_spec` and `.query` inside `retrieve_multi_source` with persisted multi-source manifest. **Not** `retrieval_adapter.retrieve`, because that re-indexes/opens source.
- Match each hit to exactly one source-manifest **occurrence** using exact locator spelling + source digest (do not conflate two locations with identical bytes). Preserve revision/occurrence, rank/finite score, semantic-space/generation identity, output provenance and deterministic ordering; refuse missing/mismatched/ambiguous proof.
- Evidence remains `MATCHED`, `binding_eligible=False`; source-native PTS/timebase remain locators, not cut points. No model-timestamp upgrade or VFR nominal-FPS inference.
- Frozen-to-current consumed producer drift was resolved at **contract-level**: old retrieval adapter blob `348bf9979e5c2e0a77e338e7cb5ff84910db2ad6` → `0f0268d83da4ff6c06c45ad54d85070071d6e155`; old coordinator blob `a4ed02c92cb03aa4e56ab600e34f4f1cb4fc416e` → `1696b31afc58d83269389f025759b2ef7dba7670`. `query_local_index` is separate/additive, not required for this query-only path.
- No implied live source permission revalidation, generation-to-corpus-snapshot cryptographic attestation, source opening, model call, or re-indexing. The newly adopted Core does NOT make C05 READY; fresh C04/B05 dependencies/receipts/contract ownership/leases plus actual source grant required.

### H3-A04 — Adopted Option B primitive producer

- One and only one signer observation `_run_codesign_entitlements(application)` returns successful `subprocess.CompletedProcess[bytes]`. It is a fixed **observation subleaf**, **not** a primitive-return producer.
- The boundary `measure_and_handoff_n4a` validates return code and exact signer stdout, uses accepted S1 renderer bytes, constructs **one** five-field `N4ABoundaryPrimitive` and passes the same object (`is` identity) to registration, Task-4, Task-5, `N4ASealHandoff.measured_primitive` and `N4AProductionResult.primitive`.
- Maintain `seal_capability is handoff.capability`, `transient_application is handoff.source_application`, Task-3 descriptor-anchored write-free lifecycle, exact digest/octet attribution, proper refusal/cleanup, no retry, no second constructor.
- Original frozen wording that "leaf remains sole primitive producer" is clarified as **single boundary measurement-and-primitive-production flow**, preserving old v1.0.0 history. No live `codesign` or source write permitted without separate exact grant.

## 5. Four-Gate WBS — concrete remaining product work

**Master tree:** `docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md`. Its child checkmarks are bounded; contract-only and synthetic items do not close genuine parent requirements.

### Gate 0 — Diagnostic visual retrieval

- Synthetic source/manifest/CI/config/reviewer software foundations exist (#125, #173, #178, #187–#190, #194, #205–#212). **G0.1.4 experiment readiness remains [ ]**; macOS Stage-B and genuine model/host/source rights prerequisites unresolved.
- **G0.1.5 corpus [ ]:** 60–120 min proposed, ≥3 sessions, ≥6 revisions, family coverage; no genuinely authorized immutable source root/corpus freeze or source hashes/probes.
- **G0.2.2 [ ]:** 24 positive editor-authored queries (6 each across appearance/action/interaction/scene-composition-camera movement), 8 plausible absent and 8 separate development queries, versions and blinding.
- **G0.2.3 [ ]:** two *real* independent human reviewers, interval-linked gold, uncertainty and adjudication. Software P-05 envelopes, real config digest binding, reviewer membership and gold rational identity tests are preparation only.
- **D-2 30 genuine Owner inputs:** last documented census **0 VERIFIED, 7 PENDING, 21 BLOCKED, 2 NOT_OBSERVED**. PR #211 repaired untrusted text `OWNER_SIGNED` marking rows VERIFIED; all external attestation remains unknown. No future packet may claim proof from self-declared text.
- **D-3 genuine execution NOT_AUTHORIZED**, `authorized_local_execution_gate_open() -> False`, real diagnostic **NOT_RUN**. Frozen config/sandbox model binding representation gaps need separate governing decision.
- G0.3 real freeze/baseline/model/repeatability and G0.4 decision stay [ ]. Provisional thresholds Hit@10 ≥20/24, lift ≥5/24, each family ≥3/6; never claim PASS without admissible measured source evidence.

### Gate 1 — Representation/model choice

- G1.1.4 source-only V1 baseline/provenance reconciliation is [x] following #193/#196 merges, but `03_V1_BASELINE_SNAPSHOT.md:154` authentic runtime completion applicability remains **BLOCKED**.
- V2 768-D and SO400M 1152-D profiles still synthetic placeholder identities, not authentic V2 runtime. Tokenizer/BOS/EOS/padding/pooling and model license/assets/weights need genuine authority and observations.
- **Gate B NO_GO_BLOCKED**; native Task-4/5 exception **NOT_ADOPTED / NOT_AUTHORIZED_FOR_EXECUTION**. Synthetic amendments do not grant model loading. G1.2.4, real G1.3 benchmarks and G1.4 model selection/acceptance remain unfinished.

### Gate 2 — Reliability/scale

- Synthetic W0–W10 and receipts/runs exist; #197 corrected G-12 report-value contradictions while keeping source carriers immutable. **G2.1.3 real workload [ ]**: owner-observed archive counts, lengths, codec and storage variety, operator usage and representative workload not available.
- G2.2.2 real V1 workload, G2.2.3 selected model, G2.3 measured-fix mechanisms, G2.4 acceptance remain open.
- Do not deploy Redis/ANN/cache/queues/checkpoint scale machinery absent observed deficiency, and do not call synthetic host loads production workload measurement.

### Gate 3 — Editing/QC/export

- Synthetic source snapshot, no-follow identity, native PTS/timebase refinement, human-decision/edit-plan schema, safe FFmpeg fixture previews and QC foundations have scoped [x] records.
- **A-7 positive `tkhd.track_ID` mapping = PENDING/UNADOPTED**, despite decision proposal #203 + design #206; refusal-only multi-trak protection #183 active, `IT-8 PARKED_BLOCKED`.
- **IT-6/G-4 terminal-tail admission = PENDING** (#200 proposal), `DC-BIND` strict xfail remains; `A-12` is consumption-time re-verification, NOT tail admission.
- Real human V1 pilot G3.2, authorized preview/QC G3.3, production export G3.4 and final G3.5 acceptance all open. Source media and production actions require distinct explicit approvals.
- H3-A04 belongs to Gate-0 Stage-B evidence orchestration, not to Gate-3's A-7 stream namespace question.

## 6. Prior runs/PRs — avoid repeating completed work

- #194 repaired broad Gate-0 Linux CI/fixture failures; old failed runs remain historical. The broad test suite is synthetic; prior CI counts are not authentic source observations.
- #197 corrected Gate-2 report-carrier mismatch G-12; do not quote old report's superseded numbers as measurements.
- #193/#196 source-only Gate-1 V1 reconciliation were merged; old "draft open" language is historical.
- #203/#206 documented Gate-3 positional `tkhd.track_ID` policy P2, owner B-1…B-11 unresolved; no stream-mapping code implemented.
- #208 config-digest binding; #209 intake/gold grouping; #211 attestation refusal; #212 reviewer query/window membership all merged. Human catalog still absent.
- #214–#217 historical draft evidence/candidate branches remain open. Historical B04 candidate `73959e08ce962d9d21d294b29a703afc69e54009`, B05 candidate `2210b8de049dff989767b6375f8415184fdc1dd2` were separately tested but predate stronger canonical current-main product behavior. Do not merge these wholesale or repeat the conflict analyses.
- A02 candidate `49b62f27fa70f499fac3cab3c3c9dded1054bd2a` had add/add differences; independent no-import analysis preserves better A03 main source. C04 candidate `5d482a1016b97d663c57ad31d8bac21c19c8c799` is **NOT** an ancestor of main; historical false controller claim corrected append-only with #218. Never rewrite its original receipt.
- #218: 2 SSH-signed four-lane evidence files delivered and merged; #220: four-lane C05/A04 proposed interpretations, adversarial review and receipts merged; #221: previous, now superseded status handoff. #222–#225 newly enact the explicitly accepted contract-only interpretation.
- A 1Password SSH signer `failed to fill whole buffer`/empty agent issue occurred previously and was resolved with Owner interactive unlock/approval; signed #218 delivery subsequently worked. Never disable signing or invent another signing identity as a workaround.
- Primary local checkout was **reportedly** dirty with ~407 entries at an earlier checkpoint; **not reverified in this GitHub-only session**. Never reset/clean/stash/overwrite it. Local Batch-008 state may be uncommitted/unreconciled; don't assume newest filename equals authority.

## 7. Orchestration and collaboration preferences

- The Owner now works in **Codex** (previously DeepSeek), wants 3–5 substantive **genuinely independent** tasks in parallel, integrated by one controller with exclusive writer paths; does NOT want a single small prompt each turn or repetitive routine approval questions. Do not manufacture extra agents to occupy slots.
- Follow `AGENTS.md`, `docs/architecture/CODEX_NATIVE_THREAD_OPERATIONS_RUNBOOK.md`, `THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`, and `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`. Native Codex fresh `create_thread` with verified thread/project/worktree identity, READ_ONLY preflight, isolated branches/worktrees, leases and stale-base checks. Ambiguous `clientThreadId` is NOT an active worker ID; do not blindly retry.
- Use rolling BUILD / VERIFY / REPAIR frontiers; start independent READY work concurrently, verify immutable candidate and actual CI before successors. One controlled integration path for shared contracts and WBS. **Current Atlas H3-C05/A04 PLANNED**, regardless of accepted Core.
- `.orchestration/remaining-work/atlas/progress.json` is frozen at **2026-10-21**, with weighted 67% BUILD/64% VERIFY **historical H3 progress**, not current four-Gate product completion. `batch-006` READY roster was stale, `batch-007` deliberately empty; do not replay either blindly.
- A GitHub-only ChatGPT environment cannot claim to create or observe native Codex threads on the Owner's Mac. If no local native tool is connected, give one strong controller prompt that delegates actual native thread creation **to Codex**, but only when a justified READY frontier is established.
- For any PR: independently verify base/head/diff, CI check outcomes, source/contract fingerprints, historical frozen refs, adversarial review, source authority, backup state; merge only in authorized scope. Update living handoff and WBS child [x] items based on actual evidence, not enthusiasm.

## 8. Immediate next safe frontier (not an automatic source grant)

Start after a fresh live GitHub/Atlas/Owner-authority verification, not solely from this snapshot:

1. **C05 post-adoption READ_ONLY verification:** validate the new v1.0.2 MD/JSON/Atlas/index closure, current C04/B05 producer dependencies on main, actual existing multi-source read-only tests and semantic behavior; classify SATISFIED vs MISSING_PROVEN vs CONTRACT_BLOCKED. Do not change product source absent separate specific grant.
2. **A04 post-adoption READ_ONLY verification:** inspect current A03/Task-3 dependency, one-shot observation/helper return versus boundary primitive creation, identity `is` propagation using only mock/synthetic tests; prepare minimal scoped RED test packet if missing. Do not perform real codesign or amend source without grant.
3. **Gate-0 D-2 or Gate-2 W1 genuine input readiness:** separate non-protected, text-only Owner rights/query/reviewer/model/host and archive/operator workload inventory, if actually provided. Do not invent authentic attestations or touch protected archive.
4. **Single controller/WBS audit:** reconcile date-stale Atlas/progress and open draft PRs, task dependencies, source writer ownership, lease and exact current main. Do not flip parent WBS status automatically.
5. **Optional independent Gate-3 design track:** A-7 positive mapping and IT-6 terminal-tail decisions remain unadopted; request exact governing approval only when those designs are genuinely being advanced.

There is **NO blanket source-code BUILD authorization for C05 or A04**. If only two independently eligible read-only jobs exist, run two—not five filler tasks. After actual authorized TDD RED→GREEN/independent review, merge in dependency-safe order and update WBS.

## 9. Superpowers brainstorming / Six-Cycle documentation design record

This handoff is NOT a new reusable Superpowers skill, software feature, or architecture amendment. The six cycles below are a quality/reconciliation procedure for the text only:

1. **Clarify purpose & brainstorm alternatives:** The user asks for complete new-ChatGPT continuity, GitHub link, no repeating questions. Evaluated (A) append another massive overlay to `01`, (B) create an immutable versioned handoff + small entry-point pointers (**chosen**), and (C) rewrite frozen/legacy docs wholesale (**rejected** as historical loss).
2. **Verify repository facts:** Read charter, living handoff, orchestration design, maintenance protocol, WBS, Atlas/prompt index/AGENTS and latest PR state directly from GitHub. Identified surprising current truth: #222–#225 already merged even though prior conversation had #222/#223 CI in progress.
3. **Resolve provenance/status conflicts:** Distinguish explicit contract Owner adoption from unchanged product implementation; old `NOT_ADOPTED` overlays are historically correct but superseded. Distinguish old PR-candidate VERIFIED from current main and stale `progress.json` from actual WBS.
4. **Design next dependency-safe path:** Keep existing four Gate WBS, report honest unresolved real corpus/model/human/Gate acceptance, allow independent safe preparations while refusing ungranted source changes and avoiding redundant B04/B05 merges.
5. **Adversarial self-review:** Check every major claim against SHA/PR/CI and ask whether it silently invents a model run, media source, WBS [x], RED test, Owner credential or exact frame edit. None of these can be promoted by a documentation artifact.
6. **Verification-before-completion:** Read back this file and its entrypoint pointers at immutable branch head, confirm paths, PR diff only intended docs and final GitHub CI/checks; re-fetch current main and backup. Report any unobserved CI honestly rather than claim it passed.

**Do not claim an independent agent review or runtime Superpowers skill dispatch was performed merely because this ledger exists.** These are repository-informed method steps and an adversarial self-check.

## 10. Expected first answer of the new ChatGPT instance

Re-fetch repository before answering. Briefly report actual main SHA, merged #222–#225 adoption, H3-C05/A04 PLANNED, open historical draft PRs, D-3 NOT_AUTHORIZED and other Gate blockers. Then present the genuinely READY, dependency-safe next parallel work based on live evidence; do not immediately produce another redundant Codex prompt or re-ask for adopted decisions. If the Owner pastes a Codex report, review it against the repository and continue the PR/CI/WBS integration loop.

The Owner should be able to continue this collaboration **as if the chat window never changed**. This file provides continuity and pointers, not permission expansion.
