# A-7 S5 Contract-Owner Adoption Decision Proposal

**Status: PROPOSED — NOT ADOPTED; NO IMPLEMENTATION AUTHORITY**
**Canonical base:** `main@693d8052df201627caa8a72afc2682d6c138c294`
**Companion architecture proposal:** PR #252, head `ae421720e689211306b7112fe54e506b98fc1341`
**Scope:** Owner/contract-owner decision text for the bounded S5 shared-source-admission design. This document does not change code, tests, schemas, receipts, sealed records, frozen specifications, WBS, Atlas, media, or Gate state.

This is a decision instrument for review. Its recommendations are not current contracts until an authorized Owner/contract owner explicitly adopts the applicable quoted text. Even adoption of architectural direction does not authorize implementation, production resource limits, real media, native tools, rendering, export, or Gate promotion.

## 1. Verified review basis and authority

### 1.1 Baseline and PR #252

- **VERIFIED:** Live GitHub `main` is `693d8052df201627caa8a72afc2682d6c138c294` (tree `39a1624960fa39b6e89aa598a9fe7d11e7e20ea9`).
- **VERIFIED:** PR #252 is open and Draft at expected head `ae421720e689211306b7112fe54e506b98fc1341`, based on `main`. It adds exactly `docs/decisions/2026-10-28-a7-s5-shared-source-admission-architecture-proposal.md`.
- **VERIFIED:** PR #252’s recorded independent review says `READY_FOR_ADOPTION_REVIEW, NOT_ADOPTED / NOT_IMPLEMENTATION_READY`. It accepts the shared bounded/digest-verified immutable-byte direction as coherent while requiring exact dispositions for frozen surfaces, historical V3 loading, resource budgets, consumer boundaries, and no-unbounded-read proof. It also warns that S5 binds only the bytes consumed by that check; later preview/render/native reopening is a separate identity boundary.
- **VERIFIED:** PR #239 merged at `10399a8b102c6062762640cb1b57adc2c98584db`, and that merge is an ancestor of this main. The bounded Owner role assumption in `docs/decisions/2026-10-28-a7-p2-governance-reconciliation.md` is therefore durably recorded.
- **VERIFIED:** The P2 record says the Repository Owner assumes the A-7/Gate-3/fixture/A-5/A-12/IT-6/A-1/Root-G contract-owner responsibilities for the **bounded A-7 P2 implementation only**, for listed P-1/P-2/P-3/P-4/P-5/P-7/P-8/P-11/P-12 decisions, and only insofar as existing contracts and code support them. It explicitly says a contradiction blocks the affected slice. This is not a general delegation to rewrite frozen Gate-3 contracts.
- **VERIFIED:** A-12/P-11 amendment PR #251 is integrated in the baseline. It permits S5’s named, expected-digest-verified source-byte read for `moov/trak/tkhd` and video-handler `hdlr` inspection, while barring extra FFmpeg/FFprobe, timing-table reparse, new PTS/timebase/edit-boundary derivation, evidence/schema/receipt/sealed-record changes, and promotion of `PRODUCER_SEALED` or `NOT_OBSERVED` claims. It sets no numeric limit and grants no code or plan authority.
- **VERIFIED:** S1–S4 are present on this main. The original S5 implementation plan names only `review_bundle.py` and a new ReviewBundle identity test, and requires no timing parser in S5. The broader shared-admission design exceeds that two-file implementation boundary.

### 1.2 Current frozen/shared source facts

The following exact-baseline source facts constrain this decision:

