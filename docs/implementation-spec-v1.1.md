# Gate-0 Implementation Specification v1.1 (Draft for Review)

**STATUS: GATE0_SPEC_DRAFT — REVIEW REQUIRED; IMPLEMENTATION NOT APPROVED**

This is a bounded planning specification for the approved Gate-0 sampled-visual
retrieval diagnostic. It authorizes no production code, real-archive execution,
model download, provider request, cloud egress, or later gate.

## 1. Scope and boundary

Gate 0 tests whether one locally executed offline text-to-image embedding arm
improves useful visual-moment retrieval over a transparent metadata floor. The
evaluation is 24 positive and eight plausible-absent queries, four positive
families, two independent reviewers, and a frozen source-disjoint corpus.

In scope: authorized already-local media; read-only inventory/probing; fixed
four-second half-open windows; deterministic 2 FPS sampling; one offline
embedding arm; exact local cosine scoring; metadata floor; blinded judgments;
metrics; repeatability; resource/failure accounting; and local provenance
artifacts. Non-goals are native-video/audio reasoning, ASR, VDF, duplicate
canonicalization, fusion/reranking, cloud/provider dispatch, vector services,
Drive materialization, queues/schedulers, durable orchestration, custom UI,
editing/export/rendering, AI QC, GPU rental, and full-archive indexing.

Later code may be added only under a separately approved src/gate0/ with tests
under tests/gate0/; no implementation or tests are created by this task and
src/ remains README-only until explicit approval. Normative seams are injectable
decoder/PTS, embedding, filesystem/artifact-store, clock, policy, and egress
adapters.

## 2. CLI, identity, and statuses

Expose gate0 prepare|inventory|split|label|preflight|extract|embed|rank|
evaluate|report|repeat. Legal order is:

    prepare → inventory → split → label → preflight → extract → embed → rank
             → evaluate → report; repeat reads the frozen manifest afterward

Required options are run, canonical config, input root, output root, and an
explicit run_id or documented creation rule. Exit classes are 0 success,
10 valid negative evidence, 20 blocked prerequisite, 30 invalid protocol,
and 40 operational failure. Stage writes and artifact publication are atomic.
repeat is read-only. A repeated stage is idempotent only when its immutable
input/configuration digest and terminal output digest match; changed input,
policy, arm, query/gold version, threshold, or profile creates a new run and
never mutates an earlier run.

Opaque IDs are used for occurrence_id, revision_id, content_id, relation_id,
interval_id, window_id, space_id, representation_id, run_id, attempt_id,
invocation_id, artifact_id, assertion_id, policy_decision_id, and tombstone_id.
A path is a locator, not identity.

Status namespaces are distinct: stage_status =
PLANNED|RUNNING|SUCCEEDED|PARTIAL|FAILED|CANCELLED|BLOCKED;
provider_status = SUCCESS|PARTIAL|FAILED|UNSUPPORTED|ESCALATED;
assertion_status = ACTIVE|UNCERTAIN|NOT_OBSERVED|SUPERSEDED;
review_status = UNREVIEWED|ACCEPTED|REJECTED|AMBIGUOUS; and
benchmark_status = PLANNED|VALID|INVALID_PROTOCOL|PASS|FAIL|NOT_RUN.
NOT_OBSERVED is a status/availability value, never an evidence class.
Artifact availability is a separate namespace:
availability_status=AVAILABLE|QUARANTINED|CLEANUP_PENDING|CLEANED|TOMBSTONED.

## 3. Exactly 13 persisted artifacts

Gate 0 has exactly the following persisted files. The architecture contract's
12-file list is the experiment-result set; discovery_authorizations.jsonl is
the additional pre-run control artifact required to preserve the contract's
distinct discovery-versus-processing authorization boundary. Each file has one owner, one
schema version, and a content digest. JSONL records are independently
canonicalized and hashed; unknown fields are rejected by future schema tests.
Required fields are non-null unless explicitly NOT_OBSERVED.

