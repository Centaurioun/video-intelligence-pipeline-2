# Routine Development Prerequisite Recovery Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Promote the owner-approved routine development prerequisite recovery design into canonical repository execution policy so ordinary missing development/test prerequisites are automatically recovered within authority instead of becoming premature owner blockers.

**Architecture:** Add resource-policy v4 as the machine-readable source for environment/prerequisite recovery, then project the same semantics into the human-readable execution protocols and fresh-session handoffs. Preserve resource-policy v3 as historical evidence, preserve narrower Gate/task authority precedence, and make current-index/handoff references unambiguous so fresh roots do not follow stale “dependency install always requires separate approval” language.

**Tech Stack:** Markdown process contracts, YAML machine-readable resource policy, GitHub protected-main PR workflow.

**Spec:** `docs/superpowers/specs/2026-09-24-routine-development-prerequisite-recovery-design.md`

## Global Constraints

- Routine development prerequisite recovery is ordinary ENABLE work for ordinary development Goals.
- Reuse the current Goal environment, known project environments, and compatible cached dependencies before provisioning.
- Shared project-environment mutation requires serialized `ENV_ADMIN` ownership.
- Goal-local project/user-scoped environments may be created or repaired without owner approval.
- Public package-registry/CDN network access is authorized only for routine development dependency retrieval.
- Homebrew/apt/yum/sudo/system-wide mutation remains outside automatic authority.
- Provider/model API activity, model/checkpoint/weights acquisition, protected/archive-media retrieval, credentials/private registries, destructive Git, production render/export, Gate promotion, and unrelated network activity remain outside this authority.
- Environment/import/collection failures do not count as behavioral RED.
- Post-hoc test-efficacy recovery may verify test efficacy but must retain chronological RED as `NOT_OBSERVED`.
- Routine environment ENABLE work does not consume the product remediation-generation budget unless it becomes a genuine load-bearing technical root-cause family.
- Explicit narrower Gate/task/spec/plan authority overrides this general policy.
- Gate-0 Revision-18 remains under its existing frozen narrower no-install/no-download authority unless separately amended.
- Preserve `docs/portfolio/portfolio-v1/resource-policy-v3.yaml` unchanged as historical evidence.
- Do not mutate canonical `main` directly; use the protected-main PR.

## Review Focus

- A child sees `ModuleNotFoundError`: it must return prerequisite evidence to the root; the root must attempt recovery rather than classify owner blocker.
- Two roots need the same shared `.venv`: reads may coexist but mutation must serialize under `ENV_ADMIN`; Goal-local environments remain independently creatable.
- A package install needs public PyPI/npm/crates traffic: dependency retrieval is allowed, but SDK installation must not imply provider/API execution authority.
- A dependency transitively wants a model/checkpoint or system package: ordinary recovery must stop at that narrower hard boundary and continue independent READY work.
- A test collected only after environment repair: the environment failure is not RED; behavioral RED must be rerun, or post-hoc efficacy must explicitly keep chronological RED `NOT_OBSERVED`.

---

### Task 1: Add machine-readable resource policy v4

**Files:**
- Create: `docs/portfolio/portfolio-v1/resource-policy-v4.yaml`
- Preserve unchanged: `docs/portfolio/portfolio-v1/resource-policy-v3.yaml`

**Interfaces:**
- Consumes: resource-policy v3 concurrency/model/remediation semantics.
- Produces: current machine-readable `routine_dev_prerequisite_recovery`, `environment_admin`, `goal_local_environment`, `routine_dependency_network`, `system_package_manager`, `model_checkpoint_download`, and TDD/remediation environment semantics.

- [ ] **Step 1: Create v4 by carrying forward every v3 policy field unchanged unless this design explicitly supersedes it**

Use `schema_version: 4` and `portfolio_epoch: execution-portfolio-v1`.

- [ ] **Step 2: Add exact prerequisite-recovery policy**

The v4 YAML must include semantics equivalent to:

