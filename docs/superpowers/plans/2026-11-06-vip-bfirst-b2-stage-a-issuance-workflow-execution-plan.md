# B-first B2 Stage A Issuance Workflow Execution Plan

> **For agentic workers:** This is a proposed, owner-gated execution packet. Do not implement or run it until the explicit Stage A operational approval in this document is recorded. Use the repository's current execution protocol; stock per-inner-task subagent review is not required.

**Goal:** Implement and, only after separate operational approval, issue one immutable CI artifact containing the proposed synthetic `bfirst_tiny_video_v1.mp4`, with independently reviewable producer and pin evidence.

**Architecture:** A single exact-SHA-bound `push` run on the dedicated feature branch generates one bounded MP4 and uploads one archive whose sole member is that MP4. The workflow records producer claims in run output; a separate receipt recorder and independent artifact reviewer create post-run evidence without changing the producing commit. A further owner-reviewed pin record is kept distinct from Stage B closed-manifest registration.

**Tech Stack:** Canonical Python standard library; already-present Linux FFmpeg/FFprobe only if verified on the authorized runner; GitHub Actions; `actions/checkout` and `actions/upload-artifact` pinned to verified full commit SHAs; GitHub REST API for post-run run/job/artifact verification.

**Spec:** LAB B2 design at `design/vip-bfirst-pinned-synthetic-video-fixture-20261106@4bec4ef197539781c47ae1ea63b7fb4ffcbdb229`; independent audit and exact Stage A packet at LAB `review/vip-bfirst-b2-artifact-issuance-feasibility-20261106@be438719ca955b8d3bdefcb1beafdb1e34d37c5d`. This proposal resolves the audit's `workflow_dispatch` blocker and does not amend either source document.

## Global Constraints