| File and owner | Records and responsibility | Required joins |
|---|---|---|
| source_manifest.json (inventory) | Occurrences, immutable revisions/content, locator/probe evidence, inclusion, relation-component membership, source-preservation state. | occurrence→revision→content; per-record and whole-file digest. |
| discovery_authorizations.jsonl (inventory/policy) | Authority, occurrence/locator scope, custody, purpose, expiry, decision, and only DISCOVER/HASH/PROBE. | Each discovery attempt/revision references its authorization. |
| policy_decisions.jsonl (policy) | Revision scope, sensitivity/consent, purpose, permitted artifacts/provider/model, retention, expiry/revocation, limits, egress digest, and ALLOW/DENY/EXPIRED/REVOKED. | Revalidated for every non-discovery artifact, attempt, cache/projection read. |
| split_manifest.json (evaluation) | Frozen relation components, allocation, leakage check, and split version. | Relation inventory is frozen before allocation; no component crosses splits. |
| queries.jsonl (evaluation) | Unchanged text, family, presence, split, and version digest. | 32 evaluation queries (24 positive, 8 absent) plus 8 development queries. |
| gold_events.jsonl (labels) | Two-reviewer semantic [start,end) events, grade 0/1/2, uncertainty, rationale, adjudication, label version. | Revision and typed interval; ranking cannot read it. |
| window_judgments.jsonl (labels) | Blinded arm/window review, reviewer, grade, ambiguity, adjudication, assertion envelope. | Query/window/interval; one-reviewer runs are exploratory only. |
| window_sample_manifest.jsonl (sampling) | One row per target slot: typed window, exact half-second tick, selected PTS/frame, stream/time base, decoder result, duplicate reason, missing coverage. | Revision/window/interval/attempt; target accounting is conserved. |
| run_manifest.json (run owner) | Frozen inputs/config/policies, thresholds, attempts, invocation summaries, stage transitions, artifact digests, status projection, stop reason. | Idempotency key is run+stage+input_digest+config_digest; attempts are immutable. |
| ranked_candidates.jsonl (ranking) | Query/arm/window/representation, finite score, rank, total-order key, coverage/status. | Query/revision/window/space/representation; never gold labels. |
| runtime_and_failure_ledger.json (operations) | Runtime/resources, every failure/omission/retry, target accounting, egress blocks, invalidation, rollback, and permitted tombstones. | Run/attempt/artifact; planned=succeeded+failed+omitted+quarantined. |
| metrics.json (evaluation) | Denominators, Hit@10, family results, paired difference, diagnostics, coverage, validity, benchmark status. | Query/gold/judgment/ranking/baseline digests. |
| gate_decision.md (gate owner) | Authority, reviewers, prerequisites, criteria, validity, and exactly PASS/FAIL/INVALID_PROTOCOL/NOT_RUN. | References run and metrics digests. |

The following are record types, not extra files, and each has one canonical
owner; all other files carry only its ID and payload_digest reference. Attempts
and local invocations are canonical records in run_manifest.json; typed source
relations are canonical records in source_manifest.json; semantic typed
intervals are canonical records in gold_events.jsonl, while technical windows
and target intervals are canonical records in window_sample_manifest.jsonl;
assertion/evidence envelopes are canonical in the claim-bearing record that
creates them; space and representation descriptors are canonical in
run_manifest.json; and invalidation, rollback, and tombstone records are
canonical in the failure ledger. Split allocations are canonical records in
split_manifest.json; queries in queries.jsonl; gold_event records in
gold_events.jsonl; window judgments in window_judgments.jsonl; ranked candidates
in ranked_candidates.jsonl; metrics in metrics.json; policy decisions in
policy_decisions.jsonl; and discovery authorizations in
discovery_authorizations.jsonl. No logical record is duplicated as an
independent object in another file. A provider invocation is only a logical
seam in Gate 0 and never implies a cloud provider. This is the complete
persistence model: no fourteenth runtime artifact is permitted. A documented
optional projection, such as run_manifest.windows restating technical windows,
is a convenience view only and MUST NOT be read as the canonical owner of
another artifact's record. run_manifest.json also MAY carry the optional closed
`arms` registry described in Section 9.1.

The canonicalized config.json is a run-input/control file, not a derived Gate-0
artifact and not part of the 13-file result inventory; its digest is referenced
by run_manifest.json. Gate 0 does not persist a separate vector payload or
index-build file: representation and space descriptors plus vector/index
digests and rebuild recipes are embedded in run_manifest.json and referenced by
ranking records. A future gate may promote those projections only through an
explicit contract revision.

