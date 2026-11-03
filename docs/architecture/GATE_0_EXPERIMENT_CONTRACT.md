# Gate 0 Experiment Contract

**Decision:** test whether one locally executed, sampled visual semantic arm
improves an editor's chance of finding a useful visual moment within ten ranked
candidates over a transparent metadata baseline. This contract authorizes a
future bounded experiment; it does not implement or execute one.

## Question, scope, and authority

Gate 0 is a retrieval diagnostic. It does not test duplicate quality, audio
search, native-video reasoning, frame accuracy, editorial quality, Reel
creation, provider quality, archive scale, or a production interface.

The owner approves corpus/policy before execution and signs the promotion record
after separate validity, quality, operations, and safety results. A run changing
corpus, query set, arm, model/configuration, policy purpose, or threshold is a
new experiment.

## Inputs and corpus

- 60–120 minutes of authorized, already-local media from at least three recording
  sessions and six source revisions, including available fast action, static,
  interaction, and group/scene content. Record actual coverage rather than
  inventing VFR/orientation claims.
- A separate 10–15 minute, source-disjoint development subset is permitted only
  for offline feasibility/configuration selection. It never contributes to the
  evaluation denominator.
- Source manifest records occurrence/revision/content identity, selected stream,
  locator, byte/hash/probe evidence, inclusion/exclusion reason, and local-only
  policy reference. A corpus lacking this authority is
  `BLOCKED_PREREQUISITE`, not negative retrieval evidence.
- Group known exact-byte, transformed, partial-copy, and same-session relations
  before allocation. No known group crosses development and evaluation. VDF is
  not a Gate-0 dependency.

## Queries, labels, and blinding

Freeze 32 text-to-visual evaluation queries before either arm ranks held-out
media: 24 positive queries, six per family—appearance, visible action,
interaction, and scene/composition/camera movement—and eight plausible absent
queries. Freeze eight separate development queries. Use the editor's actual
language; do not translate, rewrite, or derive query text from model output.

Two independent humans inspect the full evaluation corpus and create an event
catalog keyed to source revision and semantic candidate intervals. They apply:

- grade 0: irrelevant;
- grade 1: related but does not visibly establish the request;
- grade 2: visibly establishes a useful review candidate.

They adjudicate disagreements and record interval uncertainty. Labels are not
ranker input. After ranking, audit the blinded union of both arms' top ten. A
new positive or mistaken absent-query label invalidates the held-out label
version; preserve the result as exploratory and use fresh held-out data for a
pass claim. A one-person run is exploratory only.

## Arms and technical window profile

The transparent baseline tokenizes the unchanged query and original basename
plus immediate parent directory, Unicode-casefolds, splits nonletters/non-digits,
uses token-set Jaccard scoring, and logs empty/all-zero ties. It consumes no
annotations, transcript, generated title, or model description.

This metadata baseline is intentionally a **transparent floor**, not a validated
proxy for the editor's complete manual filename-search-and-scrubbing workflow.
Every window in a source inherits the same metadata score, so the baseline is
expected to be weak at temporal localization. The paired lift is therefore a
narrow diagnostic against this declared floor; it must not be reported as a
human-time-savings estimate or superiority to a strong production search
baseline. Stronger lexical/manual-workflow baselines belong to Gate 1.

The semantic arm is one offline text-to-image embedding model selected on the
development subset for declared capability, license, and local smoke feasibility,
not held-out quality. It uses fixed four-second, non-overlapping, half-open
technical windows. For the declared 2 FPS profile, targets are sampled at
`0.0, 0.5, 1.0, ...` seconds from each window start while the target remains
inside the half-open window. Record the first decoded presentation frame at or
after each target, deduplicate repeated frames, and record source PTS/time
base/stream/missing coverage. Never convert seconds to a source frame with FPS
alone.

