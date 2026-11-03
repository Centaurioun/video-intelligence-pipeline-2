# Project Reading Order

This workspace intentionally separates current project state, architecture/specification,
repository process contracts, historical design/evidence context, curated references,
and complete external source trees.

## 2026-10-24 — Owner decision: development source-authorization enforcement removed

The Owner explicitly removed development-time source-authorization enforcement
from `scripts/verify-workspace.sh` after it repeatedly blocked ordinary Root-H
and Gate-3 development. The verifier now reports
`DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT=DISABLED_BY_OWNER` and contributes no
failure for missing branch/path grants. See
[ADR-0003 — development source-authorization enforcement removed](decisions/ADR-0003-development-source-authorization-enforcement-removed.md).
Unrelated protections (media integrity, PTS/timebase, evidence integrity,
secrets, providers, protected archives, production Owner trust activation, and
canonical-main merge authorization) remain in force.

## Fresh-session entry point

Every fresh repo-capable ChatGPT/Codex session should begin with:

1. [Workspace guidance](../AGENTS.md)
2. [Project charter](project/00_PROJECT_CHARTER.md)
3. [Current state and handoff](project/01_CURRENT_STATE_AND_HANDOFF.md)
4. [Fresh-session execution handoff (2026-10-03)](project/04_FRESH_SESSION_EXECUTION_HANDOFF_2026-10-03.md)
5. [Codex execution bootstrap handoff](project/03_CODEX_EXECUTION_BOOTSTRAP_HANDOFF.md)
6. [Orchestration design and next plan](project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md)
7. [Project state maintenance protocol](project/STATE_MAINTENANCE_PROTOCOL.md)

The files under `docs/project/` are the repository-level handoff surface. In particular,
`01_CURRENT_STATE_AND_HANDOFF.md` is the concise mutable state index that should be
updated by an independent post-run reconciliation agent after material terminal events.
For the current context-limit transition, read
`04_FRESH_SESSION_EXECUTION_HANDOFF_2026-10-03.md` before resuming Remaining Work
chunks; it records the exact cumulative prompt-library state, anti-loop rules, and D6
resume point. For the broader transition into substantive Codex implementation, also read
`03_CODEX_EXECUTION_BOOTSTRAP_HANDOFF.md`; it contains the compact execution bootstrap
contract and deliberately avoids replaying the full historical conversation.
ChatGPT Project-uploaded files are bootstrap/orientation copies only and are not expected
to be manually synchronized after every task.

Current verified repository evidence and explicit user authorization always supersede a
stale handoff summary.

The latest real-source FVS mainline reconciliation is
`audits/2026-09-21-real-source-fvs-mainline-integration-reconciliation.md`, with
the durable run index at
`agent-runs/run-20260921-real-source-fvs-mainline-integration-v1/`.

## 2026-10-09 — Owner-approved VIP V2 design; V1 preserved; plan for review