```yaml
routine_dev_prerequisite_recovery:
  policy: AUTO_RECOVER_WITHIN_AUTHORITY
  missing_prerequisite_is_terminal_by_default: false
  root_owns_environment_continuity: true
  child_reports_to_root: true
  recovery_order:
    - CURRENT_GOAL_ENVIRONMENT
    - KNOWN_PROJECT_ENVIRONMENTS
    - COMPATIBLE_LOCAL_OR_CACHED_DEPENDENCY
    - SERIALIZED_SHARED_PROJECT_ENVIRONMENT
    - GOAL_LOCAL_ENVIRONMENT
    - PROJECT_LOCAL_INSTALL_OR_SYNC
    - RETRY_BLOCKED_COMMAND

environment_admin:
  shared_environment_mutation: SERIALIZED
  concurrent_shared_environment_read: true
  worker_direct_shared_environment_mutation: false

goal_local_environment:
  creation_authorized: true
  repair_authorized: true
  project_user_scope_only: true
  elevated_privilege_allowed: false
  commit_environment_artifacts: false

routine_dependency_network:
  public_registry_retrieval_authorized: true
  scope: ROUTINE_DEV_PREREQ_ONLY
  provider_model_activity_authorized: false
  model_checkpoint_download_authorized: false
  protected_media_retrieval_authorized: false
  private_registry_credentials_authorized: false
  unrelated_network_activity_authorized: false

system_package_manager:
  automatic_mutation_authorized: false
  sudo_authorized: false
  homebrew_mutation_authorized: false

model_checkpoint_download:
  automatic_authorization: false

tdd:
  environment_failure_counts_as_behavioral_red: false
  test_efficacy_recovery_authorized: true
  chronological_red_may_be_rewritten: false

problem_remediation:
  default_failed_generation_limit_per_root_cause_family: 3
  park_affected_descendants_after_exhaustion: true
  continue_independent_ready_work: true
  environment_enable_work_consumes_product_generation: false
```

Exact YAML key naming may use the above directly; semantics may not be weakened.

- [ ] **Step 3: Validate YAML syntax and v3 preservation**

Validation:
- parse v4 with an available YAML parser if present;
- otherwise perform a strict structural/manual check without installing a parser solely for policy validation;
- verify v3 blob is unchanged.

Expected: v4 parses/has expected keys; v3 blob unchanged.

- [ ] **Step 4: Commit**

```bash
git add docs/portfolio/portfolio-v1/resource-policy-v4.yaml
git commit -m "policy: add routine prerequisite recovery resource policy"
```

---

### Task 2: Promote root/child recovery semantics into execution protocols

**Files:**
- Modify: `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`
- Modify: `docs/architecture/SUBAGENT_LANE_PROTOCOL.md`

**Interfaces:**
- Consumes: resource-policy-v4 machine semantics.
- Produces: root-owned recovery flow and child prerequisite handoff behavior.

- [ ] **Step 1: Update throughput protocol current resource authority**

Replace current references to `resource-policy-v3.yaml` as the current resource authority with `resource-policy-v4.yaml`, while retaining historical references only when explicitly labeled historical.

- [ ] **Step 2: Add Routine Development Prerequisite Recovery section**

The section must define:

```text
child prerequisite failure
-> preserve exact failure evidence
-> return prerequisite record to root
-> root systematic-debugging classification
-> recovery ladder
-> rerun exact blocked command
-> behavioral RED/fix/GREEN where applicable
-> only then park/escalate if no authority-compliant recovery remains
```

It must state:
- routine prerequisite failure is ENABLE work;
- root owns environment continuity;
- environment bootstrap does not consume product repair budget;
- public package-registry dependency retrieval is permitted within v4 scope;
- shared environment mutation requires `ENV_ADMIN`;
- Goal-local environments are an automatic fallback;
- system/model/provider/protected-media/narrower-authority boundaries remain closed.

- [ ] **Step 3: Update subagent protocol**

A child handoff on environment failure must include:

```text
PREREQUISITE_STATUS
BLOCKED_COMMAND
ERROR
INTERPRETER_OR_RUNTIME
ENVIRONMENT_PATH
MISSING_PREREQUISITE
AFFECTED_TEST_OR_TASK
LOCAL_OR_CACHED_RECOVERY_OBSERVED
ROOT_ACTION_REQUIRED=ENVIRONMENT_RECOVERY
```