- Canonical read-only implementation anchor: `cac74495d80d9eaa144a12e9aa67eba78ba2f062` (tree `1e851b89273e7ae9a580643b8b704a2d5945c099`); observed Canonical `main`: `3bfcc2ba221b36df6773e630b44479ec961d630a`. LAB `main`: `5eab58ea2a5424424cb95f2690654b91395425df`.
- No Canonical or LAB `main` writes/merges, no PR, no protected/archive media, model/provider activity, production render/export, Gate promotion, or B1 Git-blob fallback.
- This plan authorizes documentation only. It does not authorize workflow/source edits, the first push, FFmpeg/FFprobe execution, artifact upload/download, repository-variable or ruleset changes, pin adoption, or Stage B/C.
- Exact proposed fixture intent: MP4, 64×64, 10 seconds, CFR target 4/1, 40 video frames, one video stream, no audio, no B-frame reordering, proposed `mpeg4` codec, raw MP4 ceiling 65,536 bytes. These are not observed output properties.
- Actual codec support, frame/stream properties, PTS, timebase, file size/digest, tool hashes, artifact ID/archive digest, numeric job ID, and expiry remain `NOT_OBSERVED` until separately authorized issuance and review.
- Preserve `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED` and `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.
- A job/step must fail closed on missing settings, identity drift, unsupported tools, timeout, limit breach, probe/decode mismatch, upload mismatch, or incomplete evidence. No silent codec/size change, regeneration under the same identity, or automatic expiry replacement.
- Preserve source-native integer PTS and rational timebase as measured values. Do not infer PTS from nominal FPS or turn semantic matches into frame-accurate cuts.

## Review Focus

1. A feature push itself starts the workflow; branch/path filters are selection gates, not authentication. Tests and release procedure must prove the exact reviewed SHA, pre-push controls, and refusal of reruns or a changed source SHA.
2. `github.sha`/`github.workflow_sha` must equal an independently configured expected producer SHA; the workflow cannot embed its own final commit SHA. Test missing, malformed, stale, and mismatched values.
3. A successful producer receipt is not acceptance. Tests and review must bind run, numeric job, artifact ID, GitHub archive digest, downloaded archive bytes, extracted MP4 digest, and independent decode.
4. Artifact retention/deletion is not permanent storage. Tests must refuse expired, deleted, unavailable, or mismatched artifacts and prohibit same-identity reissuance.
5. The producer archive must contain exactly one safe MP4 member. The post-run JSON receipt and independent pin record must live outside that archive and outside the producer source commit.

---

## Authority and Preflight Record

This is an execution plan, not approval to execute. Current task authority is limited to the proposed LAB document. Before future code work, a new Canonical worker must re-read live source and settings, bind a clean isolated worktree at the authorized base, receive exact exclusive path ownership, and obtain the named operational approval below.

This planning worker is native Codex thread `01a1b2b3-8105-7680-b4f6-5607422f801d` in LAB project `c45ddb76-edbc-4aed-8f6e-8da3afaeb420`. Its actual CWD/worktree is `/Users/yusuf/.codex/worktrees/e821/vide-intelligence-pipeline-2`; Git top level is that directory and common Git directory is `/Users/yusuf/Repos/vide-intelligence-pipeline-2/.git`. The verified isolated worktree began clean/detached at LAB `main@5eab58ea2a5424424cb95f2690654b91395425df` (tree `dae72052bbdbc1962713f302b50f8fa2fd78ed7f`), then was bound to `design/vip-bfirst-b2-stage-a-issuance-execution-plan-20261106`. It is distinct from the shared LAB checkout and canonical repo. This is documentation-worker identity only; it does not authorize or stand in for the future Canonical issuer/reviewer.

The planning preflight observed the following on 2026-11-07 (Europe/Istanbul), using read-only GitHub API calls against `Centaurioun/video-intelligence-pipeline`:

| Read-only observation | Observed value | Scope and limit |
|---|---|---|
| Repository | `private=true`, `default_branch=main`, `archived=false` | `GET /repos/Centaurioun/video-intelligence-pipeline` |
| Actions | `enabled=true`, `allowed_actions=all`, `sha_pinning_required=false` | `GET /repos/.../actions/permissions`; no action allowlist or enforced pinning |
| Workflow token default | `default_workflow_permissions=read`, `can_approve_pull_request_reviews=false` | `GET /repos/.../actions/permissions/workflow` |
| Artifact/log retention | `days=90`, `maximum_allowed_days=400` | `GET /repos/.../actions/permissions/artifact-and-log-retention`; live setting can drift; future artifact `expires_at` and availability still require run-time API verification |
| Selected actions endpoint | API returned HTTP 409 because all actions are allowed | Confirms there is no selected-action allowlist to rely on |
| Active rulesets / branch rules | `GET /repos/.../rulesets?includes_parents=true` returned active `protect-main-canonical`, whose only included ref is `refs/heads/main`; two portfolio trust rulesets are disabled. The legacy branch-protection endpoint returned 404 for `main` (`Branch not protected`). The active ruleset has a repository-role bypass with pull-request-only mode. | No active ruleset for the proposed feature ref was returned. The main-only ruleset does not protect the issuance branch. Workflow actor execution restrictions remain `NOT_OBSERVED`. An owner-controlled one-pusher restriction and post-run ref freeze must be independently verified before any workflow push. |
| Issuance artifact/run | `NOT_OBSERVED` | No producer run, upload, or download was performed. |

Canonical workflow census at the pinned implementation candidate found exactly five workflow YAML files:

| Workflow | Events | Permissions | Matrix / time | Artifact behavior |
|---|---|---|---|---|
| `python-synthetic-smoke.yml` | `pull_request` to main, `push` to main, `workflow_dispatch` | `contents: read` | Python 3.11/3.14; 20-minute job | `upload-artifact@v4` for PR #258 receipts, 14-day retention |
| `canonical-history-regressions.yml` | `pull_request` to main or one named task branch, `workflow_dispatch` | `contents: read`, `actions: read` | Python 3.11/3.14; 30-minute job | `upload-artifact@v4`; no per-artifact retention set in workflow |
| `gate0-broad-synthetic-regressions.yml` | `pull_request` to main, `push` to main, `workflow_dispatch` | `contents: read` | Python 3.11/3.14; 20-minute job | No upload step |
| `gate0-d1-integrated-regressions.yml` | `pull_request` to main, `push` to main, `workflow_dispatch` | `contents: read` | Python 3.11/3.14; 20-minute job | No upload step |
| `gate2-receipt-report-regressions.yml` | `pull_request` to main, `push` to main, `workflow_dispatch` | `contents: read` | Python 3.11/3.14; 20-minute job | No upload step |

All existing `workflow_dispatch` examples are already on Canonical `main`; none is a reusable `workflow_call` issuance mechanism. Existing media test code creates lower-assurance runtime fixtures and hard-codes a Mac FFmpeg path in one integration test, so it does not prove a hosted Linux issuance path. `tests/gate0/media/generated_media.py` states that checked-in media is forbidden. `real_source_probe.py` passes a filesystem `Path` to FFprobe, which reads that path; the separate B2 consumer design therefore requires a private verified snapshot. No source behavior from LAB is treated as Canonical evidence.

The B2 design and audit remain proposals. They preserve the B2 CI artifact choice, no committed media rule, strict failure on artifact expiry/deletion, and separation between `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED` and the legacy CORE-01 contract blocker.

## Trigger Design Decision

### Compared approaches

| Approach | Disposition | Reason |
|---|---|---|
| New workflow with only `workflow_dispatch` on an unpublished feature branch | Reject | GitHub requires a workflow with `workflow_dispatch` to exist on the default branch. Getting it there would require an unauthorized main change/PR/merge. |
| Add an issuance trigger to an existing main workflow or call a reusable workflow on main | Reject for this packet | No current reusable issuance mechanism was found; changing or relying on a main workflow expands the authorized source surface. Any main change is outside scope. |
| Dedicated feature-branch `push`, exact branch + narrow paths + independent expected-SHA check | Recommend conditionally | GitHub documents push runs for workflow files not merged into the default branch. A push to the exact reviewed feature commit is the only selected route that does not require a main change. It is safe to use only after source review and effective pre-push restrictions are proven. |

The official GitHub event documentation says `workflow_dispatch` needs the workflow on the default branch, while a `push` workflow may run from an unmerged branch. When both branch and path filters are set, both must match. The `push` run's `GITHUB_SHA` is the tip commit pushed, and `github.workflow_sha` identifies the workflow source commit. These facts are documented in [Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows), [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), and [Contexts reference](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts).

Proposed workflow trigger and guard, shown as text only:

```yaml
name: B-first pinned synthetic video issuance