- `src/gate3/AGENTS.md:7` freezes T1–T11.
- `docs/decisions/2026-10-28-a7-p2-governance-reconciliation.md` P-2 expressly allowed the pure `src/gate3/stream_identity.py` module but said no `container.py`, timing-code, schema, or unrelated Gate-3 edits. P-11 was accepted only where existing contracts support it; contradiction blocks S5.
- `src/gate3/container.py::_parse_stts` (`:91`) expands run counts into per-sample values; `_parse_ctts` (`:96`) expands composition runs. `parse_iso_bmff_timing_bytes` (`:155`) subsequently builds timing arrays and sorts presentation timestamps. A small file can therefore encode a large work/allocation count.
- `parse_iso_bmff_timing_bytes` accepts already materialized bytes; `parse_iso_bmff_timing(path)` (`:202`) reads the path. The byte API enables sharing but is not by itself a bounded admission contract.
- `src/gate3/refinement.py::_remeasured_facts` (`:337`) handles `named_bytes_remeasured` by path-based timing parse and `persisted_measurement_artifact` by reading the artifact, resolving declared bytes, and remeasuring. `is_binding_eligible` (`:461`) remains the authoritative predicate and must not be replaced by structural eligibility.
- `src/vip_fvs/stream_identity_gate.py::require_bound_stream_identity` (`:170`) currently reads source bytes and, for multiple tracks, probe bytes/JSON. The pure `require_stream_identity` accepts already materialized source bytes.
- `src/vip_fvs/source_snapshot.py::_open_regular_nofollow` (`:300`), `_read_snapshot_bytes` (`:328`), and `verify_snapshot_evidence` (`:1056`) are separate file-admission/verification paths. Snapshot verification can independently reopen/hash source bytes.
- `ReviewBundle._validate_payload` (`src/vip_fvs/review_bundle.py:107`) performs V3 snapshot evidence validation. `_resolve_artifact_identity` (`:322`) invokes the persisted refinement and authoritative E01 validation; `from_record` (`:400`) catches revalidation failures only after envelope/payload validation. A V3 snapshot failure can therefore fail before the existing “current E01 unvalidated” result is returned.
- `human_decision.py:create_human_decision` (`:130`) and `resolve_human_decision_resume` (`:283`) currently require `current_e01_validated`; this property is E01-specific. `local_preview.py::_render_multi_plan_preview` (`:556`) reloads each bundle and rechecks E01 before continuing. `real_plan.py::build_real_edit_plan_from_selections` (`:477`) checks each selection’s pins and authoritative refinement; lineage variants are at `:580` and `:595`. These are distinct seams for fresh S5 enforcement.
- Timing-parser callers also include source snapshot temporal binding (`source_snapshot.py:746,854`), refinement and adapter paths (`refinement.py`, `refinement_adapter.py`), persisted artifact verification (`container.py:268`), and other Gate-3 helpers such as QC, verification, coordinator, and discriminating code. A parser limit cannot be treated as S5-local without identifying and preserving these callers’ contracts.

These are source-inspection findings, not runtime test results.

## 2. Decision table

| Decision | Recommended disposition | Contract-level recommendation | Remaining gate |
|---|---|---|---|
| **D1 Shared E01/S5 source admission** | `RECOMMENDED_FOR_NARROW_ADOPTION` | Adopt same bounded, digest-verified, genuinely immutable source view for E01 authoritative remeasurement and S5 within one operation; preserve public E01 semantics and named/persisted paths. | Exact file/API implementation scope is separately authorized after frozen-surface decisions. |
| **D2 Frozen timing parser/sample bound** | `BLOCKED_BY_CONTRACT` | Require a pre-allocation whole-source sample budget, counted before any expansion; preserve values for accepted inputs. | T1–T11 freeze and P-2 no-`container.py`/timing-edit boundary must be explicitly amended. No numeric production ceiling is adopted here. |
| **D3 E01 authority compatibility** | `RECOMMENDED_FOR_NARROW_ADOPTION` | Permit an internal byte-oriented route only if it runs the same authoritative E01 checks and keeps `is_binding_eligible` behavior unchanged. | Exact interface and parser-caller ownership must be separately granted. |
| **D4 Historical V1/V2/V3 loading** | `RECOMMENDED_FOR_NARROW_ADOPTION` | Structurally valid sealed records with unavailable external dependencies may load only as unverified; malformed/tampered records still reject. Preserve bytes/schema/receipts and E01-only flag meaning. | Explicitly disposition V3 snapshot-load behavior; it differs from current validation order. |
| **D5 Descriptor/path/platform policy** | `DEFERRED_PENDING_EVIDENCE` | Require descriptor-relative no-follow admission and fail closed where equivalent guarantees are unavailable. Do not silently downgrade. | Current evidence does not qualify a full supported OS/path-component set. macOS-only initial support is a limited option, not a verified platform contract. |
| **D6 Fresh consumer enforcement** | `RECOMMENDED_FOR_NARROW_ADOPTION` | Require fresh operation-scoped S5 at each binding consumer; no serialized/reusable S5 boolean. | Rendering/native reopening is a separate, unapproved source identity boundary. |
| **D7 Production resource budgets** | `DEFERRED_PENDING_EVIDENCE` | No bounded production admission without adopted resource limits; no unlimited fallback when a limit is unknown. | Workload distributions and combined memory tests are absent. Set `PRODUCTION_RESOURCE_BUDGET = PENDING_EVIDENCE`. |

