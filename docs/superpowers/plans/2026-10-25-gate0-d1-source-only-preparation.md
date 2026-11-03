# Gate-0 D-1 Source-Only Preparation — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or repository-approved rolling-frontier parallel execution in distinct worktrees. This is a three-lane, exclusive-writer plan; do not spawn artificial workers or serially block genuinely independent work. Steps use checkboxes.

**Goal:** Prepare a real-Gate-0 input and verification *software path* entirely under synthetic/generated fixtures, while retaining a hard, explicit prohibition on real-media/model/provider/scored execution until later Owner approvals.

**Architecture:** Reuse Gate-0's existing ten-stage orchestrator, closed 13-artifact contracts, generated-media probe/decoder and label/evaluation validators. Add an **explicitly separate, fail-closed** `authorized_local` preparation path rather than disguising it as `media-corpus.json` or `synthetic-corpus.json`. In parallel, create standalone reviewer-envelope and config-freeze tools with their own test ownership. Existing frozen contract and thresholds stay authoritative.

**Tech Stack:** Python 3.11/3.14; pytest; stdlib JSON/hashlib/pathlib; existing Gate-0 adapters and `gate3.fixturegen`-style generated/disposable media where used. No cloud, real model weights, installation or network.

**Spec / approved scope:** `docs/decisions/2026-10-25-gate0-d1-source-only-preparation-approved.md`; PR #182 packet `docs/gate0/OWNER_AUTHORIZATION_INPUT_PACKET_2026-10-25.md` at immutable SHA `4a65bff0904c60163bf501014e07fbe5d4239cfc`; frozen `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md`; `docs/implementation-spec-v1.1.md`; `docs/implementation-spec-v1.1.1-erratum.md`.

## Global constraints / baseline

