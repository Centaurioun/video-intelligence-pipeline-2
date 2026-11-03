# DeepSeek Harness Controller Profile — Execution Portfolio v1

**Status:** CURRENT DEEPSEEK EXECUTOR PROFILE  
**Scope:** DeepSeek Harness used as an Execution Portfolio root/controller.  
**Common orchestration authority:** `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`  
**Current resource authority:** `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`

Historical Gate-specific DeepSeek controller branches, evidence, and `resource-policy-v2.yaml` remain historical provenance. This profile does not rewrite their past model or resource settings.

## 1. Model and reasoning policy

DeepSeek retains the currently verified executor-specific policy unless the owner explicitly replaces it.

Current policy:

- parent/root: `deepseek-flash` with reasoning `high`;
- child `off`: deterministic/mechanical collection or verification only;
- child `low`: default for bounded straightforward implementation/analysis;
- child `high`: architecture, systematic debugging, security/adversarial work, evidence reconciliation, synthesis, complex implementation;
- child `max`: prohibited by default and requires explicit owner authorization.

A child assigned `off` or `low` that discovers materially harder reasoning must stop with `ESCALATION_REQUIRED`; the parent may respawn that scope as a fresh `high` child.

Do not silently self-escalate.

Do not inherit Codex LUNA policy.

## 2. Required root preflight

Before substantive work:

- verify correct repository/worktree/branch;
- fetch/compare current origin/main;
- verify assigned execution branch/remote state;
- bind exact Goal/portfolio base or anchor SHA;
- read current project handoff;
- read throughput, lane, durability, sync, and current resource-v5 policy;
- verify subagent backend if delegation is intended;
- verify nested child delegation separately if Area Leads are expected to spawn Workers;
- verify current model/reasoning identities through supported runtime metadata when possible;
- verify heavy-resource lease state before heavy execution.

Failure to verify a preferred capability does not automatically block the Goal when the policy defines a safe fallback.

## 3. Root role

The root is primarily:

`CONTROLLER -> SCHEDULER -> DEPENDENCY MANAGER -> MILESTONE-BRANCH INTEGRATOR -> VERIFIER`

Keep root live context bounded.

Delegate substantive work whenever clean ownership exists.

Use repository/Git state rather than conversation history as durable memory.

## 4. Goal semantics

One root handles one milestone Goal at a time.

Goal means useful product milestone, not a micro-task.

Continue through:

- ordinary child completion;
- ordinary test failure;
- ordinary repair attempts;
- newly opened READY work.

Return only at the terminal conditions defined by the throughput/durability protocols.

## 5. Delegation

Preferred topology:

`Root -> Area Lead -> Worker`

only when compliant nested delegation is positively supported.

Otherwise flatten to:

`Root -> Workers`

Child task packets are self-contained and bind:

- Goal/lane ID;
- exact BASE_SHA;
- task;
- read/write scope;
- model/reasoning;
- tests;
- contract refs;
- Problem IDs;
- durable state path.

## 6. Writer isolation

One active writer controller per exact branch.

Writer children require:

- exclusive path ownership; or
- isolated child branch/worktree.

A DeepSeek root never writes another active root's branch.

DeepSeek and Codex may both participate in a portfolio only on separately assigned branches/worktrees.

No executor takeover of an active writer branch without explicit durable handoff.

## 7. Rolling frontier

Continuously:

`verify authority -> discover READY -> allocate ownership -> delegate -> collect -> stale-base/contract check -> integrate/park -> persist -> close -> refill`

Do not manufacture duplicate work.

Do not leave useful READY capacity idle while the root performs delegable work.

## 8. Durable state

Code/tests live in commits.

Scheduler/problem state is compact and machine-readable.

Terminal children return compact handoffs.

Long per-child Markdown essays are not required for ordinary execution.

Historical lane memos remain historical evidence.

## 9. Failure handling

Use systematic-debugging.

Behavior changes use TDD where applicable.

Default maximum:

three evidence-supported failed repair generations for the same load-bearing Problem/root-cause family.

After exhaustion:

- persist Problem state;
- park affected descendants;
- continue independent READY work;
- return only if the remaining Goal is actually blocked.

## 10. Resource limits

DeepSeek child count does not expand heavy-resource authority.

Current resource-v5 policy distinguishes:

- adaptive logical root/child writers;
- serialized worktree administration;
- heavy local execution lease;
- FFmpeg/model-heavy lease;
- canonical-main integration budget.

Current ordinary-development starting leases:

- HEAVY_CPU max concurrent = 2, calibrating to 3 when stable/useful;
- FFMPEG_HEAVY max concurrent = 2, calibrating to 3 when stable/useful;
- MODEL_MPS is calibrated separately and requires an already-authorized local model/runtime;
- ENV_ADMIN and canonical-main integration remain serialized at 1.

A heavy-resource failure lowers only the affected lease class; it does not globally serialize lightweight logical work.

## 11. Review/certification epoch

Ordinary execution does not allocate reviewer/certifier swarms.

Reviewer/certifier swarms and reviewer-after-every-inner-task loops are not ordinary execution. Every BUILD_GREEN H3 feature candidate still enters an asynchronous VERIFY code-review lane before convergence/current-main integration; independent BUILD continues unless a true HARD_VERIFY dependency exists.

Broader formal certification remains deferred to the later owner-directed final epoch. Verification, tests, systematic-debugging, and evidence discipline remain mandatory.

## 12. Evidence discipline

Subagent assertions are candidate state until checked against repository/runtime artifacts needed for the claimed fact.

Canonical evidence classes remain:

- MEASURED;
- MATCHED;
- VISUALLY_OBSERVED;
- AUDIO_OBSERVED;
- EDITORIAL_INFERENCE.

`NOT_OBSERVED` remains an availability/state marker.

Do not upgrade evidence strength silently.

## 13. Main boundary

DeepSeek execution roots never merge canonical main.

Canonical-main integration requires explicit owner authorization for the exact integrated state.

## Routine development prerequisite recovery

Routine development prerequisite recovery follows resource-policy v4 and the common throughput/subagent protocols.

A missing ordinary development/test dependency is ENABLE work rather than a terminal owner blocker by default. Children report exact prerequisite evidence to the Harness root; the root owns recovery. Shared project-environment mutation is serialized under `ENV_ADMIN`; Goal-local project/user-scoped environments and public-registry retrieval for routine dependencies are allowed within v4.

This does not authorize system-wide package-manager mutation, provider/model activity, model/checkpoint acquisition, protected media, credentials/private registries, or any action forbidden by a narrower Gate/task authority.
