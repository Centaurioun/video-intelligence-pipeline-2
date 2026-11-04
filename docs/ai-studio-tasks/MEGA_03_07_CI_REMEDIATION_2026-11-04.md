# VIP AI Studio LAB — MEGA-03–07 HOSTED-CI REMEDIATION MISSION

**Version:** LAB-MEGA-03-07-REMEDIATION-v1.0  
**Created:** 2026-11-04  
**Execution target:** \`Centaurioun/video-intelligence-pipeline-2\` ONLY (public lab)  
**Protected canonical repository:** \`Centaurioun/video-intelligence-pipeline\` — DO NOT MODIFY  
**Mission:** Fix source-verified incorrect AI Studio code and tests in MEGA-04/05/06/07 and PX without weakening canonical contracts or MEGA-03 security.  
**Execution model:** AI Studio writes code + pytest regression source, but **DOES NOT run pytest**. Owner pushes only the changed lab files; GitHub Actions runs real Python 3.11/3.14 tests and external review follows.

## 0. Why this mission exists

The initial AI Studio report declared all five MEGA waves \`COMPLETED_SYNTHETIC\` based on AST/compile checks. That is **not valid behavioral verification**. We independently read GitHub Actions logs and actual source modules. Many guessed API names, constructors and return types were wrong.

**Grounded LAB commit for current failure inventory:**
\`732763cfe79752be569df5e9ac70e5d2901271f4\`

**Grounded Actions run:**
https://github.com/Centaurioun/video-intelligence-pipeline-2/actions/runs/41750539083

Two Linux matrix members, Python 3.11 and 3.14, agreed on:

| Suite | Real executed outcome per Python version |
|---|---|
| Existing Gate-1/product tests | 146 PASS |
| Existing 3-profile integration tests | 39 PASS |
| MEGA-02 tests | 82 PASS |
| **Prior baseline total** | **267 PASS** |
| MEGA-03 | **13 PASS** |
| MEGA-04 | **6 FAIL** |
| MEGA-05 | **COLLECTION ERROR** |
| MEGA-06 | **1 PASS / 5 FAIL** |
| MEGA-07 | **2 PASS / 4 FAIL** |
| MEGA-CROSS-GATE / CLI | **4 FAIL** |

**No claim may be stronger than the underlying test evidence.** Failure counts above are as of the named SHA. If the imported ZIP, local files or GitHub changes differ, inspect actual contents before editing and record the divergence; do not blindly replay patches from an old SHA.

**Prior repairs ALREADY present in the LAB main (do not revert):**

- MEGA-03 S5 is now **metadata-only**. Any source-root or source byte access is refused, before \`os.open\`; no real media can be read, hashed, decoded or called MEASURED in this lab.
- MEGA-03 stream-identity preflight does not call the byte-consuming \`gate3.stream_identity.evaluate_stream_identity\`, does not invent a positive ffprobe/BMFF mapping, and keeps nonbinding status.
- \`src/vip_lab/__init__.py\` no longer eagerly imports the entire cross-gate integration tree. Preserve wave-level test independence.
- Six original \`src/gate0/media/\` Python modules, omitted from the reduced ZIP but present on the original canonical main, were restored **unchanged** in the lab. Their presence only fixes import dependencies; it does not authorize executing local media tools.
- CI executes all MEGA wave suites even when one fails, using \`continue-on-error\` for each test step and a **final mandatory failure gate**. Do not remove that final failure gate, hide failures or turn FAIL into PASS via skips.
- Two Python versions' existing 267 tests and 13 MEGA-03 tests passed on the named SHA. Preserve these invariants.

## 1. Exact authorities and execution limits

Read, as found in this imported workspace:

- \`AGENTS.md\`
- \`docs/ai-studio-tasks/MEGA_03_TO_07_COMBINED_SYNTHETIC_IMPLEMENTATION_PROGRAM.md\` (**LAB-MEGA-03-07-v1.1.0**)
- \`docs/ai-studio-tasks/MEGA_03_07_PROGRESS.md\`
- \`.github/workflows/vip-ai-studio-synthetic-ci.yml\`
- The relevant existing \`src/gate0\`, \`src/gate2\`, \`src/gate3\`, \`src/vip_fvs\`, \`experiments\` code and tests listed below.

**This remediation document narrows** the original umbrella mission: repair observed CI/source-contract failures, not add more subsystems.

Allowed writes only to:

- \`src/vip_lab/mega04/**\`, \`src/vip_lab/mega05/**\`, \`src/vip_lab/mega06/**\`, \`src/vip_lab/mega07/**\`
- \`src/vip_lab/integration.py\`, \`src/vip_lab/cli.py\` if real defects remain after producer repairs
- \`tests/vip_lab/test_mega04.py\`, \`test_mega05.py\`, \`test_mega06.py\`, \`test_mega07.py\`, \`test_cross_gate_integration.py\`, \`test_lab_cli.py\`
- \`docs/ai-studio-tasks/MEGA_03_07_PROGRESS.md\` for truthful checkpoint updates.

**Read-only:**
\`src/vip_lab/common.py\`, all MEGA-03 files and tests, \`src/vip_lab/__init__.py\`, canonical \`src/gate0/**\`, \`src/gate1/**\`, \`src/gate2/**\`, \`src/gate3/**\`, \`src/vip_fvs/**\`, \`experiments/**\`, \`schemas/**\`, \`.github/**\`, \`requirements/**\`, \`config/**\`, original docs/specs/decisions. If a repair unavoidably requires a read-only path, report \`BLOCKED_SCOPE\` with proof.

**No pytest execution, no package installation, no downloads, no network/provider calls, no real/protected media, no FFmpeg/FFprobe, no original-repository edits, no CI YAML edits, no Git push, no direct canonical source changes.**

Public lab must contain no private paths/archives, credentials, real source media, model assets or personal records.

The five assertion-level evidence classes are strictly:
\`MEASURED\`, \`MATCHED\`, \`VISUALLY_OBSERVED\`, \`AUDIO_OBSERVED\`, \`EDITORIAL_INFERENCE\`.  
\`NOT_OBSERVED\` is a **state marker**, not a sixth evidence class. **Never upgrade a synthetic fixture to real MEASURED evidence.**

## 2. Repair method: Superpowers systematic debugging without fake TDD

For EACH suite:

1. Inspect actual caller and callee source signatures before proposing a code change.
2. Locate the CI error at its exact function/line; state **root cause**.
3. Distinguish **test fixture is invalid** versus **implementation violates real contract**. Fix whichever is actually wrong; often both need changes.
4. Author or correct a real positive and a hostile refusal assertion first, then change the minimal lab implementation.
5. Preserve canonical producer validation rather than adding fake fields, private mutable aliases or bypass wrappers.
6. You may run \`ast.parse\` / \`compile\` on the changed Python source for syntax only; \`pytest\` is forbidden in AI Studio. Record \`RED=NOT_EXECUTED\`, \`GREEN=NOT_EXECUTED\`.
7. In the progress ledger record the source evidence, exact changed paths, invalid assumption, fix, new assertions, and \`IMPLEMENTED_UNVERIFIED\`.
8. GitHub Actions after the Owner's push produces the actual pass/fail evidence. When FAIL persists, another evidence-driven remediation pass is appropriate. Do not claim PASS in AI Studio.

Avoid changing expected results solely to make a test green. The exception is a test that **directly contradicts a verified, applicable frozen source contract**; correct the test to that contract and add an assertion that makes regression visible. Never delete, skip, xfail or blanket catch tests.

---

## 3. MEGA-04 — Gate-0 D-2, query/reviewer and experiment preflight

**Real CI:** 6 FAIL. All related to guessed source data models and invalid test fixtures.

Files to inspect:
- \`src/gate0/d2_intake.py\`
- \`src/gate0/labels.py\`
- \`src/gate0/reviewer_envelope.py\`
- \`src/gate0/config_freeze.py\`
- \`src/vip_lab/mega04/{d2_readiness,query_review_preflight,experiment_readiness}.py\`
- \`tests/vip_lab/test_mega04.py\`

### 3.1 D-2 package format — exact actual contract

\`gate0.d2_intake.D2_FIELDS\` contains **30 frozen \`D2FieldSpec\` entries**, not 7. The class fields are:

\`\`\`python
field_id, ordinal, domain, title, controlling_authority,
expected_evidence, unresolved_ruling, state_rule, validator,
observation_only
\`\`\`

**There is NO \`D2FieldSpec.required_evidence_keys\`.** The current test fixture accesses it and crashes.

\`D2_PACKAGE_FILE = "d2-package.json"\` and \`D2_PACKAGE_SCHEMA_VERSION = "gate0.d2-intake-package.v1"\`. \`load_d2_package\` reads this **one canonical package manifest** with closed schema. The current lab helper instead writes ad-hoc \`owner-attestation.json\` and \`d2-fields.json\` that the canonical loader does not expect.

\`evaluate_d2_package(package_dir) -> D2IntakeReport\`, with attributes:

\`\`\`python
package_id, package_digest, attestation_state, authenticity,
owner_approval_claimed, execution_authorized, counts, complete,
exit_code, results
\`\`\`

Each \`D2FieldResult\` in \`report.results\` contains:

\`\`\`python
field_id, ordinal, domain, title, state, declared_status,
validator_check, controlling_authority, expected_evidence,
unresolved_ruling, reasons, evidence_digests
\`\`\`

**Nonexistent fields used by current lab code:** \`report.fields\`, \`row.resulting_state\`, \`row.passed\`, \`row.reason_code\`, \`report.attestation_classification\`, \`report.reasons\`, \`report.d3_status\`.

Repair:
- Make \`src/vip_lab/mega04/d2_readiness.py\` consume exact canonical report fields.
- Change \`tests/vip_lab/test_mega04.py\` to generate a **legitimate synthetic D-2 package** using the exact frozen schema. Inspect \`_ALLOWED_PACKAGE_KEYS\`, \`_ALLOWED_FIELD_KEYS\`, \`_ATTESTATION_KEYS\`, \`_EVIDENCE_KEYS\` and the loader before choosing fixture fields.
- Do not invent \`required_evidence_keys\` or a second D-2 validator.
- Prefer \`tmp_path\` text-only fixtures that the existing loader admits. No corpus source paths; no implied Owner signature authenticity.
- Keep \`verified_count=0\`, \`owner_approval_claimed=False\`, \`execution_authorized=False\`, \`d3_status="NOT_AUTHORIZED"\` for synthetic claims; use actual \`report.results\` states.
- Guard source package path containment; do not read any source archive.
- New positive: valid synthetic D2 package gets a **valid declared/unauthenticated readiness classification**, never real approval.
- New negative: missing/wrong manifest digest, forged authorization claim, path traversal, unknown fields and incomplete evidence remain invalid/blocked as canonical validator dictates.

### 3.2 Query and reviewer producer API

**Actual \`gate0.labels.build_queries\` signature:**

\`\`\`python
build_queries(
    specs: Iterable[tuple[str, str, tuple[str, str]]],
    split_by_id: Mapping[str, str],
    query_version: str,
) -> tuple[dict, ...]
\`\`\`

Exactly **40** items are required, each specification **a tuple**:
\`(query_id, text, (family, presence))\`.
The current test supplies mapping/dict query specs; source does NOT accept those.

Protocol: **32 EVALUATION** queries (24 POSITIVE, 8 ABSENT), 8 DEVELOPMENT. Four permitted \`FAMILIES\` from \`gate0.labels\`; do not relabel a user's realistic text as actual positive-human-authored evidence.

**Actual \`gate0.labels.build_gold_events\` signature:**

\`\`\`python
build_gold_events(
    events: Iterable[Mapping],
    queries: Iterable[dict],
    label_version: str,
    *,
    reviewer_count: int = 2,
) -> tuple[dict, ...]
\`\`\`

Each gold assertion requires **two separate reviewer event rows** with exactly two distinct \`reviewer_id\` values, bound to same query/revision/start/end, and fields:
\`query_id\`, \`revision_id\`, \`reviewer_id\`, \`grade\`, \`rationale\`, \`stream_index\`, \`start\`, \`end\`.
The current one-event \`{"reviewers": ["alice","bob"]}\` fixture violates it.

\`gate0.reviewer_envelope.build_reviewer_envelope(rows, *, token_map, mapping_version, config_digest, ...)\` and \`validate_reviewer_envelope\` require named mapping/tokens and actual source shape. Read the defined \`ROW_REQUIRED_FIELDS\`, \`TOKENS\`, blinding constraints. Do not forge actual human review; fixtures are explicitly generated test input only.

Repair:
- Implement conversion of lab declarative query fixtures to the real \`build_queries\` tuple specification, preserving exact IDs and declared families.
- Correct gold-event fixture and producer calls to require two actual synthetic reviewer rows; distinguish test-only synthetic grades from accepted human labels.
- Ensure malformed query input returns the query-level refusal before evaluating gold; when testing gold-specific refusal, start from a **valid query baseline**.
- Assert ranker input contains **no hidden labels or held-out grades**.
- Config-freeze mismatch must follow actual \`inspect_freeze_readiness\` status semantics; do not arbitrarily change \`INVALID\` to \`BLOCKED\` without evidence.
- Absolutely no real Gate-0 D-3 execution, corpus discovery or authentication.

### MEGA-04 acceptance
\`tests/vip_lab/test_mega04.py\` collects and tests all intended positive/negative cases; the canonical D2 and labels modules are unchanged; no real \`VERIFIED\`/Gate pass appears.

---

## 4. MEGA-05 — Gate-1 model assets and benchmark identity

**Real CI:** test COLLECTION ERROR, plus inherited cross-gate \`AttributeError\`.

Files:
- \`src/vip_fvs/synthetic_profiles.py\`
- \`experiments/persistent_local_index/model_profile.py\`
- \`src/vip_lab/mega05/{model_assets,benchmark_entry,runtime_authority}.py\`
- \`tests/vip_lab/test_mega05.py\`

Exact canonical synthetic identity constant is:

\`\`\`python
CLOSED_SYNTHETIC_PROFILE_IDS = (
    V1_PROFILE_ID,
    V2_BASE_PROFILE_ID,
    V2_SO400M_PROFILE_ID,
)
\`\`\`

**\`SYNTHETIC_PROFILE_IDS\` is NOT a public producer symbol.** The MEGA-05 production modules were already repaired in lab with an **import alias**; the **test file itself still imports the nonexistent name**. Fix that test import.

\`ModelProfile\` has field \`family\`, not \`model_family\`. It has exactly these fields:

\`\`\`text
profile_id, model_id, family, frozen_revision, weights_sha256,
processor_asset_digests, processor_digest, image_preprocessing_digest,
text_preprocessing_contract, image_size, patch_size, embedding_dim,
output_dtype, normalization, loader_kind, device_backend,
precision_policy_id, precision_policy_version
\`\`\`

Replace uses of nonexistent fields in \`model_assets.py\` and dependent benchmark checks only after inspecting \`ModelProfile\` and actual \`SyntheticProfileBundle\` fields. Do not invent compatibility properties on canonical classes.

Invariants:
- V1 Base 768D, V2 Base 768D and V2 SO400M 1152D.
- Two 768D arms are **different semantic spaces**, never interchangeable.
- Correct V1 \`cpu\` and \`v1-float32\` policy.
- SO400M 1152D × four-byte float32 = 4608 bytes per row.
- Fake profile, self-declared weights digest and unobserved processor/tokenizer never count as authentic model execution.
- No real model assets/provider/download or benchmarking.
- \`benchmark_status="NOT_RUN"\`, \`winner=None\`, \`gate_decision="NOT_AUTHORIZED"\`.

MEGA-05 acceptance: test collection succeeds and any positive synthetic result does not imply actual model readiness.

---

## 5. MEGA-06 — Gate-2 synthetic workload, recovery and measurement

**Real CI:** 1 PASS, 5 FAIL.

Files:
- \`src/gate2/workload.py\`, \`recovery.py\`, \`faults.py\`, \`measure.py\`, \`decision.py\`
- \`src/vip_lab/mega06/{workload_plan,recovery_matrix,measurement_review}.py\`
- \`tests/vip_lab/test_mega06.py\`

### 5.1 WorkloadSpec exact signature

\`\`\`python
WorkloadSpec(
    jobs: int, stages: int, artifact_bytes: int, cost_units: int,
    fault_position: int, seed: int,
    f01_sha: str, c04_sha: str, e05_sha: str,
    config_digest: str, concurrency: int = 1, repetitions: int = 2,
)
\`\`\`

Limits: jobs 1..100, stages 1..20, artifact_bytes 1..1,000,000, cost_units 1..1,000,000, concurrency **exactly 1**, repetitions 1..100, \`fault_position\` from 0 to stages−1, product jobs×stages×artifact_bytes ≤8,000,000. Frozen SHAs are lowercase **40 hex** and config digest **64 hex**.

Find why current test's "valid" workload is actually \`INVALID\`; fix fixture or lab adapter by real constructor fields. Use \`generate(spec)\` as the true deterministic fixture generator; no rewrite of generator and no imagined \`total_steps\` property.

### 5.2 RecoveryBinding and harness actual interface

\`\`\`python
RecoveryBinding(
    f01_sha, c04_sha, e05_sha,
    workload_digest, configuration_digest,
    previous_manifest_digest, current_manifest_digest,
    generation_id, semantic_space_id, receipt_identity,
)
RecoveryHarness.open(checkpoint_path, binding, adapter)
harness.run(crash_point=None | "before_action" | "after_side_effect_before_completion")
\`\`\`

Inspect actual adapter methods consumed by \`RecoveryHarness\`, particularly
\`validate_receipt\`, \`reconcile_sqlite_tail\`, \`state_digest\`, \`start_or_resume\`, and anything subsequent code calls. Construct a **generated-only** in-memory/temp-fixture adapter obeying the actual contract. Do not build new production journals.

- Repeated operations should be idempotent where actual recovery contract requires.
- Tampered binding, corrupted checkpoint and invalid resume should refuse using \`RecoveryRefusal\` where appropriate.
- Validate real error class and ordering; no cheap \`INVALID\`↔\`BLOCKED\` swap just to appease tests.
- Do not alter source-media or live index storage.

### 5.3 Measurement and NOT_OBSERVED

**Actual \`gate2.measure.Measurement\` signature:**

\`\`\`python
Measurement(metric_id, unit, value, evidence_class, derivation, reason=None)
Measurement.measured(*, metric_id, value, unit, derivation, evidence_class="MEASURED")
Measurement.not_observed(*, metric_id, reason)
MeasurementSet()
measurement_set.add(measurement)
measurement_set.measurements
measurement_set.to_dict()
\`\`\`

**DOES NOT support:** \`status=\`, \`provenance_digest=\` constructor arguments, \`MeasurementSet.items\`.

\`gate2.measure.NOT_OBSERVED\` is an **object sentinel**, not the literal string. For absence, use \`Measurement.not_observed\`, do not put the string \`NOT_OBSERVED\` into \`evidence_class\`.

Fix \`measurement_review.py\` to interpret its synthetic lab payload as a **bounded declaration** and delegate to proper existing constructors; do NOT treat an untrusted generated metric value as proof of a real host measurement. Clearly isolate and label generated-only counters. Invalid evidence classes should fail via the actual validation surface.

The existing \`gate2.decision.MECHANISMS\` tuple **does exist**; avoid unnecessary repair. Mechanism needed remains NOT_DETERMINED and production eligibility False without real workload evidence.

MEGA-06 acceptance: true deterministic generated-only positive and negative recovery tests, correct measurement semantics, no infrastructure promotion.

---

## 6. MEGA-07 — Gate-3 exact rational PTS and QC safety

**Real CI:** 2 PASS, 4 FAIL; source timing/cut semantics have elevated safety priority.

Files:
- \`src/gate3/rational.py\`, \`pts.py\`, \`temporal.py\`, \`qc.py\`
- \`src/vip_fvs/real_preview_receipt.py\`
- \`src/vip_lab/mega07/{candidate_temporal_gate,editorial_lineage,qc_export_readiness}.py\`
- \`tests/vip_lab/test_mega07.py\`

### 6.1 Actual temporal classes and signatures

\`\`\`python
Rational(numerator: int, denominator: int)
# properties: numerator, denominator. NOT num, den.
TimeBase(num: int, den: int)
# methods: ticks_to_seconds(ticks), seconds_to_ticks_floor(rational_seconds)
PtsTable(time_base: TimeBase, ticks: tuple[int, ...])
# methods: is_ambiguous(tick), ordinal_of(tick, *, occurrence=None)
resolve_start(table, requested_ticks) -> SnapResult
resolve_end(table, requested_ticks) -> SnapResult
SnapResult(requested_ticks, resolved_ticks, policy)
classify_vfr(table, declared_rate=None) -> tuple[str, Rational | None, str, Any]
detect_discontinuity(table, start_ticks, end_ticks) -> list[tuple[int,int]]
\`\`\`

Incorrect fields in current lab code: \`Rational.num/den\`, \`TimeBase.rational\`, \`PtsTable(tuple(ticks))\`, \`table.is_ambiguous\` as property, \`SnapResult.resolved\`, \`.resolved_tick\`, \`.reason_code\`, \`classify_vfr(...).is_vfr/min_delta/max_delta\`, and two-arg \`detect_discontinuity(table, disc_gap)\`. Repair by using **actual** APIs.

**Critical frozen half-open semantics:** \`resolve_start\` chooses first PTS at-or-after requested tick; \`resolve_end\` chooses first PTS **strictly after** requested tick. With generated PTS values every 3000 ticks, the end requested at tick 180000 resolves to **183000**, not 180000. A current test expecting 180000 is incorrect; revise based on this real contract and add a focused half-open regression assertion.

**VFR ambiguity:** \`PtsTable\` accepts non-decreasing timestamps, including **duplicate** PTS. Nonmonotonic ticks are rejected; duplicate PTS require explicit retained occurrence where binding is attempted. Never silently take first duplicate. Use source-native integer PTS and rational timebase; never nominal FPS multiplication.

**Major evidence correction required:** Generated numeric PTS tables in AI Studio are *synthetic test fixtures*. The script currently sets \`evidence_state="MEASURED"\` and \`refinement_evidence_class="MEASURED"\` merely by math against self-declared data. **That is too strong** for a real archive claim. Keep candidate MATCHED, \`binding_eligible=False\`, and actual measured-source status NOT_OBSERVED. A synthetic computation can be reported as \`SYNTHETIC_DIAGNOSTIC_ONLY\` without upgrading canonical assertion evidence. Never promote a semantic candidate to an exact edit-ready boundary.

### 6.2 Actual QC functions and safety boundary

\`\`\`python
gate3.qc.bare_pass_is_insufficient(record)
gate3.qc.may_consume_for_binding_origin(
    record, attestation, *, source_content_digest,
)
\`\`\`

Current lab code calls \`bare_pass_is_insufficient()\` with no argument and \`may_consume_for_binding_origin(origin_string)\` with an invalid signature. Both are wrong.

- For bare \`"PASS"\` or missing evidence, block with a **lab-owned** refusal after inspecting the canonical field contract. If reusing \`bare_pass_is_insufficient\`, pass an exact correctly shaped, generated-only record; never invoke with a missing argument.
- \`may_consume_for_binding_origin\` consumes a **source-bound attestation**, can traverse Gate-3 measurement authority, and is NOT suitable for a synthetic origin string. **Do not call it** without independent source-bound evidence and current authorization. In this lab \`binding_consumable=False\` with a clear \`NOT_OBSERVED\`/not-authorized reason is the safe result.
- Technical QC Boolean fixtures are not real technical measurements. Editorial Boolean fixtures are not actual visual/audio/human observations. Successful synthetic structural check MUST NOT become real PASS.
- Production export is always \`REFUSED_NOT_AUTHORIZED\`, even if both synthetic axes are structurally complete.
- No render, no preview subprocess, no FFmpeg/FFprobe, no media reads.

### MEGA-07 acceptance
Valid generated rational PTS data produces only a **nonbinding diagnostic**, detects forbidden nominal-FPS derivation and ambiguity, and follows actual half-open semantics. QC remains synthetic and non-production. No source-native real MEASURED evidence is invented.

---

## 7. PX — Cross-Gate integration and CLI

**Real CI:** 4 FAIL, currently mostly inherited from MEGA-05 invalid \`ModelProfile.model_family\` and MEGA-07 invalid QC call.

Files:
- \`src/vip_lab/integration.py\`, \`src/vip_lab/cli.py\`
- \`tests/vip_lab/test_cross_gate_integration.py\`, \`tests/vip_lab/test_lab_cli.py\`

**Do not rewrite PX before the wave producers are repaired.** After MEGA-04/05/06/07 API alignment:
- Inspect all stage packet producers and consumers.
- Ensure one blocked stage does not falsely authorize a downstream stage; MEGA-03 source admission missing means MEGA-07 remains nonbinding.
- Fix any *independent* producer/consumer mismatches, not only broad exception catches.
- Keep cross-gate report deterministic and truthful, with no human/Gate promotion and no fake benchmark winner.
- CLI \`preflight-s5\`, \`preflight-gate0\`, \`preflight-gate1\`, \`preflight-gate2\`, \`preflight-gate3\`, \`summarize-program\` should produce stable refusal codes and nonzero exit status for blocked execution requests.
- Cross-gate tests should include one meaningful positive structural synthesis and multiple negative authority/lineage/identity cases; they should *actually invoke* source-backed lab functions, not mocks that always return expected values.

---

## 8. Work order: dependency-safe repair frontier

This is one bounded remediation job, not another feature expansion.

1. **Preflight:** source inspection and real CI log review. Identify tests previously passing; preserve 267 baseline and 13 MEGA-03 successes.
2. **MEGA-05:** unblock its import and correct model dataclass source attributes. Other PX tests depend on it.
3. **MEGA-07:** correct rational/PTS/QC source contracts and *remove synthetic→MEASURED promotion*. Other PX tests depend on it.
4. **MEGA-06:** repair WorkloadSpec, RecoveryHarness, Measurement / MeasurementSet source API usage and test fixtures.
5. **MEGA-04:** repair full 30-field D2 manifest/report and correct 40-query / 2-reviewer protocols.
6. **PX:** rerun interface reasoning and repair any remaining independent cross-gate consumer bugs.
7. **Static review:** make sure every source import and attribute exists; check no illegal media/model IO. Optional \`ast.parse\` is NOT pytest.
8. **Ledger:** replace inaccurate \`COMPLETED_SYNTHETIC\` claims with \`IMPLEMENTED_UNVERIFIED\` pending CI; record status for each wave and exact source-contract corrections.
9. **Stop.** No B08+, S5 grant rewrite, canonical promotion, new provider/model execution, hidden missing prerequisite bypass, nor second mega feature.

Do not stop after fixing the first wave; attempt all independent repairs and preserve a coherent checkpoint if interrupted. If any item genuinely requires forbidden canonical code modification or real source/model authority, mark \`BLOCKED_SCOPE\` and continue.

## 9. Host CI contract and mandatory final reporting

The workflow \`.github/workflows/vip-ai-studio-synthetic-ci.yml\` is already prepared. You MUST leave it unchanged.

It runs on Python 3.11 and 3.14:
- prior 267 test baseline;
- MEGA-03 (13 known passing on pre-remediation SHA);
- MEGA-04 / 05 / 06 / 07;
- cross-gate and lab CLI;
- a final aggregate step refusing any failed wave, even when every suite was attempted.

**AI Studio must NOT claim a CI pass.** The Owner will push completed changed lab paths, then we will inspect actual hosted run SHA and full logs. Later Codex independent review is still required.

Final answer in Turkish must include:

A. Local snapshot and source API names inspected, including ZIP \`.git\` absence.  
B. Exact root causes, per wave; distinguish invalid tests vs incorrect lab implementation.  
C. Every modified path and important updated function.  
D. Tests authored/changed, precise negative guards; \`AI_STUDIO_PYTEST=NOT_EXECUTED_BY_DESIGN\`.  
E. Model/media/PTS/authority invariants preserved.  
F. All unresolved blockers and \`PARTIAL_BLOCKED\`/ \`IMPLEMENTED_UNVERIFIED\` per wave.  
G. Progress ledger updated: \`docs/ai-studio-tasks/MEGA_03_07_PROGRESS.md\`.  
H. Owner handoff: **only selective changes to second public LAB repo**, don't delete remote \`.github/\` or historical docs by replacing the entire reduced ZIP.  
I. Exact next CI test selectors and clear acknowledgement that no RED/GREEN runs occurred locally.

**Do not start a new implementation mission after this remediation.**
