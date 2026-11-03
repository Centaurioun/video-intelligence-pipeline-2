# Gate-0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task under the explicit Issue #9 execution authorization. Every task uses checkbox steps and must preserve the repository's Luna Medium, isolated-lane, and main-agent integration rules.

**Goal:** Build only the reviewed Gate-0 local sampled-visual retrieval diagnostic, answering whether one offline text-to-image embedding arm improves grade-2 visual-moment retrieval over the metadata floor on a frozen source-disjoint corpus.

**Architecture:** A local, provider-neutral, stage-ordered CLI publishes exactly 13 persisted result files under one immutable run directory. Typed contracts, explicit authorization/policy boundaries, rational PTS sampling, deterministic local ranking, and sealed attempts make the diagnostic replayable without adding later-gate services or capabilities.

**Tech Stack:** Python 3.11.9; `pytest`; FFmpeg/ffprobe adapter; UTF-8 RFC-8785-style canonical JSON/JSONL; SHA-256; Linux `bwrap --unshare-net --die-with-parent`; exact lockfile `requirements/gate0.lock`; float64 row-major numeric operations with single-thread controls.

**Spec:** `docs/implementation-spec-v1.1.1-erratum.md` (narrow overlay for the clauses below); `docs/implementation-spec-v1.1.md`; `docs/audits/GATE0_SPEC_NORMALIZATION_REVIEW.md`; `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md`; `docs/architecture/CANONICAL_CONTRACTS.md`; `docs/architecture/ASTRA_DECISION_REGISTER.md`.

## Global Constraints

- Planning-only until a separate explicit user approval; this plan authorizes no code, tests, fixtures, schemas, real media, model downloads, provider calls, cloud egress, or later gates.
- Gate 0 remains local-only, source-preserving, provider-neutral, and bounded to exactly 13 persisted result files; configuration and test fixtures are not runtime result artifacts.
- Use `NOT_OBSERVED` for unavailable runtime, corpus, model-feasibility, performance, thermal, decoder, and enforcement evidence; static review is not runtime validation.
- Keep evidence classes distinct and never convert semantic/model time into frame-accurate cut coordinates; use the declared PTS/time-base domains only.
- Never commit secrets, credentials, model weights, large media, caches, vector stores, or third-party source changes.
- Every implementation task is TDD-shaped: failing test, observed RED, minimal implementation, observed GREEN, focused regression/refactor, and scoped commit.

---

> Status: Issue #9 execution authorized for plan-bounded local/synthetic T00–T11 implementation only. Real-media/archive processing, model downloads, provider calls, cloud egress, and Gates 1–3 remain prohibited.

## 1. Authority, outcome, and fixed boundary

Implement only the reviewed Gate-0 sampled-visual retrieval diagnostic described by `docs/implementation-spec-v1.1.md`, with the narrow current `docs/implementation-spec-v1.1.1-erratum.md` overlay controlling discovery authorization, policy ownership, envelope cardinality/FK, purpose, CLI, and gate-decision wording, plus `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md`, `docs/architecture/CANONICAL_CONTRACTS.md`, and `docs/architecture/ASTRA_DECISION_REGISTER.md`. The future implementation must answer one question: whether one locally executed offline text-to-image embedding arm improves grade-2 visual-moment retrieval over the transparent metadata floor on a frozen source-disjoint corpus. It must remain local-only, read-only with respect to source media, provider-neutral, and bounded to the declared 13 persisted artifacts.

The implementation starts only after this plan and the specification receive separate explicit approval. The current specification remains `GATE0_SPEC_DRAFT — REVIEW REQUIRED; IMPLEMENTATION NOT APPROVED`; all current runtime behavior and corpus availability are `NOT_OBSERVED`.

## 2. Repository surface and ownership

### Implementation-boundary decisions frozen by this plan

These are implementation choices within the approved contract, not new Gate-0 capabilities. They are recorded here so a later implementation session does not re-decide them:

0. **Authority precedence:** `docs/implementation-spec-v1.1.1-erratum.md` is the narrow current overlay for discovery authorization, policy ownership, envelope cardinality/FK, purpose, CLI, and gate-decision wording; `docs/implementation-spec-v1.1.md` remains authoritative for all other Gate-0 behavior. The architecture contract's 12-file experiment-result list remains historical context at this boundary; the normalized 13-file inventory, including `discovery_authorizations.jsonl`, is unchanged. Any unrelated architecture change requires a new versioned specification and plan review. Where later annex prose says the operation-to-purpose mapping is identity, the overlay controls: HASH and PROBE are T02 discovery suboperations and map to DISCOVER.
1. **Runtime and control input:** Python 3.11.9 is the planned runtime because the repository already uses Python for its verification/curation tooling and has no competing production runtime. `config/gate0/default.json` is the one canonical control input, UTF-8 RFC-8785-style canonical JSON, and its `config_digest` is the SHA-256 of canonical bytes. `requirements/gate0.lock` is the one exact resolved dependency lock; its canonical-byte SHA-256 is `dependency_lock_digest` and is recorded separately from `config_digest` in `run_manifest.json`. The run manifest also requires `python_version`, `os_release_digest`, `runtime_executable_digest`, `dependency_lock_digest`, and `blas/thread-control digest`. Changing language, minor version, lock path, or adding a service requires a plan revision.
2. **Artifact layout:** the output root contains exactly the 13 named result files from the specification. `schemas/`, `tests/`, fixtures, logs, temporary files, vector payloads, indexes, rollback records, and egress records are source/test inputs or records inside the 13 files, never additional persisted run artifacts. Atomic publication uses an ignored temporary path removed before successful completion.
3. **Timing authority:** the selected decoder’s declared presentation sequence is authoritative. The default adapter does not reorder frames; any adapter that must reorder declares and records its deterministic ordering operation and cannot substitute a later minimum PTS. Source PTS/frame evidence is emitted only by this adapter. Equal PTS uses decoder ordinal, then bytewise source-frame identity; a missing tie key is protocol-invalid.
4. **Repeated-sample aggregation:** Gate 0 v1.1 aggregates over target slots, not unique frame identities. This is the explicit interpretation of the older contract’s “deduplicate repeated frames” wording: deduplicate/annotate observations for audit, but do not delete target rows or collapse valid target slots before pooling. Every target row therefore contributes one auditable slot observation when it has a valid selected frame; repeated selection of one frame remains visible. Unique-frame occupancy is a secondary diagnostic only. This v1.1 clarification is frozen in the run/config digest; changing it creates a new protocol version/run and cannot be introduced during coding.
5. **Network boundary:** the supported launch contract is `scripts/gate0-run.sh`, which must execute the Gate-0 process under Linux `bwrap --unshare-net --die-with-parent` with an explicit read-only workspace/output policy and inherited child namespace; the launcher records the bwrap executable/version digest and network-boundary attestation in `run_manifest.json`. There is no fallback to a process-local monkeypatch, host networking, DNS/proxy exception, or loopback exception. If bwrap or the attestation is unavailable, preflight blocks with exit 20. The injected egress guard remains defense-in-depth and a test seam.
6. **Policy timing and retention:** the sole control input is `config/gate0/default.json`; its typed `policy` object supplies retention expiry values, authorities, quarantine destination, and permitted post-expiry fields, while the effective decisions are persisted in `policy_decisions.jsonl`. There is no second `policy.json` control path. The implementation must not invent durations or retain locators/digests after expiry by default. Missing/inconsistent values are `BLOCKED_PREREQUISITE`, not a negative result.
7. **Identifiers and diagnostics:** IDs are opaque, deterministic within a frozen run and replayable from declared inputs/configuration, but never content identity or path identity. `attempted_bytes` and `transmitted_bytes` are separate fields; a blocked attempt may report the former while requiring `transmitted_bytes=0`.

The exact artifact-owner mapping is fixed as follows: `source_manifest.json` → inventory; `discovery_authorizations.jsonl` → inventory authorization rows; `policy_decisions.jsonl` → policy and the sole serialized owner of every `PolicyDecision`; `split_manifest.json` → split; `queries.jsonl` and `gold_events.jsonl` → labels/evaluation; `window_judgments.jsonl` → post-ranking labels; `window_sample_manifest.jsonl` → extract; `run_manifest.json` → run/stage owner; `ranked_candidates.jsonl` → rank; `runtime_and_failure_ledger.json` → operations/failure; `metrics.json` and `gate_decision.md` → evaluation/report. No other stage may create an independently persisted logical record for an owner’s record type.

Create production code only in `src/gate0/` and tests only in `tests/gate0/` after approval. Keep the existing `src/README.md`-only state unchanged during planning. Use these ownership boundaries:

| Area | Planned paths | Responsibility |
|---|---|---|
| CLI/stage orchestration | `src/gate0/cli.py`, `src/gate0/stages/` | legal stage order, options, exit classes, atomic publication, prerequisite projection |
| identity/canonicalization | `src/gate0/identity.py`, `src/gate0/canonical_json.py` | opaque IDs, RFC-8785-style JSON, record/file digests, bytewise ordering |
| contracts/schemas | `src/gate0/contracts/`, `schemas/gate0/` | 13-artifact schemas, envelopes, status namespaces, foreign keys, unknown-field rejection |
| inventory/policy | `src/gate0/inventory.py`, `src/gate0/policy.py` | discovery authorization, ffprobe evidence, effective ALLOW, local-only egress policy |
| split/labels | `src/gate0/split.py`, `src/gate0/labels.py` | relation freeze, transitive component split, query/gold/judgment versioning and blinding boundaries |
| temporal sampling | `src/gate0/temporal.py`, `src/gate0/adapters/decoder.py` | half-open windows, rational targets, presentation-order first-frame selection, VFR/PTS failure accounting |
| representations/arms | `src/gate0/arms/metadata.py`, `src/gate0/arms/semantic.py`, `src/gate0/adapters/embedding.py` | metadata floor and one offline semantic arm; no fallback or fusion |
| ranking/evaluation | `src/gate0/ranking.py`, `src/gate0/evaluation.py` | exact cosine, total-order ranking, blinded audit, Hit@10 and diagnostics |
| operations/artifacts | `src/gate0/artifacts.py`, `src/gate0/failure.py`, `src/gate0/repeat.py` | atomic outputs, immutable attempts, target conservation, retry, invalidation, rollback, repeatability |
| configuration | `config/gate0/default.json`, `requirements/gate0.lock` | one canonical control input and one exact dependency lock; no secret values |
| synthetic fixtures | `tests/gate0/fixtures/` | checked-in tiny fixture catalog, golden oracles, deterministic fake seams, and one media-backed smoke fixture; `tests/gate0/oracles/` is forbidden and is not a second oracle hierarchy |
| integration tests | `tests/gate0/` | stage order, schemas, policy, temporal behavior, ranking, failure, no-egress, repeatability, verifier |
| documentation/verifier | `docs/gate0/`, `scripts/verify-gate0.py`, `scripts/verify-workspace.sh` | implementation contract receipts and static/security checks; no runtime claim without execution evidence |

No task may add a vector service, queue, scheduler, UI, Drive materializer, cloud adapter, ASR, VDF, editor/render pipeline, AI QC, MCP orchestration, archive-scale index, or later-gate artifact.

## 3. Dependency order and task cards

The paragraphs in this section preserve the approved architectural reasoning
and traceability context. They are non-normative background. The normalized
task cards in Section 8, together with the task-to-test matrix, are the sole
executable task contract; if wording differs, Section 8 and the matrix control.
Every behavior-changing card follows RED → GREEN → REFACTOR and ends with its
listed checks. A card may not consume a later card’s output unless the
dependency is complete.

### T00 — approved workspace and configuration contract

