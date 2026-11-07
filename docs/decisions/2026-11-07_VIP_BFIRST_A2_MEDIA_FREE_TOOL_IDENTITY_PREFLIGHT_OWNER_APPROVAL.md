# VIP — B-first A2 media-free FFmpeg/FFprobe identity preflight owner approval

**Date:** 2026-11-07 (Europe/Istanbul)
**Disposition:** OWNER APPROVED — ONE BOUNDED MEDIA-FREE TOOL-BYTE MEASUREMENT PREFLIGHT, CONDITIONAL ON PRE-PUSH SOURCE/ACTOR/BRANCH/TRIGGER CONTROLS.
**Not approved:** A2 production issuance push/run, MP4 generation, artifact upload/download, FFmpeg/FFprobe execution, Stage B/C, real/protected media/model/provider, Gate promotion or main merge.

## Exact explicit approval provenance

Following the independently reviewed question:

> "Standart GitHub-hosted runner'ın mevcut ağ erişimini açık bir artık risk olarak kabul ederek, yalnızca medya içermeyen, bağımsız incelenmiş ve tek yetkili ölçümle sınırlandırılmış Strategy B preflight operasyonunu onaylıyor musun?"

The Repository Owner explicitly replied: **"Onaylıyorum."**

This approval accepts two precisely scoped residual risks:

1. **Ordinary GitHub-hosted runner egress remains available**; workflow `permissions: {}` constrains `GITHUB_TOKEN` only and is NOT network isolation. Review must ensure workflow code has no purposeful HTTP/egress, checkout, package install, remote media or external provider. No claim is made against malicious hosted runner or a malicious GitHub administrator.
2. **A platform rerun might be scheduled**, despite the limit of one authorized measurement body. The first workflow step must reject `github.run_attempt != 1` before any executable-byte read; a later run attempt may exist and must be recorded as an unauthorized platform attempt, not mistaken for a second approved measurement. The owner does NOT require proving that the platform is technically incapable of scheduling a rerun.

No additional network traffic beyond unavoidable hosted-runner control-plane communication is intentionally authorized. No tokens, secrets or extra egress are granted. This is low-assurance, locally controlled **synthetic developer diagnostic** work, not a high-assurance isolated-execution certification.

## Pinned documentary and source authority

- Canonical repository: `Centaurioun/video-intelligence-pipeline`; allowed frozen source starting point: B-first candidate `cac74495d80d9eaa144a12e9aa67eba78ba2f062`, tree `1e851b89273e7ae9a580643b8b704a2d5945c099`. Canonical main `3bfcc2ba221b36df6773e630b44479ec961d630a` read-only.
- LAB repository: `Centaurioun/video-intelligence-pipeline-2`; LAB main `5eab58ea2a5424424cb95f2690654b91395425df` read-only.
- Strategy B design: LAB Git commit `58482251020713ccb4053ce14a98506739e3ed27`, `docs/superpowers/specs/2026-11-07-vip-bfirst-a2-ffmpeg-ffprobe-tool-identity-preflight-design.md`. Its **commit and file are VERIFIED** by GitHub, but its originally claimed remote branch was **NOT_FOUND** in an independent ref lookup; do not infer why or mutate history to 'fix' this.
- Independent feasibility audit: LAB commit `89c67a1602442b42887c1328a50be57c3f832e0b`, `docs/reviews/2026-11-07-vip-bfirst-a2-tool-identity-preflight-independent-feasibility-audit.md`.
- Existing A1 producer: local-only **REPORTED** commit `413d032e5635e4d8670e5565856f7fcfcfaca3ff`, tree `589ef2a0119a339fba5cfd5603c608a6f7792b3c`; it is absent from GitHub; it and its worktree must remain untouched and unpushed. Existing issuance branch `feature/vip-bfirst-video-issuance-20261106` remained NOT_FOUND in GitHub. Canonical ruleset `26738994` applies to that issuance branch, NOT the new preflight branch.
- Existing Stage A operational grant: LAB `af8b1de7286095e8ed86a3fb11e08006cdcdf8ec` remains strictly conditional. The extra preflight is an independently scoped addition, NOT one of its single production issuance runs.
- Two immutable DO_NOT_DELETE backup GitHub releases were independently rechecked `immutable=true`.

## Exactly authorized preflight source and offline TDD

**New isolated Canonical native worker**, one exclusive writer in a clean worktree based at the frozen B-first candidate. Proposed uniquely owned local/remote branch `design/bfirst-a2-tool-identity-preflight-20261107`.

**Exclusive source-write path:** `.github/workflows/bfirst-tool-identity-preflight.yml` (one new GitHub Actions YAML file). Do not write generator code, the existing A1 source, fixtures, other workflows, GitHub main, code contracts or other source paths. Any absolutely necessary test code beyond this file must be separately scoped, not silently invented.

Before the branch is pushed: use a **locally working static GitHub Actions YAML validation** and deterministic prospective RED/GREEN contract check where feasible without extra source writes; if robust behavioral test requires new test source paths, stop for narrowly authorized path revision. No actual FFmpeg/FFprobe invocation in any phase; even `-version` is forbidden for this preflight.