Minimum logical envelopes are: assertion (assertion_id, typed subject,
predicate/value/type, one of MEASURED/MATCHED/VISUALLY_OBSERVED/AUDIO_OBSERVED/
EDITORIAL_INFERENCE, producer, attempt/reviewer, coverage, uncertainty, status,
supersession, review, and replay/retention); interval (interval_id, revision/
stream, time_domain, start/end and endpoint rule, time base or mapping,
precision, assertion refs, and producer attempt); attempt (attempt_id, stage/
run, start/end, exit class, input/config/tool digests, status, outputs, failure
refs, and retry equivalence); relation (relation_id, left/right revisions, kind,
method, confidence/uncertainty, producer, and review); and space/representation
(model requested/resolved identity or NOT_OBSERVED, processor, preprocessing,
pooling, dimension, dtype, normalization, metric, runtime, config digest,
revision, window, attempt, artifact, and coverage).

## 4. Policy, splits, labels, and blinding

Discovery authorization permits only local discovery, hashing, and probing.
Processing needs a separate effective ALLOW; unknown, stale, expired, or
revoked policy blocks dispatch and governed cache reads. Inventory captures
pinned ffprobe JSON, selected stream/time bases, and failures.

Freeze the complete relation-edge inventory before allocation and split by
transitive component. If a post-freeze relation crosses splits, invalidate the
split and create a new split version; never silently reallocate. Use a
10–15-minute source-disjoint development subset only for feasibility. Evaluation
is 60–120 minutes across at least three sessions and six revisions, with actual
coverage recorded.

Freeze source/split/query/gold/rubric/reviewer/config/threshold digests before
preflight; stage input manifests prove that extract/embed/rank received no gold
or judgment paths. Two humans catalog and adjudicate the evaluation corpus.
Blinding hides arm, score, provider/model, rank, and any metadata not declared
visible. A new positive or mistaken absent label invalidates the held-out label
version; one-person runs are exploratory only.

## 5. Temporal, VFR, arms, and ranking

The technical origin is the selected stream's normalized presentation origin.
window_i=[origin+4i,origin+4(i+1)); incomplete final windows are omitted by
the default profile and counted in coverage. Targets are integer ticks 0..7,
exactly tick/2 seconds, compared to stream PTS by cross-multiplying integer
rationals without binary floating point. Store both target rational and any
derived stream tick. Negative/non-monotone/discontinuous/missing/out-of-range
PTS, wrong-stream frames, and ambiguous time bases preserve raw values and
produce named target/window coverage failures; they are never silently repaired.

Select the first decoded frame in declared presentation order whose presentation
PTS satisfies target <= PTS < end from the declared stream/time base. The
decoder/presentation order is authoritative; an adapter that reorders frames
must record that ordering and cannot silently substitute a later minimum. Record
decoder ordinal, presentation order, raw and normalized PTS, DTS/frame index
when available, source-frame identity, time base, and reason. These
source-frame identity fields are present exactly when a source frame was
selected for the target; their absence is explained by coverage_status or
duplicate_reason, never silently dropped. `precision` is a free-descriptor S
string, not an enum. Equal-PTS frames
use decoder ordinal first, then deterministic bytewise source identity. Deduplication is a target-to-frame observation, not silent row
deletion: retain one auditable row per target, distinguish repeated pixels at
different PTS from the same source frame, and declare whether aggregation is
over unique frame identities or target slots. No source frame is derived from
seconds×FPS. Semantic, technical-window, matched-offset, source-PTS/frame,
proxy, timeline, and rendered coordinates are distinct; Gate 0 authorizes no cut.

The metadata floor uses unchanged query plus basename and immediate parent,
Unicode-casefolded and split on nonletters/non-digits, with token-set Jaccard.
It consumes no annotations, transcript, generated title, or model description.
The semantic arm is one offline text-to-image model selected on development for
capability, license, and local smoke only; no winner is frozen and failure never
triggers cloud fallback. Frame vectors are L2-normalized, averaged per window,
then normalized. Non-finite/zero vectors remain status rows without a primary
rank or score.

The primary ranking excludes failed vectors. Its total tuple is finite score
descending, then bytewise UTF-8 source revision ID, normalized rational window
start, bytewise window ID, and bytewise unique candidate ID; collisions are an
error, not runtime-sort stability. Display rounding never affects ordering.