on:
  push:
    branches:
      - feature/vip-bfirst-video-issuance-20261106
    paths:
      - .github/workflows/bfirst-pinned-video-issuance.yml
      - tests/vip_fvs/fixtures/generated_video/build_pinned_video.py
      - tests/vip_fvs/unit/test_pinned_video_fixture_issuer.py

permissions:
  contents: read
  actions: read

concurrency:
  group: bfirst-video-issuance-${{ github.ref }}
  cancel-in-progress: false

jobs:
  issue:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    steps:
      - name: Verify the reviewed producer identity before checkout or generation
        env:
          EXPECTED_PRODUCER_SHA: ${{ vars.BFIRST_B2_EXPECTED_PRODUCER_SHA }}
          EVENT_NAME: ${{ github.event_name }}
          REF: ${{ github.ref }}
          SOURCE_SHA: ${{ github.sha }}
          WORKFLOW_SHA: ${{ github.workflow_sha }}
          WORKFLOW_REF: ${{ github.workflow_ref }}
          RUN_ATTEMPT: ${{ github.run_attempt }}
        run: |
          python3 - <<'PY'
          import os
          import re
          import sys

          expected = os.environ.get("EXPECTED_PRODUCER_SHA", "")
          checks = {
              "event": os.environ.get("EVENT_NAME") == "push",
              "repository": os.environ.get("GITHUB_REPOSITORY") == "Centaurioun/video-intelligence-pipeline",
              "ref": os.environ.get("REF") == "refs/heads/feature/vip-bfirst-video-issuance-20261106",
              "workflow_ref": os.environ.get("WORKFLOW_REF") == "Centaurioun/video-intelligence-pipeline/.github/workflows/bfirst-pinned-video-issuance.yml@refs/heads/feature/vip-bfirst-video-issuance-20261106",
              "expected_sha_format": re.fullmatch(r"[0-9a-f]{40}", expected) is not None,
              "source_sha": os.environ.get("SOURCE_SHA") == expected,
              "workflow_sha": os.environ.get("WORKFLOW_SHA") == expected,
              "first_attempt": os.environ.get("RUN_ATTEMPT") == "1",
          }
          failed = [name for name, passed in checks.items() if not passed]
          if failed:
              print("producer identity guard failed: " + ", ".join(failed), file=sys.stderr)
              raise SystemExit(1)
          print("producer identity guard passed for the configured exact SHA")
          PY
      # Then: checkout exact triggering SHA with a full-SHA-pinned action,
      # persist-credentials:false; run mocked unit tests; verify tool identity;
      # generate/inspect exactly one file; upload only that file.
