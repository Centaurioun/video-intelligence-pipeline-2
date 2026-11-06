# VIP CORE-02 — Pinned fixture anchor and bounded re-entry after BLOCKED_TRUST_ANCHOR

**Date:** 2026-11-06  
**Disposition:** DESIGN/EXECUTION CLARIFICATION WITH VERIFIED GIT OBJECTS — bounded developer-only B-first admission primitive may be attempted; **NO protected source, model, main merge, production, Gate or real workflow authority**.  
**Starting evidence:** Codex handoff `BFIRST_MANIFEST_PRIMITIVE_PARTIAL / BLOCKED_TRUST_ANCHOR` in local native worker `01a1b24d-9862-7ab2-a569-e11d83c8b71e`; this local claim is REPORTED, not independently verified. Github confirms remote branch `feature/vip-core02-bfirst-fixture-manifest-20261106` **does not exist** and Canonical main is unchanged.
**Governing approval:** `docs/decisions/2026-11-06_CORE02_BFIRST_TRUSTED_FIXTURE_MANIFEST_OWNER_ADOPTION.md` and exact B-first TDD and ownership packet in predecessor LAB branch `decision/vip-core02-bfirst-trusted-fixture-manifest-20261106@8de8664c8ce8501f86d484b63389f8d1a1c95fec`. The owner broadly approved continuation within this B-first synthetic path but did not identify a protected, independent signer or trusted CI release, so no such trust root is asserted.

## Verified immutable developer-reference anchor — narrow threat model only

The external controller/task packet chooses the following **exact Canonical source commit and Git blob object IDs** independently of the candidate manifest JSON and source-provided grant. These are explicit reviewed Git references for the **honest/developer-misconfiguration** threat model only:

- Repository: `Centaurioun/video-intelligence-pipeline`
- Frozen source commit: `215ec88270a2437a746fbab1f4842b83ee11c512`
- Frozen source tree: `6a07cdfcc8807db4ed2142f4a9874241b3c85007`
- Allowed fixture root relative to that tree: `tests/vip_fvs/fixtures/`
- Fixture `cfr_4s_shape`: `tests/vip_fvs/fixtures/cfr_4s_shape.json`; Git blob `ed7780041be153138273848359c8e368493d3057`; 1,834 bytes; `artifact_kind=timing_recipe_json`
- Fixture `vfr_nonuniform`: `tests/vip_fvs/fixtures/vfr_nonuniform.json`; Git blob `bbb8374548bb2021f9fd62c9c8e2cc6cfeb6c68b`; 1,294 bytes; `artifact_kind=timing_recipe_json`
- Existing `tests/vip_fvs/fixtures/materialize.py`: Git blob `91a176e1d046e9c85fae5c194443db42b7ffd4a5`; emits a JSON descriptor, **not any video bytes**.

The above blob IDs and lengths were independently retrieved from GitHub's recursive Git tree of the exact frozen source commit. The SHA-256 byte digests of the fixture files are NOT asserted here without independent raw-byte verification: the worker must derive each only after verifying the pinned Git blob object identity (`git cat-file`/`git hash-object` on a read-only exact object) and then freeze/record the content SHA-256 in the closed reviewed allowlist. No editable manifest may supply **its own authoritative expected digest**. The Git blob SHA-1/Git object ID and expected SHA-256 have distinct roles.

**Crucial authority distinction:** Under this limited threat model, the *controller-selected frozen Git source identity and allowlist* can be the low-assurance development trust anchor; `open_trusted_root()` in `bounded_admission.py` only constructs a filesystem capability and does NOT independently decide whether a path or policy is authorized. This is sufficient for an auditable, reviewed **component contract test**, not for a tamper-proof trust guarantee when the same user can alter the local checkout, runner, code and object database. A genuinely protected release/CI root is NOT_OBSERVED and must not be invented.

## B-first first-slice implementation route (no new shared source owners)