## 6. Metrics, repeatability, and failure

Primary metric is query-macro grade-2 Hit@10 over exactly 24 positive query IDs.
A hit is one binary result when any eligible grade-2 event matches a top-ten
candidate with the same revision and the declared typed mapping, half-open
interval intersection, uncertainty bound, and duplicate policy.
gold_events.jsonl plus its frozen version is authoritative; judgments are the
post-ranking blinded audit. A positive query without a grade-2 event is distinct
from an empty/failed ranking, and neither changes the denominator. Retain
per-query paired indicators and fixed six-query family membership/denominators.
Report numerator/denominator, family results, paired difference over the same
candidate universe, all failures, and secondary diagnostics.

Diagnostic thresholds are semantic Hit@10 >=20/24, paired lift >=5/24, and
>=3/6 in every positive family. Freeze before scoring; they are reversible
between protocol versions, not SLAs or productivity claims. Run both a
frozen-index query replay and a full-pipeline replay with separate attempts.
Their canonical repeatability projections compare source/window/target mapping,
selected frame identity/PTS, vector hashes or canonical values, complete
candidate identity/order, exact finite scores, failure/omission ledger, and
primary and secondary metrics. Runtime/host/RSS/thermal/timing may differ as
observations and are excluded from identity; missing thermal data is
NOT_OBSERVED. Any first differing identity-bearing record blocks PASS.

Identity mismatch, source mutation, unauthorized processing/egress, missing
provenance, invalid labels/leakage, unaccounted coverage, or missing required
target mapping yields INVALID_PROTOCOL; quality/resource failure is valid
negative evidence. One unchanged retry is allowed only for transient local I/O;
unchanged means same input/config/tool/environment digests, target set, and
error class. Failed attempts are sealed, new attempt IDs use retry_of, and
every target has exactly one terminal disposition:
planned=succeeded+failed+omitted+quarantined.

## 7. Invalidation, rollback, retention, and security

Every stage boundary and projection read revalidates source identity and policy.
Revocation, expiry, digest mismatch, or policy change propagates through
samples, frames, vectors, indexes, rankings, metrics, and caches, marks them
QUARANTINED, appends an invalidation event, blocks consumption, and forbids
rebuild until a new authorized revision/run exists. Source media is immutable.

Rollback is idempotent:
AVAILABLE → QUARANTINED → CLEANUP_PENDING → CLEANED|TOMBSTONED. The event
contains authority/actor, trigger, closed affected-membership digest,
before/after status, quarantine destination, timestamps, errors, and
idempotency key. Projections are unavailable while rollback is incomplete.
Retention classes are SOURCE_REFERENCE, DERIVED_REPLAYABLE, DERIVED_RESTRICTED,
AUDIT_MINIMUM, and TOMBSTONE; each has owner, expiry event/clock, readers,
deletion action, and rebuildability. After expiry, only policy-permitted
audit/tombstone fields remain usable.

A tombstone contains ID, deleted artifact/revision, parents, permitted digest
and byte count, reason, policy/retention refs, deletion time, producer/run/
attempt, schema version, and rebuildability. It is access-controlled,
non-searchable, contains no raw media/pixels/query text/credentials or
unredacted locator unless policy permits, and never replaces a source.

Gate 0 uses a deny-by-default network boundary for process and children,
including DNS/proxy behavior and forbidden cloud/provider/proxy destinations.
An attempted call records destination, protocol, attempted bytes, decision,
tool/attempt, timestamp, and outcome as EGRESS_BLOCKED, with no payload and
zero bytes. These egress fields are the `EGRESS_BLOCKED` conditional of the
Section 9.2 failure/control event row. Secret sources include
environment/config, exceptions, ffprobe,
locators, diagnostics, logs, manifests, and artifacts. Deterministic scans and
redaction fail closed on uncertainty. No credential, token, key, model weight,
large media, vector store, or secret enters source, artifact, log, bundle, or
commit; the UI is never a policy boundary.

## 8. Fixtures, schemas, and acceptance

