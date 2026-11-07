# VIP B-first A2 — Independent preflight feasibility audit
Date: 2026-11-07 (Europe/Istanbul)
Status: A2_BLOCKED_TOOL_IDENTITY; A3_NOT_RUN; STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED.

## Repository verification
- LAB design commit 58482251020713ccb4053ce14a98506739e3ed27 and tree d9c0a3e6b458e0da6cbc31a3a91677804e681fb5 VERIFIED by GitHub. Its net difference to LAB main 5eab58ea2a5424424cb95f2690654b91395425df is exactly one new design document, with two commits.
- The claimed remote design branch review/vip-bfirst-a2-ffmpeg-tool-identity-preflight-design-20261107 returned 404, and search for matching branches returned zero. Exact commit/file remain accessible. Thus BRANCH NOT VERIFIED; do not assume why or recreate it by force.
- Canonical main 3bfcc2ba221b36df6773e630b44479ec961d630a, prior B-first source candidate cac74495d80d9eaa144a12e9aa67eba78ba2f062 unchanged. A1 producer 413d032e5635e4d8670e5565856f7fcfcfaca3ff is REPORTED locally and unavailable from remote GitHub (422); remote issuance branch absent (404).
- Canonical issuance-branch ruleset 26738994 independently observed active and correctly scoped to the issuance branch only; it does not cover a new preflight branch. Both DO_NOT_DELETE backup release records returned immutable=true.

## Material finding F1: egress limitation
GitHub documents that default hosted runners have public internet access. Workflow permission scopes such as permissions: {} restrict GITHUB_TOKEN, NOT network egress. A dedicated private-networking runner / eligible VNET with outbound policy can provide an independent control, but no such control was observed for this Canonical environment.
Official: https://docs.github.com/en/actions/concepts/runners/private-networking
Official: https://docs.github.com/en/organizations/managing-organization-settings/about-azure-private-networking-for-github-hosted-runners-in-your-organization
Under the proposed design's hard requirement that unrelated egress is demonstrably blocked, do NOT push a preflight workflow on an ordinary unisolated hosted runner. This is a true feasibility blocker, not proof of malicious egress.

## Material finding F2: rerun guarantees
GitHub allows repository writers to rerun workflows and jobs. A run_attempt == 1 first-step guard can refuse measurement on later attempts, but cannot prevent a new attempt from being scheduled.
Official: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs
If the requirement means absolutely no second platform attempt, the proposed standard hosted workflow cannot enforce it. A more implementable explicitly approved definition is AT MOST ONE AUTHORIZED TOOL-BYTE-MEASUREMENT BODY (all later attempts abort before bytes read). This is NOT the same as asserting only one workflow attempt can ever exist.

## Material finding F3: preflight identity is not lasting issuer identity
Even independently reviewed preflight FFmpeg and FFprobe executable SHA-256 values are candidate expected hashes on a moving ubuntu-24.04 image. The later producer must hash actual resolved file bytes before execution and refuse mismatch. A matching executable hash alone does not pin dynamic runtime libraries or codec capability; image version, linkage, package identity and bounded decode remain distinct measurements. An honest-runner trust assumption must be explicitly declared. Do not approve expected hashes from the production issuer itself.

## Directly measured, read-only local alternative: supplied Linux tool archive
The Project uploaded ffmpeg-n9.0-latest-linux64-gpl-9.0.tar.xz was inspected without executing binaries, installing packages, network access, or writing/extracting files on disk. Archive file SHA-256: 0fdfc7026aa120390715a88f13aa367b583f91ca2d94808ab1a5ec381b10aacb.
Embedded bin/ffmpeg: 171561896 bytes, SHA-256 1e0dd2fad53e07cfff59edd0ecf7b332c80ea146983ddeddceb50990ff6c95d4.
Embedded bin/ffprobe: 171332456 bytes, SHA-256 0eddabd2ffd9f5fbc624b5a42c01df30c728b1cbbf4e450e7d0e920ff732a348.
A separate uploaded ffmpeg-9.0.1.tar.xz has source-archive SHA-256 cf38e0e28c7e5605942c4a77755349b0145804a397af37eb1fb4c77cb237f635; source archive digest is not a compiled executable digest.
These are MEASURED uploaded-file bytes only, NOT authenticated origin, approved tool identity, ubuntu-24.04 compatibility, confirmed static linkage, proven codec support, or current hosted-runner executable identity. Do not set existing BFIRST_B2_APPROVED_FFMPEG_SHA256 or BFIRST_B2_APPROVED_FFPROBE_SHA256 to them. They offer a concrete Strategy C provenance-and-distribution investigation candidate, not automatic authorization to use these binaries.

## Recommendation and exact owner decision frontier
A: Existing independent hosted Ubuntu tool receipt remains NOT_OBSERVED.
B: Minimal media-free hosted preflight is proportionate to one developer-only synthetic MP4, but only if the Owner explicitly accepts a bounded honest-runner model with no enforced egress isolation, with reviewed no-network/no-secret/no-download code and with at-most-one authorized measurement body rather than the unattainable claim that no second platform attempt could be launched. After external hash review and Owner approval, a later A2 producer must rehash binaries before execution and stop on mismatch. Separate source/workflow branch, actor controls, expected-source SHA, reviewer and one intended extra preflight run require exact authorization.
C: If enforced network isolation and stronger reproducibility cannot be relaxed, evaluate separately authenticated pinned binary distribution or genuinely network-restricted runner. Uploaded Linux archive is not yet authenticated or eligible for silent substitution in A1; adoption would require a newly scoped source/CI contract and fresh TDD/review.

No first issuance push, additional workflow run, repo setting mutation, archive installation, binary execution, model/provider call, real/protected media, Stage B/C, main merge, PR or Gate promotion occurred. User's design result is not by itself permission for any new operational preflight or relaxation.

Terminal: BFIRST_A2_PREFLIGHT_DESIGN_REVIEWED_WITH_NETWORK_AND_RERUN_BLOCKERS; A2_BLOCKED_TOOL_IDENTITY; A3_NOT_RUN; STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED; CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT.
