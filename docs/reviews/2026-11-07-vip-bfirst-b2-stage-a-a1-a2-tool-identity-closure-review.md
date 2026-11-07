# VIP B-first B2 Stage A — A1 local evidence and A2 tool identity blocker

**Date:** 2026-11-07 (Europe/Istanbul)  
**Disposition:** `A1_REPORTED_LOCALLY_VERIFIED_NOT_REMOTE_AUDITABLE`; `A2_BLOCKED_TOOL_IDENTITY`; `A3_NOT_RUN`.  
**Current authority:** Read-only GitHub/web verification and this LAB review record only. No first issuance push, no media creation, no FFmpeg invocation, no tool installation, no production or Gate activity.

## Exact evidence

Canonical `Centaurioun/video-intelligence-pipeline`:
- GitHub `main@3bfcc2ba221b36df6773e630b44479ec961d630a` (read-only).
- Previous B-first code feature `@cac74495d80d9eaa144a12e9aa67eba78ba2f062` (read-only).
- **A1 local Codex report**: native implementation worker `01a1b352-89e3-72b1-a946-6f91208b37b5`, local isolated worktree `/Users/yusuf/.codex/worktrees/112b/video-intelligence-pipeline`, exact locally committed producer `413d032e5635e4d8670e5565856f7fcfcfaca3ff`, tree `589ef2a0119a339fba5cfd5603c608a6f7792b3c`, three allowed paths only (`build_pinned_video.py`, `test_pinned_video_fixture_issuer.py`, `bfirst-pinned-video-issuance.yml`), Python 3.11 and 3.14 30 PASS each, reported prospective RED receipts, actionlint, compile and independent clean-worktree source reviewer `ACCEPT`. These are **REPORTED**, not independently fetched or rerun; GitHub `GET /repos/.../commits/413d032...` returned 422 no commit, and `GET /git/ref/heads/feature/vip-bfirst-video-issuance-20261106` returned 404.
- GitHub ruleset `26738994` independently fetched: `bfirst-video-issuance-single-actor`, `active`; exact included `refs/heads/feature/vip-bfirst-video-issuance-20261106`; types `creation` and `update`; one bypass user `86323645`/`Centaurioun` with `always` mode. This verifies configuration, not a live enforcement attempt or permission to bypass pre-push checks.
- Codex **reports** repository variable `BFIRST_B2_EXPECTED_PRODUCER_SHA=413d032...` set/read back and `BFIRST_B2_APPROVED_FFMPEG_SHA256`/`BFIRST_B2_APPROVED_FFPROBE_SHA256` absent; privileged GitHub Actions variables REST endpoint is unsupported by this linked GitHub fetch connector, so these variable claims are not independently reproduced here.
- Existing owner operational authorization `Centaurioun/video-intelligence-pipeline-2@af8b1de7286095e8ed86a3fb11e08006cdcdf8ec` and execution plan `@c7761a274a432e658df4aee366b50bc900a985a4` independently reread. Exact pre-push tooling trust boundary requires already present **AND preapproved** FFmpeg/FFprobe executable identities. Only one intended production-triggering push/run and artifact upload are authorized; tool-probe-only additional workflow execution and new source/workflow paths are **not** automatically authorized.
- LAB `main@5eab58ea2a5424424cb95f2690654b91395425df`; Canonical and LAB backup releases at `vip-backup-2026-11-06` independently returned `immutable=true`. Earlier Codex report's local folder/repository-search for `DO_NOT_DELETE` is not reliable evidence of backup absence; these are distinct GitHub backup repos/releases.

## Root-cause and safety analysis

The A2 producer is designed to compare the actual hosted `ubuntu-24.04` FFmpeg and FFprobe executable bytes to an **external pre-approved** digest before generation. The intended exact digests were not selected and accepted beforehand, and the runner's future binaries are not available via the local Mac worker SHA. Current GitHub-hosted `ubuntu-24.04` runner image labels do not pin executable bytes; images roll forward. Official GitHub runner image published software manifests are not individual FFmpeg/FFprobe executable SHA-256 attestations, and may not enumerate them. Treat availability, exact versions, actual digest and codec support as `NOT_OBSERVED`, not `MATCHED`.

