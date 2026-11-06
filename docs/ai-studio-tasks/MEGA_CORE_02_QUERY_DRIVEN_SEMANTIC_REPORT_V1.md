# MEGA-CORE-02 — Query-Driven Semantic Report V1 / Unified One-Video CLI

**Date:** 2026-11-06 (Europe/Istanbul)
**Packet version:** VIP-MEGA-CORE-02-v1.0.0
**Status:** OWNER-APPROVED V1 PRODUCT DIRECTION / IMPLEMENTATION TASK PREPARED / NOT YET EXECUTED
**Repository / ordinary Google AI Studio publication:** Centaurioun/video-intelligence-pipeline-2 (LAB), existing main only
**Independently inspected LAB source baseline:** 35b3bcee1c99feeaedc58c9d43fc367904ccc5b1
**Canonical reference (READ ONLY):** Centaurioun/video-intelligence-pipeline main@3bfcc2ba221b36df6773e630b44479ec961d630a
**Prior completed slice:** MEGA_CORE_01_CODEX_VERIFIED — LAB 35b3bcee1c99feeaedc58c9d43fc367904ccc5b1, GitHub Actions run 42132713404 (Python 3.11/3.14 success). Genuine local focused matrix was Codex-reported as 170 passed, 10 skipped on each interpreter; the hosted workflow has a different test selection.
**Executor:** Google AI Studio for SOURCE / TEST AUTHORING. Codex will later execute genuine Python and generated-media checks.
**Owner's explicit decision:** QUERY_DRIVEN_SEMANTIC_REPORT_V1 is approved as the first CORE CLI delivery boundary. This decision is NOT approval of automatic scene captioning, real-media/model execution, canonical integration, Gate promotion or protected archive access.

## 0. Product decision and outcome

Deliver one usable, local-first, command-line workflow for ONE explicitly authorized local video and ONE natural-language TEXT query:

1. Verify scoped real-source/model/output authority BEFORE any governed source read or model load.
2. Reuse the already implemented immutable source snapshot, exact source/stream identity, deterministic PTS/timebase sampling, local checked SigLIP runtime, persistent index and query system.
3. Run/reuse indexing and retrieve multiple ranked semantic candidate moments linked to the SAME source revision.
4. Produce a **versioned, machine-readable JSON analysis report** with source, model, sampling, stream, query, score, approximate matched positions, measured sample timing evidence, limitations and truthful outcome.
5. Expose it through ONE coherent existing vip-fvs CLI command, with deterministic success/refusal exit codes, no-clobber output and no fabricated evidence.

The V1 capability is **query-driven semantic retrieval**, not unconditional full-video captioning. A hit says "this sampled visual content is similar to this query"; it does NOT establish an exhaustive scene description, an event boundary, confidence probability, editorial suitability, or a source-native cut interval.

CORE-02 is the final intended large AI Studio CODE AUTHORING slice before local Codex correction and selective canonical integration. Do not open a new Gate programme, create 5+ MEGA slices, redo CORE-01, or build another application.

## 1. Mandatory live preflight and source authority

1. Refresh the EXISTING LAB repository/main in Google AI Studio. Read LAB AGENTS.md, docs/INDEX.md, the two CORE-01 task files and this entire packet. If a ZIP snapshot lacks .git, record Git metadata as NOT_OBSERVED; GitHub UI sync can still publish, so verify remote independently when possible. Do not invent Git actions or SHAs.
2. Inspect actual head/files before coding. The SHA above is a pinned inspected baseline, not an instruction to overwrite newer work. If LAB main has advanced with relevant changes, reconcile first and preserve them; if the contract is incompatible, report BLOCKED rather than replacing newer source.
3. Canonical repository is READ ONLY. Its architecture/evidence/authorization contracts are governing reference; LAB is a selective source candidate, never wholesale copy/merge authority.
4. Inspect actual implementation signatures and callers of:
   - src/vip_fvs/cli.py (existing index-local, query-local, prepare-real and other commands);
   - src/vip_fvs/coordinator.py (index_local_source, query_local_index);
   - src/vip_fvs/real_source_service.py (RealSourceRequest, prepare_real_source, candidate-from-hit);
   - src/vip_fvs/real_source_probe.py, src/vip_fvs/source_snapshot.py, src/vip_fvs/pilot_authorization.py;
   - src/vip_fvs/local_semantic.py, src/vip_fvs/semantic_index.py;
   - experiments/persistent_local_index/{media.py,indexer.py,search.py,storage.py,model_space.py,local_model.py,embedding.py};
   - directly dependent existing product/CLI tests.
