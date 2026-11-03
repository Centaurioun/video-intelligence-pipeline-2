# VIP V2 Two-Stage Migration Entry Gate Design

**Status:** `OWNER_APPROVED_FOR_CONTRACT_AMENDMENT_PREPARATION — CONTRACT_NOT_APPROVED — GATE_A_NOT_ACTIVE — NOT_AUTHORIZED_FOR_EXECUTION`
**Authority snapshot:** canonical `main` / GitHub `main` / `origin/main` at `bf605b9b9008c634607cedf2e42d7fb8f54aa9d1`
**Run:** `run-20261011-vip-v2-two-stage-entry-gate-design`
**Purpose:** propose a narrow preparatory-code entry contract without activating it.
**Design provenance:** PR #73 design candidate `3bc5ae79eada6c29cfbe44c26635c297d95110b4`; published PR #73 head `177d97d78fc416ce9e62ea493a3100ec44219459`; prior independent review is preserved at `docs/agent-runs/run-20261011-vip-v2-adr-entry-amendment/reviews/pr73-independent-design-review-001.md` and was bound to the original candidate, not this amendment candidate.
**Source blobs:** original design `b1a89c32325e1a0aa7023d1e79796328890dbcf9`; original proposed redlines `72af664da2f1eff2e1289c215e5f8e91c493e0ae`; prior independent-review blob `86a12d5d3b79f03263f25d2b5dacfd1e4808e322` at review commit `9f756d41196a550b942b0142b92a3d7f1237a840`.

## 1. Intent and binding constraints

The owner accepted this design direction for contract-amendment preparation, subject to the ADR-level clarification below. This design copy remains a proposal only. It does not amend current authority, clear the blocked receipt, authorize Task 1, or authorize implementation, model, or media activity. The current PR #72 decision remains `TASK1_MODEL_FREE_ENTRY_BLOCKED`; that historical/current decision remains controlling until the exact proposed ADR and subordinate amendments are accepted and canonically adopted, followed by fresh scoped review and separate Task 1 execution authorization.

The owner clarified that Task 1 is V2-related software implementation. It must not be labeled documentation-only or categorically placed outside migration because it is model-free. Accordingly, this amendment candidate proposes an explicit, narrow ADR-0002 amendment for post-V1 Gate A and retains Gate B for full V2 migration/runtime work. The published PR #73 design and its review remain unchanged historical evidence.

Preserve these current dispositions without reinterpretation: Task 0 `NO_GO_BLOCKED`; V2 Bootstrap `BLOCKED`; H3-C05 `UPHOLD_UNAUTHORIZED`; F07 `PASS_CURRENT_RUNTIME_RECEIPT_ONLY`; tokenizer semantic correctness `NOT_OBSERVED`. Do not rewrite the historical blocked refresh receipt or relabel it PASS. Preserve all 56 checklist condition IDs and meanings, its A–G/Go-No-Go structure, and all 13 refresh protocol steps.

## 2. Approaches considered

| Option | Shape | Benefit | Cost / risk | Disposition |
|---|---|---|---|---|
| A. Retain one hard implementation gate | No code starts until all applicable Task 0/full migration readiness passes. | Least authority complexity; directly follows current hard gate. | Keeps model-independent profile-contract work coupled to unresolved runtime/model/media readiness. | Safe fallback if a subordinate exception is not adopted. |
| B. Add a narrowly scoped preparatory entry gate | Define a separate, owner-approved Task 1 preparation entry while retaining the unchanged full migration gate. | Lets only the already planned model-free contract work proceed after fresh scoped assessment and explicit authorization. | Requires explicit amendments to the accepted plan and subordinate migration authority, strong scope enforcement, and independent review. | **Recommended**, conditional on owner approval of amendments and exact later execution authorization. |
| C. Separate synthetic prototype | Build a detached prototype outside accepted Task 1. | Avoids altering migration entry language. | Duplicates the contract and risks creating a second, weakly governed implementation that cannot be accepted as Task 1. | Reject; does not satisfy the requested plan-bounded work as cleanly. |

Option B is recommended as a narrowly scoped Gate A after V1 completion. Task 1 remains software implementation associated with the V2 migration program. The owner has directed that an explicit ADR-level amendment resolve the activation boundary; subordinate wording cannot characterize Task 1 as outside migration or override the ADR. Gate A does not establish V2 model/runtime readiness, authorize Gate B, or waive the full Task 0 gate for later work.

