# VIP B-first pinned synthetic video fixture and strict admission design

**Date:** 2026-11-06
**Status:** Proposal only — exact owner authorization required before fixture bytes, generator execution, source/CI changes, or runtime use.
**Scope:** One tiny immutable synthetic video fixture and a future additive `analyze-local` fixture-ID route for local developer regression.
**Terminal disposition:** `BFIRST_PINNED_VIDEO_FIXTURE_DESIGN_PROPOSED — BOUNDED_SOURCE_EXECUTION_PENDING`.

## Decision summary

Adopt a one-time reviewed **Git blob** (B1) as the first fixture artifact, registered by a closed `fixture_id` in the trusted fixture policy. The blob is immutable by Git object identity and content digest, reviewable in the exact candidate tree, needs no moving release service, and makes the policy's artifact pointer directly auditable. It is not cryptographic proof of synthetic origin: the local trust model assumes a reviewed source revision and honest runner. A same-user adversary who controls checkout, Git refs, executable, and policy can replace all of them. An immutable CI artifact (B2) adds retention and workflow identity dependencies without improving the initial local trust case; reconsider only if measured repository storage/review burden warrants it.

The first case is a proposed 64×64, short, constant-frame-rate MP4 with a single video stream, no audio, and at least two distinct deterministic frames. The exact codec, dimensions, frame count, timestamps, stream index, file size, and digest remain **unmeasured** until a separately authorized generation and independent inspection. No video exists in the current reviewed fixture set: it contains JSON timing recipes; existing FFmpeg integration media is generated at test runtime and is lower assurance.

Strict admission selects `fixture_id` using independently pinned policy identity before any media-byte read, probe, or indexing. It then opens the registered path beneath an approved root with no-follow bounded descriptor custody, verifies bytes against the pinned Git blob/digest and size, and holds/revalidates that descriptor through probe and query. It never falls back to arbitrary `--source` or a self-authored legacy grant. Failure is closed and explicit. The existing legacy developer workflow remains a separate lower-assurance path until an independently approved migration.

## Evidence and current behavior

The owner-adopted B-first decision limits this route to a reviewed closed fixture manifest, honest local misconfiguration prevention, deterministic fake embeddings, and local probe/index/query/report. It distinguishes an independently selected policy anchor from the current worktree's observed file identity. It explicitly rejects grant self-issuance, strict-to-legacy fallback, runtime FFmpeg generation under strict admission, and claims of anti-tamper security against a same-user actor.

The occurrence successor repair establishes `PinnedPolicyFixtureReference` as `MATCHED` policy-to-file reference evidence, while actual opened file device/inode is `MEASURED`; source occurrence remains `NOT_OBSERVED`. Its JSON-only fixture reader refuses caller-invented occurrence claims before opening bytes. This is not yet a pinned video fixture or production trust root.

The independent reconciliation reports no checked-in common-format media in the candidate tree. Existing `tests/vip_fvs/fixtures/` materializes JSON only. `tests/vip_fvs/integration/test_core_analyze_local_cli.py` creates a 64×64 runtime MP4 with fake embeddings and a self-authored synthetic grant; that demonstrates neither immutable fixture registration nor trusted strict admission. Consequently, `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED` remains true and `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT` remains unchanged.

Exact implementation review must re-open these sources at the selected Canonical candidate `cac74495d80d9eaa144a12e9aa67eba78ba2f062` (tree `1e851b89273e7ae9a580643b8b704a2d5945c099`) because LAB behavior is not proof of Canonical source behavior:

- `AGENTS.md`, `docs/INDEX.md`, `docs/project/00_PROJECT_CHARTER.md`, `01_CURRENT_STATE_AND_HANDOFF.md`, `02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md`, `03_CODEX_EXECUTION_BOOTSTRAP_HANDOFF.md`, current architecture/authorization contracts, native thread runbook, and `docs/portfolio/portfolio-v1/resource-policy-v5.yaml`.
- `src/vip_fvs/trusted_fixture_manifest.py`, `core_analysis.py`, `query_analysis_authorization.py`, `core_generation_evidence.py`, `core_report.py`, `cli.py`, source snapshot and bounded admission/FFprobe paths.
- `tests/vip_fvs/integration/test_core_analyze_local_cli.py`, `tests/vip_fvs/fixtures/materialize.py`, `tests/gate0/media/generated_media.py`, `tests/gate0/fixtures/generated-media/build_media_corpus.py`, `src/gate3/fixturegen.py`.
- `.gitignore`, media/binary fixture rules, Git LFS configuration if present, CI workflow selection, and signing/review policy.

