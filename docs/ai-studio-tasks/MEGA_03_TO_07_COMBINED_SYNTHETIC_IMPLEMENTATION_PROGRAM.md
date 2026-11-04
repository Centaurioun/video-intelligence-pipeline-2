# VIDEO INTELLIGENCE PIPELINE — AI STUDIO LAB
# MEGA-03 → MEGA-07: ONE-TURN MULTI-GATE SYNTHETIC INTEGRATION PROGRAM

**Version:** LAB-MEGA-03-07-v1.0.0
**Status:** AUTHORING AUTHORIZED FOR EXPERIMENTAL LAB ONLY — NOT CANONICAL IMPLEMENTATION OR GATE PROMOTION
**Date:** 2026-11-04
**Target:** https://github.com/Centaurioun/video-intelligence-pipeline-2
**Forbidden target:** https://github.com/Centaurioun/video-intelligence-pipeline
**Report:** Turkish
**Task:** Implement as much of MEGA-03 through MEGA-07 as is genuinely implementable from the verified sources, in ONE uninterrupted AI Studio task. Write code and pytest tests; DO NOT execute pytest locally. Owner will push to the lab; GitHub Actions will execute tests.
**Pre-task lab baseline:** 1e2ab6e8572483508070bd72d0ec029897d9b66b — MEGA-02 accepted by lab CI before this instruction. If workspace files differ, inspect and report actual state rather than trusting this historical SHA.
**Lab CI verification:** run 41744170326 — Python 3.11: 146+39+82=267 passing; Python 3.14: 267 passing. This does not certify new work.
**Scope priority:** Correct, bounded, non-duplicative source changes > amount of code. A correctly refused/blocked subtask is superior to an invented integration.

---

## 0. EXECUTIVE AUTHORIZATION — FIVE WAVES IN ONE TURN

The owner wants a single large engineering assignment to accelerate delivery of the remaining code-capable lab preparations. This explicit authorization allows work only on the reduced ZIP workspace and subsequent human-selected promotion to the SECOND, public experimental repository. It does NOT authorize the original repository, model downloads, network, real-media processing, production output, canonical Gate decisions or relaxed security.

Do not stop merely because one independent wave encounters a blocker. Continue to the next dependency-safe wave, keeping a durable in-workspace progress ledger. Never work around the blocker by fabricating authority or silently modifying frozen contracts.

The five waves are:

- MEGA-03 — Gate-3 S5 contract preflight, source admission decision safety, stream namespace refusal and ReviewBundle consumption readiness. This is a compatibility/dry-run lab, NOT merging PR #258 or adopting P2 positive stream mapping.
- MEGA-04 — Gate-0 D-2 source-only readiness integration, honest query/reviewer inputs and diagnostic experiment preflight. NOT a real Gate-0 experiment.
- MEGA-05 — Gate-1 native model asset/authorization prerequisites and fail-closed runtime preparation, frozen three-model identities and benchmark eligibility. NOT a real SigLIP2 native adapter/session or actual model benchmark.
- MEGA-06 — Gate-2 synthetic workload/recovery fault contracts, coherent measurement-state summaries and no-premature-infrastructure decision guards. NOT representative scale acceptance or actual archive benchmark.
- MEGA-07 — Gate-3 candidate-to-temporal-to-human-to-plan-to-QC *preflight* integration and exported-artifact eligibility guards. NOT opening, rendering or exporting real media.

All waves should be attempted in this ONE task turn. Each wave has a self-contained interface and dedicated test file; if fully completed, mark IMPLEMENTED_UNVERIFIED pending GitHub CI. If blocked by a higher-authority decision or inaccessible PR branch, mark BLOCKED_SCOPE and continue independent waves.

**There is no requirement to fabricate 5 green deliverables.** No implemented behavior may claim a Gate is accepted or a real model/media has been observed.

---

## 1. GOVERNING PROJECT FACTS AND WHAT ALREADY EXISTS

Read the actual workspace files before writing a single module. These existing foundations must be reused, not copied or replaced:

### 1.1 Root rules and authority
- AGENTS.md
- docs/INDEX.md
- docs/project/00_PROJECT_CHARTER.md
- docs/project/01_CURRENT_STATE_AND_HANDOFF.md
- docs/project/02_ORCHESTRATION_DESIGN_AND_NEXT_PLAN.md
- docs/project/STATE_MAINTENANCE_PROTOCOL.md if available
- docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md
- docs/architecture/CANONICAL_CONTRACTS.md
- docs/project/PYTHON_TEST_MATRIX_AND_CI.md
- Existing lab MEGA-02 task and code in src/vip_fvs/query_batch.py, synthetic_profiles.py, batch_retrieval.py, three_arm_batch.py, batch_report.py, cli.py.

### 1.2 Gate-3 and S5 contracts
- docs/decisions/2026-10-25-g3-a7-stream-namespace-positive-mapping-disposition.md
- docs/superpowers/plans/2026-10-25-g3-a7-stream-identity-mapping-implementation-plan.md
- src/vip_fvs/source_snapshot.py
- src/vip_fvs/stream_identity_gate.py
- src/vip_fvs/review_bundle.py
- src/vip_fvs/human_decision.py
- src/vip_fvs/refinement_adapter.py
- src/vip_fvs/real_plan.py
- src/vip_fvs/real_preview_qc.py
- src/vip_fvs/real_preview_verifier.py
- src/gate3/pts.py
- src/gate3/temporal.py
- src/gate3/rational.py

