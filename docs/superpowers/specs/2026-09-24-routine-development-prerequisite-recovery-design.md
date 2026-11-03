# Routine Development Prerequisite Recovery — Design v1

**Status:** OWNER-APPROVED DESIGN, PENDING POLICY IMPLEMENTATION  
**Date:** 2026-09-24  
**Scope:** repository-wide ordinary development execution policy  
**Owner intent:** routine, reversible development-environment failures must be repaired by the executing root rather than escalated as owner blockers.

## 1. Problem

Current execution policy combines two requirements that are individually reasonable but operationally conflict:

1. ordinary failures must enter systematic debugging and bounded remediation; and
2. Homebrew/pip/dependency installation and dependency download are generally unauthorized unless separately approved.

That combination causes trivial development-environment failures such as missing `numpy`, `pytest`, Pillow, test plugins, or equivalent ecosystem packages to terminate or distort otherwise-authorized Goals.

The desired behavior is not “install anything globally.” The desired behavior is:

- the root orchestrator owns development-environment continuity;
- children report missing prerequisites to the root instead of treating them as owner-level blockers;
- known project environments and caches are reused first;
- compatible project-local/shared environments may be repaired under serialized ownership;
- otherwise a Goal-local isolated environment may be created;
- ordinary package-registry network access required only for development dependencies is allowed;
- host-wide package-manager/system mutation remains outside routine authority;
- model/checkpoint downloads, provider/cloud execution, protected-media retrieval, credentials, destructive Git and narrower Gate prohibitions remain separate authority classes;
- TDD cannot treat an environment/import/collection failure as behavioral RED.

## 2. Design principles

### 2.1 Recovery before escalation

A missing routine prerequisite is ENABLE work, not by itself:

- `GOAL_BLOCKED_AUTHORIZATION`; or
- `GOAL_BLOCKED_EXTERNAL_PREREQUISITE`.

The root must execute the bounded prerequisite-recovery ladder before terminal escalation.

### 2.2 Root-owned environment continuity

Workers/subagents do not independently make owner-level decisions about environment repair.

On prerequisite failure a child returns, at minimum:

- exact blocked command;
- exact error;
- interpreter/runtime/environment used;
- missing import/package/tool/config;
- affected test/task.

The root either performs the repair itself or dispatches a bounded environment-repair worker.

### 2.3 Reuse before mutation

Recovery order is:

1. current Goal environment;
2. known project environments;
3. already-installed / already-cached compatible dependency;
4. serialized shared-project-environment repair;
5. Goal-local isolated environment creation/repair;
6. package installation/sync through the ecosystem-native project-local mechanism;
7. rerun the exact blocked command.

No unbounded host scan is implied.

### 2.4 Shared environment is a serialized mutable resource

A shared project environment such as repository `.venv` may be read concurrently but mutation requires a single `ENV_ADMIN` owner/lease.

Parallel roots must not concurrently mutate the same shared environment.

When shared mutation is unsafe, unavailable, version-incompatible, or unnecessary, a Goal-local environment is preferred.

### 2.5 Goal-local environments are routine reversible state

Creating and using a Goal-local virtual/dependency environment is ordinary development work and does not require owner approval when all of the following hold:

- it exists only to execute already-authorized code/tests/static checks/local-synthetic verification;
- it is project/user scoped;
- no elevated privilege is required;
- no protected media is retrieved;
- no provider/model service is called;
- no model/checkpoint/weights are downloaded;
- no system-wide package manager is invoked.

The environment is not committed merely for remote symmetry.

## 3. Routine development prerequisite definition

A `ROUTINE_DEV_PREREQ` is a package, runtime component, test dependency, build-time tool, non-secret configuration value, or deterministic local fixture required solely for already-authorized development or verification.

Examples include:

- Python packages: NumPy, pytest, pytest plugins, Pillow, torch as a Python package;
- Node project dependencies;
- Rust/Go ecosystem build/test dependencies;
- formatters, linters, type checkers and code generators;
- project-local CLI tools;
- missing package-manager environments;
- non-secret test environment variables;
- deterministic scratch directories;
- deterministic/reconstructible local test fixtures/config;
- project-local tool caches.

Not routine:

- provider/cloud API activity;
- model/checkpoint/weights acquisition;
- protected/archive-media retrieval;
- credentials/private-registry interaction;
- arbitrary unrelated network activity;
- `sudo`;
- Homebrew/apt/yum or equivalent system-wide package-manager mutation;
- kernel/driver/OS-security changes;
- destructive Git operations;
- production render/export;
- Gate promotion.

Installing a client SDK/library does not authorize using the corresponding remote service.

## 4. Network policy

Ordinary development Goals may use network access solely to retrieve `ROUTINE_DEV_PREREQ` packages from normal public package registries/CDNs through the selected ecosystem-native package manager.

Record when observable:

- requested package/tool;
- resolved version;
- package manager;
- target environment path;
- install/sync command;
- whether network retrieval occurred.

This network authority is narrowly scoped to dependency retrieval. It does not authorize provider/model activity, private registry access, model downloads, protected-media retrieval or unrelated browsing/scraping.

## 5. Ecosystem behavior

The policy is language-neutral.

Typical mechanisms:

- Python: `venv` + `pip` or `uv`;
- Node: project-local `npm`, `pnpm`, or `yarn`;
- Rust: `cargo` using project/user cache;
- Go: module download/build cache;
- equivalent ecosystem-native project/user-local mechanisms.

The root should prefer the repository-declared package manager/lockfile when one exists.

If no canonical environment manifest exists, a bounded Goal-local repair is allowed and must be recorded as environment state rather than silently treated as canonical dependency truth.

## 6. Reproducibility and dependency drift

An ad-hoc repair may unblock the current Goal.

If the completed capability genuinely depends on the newly supplied package/tool, record `NEW_DEV_DEPENDENCY` with:

- package/tool;
- resolved version;
- reason;
- owning capability;
- environment used;
- relevant test entrypoint.

Do not leave a permanent capability dependent only on accidental local state.

Promotion into a shared/canonical lock or manifest occurs only within an authorized write surface, normally during the current Goal if owned or during convergence/environment maintenance otherwise.

A root must not mutate a shared lockfile outside its write authority merely for convenience.

## 7. TDD semantics

Environment failures are not behavioral RED.

The following do **not** satisfy the RED step:

- `ModuleNotFoundError`;
- missing pytest;
- missing test runner;
- dependency-driven collection failure;
- broken PATH;
- missing routine tool;
- package import failure.

After environment recovery, the pre-implementation test must be rerun.

For a behavior change the required sequence remains:

`expected behavioral failure -> implementation -> GREEN`.

If implementation already happened before the environment was repaired, chronological TDD compliance must not be fabricated.

A bounded **test-efficacy recovery** is allowed:

1. use an isolated temporary/pre-change checkout or equivalent non-destructive mechanism;
2. apply/run the new test against the pre-implementation implementation;
3. observe the intended behavioral failure;
4. run the same test against the implementation head;
5. observe GREEN;
6. record:
   - test efficacy = VERIFIED;
   - original chronological RED = NOT_OBSERVED.

This repairs evidence quality without rewriting history.

## 8. Remediation budget interaction

Routine environment bootstrap/recovery is ENABLE work.

It does not consume one of the default three failed product-remediation generations unless the provisioning attempts themselves expose a genuine load-bearing technical root-cause family.

Malformed package-manager commands or environment setup attempts that never exercised the intended dependency resolution likewise do not count as behavior-changing remediation generations.

## 9. Escalation rule

A routine missing dependency/tool may become terminal only after the root documents that:

- bounded existing-environment reuse was attempted;
- cached/local reuse was attempted;
- authorized shared or Goal-local provisioning was attempted where applicable;
- the exact blocked command was retried;
- no authority-compliant recovery remains.