The future fixture catalog has stable IDs, generation/tool version, container/
codec, stream time base, PTS sequence, duration, duplicate state, expected
schedule and selected PTS/frame or named failure, generation/check-in method,
and hash when checked in. Fake decoder/clock/embedding/filesystem/policy/
egress seams provide exact oracles plus one tiny media-backed adapter smoke
fixture. Versioned machine-readable schemas (or an equivalently precise
validator) cover all 13 files: fields/types/nullability, ID syntax, status
namespaces, typed intervals, canonical serialization, per-record/file digest
scope, foreign keys, and unknown-field rejection. Golden tests cover endpoint
and rational-time mapping, VFR/B-frame/malformed PTS, duplicate/ties, vectors,
metadata tokens, labels/leakage, CLI order and changed-digest rerun, retry/
rollback/invalidation, target conservation, repeatability, no-network/provider
sentinels, secret redaction, and prohibited later-gate artifacts.

Decision precedence is INVALID_PROTOCOL (identity/policy/leakage/coverage)
→ NOT_RUN with run stop reason BLOCKED_PREREQUISITE (missing required
inputs/feasibility) → repeatability failure → quality/resource FAIL or
diagnostic PASS. Thus BLOCKED_PREREQUISITE is never a benchmark result or
negative retrieval result: it projects to benchmark_status=NOT_RUN,
gate_decision=NOT_RUN, and exit 20.

Before execution verify authorized corpus/retention, two reviewers, frozen
manifests, effective local-only policy, feasible licensed offline model,
budgets, fixtures, reviewed config, and all documentation/security checks.
Current runtime results are NOT_OBSERVED; the current workspace verifier must
not pretend to validate runtime behavior. Explicit user approval is required;
only a later task after approval may invoke writing-plans. Gates 1–3 remain
out of scope.

## 9. Normative schema, digest, and decision annex

### 9.1 Serialization and envelope rules

The file artifact envelope is a canonical artifact-envelope record owned by
run_manifest.json; it is not a hidden line, sidecar, or undocumented header in
the payload file. It has artifact_id, artifact_type, schema_version, digest_algorithm, payload_digest,
producer_attempt_id, input_artifact_refs, policy_decision_id, retention_class,
availability_status, and created_at. A JSONL record additionally has record_id,
record_type, record_schema_version, record_digest, and payload fields. JSON
objects are UTF-8, RFC 8785-style canonical JSON: lexicographic object keys,
no insignificant whitespace, UTF-8 bytes, and finite numbers only. JSONL is one
canonical object per LF-terminated line, ordered by record_id bytewise. A
record_digest hashes canonical payload with record_digest omitted. A file
payload_digest hashes the ordered canonical lines including their LF bytes; the
envelope fields and payload_digest are excluded. Markdown gate_decision.md is
UTF-8 LF text with trailing whitespace removed, and its digest covers exactly
those bytes. Algorithm is SHA-256. IDs are lowercase ASCII
[a-z0-9][a-z0-9_-]{0,127}; digests are lowercase 64-hex strings. Foreign keys
carry both the opaque ID and referenced payload_digest where the referenced
artifact is immutable. Missing data is omitted only when optional; required
unavailable observations use the declared NOT_OBSERVED enum, never null-as-zero.

Two artifact shapes are JSON documents rather than JSONL line streams and are
closed: a record-collection artifact is exactly `{"records": [...]}`, and
source_manifest.json additionally carries bytewise-sorted unique `revision_ids`.
Each `records[]` item carries the record envelope. The term "record" is defined
in Section 9.2.

run_manifest.json MAY carry one optional root property `arms`: an array of closed
objects `{arm_id S R, representation_kind E R}` whose enum is exactly
`metadata_floor|embedding`, with unique arm_id, exactly the two D03 arms, and no
additional properties. `arms` stays outside the frozen 18-key required root
surface and requires no gate0.run_manifest.v2 bump. The cross-artifact validator
requires the registry whenever ranked_candidates.jsonl or window_judgments.jsonl
contains rows.

### 9.2 Required field matrix

The following matrix is normative. Fields not listed are prohibited. Type
suffixes mean S string, I non-negative integer, Z signed integer, R exact
rational object, B boolean, E namespaced enum, A array, and O object. Required
fields are marked R; optional fields are marked O. Every record also has the
record envelope.

