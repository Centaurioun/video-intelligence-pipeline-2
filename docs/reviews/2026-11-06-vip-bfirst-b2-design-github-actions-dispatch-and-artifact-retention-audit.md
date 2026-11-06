# VIP B-first — Independent B2 synthetic video fixture design audit

**Date:** 2026-11-06  
**Review scope:** Independent GitHub read-only verification of exact design/code refs, GitHub workflow source, and public GitHub Actions documentation; no video bytes generated, FFmpeg invoked, model loaded, new workflow installed, artifact uploaded, PR or main merge.  
**Disposition:** `B2_DESIGN_CONDITIONALLY_SUPPORTED` — one operationally material pre-issuance correction required (`workflow_dispatch` on a new feature-only workflow), plus explicit fixed-run artifact issuance/review/retention policy. `STAGE_A_NOT_AUTHORIZED_FOR_EXECUTION_BY_THIS_AUDIT`.

## Exact GitHub verification

- LAB `design/vip-bfirst-pinned-synthetic-video-fixture-20261106` HEAD `4bec4ef197539781c47ae1ea63b7fb4ffcbdb229`; tree `96c818c842d5badd5105142df83757266124c8f2`.
- LAB baseline/main `5eab58ea2a5424424cb95f2690654b91395425df`: compare shows **four commits ahead**, with a net difference of **one new design document**. The final commit itself edits that document; do not incorrectly describe the entire branch as a single-commit history.
- Exact document `docs/superpowers/specs/2026-11-06-vip-bfirst-pinned-synthetic-video-fixture-and-strict-admission-design.md`; Git blob `fdfbf2e60adabbc22a0aa60b70f179416482b26e`. Independent SHA-256 of GitHub-fetched UTF-8 bytes: `7ca2da061f6e290fbdcbe4debf470ea8480ae6d23aa2bcca86c6abb8baa63c2c`, exactly matching Codex report.
- Canonical main `3bfcc2ba221b36df6773e630b44479ec961d630a`; B-first code successor `cac74495d80d9eaa144a12e9aa67eba78ba2f062`; LAB main unchanged. Both DO_NOT_DELETE backup GitHub releases returned `immutable=true`.
- Independent reviewer `NO_MATERIAL_FINDING`, equal LAB verifier baseline-versus-candidate 26 errors, secret/diff check, and native worker/worktree identities are **Codex-reported** and not independently reproduced here. No runtime/media CI was claimed for the design task.

## Positive design evaluation

- B2 avoids committing media binary objects where Canonical `tests/gate0/media/generated_media.py` explicitly prohibits checked-in generated media. A B1 Git blob is not independently permitted simply because its byte count is small.
- A single proposed 64×64, 10-second, 4-fps, 40-frame, one-video/no-audio MP4 with finite 65,536-byte ceiling is intentionally minimal. The 4.5-second default sampler makes two or more candidate sample opportunities plausible, but **final sample PTS/stream index/size/codec are NOT_OBSERVED**, not mathematical deductions from nominal FPS.
- Separates CI artifact **ZIP archive digest** from the **raw extracted MP4 SHA-256**, and producer workflow/run/artifact IDs from the separate reviewed policy identity.
- Treats github.com artifact upload immutability as **immutable until deletion/expiry**, not perpetual availability. Local verification must refuse missing/expired/mismatched archive, unexpected members, and raw-file digest/size mismatch; no silent replacement or regeneration. GitHub's repository's actual retention setting has not been independently observed.
- Requires private verified snapshot prior to path-based FFprobe/decoder reads; correct given existing `real_source_probe.py` reads the provided pathname before/after probe and passes it to FFprobe. Maintains no arbitrary-source fallback, fake-only embeddings, matched POINT vs measured PTS/timebase, report digest, and legacy CORE-01 blocked state.

## F1 — New workflow cannot be dispatched exclusively from an unpublished feature branch — MATERIAL PRE-ISSUANCE FIX

The Stage A outline proposes a **new** `.github/workflows/bfirst-pinned-video-issuance.yml`, while Canonical `main` must remain unchanged and no PR/merge is authorized. GitHub's current documentation explicitly states that a workflow accepting `workflow_dispatch` must **exist on the repository's default branch** to be triggered manually: 

- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow
- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onworkflow_dispatch

The current Canonical `.github/workflows/python-synthetic-smoke.yml` exists on main and supports `workflow_dispatch`; this historical success **does not imply a NEW feature-only workflow would be dispatchable**.

