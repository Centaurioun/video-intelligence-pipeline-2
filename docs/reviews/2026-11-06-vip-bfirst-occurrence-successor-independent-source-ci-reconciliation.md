# VIP — Independent B-first occurrence successor source and CI reconciliation

**Date:** 2026-11-06
**Scope:** Read-only GitHub source, Git ref, diff and Actions job logs; no access to private Codex native worktrees, no direct local pytest, protected media, real model or provider. Historical TDD receipts remain as reported, not newly re-created.
**Disposition:** `BFIRST_OCCURRENCE_SEMANTICS_REPAIR_SOURCE_VERIFIED` (narrow component), with reported native RED/GREEN and independent review; no product/pilot integration authorization.

## Immutable Git facts independently verified

- Canonical main: `3bfcc2ba221b36df6773e630b44479ec961d630a`, tree `032b7ea8908fa04f1d85cf0d57c1608d28864557`.
- Canonical candidate branch: `feature/vip-bfirst-policy-observed-occurrence-repair-20261106@cac74495d80d9eaa144a12e9aa67eba78ba2f062`, tree `1e851b89273e7ae9a580643b8b704a2d5945c099`.
- Exactly **one commit ahead** of `c474b8702d610462c455f8598052c06fe7dd9dd9`, no behind. Exactly TWO modified paths: `src/vip_fvs/trusted_fixture_manifest.py`, `tests/vip_fvs/unit/test_trusted_fixture_manifest.py`. No other production path changed; no PR or merge performed by this review.
- LAB main: `5eab58ea2a5424424cb95f2690654b91395425df`.
- Both DO_NOT_DELETE backup GitHub Releases at tag `vip-backup-2026-11-06` independently fetched with `immutable=true`.
- GitHub Actions run [42286871903](https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/42286871903) is `workflow_dispatch`, exact `head_sha=cac74495...`, `success`. Both fetched job logs state **308 passed** under Python 3.11 and **308 passed** under Python 3.14. These are the workflow's deterministic synthetic smoke selection; **the new manifest test file is not part of that smoke selection**.
- Codex report states true *prospective* behavioral RED (two failing tests) against `c474...` on both Python 3.11/3.14, GREEN after change, local focused selections 51+12+53 passed and reviewer 20 passes per interpreter plus combined 107 Python3.14 passed. These are **REPORTED** from the native Codex worker/reviewer; GitHub connector cannot directly certify those private local test records.
- The earlier `c474...` candidate's missing original behavioral RED was and remains historically `NOT_OBSERVED`. A new successor RED does not rewrite previous test chronology.

## Verified code semantics

1. Introduces frozen `PinnedPolicyFixtureReference(commit, tree, path, blob_oid, evidence="MATCHED")` as distinct from an actual opened file's `device` and `inode` (`file_identity_evidence="MEASURED"`).
2. `AdmittedTimingRecipe.source_occurrence_id` is `None` and `source_occurrence_status="NOT_OBSERVED"`. This accurately withholds a unique/custody occurrence claim; `NOT_OBSERVED` is a state marker, NOT an evidence class.
3. The caller-supplied `occurrence_id` now refuses `FIXTURE_OCCURRENCE_NOT_OBSERVED` **before opening input fixture bytes**. Existing unknown ID, disallowed purpose/operation and timing JSON-as-video/REAL refusal remain.
4. New two-root synthetic test copies the **same reviewed JSON fixture bytes** into two concurrently existing roots. Policy reference and content SHA match while actual file identities differ, and no invented source occurrence is emitted. A second test refuses caller's `git:<commit>:<path>` occurrence assertion.
5. The reader still uses `bounded_admission.admit_relative_file_bytes` with bounded no-follow descriptor read, followed by physical file identity check. Its source policy is a low-assurance, code-pinned developer allowlist, **not protected independent signer trust**; any local user controlling code, checkout and Git refs could defeat this threat model. Same-byte copy cannot prove original historical custody.

## Limits and remaining status

- The repair is source-level correct for the reviewed scope. The separate Codex reviewer `NO_FINDING` with clean worktree and local tests is reported but not independently fetchable from GitHub. No full Canonical suite rerun was observed for this candidate.
- GitHub full recursive tree of `1e851b89...` (not truncated, 2283 entries) contains **zero checked-in files** with common media extensions `.mp4/.mov/.mkv/.webm/.avi/.y4m/.mpg/.mpeg/.wav/.flac/.m4v`. Current `tests/vip_fvs/fixtures/` contains two JSON timing recipes and `materialize.py`, which emits JSON, not video.
- Existing `tests/gate0/fixtures/generated-media/build_media_corpus.py`, `tests/gate0/media/generated_media.py` (imported by builder), and `tests/vip_fvs/integration/test_core_analyze_local_cli.py` show **run-time FFmpeg synthetic media generation**. Those paths are lower-assurance test harnesses, **not reviewed pinned immutable video byte fixtures**. The existing CLI integration creates a 64×64 FFmpeg `mpeg4` MP4 at test time with fake embeddings and a self-authored `SYNTHETIC_FIXTURE_ONLY` grant; it does not establish a B-first trusted-video admission path.
- Production `analyze-local` CLI and query grant were deliberately not modified in the two-path B-first successor. The strict manifest-to-video E2E integration has NOT been executed, nor authorized by this review.
- No real/protected/archive video, actual model load/download, provider call, editing/render/export/QC, Gate advancement or main merge was observed or conducted.

## Recommended future action (planning only, not code authorization)

Prepare an approved **small immutable synthetic-video fixture** design: choose a tiny bounded test binary or protected immutable CI artifact, exact independently reviewed identity and SHA-256, source occurrence/path custody, generator/FFmpeg provenance and inspectable native video PTS/timebase/stream properties; ensure it is a real decodable MP4 and can yield at least two deterministic candidate samples under fake embeddings. Compare a one-time reviewed generated binary committed in Git (B-first) against a pinned CI immutable artifact; do not confuse test-time dynamic generation with independently reviewed artifact issuance. Include unavoidable binary review limitations and an external immutable trust assumption. Plan a separate versioned strict CLI `fixture_id` route with no arbitrary-source fallback and pre-read authorization only **after** the fixture/media and admission contract is approved. Do not add new binary media, generator runtime, CLI flags or production code in this review.

**Terminal:** `BFIRST_OCCURRENCE_SEMANTICS_REPAIR_SOURCE_VERIFIED`; `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`; `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.
