# Decision history and rejected alternatives — 2026-10-08 index

**This is a navigation/recovery index, not a rewrite of the historical decisions.** Each item states its status and rationale. Full wording, exceptions and reconsideration triggers remain in the linked immutable sources. Branch-target material remains subject to durable Git-history preservation before branch deletion.

## Current decisions grounded in canonical main

| Decision/status | Why | Authoritative location |
| --- | --- | --- |
| **ACCEPTED:** local-first/selectively hybrid pipeline, source immutability, source-native PTS/timebase for exact edit boundaries | Semantic timestamp/location inference cannot certify VFR frame boundaries; editorial choices require a human | `docs/project/00_PROJECT_CHARTER.md`; frozen Gate contracts |
| **ACCEPTED:** four scientific evidence/decision Gates, not four mandatory permanent implementation worktrees | Gate maturity is scientific; implementation parallelism should follow real dependencies/ownership | `docs/project/00_PROJECT_CHARTER.md`; `docs/superpowers/specs/2026-09-23-execution-portfolio-rejected-alternatives.md` §4 and §33 |
| **ACCEPTED:** immutable SHA/tree-bound candidate and explicit owner-controlled integration | Tests alone are insufficient to prevent unreviewed semantic/schema conflicts | rejected alternatives §§23–28; PR #57 G02/G03 exact evidence and owner-directed protected merge |
| **REJECTED:** automatic merge of independent roots or automatic main promotion on passing tests | Textual Git conflict freedom is weaker than API/semantic/contract verification; canonical scope changes require owner decision | rejected alternatives §§23, 24, 27, 28 |
| **REJECTED:** a single giant root controller or fixed 20/40/60-agent quotas | Context bottlenecks, duplicate tasks, write overlap and scheduler overhead do not increase genuine throughput | rejected alternatives §§3, 6–9; Remaining Work Atlas design |
| **ACCEPTED:** rolling dependency-safe frontier, isolated exclusive writers, durable problem/evidence trail | Limits stale-context and long-goal stalls; preserves reproducibility | `docs/superpowers/specs/2026-10-03-remaining-work-execution-atlas-and-parallel-verification-design.md` |
| **REJECTED:** deleting resolved Problems; hiding failed approaches | Problem history helps avoid repeated incorrect repairs and preserves auditability | rejected alternatives §§16–17 |
| **REJECTED:** hard reset, git clean and force-push as routine recovery | Could destroy uncommitted work and audit evidence | rejected alternatives §30 |
| **REJECTED:** fake whole-project completion percentages | Gate maturity and real-media validation do not reduce to an unqualified code-completion percentage | rejected alternatives §34; terminal G03 scope exclusions |
| **ACCEPTED:** source historical-presence authority is separate from current source-write authorization | Legitimately inherited files must be attributable without silently gaining future write privilege | `docs/superpowers/specs/2026-09-25-root-h-workspace-source-authorization-design.md`; ordinal 5 and 6 authority amendments on admin branch |
| **ACCEPTED FOR CURRENT LOCAL-FIRST SCOPE:** G02 candidate plus G03 eight-lane final verification | Bound product candidate and six independently verified roots; 1,290 reported passing tests, no blocking current-scope findings | PR #57; `controller/remaining-work/authoritative@a81104f47667a7f9ee1f47a86e1bfe711bfa2dd4` |
| **NOT AUTHORIZED / NOT OBSERVED:** real-media QC, protected archive, provider/cloud, model download, production export, broad modality/Gate promotion | Synthetic/current-local evidence cannot imply those safety, model-quality or operational conclusions | G03 final verification at `controller/area/G@988b8790cc45ad1c1093f0d1ebbae15ab0716f38` |

For full source-auth implementation authority do not infer current grants from a `HISTORICAL_SOURCE_PRESENCE_AUTHORIZED` record. Refer to the exact frozen source-authority schema and admin branch at `d766def9d22978328e8767ce7cc769956f41df15`.

## Current proposals and historical material that must not silently become adopted

| Candidate/reference | Status for this index | What must be preserved |
| --- | --- | --- |
| `docs/event-driven-portfolio-orchestration-20261007` ([PR #56](https://github.com/Centaurioun/video-intelligence-pipeline/pull/56), head `19b07d65443caf0c8c35fb98f3270fe70f441059`) | **PROPOSED; draft PR at 2026-10-08 review** | “Messages wake; Git proves,” rationale against five-minute polling/manual owner relay, scoped pressure-test requirement before globally installing skill |
| `policy/hierarchical-throughput-mandatory-parallel-v1` ([PR #14](https://github.com/Centaurioun/video-intelligence-pipeline/pull/14)) | **PROPOSED / historical draft** | Earlier throughput-policy alternative; compare with later approved Atlas before adopting |
| `handoff/chatgpt-continuation-20260925-v2` | **HISTORICAL / branch-unique records observed** | Original context, multi-root architecture, decisions and rejected/conditional approaches, not a modern dispatcher |
| `design/h3-e03-lineage-successor-20261006-g03` | **HISTORICAL / branch-unique design observed** | Exact E03 provenance design and peer-review iteration; preserve not automatically current authority |
| `archive/history/branch-preservation-v1` with `.orchestration/maintenance/branch-hygiene-cleanup-v1/preservation-recovery.json` | **HISTORICAL RECOVERY** | Older branch names, HEADs, preservation root and recovery map; do not treat it as coverage of newly created 2026-10 branches |
| `controller/remaining-work/authoritative`, `controller/area/G`, `execution/execution-portfolio-20260924-v1/bootstrap` | **LIVE TERMINAL EVIDENCE / TRUST ROOTS** | Terminal Atlas, exact G03 review/verification and historical source-authority amendments; retain actual reachable refs until independently migrated |

## 2026-10-09 branch-history consolidation

The owner-reviewable per-ref history, source status, current worktree assessment, and retirement gates are summarized in [`09_2026-10-09_BRANCH_HISTORY_CONSOLIDATION.md`](09_2026-10-09_BRANCH_HISTORY_CONSOLIDATION.md). Its 70 candidates remain live pending the documented gates and separate owner deletion authority.

## Future recovery index obligations

Before retiring *any* branch, record its exact name/head/tree, complete set of branch-unique plans/rejected rationales/results, present decision status (accepted/proposed/rejected/deferred), successor evidence or reconsideration condition, permanent reachable archive ref, fresh-clone/bundle restore test, and presence/absence of uncommitted local state.

Do not confuse an inventory SHA entry with Git-object retention. Do not delete historical failure records or rewrite old architecture debates into current policy. The first branch-head snapshot is `docs/audits/2026-10-08-branch-head-inventory.json`; the phase gates are `docs/audits/2026-10-08-main-adoption-and-branch-preservation-plan.md`.

**Outstanding work:** This index is representative but not a full 674-branch content audit; branch-by-branch unique-asset extraction and recoverability certification remain PENDING. No branch deletion is authorized by this index.
