# VIP B-first B2 Stage A — independent operational readiness audit

**Date:** 2026-11-07 (Europe/Istanbul)  
**Disposition:** `STAGE_A_PLAN_SOURCE_VERIFIED`, `STAGE_A_FIRST_PUSH_BLOCKED_PENDING_EFFECTIVE_BRANCH_ACTOR_CONTROL_AND_EXPLICIT_OPERATIONAL_OWNER_GRANT`; `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`; `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.  
**Authority:** Read-only GitHub source and public official GitHub Actions documentation, plus documentation-only independent review. This is **not** an authorization to create a workflow, configure repository settings, generate video, upload/download artifacts, or push a producer branch.

## Independently verified repository facts

- LAB planned branch `design/vip-bfirst-b2-stage-a-issuance-execution-plan-20261106` at `c7761a274a432e658df4aee366b50bc900a985a4`, tree `f23b36f815bb054a81830ac1340e1ba5014828a9`, **direct parent** LAB main `5eab58ea2a5424424cb95f2690654b91395425df`. Exactly one new file relative to main: `docs/superpowers/plans/2026-11-06-vip-bfirst-b2-stage-a-issuance-workflow-execution-plan.md`.
- Canonical `main@3bfcc2ba221b36df6773e630b44479ec961d630a`, B-first source `feature/vip-bfirst-policy-observed-occurrence-repair-20261106@cac74495d80d9eaa144a12e9aa67eba78ba2f062`. Neither changed. LAB main unchanged. Two DO_NOT_DELETE backup releases independently returned `immutable=true`.
- GitHub repository metadata: `default_branch=main`, `visibility=private`, not archived. Five `.github/workflows/` YAMLs at the pinned Canonical source; none named `bfirst-pinned-video-issuance.yml`. Canonical recursive source tree has no pinned media in `tests/vip_fvs/fixtures/` (JSON recipes only).
- The proposed issuance ref `feature/vip-bfirst-video-issuance-20261106` was absent on GitHub at time of check. No Stage A artifact/run or source implementation candidate was inspected or claimed.
- GitHub ruleset collection has only `protect-main-canonical` active; its exact ruleset conditions include only `refs/heads/main` and have deletion/non-fast-forward/PR rules. The two portfolio-trust rulesets are disabled. **No active protection of the planned issuance branch was independently observed**.

## Source-plan evaluation

The Stage A execution plan is internally consistent about not silently pushing or self-authorizing a new workflow. It rejects `workflow_dispatch` for a new feature-only workflow and proposes a restricted `push` event with exact branch+paths, a first-step externally selected `BFIRST_B2_EXPECTED_PRODUCER_SHA` comparison against `github.sha` and `github.workflow_sha`, exact workflow/ref/event, and `run_attempt=1`. This matches GitHub's documented context and workflow-trigger semantics:
- https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow
- https://docs.github.com/en/actions/reference/workflows-and-actions/contexts
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow

**Hard qualification:** GitHub branch/path filters and a SHA comparison written *inside the same editable workflow* do not authenticate the first push by themselves. The named allowed issuer actor, branch creation/update controls, independently set repository variable and exact candidate SHA must all be effective and independently checked **BEFORE** a push that executes the workflow. Current main-only ruleset does not satisfy the issuance-branch gate. If required controls cannot be configured/verified, `BLOCKED_BRANCH_ACTOR_CONTROL` remains; no push.

The plan separately keeps publisher-reported run/job/artifact evidence from an independent artifact reviewer/pin record. The raw extracted MP4 SHA and the compressed GitHub artifact ZIP digest are separate values. An uploaded artifact is immutable while present but may expire or be deleted, so the proposed 90-day policy is a finite developer fixture and not a perpetual local-first archive:
- https://github.com/actions/upload-artifact
- https://docs.github.com/en/actions/tutorials/store-and-share-data
- https://docs.github.com/en/rest/actions/artifacts

## Unverified or conditional operational assertions

- The Codex worker **reports** `Actions enabled`, `allowed_actions=all`, `sha_pinning_required=false`, workflow token default `read`, `can_approve_pull_request_reviews=false`, artifact retention `days=90`, max `400`. The ChatGPT GitHub connector rejected the privileged `/actions/permissions` endpoint family, so these are *reported native API observations*, not independently reproduced here. Recheck with an authenticated, properly authorized administrative path before actual settings change or launch.
- The repository variable `BFIRST_B2_EXPECTED_PRODUCER_SHA` is not confirmed installed or read back. Branch actor/ruleset controls are **not configured or independently verified**. No verified full 40-character producer SHA yet exists.
- The exact hosted `ubuntu-24.04` FFmpeg/FFprobe binaries, versions and digests are `NOT_OBSERVED`. A future plan must distinguish pre-authorized accepted executable identity from a tool identity merely measured after first run. An unapproved executable cannot become trusted just because the producer hashed it itself. If policy requires a fixed pre-approved executable digest and there is no lawful preflight way to obtain it, stop for explicit trust-policy resolution rather than silently using a moving runner tool.
- GitHub Actions workflow syntax should be validated with a GitHub-compatible parser/`actionlint` if already available. PyYAML `safe_load` uses YAML 1.1 Boolean handling of `on`; a parser returning key `True` does not mean the GitHub `on:` event contract is correct. This is a future testing caveat, not proof the design is invalid.
- The proposed workflow's `push.paths` filter is **not** a safety boundary. Any later push changing an allowed path could trigger a new run; the SHA guard and externally enforced actor/ref controls must refuse it. Also check for other workflows that might execute on the feature push.
- Reported `NO_MATERIAL_FINDING` from a separate local design reviewer, matching 26 historical LAB verifier failures, and report-document SHA-256 are Codex-reported unless independently reproduced; the GitHub commit/tree/path claims above were independently reproduced.

## Owner decision and staged execution limits

An exact new **Owner operational approval** is required to authorize proposed Stage A source code, workflow and bounded real synthetic-media issuance, not an unrestricted future-action waiver. Suggested gates within one named authorization:

**Gate A1 — offline source/test candidate:** authorize a new clean isolated Canonical native worker based at `cac74495...`, only the proposed workflow+generator+unit-test paths, mock-only behavioral RED/GREEN, static code/source/secret review and a **pre-push independent reviewer**. No runnable workflow push, media generation, network artifact operation or repo setting mutation during A1.

**Gate A2 — administrator pre-push configuration and one-run issuance, CONDITIONAL:** only after a final exact producer commit SHA, clean reviewed isolated worktree, effective one-actor branch create/update protection and exact variable value are independently verified, authorize the named operator to configure `BFIRST_B2_EXPECTED_PRODUCER_SHA`, establish effective branch/actor controls and perform **one non-force push** to the exact feature ref. This triggers at most one intended run. Authorize that bounded GitHub Actions job to run installed FFmpeg/FFprobe only on generated `lavfi` frames (64×64, 10s, 4fps target, one MP4 <=65536 bytes), exact finite runner budgets, one artifact upload, no external inputs, model/provider, protected archive, package installation, secrets or production services. If conditions are not independently provable, NO push and `BLOCKED`.
  
**Gate A3 — independent evidence review, CONDITIONAL:** one authorized exact artifact API lookup and one download of its ZIP, no broad browsing/upload, independent hash+safe-member+decode+PTS/timebase verification, separate evidence branch receipts and reviewer-owned pin candidate. No producer self-approval, no automatic artifact reissue, no Stage B manifest registration or Stage C CLI update.

**Remaining separate decision:** Review of the actual artifact, live expiry/availability and adoption of the independent pin record for later Stage B. Do not label media E2E validated before these measurements.

**Terminal:** `BFIRST_B2_STAGE_A_PLAN_AUDITED_WITH_OPERATIONAL_GATES` · `FIRST_ISSUANCE_PUSH_BLOCKED_PENDING_OWNER_APPROVAL_AND_ACTOR_CONTROL` · `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED` · `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.
