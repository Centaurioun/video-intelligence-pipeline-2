# VIP CORE-02 — Independent reconciliation of digest repair and synthetic-fixture provenance design

**Date:** 2026-11-06  
**Auditor:** ChatGPT independently reading exact GitHub commits and GitHub Actions logs, not the local Codex worktree.  
**Disposition:** **Lane A — SOURCE_FIX_VERIFIED; GitHub synthetic CI VERIFIED; local focused test / native review evidence reported but not independently re-executed. Lane B — DESIGN_REVIEWED, OWNER_ARCHITECTURE_DECISION_PENDING.** No merge, implementation or mainline authorization from this review.

## Frozen verified repository evidence

- Canonical main HEAD `3bfcc2ba221b36df6773e630b44479ec961d630a`, tree `032b7ea8908fa04f1d85cf0d57c1608d28864557`.
- LAB main HEAD `5eab58ea2a5424424cb95f2690654b91395425df`, tree `dae72052bbdbc1962713f302b50f8fa2fd78ed7f`.
- Lane A source: `520ab543c7eb765ce1cba989742dde3abd4bbf4e` (tree `3ad25b7b00b03a14e6ed2cc068a027dc042f2a46`).
- Lane A published branch `feature/vip-core02-report-digest-repair-20261106` HEAD `215ec88270a2437a746fbab1f4842b83ee11c512`, tree `6a07cdfcc8807db4ed2142f4a9874241b3c85007`, direct single parent above.
- Exact Lane A diff: three paths only `src/vip_fvs/core_report.py`, `tests/vip_fvs/unit/test_core_report.py`, and `tests/vip_fvs/integration/test_core_analyze_local_cli.py`.
- Lane B published branch `design/vip-core02-trusted-synthetic-fixture-provenance-20261106` HEAD `785b3f8384f733f11bf98949328452cd17bb61ef`, tree `7080cc938a1961d79a91095fe30d6ab325773457`, direct single parent `cc0f3b26d081e0312a05bc80a85bfe326885694b`. Exact Lane B diff: a single added Markdown proposal `docs/superpowers/specs/2026-11-06-vip-core02-trusted-synthetic-fixture-provenance-design.md`. No Canonical application code touched by Lane B.
- Canonical and LAB backup releases at `vip-backup-2026-11-06`: both `immutable=true` at audit-time GitHub fetch. This does not check local Mac worktree contents.

## Lane A: exact source-level verification

- Predecessor `_canonical_bytes(report)` omitted `report_digest`, and publisher incorrectly reused it for final bytes after calculating digest.
- Candidate creates `_json_bytes(payload)` (normal canonical JSON serialization including all fields) and retains `_canonical_bytes(report)` for canonical **hash input**, which explicitly removes `report_digest`.
- Publisher at candidate `src/vip_fvs/core_report.py` line ~171 now writes `payload = _json_bytes(payload_report)` after setting the digest and calling the validator. Thus, assuming the write succeeds, persisted JSON includes `report_digest`, and the hash remains self-reference-free. This fixes independently identified earlier finding F1.
- New unit test `test_published_report_contains_verifiable_digest` reloads persisted JSON; other tests cover repeat destination determinism, tamper mismatch, existing file no-clobber, symlink refusal, and injected directory `fsync` failure *after* successful `os.link` (target may already exist with verifiable digest).
- CLI integrated synthetic test also recomputes digest from the actual output JSON.
- Repo source review alone does **not** prove all filesystem races, crash consistency, OS/filesystem portability or model-source admission. The post-link `fsync` ambiguity is explicitly acknowledged, not repaired by a broader commit protocol.

### CI and reported local verification

- GitHub run [42272159384](https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/42272159384) `workflow_dispatch` has exact `head_sha=215ec882...` and `conclusion=success`.
- Fetched and read both job logs: **308 passed** Python 3.11 smoke; **308 passed** Python 3.14 smoke. This workflow is a selected deterministic contract/timing suite, not the complete CORE-02 five-file test group.
- The Codex handoff *reports* 82 focused tests passing on each interpreter, a test-first RED/GREEN demonstration, passing compilation/worktree/diff/secret checks and a native independent reviewer `ACCEPT` on exact SHA. These were not independently rerun or retrieved from the native tool. Reviewer also reported pytest absent in their environment. Distinguish source-level verified results from local-test reports.
- Full suite was **not rerun** for this narrowly scoped repair. Historical baseline-matched Python 3.11 8 failures / Python 3.14 7 failures remain reported historical evidence, not newly certified as harmless.

**Lane A decision:** The identified digest serialization bug is fixed in source and the narrow repair is verified to the degree above. No fresh mandatory code action is identified from this particular source diff. This is NOT Canonical main integration, Gate completion, true synthetic media provenance or production readiness.