- Planning BASE_SHA `18a86820ccc78dbfa2dd571661ea9a6d3e813289` (post Gate-3 #181/#183/#184/#185); always recheck live `main` and ownership before work. Read `AGENTS.md`, `docs/INDEX.md`, the above decision/contracts and source implementation; work on an isolated branch/worktree.
- Owner approved **D-1 only**. D-2 genuine corpus, rights and editor/reviewer assets `PENDING`; D-3 real execution `NOT_AUTHORIZED`. An actual `authorized_local` invocation with no independently attested D-2/D-3 must yield `BLOCKED_PREREQUISITE` (exit 20 where CLI contract specifies), not process media, silently treat generated input as real, or return a Gate verdict.
- Only repository-checked fixtures/disposable generated MP4; no protected or any real archive file/hash/probe/decode/mount; no authentic model load/download/inference, PyPI/network/provider call, scored trial, rendered output or Gate promotion. No production activation claims.
- Preserve original synthetic 10-stage CLI, fake embedding, generated-media identity guards, 13 mandatory artifacts, `NOT_RUN` status/exit 20, 40 query split (24 positives 6/family + 8 absent, 8 development), two reviewers, 4-second/2-FPS technical windows, source PTS, 20/24 and 5/24 and 3/6 thresholds. No model timestamps as cut bounds.
- No `src/gate3/**`, `src/gate1/**`, `src/gate2/**`, shared `schemas/gate0/**`, `src/gate0/evaluation.py`, `src/gate0/labels.py` changes without separate contract-owner ruling. Do not create a new development SOURCE-AUTH grant system (ADR-0003). Do not touch canonical main or immutable backup.
- **Single writer per named path.** Workers may read other lanes' modules for contracts but must not edit them. CI workflow edits and shared manifest/schema changes require explicit owner assignment to a controlled integration lane, not concurrent task workers.
- If an exact package version/lock or real SigLIP interface requires downloading/unobserved artifacts, record `BLOCKED_DEPENDENCY_VERIFICATION` and continue safe code/tests without fetching or inventing hashes. Passing tests that only use fake adapters are **not** authentic model evidence.

## Five review-priority negative cases

1. Real-corpus path with missing D-2/D-3 attempts to read named source ⇒ **refuse before file access** (Lane A); test via source-open/probe/decoder spies that would raise if invoked.
2. Generated fixture with a forged `authorized_local` tag ⇒ never produce real experiment evidence or PASS (Lane A).
3. Real-mode call accidentally loads labels into the ranker or uses `FakeEmbeddingAdapter` as a real embedding model ⇒ hard refusal, no scored result (Lane A).
4. Invalid/incomplete/conflicting blinded reviewer rows (unknown token, one reviewer, duplicate key, mismatched digest/adjudication) ⇒ assembler refusal; no fabricated human judgement (Lane B).
5. Placeholder all-zero/unverified provenance or changing inputs after freeze ⇒ `BLOCKED_PREREQUISITE`/explicit failure, not an "approved" configuration (Lane C).

---

## Lane A — G0-D1-A / P-08 core real-path *preparation* (single writer)

**Owns:** `src/gate0/cli.py`, `src/gate0/execution.py`, `src/gate0/media_experiment.py`, `requirements/gate0.lock` **only when a reproducible offline resolution is independently verified**, plus dedicated new tests under `tests/gate0/unit/test_authorized_local_d1_*.py` and `tests/gate0/media/test_authorized_local_d1_*.py`. No changes to Lane B/C modules or frozen labels/evaluation/contract schemas.

**Existing signatures to preserve:** `gate0.execution.has_synthetic_input(input_root)`, `has_media_input(input_root)`, `execute_stage(...)`; `gate0.media_experiment.measure_revision(revision, *, input_root, ...)`; `gate0.cli.main()`. The `gate0.media_experiment.MEDIA_CORPUS_KIND` remains `generated_synthetic_media_not_experiment_evidence` for its original path.

### A0. Baseline and TDD readiness
- [ ] Confirm main/tree, scope, exclusive paths, existing `src/gate0/execution.py` at `_load_inputs`, `_stage_prepare`, `_stage_inventory`, `_representations`, `_stage_embed`; `media_experiment.py` fixture provenance guard; `cli.py` stage routing; compatibility fixture lock.
- [ ] Run baseline `PYTHONPATH=src:experiments:scripts python -m pytest tests/gate0 -q`; record real counts and any environment-only failure. Keep synthetic `NOT_RUN` exit-20 expectation.
- [ ] Define the smallest reversible seam: `has_authorized_local_input(input_root: str|Path) -> bool`; `load_authorized_local_declaration(path: Path) -> Mapping[str, Any]` (new in `media_experiment.py`); explicit `authorized_local` marker and provenance, not the existing generated-media marker. New declaration filename **proposed by this plan**: `authorized-corpus.json`. If a frozen schema requires another exact path/field, stop and obtain a contract disposition rather than self-authorizing a schema rewrite.

### A1. Distinct admission + hard operational gate
- [ ] **RED** `test_authorized_local_d1_refuses_without_d2_d3_before_source_io`: create an in-memory/synthetic declaration and source-open/probe/decoder spies; call the CLI path and assert exit 20 `BLOCKED_PREREQUISITE`, zero media accesses, zero model accesses, zero output Gate decision.
- [ ] **RED** `test_generated_fixture_cannot_be_promoted_by_corpus_kind_relabel`: a fixture manifest renamed/relabelled `authorized_local` cannot produce a real result; pre-existing generated `media-corpus.json` remains unchanged and `NOT_RUN`.
- [ ] **GREEN** implement strict mode dispatch + refusal gate in `cli.py`/`execution.py`; read only the *declaration* under allowed tests. Real-mode authorization is a future D-3 trust root, not a fabricated D-1 env var or an automatically trusted JSON flag. If real mode cannot be safely activated today, leave it deliberately non-executable and return its explicit blocker.
- [ ] Run targeted and existing CLI/media admission tests; commit first contract-safe A1 slice.

### A2. Generated-fixture proof of source/provenance preparation
- [ ] **RED** tests on synthetic declarations/fixtures for source revision/occurrence/content identity, split-group relations, selected stream, local-only policy, digest-bound identity, no-follow/symlink/hardlink/quota limits and measured actual window extent rather than trusting declared `window_count`.
- [ ] **GREEN** implement reusable *validation/preparation* helpers in `media_experiment.py` while keeping `_require_source_provenance` mandatory for the pre-existing generated-media execution path. Do not bypass that guard or process any real source.
- [ ] Exercise VFR/non-member sample PTS, mixed-stream ambiguities, attempted source mutation; no `seconds × nominal FPS`. Where a generated test requires instrumentation instead of ffmpeg real decode, use the project's existing fake probe/decoder seam.
- [ ] Run Gate-0 generated-media tests and commit.

### A3. Human query/gold input seam, never ranker leakage
- [ ] **RED** test that `editor-queries.json` and `human-gold.json` *proposed names* are loaded only by their correct stage under a synthetic test seam; missing/not version-frozen/editor-origin-unverified inputs fail. Assert 40 query cardinality/split, 24 positives with six per family, eight absent, eight development, two distinct reviewers/adjudication, half-open typed intervals and human-origin status.
- [ ] **RED** test that `rank` receives no gold/human judgments, no ranker read of human labels; edited query text changes version digest; no synthetic vectors reused for real predictions.
- [ ] **GREEN** separate real-input preparation from synthetic `_load_inputs` path in `execution.py`, pass only typed projections to existing `labels.build_queries/build_gold_events` and never silently accept fake labels as true. Keep authentic evaluation blocked until D-2/D-3.
- [ ] Run tests and commit.

### A4. Authentic-model and decoder precondition wiring, no model load
- [ ] **RED** synthetic tests for absent model identity/root/licence/weights SHA/processor/preprocessing/runtime precision + no mounted sandbox: explicit `BLOCKED_PREREQUISITE`, zero `LocalSiglipEmbeddingAdapter.load_cpu` calls, zero inference, zero network.
- [ ] **RED** test that a real-mode path cannot invoke the `FakeEmbeddingAdapter` as if authentic; generated-media path still uses fake vectors and stays `NOT_RUN`.
- [ ] **GREEN** wire a narrow deferred `LocalSiglipEmbeddingAdapter` configuration/precondition seam and `decode_pixels=True` capability **behind** the real-mode operational gate. Verify no actual decode of real files and preserve synthetic deterministic behavior. Do not change frozen `src/gate0/adapters/siglip_local.py` without a new contract disposition.
- [ ] Dependency lock: retain existing `pytest==8.3.3` lock and, if offline pinned compatible versions can be independently established, update the lock with provenance; otherwise report this specific remaining blocker rather than invoking PyPI or claiming `torch`/`transformers` installed.
- [ ] Run all Gate-0 focused/whole suite; verify no Gate PASS; commit.

### A5. Independent review, delivered PR
- [ ] Fresh `PYTHONPATH=src:experiments:scripts python -m pytest tests/gate0 -q`, negative mutation checks and `bash scripts/verify-workspace.sh`. Record exact pass/fail/xfail/environmental baselines, no unapproved network or true model calls; scan secrets. No auto-merge.
- [ ] Request an independent read-only reviewer; compare source changes to the frozen contract; push branch `implementation/g0-d1-a-authorized-local-prep-20261025` and open a PR with exact base/head, file ownership and `BLOCKED` remainder.

---

## Lane B — G0-D1-B / P-05 reviewer-envelope tool (parallel, independent)

**Owns:** new `src/gate0/reviewer_envelope.py` and new `tests/gate0/unit/test_reviewer_envelope_d1.py` only. Read but do not edit `src/gate0/evaluation.py` or `labels.py`.

**Reference interfaces:** `gate0.evaluation.ReviewerInputEnvelope`, `load_reviewer_input(path, *, authorized_root, token_map, expected_mapping_digest, expected_input_digest=None, mapping_version='gate0-v1', config_digest='0'*64)`; `_input_digest_for`, `_mapping_digest_for` (existing helper references, not separately frozen public API). Expected closed envelope is `{'schema_version','input_digest','blind_mapping_digest','rows'}`; version `gate0.reviewer-input.v1`; two tokens `arm-a/arm-b`.

### B1. Synthetic valid closed envelope TDD
- [ ] **RED** `test_generated_synthetic_two_reviewer_envelope_roundtrips_loader`: pass artificial valid reviewer rows and a fake token_map, assert canonical digest stability and `load_reviewer_input` roundtrip under a disposable authorized *test root*.
- [ ] **GREEN** implement `build_reviewer_envelope(rows: Sequence[Mapping[str, Any]], *, token_map: Sequence[Mapping[str, str]], mapping_version: str='gate0-v1', config_digest: str='0'*64) -> dict[str, Any]` in new module. Reuse existing canonical digest logic; never insert/refashion human grades or human-authored strings.
- [ ] Keep blinding enforced at creation/validation: no real arm ID in reviewer-visible rows, no ranker identity, and no synthetic labels falsely described as human review.
- [ ] Run focused tests and commit.

### B2. Negative + emission tests
- [ ] **RED** cases: one reviewer; same reviewer twice; token mismatch; extra/missing keys; duplicate (query,window,token,reviewer); forged `input_digest`/`blind_mapping_digest`; grade outside 0–2; unknown status; adjudication disagreement and unknown query/window; crossing dev/eval review. Fail closed without creating output.
- [ ] **GREEN** minimal assembler validation + optional explicit atomic write to a disposable output path guarded by its caller-provided root; no filesystem read of real reviewer media. For input deficiencies that existing loader does not detect, do **not** silently weaken gate; flag as `PENDING` contract-owner issue.
- [ ] Run `tests/gate0/unit/test_reviewer_envelope_d1.py`, relevant evaluation tests, complete Gate-0 suite and verifier; independent read-only review, push `implementation/g0-d1-b-reviewer-envelope-20261025`, PR no merge.

---

## Lane C — G0-D1-C / P-09 configuration digest/freeze inspector (parallel, independent)

**Owns:** new `src/gate0/config_freeze.py` and new `tests/gate0/unit/test_config_freeze_d1.py` only. Existing `config.py`, `config/gate0/default.json`, frozen schemas and policy modules are read-only.

### C1. Fail-closed freeze report
- [ ] **RED** `test_placeholder_config_cannot_be_frozen_as_real`: pass `config/gate0/default.json` with 64-zero placeholder values and no D-2/D-3, assert `BLOCKED_PREREQUISITE` and explicit missing-input identities (not a usable real config).
- [ ] **RED** `test_generated_fixture_freeze_is_not_authentic`: compute canonical digests from generated fixture *inputs*; emit deterministic audit only, no signed/approved model or Gate verdict.
- [ ] **GREEN** implement `inspect_freeze_readiness(config: Mapping[str, Any], *, observed_digests: Mapping[str, str], execution_authorized: bool=False) -> Mapping[str, Any]`. `execution_authorized=True` is **not itself a trust grant**: in D-1 software the output remains preparation-only and cannot activate a real execution path. Report source of every observed digest, placeholder/refusal statuses, stage at which digest may legitimately be computed.
- [ ] Pin schema validation via existing `gate0.config.load_config` (read-only) where practical; preserve exact canonical SHA-256 and no unwarranted substitution of generated fixture IDs as real assets.
- [ ] Run focused tests and commit.

### C2. Mutation/stability and delivery
- [ ] **RED** digest substitution, misreported policy roots, mismatched source-manifest revision, ambiguous pre/post inventory freeze, digest tampering and unknown keys: fail closed. No configured root or model asset is opened.
- [ ] **GREEN** implement deterministic sorted failure/need list and digest closure on synthetic metadata; no changes to frozen thresholds/window cardinality.
- [ ] Run `tests/gate0/unit/test_config_freeze_d1.py`, relevant config tests, full Gate-0 suite and verifier; independent reviewer, push `implementation/g0-d1-c-config-freeze-20261025`, PR no merge.

---

## Integration order and explicit STOP boundaries

1. **B and C** have no shared source paths and can run in parallel with A. They may finish or be reviewed independently. Their interfaces are *tools*, not a new scored-run approval. B/C integration need not await real corpus.
2. **A** owns the only existing Gate-0 orchestrator file, so there is one A writer. Bring in B/C helpers *only after* their independently reviewed PR heads and compatibility are verified by the integration owner; no concurrent edits to `execution.py`.
3. After each merge: pin immutable candidate SHA, verify relevant PR CI; run the truly combined suite in an authorized local environment and record full-suite results. Only one integration path; no speculative status/semantic uplift. Update `docs/project/01_CURRENT_STATE_AND_HANDOFF.md` via independent reconciliation.
4. **Hard STOP:** source rights, actual local-corpus access, installing/loading model/weights, external packages and network, sandbox mounts, human review of authentic corpus, provider calls, actual scoring, Gate PASS, or any schema/error/architecture conflict requiring frozen-contract modification. Those remain D-2/D-3 and contract-owner matters; preserve a specific blocker record.
5. Gate-0's current synthetic report still exits **20 / `NOT_RUN`**, no matter how many generated tests pass. `GATE_PASS` cannot occur under D-1.

**Six-Cycle Iterative Refinement:** current source baseline → authority/ownership audit → minimal additive seams vs forbidden fixture spoofing → test-first implementation → independent negative/security review → GitHub-head and integration verification. A task's missing operational inputs are `NOT_OBSERVED`, not "completed" by software scaffolding.