Depends on: plan approval. Add only the exact approved lockfile `requirements/gate0.lock`; do not introduce an unreviewed dependency. Define `config/gate0/default.json` as the sole canonical control input with corpus, four-second windows, 2 FPS target schedule, thresholds, model/processor/runtime, policy, retention, and tie rules. Validate no secrets, provider endpoints, or mutable defaults.

RED: malformed/missing/secret-bearing `config/gate0/default.json`, missing `requirements/gate0.lock`, or mismatched config/lock digests is rejected with exit 30. GREEN: canonical config digest, dependency-lock digest, and immutable profile are emitted. REFACTOR: isolate filesystem/clock/policy seams. Check: `python -m pytest tests/gate0/unit/test_config.py -q`; canonical config/runtime/lock golden test.

### T01 — canonical IDs, JSON/JSONL, envelopes, and schemas

Depends on T00. Implement opaque IDs and canonical serialization. Define exactly 13 persisted artifact contracts: `source_manifest.json`, `discovery_authorizations.jsonl`, `policy_decisions.jsonl`, `split_manifest.json`, `queries.jsonl`, `gold_events.jsonl`, `window_judgments.jsonl`, `window_sample_manifest.jsonl`, `run_manifest.json`, `ranked_candidates.jsonl`, `runtime_and_failure_ledger.json`, `metrics.json`, and `gate_decision.md`. `config/gate0/default.json` is the input/control file, not a fourteenth result artifact. Define one owner, schema version, artifact envelope, record digest, payload digest, foreign keys, finite numbers, and unknown-field rejection.

RED: fixtures with wrong ID/status/type/digest/foreign key or an extra artifact fail. GREEN: all valid minimal fixtures validate and round-trip byte-identically. REFACTOR: centralize validators without duplicating logical records. Check schema and digest golden tests plus artifact-count assertion.

### T02 — source inventory and authorization

Depends on T01. Implement `prepare` and `inventory`, using only already-local authorized inputs. Discovery authorization permits only DISCOVER/HASH/PROBE. Record occurrence/revision/content identity, custody, selected stream/time base, pinned ffprobe JSON, inclusion/exclusion, relation components, source preservation, failures, policy references, and digests. A path is a locator only.

RED: missing/expired discovery, unreadable/probe-failing source, or zero/multiple eligible streams without a valid configured index yields named failure and no processing artifact. GREEN: deterministic synthetic inventory produces valid manifests, a single immutable `selected_stream_index`, and atomic publication. REFACTOR: injectable filesystem/probe/clock. Check `tests/gate0/integration/test_inventory_policy.py`, ffprobe fixture smoke, selected-stream positive/negative cases, and no source mutation assertion.

### T03 — relation freeze, split, query, and label protocol

Depends on T02. Implement `split` and `label`; freeze all relation edges before transitive-component allocation. Enforce source-disjoint development/evaluation. Persist 32 evaluation queries (24 positive, eight absent) plus eight development queries, exact text, family/presence/split/version digest, and the gold semantic intervals/adjudication inputs. Ranking cannot read labels. Blinded `window_judgments.jsonl` records are created only after ranking by T08; T03 does not persist placeholder judgments.

RED: cross-split relation, changed held-out label, one-reviewer pass claim, or gold path in rank inputs yields invalid protocol. GREEN: valid versions freeze and join by typed IDs/intervals. REFACTOR: keep label data flow physically separate from ranking. Check split leakage, label-version, blinding, and query-count tests.

### T04 — preflight and policy/egress boundary

Depends on T02 and T03. Implement `preflight` with fail-closed effective ALLOW checks at every stage boundary and governed cache/projection read. Validate corpus, retention, reviewers, frozen digests, licensed feasible offline model, budgets, fixtures, local-only network policy, and documentation/security checks. Add process/child deny-by-default egress adapter; blocked attempts record destination/protocol/attempted bytes/decision without payload and zero bytes.

RED: unknown/stale/revoked policy, secret, forbidden destination, missing prerequisite, or model infeasibility blocks with exit 20 or 30 as specified. GREEN: a fully synthetic authorized preflight is reproducible and records decision digests. REFACTOR: policy and egress are injectable and independently testable. Check no-network/provider sentinels, child inheritance, DNS/proxy denial, separate attempted/transmitted byte accounting, secret redaction, policy-cache denial, tombstone privacy, and prohibited-artifact scans.

### T05 — temporal windows and 2-FPS/VFR-safe sampling

Depends on T02 and T04. Implement `extract` over fixed four-second half-open windows from the selected stream’s normalized presentation origin. For integer target tick `t` in 0..7, define `target_num=t`, `target_den=2`, `window_start_num=4*i`, and `window_start_den=1` as exact rationals. For a frame with raw PTS `r` and origin PTS `o` in time base `q`, define reduced `normalized_pts_num=(r-o)*time_base_num`, `normalized_pts_den=time_base_den`; then define `relative_num=normalized_pts_num-window_start_num*normalized_pts_den` and `relative_den=normalized_pts_den`. Select iff `target_num*relative_den <= relative_num*target_den` and `relative_num*window_end_den < window_end_num*relative_den`, with `window_end_num=4`, `window_end_den=1`, all by integer cross-multiplication. Never compare a float or a pre-rounded stream tick. Serialize the single `sample_target` wire row defined in the handoff: `tick`, rational `target_offset`, optional raw/normalized rational objects, status fields, and `mapping_ref` absent exactly when normalized PTS is absent; a derived stream tick is never a second wire field. A non-representable target is compared as a rational and is never rounded for selection. Select the first decoded presentation-order frame satisfying the named predicate; never derive a frame from seconds×FPS. The selected-stream rule is the resolved `RevisionRef` from T02 and cannot be changed in T05. Persist stream, decoder ordinal, presentation order, DTS/frame index when available, source-frame identity, duplicate reason, and named coverage failures in the defined row. Preserve one auditable row per target and conserve planned = succeeded + failed + omitted + quarantined.

RED: negative/non-monotone/discontinuous/missing/out-of-range PTS, wrong stream, ambiguous time base, incomplete final window, and missing mapping reference produce explicit coverage/failure rows, never silent repair. Equal PTS is not itself ambiguous: decoder ordinal, then bytewise source-frame identity, must establish the frozen order; missing or invalid tie evidence is the failure. GREEN: fake decoder oracles produce exact selected PTS/frame outcomes for CFR, VFR, B-frame, malformed, duplicate, equal-PTS, boundary, and rational-time fixtures. The decoder adapter consumes the declared presentation sequence. Aggregate valid frame vectors over target slots in ascending target tick order; preserve unique-frame occupancy only as a diagnostic. REFACTOR: decoder/PTS seam remains injectable and its ordering authority is single-valued. Check temporal golden tests, target-slot aggregation, selected-stream rule, and target-conservation property tests.

### T06 — metadata floor and offline semantic representation

Depends on T05 and T04. Implement `embed` for the transparent floor and one development-selected offline text-to-image arm only. Metadata uses unchanged query plus original basename/immediate parent, Unicode-casefolded non-alphanumeric tokenization, token-set Jaccard, no labels/transcript/generated metadata. Semantic vectors are L2-normalized, averaged by window, then normalized; non-finite/zero vectors are status rows without rank. Freeze model/weights/processor/runtime/space/config digests before held-out access; failure never calls cloud fallback.

RED: gold/judgment input or provider endpoint appears in arm inputs; zero/non-finite vectors or missing policy are not silently dropped. GREEN: deterministic fake embedding and local smoke adapter generate valid representations and run-manifest descriptors. REFACTOR: embedding/filesystem/policy seams are explicit. Check vector hashes, normalization, metadata token and no-fallback tests.

### T07 — deterministic ranking

Depends on T06. Implement `rank` with exact local cosine and no external index. Exclude failed vectors from primary score while retaining status rows. Use the total tuple: finite score descending, bytewise UTF-8 source revision ID, normalized rational window start, bytewise window ID, bytewise unique candidate ID. Collisions are errors; display rounding never orders.

RED: ties, NaN/inf, non-normalized vectors, colliding keys, gold/judgment reads, and unstable ordering fail or remain status rows. GREEN: golden candidate order and score fixtures pass across fresh processes. Numeric identity is frozen to float64 inputs/outputs, fixed row-major accumulation order, model evaluation mode, single-thread BLAS/runtime controls, and recorded interpreter/OS/library digests; valid slot vectors are pooled serially by ascending target tick before normalization; the canonical tie key stores window start as a reduced integer numerator/denominator pair, never a float. REFACTOR: separate score computation from ordering and artifact publication. Check ranking determinism and no-gold-input tests.

### T08 — evaluation, report, and decision precedence

Depends on T03 and T07. Implement `evaluate`, `report`, and `gate_decision.md`. Compute query-macro grade-2 Hit@10 over exactly 24 positives, six-query family results, paired lift over the same candidate universe, absent-query diagnostics, all failures, coverage, and secondary diagnostics. Apply precedence INVALID_PROTOCOL → NOT_RUN/BLOCKED_PREREQUISITE → repeatability failure → quality/resource FAIL or diagnostic PASS. Thresholds are frozen per run and remain diagnostic, not an SLA or productivity claim.

RED: wrong denominator, empty ranking conflated with absent label, label leakage, invalid protocol projected to PASS, or one-reviewer pass fails. GREEN: synthetic oracle produces exact numerators/denominators and decision state. REFACTOR: evaluation only consumes declared digests and blinded post-ranking judgments. Check metrics and decision precedence tests.

### T09 — attempts, retries, invalidation, rollback, retention

Depends on T01–T08. Implement immutable attempts, stage transitions, atomic publication, one unchanged transient-I/O retry, `retry_of`, failure ledger, invalidation propagation, and idempotent rollback `AVAILABLE → QUARANTINED → CLEANUP_PENDING → CLEANED|TOMBSTONED`. Every target has a terminal disposition; source is never deleted/rewritten. Tombstones contain only permitted provenance/digest metadata and no raw payload.

RED: changed inputs/config/policy/model/threshold mutate an old run, retry silently overwrites, rollback is non-idempotent, or expired policy permits reads. GREEN: injected failures create sealed attempts, complete ledgers, quarantine and tombstone records. The typed `policy` object in `config/gate0/default.json` must define all five retention classes (`SOURCE_REFERENCE`, `DERIVED_REPLAYABLE`, `DERIVED_RESTRICTED`, `AUDIT_MINIMUM`, `TOMBSTONE`) with owner/authority, start event, expiry event/time zone, permitted readers, post-expiry fields, cleanup action, and rebuildability; effective decisions are published only in `policy_decisions.jsonl`. The failure-ledger `INVALIDATION`/`ROLLBACK` event owns a bytewise-sorted closed artifact-ID set and `membership_digest = SHA-256(LF-joined IDs)`, plus actor/authority, trigger, before/after state, quarantine destination, timestamps, errors, and idempotency key. Tombstones are non-searchable and contain no raw payload, pixels, query text, credentials, or unauthorized locator. REFACTOR: isolate artifact store/clock/policy. Check retry equivalence, invalidation graph, rollback replay, retention transitions, tombstone privacy, and source immutability tests.

### T10 — repeat and operational verification

Depends on T09. Implement read-only `repeat` for frozen-index query replay and full-pipeline replay as separate attempts. For every rank-eligible representation, persist required `vector_digest`, canonical float64 vector encoding descriptor, normalization descriptor, and accumulation descriptor in the representation record owned by `run_manifest.json`; failed/zero/non-finite representations have no vector digest and a required status reason. `ranked_candidates.jsonl` carries `representation_id` as the sole join to that representation record; it has no independent digest-reference field and never a vector sidecar. Compare identity-bearing source/window/target mapping, selected PTS/frame, vector hashes/canonical values, candidate identity/order, exact finite scores, failure ledger, and metrics; runtime/host/RSS/timing may differ and missing thermal data is `NOT_OBSERVED`. Any identity mismatch blocks PASS. Add `scripts/verify-gate0.py` and integrate static artifact-count, schema, secret, no-network/provider, prohibited-later-gate, and documentation checks into the workspace verifier without pretending runtime validation.

