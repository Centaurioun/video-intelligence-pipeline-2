# Video Intelligence Pipeline — Project Charter

**Document role:** durable repository-level project orientation  
**Update frequency:** rare; only when project mission or architectural invariants materially change  
**Authority:** explicit user authorization and current governing repository contracts supersede this summary

---

## 1. Mission

Build a local-first / selectively hybrid video-intelligence and editing-support pipeline for a large performing-arts archive, especially ballet, dance, and music footage.

The intended long-term workflow is:

`source/archive`
→ `deterministic inventory and provenance`
→ `semantic useful-moment retrieval`
→ `source-native temporal refinement`
→ `measured PTS/frame evidence`
→ `human editorial decision`
→ `versioned edit plan`
→ `render/export`
→ `technical and editorial QC`

The goal is not generic video understanding. The goal is reliable useful-moment discovery and evidence-preserving editorial handoff.

---

## 2. Core Invariants

### Source preservation

Source media is immutable by default. Paths, provider IDs, Drive IDs, filenames, vector IDs, UI IDs, or match-group IDs are not canonical content identity.

### Evidence discipline

Canonical assertion-level evidence classes are:

- `MEASURED`
- `MATCHED`
- `VISUALLY_OBSERVED`
- `AUDIO_OBSERVED`
- `EDITORIAL_INFERENCE`

`NOT_OBSERVED` is an availability/state marker, not an evidence class.

Do not silently upgrade evidence strength.

### Temporal correctness

Semantic/model/provider timestamps identify candidate regions only. They are never exact edit boundaries.

Exact temporal work must use source-native deterministic evidence such as PTS/timebase/frame information. For VFR media, never derive frame identity using `seconds × nominal FPS`.

### Editorial boundary

Technical refinement does not itself constitute an editorial decision.

Preferred handoff:

`semantic candidate`
→ `source-native refinement`
→ `measured interval`
→ `human editorial decision`
→ `edit plan`
→ `render`
→ `QC`

---

## 3. Gate Architecture

### Gate 0 — Diagnostic Retrieval

Can one bounded local semantic visual-retrieval arm materially improve useful-moment discovery over a transparent metadata baseline?

### Gate 1 — Representation / Capability Benchmark

Which representation, modality, model, provider, or retrieval capability deserves broader study?

### Gate 2 — Reliability / Scale

What restart, recovery, indexing, queueing, caching, persistence, or scheduling mechanisms are actually justified by measured workload/failure evidence?

### Gate 3 — Editing / QC

Can eligible candidates be deterministically refined into attributable edit decisions, edit plans, renders, and QC evidence?

Gates are evidence boundaries, not necessarily rigid serial work phases. Separately authorized reversible preparation may overlap, but outcome-dependent promotion decisions remain hard gates.

---

## 4. Maturity Model

Use explicit maturity states instead of vague percentages:

- `M0_NOT_STARTED`
- `M1_CONTRACTED`
- `M2_SCAFFOLDED`
- `M3_SYNTHETIC_READY`
- `M4_OUTCOME_GATED_READY`
- `M5_GATE_EVIDENCE_COMPLETE`

---

## 5. Execution Philosophy

Optimize wall-clock time through useful dependency-safe parallelism, not agent count for its own sake.

Preferred principles include:

- rolling-frontier scheduling;
- exclusive writer ownership;
- immutable candidate/milestone SHAs;
- durable Git-backed ledgers and receipts;
- multiple isolated controllers only when scopes are genuinely disjoint;
- one controlled portfolio-integration path;
- shared-contract ownership and stale-base detection;
- adaptive global concurrency;
- bounded remediation and certification.

Never manufacture duplicate work merely to occupy slots.

---

## 6. Superpowers Methodology

Use Superpowers as trigger-based workflows, not a checklist invoked all at once.

Typical routing:

- architecture/interface design → `brainstorming`
- approved design → `writing-plans`
- isolated implementation → `using-git-worktrees`
- genuinely independent work → `dispatching-parallel-agents`
- focused/coupled plan execution → `subagent-driven-development` where appropriate
- behavior change → `test-driven-development`
- unexpected failure → `systematic-debugging`
- candidate completion → `requesting-code-review`
- incoming review feedback → `receiving-code-review`
- completion claim → `verification-before-completion`
- skill creation/editing → `writing-skills`

Project-specific Gate authority belongs primarily in specs, plans, task packets, protocols, and repository instructions rather than Gate-specific skills.

---

## 7. Repository as Durable Memory

GitHub is the long-term technical memory for:

- current state;
- architecture decisions;
- specifications;
- implementation plans;
- task packets;
- run ledgers;
- subagent reports;
- audits;
- rejected alternatives;
- reconsideration triggers;
- verification evidence.

Do not depend on one long ChatGPT or Codex conversation as the only project memory.

For current mutable state, read `docs/project/01_CURRENT_STATE_AND_HANDOFF.md`.
For current orchestration direction, read `docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md`.
For maintenance ownership, read `docs/project/STATE_MAINTENANCE_PROTOCOL.md`.