No row is adopted by publication of this proposal.

## 3. D1 — Shared source admission

### Proposed contract wording

> For one ReviewBundle admission operation, E01 authoritative timing remeasurement and S5 structural stream-identity verification shall consume the same complete source byte view. The source shall be opened through the adopted descriptor-based policy, admitted only after file-type and pre-read size checks, read within an explicit cap, and SHA-256 verified over the exact bytes supplied to both consumers. Failed or partial admission supplies no bytes and grants no permission. No unbounded path-read fallback, alternate locator substitution, or mutable byte alias is allowed. The public `gate3.refinement.is_binding_eligible` predicate, source-locator binding, evidence-digest checks, selected-stream rules, timing enumeration, and refusal semantics remain authoritative and unchanged. Named-byte and persisted-measurement-artifact paths both use this same admission result. S5 does not invoke a second timing-table parse; the one existing E01 timing remeasurement remains the sole source-native timing interpretation in the operation.

Minimal API responsibility (not frozen signature/class naming):

- Admit one named source against its expected digest and required resource limits.
- Produce a complete immutable/read-only byte view with its measured SHA and length only after every check succeeds.
- Allow the authoritative E01 implementation to validate the existing evidence using that view without introducing a second eligibility predicate.
- Allow S5 to inspect only A-12 structural metadata from that same view and apply the existing positional `require_stream_identity` predicate for multi-track inputs.
- Return a typed fail-closed result for missing/oversize/non-regular/mutated/digest-mismatched/malformed inputs; never return a partially trusted view.

Named-byte E01 uses its current source locator and selected stream. Persisted-artifact E01 must validate the bounded artifact, preserve declared source-locator resolution and source digest binding, and remeasure its named bytes from the same admitted view. Merely accepting a syntactically valid artifact digest is insufficient.

The invariant is one shared source byte view **for E01 plus S5**, not a claim that the entire load has one total source read. Snapshot validation may still independently read the snapshot; until it is explicitly adapted, that read must have its own bound and be reported. Probe, refinement, ReviewBundle and manifest bytes need separate bounded artifact admission.

## 4. D2 — Frozen parser protection and exact proposed ruling

### Proposed contract-owner text

> **Gate-3 timing parser sample-budget amendment — proposed, not adopted.** For every source admitted to `parse_iso_bmff_timing_bytes`, validate timing-table counts in a preflight pass before allocating any per-sample list. The admission budget is a single cumulative sample ceiling for the entire source parse, summing decoded sample counts from every timing-bearing direct `trak` processed by the parser. Within each `trak`, the `stts` run counts define that track’s sample count. If a `ctts` table exists, its expanded run total must equal the same track’s `stts` total; it is not counted a second time against the source-wide ceiling. Use checked accumulation (`count > limit - total` before addition) so integer overflow or attacker-declared counts cannot wrap. Reject malformed, unsupported, mismatched, or over-budget tables before expansion. Do not truncate, clamp, infer, or partially parse. Keep existing malformed-table refusal classes and accepted source-native PTS/timebase results unchanged; over-budget data fails closed through the existing unsupported/unmeasurable `ValueError` surface unless a separate public refusal taxonomy is explicitly adopted. Do not add an S5 timing parse.

> This rule applies to the complete parser call, not only the selected track, because current `parse_iso_bmff_timing_bytes` parses timing-bearing tracks before selecting one. The preflight must inspect every timing table relevant to that call before the expansion pass begins. Existing direct callers must receive the same explicit finite budget or a centrally adopted finite policy; there is no unlimited default. Existing public function result shape and accepted-input values remain unchanged. Historical frozen tests and unrelated Gate-3 callers must be inventoried and run; any changed accepted result, new refusal on an in-budget valid fixture, or unrelated contract failure blocks the change.

**No production ceiling is selected.** 250,000 samples is a reported synthetic candidate only. The current parser can expand a 32-bit count from a tiny source; it cannot safely rely on source bytes as a proxy for sample count.