| Record type | Required fields | Canonical artifact |
|---|---|---|
| occurrence/revision | occurrence_id S, revision_id S, content_id S, locator S, custody O, byte_count I, digest_algorithm S, content_digest S, stream_refs A, probe_ref S, discovery_authorization_id S, source_status E, relation_ids A | source_manifest.json |
| discovery_authorization | discovery_authorization_id S, occurrence_scope A, locator_scope A, authority S, custody O, purpose S, operations E[], expires_at S, decision E, decision_digest S, policy_decision_id S R | discovery_authorizations.jsonl |
| policy_decision | policy_decision_id S, revision_scope A, purpose S, sensitivity_consent E, allowed_artifact_types A, provider_model_boundary O, retention_class E, expires_at S, revocation_ref O, egress_manifest_digest S, decision E, effective_at_use B | policy_decisions.jsonl |
| relation | relation_id S, left_revision_id S, right_revision_id S, relation_kind E, method S, confidence O, uncertainty O, producer_attempt_id S, review_status E, relation_component_id S, relation_inventory_digest S | source_manifest.json |
| split_allocation | split_version S, relation_component_id S, allocation E, frozen_at S, relation_inventory_digest S, leakage_status E | split_manifest.json |
| query | query_id S, text S, family E, presence E, split E, query_version S, query_version_digest S | queries.jsonl |
| gold_event | assertion_id S, interval_id S, query_id S, revision_id S, reviewer_id S, grade E, uncertainty O, rationale S, label_version S, review_status E, adjudication_ref O | gold_events.jsonl |
| window_judgment | judgment_id S, assertion_id S, query_id S, window_id S, arm_id S, reviewer_id S, grade E, ambiguity E, review_status E, adjudication_ref O | window_judgments.jsonl |
| typed_interval | interval_id S, revision_id S, stream_index I, time_domain E, origin R, start R, end R, endpoint_semantics E, time_base R, mapping_ref O, precision S, producer_attempt_id S, refinement_eligibility E | gold_events.jsonl and window_sample_manifest.jsonl |
| sample_target | target_id S, window_id S, interval_id S, tick I, target_offset R, selected_frame_id O, raw_pts O, normalized_pts O, decoder_ordinal O, presentation_order O, pts_status E, coverage_status E, duplicate_reason O, stream_index I O, mapping_ref O O, dts_ticks Z O, frame_index I O, source_frame_identity O O | window_sample_manifest.jsonl |
| attempt | attempt_id S, run_id S, stage E, idempotency_key S, input_digest S, config_digest S, policy_decision_id O, started_at S, ended_at O, exit_code I, stage_status E, output_artifact_refs A, retry_of O, failure_refs A, tool_environment_digest S R | run_manifest.json |
| invocation | invocation_id S, attempt_id S, requested_model O, resolved_model O, processor_digest O, runtime_digest S, provider_status E, output_ref O | run_manifest.json |
| space/representation | space_id S, representation_id S, revision_id S, window_id S, sampling_manifest_digest S, model_identity R, processor_digest S, preprocessing_digest S, pooling E, dimension I, dtype E, normalization E, metric E, vector_digest O, generation_attempt_id S, representation_status E R, failure_reason O, vector_digest_algorithm O, vector_encoding O, vector_length I O, accumulation_order E O | run_manifest.json |
| ranked_candidate | candidate_id S, query_id S, arm_id S R, window_id S R, representation_id S O†, score O, score_status E R, rank O, tie_key O, coverage_status E R, gold_accessed B R | ranked_candidates.jsonl |
| failure/control event | event_id S, event_type E, attempt_id S, affected_refs A, reason S, before_status O, after_status O, authority O, occurred_at S, idempotency_key O, membership_digest O, payload_ref O, policy_decision_id S O, destination S O, protocol E O, attempted_bytes I O, transmitted_bytes I O, tool_identity O O, decision E O, outcome E O, payload O O | runtime_and_failure_ledger.json |
| metric | metric_id S, query_version_digest S, gold_version_digest S, judgment_version_digest S, ranking_digest S, baseline_digest S, population_id S, numerator I, denominator I, calculation_version S, benchmark_status E, validity E | metrics.json |
| gate decision | run_id S, benchmark_status E, gate_decision E, stop_reason E, metrics_digest S, threshold_digest S, authority S, reviewers A, decided_at S | gate_decision.md |

