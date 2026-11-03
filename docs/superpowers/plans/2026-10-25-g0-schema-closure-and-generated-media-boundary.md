# Gate-0 D1–D8 Schema Closure and Generated-Media Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use Superpowers executing-plans or subagent-driven-development under the repository's rolling-frontier/exclusive-writer protocol. Apply RED→GREEN TDD for source/schema behavior changes. This plan records decision boundaries; it does not itself authorize changing frozen Gate-0 identity or experiment semantics.

**Goal:** Make the 13 Gate-0 generated-media artifacts validate against their approved closed JSON schemas without weakening the frozen experiment contract, and ensure a merely declared `generated` input cannot silently masquerade as authorized fixture-origin evidence.

**Architecture:** One contract-owner adjudication lane freezes the canonical D1–D8 schema/producer resolutions; a disjoint source-boundary lane prepares bounded/no-follow local media proof. After the decisions are accepted, disjoint code/schema authors implement tested changes and a fresh generated-MP4 run must show actual `--schema-payloads` PASS **13/13**. All diagnostic results remain `NOT_RUN` for real Gate acceptance.

**Tech Stack:** Gate-0 Python/Pytest, Draft 2020-12 JSON Schema / jsonschema, local FFprobe/FFmpeg on generated disposable MP4s, exact Fraction/integer PTS, existing source inventory and provenance.

**Spec:** `docs/agent-runs/2026-10-25-four-gate-wave2/contract-owner-proposal.md` on PR #166 at immutable head `d50bc631a4561775cf0bbd332cdde141e169b050`, plus `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md`, `docs/architecture/CANONICAL_CONTRACTS.md`, `schemas/gate0/registry.json` and Owner-approved four-Gate WBS.

## Global Constraints

- Planning baseline is `main@4144733cc3de04e928bff0c862693474a0a04c11`. Before actual code work, re-fetch main and PR #166 exact head; do not implement against older source-copy assumptions.
- Existing PR #166 already implements FFprobe/decoder generated-media measurement and new `--schema-payloads`; **do not reimplement** those subsystems. Its report says **eight schema failures**, which constitute real observed drift; 622 passing Gate-0 tests do **not** mean 13/13 payload validation.
- Preserve frozen 4-second half-open windows, 2 FPS sampling, 24 positive + 8 absent queries, Hit@10 20/24, paired-lift 5/24, each family 3/6, strict review isolation, exact rational uncertainty and source-native PTS. No synthetic PASS for a real Gate-0 decision.
- The project currently distinguishes authorized source permission from artifact paths. A user-writable manifest with `generation` claims is **not** independent evidence that bytes were generated on this host. No speculative protection claim: either bind to a locally controlled fixture-generation operation in the admitted synthetic runner, or identify as `DECLARED_LOCAL_MEDIA / ORIGIN_NOT_OBSERVED` and refuse eligibility for the synthetic-only path.
- Source immutable. Before opening real/protected media, separate explicit authorization is required. Any source handling during generated fixtures must be bounded by accepted byte quotas, explicit path resolution, no-follow source opens, and digest/identity consistency. Do not adopt unrestricted whole-file `read_bytes()` as a production media strategy.
- No model download, authentic model inference, provider/cloud calls, protected archive execution, production export, Gate promotion or new development SOURCE-AUTH grants.
- No changes to canonical main or Owner-frozen backup `backup/OWNER-DO-NOT-MODIFY-main-20261024-17edacbe@17edacbe64983ae284f09a8386377200bf538ec3`. No destructive Git.
- Source-schema and source-code changes must use separate exact file owners. If a governing spec genuinely needs a semantic amendment, obtain a contract-owner decision **before** editing; never auto-widen or auto-trim to make tests green.

## Review Focus

1. **Schema-per-file vs record-level shape:** `source_manifest.json` / `split_manifest.json` are multi-record documents, while JSONL entries carry their envelope; verify neither shape is silently reinterpreted → Task 2.
2. **T08 frozen metric identity:** dots in metric IDs must remain literal stable identities; do not rename to comply with an overly narrow generic ID regex → Task 3.
3. **Interval/timebase status and gold uncertainty:** exact rational values and canonical eight time domains must be retained, not serialized through floating point → Task 4.
4. **Metadata-arm representation:** no fabricated embedding model descriptor or misleading representation class; explicit arm/space semantics and blinding provenance must be signed off → Task 1/5.
5. **Locally declared media path:** symlinks, changing source, oversized file, escaped locator, untrusted manifest and generator/byte mismatch must refuse before probe or decode → Task 6.