**Frozen boundary:** this ruling conflicts directly with `src/gate3/AGENTS.md` T1–T11 freeze and the integrated P-2 statement “no edits to `container.py`, timing code.” Before implementation, the Owner/contract owner must explicitly amend those exact constraints for `_parse_stts`, `_parse_ctts`, `parse_iso_bmff_timing_bytes`, and any directly dependent callers. This proposal does not make that amendment effective. Callers to inventory include `refinement.py`, `refinement_adapter.py`, `source_snapshot.py` temporal binding, `verified_measurement_artifact`, and other existing timing consumers. The TDD scope must not opportunistically change those consumers beyond passing the adopted finite budget and preserving their contracts.

## 5. D3 — Authoritative E01 compatibility

### Proposed contract-owner text

> A byte-oriented internal E01 route may be introduced solely to let the existing authoritative check consume already-admitted source bytes. The public `is_binding_eligible(record)` remains the authority and keeps its current result semantics. The internal route must execute the same structural eligibility, `_byte_authority_covers`, source digest and locator checks, selected stream/time-domain checks, timing remeasurement comparisons, evidence-digest validation, and reorder/DTS evidence requirements. `is_structurally_eligible` alone is never binding authority. Caller-provided PTS/timing arrays, a self-asserted digest string, or a persisted artifact whose named bytes do not resolve and remeasure cannot create authority.

> For `named_bytes_remeasured`, remeasure the current named source bytes through the existing byte-oriented timing parser and preserve the declared locator/digest identity. For `persisted_measurement_artifact`, bounded-read and validate the artifact, resolve only its declared source paths under existing locator semantics, remeasure the admitted bytes, and compare every authoritative fact. Both paths must converge on the same authoritative E01 rules; neither may silently substitute a matching-digest alternate path or weaken mismatch refusals.

The exact internal function/API and the migration of `_remeasured_facts`, `_resolved_byte_source_path`, and `verified_measurement_artifact` require a separate scoped decision. Because P-2 prohibited timing-code changes, this proposal cannot authorize edits to `src/gate3/refinement.py` or indirectly authorize new public eligibility behavior.

## 6. D4 — Historical ReviewBundle compatibility

### Proposed contract-owner text

> ReviewBundle validation shall distinguish (1) structural envelope/schema/canonical-byte/record-digest/dependency-digest validation, (2) current external snapshot and E01 revalidation, (3) fresh operation-scoped S5 stream-identity admission, and (4) permission for binding/editorial consumption. Structurally malformed or digest-tampered records remain rejected. Structurally valid historical V1/V2/V3 sealed records whose external source, snapshot, refinement, or probe dependencies are unavailable may be returned as readable but unverified; no missing evidence creates binding or editorial authority. Historical sealed bytes, schemas, and receipts are not rewritten. `current_e01_validated` continues to mean current E01 byte-authority revalidation only and never means S5 succeeded. No persisted S5 field, new schema, or receipt is added. Consumers requiring binding reject unless current E01 and the required fresh S5 admission both succeed.

This differs from current V3 behavior: `_validate_payload` calls `verify_snapshot_evidence` during payload validation. In `from_record`, this occurs before the catch that turns `_resolve_artifact_identity` failure into `_current_e01_validated=False`. Therefore a valid sealed V3 record with a missing/corrupt external snapshot may throw during loading today rather than return unverified. The proposed disposition deliberately changes that loader compatibility behavior while preserving tampered-record rejection. It needs explicit adoption; it is not implied by A-12 or by a general “historical records stay unchanged” statement.

Required synthetic regression families:

- V1/V2/V3 structurally valid and dependencies valid: existing load and current E01 success behavior unchanged.
- V1/V2/V3 structurally valid, external source/snapshot/probe/refinement dependency unavailable: record bytes unchanged, readable unverified result, `current_e01_validated=False`, no S5 permission.
- Each version malformed schema, noncanonical bytes where canonicality is required, record/dependency digest tampered, or payload identity altered: reject; do not classify as mere external unavailability.
- V3 snapshot validation order failure is caught only at the external-validation stage; structural digest/schema failures still reject before that stage.
- No mutation of sealed bytes and no schema/receipt additions.

## 7. D5 — Descriptor, path and platform boundary

### Proposed contract wording

> Source, probe, refinement and other decision-bearing artifacts shall be admitted as regular files through descriptor-based reads. Enforce the adopted path-component policy for both parent and final components; reject symlinks/reparse points rather than following them. Check the opened object with `fstat` and reject non-regular files. Check initial descriptor size against its finite cap before allocating a content buffer or reading content. Read no more than the admitted size/cap in bounded chunks. Refuse truncation, growth/size change, detected concurrent mutation, file identity inconsistency, or expected-digest mismatch; expose no partial buffer. Hash the exact immutable bytes consumers parse. If the platform cannot enforce the required parent/final no-follow semantics, admission fails closed. Never silently fall back to `Path.read_bytes()` or a weaker path check.