## 3. Two decisions and two gates

### Gate A — scoped model-free preparatory code

The only proposed eligible work is Task 1, “Closed, validated three-profile semantic-space contract,” from the accepted plan provenance blob `78127a9199a912531d5b2240eed66e93814d83f3` (planning approval only). Allowed operations, after both contract adoption and a separate explicit owner authorization, are limited to:

- a frozen `ModelProfile` type and closed validation logic;
- deterministic profile-to-existing-`SemanticSpace` mapping;
- synthetic model identity fixtures with complete immutable identity fields;
- model-free RED/GREEN/REFACTOR tests;
- V1 persisted identity preservation regression;
- independent feature review and bounded verification.

Only the Task 1 files and operations listed in the accepted plan are in scope: create `experiments/persistent_local_index/model_profile.py`; modify `experiments/persistent_local_index/model_space.py` only as needed for V2 compatibility while preserving V1 persisted identity semantics; add model-free tests at `experiments/persistent_local_index/tests/test_model_profile.py`; and use the listed existing `experiments/persistent_local_index/tests/test_model_space.py` regression path as specified by the plan. The single owner execution authorization must state the exact allowed operations for each named path. No other plan task or source path inherits Gate A authority.

Gate A requires: (1) exact owner acceptance and canonical adoption of the ADR amendment and all coordinated subordinate amendments; (2) a new current, exact-main `TASK1_PREPARATORY_ENTRY_APPROVED` decision after complete scoped A–D assessment and explicit E–G applicability; (3) independent review accepting that exact decision; and (4) one separate owner execution authorization naming the decision, task, exact files and operations, execution method, branch/base SHA, and expiry/supersession rule. The owner authorization is the sole execution-start approval; no duplicate task-start token is introduced. A readiness decision alone never grants execution permission.

### Gate B — full migration and runtime execution

Gate B is the existing Task 0/full migration gate. All current Task 0 requirements and applicable A–G checks remain binding for runtime migration. Model/checkpoint acquisition, processor acquisition, model load, MPS inference, archive or video input, providers/cloud/egress, indexing, benchmarks, Gate promotion, and production integration each remain separately governed by their existing exact authorization requirements. Gate A conveys no Gate B permission and does not reduce a Gate B predicate.

## 4. Authority precedence and adoption boundary

Proposed precedence after adoption: (1) repository and architecture authority, including the amended ADR-0002; (2) the coordinated, canonically adopted subordinate amendments limited to Task 1 Gate A; (3) unchanged full-migration/Task 0 requirements for Gate B; (4) the accepted implementation plan as amended; (5) a current independently reviewed task-specific readiness decision; (6) one exact owner execution authorization. Lower layers cannot waive higher restrictions. In conflict, fail closed.

The proposed amendments update the package entrypoint `00_README_AND_ENTRYPOINT.md`, authority `01_AUTHORITY_SCOPE_AND_ACTIVATION.md`, refresh protocol `19_POST_COMPLETION_REFRESH_PROTOCOL.md`, launch packet `24_FUTURE_CODEX_LAUNCH_PACKET.md`, checklist `26_COMPLETION_AND_MIGRATION_READINESS_CHECKLIST.md`, and the accepted implementation plan, alongside this ADR. This small entrypoint addition closes its general dormant-package wording for the exact Gate A exception; the V2 Base runbook remains a Gate B/runtime procedure. PR #72 and its blocked decision remain untouched historical/current evidence.

The owner has resolved that ambiguity for preparation: an explicit, narrowly scoped ADR-0002 amendment is required because Task 1 is software implementation associated with V2 migration. The proposed amendment authorizes only the possibility of Gate A after verified V1 completion and after future exact owner acceptance/adoption; it does not activate Gate A, approve subordinate amendments, or authorize Task 1 execution. This review does not make the owner decisions required by the proposed activation sequence.

## 5. Machine-readable decision contract

The proposed decision values are:

- `TASK1_PREPARATORY_ENTRY_APPROVED`
- `TASK1_PREPARATORY_ENTRY_BLOCKED`
- `FULL_MIGRATION_NO_GO_BLOCKED`