RED: changed digest or identity mismatch is accepted, or replay succeeds only because of same-process/cache state; GREEN: unchanged synthetic replay passes in fresh independent processes with the declared cache policy and changed fixture/config fails. REFACTOR: verifier reports evidence state explicitly. Check repeatability golden tests, CLI integration, and verifier exit behavior.

### T11 — end-to-end synthetic acceptance and handoff

Depends on T00–T10. Run only checked-in synthetic fixtures and the tiny media-backed smoke fixture. Verify legal CLI order, all 13 artifact outputs, no fourteenth runtime artifact, atomicity, source immutability, no network/provider calls, exact schemas/digests, failure accounting, repeatability, rollback, and final documentation. Produce a bounded implementation receipt; do not process the real archive.

RED: any prohibited side effect or missing evidence blocks execution review. GREEN: all static and synthetic acceptance checks pass with captured commands and artifact digests. REFACTOR: remove redundant tasks/docs while preserving explicit ownership. Final acceptance requires a separate user approval before any production implementation session.

### Required fixture/oracle catalog

The implementation session must create only test-owned fixtures with stable IDs: `cfr_4s`, `vfr_nonunit`, `vfr_negative`, `duplicate_pts`, `missing_pts`, `boundary_end`, and `tie_oracle`. Each fixture records generation/tool version, codec/container or fake-decoder source, exact time base, PTS sequence, duration, duplicate state, expected eight-target schedule, selected PTS/frame or named failure, generation/check-in method, and checksum. The suite must include one tiny media-backed FFmpeg/ffprobe smoke fixture in addition to fake seams. No real-archive media, model weights, vector store, or generated runtime artifact may enter the repository.

## 4. Commands and verification gates

The later implementation session must run tests in narrow task order, then the full Gate-0 suite, then repository checks. Representative commands are:

```bash
python -m pytest tests/gate0 -q                                # after each integrated card
python -m pytest tests/gate0 -q --disable-warnings
python scripts/verify-gate0.py --synthetic-only
bash scripts/verify-workspace.sh
git grep --cached -nE 'AIza|AKIA|github_pat_|sk-|BEGIN .*PRIVATE KEY'
```

The implementation must run with network denied for Gate 0 and test that child processes inherit the boundary. A verifier result is static/synthetic evidence only; real corpus, model feasibility, and runtime performance remain `NOT_OBSERVED` until a separately approved experiment.

The future implementation session must also run the exact bounded matrix below; no real archive is needed for any of it:

```bash
python -m pytest tests/gate0/unit tests/gate0/media tests/gate0/integration -q
python scripts/verify-gate0.py --synthetic-only --deny-network
python scripts/verify-gate0.py --schemas --foreign-keys --artifact-count=13
python scripts/verify-gate0.py --secrets --redaction --prohibited-artifacts --no-provider
```

The following table is the sole authoritative task-to-test ownership matrix. For every row, RED runs before the owning code exists and is expected to fail; GREEN runs after the smallest implementation; the verifier column is the required post-GREEN check. Each test file has one owner; shared contract changes are integrated only by the main implementation owner after focused tests pass.

| Task | Owned tests and oracle | RED → GREEN | Verifier/regression |
|---|---|---|---|
| T00 | `tests/gate0/unit/test_config.py`; config/runtime/lock golden | `python -m pytest tests/gate0/unit/test_config.py -q` → same | `scripts/verify-gate0.py --config --digests` |
| T01 | `tests/gate0/unit/test_identity.py`, `test_canonical_json.py`, `test_schemas.py`; 13-file/unknown-field oracle | `python -m pytest tests/gate0/unit/test_identity.py tests/gate0/unit/test_canonical_json.py tests/gate0/unit/test_schemas.py -q` → same | `scripts/verify-gate0.py --schemas --foreign-keys --artifact-count=13` |
| T02 | `tests/gate0/integration/test_inventory_policy.py`; authorization/probe/selected-stream oracle | `python -m pytest tests/gate0/integration/test_inventory_policy.py -q` → same | `scripts/verify-gate0.py --inventory --source-immutable --selected-stream` |
| T03 | `tests/gate0/unit/test_split_labels.py`; leakage/blinding oracle | `python -m pytest tests/gate0/unit/test_split_labels.py -q` → same | `scripts/verify-gate0.py --split --labels` |
| T04 | `tests/gate0/integration/test_preflight_egress.py`; bwrap-unavailable, child-DNS/proxy, zero-byte oracle | `python -m pytest tests/gate0/integration/test_preflight_egress.py -q` → same | `scripts/verify-gate0.py --deny-network --no-provider --secrets` |
| T05 | `tests/gate0/media/test_pts.py`, `test_windows.py`, `test_sampler.py`, `test_ffprobe_adapter.py`; selected-stream, nonzero-origin, nonunit-timebase, B-frame/equal-PTS, boundary, VFR catalog | `python -m pytest tests/gate0/media -q` → same | `scripts/verify-gate0.py --sampling --target-conservation --selected-stream` |
| T06 | `tests/gate0/unit/test_arms.py`; normalization/zero-vector/no-fallback oracle | `python -m pytest tests/gate0/unit/test_arms.py -q` → same | `scripts/verify-gate0.py --representations --no-provider` |
| T07 | `tests/gate0/unit/test_ranking.py`; bytewise/rational tie and collision oracle | `python -m pytest tests/gate0/unit/test_ranking.py -q` → same | `scripts/verify-gate0.py --ranking --determinism` |
| T08 | `tests/gate0/unit/test_metrics_decision.py`; post-ranking window-judgment, denominator, and precedence oracle | `python -m pytest tests/gate0/unit/test_metrics_decision.py -q` → same | `scripts/verify-gate0.py --metrics --decision-precedence --judgment-owner=T08 --review-input=tests/gate0/fixtures/golden/judgments.json` |
| T09 | `tests/gate0/unit/test_failure_retention.py`, `test_rollback.py`; cleanup-pending/tombstone/attempt-transition/closure oracle | `python -m pytest tests/gate0/unit/test_failure_retention.py tests/gate0/unit/test_rollback.py -q` → same | `scripts/verify-gate0.py --retention --rollback --invalidation --manifest-closure` |
| T10 | `tests/gate0/integration/test_cli_repeatability.py`, `test_verifier.py`; vector-digest/replay/repeat-comparison oracle | `python -m pytest tests/gate0/integration/test_cli_repeatability.py tests/gate0/integration/test_verifier.py -q` → same | `scripts/verify-gate0.py --repeatability --repeat-comparison-closure --synthetic-only` |
| T11 | `tests/gate0/integration/test_synthetic_acceptance.py`; all fixture/artifact/no-side-effect oracle | `python -m pytest tests/gate0/integration/test_synthetic_acceptance.py -q` → same; RED must fail if any artifact count, side-effect, or synthetic projection is absent, GREEN must pass all synthetic projections | `python -m pytest tests/gate0/unit tests/gate0/media tests/gate0/integration -q && python scripts/verify-gate0.py --synthetic-only --deny-network --schemas --foreign-keys --artifact-count=13 --secrets --redaction --prohibited-artifacts --no-provider && bash scripts/verify-workspace.sh` |

The static verifier must check the exact artifact-owner table, the dependency-closure membership digest, tombstone non-searchability, child-process deny-boundary sentinel, `attempted_bytes != transmitted_bytes` semantics when applicable, and the plan’s target-slot aggregation choice. It must not claim that static checks validate FFmpeg behavior, model quality, real-corpus feasibility, or thermal/resource limits.

### Normative implementation-handoff fields

For this planning task, the exact plan fields below are the single-valued downstream handoff. They clarify implementation shape without adding a Gate-0 capability or a fourteenth artifact. Where the older architecture text says 12 result files, v1.1 plus this plan’s authority ruling controls; where a draft field matrix marks an implementation-required field optional, the required handoff field below controls for a valid rank-eligible run. Any implementation approval that rejects these clarifications must first produce a new versioned specification and re-run this planning task.

**Issue #7 authority ruling:** the Section 8 shared boundaries, this Section 9
normative handoff, and the exact 13-schema registry are the sole executable
contract for this plan. The v1.1 Section 9.2 field matrix is preserved as
provenance but is incomplete where its prose and validation obligations require
mapping evidence, representation identity, status, or replay descriptors. The
explicit `sample_target` fields (`window_id`, `interval_id`, `selected_frame_id`,
`mapping_ref`) and the explicit representation descriptor/status fields below
therefore supersede the matrix shorthand for this planning task; they are
required members of the named existing schemas, not open extensions, new
artifacts, or architecture changes. T01's registry and verifier must reject
both omission and alternate field names.

- `run_manifest.json.runtime.python_version`, `.os_release_digest`, `.runtime_executable_digest`, `.dependency_lock_digest`, `.config_digest`, and `.blas_thread_control_digest` are required strings. `requirements/gate0.lock` is canonical UTF-8 LF text; `dependency_lock_digest` is SHA-256 over its exact bytes. `config_digest` is SHA-256 over canonical UTF-8 RFC-8785-style bytes of `config/gate0/default.json`. The lock digest is not folded into the config digest.
- `window_sample_manifest.jsonl` uses one canonical `sample_target` wire row: `target_id` (string), `window_id` (string), `interval_id` (string), `tick` (integer), `target_offset` (`{numerator: int, denominator: int}`), optional `raw_pts` (`{ticks: int, time_base_num: int, time_base_den: int}`), optional `normalized_pts` (`{numerator: int, denominator: int}`), `pts_status`, `coverage_status`, optional `selected_frame_id`, optional `decoder_ordinal`, optional `presentation_order`, optional `duplicate_reason`, and conditional `mapping_ref`. The flat mathematical fields used in the predicate are internal names mapped exactly to these wire fields: `tick`/`target_offset` supplies `target_num/target_den`, `raw_pts` supplies `raw_pts_ticks/time_base_num/time_base_den`, and `normalized_pts` supplies `normalized_pts_num/normalized_pts_den`. `mapping_ref` is required exactly when `normalized_pts` is valid and absent otherwise; absence is never encoded as an empty string or null. Every optional wire field is omitted when unavailable; internal `None`/`ABSENT` sentinels are never serialized. The exact mapping is `normalized_pts_num = (raw_pts_ticks - origin_pts_ticks) * time_base_num`, `normalized_pts_den = time_base_den`, reduced by GCD. For window `i`, define `relative_num = normalized_pts_num - (4*i)*normalized_pts_den` and `relative_den = normalized_pts_den`; selection is the literal pair of predicates `target_num*relative_den <= relative_num*target_den` and `relative_num*1 < 4*relative_den`, after cross-multiplication and without float/pre-rounding. The nonzero-origin oracle covers at least two windows and asserts that the second window still uses the relative end `<4` predicate.
- `run_manifest.json.representations[]` is the canonical representation record. Every rank-eligible record requires `vector_digest`, `vector_digest_algorithm=SHA-256`, `vector_encoding=float64_le_row_major`, `vector_length`, `normalization`, `pooling`, and `accumulation_order`. `vector_digest` hashes the exact little-endian IEEE-754 binary64 bytes of the final normalized vector in row-major element order; no JSON formatting is in its scope. Failed/zero/non-finite records require `representation_status` and `failure_reason` and omit `vector_digest`. `ranked_candidates.jsonl.representation_id` is the sole join; no separate digest-reference field or vector sidecar exists.