Required enum values are the namespaces in Section 2 plus coverage_status
PLANNED/SELECTED/FAILED/OMITTED/QUARANTINED/EMPTY, pts_status VALID/MISSING/
NON_MONOTONE/DISCONTINUOUS/OUT_OF_RANGE/WRONG_STREAM/AMBIGUOUS, and failure
event_type FAILURE/RETRY/EGRESS_BLOCKED/INVALIDATION/ROLLBACK/TOMBSTONE/
SECRET_SCAN. Cardinality is one-to-one for IDs ending in _id unless a field
ends in _refs or _ids; arrays are unique and bytewise sorted. This matrix is
the implementation contract; future machine-readable validators must encode it
without widening it.

Serialized enum values use the uppercase snake-case spelling written in this
matrix. The lowercase forms in `CANONICAL_CONTRACTS.md` are display aliases,
not serialized spellings. `reason` and `precision` are free-descriptor `S`
strings; no new enum namespace is invented for them.

The record types are closed per file: gold_events.jsonl is exactly the union
`{gold_event, typed_interval}`; window_sample_manifest.jsonl is exactly
`{sample_target, typed_interval}`; source_manifest.json is exactly
`{occurrence_revision, relation}`; no other record type is permitted in those
files. A "record" is one JSONL line or one `records[]` item; the nested arrays
within run_manifest.json (attempts, invocations, representations,
artifact_envelopes, stage_transitions, repeat_comparisons) are typed document
members, not records.

The gold_event row lists only gold_event fields: interval coordinates
(stream_index, time_domain, origin, start, end, endpoint_semantics, time_base,
precision, refinement_eligibility) belong to typed_interval and are not
duplicated on gold_event. † representation_id is required if and only if the
candidate's arm has representation_kind `embedding`, and is prohibited for
`metadata_floor`. Every embedding-arm candidate, including non-FINITE status
rows that carry no primary score or rank (Section 5), has a required,
window-matched representation_id; representation_status MUST be SUCCEEDED when
the candidate's score_status is FINITE, while non-FINITE status rows may
reference a non-SUCCEEDED representation. These cross-artifact conditionals are
enforced by the validator, not by JSON Schema alone. For
`event_type = EGRESS_BLOCKED`, policy_decision_id, destination, protocol,
attempted_bytes, transmitted_bytes, tool_identity, decision, outcome, and
payload are required; transmitted_bytes MUST be 0 and payload MUST be null.
Representation vocabulary is frozen: pooling `MEAN_TARGET_SLOTS`;
accumulation_order `target_tick_ascending_serial`; representation_status
`SUCCEEDED`, `FAILED`, `ZERO_VECTOR`, or `NON_FINITE`; dtype `float32` or
`float64`; normalization `L2`; and metric `COSINE`. metric_id is a dotted
identifier matching `^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$` with maximum
length 128; the generic opaque-ID grammar above does not apply to metric_id.

### 9.3 Matching, coverage, status, and retention decisions

Candidate-to-gold matching is defined as follows: use gold_events.jsonl, not
window_judgments.jsonl; require grade=2 and identical revision_id. The
candidate mapping is deterministic stream-origin mapping: semantic_seconds is
(normalized_pts minus normalized_origin_pts) multiplied by the declared exact
time_base, and the candidate semantic interval is the half-open interval formed
by its technical-window endpoints under that mapping. mapping_ref and
origin/time-base evidence are required in the sample manifest. Expand a gold
interval [start,end) by its explicit exact uncertainty [u_start,u_end] to
[start-u_start,end+u_end), then match when the candidate and expanded gold
intervals have non-empty half-open intersection. A candidate is eligible once
per unique candidate_id; relation-linked duplicates do not satisfy a second
hit. Any eligible candidate in the ranked top ten makes one query hit. No
grade-2 event yields a fixed zero for that query. Missing mapping, origin, time
base, or uncertainty conversion yields INVALID_PROTOCOL, not zero. This is a
typed coordinate relation, not a frame-accuracy or editorial-cut claim.