This design does not assert that this source census was freshly executed in the LAB worktree; the referenced reconciliation is read-only source/CI evidence and the exact Canonical candidate remains the implementation inspection anchor.

## Goals, limits, and non-goals

Goals:

1. Give developers one real, decodable, immutable video input for regression of strict fixture-ID admission and report semantics.
2. Exercise the supported image-source query pipeline with deterministic fake embeddings, at least two ranked matches, and measured video-stream index, integer source PTS, and rational timebase.
3. Make policy identity, artifact identity, current file identity, and occurrence status separate and inspectable.
4. Fail closed before source-byte access when policy/ID authorization is missing or inconsistent.

Limits and anti-goals:

- Local regression only; not proof of authentic archive provenance, external signing, custody against a same-user attacker, production readiness, Gate progress, or release approval.
- No real model, provider, archive media, download, network operation, audio, editing, rendering/export, QC, scheduler, schema migration, or main merge.
- No VFR/frame-accurate claim, no fabricated interval, no conversion of semantic similarity into temporal or editorial authority.
- No dynamic strict-path media generation. Fixture issuance is a separate operation and authority from code that consumes the frozen bytes.

## Artifact and custody decision

### Alternatives

| Option | Advantages | Costs and failure modes | Disposition |
|---|---|---|---|
| B1: one-time generated, inspected MP4 checked in as a Git blob | Exact tree/blob identity; offline; reviewable alongside policy; straightforward source pinning | Binary diffs are opaque; repo history retains every version; Git alone does not prove synthetic origin; requires independent generation receipt and raw-byte inspection | **Choose for one tiny artifact**, subject to measured size and repository policy review |
| B2: immutable CI artifact | Keeps binary out of source history; workflow can attach a producer identity | Requires immutable retention, artifact ID/digest pinning, trustworthy workflow and retrieval availability; a URL or mutable release tag is insufficient; adds CI trust dependencies | Defer; reconsider if B1 exceeds storage policy |
| Generate at test runtime and self-hash sidecar | Simple, reproducible test setup | Manifest and bytes can share one untrusted invocation; tool drift; does not create a reviewed pinned source authority | Reject for strict admission; existing tests stay explicitly lower assurance |

The Git blob is an artifact anchor, not an origin oracle. The policy must be independently selected by the developer/test launcher as an exact reviewed Git commit/tree/path/blob identity (or equivalent separately reviewed immutable policy identity); a digest embedded only inside a mutable manifest is circular. The policy contains a literal fixture ID, relative path, expected Git blob object ID, SHA-256, exact byte size, allowed purpose/operations, and finite processing limits. No identity may be synthesized from the bytes at invocation time.

Generation custody belongs to a named future fixture issuer, separate from the strict admission/CLI implementer. The issuer packet must record:

- exact generator script and source commit, and whether it is a narrowly written generator or a reviewed deterministic command;
- FFmpeg executable path, measured executable SHA-256, measured version output, and container/environment identity; do not infer codec support from a filename;
- full command arguments, environment, generation timestamp, and bounded output path;
- resulting artifact SHA-256 and byte count, measured from raw bytes;
- independent raw-byte and decode inspection receipt, with inspection tool identities and results, including stream count/type, codec, dimensions, frame count/duration, integer PTS and rational timebase;
- a separate human visual observation of decoded frames if relied upon, labeled `VISUALLY_OBSERVED`; intended synthetic purpose is an assertion, not a measurement.

No exact size, hash, PTS, codec, frame rate, or stream index is claimed in this proposal. All are `NOT_OBSERVED` until issuance. Do not use a filename, manifest self-hash, generated-media sidecar, or codec heuristic as provenance.

## Initial fixture shape and report semantics

Proposed single case `bfirst_tiny_video_v1`: a 64×64 CFR MP4, a small finite number of deterministic solid-color or simple geometric frames, one video stream, no audio, and at least two distinguishable frames. Keep it small enough for repository policy and human review, but choose exact codec and frame count only after a separately authorized probe/decode experiment. Avoid B-frame/VFR complexity in this first case; named future fixtures may address those properties.

The purpose is specifically to pass real decoded image samples through the supported source-query path while removing model nondeterminism. Fake embeddings are fixed and deterministic, allowing a stable ranking assertion for at least two candidates. The report must use the exact measured absolute stream index and source-native integer PTS paired with the measured rational timebase. `MATCHED` semantic results remain nonbinding POINT evidence; measured media timing remains separate. Do not invent intervals, derive source time by multiplying a nominal FPS, or call semantic POINT a frame-accurate edit.

## Strict admission contract