The implementation plan, not a generic command example, is the only task-to-test command surface: the matrix below is authoritative, and every task-card `Check` must match its matrix row exactly. In every row, RED is expected to fail because the named behavior/oracle is not implemented; GREEN is accepted only when the named oracle passes: T00 canonical config/lock/runtime fields; T01 13-file/schema/FK/digest validation; T02 authorization and source immutability; T03 split leakage and blinding; T04 bwrap-unavailable, child-DNS/proxy, zero-byte, and secret denial; T05 nonzero-origin/nonunit-timebase/B-frame/equal-PTS/boundary sampling and conservation; T06 vector normalization/zero/no-fallback; T07 total-order ranking/collision; T08 metric denominator/decision precedence; T09 retry/retention/rollback/tombstone closure; T10 CLI/replay/vector digest; T11 complete synthetic no-side-effect acceptance.

## 5. Acceptance, stop, and rollback conditions

Stop immediately and mark the run `GATE0_IMPLEMENTATION_PLAN_NEEDS_WORK`/implementation blocked if a task requires an architecture decision, a cloud/provider dependency, a new persisted artifact, a source mutation, a semantic-to-frame claim, a hidden label input, a relaxed policy, or later-gate capability. Preserve failure artifacts and do not guess.

Execution review is ready only when every task has exact ownership, dependencies, RED/GREEN/REFACTOR checks, schema/fixture paths, provenance/policy obligations, failure/retry/rollback behavior, and a verifier command; all six refinement cycles and fresh red-team review pass; and the explicit implementation approval remains a separate gate.

The following preflight decision table is normative for the later implementation session:

| Condition | Required result |
|---|---|
| Missing effective discovery authorization | no governed read; `BLOCKED_PREREQUISITE`, exit 20 |
| Missing/expired/revoked/mismatched processing policy or retention inputs | no derived artifact; `BLOCKED`/`INVALID_PROTOCOL` as applicable, exit 20/30 |
| Source digest or identity mismatch | dependency closure, quarantine, `INVALID_PROTOCOL`, exit 30 |
| Forbidden network/provider/proxy attempt | one redacted `EGRESS_BLOCKED` event, transmitted bytes 0, no stage success |
| Missing/ambiguous PTS or unaccounted target | named coverage failure; if protocol cannot account, `INVALID_PROTOCOL`, exit 30 |
| Quality/resource failure with complete accounting | valid negative evidence, `FAIL`, exit 10 |
| Missing corpus/model/reviewer/fixture before a valid attempt | `NOT_RUN` with `BLOCKED_PREREQUISITE`, exit 20 |
| Repeatability identity mismatch | repeatability failure; never `PASS` |

## 6. Checkpoint and integration strategy

Use one approved implementation branch with small commits by task card: `gate0: contract`, `gate0: inventory`, `gate0: temporal`, `gate0: arms`, `gate0: ranking`, `gate0: evaluation`, `gate0: failure`, and `gate0: verification`. Before each integration checkpoint run the focused suite and secret/prohibited-artifact scans. Never commit credentials, weights, large media, caches, vectors, or external source. Preserve source and all failure/provenance records. The main agent or designated implementation lead remains the sole integrator for shared contracts.

## 7. Plan-to-spec traceability

T00–T01 cover identity, statuses, exactly 13 artifacts, canonical serialization, and schema annex. T02–T04 cover discovery/processing authorization, inventory, policy, split, labels, blinding, frozen inputs, and zero-egress. T05 covers all temporal/VFR/PTS/2-FPS obligations. T06–T08 cover the two declared arms, ranking, metrics, threshold and decision semantics. T09–T10 cover failure, invalidation, rollback, retention, repeatability, and verifier obligations. T11 covers synthetic acceptance and the explicit no-real-archive boundary. No task authorizes later gates.

## 8. Normalized execution-worker task contract

This section is the single execution-worker handoff addendum. It makes the
existing T00–T11 prose and matrix mechanically actionable without changing
the approved architecture. The repository-local location
`docs/plans/2026-09-12-gate0-implementation.md` is an intentional location
override of the current writing-plans default; no second normative plan exists.

### Shared typed boundaries

The following names are the only cross-task symbols. They are planning
interfaces, not files created by this review:

| Boundary | Canonical path and exact shape |
|---|---|
| Configuration | `src/gate0/config.py`: `load_config(path: Path) -> ConfigDigest`; `ConfigDigest` contains `config: Gate0Config`, `config_digest: str`, `dependency_lock_digest: str`, `python_version: str`. `Gate0Config` has exactly `corpus`, `windows`, `sampling`, `thresholds`, `model`, `runtime`, `policy`, `retention`, `tie_rules`, `sandbox`, and `blinding` objects as declared by `schemas/gate0/config.json`; unknown top-level or nested fields are rejected. |
| Artifact publication | `src/gate0/artifacts.py`: `publish(attempt: AttemptContext, artifact: ArtifactEnvelope, payload: bytes) -> PublishedArtifact`; `PublishedArtifact` contains `artifact_id`, `payload_digest`, `path`, `availability_status`. |
| Stage result | `src/gate0/stages/types.py`: `StageResult[Payload]` contains `stage_status`, `exit_code`, `attempt_id`, `output_artifact_refs`, `failure_refs`, and `payload`. |
| Policy | `src/gate0/policy.py`: `PolicyDecision` contains `policy_decision_id`, `revision_scope`, `purpose`, `allowed_artifact_types`, `retention_class`, `expires_at`, `decision`, `effective_at_use`; `require_allow(context: PolicyUseContext) -> None`, where `PolicyUseContext` is the closed tuple `{revision_id: str, operation: Literal["DISCOVER","HASH","PROBE","PROCESS","CACHE_READ","PROJECTION_READ"], purpose: Literal["DISCOVER","HASH","PROBE","PROCESS","CACHE_READ","PROJECTION_READ"], artifact_type: str, provider_model_boundary: str, retention_class: str, now: str, expected_egress_manifest_digest: str, discovery_decision: PolicyDecision|None, processing_decision: PolicyDecision|None}`. The operation-to-purpose mapping follows the erratum: DISCOVER, HASH, and PROBE map to DISCOVER for T02 discovery; PROCESS, CACHE_READ, and PROJECTION_READ map to themselves. Discovery and processing decisions are separate inputs; the sole checker rejects missing, expired, revoked, purpose-, revision-, artifact-, retention-, provider-, or egress-digest-mismatched decisions and rejects discovery authorization for PROCESS, CACHE_READ, or PROJECTION_READ. |
| Egress | `src/gate0/egress.py`: `EgressGuard.request(context: EgressRequestContext) -> EgressDecision`; `EgressRequestContext` is `{run_id: str, attempt_id: str, policy_decision_id: str, egress_manifest_digest: str, tool_identity: str, destination: str, protocol: str, attempted_bytes: int, now: str}`. `EgressDecision` is `{event_id: str, attempt_id: str, policy_decision_id: str, tool_identity: str, timestamp: str, decision: str, outcome: str, destination: str, protocol: str, attempted_bytes: int, transmitted_bytes: int, payload: None}`; DENY/BLOCKED requires `transmitted_bytes=0` and the event is append-only and joinable to the attempt. |
| Decoder | `src/gate0/adapters/decoder.py`: `DecoderAdapter.iter_frames(source: RevisionRef, stream_index: int) -> Iterator[DecodedFrame]`; `DecodedFrame` contains raw PTS, time base, decoder ordinal, presentation order, source-frame identity, and pixels/status. |
| Embedding | `src/gate0/adapters/embedding.py`: `EmbeddingAdapter.embed(text_or_pixels: EmbeddingInput) -> EmbeddingResult`; `EmbeddingResult` contains finite float64 vector or a named failure/status. |
| Storage/clock | `src/gate0/adapters/runtime.py`: `ArtifactStore.read(ref: ArtifactRef) -> bytes`, `ArtifactStore.write_atomic(ref: ArtifactRef, payload: bytes) -> None`, `Clock.now() -> str`. |
| Repeatability | `src/gate0/repeat.py`: `compare_replay(expected: ReplayProjection, observed: ReplayProjection) -> ReplayComparison`; identity-bearing differences are blocking. |
| CLI | `src/gate0/cli.py` is invoked as `python -m gate0.cli <stage> --run <run_dir> --config config/gate0/default.json --input-root <path> --output-root <path> --run-id <id>`; `scripts/gate0-run.sh` wraps this invocation inside the required bwrap boundary. The CLI rejects any normalized path for which `run_dir != output_root / run_id`; `run_dir` must be the canonical existing `<output-root>/<run-id>/` directory, and the same invariant is asserted by T10 and the launcher acceptance oracle. |

The symbols above have these exact planning shapes and ownership: `AttemptContext`
is `{run_id: str, attempt_id: str, stage: str, input_digest: str,
config_digest: str, policy_decision_id: str|None, output_root: Path}` from
`stages/types.py`; `ArtifactEnvelope` is the Section 9.1 envelope with all
fields required there; and `ArtifactRef` is `{artifact_id: str,
payload_digest: str, artifact_type: str}` from `contracts/types.py`.
`RevisionRef` is `{revision_id: str, content_id: str, locator: str,
selected_stream_index: int, selection_source: Literal["config","unique_probe"]}`
from `contracts/types.py`; the config's nullable stream index is resolved to
this non-null record before the inventory payload is emitted. `DecodedFrame` is
`{raw_pts_ticks: int, time_base_num: int, time_base_den: int,
decoder_ordinal: int, presentation_order: int, selected_frame_id: str,
pixels: bytes|None, status: str}`. `EmbeddingInput` is either
`{kind: "text", text: str}` or `{kind: "pixels", pixels: bytes}`;
`EmbeddingResult` is `{vector: tuple[float, ...]|None, status: str,
failure_reason: str|None}`. `RepresentationRecord` is the exact
plan-authorized named record `{space_id, representation_id, revision_id,
window_id, sampling_manifest_digest, model_identity, processor_digest,
preprocessing_digest, pooling, dimension, dtype, normalization, metric,
vector_digest, vector_digest_algorithm, vector_encoding, vector_length,
accumulation_order, generation_attempt_id, representation_status,
failure_reason}`; rank-eligible rows require all digest/descriptor fields,
failed rows omit `vector_digest` and require status/reason fields. This
field-complete shape is part of the T01 schema and golden; it is not an open
extension or a second competing record shape. `ReplayProjection` is the ordered tuple
of source/window/target mappings, selected frame identities, vector digests or
canonical values, candidate identities/order/scores, failure ledger, and
metrics; `ReplayComparison` is `{equal: bool, first_difference: str|None,
evidence_state: str}`. `InventoryPayload` is the typed collection of source
`{source_records: tuple[OccurrenceRevisionRecord, ...], discovery_records:
tuple[DiscoveryAuthorizationRecord, ...], inventory_digest: str}` produced by
T02. `DiscoveryAuthorizationRecord` has one required scalar
`policy_decision_id` reference only; no `discovery_policy_decision` object is
serialized here. The exact `PolicyDecision` has `purpose=DISCOVER` and is
serialized only in the sole `policy_decisions.jsonl` owner; the authorization
record contains only its scalar `policy_decision_id` reference.
One T02 attempt creates exactly one discovery decision with complete ordered
revision scope; both discovery artifact envelopes and every authorization row
reference the same ID. The discovery schema owns only the authorization row.
T01/T02 validate the cross-file FK before publication.
`schemas/gate0/policy_decisions.json`. The artifact-envelope `policy_decision_id`
is the same scalar ID; every envelope foreign-key resolves to that scalar ID
before publication. T04
consumes only this scalar reference and may create a distinct processing
decision; it never copies or embeds the discovery decision. T01/T02 validate
exact scope, purpose, decision, and allowed artifact types before publication.
Missing, expired, processing-purpose, unlisted, duplicated, or
scope-mismatched references are distinct golden failures. `ReplayProjection` is `{source_revision_ids: tuple[str, ...],
target_rows: tuple[SampleTargetRecord, ...], selected_frame_ids: tuple[str, ...],
representation_digests: tuple[str, ...], candidate_rows: tuple[RankedCandidateRecord, ...],
failure_event_ids: tuple[str, ...], metric_rows: tuple[MetricRecord, ...]}`;
all tuples are canonical ordered and required rows are never silently omitted.
`StageResult[Payload]` may be instantiated only with the exact closed union
`InventoryPayload|SplitLabelPayload|PreflightPayload|SamplePayload|RepresentationPayload|RankingPayload|EvaluationPayload|PreparePayload|ReportPayload|RepeatPayload`.
No other symbol or generic payload is permitted as a cross-task dependency.

