# Project State Maintenance Protocol

**Purpose:** make GitHub the living project memory so the user does not have to manually keep ChatGPT Project files synchronized.

---

## 1. Source-of-truth model

Use these layers:

1. **Explicit current user authorization** — highest authority.
2. **Current governing repository contracts and verified Git state** — technical authority.
3. **`docs/project/01_CURRENT_STATE_AND_HANDOFF.md`** — current mutable handoff/index into the technical authority.
4. **`docs/project/00_PROJECT_CHARTER.md`** — durable mission/invariants.
5. **`docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md`** — current condensed orchestration interpretation.
6. **ChatGPT Project-uploaded files** — bootstrap/orientation copies only; they are intentionally not expected to be manually updated after every task.
7. **Conversation memory** — convenience only, never technical authority.

When layers conflict, move upward in this list and verify repository evidence.

---

## 2. Ownership

### Execution Codex / implementation controller

Owns task-local execution evidence only unless its Goal explicitly says otherwise:

- implementation code/tests;
- task/run ledger;
- lane memos;
- receipts;
- candidate SHAs;
- task-specific verification evidence.

An execution controller SHOULD NOT normally update the global `01_CURRENT_STATE_AND_HANDOFF.md` as part of its own success claim. This avoids self-attestation and closeout-SHA recursion.

### Independent reconciliation agent

After a major terminal execution/review/benchmark task, an independent ChatGPT/reconciliation agent should:

1. verify terminal claims against GitHub/repository evidence;
2. classify what is newly `MEASURED`, merely `MATCHED`, still `NOT_OBSERVED`, or blocked;
3. update `docs/project/01_CURRENT_STATE_AND_HANDOFF.md` on canonical `main` if the current global state materially changed;
4. update `docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md` only if the preferred orchestration/design actually changed;
5. leave `00_PROJECT_CHARTER.md` untouched unless durable mission/invariants changed;
6. record detailed audits/decision history separately instead of bloating the handoff files.

ChatGPT is the preferred default reconciliation owner because it can compare the terminal controller report with repository evidence before rewriting global state. A dedicated verification Codex may perform the same role when explicitly assigned.

---

## 3. Update triggers

Update `01_CURRENT_STATE_AND_HANDOFF.md` after any material event such as:

- terminal Issue/Goal result;
- Gate maturity/disposition change;
- newly verified blocker or blocker closure;
- authorization change;
- canonical execution boundary change;
- accepted planning/design reconciliation that changes the immediate next action;
- pilot/benchmark result;
- production promotion or explicit stop decision.

Do **not** update it for every minor commit, lane completion, reviewer comment, or transient intermediate state.

Update `02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md` only when a material architecture/orchestration decision changes.

Update `00_PROJECT_CHARTER.md` only when durable mission, Gate definitions, evidence invariants, or high-level authority principles change.

---

## 4. Required fields for current-state updates

Every material refresh of `01_CURRENT_STATE_AND_HANDOFF.md` should preserve or update:

- last reconciled date;
- reconciliation/canonical anchor SHA;
- current Gate/maturity/disposition;
- active/terminal task state;
- verified or matched evidence summary;
- current blockers;
- current authorization boundary;
- current preferred planning branch/audit pointer when relevant;
- exact immediate next action;
- important `NOT_OBSERVED` facts;
- fresh-session reading rule.

Do not replace exact SHAs with vague phrases such as “latest commit”.

---

## 5. Certified state vs bookkeeping state

Do not collapse these concepts:

- `CERTIFIED_CANDIDATE_SHA` — substantive tests/certification ran here;
- `CLOSEOUT_HEAD_SHA` — later bookkeeping/documentation head, if any;
- `REMOTE_DURABILITY` — externally observed remote state.

If a closeout documentation commit follows substantive certification, the handoff must say so rather than implying certification executed on the later bookkeeping SHA.

---

## 6. Planning branches vs canonical main

Detailed design exploration, rejected alternatives, audits, and independent critiques may live on planning branches.

The concise global current-state handoff belongs on canonical `main` because every fresh agent should be able to recover the current project state without guessing which historical planning branch is newest.

A planning-branch conclusion does not become current execution authority merely because it exists. The global handoff may point to it and state its approval/reconciliation status.

---

## 7. ChatGPT Project file policy

The user should not be required to manually replace Project-uploaded files after every task.

Fresh ChatGPT sessions should treat the uploaded Project files as stable bootstrap context and then immediately read the current repository handoff files under `docs/project/`.

If an uploaded Project file says Issue X is active but repository `01_CURRENT_STATE_AND_HANDOFF.md` says it has terminated, the repository handoff controls after verification.

No manual user synchronization is required.

---

## 8. Fresh-session startup

A fresh repo-capable ChatGPT/Codex should read, in order:

1. `AGENTS.md`;
2. `docs/INDEX.md`;
3. `docs/project/00_PROJECT_CHARTER.md`;
4. `docs/project/01_CURRENT_STATE_AND_HANDOFF.md`;
5. `docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md`;
6. this protocol;
7. governing task/spec/plan and run evidence relevant to the immediate request.

Then verify mutable claims before acting.

---

## 9. User burden

The intended user workflow is simple:

- give the terminal Codex/controller response to the reconciliation ChatGPT;
- let that agent independently verify the repository;
- let the agent update the repository handoff when needed;
- continue from the repository state.

The user should not have to manually edit handoff Markdown files, SHAs, issue status summaries, or next-action text.
