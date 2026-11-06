# CORE-02 — independent GitHub source and CI audit

**Date:** 2026-11-06  
**Auditor:** ChatGPT, separate from local Codex worker and reviewer.  
**Disposition:** NEEDS_WORK on Report V1 artifact integrity; additional synthetic-source provenance design decision required. This is an advisory source audit, not an executable repair authorization.  
**Scope:** Read-only GitHub inspection of Canonical source at an immutable candidate SHA. No local test suite, model, media, protected archive or implementation executed.

## Frozen refs and independent GitHub checks

- Canonical `main`: `3bfcc2ba221b36df6773e630b44479ec961d630a`, tree `032b7ea8908fa04f1d85cf0d57c1608d28864557`.
- CORE-01 parent/successor: `261319d4ac7f3c2ac80b67a59baea13bba73bfed`.
- CORE-02 branch: `feature/vip-core02-single-video-semantic-report-20261106`; GitHub HEAD `520ab543c7eb765ce1cba989742dde3abd4bbf4e`, tree `3ad25b7b00b03a14e6ed2cc068a027dc042f2a46`.
- `git compare 261319d...520ab543`: exactly **six commits ahead and ten changed files**, five production paths and five focused test paths; no branch divergence. The CORE-01 inheritance includes its earlier changes, while the CORE-02-specific diff has exactly ten paths.
- GitHub workflow [42259406185](https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/42259406185) is `workflow_dispatch`, exact `head_sha=520ab543...`, `success`. Fetched both job logs independently: Python 3.11 **308 passed** and Python 3.14 **308 passed** in the workflow's deterministic synthetic smoke selection; neither is the full Canonical suite or necessarily the five CORE-02 focused test files.
- Reported local Codex tests: CORE-02 focused five files 72 passed per Python 3.11/3.14; broad and full suites have 8 and 7 reported baseline-matched failures respectively. The claims and independent review thread `01a1b1d5-4d5e-7170-b02e-77cd601cd165` were supplied by the user from Codex and were **not independently rerun or directly fetched** in this GitHub-only audit.
- LAB main remained `5eab58ea2a5424424cb95f2690654b91395425df`, both private backup releases were fetched as `immutable=true`. No PR/merge was requested or performed by this audit.

## Findings

### F1 — Definite artifact-integrity bug: computed Report V1 digest is omitted from published JSON — MUST FIX

**Source:** `src/vip_fvs/core_report.py` lines 44–56, 151–193 at exact candidate SHA.

The single helper `_canonical_bytes(report)` makes a copy and `pop("report_digest", None)` before JSON encoding. That behavior is correct when calculating the canonical hash *input* and makes `compute_core_report_digest(report)` self-reference-free.

However `publish_core_semantic_report` then sets `payload_report["report_digest"] = compute_core_report_digest(payload_report)`, validates that object, and writes `payload = _canonical_bytes(payload_report)`, which removes the freshly computed `report_digest` **from the persisted JSON bytes**. `analyze_local_video` constructs a report without `report_digest` and returns that original mapping, so the outcome does not separately repair the omission.

Thus the source demonstrably computes a digest but does not serialize it inside the final report. A valid field-level digest validation test and a published-file equality test are different; existing `tests/vip_fvs/unit/test_core_report.py::test_report_digest_recomputed_without_self_field` only checks recomputation, and existing CLI integration tests inspect other JSON fields without asserting a persisted `report_digest`.

**Required RED/GREEN correction (candidate, no source edits yet):** Add `test_published_report_contains_verifiable_digest`: publish Report V1 to a synthetic temporary root, reload JSON, assert 64-hex `report_digest` exists and equals `compute_core_report_digest(reloaded)`; verify deterministically identical bytes for two equivalent publications to separate destinations and no overwrite/atomic failure invariants. Keep two distinct functions, one for *canonical hash input* (digest excluded) and another for *final JSON serialization* (digest retained). Never hash self-referential JSON directly. Update CLI synthetic published-file test to check the digest explicitly. Independently review the final exact SHA.

**Disposition:** `CORE02_SYNTHETIC_CANDIDATE_VERIFIED` cannot be accepted as full contract verification while this defect exists. `CORE02_SYNTHETIC_NEEDS_WORK`.

### F2 — Synthetic source-kind claim is self-declared, not independently attested — design/policy decision required

**Source:** `src/vip_fvs/query_analysis_authorization.py` lines 19–27, 70–117, 121–152; `src/vip_fvs/cli.py` `analyze-local` dispatch at approx. lines 991–1046; `src/vip_fvs/core_analysis.py` lines 93–157 at exact candidate SHA.

The grant loader verifies strict canonical JSON structure, fields, expiry, declared `grant_kind="SYNTHETIC_FIXTURE_ONLY"`, declared `source_kind="synthetic"`, source digest/size, query/model/output scope and other exact matches. It computes `record_digest` from **the supplied grant bytes themselves**; this is a content integrity identifier, not independent signer/issuer authentication or trusted generator provenance. The `generator` field is only checked as nonempty text. The `analyze-local` branch uses this grant to snapshot/probe/index/source-hash any path passing those checks with fake embeddings. There is no visible independent fixture-generator receipt or verification that the actual file was produced by an authorized synthetic generator.

