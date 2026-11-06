# VIP CORE-02 — B-first trusted synthetic fixture manifest: bounded execution plan

> **For Codex:** Follow the approved design and Superpowers trigger-based workflow: TDD for behavior, systematic debugging for unexpected failures, verification-before-completion, independent feature-level review. Current Canonical `AGENTS.md`, global writer/lease rules and native-thread runbook outrank this plan. No source code was modified when writing this plan.

**Date:** 2026-11-06  
**Plan state:** OWNER APPROVED ARCHITECTURE; BOUNDED SYNTHETIC CODE CANDIDATE ONLY. NO MAIN INTEGRATION.  
**Approved governing decision:** LAB `docs/decisions/2026-11-06_CORE02_BFIRST_TRUSTED_FIXTURE_MANIFEST_OWNER_ADOPTION.md`, same decision branch.
**Proposed design:** LAB `docs/superpowers/specs/2026-11-06-vip-core02-trusted-synthetic-fixture-provenance-design.md` at `785b3f8384f733f11bf98949328452cd17bb61ef`.
**Canonical code base:** `Centaurioun/video-intelligence-pipeline@215ec88270a2437a746fbab1f4842b83ee11c512`, tree `6a07cdfcc8807db4ed2142f4a9874241b3c85007`.
**Canonical protected main:** `3bfcc2ba221b36df6773e630b44479ec961d630a`.
**Historical CORE-01 interval:** `BLOCKED_BY_CONTRACT`.

## Goal and hard boundary

Implement and independently verify the **smallest closed, versioned, repository-pinned fixture manifest admission primitive**. A trusted policy supplies which named source may be read; a digest verifies the bytes from the authorized source. A source-provided JSON grant, claimed `source_kind=synthetic`, filename, codec, FFprobe and a SHA calculated by pre-reading an arbitrary path are never sufficient to authorize strict source reads. Do not claim immunity to an adversary who can change all local trust anchors.

**A first-source read is lawful only after a separately selected, immutable trusted policy has authorized that precise occurrence/path and purpose.** The subsequent bounded descriptor-relative source read is for matching already authorized bytes to the manifest, not for retroactive permission.

**First execution slice deliberately excludes real-media decoding, dynamic video generation, real models, real archive, provider, Gate, rendering, production and main merge.** Retain existing developer-only test flow as lower assurance, never trusted admission.

## Exact allowed source owner for first implementation slice

- NEW: `src/vip_fvs/trusted_fixture_manifest.py` (bounded read-only policy/manifest resolver, fixture ID selection, path-independent source preauthorization and descriptor-relative bounded verification).
- NEW: `tests/vip_fvs/unit/test_trusted_fixture_manifest.py` (RED/GREEN, adversarial source read order and forgery/refusal tests).
- NEW (JSON only, optional if it can be linked to a real reviewed Git object): `tests/vip_fvs/fixtures/trusted_fixture_manifest.v1.json` (versioned closed allowlist for the existing **JSON timing descriptor** fixture identity; `artifact_kind=timing_descriptor` must NEVER authorize video decode/index).
- Existing `tests/vip_fvs/fixtures/cfr_4s_shape.json`, `vfr_nonuniform.json` may be **read, not modified** for a frozen policy test. Their `materialize.py` emits JSON descriptors, NOT video; no MP4 file is present in the pinned fixture tree.
- Existing `src/vip_fvs/{cli.py,core_analysis.py,core_report.py,query_analysis_authorization.py,source_snapshot.py,real_source_probe.py}` and `docs/architecture/CANONICAL_CONTRACTS.md` are READ-ONLY in this first slice. Do not add `--fixture-id` or modify `analyze-local` until the separately required pinned **video** fixture, policy identity, runtime proof and full caller-flow design exist. This avoids a fake "trusted end-to-end" demonstration.
- If minimal correct implementation needs other source/code paths, stop as `BLOCKED_BY_SCOPE` with exact source evidence; broad user approval cannot substitute for a verified shared-contract owner or a named source-write packet.

## Task 0 — VERIFY current Git and resource ownership

- [ ] Read Canonical `AGENTS.md`, `docs/INDEX.md`, four project handoffs, `CODEX_NATIVE_THREAD_OPERATIONS_RUNBOOK.md`, `CANONICAL_CONTRACTS.md`, current corpus admission, source snapshot and bounded-admission rules and current GitHub HEAD for main, repaired CORE-02 candidate and owner adoption.
- [ ] Inspect native create-thread tool's exact live schema, project ID/branch base and exclusive writer leases; if an isolated verified native worker cannot be created, report `BLOCKED`.
- [ ] Create a **fresh clean isolated Canonical native worktree** from EXACT `215ec88270a2437a746fbab1f4842b83ee11c512`, suggested unique `feature/vip-core02-bfirst-fixture-manifest-20261106`. Keep previous dirty worktrees and remote main untouched.
- [ ] Establish exact Git tree, clean status, unique branch, isolated worktree binding, no path collisions and valid current contract fingerprints.
- [ ] Independently verify the existing Canonical repository has *no pinned actual video media fixture* under `tests/vip_fvs/fixtures/`. If different, update the evidence record before changing scope. No generated MP4 can be retroactively 'trusted' solely by creating a matching manifest during its own test.

## Task 1 — Closed policy and trust anchor contract