1. Caller supplies only the closed `fixture_id` selector for strict mode. Launcher supplies or pins the policy revision independently. Resolve and validate exact policy revision/tree/path/blob before opening any video path.
2. Validate ID membership, purpose, operation, policy schema/version, and finite limits. Unknown ID, wrong policy revision, disallowed operation, missing trust anchor, or legacy strict-mode selector mismatch stops before video bytes are read, probed, indexed, or decoded.
3. Resolve the fixed relative path beneath a pre-approved fixture root. Reject absolute paths, traversal, symlinks, and unapproved roots. Open with no-follow semantics and bounded reads; retain descriptor custody. Record measured device/inode and exact opened bytes separately from policy `MATCHED` identity. Hardlinks require explicit rejection or proof the opened object is the pinned object under the platform's available semantics; default to reject unexpected link count where reliably available.
4. Verify exact size, SHA-256, and Git blob identity against independently pinned policy, then probe and decode only through that admitted descriptor or a safe, verified private snapshot derived from it. Revalidate identity immediately before/after probe and before indexing/query. Any path replacement or identity drift fails closed; do not reopen an untrusted pathname after admission.
5. Keep the descriptor open for the bounded operation. If FFprobe/decoder APIs cannot consume the descriptor safely, copy once from the held descriptor into a bounded private no-clobber snapshot, hash while copying, fsync, verify snapshot identity, and pass only that snapshot onward. Document this as a snapshot, not source occurrence proof.
6. Strict mode has no fallback to arbitrary `--source`, old synthetic grants, JSON timing recipes, or dynamically generated media. Legacy CLI remains separately labeled lower-assurance developer plumbing until an exact contract migration is authorized.
7. Publish report atomically with no-clobber behavior. Report exact policy revision and fixture ID; `MATCHED` pinned policy reference; measured opened-byte digest/size and file identity; source occurrence `NOT_OBSERVED`; evidence classes per assertion; source-native time data; deterministic fake embedder identity; and explicit local trust-model limitations.