**Consequence:** `real_mode` and real inference correctly fail closed, but that does **not prove the input itself is synthetic**. A self-consistent grant can be created for arbitrary source bytes; a mislabeled real video could reach a fake-embedding processing path, contrary to the narrowly approved generated-media-only policy. This is an enforcement and threat-model limitation, not evidence that protected media was actually processed.

**Decision candidate:** Require a verified synthetic generation/attestation provenance chain under Canonical source-admission authority, or confine `analyze-local` to a recognized test-fixture root with attributable immutable generation receipts, before treating its synthetic admission as a genuine policy boundary. Do not silently extend this to protected source or REAL mode. Owner design approval is needed before changing policy schema.

### F3 — Real mode genuinely remains disabled for this new command — POSITIVE

**Source:** `src/vip_fvs/core_analysis.py` lines 93–99, `src/vip_fvs/cli.py` lines 991–1004. The CLI requires explicit `--fake-embedder` and the orchestrator rejects `real_mode=True` and runtimes not marked `fake` before source decoding/probing. `require_query_analysis_authorization` is implemented as a scope validator but is not wired to activate a REAL command. This is consistent with current owner restrictions.

### F4 — Temporal candidate semantics are appropriately nonbinding, but do not solve legacy interval — POSITIVE / OPEN

**Source:** `src/vip_fvs/core_report.py` lines 26–41, 118–143; `src/vip_fvs/core_analysis.py` lines 216–276; unchanged `src/vip_fvs/real_source_service.py`.

The new report uses `location_kind="POINT"` with no `start`/`end` fields and `window_width_seconds="NOT_OBSERVED"`. Matching relevance is `MATCHED` and `binding_eligible=false`, while sampled integer PTS/rational timebase are retained as separate `MEASURED` technical fields. The old legacy `+1 second` semantic interval is **not** removed. Continue marking `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT` and do not describe CORE-02 as granting edit boundaries.

**Potential future audit:** The `semantic_seconds` value is derived directly from `PTS × rational timebase`, so explicit origin semantics deserve coverage for nonzero PTS/video presentation origins; never extrapolate frames with nominal FPS. This point is a risk/review item, not proof of an observed incorrect sample.

### F5 — Report publication confinement and failure injection need additional adversarial review — RISK, NOT PROVEN BUG

**Source:** `src/vip_fvs/core_report.py` lines 151–193. The publisher resolves the target parent, checks root containment and links a temporary same-directory file via `os.link` without overwriting the target; it uses `O_NOFOLLOW` for the opened parent and temp. It is promising for ordinary no-clobber cases. However the existing tests inject `os.link` failure and check simple symlinks; parent/ancestor replacement races and post-link `os.fsync` errors are not independently certified. In particular an error after successful link but during directory sync may leave the file at destination while the caller reports failure. Treat crash/race durability guarantees as unproven until bounded fault-injection and directory-entry race tests are reviewed.

### F6 — ZERO_MATCH, benchmark and test claims must remain narrow — BOUNDARY

**Source:** `src/vip_fvs/core_analysis.py` lines 209–243; `tests/vip_fvs/integration/test_core_analyze_local_cli.py` injected empty query test. The empty-result path is truthful for an *injected deterministic synthetic empty-result engine*. It does not show real-model negative retrieval quality, model recall or calibrated relevance thresholds. Top-K saturation is correctly marked `NOT_OBSERVED` for total eligible hits. Both original Canonical main and LAB main remain unmodified.

## Recommendation / next authorized action

1. **Immediate narrow code fix requiring separate owner approval:** report digest persistence and test of the actual on-disk JSON, with code review on a new isolated Canonical successor branch based exactly on `520ab543...`; do not modify shared dirty worktrees, inherited CORE-01 temporal code, Gate-3 or existing main.
2. **Design decision before claiming strict synthetic admission enforcement:** select how trusted fixture generator provenance will be demonstrated, separately from user-supplied source metadata. Avoid claiming an unforgeable source-kind guarantee until the chain exists.
3. **Additional adversarial publication tests:** no-clobber, symlink/ancestor races and post-link directory-sync failure, at least reporting limitations honestly if not yet in scope.
4. **Re-run and review:** CORE-02 focused tests on Python 3.11/3.14 and host CI at final SHA, maintain exact baseline delta for pre-existing 7/8 local failures; no full-green claim from synthetic smoke 308 per interpreter. Current Codex reviewer PASS is respected as reported but does not negate independently observed source defect.
5. **No PR/main merge, no genuine model, protected media, provider, or Gate promotion.** CORE-01 legacy interval remains `BLOCKED_BY_CONTRACT`. Preserve original candidate SHA for comparison, never replace history.

**Terminal marker: CHATGPT_CORE02_SOURCE_AUDIT_NEEDS_WORK — OWNER_REPAIR_DECISION_PENDING.**