## Decision register before code

| ID | Governing resolution proposed for Owner/contract-owner confirmation | Protected invariant |
|---|---|---|
| D1 ranked candidates | Add exact `arm_id`, `window_id`, optional `interval_ref`; use the **governing record schema version**, not an invented duplicate interval | Candidate ↔ window identity |
| D2 window sample schema | Closed union of `sample_target` and `typed_interval` with exact rational time-base and stable origin; align status vocabulary to actual approved canonical meanings | Sampling/refinement evidence identity |
| D3 gold uncertainty | Explicit optional rational `{start,end}`, never float conversion; missing certainty cannot yield real valid evaluation | Human-label uncertainty |
| D4 time-domain | Use the canonical eight time-domain values; reject legacy alias unless a separately approved migration maps it exactly | Non-upgraded evidence |
| D5 manifest/ledger | Match frozen artifact-type, representation and egress vocabulary. For extension properties, **prefer only those required by existing authority/provenance contract**; unknown fields must be deterministically refused or formally versioned | No blanket `additionalProperties=true` escape |
| D6 manifest document shape | Closed multi-record document wrapper retaining fully validated inner record schemas | 13 artifact owners |
| D7 metrics | Explicit approved T08 identifiers or narrowly scoped dot-supporting metric-id grammar; **no producer metric renaming** | Reproducible results and comparison |
| D8 specification matrix | Update only after D1–D7 acceptance to accurately describe final artifact fields; preserve old historical decisions | Authority clarity |

**Owner questions retained (NOT silently settled):** (a) metadata arm: explicit `arm_id`+registry/representation_kind (recommended) vs optional descriptor; (b) `blinding.access_scope="T08_only"` is a provisional implementation value, not historically owner-approved; (c) select exactly which `run_manifest` extensions are mandatory/optional/removed. Present a compact decision table and evidence for those three before editing frozen contract or treating 13/13 as an approved schema revision. The user authorized proceeding with schema reconciliation, **not selecting undocumented semantics without review**.

## Parallel readiness and task ownership

| Task | Files | Can start | Dependency |
|---|---|---|---|
| 0 baseline | read-only Gate-0 PR, contract and schema registry | immediately | none |
| 1 decision freeze | Gate-0 contract proposal/approval memo only | immediately | Owner/contract-owner semantics decisions before writes |
| 2 manifest schema wrappers | `schemas/gate0/source_manifest.json`, `split_manifest.json`, corresponding tests | after Task 1 | independent file owner |
| 3 metric schema | `schemas/gate0/metrics.json`, corresponding tests | after Task 1 | independent of Task 2 |
| 4 intervals, labels, status | `schemas/gate0/gold_events.json`, `window_sample_manifest.json`, producer tests | after Task 1 | exclusive Gate-0 producer owner |
| 5 ranking and run evidence | `schemas/gate0/ranked_candidates.json`, `run_manifest.json`, `runtime_and_failure_ledger.json`, producers/tests | after Task 1; serial with Task 4 if same producer | shared `src/gate0/execution.py` single writer |
| 6 source-use boundary | `src/gate0/media_experiment.py`, `src/gate0/media/{probe,decode}.py` + tests | immediately for design/reproduction; code under scoped agreed API | independent of schema files |
| 7 final 13/13 and acceptance | `scripts/verify-gate0.py`, Gate-0 integration tests, documentation report | after 2–6 | only after schema/producer freeze |

No arbitrary eight-agent fan-out. Tasks 2/3 may overlap with Task 6 after design freeze. Tasks 4/5 may overlap only if no shared `execution.py` writer. Task 7 is the joining task.

## Task 0 — Independent baseline and reproduction

**Files:** Read PR #166 and current main, no code writes.

