# Execution Portfolio — Rejected, Deferred, and Conditional Alternatives

**Status:** planning companion to Execution Portfolio Orchestration Design v1  
**Purpose:** preserve approaches intentionally not selected now, the reason they were not selected, and the conditions under which they may be reconsidered.

This is not an implementation authorization.

---

## 1. Repeated intermediate review/certification

**Current disposition:** REJECTED FOR THIS EXECUTION EPOCH.

Examples:

- reviewer after every task;
- certification after every batch;
- three-certifier waves after each remediation;
- recursive review -> patch -> rereview loops;
- documentation-only audit waves that do not advance executable product capability.

**Reason:**

The owner explicitly prioritizes product completion and has experienced substantial time/token/allowance cost from repeated review/certification cycles. The remaining epoch is execution-first.

**What remains:**

- TDD;
- tests;
- deterministic verification;
- systematic-debugging;
- verification-before-completion.

**Reconsideration trigger:**

Major remaining executable work has been integrated, or the owner explicitly requests a final review/certification phase.

---

## 2. Using Superpowers subagent-driven-development unchanged

**Current disposition:** NOT USED AS THE END-TO-END GOVERNING WORKFLOW.

**Reason:**

Its default flow includes fresh task review and final review. That conflicts with the owner-directed final-only review policy.

**What is retained conceptually:**

- fresh isolated workers;
- self-contained task packets;
- task-focused delegation;
- clean contexts.

**Replacement:**

Repository-specific hierarchical rolling-frontier execution using dispatching-parallel-agents, using-git-worktrees, TDD, systematic-debugging, and verification-before-completion.

**Reconsideration trigger:**

A later adapted workflow exists that preserves delegation without reintroducing intermediate review gates, or the owner changes the policy.

---

## 3. One giant root Codex for all remaining work

**Current disposition:** REJECTED WHEN MULTIPLE LARGE INDEPENDENT BLOCKS EXIST.

**Reason:**

- root context becomes a bottleneck;
- scheduling becomes centralized;
- one blocker can dominate attention;
- independent product areas cannot exploit wall-clock parallelism;
- context compaction risk grows.

**Selected alternative:**

Multiple parallel root Codex sessions, each with its own milestone Goal, branch/worktree, and subagent tree.

**Reconsideration trigger:**

The remaining executable frontier is tightly coupled enough that parallel roots would create more rework than throughput.

---

## 4. Four permanent Gate-root execution folders as the default topology

**Current disposition:** REJECTED FOR NEW DAY-TO-DAY EXECUTION.

**Reason:**

The historical Gate-0/1/2/3 topology was useful for gate-specific governance, but the new execution epoch should decompose by actual product capability and code dependency rather than preserve old Gate boundaries as mandatory filesystem boundaries.

**Selected alternative:**

One repository with temporary/long-lived linked worktrees for current milestone blocks.

**Reconsideration trigger:**

A future task genuinely requires a persistent Gate-specific controller/worktree because of independent long-lived authority or resource boundaries.

---

## 5. Multiple full repository clones for parallel Codex roots

**Current disposition:** REJECTED BY DEFAULT.

**Reason:**

- duplicated object stores;
- greater synchronization burden;
- more ambiguity about which clone contains authoritative local-only commits;
- unnecessary disk and administration overhead.

**Selected alternative:**

Git linked worktrees sharing one repository/object store.

**Reconsideration trigger:**

A tool/harness cannot safely operate with linked worktrees and a separate clone is the only reliable isolation mechanism.

---

## 6. Mandatory fixed child count such as 20, 40, or 60

**Current disposition:** REJECTED.

**Reason:**

Agent count is not throughput if work is duplicated or write ownership overlaps. Runtime limits may also differ by Codex version/configuration.

**Selected alternative:**

Use the highest useful safe concurrency the actual READY frontier and harness support.

**Desired behavior:**

Aggressively delegate and keep slots busy when genuine work exists.

**Reconsideration trigger:**

A measured runtime policy establishes a beneficial fixed concurrency cap/floor for a specific machine/workload.

---

## 7. Artificial work to keep every slot occupied

**Current disposition:** REJECTED.

**Reason:**

Duplicate agents waste allowance, create contradictory output, increase integration cost, and do not advance the product.

**Selected alternative:**

No idle slot while genuine READY work exists; no fabricated task solely to fill a slot.

---

## 8. Unlimited nested delegation

**Current disposition:** REJECTED.

**Reason:**

Deep agent trees make authority, context, branch ownership, and child lifecycle difficult to observe.