`PublishedArtifact` is `{artifact_id: str, payload_digest: str, path: Path,
availability_status: str}` from `artifacts.py`; `StageResult[Payload]` is
`{stage_status: str, exit_code: int, attempt_id: str,
output_artifact_refs: tuple[ArtifactRef, ...], failure_refs: tuple[str, ...],
payload: Payload}` from `stages/types.py`; and `RepresentationRecord` is the
complete Section 9.2 `space/representation` record plus
`representation_status: str` and `failure_reason: str|None` from
`contracts/types.py`. `PolicyDecision` is `{policy_decision_id: str,
revision_scope: tuple[str, ...], purpose: str, sensitivity_consent: str,
allowed_artifact_types: tuple[str, ...], provider_model_boundary: str,
retention_class: str, expires_at: str, revocation_ref: str|None,
egress_manifest_digest: str, decision: str, effective_at_use: bool}`;
all listed policy fields are present in the in-memory and serialized decision,
with `revocation_ref` nullable only where Section 9.2 marks it optional.
`ReplayComparison` is `{equal: bool, first_difference: str|None,
evidence_state: str}` and all other symbols in the boundary table have the
field shapes stated in this paragraph or the immediately preceding table.
`ArtifactEnvelope` is `{artifact_id: str, artifact_type: str,
schema_version: str, digest_algorithm: str, payload_digest: str,
producer_attempt_id: str, input_artifact_refs: tuple[ArtifactRef, ...],
policy_decision_id: str, retention_class: str, availability_status: str,
created_at: str}`. For the two discovery-scope artifacts produced by T02,
the required `policy_decision_id` is the one T02-created discovery
`PolicyDecision` serialized in the sole `policy_decisions.jsonl` owner. Its
purpose is `DISCOVER`, its allowed artifact types are exactly
`source_manifest` and `discovery_authorization`, and its revision scope is the
complete ordered source-manifest revision tuple. Every authorization row and
both envelopes use that same scalar ID. T02 rejects an absent, unknown,
expired, revoked, processing-purpose, duplicated, or differently scoped ID
before publication. T04 carries only the reference and creates a distinct
processing decision when needed; discovery never satisfies PROCESS,
CACHE_READ, or PROJECTION_READ. The
The sole `policy_decisions.jsonl` owner carries the T02 discovery decision and
any distinct T04 processing decisions; T04 appends only its distinct processing
rows and never reserializes discovery decisions. No discovery decision
reference is serialized there; no envelope exception or
sentinel is permitted. `RepresentationRecord` has exactly the Section 9.2
space/representation fields plus the two status fields; failed records omit
`vector_digest`. All listed Python shapes serialize only through the named artifact records and
never create extra runtime files. A static symbol-closure check must fail if a
task card names a cross-task symbol absent from this table or these definitions.

#### Closed control-input and stage-handoff contracts

`schemas/gate0/config.json` is a T00-owned, non-result control schema. It is
validated before any stage starts, is not counted among the 13 published run
artifacts, and is the only permitted shape for `config/gate0/default.json`.
Unknown fields are rejected; arrays are canonical ordered arrays; digests are
lowercase 64-character SHA-256 strings. The complete nested shape is:

| Object | Required fields and types |
|---|---|
| `corpus` | `source_root: str`, `source_manifest_digest: str`, `relation_policy: Literal["component_frozen"]`, `evaluation_query_count: int=24`, `development_query_count: int=8` |
| `windows` | `duration_seconds: int=4`, `half_open: Literal[true]`, `final_window_policy: Literal["omit_incomplete"]`, `selected_stream_policy: Literal["configured_single_video_stream"]`, `selected_stream_index: int|None` |
| `sampling` | `target_fps_num: int=2`, `target_fps_den: int=1`, `target_ticks: tuple[int, ...]=(0,1,2,3,4,5,6,7)`, `origin_policy: Literal["selected_stream_origin"]` |
| `thresholds` | `semantic_hit_at_10_num: int=20`, `semantic_hit_at_10_den: int=24`, `paired_lift_num: int=5`, `paired_lift_den: int=24`, `family_hit_at_10_num: int=3`, `family_hit_at_10_den: int=6` |
| `model` | `semantic_arm_id: str`, `model_identity: str`, `weights_digest: str|None`, `processor_digest: str`, `space_id: str`, `dimension: int`, `dtype: Literal["float64"]`, `offline_only: Literal[true]`, `provider_model_boundary: Literal["local_only"]` |
| `runtime` | `python_path: str`, `python_version: Literal["3.11.9"]`, `dependency_lock_path: str`, `ffmpeg_path: str`, `ffprobe_path: str`, `blas_thread_count: int`, `cache_policy: Literal["cleared_between_replays"]` |
| `policy` | `reviewer_ids: tuple[str, ...]`, `policy_authority: str`, `local_only: Literal[true]`, `egress_manifest_digest: str`, `permitted_artifact_types: tuple[str, ...]`, `provider_model_boundary: Literal["local_only"]`, `revalidation: Literal["every_stage_boundary_and_cache_read"]` |
| `retention` | exactly the five keys `SOURCE_REFERENCE`, `DERIVED_REPLAYABLE`, `DERIVED_RESTRICTED`, `AUDIT_MINIMUM`, `TOMBSTONE`; each value is `{owner: str, authority: str, start_event: str, expiry_event: str, time_zone: str, permitted_readers: tuple[str, ...], post_expiry_fields: tuple[str, ...], cleanup_action: str, rebuildability: Literal["rebuildable","not_rebuildable"]}` |
| `tie_rules` | `score_order: Literal["descending"]`, `candidate_key: tuple[str, ...]`, `window_start_key: Literal["reduced_rational"]`, `numeric_identity: Literal["float64_row_major"]` |
| `sandbox` | `bwrap_path: str`, `bwrap_version: str`, `bwrap_digest: str`, `interpreter_path: str`, `interpreter_version: Literal["3.11.9"]`, `interpreter_digest: str`, `read_only_mounts: tuple[str, ...]`, `writable_mounts: tuple[str, ...]`, `clearenv: Literal[true]`, `net_unshared: Literal[true]`, `child_network_sentinel: Literal[true]` |
| `blinding` | `mapping_version: str`, `blind_mapping_digest: str`, `reviewer_count: int=2`, `reviewer_visible_fields: tuple[str, ...]`, `reviewer_hidden_fields: tuple[str, ...]`, `token_map: tuple[{blind_arm_token: str, arm_id: str}, ...]` |

The schema enforces `len(target_ticks)=8`, the frozen population and
threshold denominators above, all five retention keys, local-only/offline
model policy, the sandbox attestation invariants, and a two-entry blinded
arm-token map whose digest is the SHA-256 of its canonical ordered JSON bytes.
T00 owns this schema,
the config golden, its validator, and the `--config --digests` check; T01
imports the validated `ConfigDigest` and does not redefine the config shape.
When `windows.selected_stream_index` is non-null, T02 must verify that it
belongs to the pinned probe's eligible video-stream set and persist that
resolved index in `RevisionRef`; when it is null, T02 selects the only
eligible video stream when the set cardinality is exactly one and fails with
`AMBIGUOUS_STREAM` for zero or multiple eligible streams. The config value is
input-only and may be null; `RevisionRef.selected_stream_index` is always a
resolved `int`, with `selection_source: Literal["config","unique_probe"]`.
No stage may infer or change the selection after T02.

`StageResult[Payload]` is a closed union, not an open generic. Its permitted
payloads are `InventoryPayload{source_records: tuple[OccurrenceRevisionRecord,
...], discovery_records: tuple[DiscoveryAuthorizationRecord, ...],
inventory_digest: str}`, `SplitLabelPayload{split_manifest: SplitManifestRecord,
query_records: tuple[QueryRecord, ...], gold_records: tuple[GoldEventRecord,
...], label_version_digest: str}`,
`PreflightPayload{policy_decisions: tuple[PolicyDecision, ...],
egress_events: tuple[EgressDecision, ...], sandbox_attestation:
SandboxAttestation, preflight_status: str}`, `SamplePayload{target_rows:
tuple[SampleTargetRecord, ...], sample_manifest_digest: str, coverage_status:
str}`, `RepresentationPayload{representation_records:
tuple[RepresentationRecord, ...], representation_digests: tuple[str, ...]}`,
`RankingPayload{candidate_rows: tuple[RankedCandidateRecord, ...],
ranking_status: str}`, `EvaluationPayload{metric_rows: tuple[MetricRecord, ...],
decision_status: str}`, `PreparePayload{run_id: str, initialized: Literal[true]}`,
`ReportPayload{metric_rows_digest: str, gate_decision_status: str}`, and
`RepeatPayload{mode: Literal["frozen-index","full-pipeline"], frozen_input_digest: str,
replay_projection: ReplayProjection,
replay_comparison: ReplayComparison}`. `run_manifest.json` is the canonical
owner of the append-only `repeat_comparisons` tuple. Each
`RepeatComparisonRecord` is `{comparison_id: str, attempt_id: str, mode: str,
expected_input_digest: str, observed_input_digest: str, equal: bool,
first_difference: str|None, evidence_state: str, source_revision_ids:
tuple[str, ...], metrics_digest: str, created_at: str}`. T10 appends exactly
one record per repeat attempt after comparison and never creates a sidecar.
Each named record mirrors one owning
artifact schema field-for-field with no alternate aliases or implicit omission
rules; the closure check validates field shapes, generic instantiations, and
schema ownership.

The Python aliases used by those payloads are exact Section 9.2 record
aliases, not implementation-defined subsets: `OccurrenceRevisionRecord` maps
to `occurrence_revision`; `DiscoveryAuthorizationRecord` to
`discovery_authorization` with required `policy_decision_id` and embedded
no `discovery_policy_decision` object; the sole `PolicyDecision` record is
owned by `schemas/gate0/policy_decisions.json`;
`SplitManifestRecord` to `split_manifest`;
`QueryRecord` to `query`; `GoldEventRecord` to `gold_event`;
`SampleTargetRecord` to `sample_target` (serialized as rows in
`window_sample_manifest.jsonl`); `RankedCandidateRecord` to
`ranked_candidate`; `MetricRecord` to `metric`; and `WindowJudgmentRecord` to
`window_judgment`. Each alias has exactly the owning schema's field names,
types, required/optional/null rules, enum values, and canonical order. The
alias-to-schema table is part of T01's field-level closure check; Python-only
fields and silent omission are forbidden.

The canonical `sample_target` row is `{target_id: str, window_id: str,
interval_id: str, tick: int,
target_offset: {numerator: int, denominator: int}, raw_pts:
{ticks: int, time_base_num: int, time_base_den: int}|ABSENT,
normalized_pts: {numerator: int, denominator: int}|ABSENT, pts_status: str,
coverage_status: str, selected_frame_id: str|None, decoder_ordinal: int|None,
presentation_order: int|None, duplicate_reason: str|None, mapping_ref:
str|ABSENT}`. `mapping_ref` is required whenever `normalized_pts` is present.
The plan's flat mathematical names are internal aliases only:
`tick`/`target_offset` supplies `target_num/target_den`, `raw_pts` supplies
`raw_pts_ticks/time_base_num/time_base_den`, and `normalized_pts` supplies
`normalized_pts_num/normalized_pts_den`; they are not serialized fields. The
wire schema uses the literal absence rule `mapping_ref=ABSENT` iff
`normalized_pts=ABSENT`; no empty string or null substitute is accepted. The
alias table rejects an artifact filename or a Python-only record name that is
not one of the normative record types.