The owner approved the **one VIP codebase / three validated model profiles** direction, then explicitly approved proceeding with written-spec signoff, V1 preservation and planning. The **exact post-design V1 branch is now preserved** at `preservation/vip-v1-post-v2-design-20261009@3586eeaa904fc5a2e6a2745078611886f482f3de` ([preservation receipt](migrations/siglip2-post-completion/31_2026-10-09_V1_POST_DESIGN_BASELINE_PRESERVATION_RECEIPT.md)). The [detailed implementation plan](superpowers/plans/2026-10-09-vip-v2-siglip2-migration-implementation-plan.md) is **pending owner plan review and execution method selection**. Read the [eight-round VIP V2 SigLIP2 integration architecture spec](superpowers/specs/2026-10-09-vip-v2-siglip2-integration-design.md) and its [SO400M experiment-repository evidence handoff](https://github.com/Centaurioun/vip-siglip2-so400m-browser-spike/blob/main/docs/native/VIP_V2_INTEGRATION_EVIDENCE_HANDOFF_2026-10-09.md). The **written spec has subsequent owner approval for planning**; the implementation **plan requires owner review**, and no source-code/model/real-media execution is approved.

**Completed:** both documentary publications verified on main and exact post-design V1 Git ref preserved. **Next:** mandatory post-V1 refresh and readiness receipt -> review the written migration plan and select a repository-compliant execution method -> separately authorize specific code/model/media work. No upgrade execution has occurred. The historical “dormant preparation” heading below describes the pre-activation preparation package; current V1 completion evidence is in the living handoff.

## Dormant post-V1 SigLIP2 migration preparation

The post-completion SigLIP2 migration/benchmark package is **prepared but dormant**. It is not part of the current V1 Remaining Work execution frontier and does not authorize model acquisition, protected-media execution, migration implementation, Gate promotion, or full-archive indexing.

After V1 reaches a separately verified completion boundary, use this order:

1. [ADR-0002 — post-completion SigLIP2 migration and benchmark](decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md)
2. [Preparation-pack entrypoint](migrations/siglip2-post-completion/00_README_AND_ENTRYPOINT.md)
3. [Machine-readable package manifest](migrations/siglip2-post-completion/02_PACKAGE_MANIFEST.yaml)
4. [Post-completion refresh protocol](migrations/siglip2-post-completion/19_POST_COMPLETION_REFRESH_PROTOCOL.md)
5. [Post-completion refresh receipt template](migrations/siglip2-post-completion/30_post-completion-refresh-receipt-template.yaml)
6. [Six-cycle hardening audit](migrations/siglip2-post-completion/29_SIX_CYCLE_HARDENING_AUDIT.md)
7. [Three-way benchmark charter](benchmarks/siglip-three-way/B00_BENCHMARK_CHARTER.md)
8. [Benchmark pre-execution freeze checklist](benchmarks/siglip-three-way/B16_PRE_EXECUTION_FREEZE_CHECKLIST.md)

Current repository evidence always supersedes pre-completion snapshots. The refresh protocol must run before migration implementation planning resumes.

## Current repository-process reading order — Execution Portfolio

For native Codex thread discovery, coordinator messaging, fresh H3 creation, worktree binding, and monitoring, use the [Codex Native Thread Operations Runbook](architecture/CODEX_NATIVE_THREAD_OPERATIONS_RUNBOOK.md) alongside the governing protocols below. Its examples are not authority or permanent API schemas.

For ordinary Codex/DeepSeek repository execution, after the fresh-session project handoff read:

0. [Remaining Work controller entrypoint](../.orchestration/remaining-work/CONTROLLER_START_HERE.md) — read first for Remaining Work Atlas execution once present.
1. [Remaining Work Execution Atlas design](superpowers/specs/2026-10-03-remaining-work-execution-atlas-and-parallel-verification-design.md)
2. [Remaining Work Execution Atlas implementation plan](superpowers/plans/2026-10-03-remaining-work-execution-atlas-implementation-plan.md)
3. [Throughput-first development protocol](architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md)
4. [Subagent lane protocol](architecture/SUBAGENT_LANE_PROTOCOL.md)
5. [Remote durability and rolling-frontier orchestration protocol](architecture/REMOTE_DURABILITY_AND_TORRENT_ORCHESTRATION_PROTOCOL.md)
6. [Main-agent synchronization protocol](architecture/MAIN_AGENT_SYNC_PROTOCOL.md)
7. [Execution Portfolio resource policy v5](portfolio/portfolio-v1/resource-policy-v5.yaml)
8. [Historical Execution Portfolio orchestration design](superpowers/specs/2026-09-23-execution-portfolio-orchestration-design.md)

This is the current ordinary-development process order. Older Gate/audit/run documents remain evidence and may govern the historical task they document, but they do not reintroduce intermediate review/certification as the default current execution loop.

`portfolio/portfolio-v1/resource-policy-v3.yaml` and `portfolio/portfolio-v1/resource-policy-v4.yaml` remain preserved as superseded historical process evidence. Resource-policy v5 is the current authority for ordinary development resources and prerequisite/environment recovery.

## Gate-0 architecture/specification reading order

For a Gate-0 planning, remediation, review, or execution task, continue with:

6. [Main-agent synchronization protocol](architecture/MAIN_AGENT_SYNC_PROTOCOL.md)
7. [Subagent lane protocol](architecture/SUBAGENT_LANE_PROTOCOL.md)
8. [Gate-0 implementation specification v1.1](implementation-spec-v1.1.md)
9. [Gate-0 implementation specification v1.1.1 erratum](implementation-spec-v1.1.1-erratum.md)
10. [Gate-0 implementation plan](plans/2026-09-12-gate0-implementation.md)
11. [Gate-0 specification normalization review](audits/GATE0_SPEC_NORMALIZATION_REVIEW.md)
12. [Gate-0 experiment contract](architecture/GATE_0_EXPERIMENT_CONTRACT.md)
13. [Canonical contracts](architecture/CANONICAL_CONTRACTS.md)
14. [Architecture decision register](architecture/ASTRA_DECISION_REGISTER.md)
15. [Post-Astra six-cycle refinement](audits/POST_ASTRA_SIX_CYCLE_REFINEMENT.md)
16. [Architecture decision package](audits/ASTRA_ARCHITECTURE_DECISION_PACKAGE.md)
17. [Subagent lane six-cycle refinement](audits/SUBAGENT_LANE_PROTOCOL_SIX_CYCLE.md)
18. [Main-agent sync six-cycle refinement](audits/MAIN_AGENT_SYNC_PROTOCOL_SIX_CYCLE.md)

For the current Gate-0 implementation state, always prefer the current-state handoff plus
`docs/agent-runs/run-20260912-issue12/ledger.md`,
`docs/gate0/implementation-receipt.md`, and the Issue #12 whole-branch recertification
memos over older execution summaries.

## Experimental vertical-slice evidence

The following records preserve the local semantic-retrieval vertical-slice evidence,
including negative results, root-cause diagnostics, performance measurements, design
choices, execution failures/non-starts, terminal implementation evidence, bounded
real-media validation, target-scale exact-search measurements, exact-search metadata
optimization evidence, non-claims, and follow-up authority:

- [Single-video semantic retrieval spike findings](experiments/2026-09-15-single-video-semantic-retrieval-spike-findings.md)
- [Persistent local semantic index v1 execution evidence ledger](experiments/2026-09-15-persistent-local-semantic-index-v1-evidence.md)
- [Persistent local semantic index v1 terminal implementation reconciliation](experiments/2026-09-15-persistent-local-semantic-index-v1-terminal-implementation.md)
- [Persistent local semantic index v1 real-media + 320k scale reconciliation](experiments/2026-09-15-persistent-local-semantic-index-v1-real-media-and-320k-scale-reconciliation.md)
- [Persistent local semantic index v1 Attempt 4 metadata/result materialization reconciliation](experiments/2026-09-15-persistent-local-semantic-index-v1-attempt4-reconciliation.md)

The single-video throwaway implementation is historical evidence at commit
`0c14fce1fa979d466292fbd5cfd1e876bfacee92`, recoverable through
`archive/history/branch-preservation-v1`; its findings are summarized in the canonical
report above. The persistent-index planning authority is historical evidence at commit
`0a84753148938fccf3f786b070723dd57ca5a3fc`, recoverable through the same preservation
root. Its canonical evidence ledger is the execution history; the earlier approved spec
and plan paths remain on the preserved historical commit and are not asserted to exist on
current main. The experimental implementation/evidence head
`93f5d362091555937bf00ed221bb8dc24d656573` is likewise preserved through that root.
That branch has now accumulated synthetic implementation proof, a one-file bounded
real-media persistent-index smoke, a synthetic ~320k-row exact-search benchmark, and a
behavior-preserving metadata/result materialization optimization that reduced the measured
320k exact-search path from ~3,044 ms to ~47.7 ms while preserving exact outputs.
These evidence records do not promote a Gate, authorize broader protected/archive
execution, or make the experimental slices production architecture.

## Orchestration planning history

The current orchestration authority is
[the Execution Portfolio design](superpowers/specs/2026-09-23-execution-portfolio-orchestration-design.md).
The earlier planning lineage remains historical evidence at commit
`fd72fe2ad4401d64f50457dcb9c6b3ff6a106299`, recoverable through
`archive/history/branch-preservation-v1`.

The current repository handoff summarizes its accepted interpretation, but detailed
reasoning, independent critique, rejected alternatives, and post-Issue-12 reconciliation
remain planning-history evidence and should not be rewritten away.

A planning-branch document is not execution authorization merely because it exists.

## Architecture provenance and challenge history

Continue with, as needed:

19. [Astra six-cycle ledger](audits/ASTRA_SIX_CYCLE_LEDGER.md)
20. [Phase-0.5 evidence synthesis](audits/PRE_ASTRA_EVIDENCE_SYNTHESIS.md)
21. Phase-0.5 cross-critiques in `research/pre-astra/cross-critiques/`
22. Phase-0.5 stream memos in `research/pre-astra/`
23. Astra reviewer memos in `research/astra/`
24. [Astra architecture review brief](audits/ASTRA_ARCHITECTURE_REVIEW_BRIEF.md)
25. [Luna Gate-0 six-cycle ledger](audits/LUNA_GATE0_SIX_CYCLE_LEDGER.md)
26. [Authoritative v1.0 report](../Video_Intelligence_Pipeline_Raporu_v1.0.md)
27. [Phase-0 requirement traceability](audits/PHASE_0_REQUIREMENT_TRACEABILITY.md)
28. [Phase-0 six-cycle ledger](audits/PHASE_0_SIX_CYCLE_LEDGER.md)

## Reference-source evidence

Use this order:

29. [Reference manifest](../reference-pack/manifest.yaml)
30. Per-source `reference-pack/<id>/NOTES.md`
31. Selected `reference-pack/<id>/source/` files
32. `external/<id>/` only when a focused, recorded question requires full-source context

## Multi-agent execution history

For a current task, use its `docs/agent-runs/<run_id>/ledger.md` and lane memos after the
governing task has created them. These files are the durable detail surface; completed
child agents should not be asked to restate full work into the main chat context.

For every repo-working main-agent turn, synchronize canonical local `main` and
`origin/main` according to `architecture/MAIN_AGENT_SYNC_PROTOCOL.md`. Subagent lane
branches remain local by default and become remotely durable through controlled
integration, not by pushing one remote branch per child unless a governing task says
otherwise.

The v1.0 report remains preserved historical design authority for what was originally
proposed, but it is no longer the current architecture contract where later audited
decisions supersede it.

No reading order or handoff document itself authorizes real-archive execution, model
downloads, provider/cloud calls, external egress, later-Gate execution, destructive
cleanup, or production promotion.