### 1.3 Gate-0
- src/gate0/d2_intake.py
- src/gate0/config_freeze.py
- src/gate0/reviewer_envelope.py
- src/gate0/labels.py
- src/gate0/evaluation.py
- src/gate0/policy.py
- docs/gate0/D2_OWNER_INPUT_INTAKE_CHECKLIST_2026-10-25.md
- Existing relevant tests in tests/gate0/.

### 1.4 Gate-1
- docs/decisions/ADR-0002-post-completion-siglip2-migration-and-benchmark.md
- docs/migrations/siglip2-post-completion/32_PROVISIONAL_SIGLIP2_TOKENIZER_PROCESSOR_POOLING_CONTRACT.md
- experiments/persistent_local_index/model_profile.py
- experiments/persistent_local_index/model_space.py
- experiments/persistent_local_index/siglip2_native.py
- experiments/persistent_local_index/embedding.py
- src/vip_fvs/synthetic_profiles.py
- src/gate1/harness.py
- src/gate1/evaluation.py
- src/gate1/verify.py

### 1.5 Gate-2
- src/gate2/preregistration.py
- src/gate2/workload.py
- src/gate2/faults.py
- src/gate2/recovery.py
- src/gate2/measure.py
- src/gate2/decision.py
- src/gate2/verify.py
- Existing tests/gate2 unit/integration suites.

### 1.6 Source-of-truth corrections confirmed by GitHub at task creation

- The canonical original main is historically 592952daf475b1bbae2eebdee64d992c1a744f08; do not infer that the reduced lab ZIP has the same commit object.
- Original PR #258 was independently observed OPEN/DRAFT, head 5a60cd8e0abc021767b05c87ca50202822c049d0. It adds src/vip_fvs/_bounded_admission_fs.py, src/vip_fvs/bounded_admission.py and tests/vip_fvs/unit/test_bounded_admission.py, NONE OF WHICH ARE ALREADY PROMOTED TO ORIGINAL MAIN by that PR. Do not reconstruct, overwrite or claim to import PR #258 from the lab ZIP.
- Original PR #259 was OPEN/DRAFT, head e08382db65dcde703aadecc6ab329741f3c4b24c. It contains separate continuity/handoff material. It is NOT an implementation authority.
- A-7 positive FFprobe-global stream ↔ ISO-BMFF track mapping via positional track_ID is a PROPOSAL, not adopted; no new positive stream mapping.
- Gate 0 D-3 source execution is closed, human labels and authorised corpus are not observed; D-2 metadata validation is not real Owner authentication.
- Gate 1 authentic SigLIP2 tokenizer/processor/pooling remains NOT_OBSERVED; Gate B remains NO_GO_BLOCKED.
- Gate 2 synthetic workload does not prove representative production scale or justify ANN/queues/caching.
- Existing real-source Gate-3 components have security and exact-PTS contracts; the lab must not bypass them.

### 1.7 Evidence vocabulary

Exactly five assertion-level evidence classes:
MEASURED / MATCHED / VISUALLY_OBSERVED / AUDIO_OBSERVED / EDITORIAL_INFERENCE.

NOT_OBSERVED is a state marker, not a sixth assertion class.
Synthetic fixtures NEVER upgrade a real assertion's strength.
Semantically discovered candidate timestamps are nonbinding; never derive VFR frame ordinal by seconds multiplied by nominal FPS.
Source media immutable.

---

## 2. LAB ARCHITECTURE AND STRICT WRITE DOMAINS

**Design decision:** Do not build a competing source authority implementation or rewrite accepted gate code. Implement an experimental integration/admission readiness layer in a separate Python package. Use existing production contracts as read-only dependencies wherever signatures actually permit.

Create namespace:

  src/vip_lab/__init__.py
  src/vip_lab/common.py

Then create separate subpackages (with __init__.py) for each wave:

  src/vip_lab/mega03/
  src/vip_lab/mega04/
  src/vip_lab/mega05/
  src/vip_lab/mega06/
  src/vip_lab/mega07/

Add:

  src/vip_lab/integration.py
  src/vip_lab/cli.py

Required tests, each with meaningful parametrized positive AND negative assertions:

  tests/vip_lab/test_mega03.py
  tests/vip_lab/test_mega04.py
  tests/vip_lab/test_mega05.py
  tests/vip_lab/test_mega06.py
  tests/vip_lab/test_mega07.py
  tests/vip_lab/test_cross_gate_integration.py
  tests/vip_lab/test_lab_cli.py

The lab package MUST NOT be imported automatically by the canonical production CLI or gate entrypoints.

For each wave, group related functions in the named modules below. If the current repository already has an exactly matching production function, **call that function** and add only safe orchestration/validation, not a copy.