`run_manifest.json` has the exact top-level shape `{schema_version: str,
run_id: str, gate_owner_id: str, source_revision_ids: tuple[str, ...], config_digest: str,
dependency_lock_digest: str, policy_decision_ids: tuple[str, ...],
thresholds: Thresholds, runtime: RuntimeIdentity, sandbox:
SandboxAttestation, invocations: tuple[InvocationRecord, ...],
blinding: BlindingBinding,
stage_transitions: tuple[StageTransitionRecord, ...], attempts:
tuple[AttemptRecord, ...], artifact_envelopes: tuple[ArtifactEnvelope, ...],
representations: tuple[RepresentationRecord, ...], repeat_comparisons:
tuple[RepeatComparisonRecord, ...], status: str,
stop_reason: str|None}`. These closed records are serialized only by the
`run_manifest.json` schema; `BlindingBinding` is
`{mapping_version: str, blind_mapping_digest: str, token_map:
tuple[{blind_arm_token: str, arm_id: str}, ...], reviewer_count: int,
reviewer_visible_fields: tuple[str, ...], reviewer_hidden_fields:
tuple[str, ...], access_scope: Literal["T08_only"]}`. The token map is
created before reviewer input is accepted, is never exposed in the
reviewer-input file or reviewer-visible projection, and is read only by T08
after policy authorization. `blind_mapping_digest` is the SHA-256 of
canonical UTF-8 JSON bytes for the exact object
`{mapping_version, config_digest, token_map}` (in that key order, with the
token map ordered by `blind_arm_token`). T00 computes and stores that value in
`config/gate0/default.json.blinding`; prepare copies the same object and digest
into `run_manifest.json.blinding` without changing it; and T08 requires both
run-manifest equality and envelope equality before accepting review input. A
config-digest, mapping-version, token-order, or envelope mismatch is a named
T00/T08 failure and cannot be repaired by deriving new tokens.
The canonical stage controller
`src/gate0/stages/lifecycle.py:advance_stage(attempt: AttemptContext,
expected_predecessor: str, next_status: str) -> StageTransitionRecord` owns
transition emission and is called by the CLI once for `prepare` and once for
each legal stage; T09 owns its implementation and lifecycle records, and T10 owns
replay reads. Required rows remain present with explicit status on failure.

The run-manifest record shapes are closed here: `Thresholds` is
`{semantic_hit_at_10_num: int, semantic_hit_at_10_den: int,
paired_lift_num: int, paired_lift_den: int, family_hit_at_10_num: int,
family_hit_at_10_den: int}`; `RuntimeIdentity` is `{python_version: str,
os_release_digest: str, runtime_executable_digest: str,
dependency_lock_digest: str, config_digest: str,
blas_thread_control_digest: str, tool_environment_digest: str}`; the closed
`tool_environment_digest` is SHA-256 over canonical records for resolved
FFmpeg and ffprobe paths, version bytes, executable digests, and any other
decoder/probe runtime inputs named by T09. `InvocationRecord` is
`{invocation_id: str, attempt_id: str, requested_model: str|None,
resolved_model: str|None, processor_digest: str|None, runtime_digest: str,
provider_status: str, output_ref: ArtifactRef|None}`; `AttemptRecord` is
`{attempt_id: str, run_id: str, stage: str, idempotency_key: str,
input_digest: str, config_digest: str, policy_decision_id: str|None,
started_at: str, ended_at: str|None, exit_code: int, stage_status: str,
output_artifact_refs: tuple[ArtifactRef, ...], retry_of: str|None,
failure_refs: tuple[str, ...], tool_environment_digest: str}`; and
`StageTransitionRecord` is
`{transition_id: str, run_id: str, attempt_id: str, stage: str,
from_status: str, to_status: str, input_digest: str, config_digest: str,
policy_decision_id: str|None, event_time: str,
failure_event_ids: tuple[str, ...]}`. `SandboxAttestation` is the exact
config-bound object with `bwrap_path`, `bwrap_version`, `bwrap_digest`,
`interpreter_path`, `interpreter_version`, `interpreter_digest`,
`read_only_mounts`, `writable_mounts`, `clearenv`, `net_unshared`,
`argv_digest`, `mount_policy_digest`, and `child_network_sentinel` fields.
The legal stage predecessor table is the declared CLI order:
`prepare→inventory→split→label→preflight→extract→embed→rank→evaluate→report`;
`repeat` is read-only from a reported run. For every stage, the lifecycle
controller emits `PLANNED→RUNNING`, then exactly one terminal transition
`RUNNING→SUCCEEDED|PARTIAL|FAILED|BLOCKED|CANCELLED`; the terminal value is
the normative `stage_status`. `FAILED` maps to exit 10 for quality/resource
failure, exit 30 for invalid protocol, and exit 40 for operational failure;
`BLOCKED` maps to exit 20, and `PARTIAL` maps to exit 40. An interrupted stage
closes as `PARTIAL` with its failure reference and resumes only as a new
attempt from the last committed successful predecessor; an unchanged
transient retry uses `retry_of` and the same idempotency inputs. A changed
input/config/policy starts a new run. Repeating a same-terminal-digest run
returns the prior output without appending a duplicate transition. No stage
writes transitions directly or skips a predecessor. The `idempotency_key` is
exactly `run_id+stage+input_digest+config_digest+tool_environment_digest` using
the canonical joined-byte encoding defined by T09. A changed FFmpeg/ffprobe or
declared decoder/probe environment never qualifies as an unchanged retry; the
T09/T10 golden includes an otherwise unchanged retry with a changed tool digest
and expects new-attempt/new-run handling or repeatability failure. A changed
source/target mapping, representation/ranking identity, configuration, or
tool identity is an illegal repeat binding and exits 20 without starting a new
run. `repeat` has
the exact CLI form `python -m gate0.cli repeat --run <reported-run-dir> --config config/gate0/default.json --input-root <input-root> --output-root <output-root> --run-id <id> --mode frozen-index|full-pipeline --predecessor-run-id <id> --frozen-input-digest <64-hex-digest>`. These three options are required exactly once; `--review-input`, stage-selection, label, gold, and output-file options are forbidden. Missing/malformed options are exit 40; illegal mode, predecessor, run-directory, or digest binding is exit 20. The predecessor must be the reported run named by `--run`, `run_dir` must equal `output_root/run_id`, and the digest must match the canonical manifest.
one explicit lifecycle rule: both
`--mode frozen-index` and `--mode full-pipeline` create one new immutable
`AttemptRecord` with `stage=repeat`, predecessor `REPORTED`, and
`output_artifact_refs=()`, then emit
`PLANNED→RUNNING→SUCCEEDED|PARTIAL|FAILED` using the same terminal/exit
mapping. Frozen-index mode reads the existing representations/rankings/metrics;
full-pipeline mode recomputes the pipeline in memory under the same frozen
inputs. Neither mode rewrites source, config, prior published artifacts, or
primary result rows; both append only the new repeat attempt, transition,
comparison, and failure references to the existing run manifest/failure
ledger. The idempotency key is
`run_id+repeat+mode+frozen_input_digest+config_digest+tool_environment_digest`.
For repeat, the
`AttemptRecord.input_digest` is exactly `frozen_input_digest`, defined as the
SHA-256 of canonical UTF-8 JSON bytes for the ordered object
`{mode, source_revision_ids, sample_manifest_digest, representation_digests,
ranking_digest, metrics_digest, config_digest}`. The source/window/target
mapping and all prior rank/metric identities are therefore in scope; no
filesystem traversal, timestamps, host data, or mutable cache is in scope. A
same-terminal-digest
repeat returns the prior replay comparison without appending a duplicate
attempt or transition. In this precise sense `repeat` is read-only: the
immutable source/run inputs and prior result artifacts are not mutated, while
the append-only operational attempt and `RepeatComparisonRecord` receipts
remain auditable.
These records use the status namespaces and digest/FK rules of the named
schemas; each array is canonically ordered, and T01's field-level closure
check rejects undeclared fields or alternate nesting.

T04's launcher is literal and uses the supported host runtime
`/usr/bin/python3.11` (the file must report Python 3.11.9 during preflight):
`/usr/bin/bwrap --die-with-parent --unshare-net --clearenv --ro-bind
"$REPO_ROOT" "$REPO_ROOT" --ro-bind "$INPUT_ROOT"
"$INPUT_ROOT" --bind "$OUTPUT_ROOT" "$OUTPUT_ROOT" --dev /dev --proc /proc
--ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64
--ro-bind /etc/ld.so.cache /etc/ld.so.cache --chdir "$REPO_ROOT"
--setenv PATH /usr/bin:/bin --setenv PYTHONNOUSERSITE 1 --
/usr/bin/python3.11 -m gate0.cli <stage> --run "$RUN_DIR" --config
config/gate0/default.json --input-root "$INPUT_ROOT" --output-root
"$OUTPUT_ROOT" --run-id "$RUN_ID"`. `REPO_ROOT` and `INPUT_ROOT` are
read-only mounts; only `OUTPUT_ROOT` is writable. No home directory, socket,
proxy, DNS configuration, or inherited environment is mounted. The launcher
records the resolved bwrap path, `bwrap --version` bytes digest, resolved
interpreter path and SHA-256, Python version, read-only runtime mount list,
argv digest, mount-policy digest, and child-boundary attestation in
`run_manifest.json`. If any listed runtime path, `/usr/bin/python3.11`, or
the attestation is unavailable/mismatched, it emits one redacted control event
and exits 20; there is no fallback. The T04 launcher test asserts the exact
runtime path and mount list as well as the child DNS/proxy denial sentinel.
The T04 sentinel starts a child that attempts DNS and HTTP proxy resolution and
asserts both denial plus `transmitted_bytes=0`; T10 verifies the same sentinel
under replay.

The authoritative expected-value source for the launcher attestation is the
validated `sandbox` object in `config/gate0/default.json`, whose required
fields are `bwrap_path`, `bwrap_version`, `bwrap_digest`, `interpreter_path`,
`interpreter_version`, `interpreter_digest`, `read_only_mounts`,
`writable_mounts`, `clearenv`, and `net_unshared`. The attestation object is
canonical JSON with those fields plus `argv_digest`, `mount_policy_digest`, and
`child_network_sentinel`. Preflight computes observed values and accepts only
exact equality with the config values, `clearenv=true`, `net_unshared=true`,
and `child_network_sentinel=true`; any missing, non-canonical, or unequal value
emits `SANDBOX_ATTESTATION` and exits 20. The config and lock digests bind the
expected values to the run. The T04 golden covers valid, missing, and
mismatched cases; the 13 artifact schemas are the sole serialization authority
for all cross-task records, and Python interfaces must round-trip to them
without adding fields.

T08 metric IDs and formulas are fixed: `hit_at_10.metadata` and
`hit_at_10.semantic` have population `evaluation_positive_24`, numerator
`sum(hit_q)` over the 24 frozen positive query IDs, denominator `24`, and
`calculation_version=hit_at_10.v1`; `paired_lift.semantic_minus_metadata`
has population `evaluation_positive_24`, numerator
`sum(hit_semantic_q - hit_metadata_q)` over the same candidate universe and
queries, denominator `24`, and `calculation_version=paired_lift.v1`;
`family_hit_at_10.<arm>.<family_id>` uses the frozen six-query family
population, its exact manifest cardinality as denominator, and the same binary
hit indicator; `absent_query_diagnostic.<arm>` has population
`evaluation_absent_8`, numerator/count fields defined as diagnostic-only, and
does not affect the primary denominator. Empty/failed rankings remain explicit
status rows, but each affected positive query contributes `hit_q=0` to the
fixed 24-query primary denominator; a positive query with no grade-2 gold event
remains a separate non-ranking condition. Unaccounted coverage, identity/policy
errors, and repeatability failures retain invalid-protocol precedence. The T08
golden asserts the failed-ranking row, zero numerator contribution, denominator
24, and resulting valid-negative decision. `gate_decision.md`
reads only the two primary metrics, paired lift, and each frozen family metric:
PASS requires semantic `>=20/24`, paired lift `>=5/24`, and every positive
family `>=3/6`; otherwise a complete valid run is `FAIL`. Invalid protocol,
blocked prerequisite, and repeatability failure take the precedence already
defined in Section 5. Each metric ID, population ID, numerator, denominator,
arm, and status is asserted by the T08 golden oracle.