- [ ] **Step 1:** Freeze PR #166 head `d50bc631a4561775cf0bbd332cdde141e169b050`, current source identities and the approved Gate-0 experiment spec; verify backup SHA.
- [ ] **Step 2:** In an isolated worktree of that PR's candidate, run `PYTHONPATH=src python -m pytest tests/gate0 -q`, record Python/tool versions and exact count (historic report: 622; do not assert until rerun).
- [ ] **Step 3:** Generate disposable test MP4s using the committed fixture builder and execute the ten-stage Gate-0 generated-media workflow; run `python scripts/verify-gate0.py --schema-payloads` with required candidate-root arguments from `--help`. Capture actual 13 per-artifact statuses and exit code. Expect eight failures at historical head, but verify rather than hardcode that number.
- [ ] **Step 4:** For each failing payload, document the literal JSON Pointer discrepancy, the exact producer, source of governing authority, classification `IMPLEMENTATION_DEFECT` / `CONTRACT_DELTA` / `UNDECIDED`. Confirm schema registry exactly lists 13 artifacts.

## Task 1 — Adjudicate D1–D8 before shared-contract implementation

**Files:** A narrow decision memo under `docs/agent-runs/YYYY-MM-DD-g0-schema-closure/` on its own branch or within planned controlled integration; don't rewrite the historic proposal.

- [ ] **Step 1:** Trace D1–D8 literal proposals to current frozen spec/CANONICAL contracts and the live producer; confirm especially the three undecided semantics listed above.
- [ ] **Step 2:** Publish exact before/after schema JSON Pointers and typed record examples; choose only outcomes already governed by authoritative spec without widening.
- [ ] **Step 3:** Request explicit Owner decision for remaining truly discretionary semantics; mark `DECISION_PENDING` rather than manufacturing a green path.
- [ ] **Step 4:** Record a signed-off/Owner-reviewed contract-owner determination as the task's prerequisite for Tasks 2–5; if any changes alter the Gate-0 frozen protocol rather than align an implementation, stop for architectural approval.

## Task 2 — D6 manifest document shape

**Files:** `schemas/gate0/source_manifest.json`, `schemas/gate0/split_manifest.json`, corresponding `tests/gate0/` schema tests.

- [ ] **Step 1 (RED):** Assert `{"records":[...]}` with exact expected record envelopes is admissible, malformed nested record/unknown field is refused and JSONL record envelopes remain unchanged.
- [ ] **Step 2:** Define closed wrappers with `$defs/record` and required `records`; preserve `source_manifest.revision_ids` semantics as authorized. Do not change source identity hashes just to align a fixture.
- [ ] **Step 3 (GREEN):** Run schema tests against actual produced manifest documents; review and commit owned files.

## Task 3 — D7 frozen metric identifiers

**Files:** `schemas/gate0/metrics.json`, focused metrics tests.

- [ ] **Step 1 (RED):** Assert exact `hit_at_10.metadata`, `hit_at_10.semantic`, `paired_lift.semantic_minus_metadata`, family and absent-query diagnostics validate; illegal whitespace/unknown metric names still refuse.
- [ ] **Step 2:** Implement the approved metric-id pattern or explicit enum at the exact metric schema field, **not** a global generic-ID relaxation.
- [ ] **Step 3 (GREEN):** Revalidate actual metrics and frozen IDs, commit.

## Task 4 — D2/D3/D4 typed interval, uncertainty and status

**Files:** `schemas/gate0/window_sample_manifest.json`, `schemas/gate0/gold_events.json`, `src/gate0/temporal.py` / `labels.py` only if justified; focused tests.

- [ ] **Step 1 (RED):** Test closed `sample_target` vs `typed_interval` union, exact rational interval/uncertainty values, canonical eight time domains, duplicate interval-id refusal and precise sampling-status vocabulary.
- [ ] **Step 2:** Align schema fields first under the adjudicated contract. Producer status changes (`SUCCEEDED→SELECTED`, `MISSING_PTS→MISSING`) and unique per-revision/window IDs require explicit frozen identity review and golden regeneration, not a search/replace.
- [ ] **Step 3 (GREEN):** Run typed-interval/label integration tests, compare canonical record/digest changes to admitted contract and commit.

## Task 5 — D1/D5 ranking, identity, blinding and egress

**Files:** `schemas/gate0/ranked_candidates.json`, `run_manifest.json`, `runtime_and_failure_ledger.json`, `src/gate0/execution.py` (exclusive), tests.