If independent policy selection cannot be established, report `BLOCKED_TRUST_ANCHOR`. If a suitable pinned decodable video is absent, report `BLOCKED_NO_PINNED_VIDEO_FIXTURE`. Neither state is success. Maintain `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED` until the exact strict route is implemented and exercised; preserve `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.

## Adversarial acceptance matrix for future implementation

| Case | Expected result |
|---|---|
| Unknown fixture ID or missing independent policy anchor | Reject before any video open/read/probe; explicit blocked/refusal state |
| Wrong policy commit/tree/path/blob, stale revision, or edited policy | Reject before video bytes; never trust a self-hash inside the policy |
| Correct ID, wrong digest or size | Reject before probe/decode/index/query; retain no report claiming acceptance |
| Same bytes copied into a second root | Content/policy may match; actual file identity differs; source occurrence remains `NOT_OBSERVED`; never infer custody from content equality |
| Unlinked Git artifact or path whose blob does not equal policy | Reject even if filename, sidecar, or SHA claim looks plausible |
| Symlink, traversal, absolute path, or unexpected hardlink | Reject before reading outside approved root; no-follow descriptor checks must be observed |
| Replace/rename source after selection or during probe | Held descriptor/snapshot stays authoritative or operation fails on identity drift; pathname reopen must not redirect input |
| Corrupt or non-decodable MP4 with validly registered test bytes | Probe/decode failure is explicit; no semantic result and no partial-success report |
| Two or more ranked candidates | Stable fake-embedding ordering; each result carries nonbinding `MATCHED` POINT and measured source PTS/timebase |
| Existing output path | No-clobber publication refuses; preexisting bytes remain unchanged |
| Strict request plus legacy `--source`/grant flags | Refuse ambiguous or mixed mode; no silent legacy fallback |
| Legacy-only request | Existing lower-assurance developer behavior stays distinguishable and cannot emit trusted-manifest acceptance |
| Snapshot creation interrupted or output collision | Fail closed; no partial accepted snapshot; no clobber |
| Descriptor/source revalidation mismatch | Stop before indexing/query or report publication |

Tests must observe ordering, not only final exceptions: inject a source-open/read/probe spy and assert zero calls for pre-read authorization failures. Use filesystem race/adversary tests only in bounded temporary directories. No protected source material.

## Future execution packet outline (not authorization)

Each stage needs its own exact, reviewed packet, fresh isolated worktree, verified base, exclusive path ownership and explicit stop conditions. Current general planning authority does not authorize the following writes or FFmpeg execution.

### Stage A — issue frozen bytes (separate owner authorization required)

**Owner decision required:** authorize creating and adding one tiny synthetic MP4, exact generation tooling/command boundary, output byte cap and codec/tool policy, and the nominated issuer. This is the only stage allowed to invoke FFmpeg or write the new media asset. Use a fresh isolated worktree based on a verified exact candidate; write only the newly named media path and its generation/inspection receipt. No production code, manifest registration, CLI, CI, main ref, or protected media. Capture custody fields above; independently inspect raw bytes and decode properties. If size/storage, decoder support, or inspection cannot be established, stop with `BLOCKED_NO_PINNED_VIDEO_FIXTURE` and preserve evidence. Issuer commits only approved asset and receipt after exact diff/secret/storage checks; publication requires separate packet authority.

### Stage B — register reviewed fixture (separate owner authorization required)

After Stage A is independently reviewed and the asset commit is immutable, authorize a closed manifest entry and unit/adversarial tests only. A different worker/path owner should own policy registration. Proposed write paths: `src/vip_fvs/trusted_fixture_manifest.py` and `tests/vip_fvs/unit/test_trusted_fixture_manifest.py` (reconcile exact current source/ownership before task issuance). Tests must use the fixed blob identity, prove authorization-before-read, distinguish policy `MATCHED` from opened-file `MEASURED` identity, and preserve occurrence `NOT_OBSERVED`. No CLI, decoder, or CI changes in this stage.

### Stage C — strict CLI integration (separate owner authorization required)

Only after A/B acceptance, authorize the additive strict fixture-ID route and selected integration/admission/report tests. Proposed exclusive paths, subject to exact source reconciliation: `src/vip_fvs/cli.py`, `core_analysis.py`, `query_analysis_authorization.py`, `core_generation_evidence.py`, `core_report.py`, source snapshot/bounded-admission modules, `tests/vip_fvs/integration/test_core_analyze_local_cli.py`, and narrowly selected workflow configuration if required. Do not co-own these with Stage A issuer. Keep legacy behavior explicitly separate; no broad default migration or removal without separate contract authority.

### Prospective TDD, review, and CI gates

1. On pre-implementation code, create behavioral RED tests proving read/probe spy stays untouched for missing anchor/unknown ID/policy mismatch, and failures for digest/size/path/replacement/legacy bypass cases. Record exact baseline SHA and prospective RED commands/results; environment/tool errors are not RED.
2. Implement only the stage's exclusive paths, rerun focused GREEN tests and regression selection; verify source snapshot and no-clobber behavior.
3. Run repository-required workspace verifier and secret audit before any authorized push. Keep local, hosted, synthetic, and historical evidence distinct.
4. Obtain independent feature review on exact immutable head and hosted CI for selected supported Python versions. The review checks artifact/policy identity, pre-read ordering, bounded descriptor custody, report semantics, and scope. A reviewer `NO_FINDING` is not formal GitHub approval.
5. Reconcile exact candidate source, branch, tests, changed paths, and evidence before any later integration. No stage implies main merge, production use, Gate advancement, or real-media approval.

## Alternatives rejected and open owner choices

- Runtime generation is rejected for strict admission because it co-creates bytes and their claim in one invocation.
- A downloaded or mutable release URL is rejected as a trust anchor. B2 remains viable only with immutable artifact identity, digest, retention, and independently trusted workflow provenance.
- A signed receipt/PKI root is deferred as disproportionate to the honest-local-misconfiguration objective; reconsider only if the threat model changes.
- Filename, codec, pixel-pattern, or `synthetic` labels cannot prove origin and are not authorization.
- Multiple codecs, VFR, audio, B-frames, several fixtures, actual model embeddings, and real media are deferred to separately named tasks.

The owner must separately decide whether to authorize Stage A's one-time generation and binary addition, including a concrete byte cap and FFmpeg/tool boundary. No implementation stage starts solely from this proposal.

## Source and evidence ledger

- LAB base: `5eab58ea2a5424424cb95f2690654b91395425df`.
- Canonical candidate source anchor from task packet: `cac74495d80d9eaa144a12e9aa67eba78ba2f062`, tree `1e851b89273e7ae9a580643b8b704a2d5945c099`; canonical main `3bfcc2ba221b36df6773e630b44479ec961d630a`.
- Owner-adopted B-first constraints: LAB `decision/vip-core02-bfirst-trusted-fixture-manifest-20261106@8de8664c8ce8501f86d484b63389f8d1a1c95fec`.
- Occurrence successor independent reconciliation and task packet: LAB `462deeca063d01cc3de8094a3dbed90ef6d6ef9d`.
- No FFmpeg command, video generation, provider/model call, protected media access, implementation source change, CI change, or main update was performed in this design task.