## Lane B: independent critique of proposed architecture

- The proposal explicitly identifies the current self-authored `SYNTHETIC_FIXTURE_ONLY` JSON record+digest as scope/integrity binding, **not genuine generator provenance**. That distinction is correct and central to the project.
- Recommended alternatives are reasonable for a limited local-first threat model: B = reviewed, closed fixture allowlist/manifest with exact bytes and permitted operations; A = constrained generator that cannot accept arbitrary source file paths/URLs; A+B may provide broader generated fixture coverage.
- Key caveat: a manifest digest in the same freely editable checkout, a locally generated receipt, or a locally embedded verification public key is **not independent trust against a same-user adversary controlling code, data and tools**. The document acknowledges this. Therefore the selected trust claim must remain an operational guardrail against error/misconfiguration unless a protected independent trust anchor is adopted.
- Another key caveat: a generic `--source arbitrary_path` workflow that merely hashes bytes from a user-selected video **cannot serve as a strict pre-read fixture authorization**. Strict v1 should select `fixture_id` against an independently selected policy-owned root/manifest BEFORE any media probing/decoding/indexing, then bind the read descriptor's bytes to manifest digest/size. Unknown path/ID must refuse before reading that media. Be explicit that the policy selects what may be read; measured SHA checks that the authorized bytes match.
- A first-only B slice is the simplest initial implementation where a stable fixture set is sufficient. Do **not** silently add A's FFmpeg/toolchain/generation receipt and execution authority in the same first patch. Add A only if dynamic fixtures are demonstrably necessary and its executable provenance/argument restrictions can be implemented and tested safely.
- If existing dynamically generated synthetic CLI fixtures require A, preserve them as *lower-assurance test harness operations*, clearly separate from a strict production-facing fixture admission mode, or obtain a versioned test-only contract exception. Never silently call their existing self-declared grants trusted.
- No unsigned/local self-issued receipt or digest should be labeled a cryptographically authenticated issuer. Manifest matching is `MATCHED`; measured bytes/probe evidence stays `MEASURED`; no new evidence class. The report remains `POINT` with unknown temporal width; CORE-01 legacy interval stays `BLOCKED_BY_CONTRACT`.
- The Lane B proposal did not receive a separately reported independent native reviewer, and its LAB workspace verifier reported 26 Canonical-specific expectations failing. The latter is a provenance/compatibility/tooling finding, not proof the design itself is invalid. Do not proclaim the verifier passed or import Canonical-only files wholesale into LAB merely to silence it.
- No proof was found in the document that the user currently possesses a separately protected manifest root, trusted release or protected signer. A future design **must not assume** an unverified anchor exists.

## Recommended Owner architecture decision (not yet given)

1. **Threat-model selection:** Initial strict fixture admission targets honest-mistake/accidental or low-capability misuse on a reviewed repository/test-runner environment; it makes NO claim of security against an actor who can edit all local trust anchors.
2. **First slice:** Approve the minimal **B-only closed fixture manifest** path for explicitly reviewed synthetic test artifacts. Defer dynamic A generator and signature C until demonstrated need and separate owner approval. If test use-cases demand generated MP4, evaluate A in a follow-on design rather than pretending B covers all cases.
3. **Manifest source authority:** Require a pinned reviewed repository SHA / trusted CI-controlled artifact and explicit runner assumption. Do not treat the mutable workspace itself as independently authenticated. When no acceptable trust root is established, strict admission must fail closed.
4. **Legacy behavior:** Decide whether old arbitrary-source + self-declared JSON grant is disabled under `analyze-local`, or retained as a clearly marked *lower-assurance developer harness* with no ability to yield trusted reports and no protected media authorization. Preferred for strict admission is **deny arbitrary sources before probe/read**. Migration/compatibility must be designed and independently reviewed, not silently broken.
5. **Scope:** Local generated synthetic probe/index/query/report with fake embeddings only, finite resource budgets; REAL/protected media/model/provider/production/Gate workflows stay forbidden.
6. **Approval sequencing:** Owner must first approve this precise architecture boundary; only then prepare a detailed versioned implementation plan, with a further explicit code authorization. Do not write provenance enforcement code from a draft design.

**Disposition:** Lane A source repair accepted for its authorized limited scope. Lane B design is plausible for the declared limited threat model, but owner selection of the trust anchor, initial slice and legacy path policy is a hard decision before implementation planning.

**Terminal markers:** `CORE02_DIGEST_REPAIR_SOURCE_VERIFIED` · `SYNTHETIC_FIXTURE_PROVENANCE_DESIGN_OWNER_DECISION_PENDING` · `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.