Immediate escalation is appropriate only when resolution requires a hard boundary such as:

- elevated/system-wide mutation;
- credentials or user interaction;
- private registry access;
- provider/cloud execution;
- model/checkpoint acquisition;
- protected/archive media;
- destructive/irreversible action;
- shared-contract mutation outside write authority;
- an explicit narrower Gate/spec/plan prohibition.

Independent READY work continues where possible.

## 10. Authority precedence

This repository-wide policy governs ordinary development execution only.

Explicit narrower authority remains stronger.

Therefore a Gate/task/spec/plan that explicitly forbids pip, dependency installation/download, network activity, environment provisioning, or another prerequisite action is not silently widened by this policy.

Gate-0 Revision-18 remains subject to its frozen narrower authority until separately amended.

## 11. Durable policy placement

Implementation will update the canonical process surface rather than relying on one file.

Required policy changes:

1. add `docs/portfolio/portfolio-v1/resource-policy-v4.yaml`;
2. update `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`;
3. update `docs/architecture/SUBAGENT_LANE_PROTOCOL.md`;
4. update `docs/project/03_CODEX_EXECUTION_BOOTSTRAP_HANDOFF.md`;
5. update `AGENTS.md`;
6. update `docs/INDEX.md`;
7. update current overlays in:
   - `docs/project/01_CURRENT_STATE_AND_HANDOFF.md`;
   - `docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md`;
8. add an implementation plan under `docs/superpowers/plans/`.

The v3 resource policy remains immutable historical process evidence. V4 becomes the current resource-policy reference once implemented and promoted.

## 12. Resource-policy-v4 machine concepts

V4 should carry machine-readable policy equivalent to:

- `routine_dev_prerequisite_recovery.policy = AUTO_RECOVER_WITHIN_AUTHORITY`;
- `environment_admin.shared_environment_mutation = SERIALIZED`;
- `goal_local_environment.creation_authorized = true`;
- `goal_local_environment.project_user_scope_only = true`;
- `routine_dependency_network.public_registry_retrieval_authorized = true`;
- `routine_dependency_network.provider_model_activity_authorized = false`;
- `system_package_manager.auto_mutation_authorized = false`;
- `model_checkpoint_download.auto_authorized = false`;
- `tdd.environment_failure_counts_as_behavioral_red = false`;
- `problem_remediation.environment_enable_work_consumes_product_generation = false`.

Exact field names may be refined in the implementation plan but semantics must remain unchanged.

## 13. Acceptance criteria

The policy change is complete only when a fresh root can determine, from canonical repository policy without chat history, that:

1. missing NumPy/pytest/Pillow/equivalent routine dependencies must trigger environment recovery rather than immediate owner escalation;
2. the root owns repair and children report the prerequisite failure upward;
3. compatible shared project environments may be reused and serializedly repaired;
4. Goal-local environments may be created automatically;
5. public package-registry network use for routine development dependencies is allowed;
6. Homebrew/system-wide mutation remains outside automatic authority;
7. model weights/provider execution/protected media remain unauthorized by dependency-recovery authority;
8. environment/collection failure is not behavioral RED;
9. test-efficacy recovery may verify a test post hoc without pretending chronological TDD compliance;
10. narrower Gate/task authority still overrides this general policy.

## 14. Immediate follow-up after policy promotion

After this policy is implemented and verified, the first bounded remediation target is:

`root-multisource-operational-path / goal-20260924-multisource-path`

The remediation must address the recorded state:

- implementation tests were authored before implementation;
- initial test collection failed because NumPy was absent in the first environment;
- no intended behavior RED was therefore observed before implementation;
- later focused verification passed.

The follow-up will provision/reuse an authority-compliant environment, run the new multi-source test against the pre-implementation code head and the implementation code head, and durably record test efficacy without rewriting historical chronology.

No capability redesign is implied by that follow-up.