### Exact schema, fixture, and run-layout map

`schemas/gate0/registry.json` is the only schema registry. Its 13 entries map
one-to-one to `source_manifest.json`, `discovery_authorizations.jsonl`,
`policy_decisions.jsonl`, `split_manifest.json`, `queries.jsonl`,
`gold_events.jsonl`, `window_judgments.jsonl`, `window_sample_manifest.jsonl`,
`run_manifest.json`, `ranked_candidates.jsonl`,
`runtime_and_failure_ledger.json`, `metrics.json`, and `gate_decision.md`.
Each entry points to one exact file in `schemas/gate0/`: `source_manifest.json`,
`discovery_authorizations.json`, `policy_decisions.json`, `split_manifest.json`,
`queries.json`, `gold_events.json`, `window_judgments.json`,
`window_sample_manifest.json`, `run_manifest.json`, `ranked_candidates.json`,
`runtime_and_failure_ledger.json`, `metrics.json`, and `gate_decision.md`.
Cross-file joins, cardinalities, digest scopes, and status namespaces are
custom checks in `src/gate0/contracts/validator.py` and are invoked by
`scripts/verify-gate0.py`; JSON Schema alone is not treated as sufficient.
`schemas/gate0/config.json` is the separate T00-owned control-input schema
defined above; it is not a registry entry and never counts as a runtime result
artifact. No `tests/gate0/oracles/` directory or other oracle root is allowed.

The run layout is `<output-root>/<run-id>/` containing only the 13 result files
listed above after atomic publication. Temporary files live under an ignored
`<run-id>/.tmp/` during a stage and must be removed before success. Stage
attempts and control events are records in the declared files, not extra
runtime files. The CLI stage order is exactly `prepare inventory split label
preflight extract embed rank evaluate report`; `repeat` is a read-only command
against the frozen run.

The checked-in test-only map is exact: `tests/gate0/fixtures/catalog.json`,
`tests/gate0/fixtures/README.md`,
`tests/gate0/fixtures/golden/{config,schemas,inventory,labels,judgments,temporal,arms,ranking,metrics,lifecycle,policy,replay}.json`,
`tests/gate0/fixtures/fakes/{decoder,embedding,filesystem,policy,egress,clock}.py`,
and `tests/gate0/fixtures/media/gate0-smoke.mp4`. Golden values are authored
from the specification and checked-in inputs, never generated by the function
under test. `boundary_end` is the plan's explicit additional endpoint oracle;
the verifier expects the six v1.1 fixture IDs plus this seventh test-only case.

### T00 — approved workspace and configuration contract

**Files:** Create `src/gate0/config.py`, `config/gate0/default.json`,
`schemas/gate0/config.json`, `requirements/gate0.lock`, and the minimal
`scripts/verify-gate0.py` bootstrap; test
`tests/gate0/unit/test_config.py`; fixture
`tests/gate0/fixtures/golden/config.json`.

**Interfaces:** Consumes the approved config path and lock bytes; validates the
T00-owned `schemas/gate0/config.json`; produces `ConfigDigest` for T01/T04/T10
and the verifier bootstrap for `--config --digests`
and exit 30 for malformed, unknown-field, invariant, or mismatched input.

- [ ] Write the failing config/lock/runtime golden tests, including unknown nested fields, requiredness, enum/invariant, and `schemas/gate0/config.json` round-trip cases, and run `python -m pytest tests/gate0/unit/test_config.py -q`; expected RED is missing loader/digest behavior or an assertion failure naming the absent digest.
- [ ] Implement only `load_config`, the immutable config/lock digest shape, and the minimal verifier bootstrap for `--config --digests` in the listed files; later tasks extend this same verifier path and no other task creates a second verifier.
- [ ] Run the same command; expected GREEN is the named valid/invalid cases passing with exit-30 assertions.
- [ ] Run `python scripts/verify-gate0.py --config --digests`; expected result is a passing static config/digest check, with runtime feasibility still `NOT_OBSERVED`.
- [ ] Commit only the T00 paths with `git commit -m "gate0: define configuration contract"`.

### T01 — canonical IDs, JSON/JSONL, envelopes, and schemas

**Files:** Create `src/gate0/identity.py`, `src/gate0/canonical_json.py`,
`src/gate0/contracts/{types,validator}.py`, `schemas/gate0/registry.json` and
the 13 schema files named above; tests `tests/gate0/unit/{test_identity,test_canonical_json,test_schemas}.py` and golden `schemas.json`.

**Interfaces:** Consumes `ConfigDigest`; extends the T00-owned
`scripts/verify-gate0.py` bootstrap with `--schemas --foreign-keys
--artifact-count=13`; produces `ArtifactEnvelope`, opaque ID/digest helpers,
and validator results consumed by every later task.

- [ ] Write valid and negative fixtures for every artifact/record type, including unknown fields, enum/status, FK, digest-scope, and 13-file-count cases; run the T01 pytest command from the matrix and expect RED.
- [ ] Implement canonical serialization, ID validation, envelope creation, registry loading, and cross-artifact validation in the listed paths.
- [ ] Rerun the exact T01 pytest command; expected GREEN is byte-identical valid round trips and stable error-path failures.
- [ ] Run `python scripts/verify-gate0.py --schemas --foreign-keys --artifact-count=13`; expected result is PASS for static checks only.
- [ ] Commit with `git commit -m "gate0: define artifact contracts"`.

### T02 — source inventory and authorization

**Files:** Create `src/gate0/inventory.py`, `src/gate0/policy.py`,
`src/gate0/stages/prepare.py`, `src/gate0/stages/inventory.py`; test
`tests/gate0/integration/test_inventory_policy.py`; golden `inventory.json`.

**Interfaces:** Consumes `ArtifactStore`, `Clock`, local input root, and
discovery authorization; `prepare` produces only
`StageResult[PreparePayload]` with `output_artifact_refs=()` and
`initialized=true`; `inventory` produces `source_manifest.json`,
`discovery_authorizations.jsonl`, and a `StageResult[InventoryPayload]`; its
atomic publication set includes the new discovery row in the sole
`policy_decisions.jsonl` owner before either discovery-scope artifact is
published. T02
also creates exactly one discovery-scope `PolicyDecision` in the sole
`policy_decisions.jsonl` owner, with revision scope equal to the complete
ordered source-manifest revision tuple. Every discovery row and both artifact
envelopes reference that same ID; T04 receives only the reference and creates a
distinct processing decision. The T02 oracle covers single- and multi-revision
cardinality plus absent, expired, revoked, processing-purpose, unlisted,
duplicate, and scope-mismatch cases before publication.

- [ ] Write authorization/probe/source-immutability tests and run the T02 matrix command; expected RED is missing stage/result behavior.
- [ ] Implement prepare as run/attempt initialization only and inventory as the sole producer of source/discovery records.
- [ ] Rerun the exact T02 command; expected GREEN includes missing/expired authorization denial and deterministic synthetic inventory.
- [ ] Run `python scripts/verify-gate0.py --inventory --source-immutable --selected-stream`; expected result is PASS for static/synthetic evidence.
- [ ] Commit with `git commit -m "gate0: add authorized inventory stage"`.

### T03 — relation freeze, split, query, and label protocol

**Files:** Create `src/gate0/split.py`, `src/gate0/labels.py`; test
`tests/gate0/unit/test_split_labels.py`; golden `labels.json`.

**Interfaces:** Consumes `source_manifest.json`; produces frozen split/query/
gold records with exact 32 evaluation plus 8 development cardinality, version
digests, and no ranking-readable labels. It does not produce
`window_judgments.jsonl`; those blinded post-ranking records are owned by T08.

- [ ] Write leakage, cardinality, blinding, and label-version tests and run the T03 command; expected RED is missing protocol guards.
- [ ] Implement the frozen relation-component split, typed query/gold joins, and the pre-ranking label boundary; do not create judgment records before ranking.
- [ ] Rerun the exact T03 command; expected GREEN proves counts, family membership, and leakage rejection.
- [ ] Run `python scripts/verify-gate0.py --split --labels`; expected result is PASS for static/synthetic checks.
- [ ] Commit with `git commit -m "gate0: freeze splits and labels"`.

### T04 — preflight and policy/egress boundary

**Files:** Create `src/gate0/egress.py`, `src/gate0/stages/preflight.py`, and
`scripts/gate0-run.sh`; test `tests/gate0/integration/test_preflight_egress.py`;
test-only golden `tests/gate0/fixtures/golden/policy.json`.

**Interfaces:** Consumes discovery authorization plus revision-bound
`PolicyDecision`; produces effective policy decisions and `EgressDecision`
events. It calls the sole `require_allow(PolicyUseContext)` checker for every
stage-boundary, cache-read, and projection-read use; discovery authorization
alone never permits processing/cache reads. Every DNS, proxy, provider, and
loopback attempt passes an `EgressRequestContext` and publishes a joinable
timestamped outcome receipt with the attempt/tool/policy references and
`payload=None`; DENY/BLOCKED always records zero transmitted bytes.

- [ ] Write two-authorization, bwrap-unavailable, child-DNS/proxy, zero-byte, secret-surface, and prohibited-artifact tests; run the T04 command and expect RED.
- [ ] Implement fail-closed preflight and the required bwrap launcher/egress seam.
- [ ] Rerun the exact T04 command; expected GREEN is synthetic authorized preflight and denial for every named forbidden case.
- [ ] Run `python scripts/verify-gate0.py --deny-network --no-provider --secrets`; expected result is PASS for static/synthetic checks.
- [ ] Commit with `git commit -m "gate0: enforce preflight and zero-egress boundary"`.

### T05 — temporal windows and 2-FPS/VFR-safe sampling

**Files:** Create `src/gate0/temporal.py`, `src/gate0/adapters/decoder.py`,
`src/gate0/stages/extract.py`; tests
`tests/gate0/media/{test_pts,test_windows,test_sampler,test_ffprobe_adapter}.py`;
goldens `temporal.json` and `tests/gate0/fixtures/catalog.json`.

**Interfaces:** Consumes `DecoderAdapter` and the immutable `RevisionRef` stream
selection from T02; produces one
sample-target row per planned tick with exact rational mapping and terminal
coverage status. Equal PTS is accepted under decoder-ordinal then bytewise
source-frame identity; only missing/invalid tie evidence is ambiguous.

- [ ] Write the exact seven-entry catalog assertion (`cfr_4s`, `vfr_nonunit`, `vfr_negative`, `duplicate_pts`, `missing_pts`, `tie_oracle`, `boundary_end`) plus CFR/VFR/non-unit-timebase/nonzero-origin/B-frame/equal-PTS/missing-tie and repeated-slot pooling tests; run `python -m pytest tests/gate0/media -q` and expect RED.
- [ ] Implement integer cross-multiplication selection, presentation-order authority, ascending target-tick pooling order, and target conservation.
- [ ] Rerun the exact media command; expected GREEN includes exact equal-PTS selection and explicit missing-tie failure.
- [ ] Run `python scripts/verify-gate0.py --sampling --target-conservation --selected-stream`; expected result is PASS for synthetic/static checks.
- [ ] Commit with `git commit -m "gate0: define rational temporal sampling"`.

