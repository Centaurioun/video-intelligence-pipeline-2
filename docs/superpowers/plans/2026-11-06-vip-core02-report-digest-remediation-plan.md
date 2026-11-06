# VIP CORE-02 Report V1 persisted digest remediation plan

> **For Codex implementation workers:** Execute this plan task-by-task only in a verified isolated Canonical native worker/worktree and owned candidate branch, complying with live `AGENTS.md` and native-thread Portfolio authority. Test-first behavior change; independent review on final immutable SHA.

**Goal:** Fix the definite Report V1 serialization bug: a correctly computed SHA-256 `report_digest` is currently stripped from the on-disk JSON. Constrain changes to this defect and directly related publication failure-path tests.

**Approved:** Owner authorization recorded in `docs/decisions/2026-11-06_CORE02_DIGEST_REPAIR_AND_FIXTURE_PROVENANCE_DESIGN_AUTHORIZATION.md`, same LAB planning branch.

**Pinned implementation source:** Canonical `Centaurioun/video-intelligence-pipeline@520ab543c7eb765ce1cba989742dde3abd4bbf4e`, tree `3ad25b7b00b03a14e6ed2cc068a027dc042f2a46`. Frozen main `3bfcc2ba221b36df6773e630b44479ec961d630a`. Read independent audit at LAB `review/vip-core02-independent-audit-20261106@63f410e5e48cd962efd3e28fe724bbf90f13f552`.

## Hard scope / owned files

- Modify `src/vip_fvs/core_report.py`; modify `tests/vip_fvs/unit/test_core_report.py`.
- Only if needed for an actual persisted CLI end-to-end regression, modify `tests/vip_fvs/integration/test_core_analyze_local_cli.py`. If a minimal source change outside `core_report.py` is demonstrably necessary, STOP and obtain an explicit owner-bound scope expansion.
- Lane B synthetic fixture provenance investigation is **not** part of this code task. Do not modify `query_analysis_authorization.py`, `cli.py` production code, `core_analysis.py`, `core_generation_evidence.py`, index/SQLite schema, source snapshot code or any Gate-3/legacy review-bundle module.
- Use freshly verified clean isolated **Canonical successor branch/worktree** at exact above code SHA, not the dirty main checkout or an existing CORE-02 worker worktree. Suggested branch `feature/vip-core02-report-digest-repair-20261106`. A normal feature push and synthetic CI are allowed; no integration PR, no main merge.
- No protected/real media, real model/provider execution, downloads, cloud inference, edit/render/QC, Gate promotion, destructive Git, or backup modification.

## Verified root cause (GitHub source)

`src/vip_fvs/core_report.py::_canonical_bytes(report)` removes `report_digest` before serialization (lines 44–50). This is suitable for `compute_core_report_digest` (lines 53–56), but `publish_core_semantic_report` lines 164–167 sets `payload_report["report_digest"]` and then calls `_canonical_bytes(payload_report)`, **removing that field again from published bytes**. Existing unit tests check digest computation but not digest presence in the persisted JSON. Keep SHA-256 over exact canonical **digest-excluded** report data and ensure final published JSON includes the computed `report_digest`.

### Task 0 — isolated branch and baseline evidence

- [ ] Independently verify current remote Canonical main, CORE-02 branch HEAD, immutable source SHA/tree and approved owner receipt; inspect current Canonical `AGENTS.md`, handoff/protocols, exclusive writer lease and existing branches before creating a verified native worker.
- [ ] From exact `520ab543...`, bind a fresh clean isolated successor worktree and unique branch via the current native project/Worktree Admin mechanism. Record thread ID, host, project ID, worktree, common Git dir, base SHA/tree, zero dirt, one writer and no overlapping contracts. Do not modify existing worktrees.
- [ ] Capture available Python 3.11/3.14, pytest/FFmpeg and the exact starting test command. Existing baseline matches are historical, not newly run.

### Task 1 — real regression RED, minimal fix GREEN