Workflow design:
- `on: push` restricted to EXACT `refs/heads/design/bfirst-a2-tool-identity-preflight-20261107` branch with narrow path filter only for `.github/workflows/bfirst-tool-identity-preflight.yml`, no `workflow_dispatch`, `schedule`, `workflow_call`, PR, reusable caller, or extra trigger.
- Job `permissions: {}`, no secrets, no checkout, no GitHub Actions marketplace actions, no package downloads/installs, no artifact upload/download or cache, no manual cloud/provider requests, no media source.
- One `ubuntu-24.04` hosted job, no matrix/retry/fanout, finite 5-minute timeout, bounded output; no privileged containers, no sudo, no API calls from the workflow.
- First step validates exact `github.repository`, `github.event_name=push`, full `github.ref`, `github.workflow_ref`, `github.sha` and `github.workflow_sha` against an externally selected full producer/preflight commit SHA from `BFIRST_B2_TOOL_PREFLIGHT_EXPECTED_SHA`, and `github.run_attempt == 1`, **before reading either executable**.
- The only intended host data read after guard is PATH resolution and bounded read-only stat/hash of the selected FFmpeg and FFprobe executable bytes, plus local runner-image, OS and package metadata. Do not run the executables, including `-version`, `-encoders` or `-buildconf`. No network commands. Capture resolved real paths, regular-file type, size, SHA-256, `ImageOS`, `ImageVersion`, UTC time, architecture, package origin/version where available and missing fields as `NOT_OBSERVED`. `mpeg4` codec support stays `NOT_OBSERVED`.
- Return a bounded textual job summary/log only; **NO artifacts or receipts uploaded**. The workflow may create ordinary GitHub-hosted runner job logs/summary inherent to Actions.
- No claim that the measured bytes are permanently stable, source-signed or that later producer uses the same runner. The future production A2 must separately hash actual binaries and refuse mismatches BEFORE executing FFmpeg/FFprobe.

## Exact pre-push conditional operational gates

1. Fresh Canonical source governance, native tool schema, writer ownership and frozen SHA/tree; inspect ALL current Canonical workflow push triggers for the planned feature branch, indirect downstream triggers and required concurrency/resource limits. No LAB workflow census substituted for Canonical.
2. Complete the preflight YAML in an **isolated local branch and unpushed commit**; independently review the exact immutable candidate SHA/tree using a separate **clean read-only reviewer**. Verify the workflow actually does zero media/tool execution and has no intentional network operations or tokens/secrets.
3. A separately authorized administrator creates a **narrow active ruleset** enforcing actor-controlled creation/update of ONLY the named preflight branch, and independently verifies exact included ref, rules and permitted actor. Do not change existing ruleset `26738994` or main protections.
4. Administrator sets the non-secret repository variable `BFIRST_B2_TOOL_PREFLIGHT_EXPECTED_SHA` to the exact reviewed 40-char preflight commit, then independently reads it back; verify actual pusher's identity and safe branch state. The source SHA remains fixed after review.
5. Recheck immediately before push: active preflight ref controls, expected variable, exact GitHub workflow filters/source, no other automatic workflows, token settings, and explicit one intended first-attempt run. If a relevant condition is unproven, mark `BLOCKED` and **NO PUSH**. The owner has accepted standard runner egress availability and the possibility that GitHub can schedule reruns, but not arbitrary extra jobs or second measurement bodies.
6. Only after every pre-push gate passes: one **normal non-force push** of exact candidate to the named preflight branch, initiating the one intended first-attempt GitHub-hosted metadata/hash job. No retry, rerun, amended source SHA or second producer push is authorized. An unexpected attempt must self-refuse before bytes read and be independently recorded.
7. Independent reviewer validates live `run_id`, numeric job ID when retrievable through approved read-only API, event/ref/source/workflow SHA/attempt, bounded logs/summary and measured executable-byte digests plus runner identity. Record independent review in an isolated LAB documentation-only audit branch; no producer self-approval.
8. **STOP after reviewed candidate tool digest pair**. The owner has NOT yet approved those exact as-yet-unknown digest values, tool-hash Actions variables, production A2 issuance push, stage A3 artifact download, media generation, Stage B/C or Gate promotion. Actual approval of digests and subsequent conditional production must follow their own evidence-dependent gate.

## Distinguish observations and stop statuses

- `PREFLIGHT_SOURCE_VERIFIED` only with exact branch SHA, source checks and independent clean worktree review; otherwise `PREFLIGHT_SOURCE_PARTIAL`.
- `PREFLIGHT_MEASUREMENT_CANDIDATE_VERIFIED` only after one authorized first attempt, complete observed runner metadata and exact byte hashes independently checked; otherwise `PREFLIGHT_BLOCKED` with reason.
- `A2_BLOCKED_TOOL_IDENTITY` persists until separate owner approval of exact digest pair and their administration/readback, and fresh producer pre-push checks.
- `A3_NOT_RUN`, `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`, `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT` remain invariant.

**Terminal Owner approval:** `VIP_BFIRST_A2_STRATEGY_B_ONE_MEDIA_FREE_PREFLIGHT_APPROVED`; no permission to bypass independent gates.