**Selected alternative:**

Default maximum three tiers:

Root -> Area Lead -> Worker.

**Reconsideration trigger:**

A future harness offers strong tree-level scheduling/ownership controls and a specific milestone demonstrably benefits from deeper delegation.

---

## 9. Keeping completed children alive for knowledge retention

**Current disposition:** REJECTED.

**Reason:**

- wastes slots;
- preserves stale contexts;
- encourages hidden state;
- increases confusion about active vs historical workers.

**Selected alternative:**

Persist code/state, return compact handoff, close child, recycle slot.

---

## 10. Full-history context inheritance for every child

**Current disposition:** REJECTED.

**Reason:**

Defeats the main reason for delegation: context isolation.

**Selected alternative:**

Clean context plus self-contained task packet.

**Reconsideration trigger:**

A narrowly scoped continuation genuinely requires the exact parent conversation and no repository artifact can express the dependency efficiently.

---

## 11. Long Markdown lane memos for every worker

**Current disposition:** REJECTED FOR NORMAL EXECUTION.

**Reason:**

The owner wants product work, not documentation churn. Narrative lane memos also consume repository and context budget.

**Selected alternative:**

Code/tests/commits plus compact machine-readable JSON/JSONL scheduler/problem state.

**Reconsideration trigger:**

A legal, safety, research, provenance, or final-review requirement genuinely needs narrative explanation.

---

## 12. Chat-only worker knowledge

**Current disposition:** REJECTED.

**Reason:**

Child closure, context compaction, or session loss would erase the engineering record.

**Selected alternative:**

Git code/tests plus minimal durable machine state and Problem Catalog entries.

---

## 13. Automatic stop on the first implementation failure

**Current disposition:** REJECTED.

**Reason:**

Ordinary failures are expected engineering events and should not consume owner interactions.

**Selected alternative:**

systematic-debugging, bounded remediation, then continue independent READY work.

---

## 14. Infinite autonomous debugging

**Current disposition:** REJECTED.

**Reason:**

A hard problem can consume the entire Goal and all allowance without improving product completion.

**Selected alternative:**

Three root-cause-confirmed failed remediation generations by default, then durable problem capture and frontier-aware parking.

**Reconsideration trigger:**

The owner explicitly authorizes a dedicated Problem Resolution Goal for that problem.

---

## 15. Counting every diagnostic command as a repair attempt

**Current disposition:** REJECTED.

**Reason:**

It would prematurely exhaust the remediation budget.

**Selected definition:**

One remediation generation is hypothesis -> evidence -> concrete fix -> verification result.

---

## 16. Deleting resolved problems

**Current disposition:** REJECTED.

**Reason:**

Successful and failed attempts are reusable engineering knowledge and may prevent repeated debugging.

**Selected alternative:**

Retain resolved Problem Catalog records with symptom, cause, attempts, successful fix, proof, and recurrence signature.

---

## 17. Recording only attempted solutions

**Current disposition:** REJECTED.

**Reason:**

Knowing that an approach was considered but deliberately not attempted, and why, can be as important as a failed attempt.

**Selected alternative:**

Problem records may include not-attempted approaches plus reasons such as authority boundary, destructive risk, missing dependency, unsupported hypothesis, or excessive cost.

---

## 18. Fixed cleanup cadence for problem debt

**Current disposition:** REJECTED.

Examples:

- solve all problems after every Goal;
- open a problem Goal after every second or third Goal regardless of impact.

**Reason:**

Problem importance is event-driven, not calendar-driven.

**Selected alternative:**

Open a Problem Resolution Goal when blockers become prerequisites, recur, cluster by root cause, or materially reduce useful frontier throughput.

---

## 19. Stopping an entire Goal because one task is blocked

**Current disposition:** REJECTED.

**Reason:**

Independent product work should continue.

**Selected alternative:**

Park the affected DAG descendants; continue all other READY work.

**Exception:**

The issue is a GOAL_BLOCKER and no useful dependency-safe work remains.

---

## 20. Assuming planning can guarantee zero cross-branch overlap

**Current disposition:** REJECTED AS UNREALISTIC.

**Reason:**

Real implementation reveals shared interfaces and common files that cannot always be predicted.

**Selected alternative:**

Prevent obvious overlap, isolate all roots, record unplanned shared surfaces, and reconcile real overlaps after branches complete.

---

## 21. Treating same-file overlap as an immediate reason to cross-merge roots

**Current disposition:** REJECTED.

**Reason:**

Premature merging couples contexts and may force one incomplete milestone onto another.