5. Check LAB src/gate0/media retains six baseline files: __init__.py, decode.py, probe.py, proc.py, source_guard.py, tool_identity.py. Full-tree AI Studio sync has deleted these in the past. Never publish missing dependencies, fabricated stubs or broad resets. If missing, STOP and report exact paths/blob evidence for selective restoration.
6. Before a write/sync, inspect changed paths and retain historical docs/receipts. No new repository, feature branch or PR for ordinary LAB AI Studio delivery; do not modify canonical main.

## 2. Preferred minimal implementation surfaces (not a license to duplicate engines)

- src/vip_fvs/core_report.py — compact schema/version, canonical serialization, report validation, evidence-safe output publication.
- src/vip_fvs/core_analysis.py — thin one-source product orchestration around EXISTING snapshot/authorization/runtime/index/query/probe seams.
- src/vip_fvs/cli.py — add only one product command, proposed name **analyze-local**.
- Focused unit tests and end-to-end synthetic integration / fresh-process CLI tests under tests/vip_fvs/.
- One concise user-facing CLI usage example/documentation file, only if needed for a runnable product.

Change the suggested filenames ONLY to avoid true duplication or to respect established interfaces, and justify each changed path. Do not implement a second FFmpeg decoder, a second identity store, a new embedding backend, a new persistence engine, another model loader, an HTTP server or independent orchestration framework. Preserve all existing CLI commands and their behavior, including LAB-only batch/three-arm synthetic commands and historical Gate-3 editorial tools.

## 3. New product CLI contract

Implement an ergonomic **vip-fvs analyze-local** subcommand under the existing Python CLI, not a separate Node/Vite/React application. Reuse existing argument idioms. Its real mode must be explicit, not a fake default.

Required/derived inputs should cover:
- --source, --query, --index-root, --output-root and a report target/path (inside the allowed output root);
- source occurrence/revision and an attempt ID, either supplied through existing verified authority or explicitly required, without inventing identifiers;
- --pilot-authorization and preverified/immutable source snapshot scope where existing contracts require them;
- --model-root, --model-identity, --model-revision, --weights-sha256, --device; checked local runtime only;
- --source-snapshot-root, --max-source-bytes, --max-store-bytes; optional, explicitly selected absolute video stream where supported;
- --top-k positive integer, with a documented conservative default;
- an explicitly labelled **--fake-embedder** ONLY for synthetic developer tests and never as a silent fallback.

Do not require irrelevant Gate-3 editorial-plan/render inputs for a query report. If old prepare-real authorization fields are required by a reused helper, preserve their semantics instead of fabricating values or weakening the check. CLI must not allow real-mode source/model paths to be combined with fake-mode evidence.

The single invocation must not shell out to multiple copies of the existing CLI as a substitute for real orchestration. Call the existing Python components in-process and pass verified snapshot/runtime/index generation identities. Avoid repeated expensive model loads where the current APIs permit reuse.

Permission check BEFORE file hashing/probing/snapshot/model opening; preserve authorization and revocation/lifecycle rechecks at the actual read/publication boundaries. Ordinary development source-authorization ENFORCEMENT is DISABLED_BY_OWNER per ADR-0003; that must NOT be misinterpreted as blanket real-source/media/model permission.

## 4. Reuse and scope the real data path correctly

Index-local and query-local ALREADY work as separate commands; compose their existing underlying services instead of reimplementing index/search. Successful existing generation reuse is eligible only if the exact semantic space, source digest/revision, snapshot, selected stream and sampling policy agree. Preserve existing INDEXED / SKIPPED / REUSED / FAILED dispositions and CORE-01 nonzero failure behavior.