- [ ] Add `test_published_report_contains_verifiable_digest`: publish a synthetic Report V1 to a fresh `tmp_path`, reload bytes with `json.loads`, assert `report_digest` is a 64-character lowercase hex string, assert `compute_core_report_digest(reloaded) == reloaded["report_digest"]`, then `validate_core_semantic_report(reloaded)`.
- [ ] Add `test_published_bytes_deterministic_with_report_digest`: publish semantically identical report payloads into two new independent output-root destinations; assert **identical serialized bytes** and independent digest recomputation without relying on a nonce or absolute target path.
- [ ] Add `test_post_publication_digest_tampering_refuses`: mutate reloaded content without updating the digest and assert the existing validator refuses with `CORE_REPORT_DIGEST_MISMATCH`. Preserve explicit `NOT_OBSERVED` marker and evidence classes.
- [ ] Run `PYTHONPATH=src:experiments:. python -m pytest -q tests/vip_fvs/unit/test_core_report.py` on the **unmodified starting candidate**, capture the new tests' explicit RED failures; do not count absent module/collection failure as behavioral RED.
- [ ] GREEN minimal fix: separate the canonical **hash-input encoding** (excludes digest) from the canonical **published artifact encoding** (includes digest). Keep `json.dumps` sort keys, separators, Unicode policy, finite-number validation, trailing newline, no-clobber semantics and output schema stable; never self-hash the final document.
- [ ] Re-run new unit tests until GREEN; run the entire existing `test_core_report.py`, and `tests/vip_fvs/integration/test_core_analyze_local_cli.py`. Add a published-file digest assertion to the generated-media CLI test if it runs with available synthetic FFmpeg. Record the precise test IDs and skip reasons.

### Task 2 — publication failure-path fault injection (no broad rewrite)

- [ ] Existing target collision: file and symlink test must prove prior target bytes unchanged; previous report must not be replaced on repeat command.
- [ ] Inject failure **before** `os.link`: demonstrate no published target and no unexplained temporary artifact; do not assume a failed action committed.
- [ ] Inject failure **after** successful `os.link` (e.g., failure in `os.fsync(parent_fd)`): record that target may exist even if operation raised. Test its actual state and digest. Do not make a contradictory promise of "no output on every failure" or automatically remove an already linked destination.
- [ ] Evaluate directory/ancestor symlink swap and concurrent-collision risks within the existing dir-fd, `O_NOFOLLOW`, hard-link publication logic; add adversarial tests if practical, otherwise mark those conditions `NOT_OBSERVED` with precise limits.
- [ ] If correctness requires changing atomic publication protocol, introducing a new outcome state or source API beyond digest serialization, STOP with an exact design/authorization request. **Do not silently implement a larger recovery protocol or delete uncertain committed output.**

### Task 3 — regression, independent review, publication

- [ ] Run focused CORE-02 five-file suite and relevant Canonical CLI/index and provenance tests on Python 3.11 and 3.14 where available; `compileall`, `git diff --check`, secret scan, no unauthorized source changes. Preserve historic 7 (3.14)/8 (3.11) matched failures; any newly observed failures require a same-command/same-env comparator on `520ab543...`.
- [ ] Acquire independent feature review at the **final new SHA**, assessing exact persisted digest, no-clobber, self-reference-free canonicalization, failure-after-link ambiguity, stable Report V1 compatibility, unchanged synthetic grant and temporal semantics.
- [ ] Commit and normally push only authorized files to unique Canonical feature branch; run available synthetic GitHub Actions at the exact final SHA. Note GitHub smoke only certifies its selected tests, not full test suite. No PR/main merge.
- [ ] Report source SHA/tree, final branch/commit, changed files, RED/GREEN receipts, persisted report and tamper tests, publication fault observations, independent review, Python 3.11/3.14 and CI evidence, remaining provenance-design blocker. Terminal `CORE02_DIGEST_REPAIR_VERIFIED` only with test+review proof, otherwise `CORE02_DIGEST_REPAIR_PARTIAL`.

## Invariants

Do not change the typed `POINT` position semantics, sampled integer PTS/rational timebase, `MATCHED` vs `MEASURED`, `NOT_OBSERVED`, `ZERO_MATCH`, legacy CORE-01 `+1s` behavior, real-mode block or source occurrence/stream contracts. **Fixing the persisted digest does not establish trusted synthetic fixture provenance or authorize production deployment.**

**Terminal plan:** OWNER-AUTHORIZED BOUNDED REPORT DIGEST REPAIR; NO MAIN MERGE.