Children must not independently classify a routine dependency as owner authorization blocker.

Workers must not mutate a shared project environment directly; root/`ENV_ADMIN` owns that mutation.

- [ ] **Step 4: Add TDD environment-failure semantics**

State explicitly:
- import/collection/missing-tool failure != behavioral RED;
- environment recovery must precede behavioral RED observation;
- if implementation preceded recovery, use non-destructive test-efficacy recovery and retain chronological RED=`NOT_OBSERVED`.

- [ ] **Step 5: Mechanical validation**

Search both files for contradictory current statements such as:
- routine dependency install always requires separate owner authorization;
- missing pytest is automatically external prerequisite;
- child may mutate shared env concurrently.

Expected: no unqualified contradiction remains; narrower explicit Gate restrictions remain intact.

- [ ] **Step 6: Commit**

```bash
git add docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md docs/architecture/SUBAGENT_LANE_PROTOCOL.md
git commit -m "policy: make roots recover routine development prerequisites"
```

---

### Task 3: Update fresh-session and repository-level authority surfaces

**Files:**
- Modify: `docs/project/03_CODEX_EXECUTION_BOOTSTRAP_HANDOFF.md`
- Modify: `AGENTS.md`
- Modify: `docs/INDEX.md`

**Interfaces:**
- Consumes: v4 + updated execution/subagent protocols.
- Produces: unambiguous fresh-session/bootstrap authority.

- [ ] **Step 1: Update bootstrap handoff governing policy list**

Make `resource-policy-v4.yaml` the current resource-policy reference.

Preserve v3 only as superseded historical process evidence.

- [ ] **Step 2: Replace the ordinary-development dependency prohibition**

The general boundary must no longer say, without qualification:

`Homebrew/pip/dependency installation unless separately authorized`.

Replace it with semantics that distinguish:
- routine project/user-local dependency recovery = authorized under v4;
- Homebrew/system-wide mutation = not automatically authorized;
- provider/model/checkpoint/protected-media/private-registry = not authorized by v4;
- Gate-0 Rev18 narrower no-install/no-download authority remains unchanged.

- [ ] **Step 3: Add root environment-continuity rule to AGENTS.md**

Add concise canonical rules:

```text
- Routine missing development/test prerequisites are ENABLE work, not terminal blockers by default.
- Child reports exact prerequisite failure to root.
- Root owns recovery through resource-policy-v4.
- Shared environment mutation is ENV_ADMIN-serialized.
- Goal-local project/user environments and public-registry routine dependency retrieval are allowed.
- Environment failure is not TDD RED.
- Explicit narrower authority wins.
```

- [ ] **Step 4: Update docs/INDEX.md**

Point the current execution process order to `resource-policy-v4.yaml`.

Where v3 is mentioned historically, label it superseded/historical rather than current.

- [ ] **Step 5: Mechanical contradiction scan**

Search these three files for current unqualified phrases:
- `Homebrew/pip/dependency installation unless separately authorized`
- `venv provisioning/dependency download unless separately authorized`
- current `resource-policy-v3.yaml` authority references.

Expected:
- no ordinary-development contradiction;
- Gate-0-specific narrower prohibition may remain explicitly scoped to Gate-0;
- current process order names v4.

- [ ] **Step 6: Commit**

```bash
git add AGENTS.md docs/INDEX.md docs/project/03_CODEX_EXECUTION_BOOTSTRAP_HANDOFF.md
git commit -m "policy: expose prerequisite recovery to fresh execution roots"
```

---

### Task 4: Update current project-state overlays

**Files:**
- Modify: `docs/project/01_CURRENT_STATE_AND_HANDOFF.md`
- Modify: `docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md`

**Interfaces:**
- Consumes: promoted policy v4.
- Produces: current project overlays that do not send fresh sessions back to v3/old dependency authority.

- [ ] **Step 1: Add a top current/superseding overlay to 01**

The overlay must state:
- resource-policy v4 supersedes v3 for current ordinary development;
- routine prerequisite recovery is automatic within authority;
- shared env mutation is serialized; Goal-local env creation is allowed;
- routine public-registry dependency retrieval is allowed;
- system/model/provider/protected-media boundaries remain separate;
- Gate-0 Rev18 frozen narrower authority remains unchanged.