1. Use current owner-approved source scope: new `src/vip_fvs/trusted_fixture_manifest.py` and `tests/vip_fvs/unit/test_trusted_fixture_manifest.py`, and only optionally new `tests/vip_fvs/fixtures/trusted_fixture_manifest.v1.json`. Everything else read-only.
2. Root the trusted low-assurance **closed fixture table** in exact controller-pinned commit/path/blob identities above, e.g. reviewed constant owner policy inside the new module, or require an explicit externally selected sealed policy identity from the controller/test runner. The latter must not be a user-controlled field, a self-hash inside the JSON, or the same object offered as its own proof.
3. If using optional JSON manifest, authenticate it against the independently frozen policy selector/digest from the trusted controller module or task packet. If neither a fixed table nor a verified external selector is usable under the exact permitted source-owner scope, keep `BLOCKED_TRUST_ANCHOR`; do not weaken this rule.
4. Only after authorizing `fixture_id`, relative locator, allowed `artifact_kind`, purpose, source occurrence and operation, open the pre-authorized file by the existing `TrustedRoot`/bounded descriptor-relative/no-follow primitive and verify its measured SHA-256 and size against the *frozen* policy. This read is not permission to discover arbitrary content.
5. Reject wrong IDs, wrong content, forged grants, swaps, symlinks, unsupported operation, unknown roots or provenance. Tests should prove **zero input source bytes read** for unauthorized requests (the known policy/commit object may be read as administrative policy evidence).
6. `timing_recipe_json` cannot authorize FFprobe, video decode/index, model or REAL mode; do not claim `TRUSTED_ANALYZE_LOCAL_VIDEO`. The current B-first video outcome remains `BLOCKED_NO_PINNED_VIDEO_FIXTURE` / `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`.
7. Do NOT add a dynamic FFmpeg generator, alter `src/vip_fvs/cli.py`, change `query_analysis_authorization.py`, migrate schema, or create an input-mislabeling bypass just to green the tests. Such changes need a separately authorized versioned integration decision.
8. Source code TDD, Python 3.11/3.14, current-source contract review, independent peer review at exact candidate SHA, and non-force isolated candidate-branch push remain mandatory before claiming the bounded verifier itself verified.

## Local main process deviation: evidence, not repair authority

Codex reported that during required sync it **fast-forwarded local `main`** from `c9d0daffbe8c599a8c65891e69d108c3169f8eb9` to `3bfcc2ba221b36df6773e630b44479ec961d630a`. Earlier task packets explicitly prohibited changes to local `main` and existing dirty worktrees. If that occurred as reported, it is a **process scope deviation even if the fast-forward was non-destructive**. GitHub cannot independently verify that local ref, status or reflog. Do not automatically reset/revert local main or rewrite history. The Controller must collect read-only evidence (`git show-ref --verify refs/heads/main`, `git status --porcelain=v1` in the existing checkout, `git worktree list --porcelain`, `git reflog -n 5 refs/heads/main`), record the exact operation that moved the ref and ensure future feature work uses isolated candidate refs only. If any shared-contract/dirty worktree loss is detected, stop and escalate.

## Entry and exit status

- Verified GitHub now: Canonical main `3bfcc2...`, digest-repaired CORE-02 `215ec882...`; LAB main `5eab58...`; two immutable backups. Local worktree claim is REPORTED only. No published B-first branch exists.
- **Next task:** resume B-only **manifest verifier component** against the concrete pinned Git blob anchor above, not a self-minted manifest. This is not new real source authorization.
- If verifiable under the allowed narrow module/test scope and independently reviewed: `BFIRST_MANIFEST_PRIMITIVE_VERIFIED`, **with explicit** `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`.
- Otherwise: `BFIRST_MANIFEST_PRIMITIVE_PARTIAL / BLOCKED_TRUST_ANCHOR`, not a fabricated success.
- Always: `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`; no Canonical/LAB main merge, protected/real media, model/provider call, Gate promotion, production export or destructive Git.

**Terminal:** `VIP_CORE02_BFIRST_PINNED_DEVELOPER_REFERENCE_PROPOSED_FOR_BOUNDED_REENTRY` — no claim of independent tamper-proof policy authority.