The arm L2-normalizes frame vectors, averages and normalizes a window vector,
then ranks a normalized query by cosine using exact local scoring. This is
sampled visual retrieval, not a native-video or temporal-motion claim. A
non-finite vector, ambiguous timeline mapping, or zero-sample window is a
visible failure/coverage record. Each run freezes model/weights/processor/runtime
precision, preprocessing, window profile, space ID, tie rule, and configuration
digest before test labels are accessed.

## Required artifacts

1. `source_manifest.json`
2. `policy_decisions.jsonl`
3. `split_manifest.json`
4. `queries.jsonl`
5. `gold_events.jsonl`
6. `window_judgments.jsonl`
7. `window_sample_manifest.jsonl`
8. `run_manifest.json`
9. `ranked_candidates.jsonl`
10. `runtime_and_failure_ledger.json`
11. `metrics.json`
12. `gate_decision.md`

Artifacts carry content digests and use the Canonical Contracts identity,
assertion, time-domain, status, and policy rules. Rankings contain no gold
labels. Source media is immutable. Derived artifacts have explicit retention
and cleanup paths; cleanup preserves authorized provenance/tombstones.

## Metrics, validity, and repeatability

The primary metric is query-macro grade-2 `Hit@10` over exactly 24 positive
queries: an empty/failed ranking counts zero. Report the numerator/denominator,
per-family six-query results, paired difference, and every failure. Secondary
diagnostics are Hit@1/5, MRR@10, grade-2 Precision@10, graded nDCG@10, duplicate
occupancy, cold/warm latency, resource use, and coverage failures. Absent
queries are reported separately; Gate 0 makes no calibrated abstention claim.

Gate-0 provisional diagnostic criteria are semantic Hit@10 ≥20/24, paired lift
over the declared metadata floor ≥5/24, and ≥3/6 hits in every positive family.
These values are **reversible across protocol versions but must be frozen before
any scored Gate-0 run**. They are diagnostic experiment thresholds, not
production SLAs, estimates of population performance, or measures of editor
productivity. No Recall, semantic tIoU, ±2-second, duplicate, or frame-accuracy
claim is accepted by this gate.

Run the index twice from the same frozen inputs/configuration. Record hardware,
OS, accelerator, RAM, tool/configuration digests, elapsed decode/index/query
time, source minutes, windows/samples, index bytes, peak memory, storage growth,
and available thermal observations. Three randomized warm passes produce p50/p95
query timing; cold load is separate. Initial stop budgets are warm p95 ≤5 seconds,
indexing ≤4 hours, and peak RSS ≤80% of installed RAM. A pass requires identical
candidate identities/coverage, primary hit count, and top-ten order under the
declared tie rule. These limits are provisional local operability gates.

## Failure, rollback, and promotion

Identity mismatch, source mutation, unauthorized processing/egress, missing
provenance, invalid labels/leakage, or missing coverage makes the run
`INVALID_PROTOCOL` and prevents promotion. Quality/resource failure is valid
negative evidence. Do not alter an arm, provider, query, window, or threshold
inside a frozen run. One retry for transient local I/O is allowed if both
attempts are recorded unchanged.

Rollback quarantines derived outputs and preserves required manifests/failure
records; it never deletes or rewrites source media. A valid quality failure can
authorize one preregistered Gate-1 comparison after failure attribution. It does
not authorize provider shopping or cloud fallback.

A pass permits only a bounded Gate-1 benchmark proposal on fresh stratified data
for one named representation or capability question. It does not authorize cloud
dispatch, archive scaling, automatic canonicalization, editing, UI work, or a
production deployment.

## Prohibited Gate-0 dependencies

Cloud providers; real protected-media upload; ASR/transcript search; VDF
execution; canonicalization; fusion/reranking; Qdrant/LanceDB or another vector
service; Drive materialization; proxy lifecycle service; queue/scheduler/durable
event system; Google Video Analyzer reuse; custom UI; OTIO/Premiere/FFmpeg export
or rendering; crop tracking; Reel planner; AI QC; MCP/agent orchestration; GPU
rental; and full-archive indexing.