- [ ] Specify small strict V1 manifest schema: schema/version, policy_id, assurance_profile=`REPOSITORY_POLICY_ACCEPTED`, immutable `policy_revision`/Git object identity selected *outside the payload*, exact fixture IDs, relative locators under policy-owned root, exact expected SHA-256 and byte counts, artifact_kind, authorized operations/purposes and finite byte limits. Use canonical, duplicate-key-rejecting JSON and closed keys.
- [ ] RED: tests that malicious or erroneous payloads cannot self-select their own trust anchor; an unpinned policy, unrecognized policy revision, malformed JSON, duplicate fixture IDs, duplicate JSON keys, path traversal, Symlink root/ancestor, unknown ID, wrong purpose, wrong type, revoked/expired policy if supported, or untrusted arbitrary `--source` fail **before first source byte read or FFprobe**.
- [ ] GREEN: implement only the minimum policy-resolution and frozen-ID-to-allowed-locator lookup. The invoking runner must supply the expected trusted revision/digest independently from untrusted manifest contents. Require an explicit immutable anchor/pinned Git object; do not automatically trust the current mutable checkout manifest or use a manifest-provided digest as its own authority.
- [ ] Check identical digest at a different occurrence and a grant replay for a new query/output as separate custody cases. A hash match must never authorize an unknown occurrence.

## Task 2 — Bounded authorized byte measurement

- [ ] RED: tests for wrong expected SHA, wrong byte count, broken/symlink/changed path, nonregular file, file replacement during read, over-budget source, hardlink/same-digest second occurrence, unsupported artifact kind and unsafe parent components. Use generated local synthetic bytes/JSON, no real video.
- [ ] GREEN: integrate existing bounded descriptor-relative no-follow source admission primitive if its **current** exact interface and owner's separate Gate scope permit reuse; if integration requires unauthorized changes, implement only the minimal read-only primitive with finite cap, precise file-object identity and fail-closed TOCTOU checks. No approximate pointer/source replacement.
- [ ] Check that the chosen policy authorized the exact path, operation, artifact kind and size BEFORE reading, and measured SHA validates the allowed bytes. Ensure permitted `timing_descriptor` reads can be tested as such, but are **not** eligible for MP4 probe/index.
- [ ] Preserve evidence classes: byte counts/hash/probe `MEASURED`; matching against trusted policy `MATCHED`; `NOT_OBSERVED` only an availability marker. A manifest receipt is not a REAL-mode permit.

## Task 3 — End-to-end refusal and compatibility verification

- [ ] Test that a self-consistent, forged `SYNTHETIC_FIXTURE_ONLY` grant plus arbitrary source cannot obtain `TRUSTED_MANIFEST_ACCEPTED`; merely marking `source_kind=synthetic` is not admission.
- [ ] Test that the current legacy `analyze-local` developer-only pathway does NOT get the new trusted profile without explicit strict manifest selection and attested source read. If preexisting code currently reports no trusted profile, verify that fact without modifying legacy CLI in this slice.
- [ ] RED/GREEN test manifest accepted JSON timing fixture and refused media operation; do not claim `analyze-local` strict successful retrieval without an immutable reviewed video fixture.
- [ ] Evaluate whether useful fixed video test asset exists outside the pinned fixture directory. DO NOT import/register/inspect real or protected media; new static tiny video bytes require separate exact source provenance and reviewing process, not fabricated fixture status.
- [ ] Capture any inability to establish a separate, immutable policy selection mechanism as `BLOCKED_TRUST_ANCHOR`, and no-fixture product-path outcome as `BLOCKED_NO_PINNED_VIDEO_FIXTURE`. These are legitimate partial outcomes, not reasons to weaken the gate.

## Task 4 — Regression, review, durable candidate handoff

- [ ] Run new first-slice RED/GREEN tests on installed Python 3.11/3.14, relevant `core_report`, existing `query_analysis_authorization`, `core_analysis`, `test_core_analyze_local_cli`, source-snapshot and corpus-admission tests where applicable. Record PASS/FAIL/SKIP/XFAIL. No model download/loads; use synthetic data only.
- [ ] Compare unexpected regressions against exact `215ec882...` baseline with same runtime/pytest. Historical 3.11 8 failures and 3.14 7 failures were reported on earlier commits; do not assume baseline results without comparison.
- [ ] Use `compileall`, `git diff --check`, security/secret checks and current feature verifier. Do not call missing reference-pack presence PASS.
- [ ] Commit and push a unique isolated Canonical development branch normally (no force), run relevant GitHub **synthetic smoke** CI on final exact SHA when available; state CI coverage limits. Obtain fresh independent code review on final source SHA.
- [ ] Report in Turkish: actual thread/worktree, base and final SHA/tree, added/modified paths, independent selected trust-anchor mechanics, source-read ordering tests and forgery refusals, model-free/legacy boundaries, current fixture inventory and whether strict video E2E is blocked, Python 3.11/3.14 tests, CI, reviewer disposition and remaining blockers.
- [ ] Status `BFIRST_MANIFEST_PRIMITIVE_VERIFIED` only when implementation tests, reviewer and immutable-policy proof pass. Otherwise `BFIRST_MANIFEST_PRIMITIVE_PARTIAL`; independently always report `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED` if no exact approved media fixture exists. `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT` remains open.
- [ ] STOP without PR, main merge, Gate promotion or production enablement. Neither the manifest test nor historical CODEX verifier claims automatically authorize full product/pilot.

## Rejected shortcuts

- User-provided JSON SHA-256 proves **integrity**, not source-generation origin or trusted issuance.
- Self-computed manifest `policy_digest`, hard-coded mutable checkout path, modified current checkout, file extension, codec or pixel heuristic are not independent admission authority.
- Fixture created dynamically by a test and blessed by manifest generated in the **same invocation** is not a B-only immutable allowlist.
- Adding source media, authentic model, protected archive, new FFmpeg generator runtime, signed receipts, legacy contract rewrite, source occurrence schema migration or a broad CLI refactor is out of scope.

**Plan terminal:** `CORE02_BFIRST_SYNTHETIC_MANIFEST_TDD_PACKET_READY`, no canonical main write/merge.