Do not rewrite historical sections.

- [ ] **Step 2: Add/update top current/superseding overlay in 02**

Record the same authority transition as an execution-policy update and make future root/task-packet generation consume v4.

- [ ] **Step 3: Validate overlay precedence**

A fresh reader following the top/current overlay must not infer v3 is still the current resource policy.

- [ ] **Step 4: Commit**

```bash
git add docs/project/01_CURRENT_STATE_AND_HANDOFF.md docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md
git commit -m "docs: advance current state to resource policy v4"
```

---

### Task 5: Repository-wide policy consistency and protected-main integration

**Files:**
- Verify all files changed in Tasks 1–4.
- Update PR #13 metadata if needed.

**Interfaces:**
- Consumes: complete policy branch.
- Produces: canonical current policy on protected `main`.

- [ ] **Step 1: Run targeted repository policy search**

Search for all current references to:
- `resource-policy-v3.yaml`;
- `dependency installation unless separately authorized`;
- `venv provisioning/dependency download unless separately authorized`;
- `Homebrew/pip`.

Classify every occurrence as:
- current ordinary-development policy — must be v4-compatible;
- explicit narrower Gate/task historical authority — preserve;
- historical run evidence — preserve.

Do not indiscriminately rewrite historical evidence.

- [ ] **Step 2: Verify required files**

Require:
- design spec exists;
- implementation plan exists;
- v4 exists;
- v3 unchanged;
- throughput protocol points to v4/current semantics;
- subagent protocol carries child->root prerequisite handoff;
- bootstrap handoff points to v4/current semantics;
- AGENTS has root environment-continuity rules;
- INDEX names v4;
- current 01/02 overlays name v4.

- [ ] **Step 3: Verify branch diff**

Require branch diff from original main `b54f6e2d19cb8b080477669705c115865553034c` to contain only policy/docs files authorized by this plan.

Run/inspect:
- changed paths;
- whitespace/diff checks where supported;
- secret scan/workspace verifier where appropriate, classifying known unrelated baseline failures rather than hiding them.

- [ ] **Step 4: Update PR #13 out of draft when implementation is complete**

PR description must identify:
- owner-approved spec;
- resource-policy v4;
- preserved narrower Gate-0 authority;
- no product/runtime code change.

- [ ] **Step 5: Merge through protected-main PR workflow**

Merge only after:
- PR head equals verified policy head;
- required review-thread resolution is satisfied;
- protected-main rules allow merge;
- no force/bypass outside the configured PR-only path is used.

Expected merge method: repository-allowed merge commit.

- [ ] **Step 6: Post-merge verification**

Fetch/verify:
- PR merged;
- `main` advanced;
- main contains v4 and all policy projections;
- branch protection remains active;
- product execution branches are unchanged.

- [ ] **Step 7: Record immediate R3 follow-up**

Do not mutate R3 during policy promotion.

After canonical promotion, generate a bounded R3 remediation instruction to:
- recover/reuse an authority-compliant environment;
- exercise the multi-source test against pre-implementation code;
- observe intended behavioral RED;
- run same test at capability code head and observe GREEN;
- record `test_efficacy=VERIFIED`;
- retain `chronological_red=NOT_OBSERVED`;
- update durable R3 Problem/handoff without redesigning capability.

---

## Self-review

- **Spec coverage:** every design section maps to Tasks 1–5; no requirement is intentionally omitted.
- **Placeholder scan:** no TBD/TODO/“implement later” placeholders remain.
- **Type/key consistency:** resource-policy-v4 concepts use one vocabulary across Task 1 and downstream projections.
- **Review Focus coverage:** child escalation, ENV_ADMIN serialization, public-registry-vs-provider boundary, transitive hard-boundary behavior, and TDD RED semantics are all explicitly validated.
- **Historical integrity:** v3 and historical run/Gate evidence are preserved rather than rewritten.
- **Main safety:** all canonical integration occurs through protected PR #13; no direct main mutation is planned.