**Required design amendment:** Choose a **feature-branch `push` trigger** constrained to a uniquely owned issuance branch/ref (and reviewed path conditions, producer SHA, finite permissions/resources), or another verified legally authorized existing workflow/reusable-workflow trigger path. GitHub's normal `push` workflows are discovered from the event's commit/ref and do not have the `workflow_dispatch` default-branch prerequisite. Explicitly check current GitHub workflow event semantics and native environment before execution. Do not quietly merge the workflow to `main`, create an unauthorized PR or change existing CI just to enable manual dispatch.

The branch push will itself trigger the issuance workflow; therefore do not push until the exact trigger and bounded FFmpeg/output/tool permissions have been independently reviewed, source ownership and Owner operational issuance permission explicitly established, and the immutable branch SHA pinned. The resulting run must be bound to that **producer SHA**, not a later receipt commit.

## F2 — Issue/attest the reviewed artifact in two distinct identity steps

One workflow can both generate video and upload an artifact; its self-written receipt is **not independent publication authority**. Producer outputs and log/report can provide MEASURED byte/tool fields, but independent reviewer/controller must subsequently verify:

1. Workflow source SHA and producer event/ref/permissions; run ID, artifact ID and archive digest returned by GitHub.
2. Artifact download ZIP integrity, the expected single member `bfirst_tiny_video_v1.mp4`, absence of unexpected files/path traversal, raw MP4 SHA-256/byte length, and independent bounded decode/PTS/timebase evidence with tool IDs.
3. Separate owner-reviewed **pin record** (e.g. a documented verified manifest/receipt candidate), created only *after* run/artifact identifiers exist and checked against the GitHub API. The code/receipt may record claims but cannot auto-approve the policy it just minted.

Do not create a second commit to the producer branch that obscures which exact workflow revision generated the artifact; use a separate controlled read-only review/pin branch or explicit commit/review chain with precise stage owners. No Stage B manifest registration until independent acceptance of Stage A.

## F3 — Retention and local-first limitations

GitHub Actions artifacts are **time-limited and deletable**. `retention-days` cannot exceed repo/org policy, which remains `NOT_OBSERVED`. A long-lived strict fixture cannot assume the artifact will exist indefinitely: provide a documented expiry gate and future separately reviewed reissuance/version policy, or record that long-term offline regression becomes `BLOCKED_NO_PINNED_VIDEO_FIXTURE` once the selected trusted pin is no longer reachable under the chosen policy. This is a product/maintenance tradeoff, not a security break in the approved temporary developer test boundary.

Source reference: https://docs.github.com/en/actions/tutorials/store-and-share-data

## F4 — Resource/version/decoder assumptions

- The proposed `65,536`-byte cap is a **rejection threshold**, not a measured expected size. Initial FFmpeg/FFprobe absolute executable version/hash/toolchain and codec support must be measured at the permitted CI runner; `ubuntu-latest` is a moving OS image, not a stable executable identity.
- Record the exact resolved action implementation identities, especially upload action v4+ (version labels may resolve to new commits). Verify archive digest semantics against bytes actually re-downloaded instead of assuming the archive digest equals raw MP4 digest.
- Existing Mac-specific integration test hardcodes `/opt/homebrew/bin/ffmpeg` and thus cannot prove Ubuntu CI decode acceptance. The proposed CI-generated video must undergo actual bounded inspect on the authorized target CI environment.
- Do not allow an issuer to select arbitrary source-file paths, external URLs, codecs, shell fragments or output locations; generated lavfi inputs must be constrained at the code boundary.

## Recommendation / next exact action

1. **Revise the proposed B2 design** with a branch-only push-trigger feasibility plan and explicit post-upload independent pinning; preserve original frozen design SHA and rejected alternatives.
2. Complete a **bounded Stage A authority packet** specifying only one generated synthetic video, exact allowable future source/workflow/receipt/test paths, bounded FFmpeg/FFprobe execution, one artifact upload/download, finite resource lease, producer/ref/permissions/retention conditions, and clear stop states. This audit does **not** execute or authorize such operations by itself.
3. After explicit Stage A operational authorization, one isolated issuer worker and one independent reviewer may perform future generation under current repository resource rules. Do not overlap artifact issuance with Stage B policy registration or Stage C strict CLI without their own accepted artifacts and task packets.
4. No B2-to-B1 fallback without a formal policy exception. Neither the current design nor this review authorizes protected/archive video, models/providers, production, Gate promotion or Canonical/LAB main writes/merge.

**Terminal:** `BFIRST_B2_DESIGN_REVIEWED_WITH_F1_DISPATCH_BLOCKER`; `STAGE_A_SOURCE_EXECUTION_PENDING`; `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`; `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.