**Allowed edits:**
- src/vip_lab/** (new)
- tests/vip_lab/** (new)
- docs/ai-studio-tasks/MEGA_03_07_PROGRESS.md (create/update a concise checkpoint ledger during this one task; do not modify the task instruction itself)

**Forbidden edits:**
- original VIP repository and its PRs
- any existing src/vip_fvs/** module or existing src/gate0/**, src/gate1/**, src/gate2/**, src/gate3/**
- experiments/**, schemas/**, requirements/**, config/**
- existing tests outside tests/vip_lab/**
- .github/**, .gitignore, CI workflows
- original docs/project, docs/decisions, migration specs, frozen design records, WBS status checkboxes
- any real/protected media, authentic model assets/cache, runtime credentials.

No new dependencies. Use Python stdlib, existing project APIs, NumPy only where existing injected adapters require it, and pytest for test files.

If a genuinely required integration fix is outside the allowlist, report BLOCKED_SCOPE with symbol + exact cause; do not alter a frozen producer or invent a wrapper with weaker semantics.

---

## 3. SHARED INFRASTRUCTURE: src/vip_lab/common.py

Implement small lab-wide, dependency-light functions, not a new generic framework.

Required behavior:

1. Canonical validated UTF-8 JSON bytes, sorted keys, compact separators, reject NaN/Inf and nonstring mapping keys. Use existing canonical helpers when possible; do not invent digest semantics incompatible with existing model-space IDs.
2. Immutable, typed ReadinessFinding with:
   - stable case ID,
   - subsystem,
   - status enum: READY_SYNTHETIC / BLOCKED / NOT_OBSERVED / NOT_AUTHORIZED / INVALID,
   - nonempty reason,
   - source-reference string or NOT_OBSERVED marker,
   - expressly NO real-owner grant or Gate acceptance semantics.
3. A ReadinessPacket aggregating findings deterministically; status of a package is not PASS merely because its synthetic structure is valid.
4. Strict field/identifier/string/sha validators, integer-not-bool rules, positive rational timebase checks, deterministic summary/digest.
5. A closed synthetic-context marker. Never let a caller set an arbitrary "trusted", "approved" or "authentic" Boolean in a caller-provided JSON and have that count as verified.
6. Read-only, bounded JSON file loading for explicitly named lab scenario files (max 2 MiB; object_pairs_hook to reject duplicate keys; no symlink traversal or dereferencing arbitrary source locations). If conservative no-follow portable open is unavailable, refuse instead of falling back to unsafe generic path scanning.
7. Refusal errors with stable concise lab codes, separate from canonical Gate error enums. Do not mutate canonical failure vocabulary or silently substitute codes.

Do not add a daemon, service registry, workflow engine, generic plugin loader or remote fetcher.

Tests for shared functions may live in tests/vip_lab/test_cross_gate_integration.py.

---

## 4. MEGA-03 — S5 / E01 / REVIEWBUNDLE DRY-RUN INTEGRATION

Goal: integrate already-present source/S5 contractual facts **without implementing an unapproved source admission or positional stream mapping policy**.

Required modules:
- src/vip_lab/mega03/s5_preflight.py
- src/vip_lab/mega03/stream_identity_preflight.py
- src/vip_lab/mega03/review_bundle_check.py
- src/vip_lab/mega03/__init__.py

### 4.1 S5 admission dry-run

Build a strictly SOURCE-ONLY decision checker that accepts **synthetic, caller-supplied metadata declarations**, NOT source bytes or actual files:

- source revision reference (opaque ID),
- declared source SHA-256 (labelled DECLARED, not independently measured),
- selected stream index and declared stream kind,
- supplied policy-decision reference and declared custody state,
- whether the operator claims an E01/ReviewBundle handoff,
- optional declared closed candidate ID.

The checker must distinguish:
DECLARED / STRUCTURALLY_VALID / AUTHORITY_NOT_OBSERVED / INCOMPATIBLE / REFUSED.
No value presented by a caller becomes true source authorization by a syntactically valid declaration.

S5 scope overlaps original PR #258. This lab MUST NOT copy draft PR source or produce a substitute public BoundedAdmission API. Prefer read-only contract preflight tables. Do not open, stat, hash, walk, fstat or parse any actual media/path. Do not take filesystem paths as an admission result. If caller supplies a source_path, only hold it as an opaque string for display in explicitly synthetic data, never resolve or open it. Do not accept a declared digest as measured.

Fail closed for:
- unbound revision/digest;
- non-int/bool stream index;
- untrusted E01 claim;
- conflicting authorizations;
- unknown source identity;
- any request to construct an admissible REAL source authority token from synthetic metadata;
- any instruction to widen S5-T1 to source bytes, FFprobe, timecode, FFmpeg or parser work.

### 4.2 Stream namespace gate

Read existing src/vip_fvs/stream_identity_gate.py and current Gate-3 decision packet.
Build a **negative preflight** over metadata-only opaque synthetic indices:
- FFprobe-global video stream index is NOT assumed to equal ISO-BMFF direct trak ordinal.
- Container track_ID is not inferred from a path, decimal ordinal or synthetic declaration.
- An ambiguous multi-trak scenario yields NOT_AUTHORIZED/BLOCKED, NEVER an identity mapping.
- Existing single-track/sole-video result handling is a named existing-code behavior; do not reimplement or broaden it.
- A request for positional equality "because numbers match" is refused unless a separate adopted contract explicitly authorizes positive semantics. No such current adoption is assumed.
- A configured comparison for synthetic sample metadata must remain diagnostic only, not a certified stream identity.

Negative tests must assert no media stream opens and no accepted invented mapping.

### 4.3 ReviewBundle/E01 preflight

Read src/vip_fvs/review_bundle.py, including current_e01_validated and sealed-envelope validation. Do not create a fake ReviewBundle by bypassing its actual constructor/validation.

Build a consumer that can:
- inspect **only a provided, already validated synthetic ReviewBundle record**, using the actual existing ReviewBundle.from_record or relevant constructor when contract-permitted;
- report retained recorded lineage, dependency digest, schema version and whether an explicit existing E01 validation marker is present;
- refuse if a record is not a legitimate bundle envelope or has tampered digest, stale source revision, incompatible temporal identity or self-claimed authority;
- refuse transition to human acceptance / edit plan when mandatory bound evidence is unavailable;
- never create a human decision, edit plan or file writes.

No changes to canonical bundle schema. If a desired synthetic bundle cannot be created without forbidden source authority, write negative/refusal tests and mark this sublane BLOCKED_SCOPE, then continue MEGA-04.

### 4.4 MEGA-03 tests

tests/vip_lab/test_mega03.py must include:
- structured synthetic metadata valid-as-declaration but NOT real authority;
- unsupported bool/int, malformed SHA, missing policy reference;
- exact unbound source rejection;
- multi-track/global-index/ordinal collision refusal;
- no invented track-ID identity;
- existing real ReviewBundle validation/record roundtrip where actual API allows;
- tampered digest and E01 self-assertion refusal;
- injected no-call spies on model load, source open, probe, decoder, index writes, human decision, real plan.

**MEGA-03 success means a compatible lab preflight/refusal tool, NOT completion of B01–B04 or PR #258.**

Checkpoint MEGA-03 as IMPLEMENTED_UNVERIFIED or PARTIAL_BLOCKED in the progress ledger, then move to MEGA-04.

---

## 5. MEGA-04 — GATE-0 READINESS AND EDITORIAL LABEL BOUNDARY

Goal: create a pure read-only synthetic entry-readiness assembler consuming existing Gate-0 preparation tools without bypassing real Owner inputs.

Required modules:
- src/vip_lab/mega04/d2_readiness.py
- src/vip_lab/mega04/query_review_preflight.py
- src/vip_lab/mega04/experiment_readiness.py
- src/vip_lab/mega04/__init__.py

### 5.1 D-2 intake integration

Read existing src/gate0/d2_intake.py and identify the ACTUAL public functions for package load, structural validation and state assessment. Reuse them if available.

Produce deterministic:
- required input field IDs and declared/observed/blocked state summary,
- distinction between structurally valid and externally authenticated,
- exact pending Owner decisions,
- closed D-3 execution status (NOT_AUTHORIZED),
- no implied permission to open source paths or authenticate a self-declared OWNER_SIGNED field.

Do not copy the 30-field checklist into a new authority source. Call the existing registry/validator. If missing or undocumented, report NOT_OBSERVED, not a fabricated hardcoded conclusion.

No actual human input files are available from the public lab. Tests may use synthetic valid and invalid D-2 package fixtures in tmp_path, **only** where existing d2_intake API explicitly permits package-local text reads. Never use or inspect source-media paths referenced inside them.

### 5.2 Query and reviewer catalog boundaries

Keep separate:
1. 24 positive editor-authored queries,
2. 8 absent queries,
3. 8 development queries,
4. actual independent reviewer judgments,
5. query-to-window and revision-to-window binding.

A structurally sized 24+8+8 fixture is NOT genuine editor authorship.
Do not silently generate positives, labels or grades as human-written. Synthetic tests may create explicitly marked fake fixtures, with evidence absent.
Do not leak protected held-out labels into rankers, and do not assert query IDs imply true label-window association.
Use existing gate0 label/reviewer modules and tests to determine exact accepted symbols; never invent API names.

### 5.3 Experiment readiness

Combine existing src/gate0/config_freeze.py readiness outputs, D-2 reports, query/reviewer coverage, frozen metadata/semantic-arm policy and explicit D-3 closure into a conservative preflight packet:

- config digest exists as DECLARED but freeze_state remains NOT_FROZEN unless authoritative existing module says otherwise;
- no corpus-use permission inferred from declared manifests;
- no real experiment or 4-second window sampling;
- no metadata-vs-semantic measured lift;
- no fabricated Hit@10/graded nDCG/precision or Gate-0 decision;
- no model/rights/host readiness promoted from synthetic records.

Public lab user questions may be used as synthetic strings but do not become approved human labels.

### 5.4 MEGA-04 tests

tests/vip_lab/test_mega04.py:
- D-2 declared Owner signature cannot become VERIFIED;
- missing real corpus and human judgments block D-3;
- 24+8+8 fixture cardinality can be structurally valid but remains nonauthentic;
- duplicate query IDs, wrong family distribution, unknown window IDs refuse;
- leaking held-out labels into ranking surfaces is rejected;
- freeze readiness cannot mutate or actually freeze anything;
- no corpus/media opens and no real model calls.

**MEGA-04 result is a readiness inspector, not completed Gate 0.**

Checkpoint, continue.

---

## 6. MEGA-05 — GATE-1 THREE-PROFILE NATIVE READINESS, NO REAL MODEL

Goal: prepare the exact inputs for later authentic-model approval and a fail-closed *preflight*, NOT a fake authentic adapter.

Required modules:
- src/vip_lab/mega05/model_assets.py
- src/vip_lab/mega05/runtime_authority.py
- src/vip_lab/mega05/benchmark_entry.py
- src/vip_lab/mega05/__init__.py

### 6.1 Explicit closed model asset declaration

Consume declared synthetic-only model asset records for:
- V1 Base profile, V2 Base, V2 SO400M;
- declared model revision and SHA;
- processor/tokenizer asset digest declarations;
- device/precision policy;
- declared local license/usage status; use NOT_OBSERVED when unavailable;
- exact approved/observed status from an authoritative separate source, which is NOT provided in the lab.

Call existing ModelProfile validation and semantic-space functions. Enforce:
- V1 cpu / v1-float32 policy;
- V2 Base 768D and SO400M 1152D;
- distinct V1/V2 768D semantic spaces;
- bound processor/model revision;
- no silent 1152→768 truncation;
- no fake "authentic tokenizer" flag.

A declared SHA is NOT proof that weights were examined. Never read model files or caches, download checkpoints, initialize PyTorch, check devices or invoke real model APIs.

### 6.2 Runtime ordering and authorization

Build an injectable, **side-effect-free state machine** suitable for a future authentic execution guard, but do not expose a callable that opens a model. It may record expected predicates in a plan:

PROVENANCE_OBSERVED -> SOURCE_USE_AUTHORIZED -> MODEL_ASSETS_VERIFIED -> RUNTIME_PERMITTED -> CAN_PROPOSE_EXECUTION.

In THIS LAB, no real runtime grant exists; any transition to actual execution is forbidden.
Input claims cannot satisfy external authorization predicates by setting a Boolean. Values require a separate trusted authority unavailable in ZIP.
Test side-effect order with injected forbidden-call spies: source policy rejection must occur before any model factory / processor load / source access. Do not call the real source policy or model API with a dummy path.

### 6.3 Benchmark eligibility guard

Read existing Gate-1 evaluation, ranking and artifact semantics.
An authentic three-arm benchmark requires:
- validity-bearing Gate-0 acceptance,
- frozen and source-disjoint evaluation corpus,
- proper human relevance labels,
- authentic per-model runtime observations,
- identical query/sampling protocol,
- full omission/failure accounting,
- real host/runtime provenance.

The lab has NONE of these as evidence. The guard must keep benchmark_status=NOT_RUN, winner=None, selected_model=None, gate_decision=NOT_AUTHORIZED.

**Do not invent tokenizer vocabulary, BOS/EOS, padding, pooling, processor algorithms, or auto-download models.** The provisional document is non-executable design evidence only.

### 6.4 MEGA-05 tests

tests/vip_lab/test_mega05.py:
- three exact profiles and 768/768/1152 shapes;
- rejected fake or conflicting authentic identity;
- V1/V2 Base 768D cross-space mismatch;
- invalid/missing processor checksum declaration;
- unknown tokenizer/pooling prevents authentic runtime readiness;
- "owner_signed":true in untrusted JSON not equivalent to verified authorization;
- a forbidden model-loader callback is never called;
- no fake model score is promoted to winner;
- stable conservative report with explicit NOT_OBSERVED.

**MEGA-05 is a runtime-readiness lab, not an authentic V2 model implementation.**

Checkpoint, continue.

---

## 7. MEGA-06 — GATE-2 BOUNDED FAULT, RESTART AND MEASUREMENT HONESTY

Goal: build additional synthetic fault-injection and decision-preparation interfaces only where existing Gate-2 tools do not already provide them.

Required modules:
- src/vip_lab/mega06/workload_plan.py
- src/vip_lab/mega06/recovery_matrix.py
- src/vip_lab/mega06/measurement_review.py
- src/vip_lab/mega06/__init__.py

### 7.1 Workload plan

Consume explicit **generated-only** scenario declarations:
- stable synthetic workload ID,
- run/journal identity,
- bounded record counts and payload sizes,
- failure injection label,
- generated deterministic event sequence,
- expected counters and tolerances,
- repeat count.

Do not enumerate actual archive media, inspect codec distribution, imply 60–120 minutes of source footage exists, or claim host-scale throughput from CI runner.

Use existing src/gate2/workload.py and preregistration contracts when possible. Avoid creating another competing workload engine.
Synthetic scenario caps are local lab safeguards, NOT representative production envelope.

### 7.2 Restart/recovery scenarios

Use injected pure callbacks and temporary generated text/journal fixtures only. Test state transitions such as:
- prepared -> running -> interrupted -> resumable or terminal refusal;
- repeated completion idempotency;
- committed count preserved;
- partially written JSONL must not be interpreted as a committed valid record;
- duplicate work detection;
- checksum mismatch and truncation refusal;
- crash before commit vs crash after commit;
- restart path conflicts and immutable generation mismatch.

Reuse src/gate2/recovery.py and existing multi_source_recovery contract if actual interfaces permit; otherwise test pure readiness semantics without inventing a production journal format.
Do not write to source indexes/media. No daemon, queue, scheduler, vector service, ANN, cache or concurrency infrastructure without measured need.

### 7.3 Measurement attribution

Produce explicit separate columns:
- synthetic observation captured in generated fixture context,
- genuine host workload NOT_OBSERVED,
- model/runtime provenance NOT_OBSERVED,
- threshold suitability NOT_OBSERVED,
- mechanism_needed=NOT_DETERMINED unless supported by accepted measured workload.

Do not use the evidence class MEASURED for invented or merely expected numeric values. If the real Gate-2 Measurement type uses MEASURED for actually measured generated fixture numbers, preserve its domain boundary and attach explicit generated-only provenance. Do not silently present numbers as real scale validation.

Lab-only synthetic counters are valid test assertions but not a license to adopt caches or queues.

### 7.4 MEGA-06 tests

tests/vip_lab/test_mega06.py:
- deterministic bounded workload catalog;
- repeated generated-only run/receipt compatibility when existing Gate-2 functions permit;
- fail-closed truncated, duplicate, reordered and corrupted attempt records;
- exact once committed/replayed semantics where established;
- no false "no measured deficit" conclusion;
- never promote synthetic metrics to actual archive readiness;
- no real source reads, no external host profiling and no model files.

**MEGA-06 is synthetic reliability testing/preparation only; Gate-2 acceptance remains open.**

Checkpoint, continue.

---

## 8. MEGA-07 — GATE-3 SOURCE-NATIVE EDITORIAL / QC PREFLIGHT

Goal: connect established production contracts in an inert, explicit synthetic readiness chain; never materialize a real edit or render.

Required modules:
- src/vip_lab/mega07/candidate_temporal_gate.py
- src/vip_lab/mega07/editorial_lineage.py
- src/vip_lab/mega07/qc_export_readiness.py
- src/vip_lab/mega07/__init__.py

### 8.1 Candidate -> temporal boundary

Consume the B05/MEGA-02 candidate types in read-only mode when feasible.
A semantic retrieval candidate carries:
- exact source locator, digest and revision ID as declared record provenance;
- source_sample_pts int, rational timebase;
- evidence_class=MATCHED, binding_eligible=False.

A candidate is NOT a measured start/end interval.
Actual exact trim boundary requires independently source-native measured PTS/timebase evidence, verified source revision, stream identity, permitted temporal policy and required human decision.

Use existing gate3.pts.PtsTable, gate3.temporal.resolve_start/resolve_end, gate3.rational typed semantics on **test-generated numeric PTS tables only**. This can test VFR ambiguity, nonzero origins, B frames, duplicate PTS and discontinuity refusal.
Never do seconds × nominal FPS. Never infer an edit boundary from a formatted timestamp.

### 8.2 Editorial lineage

Read actual src/vip_fvs/review_bundle.py, human_decision.py and real_plan.py.
Create a pure preflight for an already constructed and genuine-in-context **synthetic** chain:
- exact source revision and stream/timebase identities;
- request/refinement identity;
- ReviewBundle dependency digest;
- decision artifact linkage;
- edit-plan revision and selected operation;
- no cross-source or cross-revision confusion;
- revoked/superseded decision handling;
- explicit editorial_inference evidence boundary.

Do not invent a human decision. A synthetic mock ACCEPT in a test must be labelled synthetic and never a real reviewer action. Do not invoke real-plan functions if they would require real source bytes or authorization. Invalid chains refuse rather than invent missing input.

No novel A-7 positive stream mapping, IT-6 tail admission, A-5 error vocabulary amendment or schema-v2 Gate-3 changes.

### 8.3 QC/preview/export readiness

Read actual source APIs:
- src/vip_fvs/real_preview_verifier.py
- src/vip_fvs/real_preview_qc.py
- src/vip_fvs/real_preview_receipt.py
- src/gate3/qc.py

Build a typed reviewer/technical readiness *inspector* that:
- requires named source/candidate/measurement/decision/plan lineage;
- requires independent technical output/PTS/stream evidence for preview QC;
- records editorial visual/audio evidence as NOT_OBSERVED unless actually provided by separately approved human observers;
- differentiates non-production preview approval from production export eligibility;
- keeps actual production export NOT_AUTHORIZED;
- refuses fabricated visual/auditory observations, fabricated output hashes and self-declared "QC PASS" flags;
- never calls FFmpeg, FFprobe, subprocess, model inference, real renderer, or writes media files.

The only safe successful outcome in this lab is a **structurally valid synthetic preflight packet** with explicit restrictions; not a verified real preview or production output.

### 8.4 MEGA-07 tests

tests/vip_lab/test_mega07.py:
- semantic candidate cannot become MEASURED or binding eligible;
- correct PTS and rational preservation, including nonzero and VFR fixtures;
- duplicate PTS ambiguity refuses if exact ordinal unsupported;
- missing snapshot/stream proof fails before decision/plan;
- mismatched revision, bundle digest, decision lineage or supersession refuses;
- missing human/editorial observations remain NOT_OBSERVED;
- QC cannot be marked PASS by self-declared field;
- no production eligibility after synthetic preview-only record;
- no media operations or changed index/source files.

**MEGA-07 does not implement or execute a real editorial pilot.**

Checkpoint, continue.

---

## 9. CROSS-GATE SYNTHETIC INTEGRATION — REAL COMPOSITION WORK

Required:
- src/vip_lab/integration.py
- src/vip_lab/cli.py
- tests/vip_lab/test_cross_gate_integration.py
- tests/vip_lab/test_lab_cli.py

This part should integrate the five READINESS packet types through validated, explicit dependency markers. Do not merely concatenate arbitrary dicts.

### 9.1 Cross-gate dependency graph

Represent only the actual dependency and state logic:

- MEGA-03 S5 and stream identity block may prevent actual source admissibility/ReviewBundle authority; do not incorrectly mark downstream Gate-3 eligible.
- MEGA-04 D-2 and Gate-0 readiness deficits block authentic Gate-0 validity and therefore authentic Gate-1 benchmark eligibility. They do not prevent independent synthetic MEGA-05 smoke.
- MEGA-05 model preconditions block real SigLIP2 inference; this does not prevent synthetic B08/MEGA-02 test vectors.
- MEGA-06 generated workload evidence is independent synthetic readiness; it cannot justify production infrastructure.
- MEGA-07 temporal/editorial/QC readiness remains subject to source-native measured evidence and independent human decisions, irrespective of semantic retrieval availability.

Use a typed stage result with:
- stage ID, inputs digest, produced packet digest,
- dependencies reviewed,
- status: IMPLEMENTED_UNVERIFIED / BLOCKED_SCOPE / NOT_IMPLEMENTED / NOT_OBSERVED,
- nonempty concise reasons, no evidence upgrades,
- synthetic_only=true, authentic_data_seen=false.

No stage may declare a Gate accepted or a hidden downstream permission.

### 9.2 Lab CLI

Add a *separate* lab entrypoint:

  PYTHONPATH=src:experiments python -m vip_lab.cli --help

Propose command names:
- preflight-s5
- preflight-gate0
- preflight-gate1
- preflight-gate2
- preflight-gate3
- summarize-program

All commands:
- accept only explicitly named, strict lab JSON inputs;
- do not access real media/model/external resources;
- emit a deterministic canonical JSON packet;
- print one non-success error JSON object on refusal and return nonzero;
- never fall through to the production vip_fvs CLI;
- reject extra unknown model/source/FFmpeg/export arguments;
- do not create sample source paths that refer to actual archive files.

If a command would require a protected file, genuine Owner input, unmerged PR code or missing authority, return BLOCKED_SCOPE/NOT_AUTHORIZED, not a synthetic success.

### 9.3 Cross-gate tests

- genuine positive synthetic preflight records remain unverified and nonbinding;
- one blocked phase does not stop independent phases;
- chained dependencies cannot be bypassed by flags or caller-provided "PASS";
- every output identity digest deterministic with unchanged inputs;
- malformed/fraudulent input fails closed and no side-effect callbacks execute;
- CLI outputs never claim authentic model, observed real media, benchmark winner or production export;
- source-native temporal review is not "made measured" by joining MATCHED candidates;
- no opaque score comparison across semantic spaces.

---

## 10. DO NOT DUPLICATE EXISTING IMPLEMENTATIONS

Before writing any function, check existing production code.

Where code already correctly implements a need, your integration should call it:
- SourceSnapshotStore, source_adapter and authorization remain existing custody authorities.
- ReviewBundle.from_record, current_e01_validated, dependency_digest remain existing bundle authority.
- gate0.d2_intake validators and config_freeze remain existing source-only inputs.
- ModelProfile and checked fake runtime in vip_fvs.synthetic_profiles remain the three-profile model-free contract.
- gate2 workload/recovery/measurement types are existing scope.
- gate3 PtsTable, rational and exact timing semantics remain source-native tools.
- Existing vip_fvs.batch_report and three_arm_batch remain synthetic retrieval report tools; do NOT rebuild that search engine.

The lab code may offer higher-level orchestration and reports. It must NOT create counterfeit "authorities" or a second persistent database/index/edit engine.

If your audit finds a proposed module would merely duplicate an existing API and add no measurable safety/compatibility value, explicitly mark it NOT_NEEDED with source path and evidence. You can omit that module only if you also update the dedicated MEGA wave's completion ledger and CI selection contract; the CI is controlled by the Owner, so do NOT edit CI to hide a missing deliverable. Prefer a small adapter with meaningful contract logic instead of generating boilerplate.

---

## 11. TEST AUTHORING WITHOUT PYTEST EXECUTION

Write all seven listed test files. Test **actual contract functions**, not mocks that return exactly the expected hardcoded results without touching the integrated code.

- Parametrize refusals; do not create thousands of duplicate lines.
- Use pytest tmp_path, in-memory JSON, mock model/source/FFmpeg callbacks, synthetic rational PTS fixtures.
- Do not instantiate real model sessions.
- No corpus scans or source video files.
- Never use real-world private paths, credentials or protected source digests.
- Do not change existing tests, xfail, skip, suppress failures or weaken real contracts to green CI.
- For read-only tests, verify before/after state or forbidden-call counters.
- Test no-bypass ordering, including forged "owner_signed", "MEASURED", "PASS", "production_authorized".
- Test report digest tampering, cross-space use, duplicate JSON keys, duplicate PTS and nontrivial timebase.
- Tests must behave on Python 3.11 and Python 3.14 and not require macOS-only actual execution in GitHub Linux runners.
- Optional pure offline ast.parse and compile() on new Python code is allowed; this is NOT a test pass.

Do NOT run pytest inside Google AI Studio.
Do NOT install dependencies or access network.
Do NOT run CLI or integration scripts.
Do NOT use FFmpeg/FFprobe.
Do NOT push to GitHub; user controls publication.

---

## 12. ONE-TURN EXECUTION AND CONTINUATION PROTOCOL

This is the key requirement: **attempt all five waves before ending**, without asking the owner a question already answered.

Recommended rolling sequence:

1. Audit existing source APIs and lock shared interface contracts in src/vip_lab/common.py.
2. Implement MEGA-03 with tests; record exact changed paths and any BLOCKED_SCOPE.
3. Implement MEGA-04 with tests, independently of blocked MEGA-03.
4. Implement MEGA-05 with tests; never try authentic model calls.
5. Implement MEGA-06 with tests; reuse established deterministic Gate-2 contracts.
6. Implement MEGA-07 with tests; no real render/export.
7. Implement cross-gate integration and lab CLI only after compatible staged APIs exist.
8. Run **offline static syntax/import-name reasoning only**, not pytest.
9. Write the checkpoint ledger for all five waves; report all files and remaining blockers.

Create/update:

  docs/ai-studio-tasks/MEGA_03_07_PROGRESS.md

The ledger must always contain:
- task spec version;
- local workspace snapshot uncertainty (if .git absent);
- per-wave state: NOT_STARTED / IMPLEMENTED_UNVERIFIED / PARTIAL_BLOCKED / BLOCKED_SCOPE / NOT_IMPLEMENTED;
- exact completed files and unresolved functions;
- API assumptions verified against actual source or still unverified;
- a list of tests authored, all NOT_EXECUTED_BY_DESIGN;
- most recent completed wave and exact safe next independent step;
- no fabricated CI PASS, commit SHA or real-model/media evidence.

**If context/time/response budget is exhausted mid-task:** Finish a coherent, saveable slice, update the ledger, and stop with PARTIAL_BLOCKED. The owner can use a new AI Studio turn to resume from the ledger with the instruction at the bottom of this document. Do not rewrite completed work just to fill time. Do not silently mark the task complete.

**If a wave has an authorization dependency not available in this reduced ZIP:** record the exact dependency and proceed to the next independently implementable wave. There is no need to stop the entire program.

**Do not manufacture duplicate modules just to make the package look large.**

---

## 13. HOSTED CI CONTRACT — OWNER-CONTROLLED

Existing remote lab workflow:

  .github/workflows/vip-ai-studio-synthetic-ci.yml

It is maintained separately by the user/ChatGPT GitHub controller, not by AI Studio.

The controller will configure:
- Python 3.11 and 3.14;
- existing 267-per-version synthetic baseline;
- bounded test suites tests/vip_lab/test_mega03.py through test_mega07.py;
- cross-gate and lab CLI tests;
- fail if a wave is partially deposited with missing required files;
- allow independent completed waves to run even if another wave is not yet delivered.

A "SUCCESS" check for an intermediate push does not prove all five waves are implemented. Confirm the executed test filenames and actual selected counts. Do not claim CI passed inside AI Studio.

**Independent review after CI:**
- tests actually exercise real integration seams;
- code does not bypass authority or perform real media/model/provider actions;
- contracts not invented;
- no mistakes like undefined imports, nonexistent enum members, wrong dataclass fields or invented error strings;
- no violation of VFR PTS/timebase semantics;
- lab-only changes are not blindly merged into canonical main.

---

## 14. FORBIDDEN CLAIMS AND ANTI-FAILURE RULES

Never state that:
- B00–B11 are now all completed;
- PR #258 is merged or reimplemented here;
- A-7 P2 positive stream mapping is approved;
- Gate-0 actual experiment or two human judgments occurred;
- V2 native authentic inference, tokenizer/processor/pooling were observed;
- Gate 1 chose a winner, or SO400M is empirically better;
- measured production scale needs a cache/ANN/queue;
- semantic timestamps are exact edit boundaries;
- fake human decision is actual editorial approval;
- generated preview is a real rendered result;
- export is production-eligible or any of four Gates are promoted;
- merely compiling Python is passing integration tests.

Never authorize a source path by copying SHA/flags from its own input. Never convert a synthetic fixture's self-declared authority to trusted proof.

Never use hard reset, git clean, force push, destructive cleanup, branch deletion, or protected archive execution.
Never overwrite existing V1 preserved/model-space storage, existing receipt records, historical rejected alternatives, WBS status, or original repo branches.

---

## 15. FINAL REPORT AND DISPOSITION (TURKISH)

The final answer should use:

### A. Snapshot
Repo identity, actual inspected files, current ZIP/Git caveat.

### B. Baseline versus new work
For each MEGA-03–07: existing real APIs, actual missing integration, work not done because duplicate or unauthorized.

### C. Changed paths
List EVERY new file and modification exactly. Do not claim changes that do not exist.

### D. Implementation by wave
For each wave describe actual producer/consumer, validation, refusal, deterministic identity, and side effect boundaries.

### E. Tests authored (not run)
Enumerate each new test file and major positive/negative cases.
Print exactly: AI_STUDIO_PYTEST=NOT_EXECUTED_BY_DESIGN.
If offline AST used, state exactly what compiled.

### F. Blockers
Exact source API, unmerged PR dependency, frozen contract, lack of real human/model/media/host observation, or missing authority.

### G. Progress ledger
The saved docs/ai-studio-tasks/MEGA_03_07_PROGRESS.md path and precise last completed wave.

### H. CI handoff
Only the changed files should be committed to the second lab repo, preserving .github/ and remote content. CI will run selected wave tests after Owner push. Any FAIL will be handled by source-based systematic debugging, not broad rewrites.

### I. Status
Per wave and overall:
IMPLEMENTED_UNVERIFIED / PARTIAL_BLOCKED / BLOCKED_SCOPE / NOT_IMPLEMENTED.
Final overall state cannot be VERIFIED_COMPLETE until GitHub CI and independent review.

Do not start new task packages after MEGA-07. Do not proceed to real operations.

---

## 16. SHORT CONTINUATION PROMPT FOR A LATER AI STUDIO TURN (ONLY IF INTERRUPTED)

When the Owner explicitly invokes continuation, use:

Read docs/ai-studio-tasks/MEGA_03_TO_07_COMBINED_SYNTHETIC_IMPLEMENTATION_PROGRAM.md
and docs/ai-studio-tasks/MEGA_03_07_PROGRESS.md.
Inspect actual current source.
Continue from the earliest incomplete, safely independent wave.
Preserve completed files and the contract decisions already recorded.
Do not run pytest, install, download, operate real media/model,
modify GitHub Actions or push to GitHub.
Update the ledger and report in Turkish.