**Selected alternative:**

Each root finishes in isolation and records the shared surface; convergence handles it later.

---

## 22. Root Codex sessions directly coordinating through chat

**Current disposition:** REJECTED.

**Reason:**

Creates hidden, non-reproducible cross-root state.

**Selected alternative:**

Git SHAs, commits, machine state, problem IDs, and explicit interface metadata.

---

## 23. Automatic merge after A/B/C/D-style parallel blocks complete

**Current disposition:** REJECTED.

**Reason:**

Git textual conflicts are only one conflict class. Semantic/API/schema/dependency conflicts can exist even when Git reports a clean merge.

**Selected alternative:**

Analyze actual overlaps before integration.

---

## 24. Combining convergence analysis and merge unconditionally

**Current disposition:** REJECTED AS THE DEFAULT.

**Reason:**

A root that immediately merges while discovering conflicts can contaminate the evidence surface and spend its context switching between diagnosis, design, repair, and integration.

**Selected alternative:**

Default phases:

1. convergence analysis;
2. resolution design;
3. remediation execution;
4. integration.

These phases may collapse when actual complexity is small.

---

## 25. Rigidly requiring separate E/F/G/H roots every time

**Current disposition:** REJECTED.

**Reason:**

Small/trivial convergence does not justify unnecessary agent/session overhead.

**Selected alternative:**

Use fresh roots when phase complexity/context size benefits from them. Collapse trivial phases.

---

## 26. Letting the convergence-analysis root merge code

**Current disposition:** REJECTED BY DEFAULT.

**Reason:**

Analysis should observe real branch state before mutation.

**Selected alternative:**

Read-mostly convergence analysis first. Integration occurs only after conflicts and resolutions are understood.

---

## 27. Letting milestone roots merge directly to main

**Current disposition:** REJECTED.

**Reason:**

Main should remain stable while multiple execution branches evolve independently.

**Selected alternative:**

Later isolated integration branch, followed by explicit owner decision for main.

---

## 28. Automatic final integration to main after tests pass

**Current disposition:** REJECTED.

**Reason:**

Passing tests do not grant merge authority.

**Selected alternative:**

Owner explicitly authorizes main integration after inspecting the integrated state.

---

## 29. Blind two-way sync of every local filesystem byte to GitHub

**Current disposition:** REJECTED.

**Reason:**

Would risk uploading caches, media, build outputs, virtual environments, scratch, credentials, or unknown dirty state.

**Selected alternative:**

Non-destructive Git-state reconciliation with attribution and secret/scope checks.

---

## 30. Hard reset / git clean / force push as routine reconciliation tools

**Current disposition:** REJECTED.

**Reason:**

They can destroy recoverable work/evidence.

**Selected alternative:**

fetch, compare ancestry, fast-forward when safe, preserve divergence, push only known authorized branches non-force.

---

## 31. Hard-coding gpt-5.6-luna forever

**Current disposition:** REJECTED.

**Reason:**

The owner wants Luna Medium as a capability/preset policy independent of the current Luna generation.

**Selected alternative:**

Version-agnostic LUNA family + medium reasoning, resolved against the actual Codex spawn allowlist and recorded as requested/resolved/effective identities.

---

## 32. Inventing a DeepSeek model/preset name from ambiguous terminology

**Current disposition:** REJECTED.

**Reason:**

Model identity must be verified, not guessed.

**Selected alternative:**

Retain current verified DeepSeek repository policy until the owner explicitly names/approves a replacement and the runtime supports it.

---

## 33. Using old Gate boundaries as mandatory new execution blocks

**Current disposition:** REJECTED.

**Reason:**

Execution blocks should follow actual product capability and dependency structure.

**Selected alternative:**

Capability-oriented Execution Portfolio DAG.

Historical Gate evidence/authority remains valid where applicable.

---

## 34. Fake project completion percentages

**Current disposition:** REJECTED.

**Reason:**

The repository contains components at very different maturity levels. A single percentage would imply unsupported precision.

**Selected alternative:**

Capability blocks, explicit completed/remaining frontiers, and dependency states.

---

## 35. Pre-designing every future integration conflict now

**Current disposition:** DEFERRED.

**Reason:**

The correct integration strategy depends on actual future branch heads and diffs.

**Selected alternative:**

Design only the convergence contract now; let the later convergence root inspect real evidence and choose the exact strategy.

---

## 36. Production/protected/provider expansion as part of ordinary execution Goals

**Current disposition:** REJECTED WITHOUT SEPARATE AUTHORIZATION.

