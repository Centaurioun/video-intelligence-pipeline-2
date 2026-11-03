# VIDEO INTELLIGENCE PIPELINE — FRESH CHAT CONTINUITY HANDOFF
**Snapshot date:** 2026-10-08 (Europe/Istanbul)  
**Document status:** handoff / navigation; **NOT** a new owner authorization, Gate promotion, deletion permit, or replacement for verified Git state.  
**Repository:** https://github.com/Centaurioun/video-intelligence-pipeline  
**Purpose:** allow a new ChatGPT Project conversation to continue immediately after canonical product adoption and branch-preservation certification, without replaying long chat logs.

> **Start here.** The owner's most recent objective is: preserve the project history and design rationale; simplify hundreds of GitHub branches safely; keep canonical product code on protected `main`; bring stale Atlas/controller status into alignment later through an independently verified, separate operation. Product integration and branch preservation are complete within the stated bounds; **branch deletion has NOT begun**. The immediate next choice is independent examination of the 46 exact low-risk deletion candidates and a carefully authorized bounded cleanup plan, not deleting arbitrary prefixes.

## 0. Required fresh-session procedure — do this BEFORE recommendations or writes

1. Fresh-fetch current `main` and PR/branch state. The last independently observed `main` before preparation of this handoff was **`32bdc44f93d5f48dc233e884a5f7ed653e14a7a1`**, merge commit of [PR #60](https://github.com/Centaurioun/video-intelligence-pipeline/pull/60). Do **not** freeze that SHA as permanently current.
2. Read these current-on-`main` files in order: `docs/project/00_PROJECT_CHARTER.md`; `docs/project/01_CURRENT_STATE_AND_HANDOFF.md`; `docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md`; `docs/project/STATE_MAINTENANCE_PROTOCOL.md`; THIS handoff; `docs/project/07_2026-10-08_CANONICAL_ADOPTION_AND_DECISION_RECOVERY.md`; `docs/project/08_2026-10-08_DECISION_HISTORY_INDEX.md`; `docs/audits/2026-10-08-branch-preservation-recovery-certification.md` and its JSON companion.
3. Current evidence comes from **remote Git SHA/tree, branch refs, governing contracts, PRs and source-authority ledgers**, not previous chat/Codex declarations. Project uploads are orientation only; when they conflict, verified remote Git wins.
4. The owner speaks Turkish and wants direct continuity, clear `VERIFIED` / `PENDING` / `BLOCKED` / `NOT_OBSERVED` labels, minimal owner relay, technically defensible choices, and copy-ready English Codex Goal/STEER prompts when Codex must handle local operations. Do not make them repeat information already in this handoff.
5. **No automatic deletion, source-code broadening, production use or Gate promotion.** User approval to preserve and plan a cleanup is not a blanket approval to delete names not explicitly listed and revalidated.

## 1. What the project is and why it exists

Build a **local-first, selectively hybrid** video-intelligence and editorial-assistance pipeline for a large ballet, dance, music and performing-arts video archive (originally discussed as hundreds of hours / a large multi-TB archive). Intended long-term workflow:

source/archive → deterministic inventory/provenance → useful-moment semantic retrieval → source-native temporal refinement → measured PTS/frame evidence → **human editorial decision** → versioned edit plan → render/export → technical/editorial QC.

The four **evidence/decision Gates**:
- **Gate 0 — Diagnostic retrieval:** bounded local visual retrieval versus a transparent metadata baseline. The baseline is a diagnostic floor, not a complete human editor workflow.
- **Gate 1 — Representation/capability:** compare eligible modalities, representations, providers/models under frozen benchmarking protocols; no benchmark winner can be inferred from a current candidate implementation.
- **Gate 2 — Reliability/scale:** workload/failure-based justification of queues, persistence, indexing, caching, recovery, restart and scaling; local/synthetic test success does not establish archive-scale M4.
- **Gate 3 — Editing/QC:** deterministic source-native refinement, attributable edit decisions, edit plans, non-production render, QC receipts; no automatic production/real-media certification.

Scientific Gates are **not** mandatory permanent four separate Git worktrees; dependency-safe implementation may overlap while evidence-dependent Gate promotion remains hard-gated. Never silently expand the authorized finish line.

**Non-negotiable rules:**
- Source media immutable absent explicit separate current owner authority; canonical media identity is content/provenance, not filename/Drive/provider/vector ID.
- Assertion evidence classes exactly `MEASURED`, `MATCHED`, `VISUALLY_OBSERVED`, `AUDIO_OBSERVED`, `EDITORIAL_INFERENCE`. `NOT_OBSERVED` is a state marker, not an evidence class. Never inflate evidence strength.
- Semantic/model/provider timestamps are **candidate locators only**. Exact edit intervals require source-native **integer PTS/timebase/frame** evidence; never derive VFR frame numbers by multiplying seconds × nominal FPS.
- Machine refinement ≠ human editorial selection; versioned edit plans and QC require their own explicit evidence.
- Real/protected archive work, provider/cloud network requests, model downloads, production renders/exports, destructive cleanup and Gate promotion require separate explicit authorization.

## 2. Current canonical product milestone — COMPLETE ONLY FOR AUTHORIZED LOCAL-FIRST SCOPE

**Portfolio Goal:** Existing approximately 18 h 34 min Remaining Work Portfolio Goal reached final **G03 VERIFIED** for the then-authorized local-first implementation-and-verification finish line, NOT whole-product/production maturity. Controller terminal authority:
- `controller/remaining-work/authoritative@a81104f47667a7f9ee1f47a86e1bfe711bfa2dd4`
- `controller/area/G@988b8790cc45ad1c1093f0d1ebbae15ab0716f38`
- Frozen **G02 candidate `e956722a0fc2109eb4651ce728e919e691162511`**, tree `2996b4cca1164ba7b145145dbfe0b908a1010f82`.
- G01 convergence matrix (Gen023) digest `32506cc4bc08ec0c73678f7cf335359c4061760e9e44ec0d277fe56ccb7720e3`; six accepted roots H3-A07, H3-B05, H3-C05, H3-D05, H3-E05, H3-F03.
- G03 eight independent review/verification lanes, no blocking current-scope findings; the frozen candidate recorded **1,290 passing tests**: VIP-FVS 594, Gate 0 477, Gate 1 120, Gate 2 99. These are recorded candidate test receipts, NOT a new GitHub-hosted CI execution after merge.
- G02 source-authority exact check PASS, zero unauthorized paths, using fetched admin root. Full workspace verifier was separately red on inherited checkout, reference-pack/prototype environment and stale local source-auth issues; never present full workspace verification as PASS.
- **Nonblocking:** C05 rounded `timestamp_human` is display-only, NOT an exact editor boundary. Real audio/visual QC and broader modality/provider/archive-scale outcomes are `NOT_OBSERVED`.

**Canonical adoption**:
| PR | Purpose | Outcome / immutable merge |
|---|---|---|
| [#57](https://github.com/Centaurioun/video-intelligence-pipeline/pull/57) | 17-commit, 97-file verified local-first product integration; 33 `src`, 31 tests, 12 schemas, 2 scripts, 19 orchestration/evidence paths | MERGED to protected main at `e752c2fc45b533a0c679a32459225d37165a7722`; candidate vs adopted product tree had **zero changed paths** |
| [#58](https://github.com/Centaurioun/video-intelligence-pipeline/pull/58) | Branch inventory and gated preservation plan; NOT a Git-object archive | MERGED at `f4e40c2cba18f85e6f283113e8d7d48c4205dff8` |
| [#59](https://github.com/Centaurioun/video-intelligence-pipeline/pull/59) | Project current-state summary, next-plan correction and accepted/rejected decision index | MERGED at `8e733bfeee7d725a3fc304b9f5311d574a1bc012` |
| [#60](https://github.com/Centaurioun/video-intelligence-pipeline/pull/60) | Frozen branch preservation/recovery certification (two docs/audits files) | **MERGED** at `32bdc44f93d5f48dc233e884a5f7ed653e14a7a1`. The committed JSON represents an **earlier 677-ref snapshot**; the live v3 archive ledger represents **678 pre-update refs**. Do not confuse them. |

No product new-feature Goal should be launched merely because older documents mention batches still to dispatch. Historical batch-002 instructions are superseded, not current READY work.

## 3. IMPORTANT: terminal control plane and `main` Atlas are **not yet synchronized**

At last independent read:
- Terminal Portfolio `.orchestration/remaining-work/atlas/atlas.json` on `controller/remaining-work/authoritative`: **33/33 H3 nodes VERIFIED** for the local-first authorized denominator.
- `main`'s `.orchestration/remaining-work/atlas/atlas.json`: **18 VERIFIED, 3 READY, 11 PLANNED, 1 VERIFY_READY** (33 H3 nodes). `main`'s `atlas/progress.json` shows an old 63 build / 60 verified. Even terminal Portfolio `progress.json` is stale at 99/97 relative to terminal Atlas.
- Comparison identified **15 H3 state transitions**, around **67 direct Atlas-referenced prompt/evidence paths absent from main**, and **478 paths present only on the Portfolio tree** at that snapshot (many are orchestration, receipts, overlays). Do not blindly copy only `atlas.json` or set summary progress to 100.
- Completion counters refer solely to a specific bounded H3 implementation/verification finish line. Do NOT upgrade scientific Gate maturity, real-media outcome, or production-readiness percentages.
- **PENDING separate task:** propose minimal content/pointer migration plus dependent evidence/contract/authority refs on an isolated integration branch; respect exclusive writer ownership, review, fresh current `main`; run `scripts/verify-remaining-work-atlas.py --require-prompt-metadata` and exact provenance checks. Preserve separate old controller/admin branches until post-migration acceptance. Ask owner approval before any different architecture/contract or scope change.

The new chat may first prioritize 46-branch cleanup *or* this Atlas reconciliation, depending on user direction; both are safe to analyze without touching media. Avoid making a new big superfluous Portfolio Goal.

## 4. Branch explosion, why it matters, and what has actually been preserved

The owner wants GitHub branches drastically simplified **without losing reasons for accepted/rejected alternatives**, code/experiment designs, run audits, and correct authority. Hundreds of isolated Codex branches arose from parallel review, implementation, verification and repair. A prefix like `review/` or `docs/` alone is never proof that a branch may be deleted.

### Historical version 1

- Permanent historic tag: `refs/tags/archive/history/branch-preservation-v1`.
- Recovery ledger on `main`: `.orchestration/maintenance/branch-hygiene-cleanup-v1/preservation-recovery.json`.
- Ledger contains **183** legacy heads; later Codex report found **180 reachable from its original v1 root**, three explicitly uncovered by v1 and covered by v3. Historical record must not be rewritten or interpreted as all-current coverage.
- Prior v2 branch `archive/history/branch-preservation-v2-20261008` was a **snapshot only** (its old head `5ba5fe1f270fbfa632be7b80b2a4fe94c663059a`), not complete verified reachability. Retain as history.

### Current preservation version 3 — remote GitHub facts independently checked

- **Archive branch:** `refs/heads/archive/history/branch-preservation-v3-20261008`.
- **Last verified archive HEAD:** `0dce7a2a4c5b429fac94ebba0088b85e99c6296c`. It is an intentionally synthetic multi-parent **REACHABILITY_ONLY / NO_SEMANTIC_MERGE** commit; not product adoption. Its exact parent list includes **669** commit SHA parents.
- **Archive ledger inside that branch:** `branch-recovery-ledger.json`, **678** branch name → HEAD/tree rows from the pre-final-update snapshot. Its current archive commit references its preceding tip and cannot literally include its own future final SHA in the committed ledger; its live ref is the self-root.
- Just before PR #60 merged, independently observed **678 remote branches / 669 distinct HEAD commits**, zero mismatches between the 678 live ref names and the archive ledger, and zero HEADs outside the archive root/direct-parent set at that instant.
- **Important post-merge nuance:** PR #60 later advanced `main` to `32bdc44f…`; this new main merge commit is **not** itself a parent of the older v3 archive root, as expected chronologically, but **main is a protected durable ref** and both its merge parents are historical. Therefore do not claim the old archive root directly contains *every newly created future* commit. A new handoff branch/PR also changes counts. Refresh and extend/retire preservation evidence as required before any future mass deletion.

**Current candidate certification on `main`:** 
- `docs/audits/2026-10-08-branch-preservation-recovery-certification.json` — machine-readable frozen **677-ref** snapshot with HEAD/tree, PR/worktree/recovery evidence.
- `docs/audits/2026-10-08-branch-preservation-recovery-certification.md` — human-readable status.
- The later v3 archive ledger contains **678** pre-final-update entries. The *local* post-PR #60 supplement is a still-later private snapshot; do not claim these three snapshots are identical.
- On independent recheck just before this handoff, all **46** frozen `PRESERVED_ELIGIBLE_FOR_LATER_DELETION` entries still matched the corresponding live remote branch HEAD, frozen tree in the v3 ledger, archive and main reachability flags; no active open-PR-head or registered exact-HEAD worktree dependency was reported for these 46. **This makes them candidates for explicit next approval, NOT deleted and NOT a blanket authorization.**

Frozen classification summary (PR #60 committed manifest):
| Class | Count |
|---|---:|
| `RETAIN_ACTIVE_OR_AUTHORITY` | 577 |
| `RETAIN_OPEN_PR` | 3 in frozen 677-ref manifest; 4 in 678-ref post-PR snapshot (including #60) |
| `RETAIN_UNPRESERVED_OR_UNVERIFIED` | 0 (remote snapshot only; subject to new ref checks) |
| `PRESERVED_ELIGIBLE_FOR_LATER_DELETION` | **46** |
| `REQUIRES_OWNER_REVIEW` | **51** |

Open PRs **after PR #60 merge**, last independently fetched: [#56](https://github.com/Centaurioun/video-intelligence-pipeline/pull/56) event-driven controller protocol (DRAFT); [#14](https://github.com/Centaurioun/video-intelligence-pipeline/pull/14) historical throughput policy (DRAFT); [#1](https://github.com/Centaurioun/video-intelligence-pipeline/pull/1) Dependabot. Treat each as an active dependency until closed/merged through a separate decision.

### Bundles and local worktrees — **Codex-reported**, not remotely rehashed here

- Post-PR #60 private **remote-history bundle** path from Codex handoff: `/Users/yusuf/.codex/branch-preservation-remote-20261008.ywUMnq/post-pr60-all-refs.bundle`; **31,493,670 bytes**, SHA256 `e85fe3f2164aa49c09936bc8aec2402afc23202960b3f6c43dfe9ff091526a9f`. Reported `git bundle verify` and fresh restore PASS.
- Post-PR #60 **local-ref bundle**: `/Users/yusuf/.codex/branch-preservation-remote-20261008.ywUMnq/local-all-refs-post-pr60.bundle`; **33,244,462 bytes**, SHA256 `127915ecc1061a637f7c3aa65ad6461afcf018b983547594b128b6301f9e60b5`; reported fresh restore of **1,546 local branch refs**, including approximately **950** locally named branches not remotely present (frozen earlier report says 951; different snapshot).
- Private `/Users/yusuf/.codex/branch-preservation-remote-20261008.ywUMnq/local-state-audit.json` and `post-pr60-current-inventory.json` may be available on the user's Mac to Codex; ChatGPT GitHub connector cannot directly read or rehash these local artifacts. A new Codex task must verify the current files/exact digests anew before claiming local recovery.
- Reported registered local worktrees ≈ **1,524**; the earlier PR #60 frozen report said **140 dirty / 1,343 clean / 41 unavailable**, later user-reported current audit **139 dirty / 1,344 clean / 41 unavailable**. Counts are snapshot-dependent, not proof of cleanup.
- Bundles protect committed Git objects and ref tips, **NOT** uncommitted tracked modifications, untracked files, ignored caches or secrets. There are dirty local `main` and historical integration worktrees; **do not** checkout/reset/clean/remove them. Preserve their bytes separately and only with explicit later authority.

### Decision history — NOT all reconciled

- Canonical accepted/rejected rationales are indexed in `docs/project/08_2026-10-08_DECISION_HISTORY_INDEX.md` and `docs/superpowers/specs/2026-09-23-execution-portfolio-rejected-alternatives.md` (reasons and reconsideration conditions).
- The certification manifest has **5,318 branch-divergent documentation/evidence paths**, classified **UNRESOLVED for item-level acceptance**; archiving history does NOT make their proposals current governance. Examples: event-driven orchestration PR #56; early handoff `handoff/chatgpt-continuation-20260925-v2`; E03 lineage designs.
- Remaining 577 `RETAIN_ACTIVE_OR_AUTHORITY` and 51 `REQUIRES_OWNER_REVIEW` are conservative classifications, not an order to permanently keep hundreds of branches. Future reduction needs better dependency and local worktree triage, item-level historical decision index, and explicit owner-approved further batches.

## 5. GitHub protection and authority rules

- Active ruleset: [`protect-main-canonical`](https://github.com/Centaurioun/video-intelligence-pipeline/rules/23927496), applies to `refs/heads/main`: **deletion prohibited**, **non-fast-forward prohibited**, **pull request required**, with **merge-commit** as allowed merge method. No protection relaxation is needed for non-main branch retirement.
- The ruleset reported zero mandatory approving reviews and requires review-thread resolution; GitHub mergeability is **not** equivalent to an independent code review.
- Source-authentication source-of-truth: `execution/execution-portfolio-20260924-v1/bootstrap@d766def9d22978328e8767ce7cc769956f41df15`. Keep this exact admin trust-root branch; historically-authorized presence ≠ permission for current source writes. Do not edit verifier rules to manufacture PASS.
- Retain current controller branches, trust-root, open PR heads, archive v1/v2/v3, branch being worked on, active worktree/ref dependencies, and any non-verified history.
- **Disallowed absent explicit separate owner authorization:** hard reset, `git clean`, force push, reflog expiry, object prune, branch/worktree destruction and PR merges beyond approved scope. Deleting an old remote branch is destructive maintenance: require an approved exact-name/SHA batch, fresh check, preserved reachable backup and post-delete recovery checks.
- This handoff is **not** that deletion approval.

## 6. NEXT TASK — branch hygiene (what the new ChatGPT should do)

**Immediate recommendation:** Now that PR #60 has merged and the v3 Git ancestry evidence is strong, independently review the **46** exact candidates in the committed certification JSON, compare against fresh `ls-remote` / GitHub branch refs and current PR/worktrees, and prepare a **bounded exact 46-entry deletion manifest** with rationale and exclusions. If all evidence remains valid, ask the owner to explicitly approve that precise deletion manifest and send ONE narrowly scoped Codex Goal to perform the first batch safely.

**Acceptance gate for a future deletion Goal:**
1. Frozen candidate list: exact branch name, HEAD SHA, tree SHA, covering `main` or v3 archival Git ref, PR state, absent active writer/worktree dependency, backup restore path.
2. New fresh query of all remote refs; any missing/drifted branch → `SKIP`, never overwrite.
3. Verify v3 archive ref still resolves at expected SHA and remote backup/fresh restore remains usable. Protect older v1/v2 refs; verify new/changed refs separately.
4. Audit dirty/untracked local worktrees as a separate task; never infer that a remote SHA bundle preserved working-directory bytes.
5. Owner authorizes **specific 46 branch names** (or a smaller numbered subset) and deletion timing, explicitly distinguishing remote-only branch deletion from local worktree/branch pruning.
6. Bounded small remote-delete batches with exact expected-SHA checks where supported; fail closed on races. After each batch: fetch branch list, check that only authorized names disappeared, check permanent archive and `main` still resolve, attempt representative restore and issue durable receipt.
7. **Never** delete `main`, any archive ref, admin trust-root, active controllers or current PR heads. No force-push, silent branch renames, local `git clean` or worktree removal.

**After the first 46**: develop a new conservative classification of the large remaining 577 + 51 based on active owner/worktree/unique-document evidence. The owner's desire to reduce hundreds of branches is real, but that ambition is NOT authority to delete while dependencies remain unverified.

**Parallel or subsequent separate non-destructive task:** terminal Atlas/control-plane reconciliation (`3 above`), independently verify 15 H3 status transitions and missing provenance carriers, and use a dedicated document/code PR rather than bulk-merging administrator/controller branches. Avoid fabricating new work to occupy agents.

## 7. Six-Cycle Iterative Refinement — handoff review rubric and outcome

This handoff is a **documentation/continuity artifact**, not a new skill, code implementation, architecture approval or real-media benchmark. Apply Superpowers as triggered. The request was explicit enough for a bounded handoff: choosing a GitHub main-linked self-contained document is preferable to chat-only memory or an isolated branch that fresh sessions cannot reliably find. Do not reinterpret this as user approval for future branch deletion.

| Cycle | Critical review question | Document safeguard |
|---|---|---|
| **1 — Intent and latest factual truth** | Does the owner want *continuity*, not a new Goal? Did PR #60 merge after the older report? | Clearly states new-chat goal, SHA-sensitive current-state discovery and PR #60 MERGED. |
| **2 — Cross-document and snapshot consistency** | Does old `01`/`02` still say batches READY? Are 677/678/669 and the post-merge main HEAD conflated? | Marks historical notes superseded and distinguishes frozen manifest, live ledger and newer main SHA. |
| **3 — Authority and technical contract integrity** | Does `VERIFIED` mistakenly imply production/Gate promotion, editable source/media, or inferred VFR frames? | Exact PTS/evidence/Gate limits and admin/current-write separation stated. |
| **4 — Recovery, worktrees and destructive-risk falsification** | Is SHA-in-JSON confused with object retention? Are dirty files in bundles? Are 46 candidates automatically authorized? | Names v3 direct-parent root, limits of bundles, explicit owner-reviewed deletion gate. |
| **5 — Early Superpowers skill routing and rejected approaches** | Does new session invent a project Gate skill, fake code execution, or use old dispatch/parallel quota? | Trigger-based skill map below; documentation over new skill; old rejected alternatives indexed. |
| **6 — Fresh-session usability and verification** | Can another ChatGPT instance orient itself and identify exact next action from one GitHub URL, without restating prior chat? | `0` bootstrap, ``6–9` owner interaction, links, proof labels, and next-step template. |

**Scope of six-cycle review:** reasoned editorial/cross-reference review, NOT a claim that six independently executed agents or external tests examined this Markdown. If later modified, rerun the six checks and verify GitHub file contents after merge. Preserve the earlier six-cycle lineage at `docs/audits/POST_ASTRA_SIX_CYCLE_REFINEMENT.md` as historical methodology.

### Early skilling / Superpowers routing for the next chat

Do a **trigger check before acting**; do not apply every skill blindly and do not invent a new `early-skilling` named Superpowers skill if one is not installed. Interpret "early skilling" here as *early identification/reading of the relevant existing skills and their actual versions*.

- Scope/architecture/behavior changes → `brainstorming` before implementation; approval gate for a genuinely new architecture. The one-off handoff itself is project memory, **not** a new `SKILL.md`.
- Approved, detailed implementation → `writing-plans`; isolated changes → `using-git-worktrees`; actual feature/bugfix → `test-driven-development`; unexpected failure → `systematic-debugging`.
- Multiple truly independent reads → `dispatching-parallel-agents` if useful and available; never duplicate tasks to occupy slots; avoid one writer per same file.
- Final candidate → `requesting-code-review`, `verification-before-completion`; reviewer comments → `receiving-code-review`.
- Creating/modifying a reusable skill → `writing-skills` with RED/GREEN/REFACTOR, NOT merely because project instructions need to be saved.
- For Git cleanup, separate fresh Git ancestry/recovery verification and destructive owner permission is more important than skill name or agent count.

The Superpowers methodology source is https://github.com/obra/superpowers and the user's plugin mirror https://github.com/openai/plugins/tree/main/plugins/superpowers. Installed skill paths/version in Codex may differ; inspect the live runtime. Six-cycle iterative refinement is a **project review technique**, not evidence of a named official Superpowers skill.

## 8. Suggested first response in the new ChatGPT conversation

Respond in **Turkish**, acknowledge that the local-first product is already merged and PR #60 is merged; cite fresh GitHub main and v3 archive refs; state 46 proposed low-risk branch deletions and 51 review-only plus 577 currently retained by conservative policy, noting counts are snapshot-based. Ask **at most one** real owner question only if required by irreversible authority; otherwise directly review exact 46 candidates and produce the SHA-locked proposal. Do not ask for the entire old chat or repeat the project setup.

If an execution prompt is needed, supply a single **English copy/paste Codex Goal** that **first validates** exact current branch refs, merged PR state, local worktree dependencies and backups; **only when the user explicitly authorizes the precise deletion manifest** does it execute remote deletion in small batches with receipts. Never delete before that authority.

Also offer the independent separate Atlas reconciliation path, but do not silently couple it to remote branch retirement. Limit updates to validated facts, and clearly label local-only evidence as reported rather than independently measured.

## 9. Key source links for navigation

- [Repository and canonical main](https://github.com/Centaurioun/video-intelligence-pipeline/tree/main)
- [Latest branch recovery certification PR #60](https://github.com/Centaurioun/video-intelligence-pipeline/pull/60)
- [Frozen 677-ref certification JSON](https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/audits/2026-10-08-branch-preservation-recovery-certification.json)
- [Frozen certification report](https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/audits/2026-10-08-branch-preservation-recovery-certification.md)
- [v3 archive root and ledger](https://github.com/Centaurioun/video-intelligence-pipeline/blob/archive/history/branch-preservation-v3-20261008/branch-recovery-ledger.json)
- [Historical branch v1 preservation](https://github.com/Centaurioun/video-intelligence-pipeline/tree/archive/history/branch-preservation-v1)
- [Branch cleanup policy and no-delete gates](https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/audits/2026-10-08-main-adoption-and-branch-preservation-plan.md)
- [Canonical current-state handoff](https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/project/01_CURRENT_STATE_AND_HANDOFF.md)
- [Canonical decision-history index](https://github.com/Centaurioun/video-intelligence-pipeline/blob/main/docs/project/08_2026-10-08_DECISION_HISTORY_INDEX.md)
- [Terminated local-first product PR #57](https://github.com/Centaurioun/video-intelligence-pipeline/pull/57)
- [Protected main ruleset](https://github.com/Centaurioun/video-intelligence-pipeline/rules/23927496)

**End-of-handoff invariant:** Git-backed project memory, reversible data-preserving action where possible, exact SHA-bound evidence, owner control of irreversible deletions, and no claim that current-scope local-first completion is production-ready video intelligence.