```

The guard body is complete design text and makes each check an explicit refusal before checkout, tool execution, or upload. The snippet is not an executable workflow file and must not be copied into the repository until the full workflow is implemented and reviewed.

### SHA self-reference and push controls

The producer commit cannot contain its own final Git SHA as a literal: adding the literal changes the commit and therefore changes the SHA. Use the exact following external binding protocol:

1. Implement the complete candidate locally on the future Canonical issuance branch, including workflow, generator and tests. Run only mocked behavioral tests and static checks.
2. Commit the candidate once; compute its full commit SHA. No source edits are allowed after this point. Any change means a new commit, fresh independent review and a newly approved expected SHA.
3. A separate reviewer inspects the complete candidate at that exact SHA before any push. The owner or authorized repository administrator records the actual 40-character SHA returned by `git rev-parse HEAD` in repository Actions variable `BFIRST_B2_EXPECTED_PRODUCER_SHA`. This setting change is a separate owner-authorized operation, not covered by this plan.
4. Before the first push, independently confirm the variable value, exact branch protection/actor restrictions and current Actions policy. Permit only the reviewed exact commit to be pushed to the one feature ref. If effective pre-push restrictions are unavailable or cannot be verified, stop; branch/path filters plus an in-workflow SHA check alone are not sufficient authentication.
5. Push only that exact commit, non-force and fast-forward safe, after the separate operational approval. This push starts the workflow automatically. Do not treat a post-push approval as a trigger gate.
6. At the very first workflow step, fail unless repository, event=`push`, exact branch ref, exact workflow ref/path, `github.sha` and `github.workflow_sha` all match the configured expected producer SHA, and `github.run_attempt` is exactly `1`. Do not accept dispatch, rerun, another SHA, a later branch head, or a different ref.
7. No later source push to this branch is allowed for issuance. Receipt and pin commits go to separate evidence branches and are excluded from the workflow paths. After the run, freeze/retire the issuance branch under owner control; no workflow activation is inferred for a future change.

The repository variable is an independent configuration input, not a cryptographic trust root. A workflow author able to change the workflow could delete its own check, and a sufficiently privileged actor can alter repository settings. The exact candidate SHA, one named authorized pusher, run metadata, API artifact record and independent review are all checked separately. No ruleset can be assumed to enforce a particular commit SHA. The plan relies on one controlled push of the already-reviewed commit plus post-run branch freeze; it does not claim protection against a malicious authorized administrator. If that operator boundary and ref freeze cannot be established, stop without a workflow push.

GitHub currently reports `allowed_actions=all` and `sha_pinning_required=false`. Therefore the future workflow must pin each external action to a verified full 40-character upstream commit SHA regardless of repository policy. The precise action release SHAs must be selected and reviewed against the official action repository at implementation time; floating tags are disallowed. Only checkout and upload actions are proposed. Grant only `contents: read` for checkout and `actions: read` because the producer receipt step reads its run jobs and artifact metadata from the GitHub REST API to record the numeric job ID, artifact linkage and expiry. Do not add `actions: write`, `contents: write`, pull-request, package, deployment or secret permissions. Upload uses the runner artifact service and does not justify write access to the repository token. Keep the API token only in the metadata step environment and never print it. The separate reviewer uses its own authenticated `Actions: read` access for an independent recheck and download. GitHub's [least-privilege guidance](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication) supports keeping the producer token read-only.

## Future Ownership and Evidence Boundaries

All paths below are proposed Canonical paths and are currently read-only in this LAB documentation task. A future Canonical writer must receive exclusive ownership after exact-base, branch, worktree and task-grant verification.

| Future path | Exclusive owner | Purpose / boundary |
|---|---|---|
| `.github/workflows/bfirst-pinned-video-issuance.yml` | Stage A workflow implementer | One-shot, exact-branch push trigger and bounded producer job. Any edit changes producer SHA and requires fresh review. |
| `tests/vip_fvs/fixtures/generated_video/build_pinned_video.py` | Stage A generator implementer | Fixed local lavfi-only generator, no source path/URL/codec/output/shell-fragment parameters. Generates to a fresh private `$RUNNER_TEMP` child and never writes media to the Git tree. |
| `tests/vip_fvs/unit/test_pinned_video_fixture_issuer.py` | Stage A generator implementer | Mocked behavioral tests for argument, path, tool, output, probe and receipt refusal behavior. |
| `tests/vip_fvs/fixtures/generated_video/issuance-receipt.json` | Separate post-run receipt recorder | After a successful producer run, records machine-readable producer claims and API-confirmed run/job/artifact/expiry identities on a separate evidence branch/commit. Never commits to or mutates the producer branch. It is not an independent acceptance or policy pin. |
| `tests/vip_fvs/fixtures/generated_video/independent-pin-record.json` | Independent artifact reviewer; separate owner approval for adoption | After artifact download and review, records reviewer evidence and explicit recommendation/adoption state. The receipt author cannot own or approve this path. Stage B manifest registration remains separately authorized. |

The producer archive is named `bfirst_tiny_video_v1` and contains exactly one member named `bfirst_tiny_video_v1.mp4`. After upload, the workflow queries `GET /repos/Centaurioun/video-intelligence-pipeline/actions/runs/{run_id}`, `GET /repos/Centaurioun/video-intelligence-pipeline/actions/runs/{run_id}/jobs?filter=latest`, and `GET /repos/Centaurioun/video-intelligence-pipeline/actions/artifacts/{artifact_id}` with `actions:read` to capture run binding, numeric job ID and artifact metadata. If any read fails or cannot identify the exact run/job/artifact, the workflow exits nonzero and the artifact remains unaccepted. `GITHUB_JOB` is only the workflow job key; never label it as the numeric job ID. The JSON receipt is a distinct workflow-run summary output and later evidence-branch JSON; it is not uploaded as an archive member. This avoids a two-file media archive, receipt/artifact digest circularity, and a receipt commit changing the producing SHA.

The receipt records source repository, full expected/source/workflow SHAs, event and branch, workflow path, run ID and attempt, workflow job key plus API-verified numeric job ID, runner image identity, Python/FFmpeg/FFprobe paths+versions+binary hashes, fixed argv, output MP4 SHA-256 and byte count, measured probe/decode fields, artifact name/ID, upload action archive-digest output, GitHub artifact REST `digest`, artifact API `created_at`/`expires_at`/`expired`, and evidence status. The upload action's SHA-256 is the archive digest; it is not the raw MP4 digest. The API artifact object exposes an artifact ID, `digest`, `expires_at`, `expired`, and `workflow_run` linkage; independently compare the API digest to the upload output and to a locally computed SHA-256 of the downloaded ZIP.

## Future Workflow and Generator Contract

- Use one `ubuntu-24.04` hosted job, `timeout-minutes: 15`, one runner, no matrix, no self-hosted runner, no package installation, no model/provider credentials, no shell fragments from input. Record exact runner image/runtime identity because GitHub-hosted image contents can change. If Python 3 or FFmpeg/FFprobe are unavailable, fail closed; do not apt/Homebrew/pip install tools under this plan.
- Resolve FFmpeg and FFprobe executable paths, resolved real paths, SHA-256 binaries, complete version/build output and runner image identity before generation. If encoder `mpeg4` support is absent, fail; do not silently select another encoder.
- The public CLI accepts no generation options or positional input. The only media source is a fixed lavfi expression in source. No path, URL, input file, output path, codec, dimensions, frame rate, frame count or shell text can be supplied by a workflow input or caller. Use argv arrays and `shell=False` for all child processes.
- Create a new private directory under `$RUNNER_TEMP`; reject an unexpected root, pre-existing output, symlink, or nonempty destination. Never write generated MP4 into the repository. Keep the fixed output basename `bfirst_tiny_video_v1.mp4`.
- Use fixed lavfi test pattern(s), 64×64, rate 4/1, duration 10, exactly 40 frames, `-an`, MPEG-4 Part 2 `mpeg4`, B-frames disabled, single encoder/filter thread. Record the exact argv and environment. No audio, user data, source media, network URL or external bytes are inputs.
- Apply process wall timeout 120 seconds for generation; 30 seconds for probe and independent full decode. Apply Linux child-process CPU limit 120 seconds for generation / 30 seconds per probe/decode and `RLIMIT_FSIZE=65536` before encoder start; then recheck actual output size is `1..65536` bytes. Apply a 15-minute whole-job timeout. Limit threads to one. Any unavailable/enforcement-failed limit is a hard refusal, not a weaker fallback.
- Run FFprobe in JSON mode with video stream and per-frame fields sufficient to observe stream index, codec, width, height, frame count, `has_b_frames`, `time_base`, frame integer PTS and duration. Parse exact integers and rational strings. Require one total stream and one video stream, no audio, `mpeg4`, 64×64, 40 decoded frames, 10-second measured duration, 4/1 CFR as supported by actual per-frame PTS/timebase, no B-frame reordering, valid monotonic unique source PTS, and supported timing. Do not derive PTS from nominal frame rate; record observations as actually returned. Any omitted/ambiguous required field fails.
- Independently decode the resulting MP4 to a null sink under the same finite timeout/CPU/thread limits; require exit 0 and exactly 40 decoded frames. This is still producer-side validation; it does not substitute for independent post-upload review.
- Generate one machine-readable producer JSON summary in the job's temporary directory and append its canonical JSON to the GitHub run summary after upload outputs and read-only API checks are available. Include producer claims, upload `artifact-id`/`artifact-digest`, API numeric job ID, artifact `digest`, `expired`, `expires_at`, and `workflow_run` linkage. The workflow fails if the current job ID or artifact API record cannot be obtained after three attempts spaced two seconds apart. No second artifact is uploaded. The later receipt recorder preserves this output in the separate evidence branch after an API cross-check.
- Upload one explicit file path only, with `if-no-files-found: error`, `overwrite: false`, hidden files excluded, archive enabled, artifact name `bfirst_tiny_video_v1`, and `retention-days: 90` subject to a fresh setting check. Do not upload the producer JSON, logs, source, environment or directory wildcard. No upload is accepted if the actual archive does not have exactly the one expected MP4 member.
- At issuance, fetch the workflow run, current run's job list, and artifact by numeric ID from GitHub REST API; verify run event/ref/path/head SHA, numeric job ID, and artifact bind to the same repository/run/head SHA and workflow, have expected name, are not expired, have a present future `expires_at`, and the GitHub `digest` equals the upload output. If API is unavailable or any field is missing/mismatched, the workflow run is failed/incomplete and no pin is authorized. The independent reviewer repeats these checks using separate read-only credentials.

GitHub documents that upload-artifact v4+ artifacts are immutable, exposes artifact ID and SHA-256 archive digest, and supports `retention-days`; immutability does not prevent deletion or expiry. Its REST artifact record provides `expired`, `expires_at`, digest and workflow-run linkage. Deleting an artifact or workflow run removes availability. These are temporary run artifacts, not a permanent archive. See [upload-artifact README](https://github.com/actions/upload-artifact), [artifact storage and retention](https://docs.github.com/en/actions/tutorials/store-and-share-data), [removing artifacts](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/remove-workflow-artifacts), and [Actions artifacts REST API](https://docs.github.com/en/rest/actions/artifacts).

## Future Test-First Tasks

### Task 1: Define importable interfaces, then pin the boundary with mocked behavioral RED

**Files:** `tests/vip_fvs/unit/test_pinned_video_fixture_issuer.py`; minimal importable interface scaffold in `tests/vip_fvs/fixtures/generated_video/build_pinned_video.py`.

**Interfaces:** `ToolIdentity(path: Path, version_output: str, sha256: str)`, `ProducerMeasurements(output_sha256: str, output_size_bytes: int, probe: Mapping[str, object], decoded_frame_count: int)`, `ProcessRunner.run(argv: Sequence[str], *, cwd: Path, timeout_seconds: int, cpu_seconds: int, file_size_limit_bytes: int | None) -> CompletedProcess`, `validate_cli_args(argv: Sequence[str]) -> None`, `validate_output_root(candidate: Path, runner_temp: Path) -> Path`, `validate_output_measurements(*, actual_size_bytes: int, probe: Mapping[str, object]) -> ValidationResult`, `generate(*, runner_temp: Path, ffmpeg: ToolIdentity, ffprobe: ToolIdentity, runner: ProcessRunner) -> ProducerMeasurements`, and `main(argv: Sequence[str] | None = None) -> int`. The module also defines `IssuanceRefused` and `ValidationResult(status: str, upload_ready: bool)`. The scaffold defines these names and signatures only and raises `NotImplementedError`; it creates no media and runs no process.

- [ ] Create the importable signature-only scaffold first; do not implement behavior in this step.
- [ ] Add tests `test_rejects_any_cli_arguments_before_tool_execution`, `test_rejects_arbitrary_input_file_or_url`, `test_rejects_wrong_output_root_or_preexisting_destination`, and `test_uses_only_fixed_lavfi_args_without_shell`.
- [ ] Mock `ProcessRunner`. Assert rejected inputs call it zero times, no arbitrary source path appears in argv, and every invocation uses a sequence argument vector with shell execution disabled.
- [ ] Add tests `test_refuses_missing_ffmpeg_or_ffprobe`, `test_refuses_unexpected_executable_identity`, `test_refuses_nonzero_exit_and_timeout`, and assert specific refusal statuses and absence of upload-ready output.
- [ ] Run `python -m pytest -q tests/vip_fvs/unit/test_pinned_video_fixture_issuer.py`. Expected pre-implementation RED is one or more behavioral assertions failing because scaffold methods raise `NotImplementedError`; import/collection/missing-prerequisite errors are not RED. Repair environment within v5 authority, then rerun the untouched tests.

The first tests pin concrete refusal behavior; the scaffold keeps imports valid so the expected failure is behavioral:

```python
def test_rejects_arbitrary_input_file_or_url(monkeypatch):
    runner = RecordingRunner()
    monkeypatch.setattr(issuer, "DEFAULT_PROCESS_RUNNER", runner)
    with pytest.raises(IssuanceRefused, match="UNSUPPORTED_ARGUMENTS"):
        issuer.main(["--input", "https://example.invalid/media.mp4"])
    assert runner.calls == []