This includes, unless separately approved:

- protected/archive-media execution;
- production export/render;
- provider/cloud calls;
- model downloads;
- Gate promotion;
- destructive repository cleanup.

The execution-first policy does not widen these boundaries.

---

## 37. Starting execution before canonical process-policy transition

**Current disposition:** REJECTED.

**Reason:**

Current main still contains process rules that conflict with the refined execution portfolio. Starting Codex before reconciling them would make fresh-agent behavior ambiguous.

**Selected alternative:**

One bounded owner-approved main-promotion step first.

---

## 38. One global Problem Catalog JSONL shared by every parallel root

**Current disposition:** REJECTED.

**Reason:**

Parallel appends on independent branches manufacture avoidable merge conflicts and turn troubleshooting memory into a shared-writer hotspot.

**Selected alternative:**

Shard durable Problem records by portfolio/Goal/problem identity; generate indexes later if useful.

---

## 39. Concurrent unsynchronized Git worktree/ref administration by multiple roots

**Current disposition:** REJECTED.

**Reason:**

Substantive branches can be independent while their linked-worktree metadata and shared refs still live in one Git common directory.

**Selected alternative:**

A short-lived Portfolio Bootstrap/Worktree Admin plus serialized topology-changing operations.

---

## 40. Accepting stale child commits without checking their original base

**Current disposition:** REJECTED.

**Reason:**

Rolling-frontier execution advances the parent while children run. A path-disjoint-looking commit may still encode stale public-interface assumptions.

**Selected alternative:**

Bind BASE_SHA in every handoff and perform stale-base/path/contract checks before integration.

---

## 41. Changing the concrete Luna generation silently within one Goal

**Current disposition:** REJECTED.

**Reason:**

It weakens reproducibility and makes agent behavior/model provenance ambiguous.

**Selected alternative:**

Resolve LUNA + medium to one supported concrete model at Goal start and freeze that resolution for the Goal unless an explicit Goal-level transition is recorded.

---

## 42. Mandatory Context Curator for every Goal

**Current disposition:** REJECTED.

**Reason:**

A curator is valuable for broad high-concurrency Goals but unnecessary overhead for smaller ones.

**Selected alternative:**

Use it adaptively when it materially reduces root-context load.

---

## 43. Treating a clean Git merge as proof of semantic compatibility

**Current disposition:** REJECTED.

**Reason:**

Branches can cleanly merge while disagreeing on API signatures, schema meaning, config semantics, temporal domains, dependency expectations, or migration order.

**Selected alternative:**

Convergence consumes terminal milestone handoffs and builds a semantic-conflict matrix before integration.

---

## 44. Launching four root writers merely because four slots exist

**Current disposition:** REJECTED.

**Reason:**

Root concurrency must respect actual independent milestones, shared-contract risk, host capacity, and canonical resource policy.

**Selected alternative:**

Separate root-writer budget from heavy-resource budget and choose the highest useful safe root concurrency after policy promotion.

---

## 45. Committing every scheduler event and transient slot assignment

**Current disposition:** REJECTED.

**Reason:**

That would recreate documentation/telemetry churn and inflate merge surfaces.

**Selected alternative:**

Keep ephemeral scheduler state local/reconstructable; commit only durable authority, terminal handoff, problem, shared-surface, and recovery state.

---

## 46. Letting a safety/integrity-critical problem hide behind NON_BLOCKING

**Current disposition:** REJECTED.

**Reason:**

Severity and frontier impact are separate, but scheduler labels cannot downgrade source-preservation, evidence/temporal correctness, authorization/security, or data-integrity failures.

**Selected alternative:**

Such problems fail closed for the affected capability and constrain GOAL_COMPLETE_WITH_DEFERRED_PROBLEMS.

---

## 47. Using writing-plans' generic execution handoff unchanged after approval

**Current disposition:** REJECTED WHEN IT CONFLICTS WITH OWNER POLICY.

**Reason:**

The generic skill may recommend task-level reviewer gates or execution modes that reintroduce the review treadmill.

**Selected alternative:**

Use writing-plans for implementation detail after approval, but bind the produced plan to the owner-approved Execution Portfolio execution method.

---

## 48. Why this alternatives register exists

This file preserves intentional choices so future sessions do not accidentally recreate discarded process patterns simply because the original discussion context is gone.

A rejected alternative may be reconsidered when its stated trigger occurs.

Reconsideration is not a failure of the current design; it is an explicit response to changed evidence, tooling, authority, or project phase.