### T06 — metadata floor and offline semantic representation

**Files:** Create `src/gate0/arms/{metadata,semantic}.py`,
`src/gate0/adapters/embedding.py`, `src/gate0/stages/embed.py`; test
`tests/gate0/unit/test_arms.py`; golden `arms.json`.

**Interfaces:** Consumes sample-target rows and `EmbeddingAdapter`; produces
`RepresentationRecord` with target-tick-ordered serial pooling, float64 vector
digest metadata, or an explicit non-rankable status.

- [ ] Write normalization, zero/non-finite, tokenization, no-fallback, and pooling-order tests; run the T06 command and expect RED.
- [ ] Implement the metadata floor and one offline semantic arm with the declared fake seam.
- [ ] Rerun the exact T06 command; expected GREEN includes vector/status goldens and no provider endpoint.
- [ ] Run `python scripts/verify-gate0.py --representations --no-provider`; expected result is PASS for static/synthetic checks.
- [ ] Commit with `git commit -m "gate0: add local representation arms"`.

### T07 — deterministic ranking

**Files:** Create `src/gate0/ranking.py`, `src/gate0/stages/rank.py`; test
`tests/gate0/unit/test_ranking.py`; golden `ranking.json`.

**Interfaces:** Consumes `RepresentationRecord` and query records but never
gold/judgment records; produces ranked candidates using the frozen score/tie
tuple and `representation_id` as the sole representation join.

- [ ] Write tie, collision, NaN/inf, normalization, no-gold-input, and fixed-order numeric tests; run the T07 command and expect RED.
- [ ] Implement exact local cosine and total ordering with reduced rational window-start keys.
- [ ] Rerun the exact T07 command; expected GREEN is byte-identical candidate ordering across the oracle runs.
- [ ] Run `python scripts/verify-gate0.py --ranking --determinism`; expected result is PASS for static/synthetic checks.
- [ ] Commit with `git commit -m "gate0: make ranking deterministic"`.

### T08 — evaluation, report, and decision precedence

**Files:** Create `src/gate0/evaluation.py`, `src/gate0/stages/{evaluate,report}.py`,
and the T08-owned post-ranking `window_judgments.jsonl` projection; test
`tests/gate0/unit/test_metrics_decision.py`; goldens `judgments.json` and
`metrics.json`.

**Interfaces:** Consumes ranked candidates and one policy-authorized local
reviewer-input file passed only to `evaluate` as
`--review-input tests/gate0/fixtures/golden/judgments.json`. The authorized
review-input root is `config/gate0/default.json.review_input.authorized_root`,
copied and digest-bound in `run_manifest.json`; structural/path/digest errors
exit 30, while a valid path denied by policy exits 20. The exact stage
invocation is `python -m gate0.cli evaluate --run <run-dir> --config
config/gate0/default.json --input-root <input-root> --output-root <output-root>
--run-id <id> --review-input <path>`. `--review-input` is required exactly
once and must be an existing regular local file beneath that authorized root;
missing, repeated, outside-root, unreadable, wrong-digest,
extra-option, gold/label, or output-root paths are exit 30 and policy denial is
exit 20. The file is a
test-owned `ReviewerInputEnvelope{schema_version: str, input_digest: str,
blind_mapping_digest: str, rows: tuple[ReviewerJudgmentInput, ...]}`. The
envelope digest is SHA-256 over canonical ordered JSON bytes of the envelope
without its digest fields. Rows are
`ReviewerJudgmentInput{assertion_id, query_id, window_id, blind_arm_token,
reviewer_id, grade, ambiguity, review_status, adjudication_ref,
assertion: {version: str, text: str, digest: str}}`;
`blind_arm_token` is an opaque pre-review token and its token-to-arm mapping is
the exact two-entry `run_manifest.json.blinding.token_map`, sealed before
review input and unavailable to reviewer input. The
reviewer-visible projection is exactly `{assertion_id, query_id, window_id,
blind_arm_token, assertion}` and contains no rank, score, provider, model, or
undeclared metadata. T08 requires exactly two distinct authorized reviewers per
`(query_id, window_id, blind_arm_token)`, rejects duplicate keys, requires
grade/adjudication consistency, verifies the envelope and mapping digests, and
joins only on the typed query/window/token key. It then is the sole producer
of the post-ranking `window_judgments.jsonl` records and metric records with
explicit numerator/denominator/population IDs. `evaluate` returns
`StageResult[EvaluationPayload]`; `report` is a terminal projection stage
returning `StageResult[ReportPayload]` with
`output_artifact_refs=(metrics.json, gate_decision.md)` and no new logical
record type. It writes only the declared `gate_decision.md` artifact under the
declared precedence. T08 owns `metrics.json`; the `report` substage is the sole
publisher of `gate_decision.md` and is not a new architecture stage. The named
Gate-0 study owner is `config/gate0/default.json.policy.gate_owner_id`, copied
as `gate_owner_id` into `run_manifest.json`; T08 report validates equality
before publication.
Report consumes the metrics digest, run validity/status projection,
two-reviewer judgment digest, policy/preflight status, and repeat comparison
status. Reviewers, rankers, policy, and repeat never publish or mutate this
file; only the four declared decision values are permitted.

- [ ] Write the executable reviewer-input, blinding, two-reviewer, exact-token-cardinality, duplicate-key, unknown-token, wrong-digest, reviewer-visible-leakage, absent-query, six-family, paired-population, leakage, and precedence tests only in `tests/gate0/unit/test_metrics_decision.py`; author their valid/negative input cases in the exact JSON layout of `tests/gate0/fixtures/golden/judgments.json`; run the T08 command and expect RED.
- [ ] Implement only the specified metric formulas and mark unsupported runtime diagnostics `NOT_OBSERVED`.
- [ ] Rerun the exact T08 command; expected GREEN is exact oracle numerators/denominators and decision states.
- [ ] Run `python scripts/verify-gate0.py --metrics --decision-precedence --judgment-owner=T08 --review-input=tests/gate0/fixtures/golden/judgments.json`; expected result is PASS for static/synthetic checks.
- [ ] Commit with `git commit -m "gate0: define evaluation and decisions"`.

### T09 — attempts, retries, invalidation, rollback, retention

**Files:** Create `src/gate0/failure.py`, `src/gate0/repeat.py`,
`src/gate0/stages/lifecycle.py`; tests
`tests/gate0/unit/{test_failure_retention,test_rollback}.py`; goldens
`tests/gate0/fixtures/golden/{lifecycle,policy}.json`; `policy.json` is
test-only input owned by T04 and consumed by T09, never a runtime control path
or persisted artifact.

**Interfaces:** Consumes `ArtifactStore`, `Clock`, `PolicyDecision`, and
`StageResult`; produces sealed attempts/events with exact retry/interruption
semantics, closed membership digests, and five retention-class transitions.

- [ ] Write unchanged-retry, changed-digest denial, second-failure exit 40, interruption/resume, target-conservation, transition-failure, tombstone/privacy, and provenance tests; run the T09 command and expect RED.
- [ ] Implement immutable attempts, one unchanged transient retry, idempotent rollback, cleanup-pending blocking, and source preservation.
- [ ] Rerun the exact T09 command; expected GREEN is sealed ledger equivalence and non-searchable tombstones.
- [ ] Run `python scripts/verify-gate0.py --retention --rollback --invalidation --manifest-closure`; expected result is PASS for static/synthetic checks.
- [ ] Commit with `git commit -m "gate0: seal lifecycle and rollback semantics"`.

### T10 — repeat and operational verification

**Files:** Modify `src/gate0/repeat.py`, `src/gate0/cli.py`, and
`scripts/verify-gate0.py`; tests
`tests/gate0/integration/{test_cli_repeatability,test_verifier}.py`; golden
`replay.json`.

**Interfaces:** Consumes the frozen run manifest and exact CLI stage contract;
produces fresh-process frozen-index/full-pipeline replay comparisons and
verifier evidence states. Missing options use exit 40, illegal predecessors
exit 20, same terminal digest returns prior output, and changed identity starts
a new run.

- [ ] Write a table-driven test for every CLI/state/stdout-stderr case plus fresh-process cache policy and repeat-digest cases for unchanged inputs, changed source/target mapping, changed representation/ranking identity, and changed configuration; run the T10 command and expect RED.
- [ ] Implement fresh-process replay, immutable/cleared cache policy, vector-digest comparison, and verifier checks.
- [ ] Rerun the exact T10 command; expected GREEN distinguishes identity equality from allowed host/runtime differences.
- [ ] Run `python scripts/verify-gate0.py --repeatability --repeat-comparison-closure --synthetic-only`; expected result is PASS for static/synthetic evidence.
- [ ] Commit with `git commit -m "gate0: verify replay and CLI contracts"`.

### T11 — end-to-end synthetic acceptance and handoff

**Files:** Create `tests/gate0/integration/test_synthetic_acceptance.py`,
`docs/gate0/implementation-receipt.md`; modify only the verifier wiring named
above; golden `catalog.json` and all prior goldens.

**Interfaces:** Consumes all prior stage outputs and fixture catalog; produces
no new runtime artifact, only the bounded implementation receipt after the
later approved implementation session.

- [ ] Write the complete no-side-effect synthetic acceptance test, assert the exact seven-entry catalog and six v1.1 minimum roles, reject `policy.json` under any run output root and reject any second policy control file, and run the T11 command; expected RED is a missing artifact, illegal side effect, or failed projection.
- [ ] Implement no production behavior in this planning task; the later execution worker integrates only already-approved task outputs.
- [ ] Rerun the exact T11 command after all later tasks; expected GREEN is all static/synthetic projections passing with exactly 13 outputs.
- [ ] Run the full matrix command in the T11 row and require `bash scripts/verify-workspace.sh` to pass; runtime claims remain `NOT_OBSERVED`.
- [ ] Commit the later implementation-session acceptance checkpoint with `git commit -m "gate0: record synthetic acceptance"`.

## 9. Self-Review

- **Spec coverage:** T00–T11 and the exact schema/fixture/interface annex map every implementation-spec CLI, artifact, authorization, temporal, representation, ranking, evaluation, lifecycle, repeatability, security, fixture, and acceptance obligation. Unsupported runtime facts remain `NOT_OBSERVED`.
- **Placeholder scan:** the plan was searched for the current writing-plans contract's banned placeholder vocabulary and found no operational placeholder. Approval/future wording is authorization language, not an implementation placeholder.
- **Type/signature consistency:** the shared typed-boundary table, closed config schema, closed stage-payload union, and run-manifest shape are the single symbol sources; task cards consume/produce only those names, the 13 schema registry entries, the separate T00 config schema, and the exact matrix paths. The closure check validates field-level shapes and generic instantiations. The sample-target flat rational fields are the plan’s explicit v1.1 handoff representation and replace any contradictory generic object shorthand for implementation planning.
- **Scope rationale:** one plan is retained because stage order, 13-artifact ownership, policy/egress, and replay contracts are cross-cutting; T00–T11 remain independently testable units.

## 10. Execution Handoff

Plan complete and saved to `docs/plans/2026-09-12-gate0-implementation.md`.

1. **Subagent-driven execution (recommended):** after separate user execution approval, dispatch a fresh Luna Medium isolated lane per task using `superpowers:subagent-driven-development`, with the repository lane preflight and main-agent integration rules.
2. **Inline execution:** after separate user execution approval, execute task batches using `superpowers:executing-plans`, preserving the exact TDD commands, checkpoints, and no-egress constraints.

Neither option is authorized by this document or Issue #7. A later execution
task must re-read this plan, verify the approved specification, and obtain
explicit user approval before creating production code, tests, fixtures,
schemas, running media, downloading models, contacting providers, or entering
later gates.