def test_rejects_wrong_output_root(tmp_path):
    runner_temp = tmp_path / "runner-temp"
    wrong_root = tmp_path / "outside-runner-temp"
    runner_temp.mkdir()
    with pytest.raises(IssuanceRefused, match="OUTPUT_ROOT_MISMATCH"):
        issuer.validate_output_root(wrong_root, runner_temp)


def test_refuses_output_over_byte_limit_before_upload_ready(tmp_path, fake_probe):
    result = issuer.validate_output_measurements(
        actual_size_bytes=65_537,
        probe=fake_probe,
    )
    assert result.status == "REFUSED_OUTPUT_TOO_LARGE"
    assert result.upload_ready is False
```

The tests use a fake runner/probe and do not invoke FFmpeg.

### Task 2: Implement bounded generation and measured media validation

**Files:** generator only at `tests/vip_fvs/fixtures/generated_video/build_pinned_video.py`; tests remain Task 1 owner’s shared test input but no simultaneous write overlap.

- [ ] Define a fixed `GenerationSpec` and pure validation helpers; CLI `main(argv)` refuses every nonempty arg list. Internal tests may supply a temp root and mocked `ProcessRunner`, but the public workflow cannot override fixed constants.
- [ ] Implement executable resolution/identity checks, private temp root validation, fixed lavfi argv, process time/CPU/file-size limits, raw SHA-256/size, JSON probe parsing, exact frame PTS/timebase capture, and independent bounded decode. Return structured producer measurements only after every invariant passes.
- [ ] Implement the declared methods and keep `main(argv)` fixed to the runner's validated `$RUNNER_TEMP`; internal injection is test-only. Add negative cases for wrong codec, extra/audio stream, wrong dimensions, duration, frame count, B-frame status, missing/nonmonotonic/duplicate PTS, unsupported timebase, output above 65,536 bytes, and malformed probe JSON. Each must refuse before an upload step could be reached.
- [ ] Run `python -m pytest -q tests/vip_fvs/unit/test_pinned_video_fixture_issuer.py`; expected GREEN is all named mocked behaviors passing with no real FFmpeg invocation.
- [ ] Verify the preexisting Canonical generated-media prohibition remains untouched; no MP4 may enter the Git index or worktree source tree.

### Task 3: Add and statically validate the push-only workflow

**Files:** workflow only at `.github/workflows/bfirst-pinned-video-issuance.yml`.

- [ ] Implement the exact branch and narrow `paths` trigger in the text design above; do not include receipt/pin paths. Do not add `workflow_dispatch`, pull request, tag, schedule, `workflow_run`, or `workflow_call` events.
- [ ] Make the first run step perform the complete event/ref/expected SHA/workflow SHA/attempt guard before checkout, tool resolution, tests that import candidate code, FFmpeg, or upload. Missing/malformed variable is a nonzero failure.
- [ ] Use only `contents: read` and `actions: read`; pin checkout and upload actions to full SHA values verified from their official source repositories. Set checkout `persist-credentials: false`. Do not add dependencies or secrets.
- [ ] Run the unit tests before the tool-presence gate. Pin runner label and fixed job/process limits. Upload exactly the one explicit MP4 after every local check passes, `overwrite:false`, retention 90 days, no hidden files.
- [ ] Add workflow-contract tests in the same test file: `test_workflow_is_push_only_on_exact_branch_and_paths`, `test_workflow_permissions_are_contents_read_and_actions_read_only`, `test_expected_sha_guard_precedes_checkout_and_tools`, `test_workflow_uploads_only_one_mp4_for_90_days`, and `test_receipt_paths_do_not_trigger_issuance`. Parse the guard step and execute its Python body with a controlled environment: assert exact repository/ref/workflow/source SHA and attempt `1` returns `0`; missing SHA, wrong event, branch, workflow ref, source SHA, workflow SHA, or attempt returns `1` and names the failed check.
- [ ] Add mocked REST-boundary tests `test_refuses_missing_numeric_job_id`, `test_refuses_artifact_api_mismatch`, and `test_workflow_failure_after_upload_stays_unaccepted`; assert metadata mismatch returns a nonzero job result and no pin/acceptance status.
- [ ] Add receipt/archive tests `test_refuses_malformed_receipt_or_output_digest_mismatch`, `test_refuses_wrong_artifact_member_count_or_archive_digest`, `test_refuses_expired_deleted_or_unavailable_artifact`, `test_rejects_wrong_event_branch_or_producer_sha`, and `test_incomplete_independent_review_cannot_create_pin_record`. Assert each failure yields no independent pin/admission result.
- [ ] Parse the workflow with an already-available YAML parser. If PyYAML is already installed, run `python -c 'import yaml,sys; yaml.safe_load(open(sys.argv[1], encoding="utf-8"))' .github/workflows/bfirst-pinned-video-issuance.yml`; otherwise use the repository's existing YAML parser and do not install a new dependency solely for this check.
- [ ] Run `python -m pytest -q tests/vip_fvs/unit/test_pinned_video_fixture_issuer.py` and confirm workflow-contract cases pass. Static validation proves structure only; it does not authorize or exercise GitHub Actions.

### Task 4: Pre-push exact-SHA review and external binding

**No source file changes. Owner/admin configuration and workflow execution remain separately gated operations.**

- [ ] Confirm clean exact-base Canonical worktree, exclusive ownership of the three producer paths, and complete diff restricted to those three paths. Run focused tests and static checks against the final candidate SHA.
- [ ] Request an independent reviewer on the exact final commit for branch/path/event logic, source scope, minimal permissions, SHA/self-reference handling, tool/output limits, archive member contract, receipt separation and all B2 invariants.
- [ ] Re-fetch branch/ruleset/Actions execution policy. The administrator must prove the dedicated branch can be updated only through the one reviewed commit by the authorized issuer actor (or equivalent enforced control) and confirm no later unreviewed push can execute producer code. If unavailable, stop without push.
- [ ] Only after separate owner operational approval, set the non-secret repository Actions variable `BFIRST_B2_EXPECTED_PRODUCER_SHA` to the exact reviewed full commit SHA and verify the readback. This setting is an external mutable control and must be captured as evidence.
- [ ] Before pushing, independently confirm expected SHA, actor restrictions, exact new branch absence or safe exact state, all checks, source review, and authorization. The first exact-SHA push automatically starts issuance. No post-push review can retroactively authorize it.

### Task 5: One-time synthetic issuance run and producer receipt

**Runtime/evidence operations require separate explicit Owner operational approval; not authorized by this plan.**

- [ ] Push the reviewed exact commit once to `feature/vip-bfirst-video-issuance-20261106`; never force push or amend it after approval.
- [ ] Confirm GitHub run head SHA, workflow SHA, event, full ref and attempt 1 match the reviewed source. Confirm the single job's conclusion and logs. Any mismatch, missing tool or nonzero step ends issuance without pin.
- [ ] Obtain run ID and numeric job ID from GitHub. `GITHUB_JOB` alone is not the numeric ID.
- [ ] Confirm exactly one uploaded artifact for the run, artifact name/ID, action `artifact-digest`, REST API `digest`, API `workflow_run.head_sha`, and `expires_at`. Ensure artifact is not expired and retention is currently within the permitted policy.
- [ ] A separate receipt recorder creates `issuance-receipt.json` on a new evidence branch, preserving all runtime fields only after comparing run/jobs/artifact API records with producer output. This evidence commit must not be on the producer branch and cannot modify the producer source SHA.

### Task 6: Independent archive and media acceptance, then separate pin record

**Review and artifact download require separately authorized read access and one bounded download.**

- [ ] A reviewer other than the issuer/receipt recorder queries the exact run and artifact through GitHub REST API with read-only Actions scope. Verify repository, run, event/ref, head SHA, workflow SHA, attempt, numeric job ID, artifact ID/name, `expired=false`, `expires_at`, and archive digest.
- [ ] Download the exact artifact ID once to a private temporary directory. Hash the raw downloaded ZIP and require equality with the GitHub API `sha256:` digest and the upload step output. A URL alone is not identity.
- [ ] Inspect archive before extraction: exactly one member, exact basename `bfirst_tiny_video_v1.mp4`, regular file only, no directories/hidden/unexpected members, symlinks, absolute paths, traversal or duplicate names. Extract only that member to a new bounded private directory.
- [ ] Rehash extracted MP4 and confirm exact size and SHA-256 match producer output; independently run bounded FFprobe and full decode in a separate review environment, capturing its own tool identity, stream index, codec, dimensions, count, integer PTS and rational timebase.
- [ ] If artifact is unavailable, expired/deleted, API is unavailable, digest differs, member list is unexpected, decode differs, or evidence is incomplete, write a failure receipt/status only. Do not reissue the same fixture ID or reuse a newly generated artifact as the old identity.
- [ ] Only after successful independent review may the separate reviewer write `independent-pin-record.json` on the evidence branch. Record exact immutable identity and expiry, all verified findings, reviewer/tool identities, actual availability, and decision. Require a distinct Owner adoption decision before treating it as Stage B input. No B2 artifact is automatically admitted to the closed manifest by issuer or reviewer.

## Required Prospective Acceptance Matrix

All tests below use mocked or controlled process/API boundaries until the separately approved one-time issuance and review. Expected refusal must happen before upload/admission.

| Test | Expected behavior |
|---|---|
| Unsupported generator arguments | Reject before tool launch |
| Arbitrary local file, absolute path, URL, or remote input | Reject before source open or tool launch |
| Wrong output root, symlink, occupied path, preexisting media | Reject before write |
| Wrong codec/encoder, extra stream, audio, dimensions, duration, CFR/count, B-frames | Reject and produce no upload-ready file |
| Output byte ceiling exceeded | `RLIMIT_FSIZE` stops growth; explicit refusal; do not lower quality or alter cap |
| Tool timeout, CPU/file limit failure, or nonzero exit | Refuse; preserve diagnostics; no upload |
| Missing FFmpeg/FFprobe or unexpected executable/version/hash | Refuse; do not install an alternate |
| Malformed/incomplete FFprobe JSON or missing integer PTS/rational timebase | Refuse; never synthesize timing |
| Malformed producer receipt or source/run/artifact mismatch | Reject receipt; never accept its self-assertion |
| Wrong branch/ref/event/source SHA/workflow SHA or run attempt != 1 | Guard fails before checkout/generation/upload |
| No artifact, multiple artifacts, or artifact has wrong name/member count | No pin; fail closed |
| Archive digest mismatch with action/API/local download | Reject before extraction/acceptance |
| Unsafe archive path, extra member, symlink or duplicate MP4 | Reject before extraction |
| Extracted MP4 hash/size differs | Reject; no registration |
| Artifact expired, deleted, API unavailable, missing expiry/identity | `BLOCKED_NO_PINNED_VIDEO_FIXTURE`; no regeneration under same ID |
| Independent review evidence incomplete or issuer/reviewer ownership overlaps | `PARTIAL`/`NOT_OBSERVED`; no independent pin/adoption |

## Acceptance Gates and Stop States

1. **Source-preflight gate:** exact Canonical source and current owner/task constraints re-read; worktree/base/path ownership/lease verified. Failure means no writes.
2. **Behavioral TDD gate:** focused mocked tests produce genuine pre-implementation RED and implementation GREEN. Tool absence/collection errors do not count as RED.
3. **Static workflow gate:** YAML and tests establish branch/path/event/SHA/permission/attempt/upload rules. It is not a hosted run and not a source trust decision.
4. **Pre-push review/authorization gate:** reviewer examines the exact final source SHA before push; Owner explicitly authorizes producer source, one automatic push-triggered run, runner/tools, outputs, artifact upload, and repository variable/protection changes. Missing branch/actor protection blocks the push regardless of the source SHA check.
5. **Issuance gate:** one exact push and one attempt, bounded FFmpeg/FFprobe and one MP4 artifact. All actual output properties remain `NOT_OBSERVED` before this gate.
6. **Independent artifact gate:** distinct reviewer verifies exact run/job/artifact identity, archive digest/member set, raw MP4 digest/size, independently measured media fields, and live expiry. No self-acceptance.
7. **Pin adoption gate:** independent reviewer writes separate pin record; Owner makes a distinct decision whether evidence is suitable as a future Stage B closed-allowlist input. Stage B and Stage C require separate tasks/authority.

Terminal results: successful completion of this planning document means only `BFIRST_B2_STAGE_A_EXECUTION_PACKET_PROPOSED — OWNER_OPERATIONAL_APPROVAL_PENDING`; `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`; `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`. Any unavailable or failed future prerequisite stays `NOT_OBSERVED` or an explicit blocked status and is not converted to acceptance.

## Exact Future Owner Operational Approval Request

Before any Stage A source implementation or issuance operation, obtain explicit owner approval naming all of the following:

1. Canonical repository and exact candidate base/source SHA; the exact final producer SHA will be supplied after implementation and pre-push independent review.
2. Exclusive ownership of the three producer paths listed above, exact feature branch `feature/vip-bfirst-video-issuance-20261106`, clean isolated native worker/worktree, finite FFMPEG_HEAVY lease and permitted test commands.
3. Permission to add one executable workflow file whose first push to the dedicated feature branch starts immediately, plus permission to set and verify `BFIRST_B2_EXPECTED_PRODUCER_SHA` and configure/verify whatever branch/actor restriction is required. No main change, PR or merge is included.
4. One bounded `ubuntu-24.04` hosted run using only already-present Python/FFmpeg/FFprobe executables; exact time/CPU/thread/output caps; no package install, secrets, model/provider, archive media, or unrelated network access. If the runner lacks required tools or limits, stop and seek a new decision.
5. One upload of one artifact named `bfirst_tiny_video_v1` with only `bfirst_tiny_video_v1.mp4`, explicit 90-day artifact retention subject to fresh GitHub policy verification, and one independent API-bound artifact download for review. No reissue if unavailable.
6. A separate post-run receipt evidence commit to `issuance-receipt.json` and a separate independently owned/reviewed `independent-pin-record.json`; no mutation of the producer branch/SHA and no Stage B/C registration.
7. The independent reviewer and Owner who may accept/reject the pin after actual artifact evidence exists. Failure, expiry or incomplete evidence means no pin and no automatic replacement.

Any missing named permission keeps the affected stage blocked. A general approval to “continue B-first” is not a substitute for the exact operational scope above.