Every planned target is exactly one of SELECTED, FAILED, OMITTED, or
QUARANTINED. A declared incomplete final tail is OMITTED before scoring and is
included in coverage denominators; any unplanned or multiply classified target
is INVALID_PROTOCOL. A failed ranking is a status-bearing failed projection;
an empty valid ranking is an EMPTY projection. Either contributes zero to the
fixed query denominator but only INVALID_PROTOCOL blocks the run.

| Stage/run condition | stage_status | stop_reason | benchmark_status | gate_decision | exit |
|---|---|---|---|---|---|
| successful valid run | SUCCEEDED | NONE | VALID then PASS/FAIL | PASS or FAIL | 0 or 10 |
| quality/resource failure with complete accounting | FAILED | QUALITY_FAILURE | VALID | FAIL | 10 |
| missing corpus/model/reviewer/fixture before valid attempt | BLOCKED | BLOCKED_PREREQUISITE | NOT_RUN | NOT_RUN | 20 |
| identity/policy/leakage/coverage/invalidation failure | FAILED | INVALID_PROTOCOL | INVALID_PROTOCOL | INVALID_PROTOCOL | 30 |
| unexpected local operational error | FAILED or PARTIAL | OPERATIONAL_FAILURE | NOT_RUN | NOT_RUN | 40 |

Retention assignment is fixed: source_manifest and discovery/policy records are
SOURCE_REFERENCE until policy expiry; samples and representations are
DERIVED_REPLAYABLE until their source/policy expiry; rankings and metrics are
DERIVED_RESTRICTED until their input expiry; run and failure ledgers plus gate
decisions are AUDIT_MINIMUM for the policy-defined audit period; tombstones are
TOMBSTONE for that same period. On expiry, derived bytes are quarantined then
deleted if rebuildable, or deleted with a tombstone if exact rebuild is not
possible. Audit fields retained after deletion are IDs, digests, event times,
reason, policy/retention refs, and rebuildability only.

### 9.4 Invalidation, rollback, fixtures, and CLI matrix

The dependency closure is revision/policy → source manifest → sample targets →
representations/vectors → rankings → metrics/gate decision, plus caches and
projections. Invalidation operates on complete file artifacts and their
canonical records: the enclosing artifact receives the availability status,
while its record IDs are listed in the event for audit; a projection may not
serve a surviving record from a quarantined enclosing artifact. An invalidation
event lists the closed sorted artifact-ID set and membership_digest = SHA-256 of
its LF-joined IDs. Transition guards are AVAILABLE to QUARANTINED on invalidation;
QUARANTINED to CLEANUP_PENDING only after all dependents are unavailable;
CLEANUP_PENDING to CLEANED only after every rebuildable byte is deleted; and
CLEANUP_PENDING to TOMBSTONED only when exact rebuild is impossible and the
permitted digest record is sealed. Cleanup failure stays CLEANUP_PENDING and
blocks all reads. Rollback never restores a quarantined artifact in place; a
new authorized run is required.

The fixture catalog is checked in under tests/gate0/fixtures only after
implementation approval and must contain IDs cfr_4s, vfr_nonunit, vfr_negative,
duplicate_pts, missing_pts, and tie_oracle, each with PTS/time-base sequence,
expected selected rows, expected coverage/failure, and generation/hash method.
Schemas and fixtures are test-only and outside the 13 runtime files.

The CLI matrix is: missing required option → usage error/exit 40; illegal
predecessor → BLOCKED/exit 20; changed input/config/policy → new run, never
reuse; same terminal digest → return prior output without a new stage attempt;
interrupted stage → PARTIAL plus sealed failure ledger and resumable new
attempt; one unchanged transient I/O retry → new attempt with retry_of; second
failure → exit 40; repeat → new read-only attempt with frozen-manifest refs.
Machine-readable stderr is one failure/control event; stdout contains only the
human summary. These rules are future test obligations, not executed tests.

## 10. Six-cycle refinement provenance

All six cumulative cycles are mandatory and their accepted corrections are
integrated above: (1) authority/scope/traceability, (2) schemas/identity,
(3) temporal/deterministic semantics, (4) validity/estimands/repeatability,
(5) security/provenance/failure/rollback, and (6) testability/minimal handoff.
The durable ledger and six lane memos are the review record, not a second
normative specification. A cycle with no justified edit is recorded as a
verification pass; an early PASS never terminates the six-cycle process.
