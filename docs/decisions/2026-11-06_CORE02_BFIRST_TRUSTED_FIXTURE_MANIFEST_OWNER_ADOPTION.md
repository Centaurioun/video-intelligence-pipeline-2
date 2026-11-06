# CORE-02 — B-first closed synthetic fixture manifest adoption

**Date:** 2026-11-06  
**Status:** OWNER APPROVED — B-FIRST ARCHITECTURE AND BOUNDED SYNTHETIC IMPLEMENTATION PREPARATION; NO REAL/PROTECTED EXECUTION, MAIN MERGE OR GATE PROMOTION  
**Decision provenance:** After ChatGPT presented the initial **B-first, closed manifest, limited local threat model** choice with exact boundaries, Repository Owner explicitly replied: **"Bunu ve bundan sonraki her şeyi onaylıyorum."** This records approval of the specifically described B-first architecture and reduces repetitive consultation for its narrowly bounded synthetic planning/implementation work. It is **not** interpreted as perpetual authorization for unknown future operations, protected/archive media, actual model download/inference, provider egress, real editing/export, production deployment, Gate promotion, destructive Git, or a merge into either main.

## Immutable source and evidence

- Design being adopted: `Centaurioun/video-intelligence-pipeline-2@785b3f8384f733f11bf98949328452cd17bb61ef`, `docs/superpowers/specs/2026-11-06-vip-core02-trusted-synthetic-fixture-provenance-design.md`.
- Independent critique: `Centaurioun/video-intelligence-pipeline-2@5706e55987954eabbc82fdcd82473e7621e04772`, `docs/reviews/2026-11-06_CHATGPT_CORE02_DIGEST_REPAIR_AND_FIXTURE_PROVENANCE_RECONCILIATION.md`.
- Canonical predecessor for B-only planning: `Centaurioun/video-intelligence-pipeline@215ec88270a2437a746fbab1f4842b83ee11c512`, tree `6a07cdfcc8807db4ed2142f4a9874241b3c85007` (CORE-02 Report V1 digest-repaired successor).
- Canonical `main@3bfcc2ba221b36df6773e630b44479ec961d630a`, LAB `main@5eab58ea2a5424424cb95f2690654b91395425df`, at owner-decision verification time. Existing CORE-01 interval `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.
- The existing `tests/vip_fvs/fixtures/` at the above Canonical candidate contains **JSON timing recipes and their JSON-only materializer**, not a pinned MP4/Y4M media fixture. Do not assume a trustworthy, immutable video asset already exists.

## Adopted decisions

**D1 — Threat model: ADOPT.** The first strict admission mode is a prevention and audit guardrail against accidental/low-capability mislabeling in a reviewed, locally controlled build/test environment. It is not anti-tamper security against an attacker who controls the runner, checkout, trusted policy, executable and memory. State this limitation in UI, report, tests and reviews.

**D2 — First implementation: ADOPT B-only.** A versioned **closed allowlist manifest** of reviewed fixture IDs, immutable expected byte SHA-256 and size, permitted local purpose/operations, known fixture roots, and policy provenance is the sole strict fixture admission authority. Selecting a fixture by its *manifest ID* precedes reading any media bytes. Arbitrary user-provided paths, source-kind labels and self-authored grants must not become admission authority.

**D3 — Trust anchor: PINNED / FAIL-CLOSED.** A trusted manifest is not identified by a digest inside the manifest itself. Require a **specific reviewed Git object/revision or CI-controlled immutable artifact**, independently selected by the developer runner/launch authority; verify its exact identity and recorded blob/checksum and refuse when absent or inconsistent. The local writable checkout is not independent evidence against a same-user adversary. Initially authorize a local honest-misconfiguration trust profile only; if no independently selected policy identity exists, strict admission stays `BLOCKED_TRUST_ANCHOR`, never silently uses an arbitrary nearby JSON.

**D4 — Legacy grants: UNTRUSTED.** The old `analyze-local --source ... --provenance ... --fake-embedder` path and `SYNTHETIC_FIXTURE_ONLY` self-authored JSON cannot claim trusted source provenance. For the first additive slice, preserve backwards-compatible deterministic test use only **as explicitly lower-assurance developer test plumbing**; it must not generate the new `TRUSTED_MANIFEST_ACCEPTED` state. Before a default/production-facing strict route is enabled, prevent arbitrary `--source` from being treated as strict admission; final deprecation/removal is a separately specified versioned UX/contract action. The strict new route must not silently fall back to legacy.

**D5 — Generation: DEFER A.** No new dynamic in-process or FFmpeg generating runtime under strict admission yet. Existing FFmpeg-generated CLI fixtures are lower-assurance tests and cannot be relabeled as B-manifest fixtures. A constrained generator plus exact executable identity, recipe and custody requires measured need and separate design. Signed receipts/PKI remain deferred; filename/pixel/codec heuristics are rejected.

**D6 — Processing scope: FIXED.** Strict admission may later authorize only generated/reviewed synthetic fixture probe/index/query/Report V1 with deterministic fake embeddings, finite source/output/time limits, one source and one query, measured stream/PTS/timebase and separate nonbinding MATCHED POINT. It does not authorize authentic source/media, models, provider/cloud, editing, rendering/export, QC or Gate promotion.

**D7 — Existing contracts: PRESERVE.** Preserve sealed CORE-01 stream provenance, CORE-02 Report V1 digest/POINT semantics, source occurrence separation, no-clobber publication, evidence classes, Canonical policy and Gate-3 contracts; no SQLite migration, broad LAB transplant, or modification of legacy `+1s` interval.

## Work and release staging

- **Stage 0 — source census/contract preflight:** Verify exact Git refs, manifest-authority options, candidate fixture availability, existing source admission and test fixtures. A proposed trusted-video fixture must not be invented by tests that generate a manifest from the same arbitrary untrusted input. The current JSON timing fixtures can test metadata/manifest refusal but do not prove video pipeline acceptance.
- **Stage 1 — implementation (B-only, synthetic, isolated):** In a fresh native Codex worktree at exact digest-repaired candidate, implement only deterministic manifest selection/admission core and model-free synthetic/adversarial tests under a narrow task packet. A bounded CLI fixture-ID entry point may be added only when an accepted, specifically reviewed fixture/manifest/root can be verified. If absent, report strict CLI integration `BLOCKED_NO_PINNED_VIDEO_FIXTURE` while still completing useful pure verifier tests.
- **Stage 2 — independent review:** Verify TDD RED/GREEN, exact bytes and source-read order, negative fake grant/legacy bypass, source occurrence, content vs authority distinction, 3.11/3.14 tests, regression deltas, GitHub synthetic CI on exact SHA, independent feature review. No integration PR or main merge.
- **Stage 3 — later separate gates:** Dynamic generator A, legacy removal/strict-by-default migration, real model/media/pilot, full archive, production provider/Gate and main integration are distinct future decisions. Broad wording in the owner's message cannot supply missing exact operation limits or operational permissions.

## Acceptance and stop conditions

Accept the B-first architecture as adopted **now**. A candidate verifier can be verified only against a genuinely pinned/reviewed source policy and synthetic fixtures. If the exact manifest trust root or video bytes are not present, mark the corresponding product path `NOT_OBSERVED` or `BLOCKED`, never claim release-ready trusted media handling. All code writes require current repository contract/lease checking, exact owned source paths, a clean isolated worktree and TDD. B-only planning and the bounded synthetic verification lane can proceed without repeated approval prompts, but must stop for any unlisted source path, protected/real activity, historical contract migration or high-impact operation.

**Terminal:** `CORE02_BFIRST_ARCHITECTURE_OWNER_ADOPTED`; `CODE_CANDIDATE_SCOPE_BOUNDED_SYNTHETIC_ONLY`; `MAIN_MERGE_NOT_AUTHORIZED`; `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.