**Single-video scope is mandatory.** Existing persistent generations may contain multiple sources. Never run global Top-K then silently filter away other sources and report misleading zero matches. Either:
- verify/use a genuinely one-source generation; OR
- implement an existing-index-compatible, correctly source-scoped retrieval path without ranking contamination, if the current storage/seams support it in this bounded slice; OR
- refuse with a named MULTI_SOURCE_INDEX_UNSUPPORTED/SOURCE_SCOPE_UNPROVABLE error.

Only the authorized source snapshot/revision may appear as candidate evidence. No silent reuse of another source with the same path or a reused checksum absent occurrence/revision/custody binding. Read source metadata from its real source_objects/sample records and verified snapshot/probe when needed; SearchHit by itself lacks stream index. Do not guess stream identity from relative video ordinal, file path, container track_ID or nominal FPS.

The existing prepare_real_source path focuses on the first match, attempts Gate-3 refinement, and raises NO_SEMANTIC_MATCH on empty hits. **Do not use that behavior as the V1 multi-hit reporting engine.** The product may reuse its relevant validators/probe/snapshot interfaces and optionally link a separate already-valid refinement artifact; it must not automatically create an editorial decision, require a positive hit or run render/QC.

No new full-frame enumeration or exhaustive caption extraction is part of V1.

## 5. Report V1 — required schema and semantics

Use explicit schema_version (integer 1 or stable string version), analysis_kind="semantic_retrieval", attempt/run identity and a stable report kind. JSON must be parseable and validated prior to publication; determinism means identical frozen inputs/IDs/outputs result in equivalent canonical JSON bytes except genuinely observed and explicitly declared attempt-time fields.

At minimum include:

**A. Outcome and limitations**
- stage_status, using the canonical namespace where appropriate (SUCCEEDED / FAILED / PARTIAL / BLOCKED).
- result_kind: MATCHES_FOUND, ZERO_MATCH, or REFUSED/FAILED as appropriate; do not invent a success-looking benchmark/QC status.
- errors/refusal codes, warnings, limitations, and the precise evidence availability state when something was NOT_OBSERVED.
- runtime_mode REAL or SYNTHETIC, and no fake evidence mislabeled as real.
- total eligible matches and returned candidate count, with transparent Top-K semantics.

**B. Source and authority**
- source occurrence/locator and source_revision_id, source_sha256, byte count, verified snapshot identity/digest when available, custody binding where actually recorded.
- source probe reference/digest, selected ffprobe absolute video stream index, exact rational timebase numerator/denominator and actual measurement provenance.
- source immutability verification before/after permitted operations where the seam provides it.
- decision/scope/authorization reference or digest without exposing secret credentials or unrelated protected paths.

**C. Model and index**
- model family/identity, frozen revision, expected verified weights SHA-256 and processor/preprocessing/semantic-space identity; actual observed runtime identity and REAL/SYNTHETIC indicator.
- generation ID, semantic space ID, index manifest/config/digest or explicit availability state; sampling policy ID, version, interval and selected stream policy.
- no model winner, visual-description/captioning claim, or fake "real inference" receipt.

**D. Query and multiple matches**
- original normalized text query and query identity/digest.
- each hit: stable source-bound row/candidate reference, rank, actual finite similarity score (NOT a probability), source_sha256/revision, source stream binding, sampled integer PTS, rational timebase, exact rational instant representation where practical, display timestamp when available, optional thumbnail reference with truthful availability.
- approx_semantic_location represented as a **POINT** at an attributable matched sample position unless actual coarse-window width is independently supported. Never encode start==end as a nonempty half-open interval, never manufacture +1 second. Existing zero-width review-bundle behavior is NOT silently rewritten here.
- assertion-level relationship: MATCHED with binding_eligible=false for relevance; MEASURED only for genuinely derived sampled/native technical timing facts with their own provenance. NOT_OBSERVED is an availability marker, not an evidence_class. Missing measured frame interval stays absent; a sample PTS is not a confirmed semantic event start/end or an edit boundary.
- source-native PTS/timebase/time origin and semantic seconds must be different named coordinate domains. No VFR frame inference using seconds multiplied by nominal FPS.

**E. Artifact**
- output path, content/schema validation, canonical payload digest/receipt as appropriate; ensure digest field does not create circular self-hashing.
- sensitive paths/credentials must not be inadvertently printed or uploaded.