> The guarantee applies to the bytes admitted and consumed by that operation: the returned source bytes are complete, immutable to consumers, and match the expected SHA-256. A held descriptor pins the opened object during that operation; path replacement afterward does not retarget that descriptor. This does not establish that a pathname still resolves to the same inode later, does not prevent another process from writing the open inode, and does not bind a later renderer/native tool that reopens the path. Strong filesystem immutability or later-path identity requires a separate immutable snapshot/locking/staging contract.

### Platform disposition

- **VERIFIED only for a limited prototype observation:** on the reported macOS synthetic run, final-component `O_NOFOLLOW` rejected a symlink with `ELOOP`; FIFO refusal and controlled growth/truncation/digest cases were exercised by a temporary prototype.
- **NOT_OBSERVED:** descriptor-relative parent-component symlink protection, concurrent writer races, file replacement race, Windows reparse-point semantics, Linux behavior, and production filesystem guarantees.
- **Recommendation:** adopt the fail-closed capability rule, not a claim of cross-platform equivalence. If an initial supported-platform list is needed, macOS-only is the narrowest candidate for further validation, but is not yet proven because parent-component policy and supported filesystem behavior remain untested. Linux/Windows must be unsupported and fail-closed until each has equivalent implementation and synthetic race/path tests. Do not silently disable `O_NOFOLLOW` or follow reparse points.

## 8. D6 — Operation-scoped S5 enforcement and later reopening

### Proposed contract-owner text

> Whenever a binding decision consumes stream identity, require a fresh S5 admission within that operation, against the current named source/probe artifacts and expected digests. No serialized, cached, lineage-inherited, or reusable S5-success boolean grants later authority. Keep current E01 eligibility, current S5 identity admission, and consumer-specific permission as distinct predicates. HumanDecision creation and resume, single-selection real-plan admission, each member of multi-selection plan admission, each lineage revalidation, and preview admission must fail closed if the required current S5 operation cannot succeed. Multi-selection applies the check independently to every source/bundle before combining placements; no selection inherits another’s result. Existing single-track compatibility and S2 positional multi-track identity remain unchanged.

> S5 proves the identity relation only for the bytes admitted and parsed by that operation. A later preview/render/FFmpeg/FFprobe/native step that reopens a pathname is a separate source-read boundary and is not proven to consume those same bytes. It requires its own separately adopted identity check or an explicitly designed content handoff; this decision does not authorize native rendering, actual media execution, or a claim of renderer-consumed byte equivalence.

Current `HumanDecision` gates E01 only, and its sealed lineage pins bundle/refinement/source identities; these are not fresh S5 proof. `build_real_edit_plan_from_selections` verifies each selection’s authoritative refinement but presently has no S5 operation. Multi-preview reloads every bundle and checks E01 before invoking later tool setup; this does not bind later pathname reads. The contract proposal must therefore cover each member at the relevant consumer seam, while downstream native reopening remains out of scope.

## 9. D7 — Resource budgets and evidence rule

Candidate values below are authorized **only as synthetic test parameters**, not defaults, production maxima, or accepted workload assumptions:

| Parameter | Synthetic test candidate | Production disposition |
|---|---:|---|
| Source bytes | 256 MiB | `PENDING_EVIDENCE` |
| Total timing samples | 250,000 | `PENDING_EVIDENCE` |
| Probe JSON | 16 MiB | `PENDING_EVIDENCE` |
| Refinement JSON | 16 MiB | `PENDING_EVIDENCE` |
| ReviewBundle JSON | 8 MiB | `PENDING_EVIDENCE` |
| Probe stream rows | 4,096 | `PENDING_EVIDENCE` |
| Process peak memory | 512 MiB | `PENDING_EVIDENCE`; not a proven combined upper bound |
| JSON nesting depth | 64 | `PENDING_EVIDENCE` |

The reported 20,000-sample synthetic parser observations show allocation amplification but do not validate a 250,000-sample ceiling. Probe results cover a shaped JSON fixture, not production distributions. Measurements were reported from `/tmp/vip_s5_diag/` and were not independently rerun for PR #252 or this proposal.

