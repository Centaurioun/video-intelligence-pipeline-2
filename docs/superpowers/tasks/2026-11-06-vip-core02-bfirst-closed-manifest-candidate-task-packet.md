# VIP CORE-02 — B-first manifest candidate: exact write packet

**Date:** 2026-11-06  
**Status:** OWNER-APPROVED B-FIRST SYNTHETIC CODE SLICE; READ/WRITE BOUNDARIES FROZEN FOR THIS PACKET.  
**Decision:** `docs/decisions/2026-11-06_CORE02_BFIRST_TRUSTED_FIXTURE_MANIFEST_OWNER_ADOPTION.md`.  
**Plan:** `docs/superpowers/plans/2026-11-06-vip-core02-bfirst-trusted-fixture-manifest-synthetic-tdd-plan.md`.  
**Source base:** Canonical `215ec88270a2437a746fbab1f4842b83ee11c512`, tree `6a07cdfcc8807db4ed2142f4a9874241b3c85007`.  
**Canonical main:** `3bfcc2ba221b36df6773e630b44479ec961d630a` (read-only).  
**LAB main:** `5eab58ea2a5424424cb95f2690654b91395425df` (read-only).  
**Candidate branch (suggested):** `feature/vip-core02-bfirst-fixture-manifest-20261106` in isolated Canonical native worktree.

## Exclusive allowed writes

1. `src/vip_fvs/trusted_fixture_manifest.py` — NEW.
2. `tests/vip_fvs/unit/test_trusted_fixture_manifest.py` — NEW.
3. `tests/vip_fvs/fixtures/trusted_fixture_manifest.v1.json` — NEW OPTIONAL, JSON only; never claim it is independently trusted until an immutable reviewed policy selection/check is verified.

All other source, tests, `AGENTS.md`, Git governance, CI workflows, input media and original clean/dirty worktrees are read-only. No touching `src/vip_fvs/cli.py` or replacing existing `query_analysis_authorization.py` in this first slice. No source media/artifact/binary additions, model loads/downloads or protected reads. No network egress except approved GitHub branch publication/synthetic CI. Do not create a PR or merge. Do not edit either DO_NOT_DELETE backup.

## Permitted finite checks

- Read-only Git inspection: `git status --porcelain=v1 --untracked-files=all`, `git rev-parse HEAD`, `git rev-parse 'HEAD^{tree}'`, `git worktree list --porcelain`, `git diff --check`, `git diff --name-status` and GitHub remote ref verification.
- Focused tests using already installed environments: `PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_fvs/unit/test_trusted_fixture_manifest.py`; related `core_report`, `query_analysis_authorization`, `core_analysis`, `test_core_analyze_local_cli`, source-snapshot/corpus-admission unit tests.
- Broader test/regression suites on Python 3.11/3.14 **only where already available**; bounded by current resource-policy v5 leases. `compileall`, diff check, tracked secret scan and required native feature-worktree verifier.
- Read-only comparison against exact source base when unexpected failures appear. No dependency downloads, model downloads, arbitrary FFmpeg/video work or fixture media generation required for this slice.
- Non-destructive commit and normal push on owned isolated Canonical candidate branch; synthetic GitHub Actions at its immutable candidate SHA. Code review by independent native feature reviewer with its own verified clean read-only worktree.

## Admissible implementation and stop gates

- Strict policy is selected from independently pinned reviewed Git object/CI fixture authority, NOT from arbitrary manifest/grant bytes. If no trusted revision-binding mechanism exists or can be proven without changing more source paths, STOP `BLOCKED_TRUST_ANCHOR`.
- Only fixture IDs present in a closed versioned allowlist and paths under its reviewed root can be authorized *before* source read. Exact SHA/size verified with bounded no-follow descriptor after preauthorization; no validation by reading arbitrary unauthorized bytes.
- Existing JSON-only timing fixture is allowed only as `timing_descriptor`, never an eligible video. In the current source census, no pinned video fixture exists; strict video E2E must remain `BLOCKED_NO_PINNED_VIDEO_FIXTURE` / `NOT_OBSERVED`. No false product certification.
- Do not treat self-authored `SyntheticFixtureGrant` as trusted issuer; existing CLI developer synthetic path remains unchanged and lower-assurance. Do not enable REAL mode.
- TDD proof includes explicit behavioral RED and GREEN for source-read order, forged grant, policy path/ID, SHA/size, scope, occurrence, symlinks/races, unknown fixture, nonvideo refusal. Independent code review on exact final SHA.
- Any need to change shared API, CLI/authorizations, canonical main, data policy, runtime provider, video source binaries or generation tooling requires a new exact separately reviewed task packet. The owner's broad future approval statement is not authority to bypass a concrete safety/ownership boundary.
- Final status may be `BFIRST_MANIFEST_PRIMITIVE_VERIFIED` only if isolated source implementation, reliable trust-policy binding proof, tests and review pass. Otherwise `BFIRST_MANIFEST_PRIMITIVE_PARTIAL` with exact causes.

**Terminal:** `VIP_CORE02_BFIRST_INITIAL_SYNTHETIC_WRITE_PACKET_ISSUED` — NO MAIN MERGE.