Use the existing canonical identity/evidence/status model; the above is a required field contract, not an instruction to invent unobserved fields or duplicate every canonical record in JSON. For genuinely unavailable noncritical data, use explicit availability notation rather than zeros, fake hex digests, default timestamps or synthetic source metadata. Missing *required* identity/timebase evidence is a refusal, not a "partial success."

## 6. Result distinction, zero matches and score interpretation

- A genuine completed query with zero eligible matches is SUCCEEDED + ZERO_MATCH + empty hit list + CLI exit 0. This MUST be distinct from failure to index, model/authorization refusal, malformed query, source mismatch or corrupt metadata.
- With an unthresholded similarity Top-K, the model may return ranked hits even for semantically irrelevant queries. Do not introduce an uncalibrated similarity threshold and call low scores "no match"; no relevance guarantee exists without a separately specified evaluation contract.
- A successful query with matches is SUCCEEDED + MATCHES_FOUND; not a Gate PASS, production-ready cut, or captioning validation.
- Partial states must enumerate missing work; never imply completed source-native refinement or authentic model use when not observed.
- All hit ranks/order must be stable under the existing exact search tie ordering; preserve actual scores and identity.

## 7. JSON publication, CLI errors and repeatability

- Successful output: create a UTF-8 JSON report atomically at the designated target under authorized output_root, with **no-clobber by default**. An existing target must refuse before replacing anything, including a mismatching older report. No automatic overwrite of historical valid evidence; if an explicit replace policy is considered, defer it to a separately justified decision.
- Write to a safe temporary file and use a race-safe exclusive publication strategy, not a naive check-then-os.replace that overwrites an existing report; handle symlinks/path traversal and cleanup only the task-owned uncommitted temporary artifact. Do not erase existing data, index generations, source files or receipts.
- stdout: exactly one machine-readable JSON result/summary for a product invocation, including known validation/refusal cases. No progress chatter or raw trace on stdout; existing other CLI commands must not regress. --help may retain ordinary argparse behavior.
- Exit 0 for SUCCEEDED (with or without hits); nonzero for REFUSED/FAILED/BLOCKED/malformed report, missing required evidence, bad shape, or non-atomic publication. Reuse existing project exit practices for parser/setup errors without broad CLI overhaul; test explicitly.
- An exception must never result in an apparent "all_checks_passed:true" or publication of an empty success report.
- Repeated invocation does not claim prior matching report bytes were newly written. Explicitly report conflict/no-clobber; preserve prior file bytes.
- Hash/probe/sample results must refer to the same verified immutable source bytes, selected stream, sampling generation and model identity. Check source snapshot integrity and honor existing source-change refusals.

## 8. Mandatory regression tests to AUTHOR

Add focused, real-value tests with injected deterministic fake runtimes, generated metadata, temp paths and explicit synthetic identities. Do not claim these tests RAN in AI Studio unless they genuinely execute. Cover at least:

1. CLI parser, help, required arguments, one JSON output and exit code.
2. Successful synthetic single-video index+query with 2+ ranked hits at different PTS.
3. Strictly query-driven report: no invented caption, visual observation or event bounds.
4. Integer PTS and non-unit rational timebase, selected absolute stream, matched sample identity.
5. Audio-first video index 1/2; reject stream misbinding.
6. A SearchHit without independently verified stream metadata does not acquire an invented stream authority.
7. Zero eligible retrieval hits -> legitimate ZERO_MATCH / exit 0, not NO_SEMANTIC_MATCH error.
8. Empty or invalid index, indexing failures, source missing/unreadable, authorization expired/revoked, missing real model, fake/real ambiguity -> named nonzero refusal.
9. Same SHA in different source occurrences or mismatched revision -> no silent source identity promotion.
10. A mixed-source index/global Top-K must not produce misleading single-video results or false ZERO_MATCH.
11. Existing source snapshot digest changed / probe stream mismatch -> no report.
12. Missing or invalid filter timebase must retain CORE-01 FILTER_TIMEBASE_MISSING refusal.
13. No legitimate coarse-window width -> candidate POINT, not manufactured half-open duration.
14. MATCHED vs MEASURED assertions and explicit NOT_OBSERVED availability.
15. No calibrated relevance score threshold or false probability claim.
16. Fake fixtures prominently declared SYNTHETIC; no real SigLIP assertion.
17. Report schema/version, canonical deterministic ordering, stable digest under same frozen inputs.
18. Report target exists, symlink/path escape, interrupted exclusive publish and malformed JSON -> no overwrite and nonzero status; prior bytes unchanged.
19. Existing index-local/query-local/query-multi and LAB fake batch/three-arm CLI behavior unchanged.
20. Real-mode boundary refuses model/source operations BEFORE accessing protected bytes when authorization absent; tests use mocks, never real archive.
21. Fresh-process CLI test for machine-readable success and known failure (not only monkeypatched main()).
22. Explicit output-root and other path guards, no source mutation, no secret values in JSON.