Reading hash values from the issuer's own first run and then approving those values *retroactively* would defeat the deliberate pre-authorization boundary. Do not set either approved variable to a guessed hash, zero hash, local Mac hash, source-tarball hash, .deb package digest or a SHA reported by the same untrusted producer and claim independent binary authorization. Keep no-push.

**Safe closure sequence, evidence-dependent:**

1. **FIRST seek an existing independently verifiable Ubuntu-24.04 GitHub-hosted runner tool evidence source** (e.g. a prior authenticated current source/runner receipt including actual FFmpeg and FFprobe file-byte SHA-256 and `ImageVersion`). Verify independently selected runner/image, executable paths, signed or reviewed provenance and **separate expected hashes** before configuring the two variables. Public release lists/version-only manifests do not suffice.
2. If no equivalent evidence source exists, design a **separate media-free, read-only tool identity preflight** with its own explicit owner/administrative gate. It may determine the exact installed binary path/size/SHA256, `dpkg` package/version/build identity and runner `ImageVersion` without invoking FFmpeg/FFprobe as processes or handling media. Any required additional GitHub Actions run, new workflow source path, branch push, permissions or network operation is **OUTSIDE** the currently approved exactly-one issuance run; propose a specific owner decision before executing. Do not treat a preflight measurement as immutable future runner identity.
3. Independent reviewer accepts only an externally sourced tool-identity reference under the declared honest-runner threat model, plus exact approval SHA/date/scope/known image/expiry; then the authorized admin may set and read back `BFIRST_B2_APPROVED_FFMPEG_SHA256` and `BFIRST_B2_APPROVED_FFPROBE_SHA256`. At the issuance run, independently remeasure exact binaries **before FFmpeg/FFprobe execution**; mismatches fail closed. Repeated fail-closed issuer runs are not preauthorized.
4. If the future run uses a different hosted image or binaries, fail closed; no automatic reissue. Alternative would be a separately designed and explicitly approved **pinned, authenticated tool distribution** (e.g., immutable CI artifact/container/package) with strict tool source trust, package/network and source ownership scopes. This is not an option to silently substitute existing binaries under Stage A.
5. Do not convert GitHub environment required reviewers into a claimed gate without checking their availability for a **private** repository/plan; such a gate also does not automatically bind tool hashes across different runners.

**Critical caveat:** Hashes from a preflight runner are only a **candidate allowlist**; they must match the actual producer runner executable bytes, and the externally approved provenance of the preflight run/tool identity must be independently reviewed. Same label `ubuntu-24.04` alone is not sufficient. This guard can detect identity drift but cannot ensure stable availability on a moving hosted runner.

## Controller recommendations

- Accept local A1 as **reported** complete; preserve its commit `413d032...` unchanged and unpublished until the exact pre-push gate is satisfied. Do not force a new generator source diff merely to resolve tool identity.
- Conduct a **read-only systematic blocker investigation** in the current native worker or a separate read-only reviewer; no new workflow push, FFmpeg run, repository-admin variable write or code changes while seeking source-verified external reference.
- If a suitable source of two preapproved exact byte SHA-256 values cannot be independently established, return one narrowly scoped **tool identity preflight execution authorization proposal**, not an attempted partial A2 push. Explicitly enumerate the extra run/trigger/path/permissions and the independence/trust/expiration limits.
- Retain operationally distinct `A1_REPORTED_VERIFIED`, `A2_BLOCKED_TOOL_IDENTITY`, `A3_NOT_RUN`; `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`; `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.

**No Canonical/LAB main write, PR, merge, archive/real model/protected media use, FFmpeg invocation, artifact upload/download, force push, branch removal, ruleset modification or backup modification is authorized by this review record.**