- [ ] **Step 1 (RED):** Invalid arm/window/interval identity, missing required context, fake metadata representation, extra run-manifest attributes, vacuous `EGRESS_BLOCKED` event and unknown failure vocabulary each refuse; valid frozen producer objects pass.
- [ ] **Step 2:** Apply adjudicated D1/D5 schema and corresponding producer changes. Preserve `arm_id`, distinct metadata vs semantic representation, `blinding.access_scope` owner decision and required `decision/outcome` on blocked egress; choose exactly which manifest extensions belong to the canonical document.
- [ ] **Step 3 (GREEN):** Run payload validator per touched artifact, all applicable Gate-0 ranking/ledger tests and commit. Do not delete apparently redundant fields until the canonical reference owner has decided their destination.

## Task 6 — Origin/protection and bounded media processing

**Files:** `src/gate0/media_experiment.py`, `src/gate0/media/probe.py`, `src/gate0/media/decode.py`, `tests/gate0/media/`, synthetic fixture builder if needed.

- [ ] **Step 1 (RED):** A manually relabeled `media-corpus.json` containing an arbitrary existing local file must *not* prove `GENERATED_ON_HOST` from the JSON field alone. Test symlink-in-root, symlink-swap during process, out-of-root path, hardlink where protected source policy disallows, oversized media, source mutation and digest mismatch: all refuse without incomplete published evidence.
- [ ] **Step 2:** Specify and implement only the minimal trustworthy generated-fixture provenance (e.g. an in-process controlled generator/manifest identity plus digest-bound source set and accepted synthetic fixture root). A declarative generator name can be preserved as provenance input but must remain `UNVERIFIED` if producer identity is not independently established. Any real non-generated source must use the existing precise source authorization policy and distinct REAL-scope entrypoint; do not blur gates.
- [ ] **Step 3:** Replace unrestricted whole-file `read_bytes()` on the admitted fixture path with quota-bounded, no-follow regular-file handles, hashing without mutating media; bind initial and final source inode/size/digest facts as appropriate. Keep FFprobe process caps/timeouts and reject mutated/unreadable files.
- [ ] **Step 4 (GREEN):** Positive disposable generated-MP4 run plus all negative scope/size/symlink tests; record exact stage no-output behavior, memory envelope and source immutability; no claim of full production hostile-media defense.

## Task 7 — Final 13/13 closure + report

**Files:** Gate-0 integration tests, verifier corrections only if proven, immutable execution report.

- [ ] **Step 1:** Execute generated-media ten-stage chain to completion with source hash/probe PTS and fake embedding evidence; preserve `report` exit 20 / `NOT_RUN` because corpus is synthetic.
- [ ] **Step 2:** Run `scripts/verify-gate0.py --schema-payloads` against **actual generated-media candidate artifacts**, with 13 named artifact statuses and **13/13 PASS**; closure/foreign keys still PASS. Run negative malformed payload/duplicate/unknown-event tests.
- [ ] **Step 3:** Run full `PYTHONPATH=src python -m pytest tests/gate0 -q` and current applicable synthetic CI, capture actual counts and negative-path results. Use independent reviewer to inspect schema identity changes against authority and source boundary; address blockers.
- [ ] **Step 4:** Produce a focused PR with immutable commit SHA and separate proposal-to-approved contract mapping; **do not merge automatically**. The WBS only advances for exact verified *synthetic capability*; G0.1.5/G0.2/G0.3 authentic experiment and G0.4 Gate decision remain open.

## Owner/authority state

- **APPROVED DIRECTION:** reconcile source/schema drift without weakening fixed experiment, correct declared-generated boundary and bounded source handling, proceed through separate Gate-0/Gate-3 lanes.
- **UNDECIDED / DO NOT SILENTLY IMPLEMENT:** metadata representation ontology, blinding-access literal, exhaustive `run_manifest` canonical keys, and any D1–D8 field that materially changes frozen contract rather than repairing inconsistency.
- **NOT_AUTHORIZED:** live archive, authentic model, provider/network, Gate promotion, production render/export, destructive Git or backup modification.

Ship no fake PR to occupy a worker. If Decision 1 remains open, continue Task 6 (once bounded design is reviewed), but leave Tasks 2–5 `BLOCKED_OWNER_DECISION` where appropriate. Evidence and dependency discipline outrank agent utilization.