Reuse existing tests and fixtures rather than copying large suites. TDD regressions are RED_EXPECTED_NOT_RUN in AI Studio; later Codex must establish genuine RED/GREEN, Python 3.11/3.14, compile/import, generated-media FFmpeg where relevant, diff and security review. Historical CORE-01 170/10 PASS/SKIP counts are NOT new CORE-02 test evidence.

## 9. Publication discipline and prohibited work

- Scope is ONLY this single-video, query-driven report and its directly needed tests/docs. Do not recopy CORE-01, modify canonical, replace Git history or delete prior receipts.
- No real archive/recording probe/hash/copy/decode, real model load/download/inference, network/provider calls, real video edit/render/export, user-facing cloud UI, Gate promotion, or production acceptance in AI Studio. Use source-inspected code and deterministic synthetic fixtures only.
- No React/Next/Vite/Express, generic caption generator, Qdrant/LanceDB, batch archive scanning, real audio ASR, new vector store, three-profile benchmarking or task proliferation.
- Preserve strict real/synthetic separation and established selected stream/PTS/timebase authority. Existing source media immutable.
- Publish source+tests directly to existing LAB main when AI Studio's GitHub integration supports a safe coherent forward-only sync. No new repository, PR or branch by default. Never force-push, reset, clean, overwrite unrelated work or fabricate missing media dependencies.
- If .git absent, state CLI push NOT_OBSERVED. Separately report whether GitHub UI sync published; actual remote SHA/diff must be verified afterwards by independent GitHub inspection. The next Codex task will use an isolated worktree.
- If a foundational governing contract cannot be upheld, STOP only that subpart, report exact proposed alternatives and BLOCKED_DESIGN_DECISION; do not silently invent a substitute.

## 10. Acceptance evidence and handoff

AI Studio deliverables:
- New real source/test code implementing one analyze-local command and validated V1 JSON;
- reproducible **synthetic** fixtures/test source, with explicit TESTS_AUTHORED_NOT_EXECUTED where appropriate;
- minimal truthful CLI usage including necessary real-mode argument names (example must be non-executed / placeholder-safe);
- exact modified-file list, final GitHub commit SHA if genuinely observed, pending blockers;
- a concise description of what is genuinely implemented, NOT_OBSERVED and what remains for Codex.

The later Codex verification package will require independent GitHub diff review, local Python 3.11/3.14 focused+smoke suites, real generated-media FFmpeg/ffprobe where useful, exact zero-match and error/exit/no-clobber tests, a standalone source review, security checks, hosted workflow results on final code SHA, and a real/synthetic evidence audit. No genuine one-video authentic inference can be claimed without a separate exact Owner authorization and independently observed runtime.

Final AI Studio response **in Turkish**:
A. Initial/current LAB head and actual published source SHA (or NOT_OBSERVED).
B. Modified files and design alternatives rejected.
C. One-command workflow; complete JSON schema and source/timing/identity binding.
D. Tests authored vs tests actually executed.
E. Zero-match, failure/exit, immutable source, existing-output refusal and fake/real semantics.
F. Missing evidence/critical contract blockers and next Codex verification command suggestions.
G. Explicitly state CORE_CLI_PRODUCT_COMPLETE = NOT_VERIFIED.

End with exactly:

MEGA_CORE_02_READY_FOR_CODEX_VERIFICATION