A 256 MiB mutable source buffer followed by a full 256 MiB immutable copy could transiently consume 512 MiB before parser lists, interpreter, JSON objects, or other buffers. Therefore the proposed 256 MiB source candidate and 512 MiB process candidate cannot be treated as a compatible memory guarantee. The implementation must either prove a no-duplicate materialization path or choose smaller source limits / a larger measured process envelope. `tracemalloc` and process RSS must both be measured, and combined worst-accepted cases must be tested.

Production source/probe/refinement/bundle distributions, valid sample maxima, JSON depth/row distributions, path/platform properties, and combined memory peaks are unmeasured. Until sufficient authorized workload and synthetic capacity evidence supports finite production settings:

```text
PRODUCTION_RESOURCE_BUDGET = PENDING_EVIDENCE
```

Pending does not mean unlimited: source-consuming S5 implementation and production use remain blocked until finite limits are selected and enforced before read/allocation/parse.

## 10. Exact future ownership matrix

This is a proposed later TDD ownership map, not a current write grant.

| Path | Classification | Proposed role / authority boundary |
|---|---|---|
| `src/vip_fvs/review_bundle.py` | `REQUIRED` | Separate structural validation, current external E01/snapshot validation, S5 admission, and consumer-ready operation result; preserve historical bytes and E01 flag meaning. |
| `src/vip_fvs/stream_identity_gate.py` | `REQUIRED` | Consume the admitted source view; bounded probe admission; retain S2 positional predicate and single-track compatibility. |
| `src/vip_fvs/human_decision.py` | `REQUIRED` | Fresh S5 requirement for create/resume where identity binds editorial authority; no persisted S5 boolean. |
| `src/vip_fvs/local_preview.py` | `REQUIRED` | Revalidate every relevant selection at preview admission; later tool reopening remains separate. |
| `src/vip_fvs/real_plan.py` | `REQUIRED` | Revalidate every selection independently before single/multi-selection binding plan admission and lineage use. |
| `tests/vip_fvs/test_review_bundle_stream_identity.py` | `REQUIRED` | Synthetic S5, bundle and operation-scope tests. |
| `tests/vip_fvs/unit/test_human_decision.py` | `REQUIRED` | Create/resume and lineage stale-authority refusals. |
| `tests/vip_fvs/unit/test_local_preview.py` | `REQUIRED` | Single/multi-selection fresh admission and refusal paths; do not execute native media here. |
| `tests/vip_fvs/unit/test_real_plan.py` and relevant adversarial plan tests | `REQUIRED` | Per-selection and lineage admission regressions, synthetic only. |
| `src/gate3/container.py` | `FROZEN / CONTRACT-OWNER AUTHORIZATION REQUIRED` | Exact pre-allocation count preflight in `_parse_stts`, `_parse_ctts`, parser call budget and refusal semantics. Explicit T1–T11/P-2 amendment required. |
| `src/gate3/refinement.py` | `FROZEN / CONTRACT-OWNER AUTHORIZATION REQUIRED` | Internal byte-view E01 path only if it invokes the identical authoritative rules; no public predicate change. Explicit P-2/frozen-interface amendment required. |
| `src/vip_fvs/source_snapshot.py` | `CONDITIONAL` | Only if snapshot verification must share admitted bytes or strengthen descriptor/read limits. Snapshot contract-owner decision required; otherwise keep separate bounded pass and disclose I/O. |
| `tests/gate3/test_stream_identity_mapping.py` | `REQUIRED` | Preserve S2 positional identity, malformed `tkhd`, unsupported structure and single-track boundary. |
| `tests/vip_fvs/test_stream_identity_gate.py` | `REQUIRED` | Preserve digest-bound probe/source behavior and fail-closed gate contracts. |
| `tests/vip_fvs/unit/test_source_snapshot.py`, `test_source_snapshot_temporal_single_read.py`, temporal-v2 and safety tests | `CONDITIONAL` | Required if snapshot read/admission behavior or parser budget caller interface changes. |
| `src/vip_fvs/refinement_adapter.py`, `src/vip_fvs/real_source_service.py`, `src/vip_fvs/real_source_probe.py` | `OUT_OF_SCOPE` | No producer argv, bind-time S4, probe publication, or source service behavior change in this S5 consumer decision. Any need requires a separate explicit scope. |
| Schemas, receipts, sealed records, historical decisions, frozen specifications, source media, Atlas, WBS | `OUT_OF_SCOPE` | Must remain unchanged under this proposal. |
| Renderer/native tools, FFmpeg/FFprobe, providers/models, export/Gate state | `OUT_OF_SCOPE` | No execution or authority granted. |