They are proposed contract values only, not current states. The current state remains the PR #72 blocked decision. The activation evidence, Task 1 file/operation scope, freshness rules, supersession conditions, and fail-closed boundaries are recorded in `docs/agent-runs/run-20261011-vip-v2-adr-entry-amendment/gate-a-activation-preconditions.json`; the existing 56-predicate inventory and 13-step history remain in their unchanged canonical source artifacts.

An APPROVED value means only that the proposed Task 1 decision procedure is satisfied. Work still cannot start without one separately recorded owner execution authorization containing all required matching bindings. Missing, stale, inconsistent, unreviewed, or superseded evidence resolves to `TASK1_PREPARATORY_ENTRY_BLOCKED`; the independent full-migration decision remains `FULL_MIGRATION_NO_GO_BLOCKED` whenever Task 0 remains blocked.

## 6. Fail-closed acceptance behavior

| Case | Required result |
|---|---|
| Exact Task 1 synthetic-only scope, current approved assessment, exact owner execution authorization | Gate A may start only after independent review and one current owner authorization binds the same SHA, scope, execution method, branch/base, and expiry/supersession rules. Gate B stays blocked. |
| No owner authorization | `TASK1_PREPARATORY_ENTRY_BLOCKED`; no edits or tests under migration authority. |
| Missing, mutable, unresolved, or inconsistent source/model identities | Reject profile; blocked decision if required fixture/provenance identity is incomplete. Never synthesize real checkpoint identity. |
| Attempt to acquire/load V2 checkpoint, processor, or model | Immediate STOP; outside Gate A; requires separate current authority under Gate B. |
| Request to access archive/video/media bytes | Immediate STOP; outside Gate A. |
| Task 2 or later under Task 1 authority | Reject; no inherited authority. |
| Unreviewed SemanticSpace persistence/schema/shared-contract change | STOP; mark decision superseded and require new design/review/authorization. |
| Stale branch, changed canonical main, changed relevant contract blob, or superseded evidence | STOP; decision cannot be reused; refresh and reassess from current authority. |
| Task 1 completion claim without fresh focused tests, V1 regression and independent review | Reject completion claim; no `PASS`/acceptance state. |
| Gate B request while Task 0 is blocked | `FULL_MIGRATION_NO_GO_BLOCKED`; deny runtime/model/media/index/benchmark/promotion operations. |

## 7. Freshness, stop, and completion rules

Bind every decision to exact canonical-main SHA; design and accepted-plan provenance; changed governing-document blob IDs; the 56-predicate contract identity; refresh receipt identity and its unchanged blocked outcome; current scope; reviewer identity/disposition; owner authorization reference; execution method; branch/base SHA; and expiry/supersession conditions. A main advance does not automatically stale every decision, but any change to a consumed authority, plan, checklist, protocol, relevant implementation contract, or evidence source does. Require reassessment when in doubt.

Stop immediately on scope expansion, identity ambiguity, real artifact access, unreviewed shared-contract change, unexpected branch/base drift, changed test semantics, failed required tests, reviewer rejection, owner authorization expiry/revocation, or contradiction between authority surfaces. Preserve failure evidence, publish no PASS, and return to owner review as appropriate.

A Task 1 completion candidate requires fresh focused tests and existing model-space regression on the exact candidate; `git diff --check`; path/scope audit; independent review of the exact frozen candidate SHA; and a handoff stating Gate B remains blocked. This design does not run or authorize these implementation checks.

## 8. Non-goals and release boundary

No new Task 1 implementation plan is created by this design; the existing accepted plan remains the source of Task 1 scope. This document and its PR are for owner review only. Adoption of this design alone cannot activate Gate A. PR #72 and PR #73 must remain unmodified. This candidate is to be published as Draft and not merged or canonically adopted under this task; any later owner-approved canonical adoption must include the complete coordinated amendment candidate. Do not claim the new gate is active.

## 9. Open owner decisions

1. Accept, reject, or revise the exact final ADR-0002 amendment and coordinated subordinate contract candidate at its frozen SHA/tree, then decide on canonical adoption.
2. After adoption, separately authorize Task 1 execution only if a fresh exact-main scoped readiness decision is independently accepted. The execution authorization must state its exact files, operations, method, branch/base SHA, and expiry/supersession conditions.
3. No Gate A activation or Task 1 execution authorization is included in this proposal. Gate B and its full Task 0 requirements remain in force.

No answer is presumed by this proposal.