File ownership for implementation must be split so no concurrent writers share these paths. Shared-contract files remain with the explicitly designated contract owner; no parallelism or narrow TDD scope removes their approval requirement.

## 11. Adversarial disposition

| Failure condition | Required resolution / current status |
|---|---|
| E01 reads source before S5 admission | Shared admission must be the first source-byte consumer for that operation; otherwise the guarantee is false. **BLOCKING until implementation traces all paths.** |
| `stts`/`ctts` expands before budget check | Two-pass count validation before any expansion, cumulative per source. **Frozen-contract amendment required.** |
| Mutable alias escapes | Return immutable bytes/read-only interface with no writable backing alias; account for freeze copy. **Must be demonstrated by test.** |
| E01 and S5 see different versions | Same operation-local byte object and same SHA; no independent path reopen between them. |
| Persisted locator is substituted | Resolve only declared source locator under existing binding semantics; no “any path with same digest” fallback. |
| Snapshot verification rereads outside limits | Adapt to the admitted bytes or retain a separately bounded and explicitly counted read. **Owner decision and test required.** |
| Valid historical record gains authority while dependency missing | Return unverified; E01 false and no S5/consumer permission. **Changes V3 current behavior; explicit adoption required.** |
| Tampered record mislabeled as unavailable | Structural schema/canonical/digest checks precede external availability handling; tampered input rejects. |
| Single-track compatibility removed | Preserve existing accepted one-track path and its limited evidence meaning; regression test required. |
| Multi-track positional identity weakened | Keep exact S2 positional equality; no ordinal, count-only, handler heuristic or guessed mapping. |
| Later renderer reopens source under stale S5 | S5 grants only operation-local identity; renderer read is separate, not covered or authorized here. |
| Synthetic cap becomes production limit by implication | Candidate table is test-only; production remains `PENDING_EVIDENCE`. |
| General Gate-3 callers change under S5 | Explicitly inventory callers; parser cap is a frozen shared contract delta, not hidden in S5 scope. |

No additional defect is asserted beyond these source-backed boundaries.

## 12. Exact Owner/contract-owner adoption instrument

The following is the proposed instrument for the Owner/contract owner to accept, reject, or amend. Its adoption would settle architecture direction only for the text explicitly selected; it would not silently approve code changes or production limits.

> **Decision title:** A-7 S5 Shared Source Admission and Consumer Contract — bounded adoption.
>
> **Authority basis:** The Repository Owner’s contract-owner role assumption in the merged A-7 P2 governance record is limited to the bounded A-7 decisions and existing-contract support stated there. This decision expressly addresses the additional S5 boundaries below; PR #251 alone does not authorize them.
>
> **Adopt D1:** Within a single ReviewBundle admission operation, existing authoritative E01 timing remeasurement and S5 structural stream-identity validation shall consume the same complete bounded, expected-SHA-256-verified, genuinely immutable source byte view. No partial admission, mutable alias, unbounded fallback, or alternate locator substitution is permitted. Named-byte and persisted-measurement-artifact E01 paths retain all current locator, evidence digest, selected stream, timing, and refusal requirements. Public `is_binding_eligible` semantics remain unchanged. S5 performs no timing-table parse, new PTS/timebase computation, edit-boundary derivation, or FFmpeg/FFprobe invocation.
>
> **Adopt D3:** An internal byte-oriented E01 path may be used only if it applies the same authoritative rules as `is_binding_eligible`; structural eligibility, caller-supplied timing facts, or a syntactically valid persisted digest alone never grants binding authority.
>
> **Adopt D4:** Structural record/schema/canonical digest validation, external snapshot/E01 revalidation, operation-scoped S5 admission, and consumer permission are separate. Malformed/tampered records remain rejected. Structurally valid historical sealed V1/V2/V3 records with unavailable external dependencies may load only as unverified and may not gain binding/editorial authority. Their bytes, schemas and receipts remain unchanged. `current_e01_validated` retains E01-only meaning; no persisted S5 field or receipt is added. This explicitly changes the current V3 failure boundary where snapshot verification may throw during payload validation, and requires compatibility regression tests before implementation.
>
> **Adopt D6:** Where a consumer uses stream identity for binding, HumanDecision creation/resume, each real-plan selection/lineage, and preview admission require fresh S5 verification within that operation. No serialized or reusable S5 success state grants later permission. S5 only establishes the bytes consumed by its own check. A later renderer/native tool reopening a source path is a separate source-identity boundary and is not covered by this decision.
>
> **Adopt the D2 principle but not a numeric limit:** Every timing-table expansion must first validate a finite, overflow-safe source-wide sample budget before allocating per-sample arrays. The per-track `ctts` total must equal its `stts` count and is not double-counted. In-budget accepted inputs retain identical source-native timing values; malformed/unsupported/over-budget input fails closed. No production ceiling is selected by this instrument. Because this changes frozen T1–T11 and the integrated P-2 “no container/timing edits” boundary, the Owner explicitly amends those exact frozen clauses only for `_parse_stts`, `_parse_ctts`, `parse_iso_bmff_timing_bytes`, and directly dependent call-budget plumbing. No other Gate-3 timing redesign is included. A separate exact implementation scope and refusal mapping must be approved before code work.
>
> **Adopt the D5 fail-closed rule; defer platform list:** A supported platform must enforce regular-file and parent/final no-follow admission, pre-read size checks, bounded descriptor reads, mutation/truncation detection, immutable materialization, and same-buffer digest verification. Platforms lacking equivalent guarantees refuse admission. There is no fallback that follows symlinks or uses an unbounded path read. macOS-only initial support may be considered after parent-component tests; Linux and Windows remain unsupported until equivalence is measured and verified. Filesystem immutability and identity of a path at a later operation are not claimed.
>
> **Defer D7 production values:** `PRODUCTION_RESOURCE_BUDGET = PENDING_EVIDENCE`. The values 256 MiB source, 250,000 samples, 16 MiB probe/refinement, 8 MiB ReviewBundle, 4,096 probe rows, 512 MiB process peak, and JSON depth 64 are synthetic test candidates only. No unlimited admission is allowed while production limits remain pending. Production resource adoption requires workload distributions and combined peak-memory synthetic capacity evidence; specifically demonstrate compatibility of source buffer, immutable freeze, parser arrays and JSON object graph under the proposed process cap.
>
> **No implementation authority:** This decision does not authorize an executable plan, code/tests, schema/receipt/sealed-record changes, S4 producer changes, native rendering, FFmpeg/FFprobe, authentic/protected media, models/providers, export, or Gate promotion. A separate later grant must name exact writable paths, implementation behavior, synthetic test scope, and stop conditions. Historical evidence strength remains unchanged: `PRODUCER_SEALED` is not independent source/probe proof, and `demuxer_build_state=NOT_OBSERVED` stays unchanged.

### Adoption response fields

The Owner/contract owner should record one explicit disposition per item: D1, D2 principle/frozen amendment, D3, D4, D5 fail-closed rule/platform list, D6, and D7 production limits. Accepting architectural direction does not accept a numeric budget. Any rejected or narrowed item must identify the affected consumer and the resulting fail-closed behavior. No silence, merge, or PR #251 approval substitutes for these dispositions.

## 13. Remaining implementation blockers and next step

An executable S5 TDD plan remains blocked until:

1. D2’s exact frozen T1–T11/P-2 exception, sample-count semantics, and over-limit refusal surface are expressly adopted; a finite production sample limit is separately justified.
2. D3’s internal byte-oriented E01 route is granted without weakening `is_binding_eligible`, with all path-resolving and timing-parser callers inventoried.
3. D4’s V3 unverified-load behavior is explicitly accepted and its structural-versus-external error boundary is testable.
4. D5’s supported platform/path-component policy is chosen and synthetic parent/final symlink, reparse-point, growth, truncation, mutation, replacement, and immutable-buffer tests define the guarantee.
5. D6’s consumer list and later source-reopening boundary are explicitly adopted; no native/render equivalence is inferred.
6. D7 workload evidence and combined capacity tests establish finite production settings, or S5 production use remains blocked.
7. A separate implementation authorization assigns the exact file set and synthetic TDD scope. This document itself grants none.

**Proposed decision status:** `READY_FOR_OWNER_ADOPTION_REVIEW` for the bounded contract choices above; **NOT_ADOPTED**, **NOT_IMPLEMENTATION_READY**, and **NOT_AUTHORIZED** for implementation or production use.
