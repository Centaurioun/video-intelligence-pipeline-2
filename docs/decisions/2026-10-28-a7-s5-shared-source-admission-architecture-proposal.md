# A-7 S5 Shared Source Admission — Architecture Decision Proposal

**Status: PROPOSED — NOT YET ADOPTED AS FROZEN IMPLEMENTATION AUTHORITY**
**Baseline:** `main@693d8052df201627caa8a72afc2682d6c138c294`
**Scope:** Architecture contract proposal for Gate-3 A-7 S5 ReviewBundle consumption.
**Out of scope:** Implementation plan, code/test/schema/receipt changes, real or protected media, FFmpeg/FFprobe, providers, exports, and Gate promotion.

This proposal records a preferred implementation direction and the additional contract-owner decisions it needs. It does not amend or extend the adopted A-12/P-11 decision by itself. A-12/P-11 PR #251 is already adopted on the baseline and remains authoritative for its stated S5 metadata-read scope and prohibitions.

## 1. Proposed decision

Adopt a shared, bounded, digest-verified source admission boundary for ReviewBundle E01 remeasurement and S5 structural stream-identity verification, subject to the additional decisions in §8.

1. Open the named source through a descriptor-based admission policy, reject unsupported path/file types and over-limit files before content allocation/read, read within a fixed cap, and verify SHA-256 over exactly the bytes later consumed.
2. Expose one genuinely immutable byte view to both the existing authoritative E01 remeasurement logic and S5. The implementation must not expose a mutable backing buffer through an alias. If immutable freezing copies the buffer, that temporary peak must be included in the budget.
3. Preserve the public `is_binding_eligible` predicate and all of its evidence, source-locator, digest, timing, and refusal semantics. Any internal byte-oriented entry point must call the same authoritative rules; it must not create a weaker eligibility predicate.
4. Bound total `stts`/`ctts` sample expansion before allocating per-sample lists. Inputs over the adopted sample ceiling fail closed. For accepted inputs, source-native PTS/timebase values and E01 interpretation remain unchanged.
5. Separate structural ReviewBundle record/schema/digest validation from external snapshot/E01 revalidation, S5 admission, and permission to consume binding/editorial evidence.
6. Revalidate S5 at each binding consumer operation. Do not serialize or reuse a stale S5 authorization boolean.
7. HumanDecision creation and resume, preview, and real-plan admission must not bypass successful operation-scoped S5 admission where that consumer relies on the stream identity binding. Existing refusal paths remain fail-closed.
8. Preserve historical sealed V1/V2/V3 bytes and existing schemas/receipts. Do not add evidence fields, receipts, or sealed-record changes under this proposal.
9. Preserve `probe_source_binding=PRODUCER_SEALED` and `demuxer_build_state=NOT_OBSERVED`; producer assertion and artifact digest do not independently prove source/probe invocation pairing.
10. S5 reads only the A-12-permitted ISO-BMFF structural metadata (`moov/trak/tkhd`, plus `trak/mdia/hdlr` for video handler). It does not parse timing tables, calculate PTS/timebase, create edit boundaries, or invoke FFmpeg/FFprobe. The existing S4 bind-time check and its negative paths remain intact.

## 2. Evidence and provenance

### 2.1 Baseline source facts independently reverified against GitHub

At the baseline SHA:

- `gate3/container.py::_parse_stts` expands each run count into a per-sample list; `_parse_ctts` also expands run counts. `parse_iso_bmff_timing_bytes` builds timing arrays and sorts presentation values. A source byte limit alone therefore does not bound sample-driven allocation or CPU.
- `parse_iso_bmff_timing_bytes` accepts bytes-like input, so a shared byte view is technically possible without changing the parser’s source-native calculation. `parse_iso_bmff_timing(path)` reopens and reads the path.
- `gate3/refinement.py::is_binding_eligible` is the authoritative E01 predicate. Persisted-measurement verification can resolve named paths via `_resolved_byte_source_path`, hash them, and remeasure them through another path read.
- `vip_fvs/stream_identity_gate.py::require_bound_stream_identity` reads source bytes and, for multi-track inputs, probe bytes and JSON. The pure `gate3.stream_identity.require_stream_identity` accepts the already-materialized source bytes.
- `vip_fvs/source_snapshot.py::verify_snapshot_evidence` performs separate source/manifest opens and digest verification. It is not automatically deduplicated by a shared E01/S5 buffer.
- V3 ReviewBundle validation can verify external snapshot evidence before artifact revalidation has been converted into an unverified-load result. Historical unverified loading is therefore not assumed to work as proposed until the load boundary is changed and tested.

These statements describe source code at the exact baseline, not runtime tests in this delivery.

### 2.2 Synthetic measurements reported from `/tmp/vip_s5_diag/`

The preceding synthetic-feasibility report supplied the following results. **They were reported by Codex from `/tmp/vip_s5_diag/`; they were not independently rerun for this document.** Environment reported: Python 3.14.9, macOS/Darwin. Timing and JSON cases were each run in three separate processes. `tracemalloc` is Python-traced allocation, not total process memory. macOS `ru_maxrss` is process high-water RSS and is cumulative, not a per-case delta.

| Synthetic timing fixture | Source bytes | Tracemalloc peak | Wall time across three runs |
|---|---:|---:|---:|
| 1 `stts` sample, no `ctts` | 124 | 1,250 B | 0.049–0.063 ms |
| 1,000 samples, no `ctts` | 124 | 97,410 B | 0.444–0.538 ms |
| 10,000 samples, no `ctts` | 124 | 963,106 B | 3.959–4.908 ms |
| 20,000 samples, no `ctts` | 124 | 1,930,946 B | 8.124–10.163 ms |
| 1,000 samples with `ctts` | 148 | 130,516 B | 0.900–1.166 ms |
| 10,000 samples with `ctts` | 148 | 1,288,052 B | 8.781–10.866 ms |
| 20,000 samples with `ctts` | 148 | 2,583,732 B | 17.969–21.091 ms |

The reported process high-water RSS ranged from about 20.8–21.0 MiB at the small cases to about 28.6–29.4 MiB at 20,000 samples with `ctts`; this includes interpreter/process baseline and is not a parser-only measurement.

The reported probe parser used the baseline `_parse_probe_streams` on synthetic JSON:

| Stream rows | JSON bytes | Tracemalloc peak | Wall time across three runs |
|---:|---:|---:|---:|
| 1 | 1,094 | 3,877 B | 0.025–0.035 ms |
| 100 | 5,625 | 22,347 B | 0.087–0.118 ms |
| 1,000 | 48,670 | 339,609 B | 0.976–1.322 ms |
| 4,096 | 200,375 | 1,456,691 B | 4.085–5.132 ms |

The bounded-reader prototype reported, once per case: 1,024-byte input over a 100-byte cap refused as `OVERSIZE`; valid 1,024-byte input admitted and digest-checked; append during the read window refused as `CHANGED_DURING_READ`; truncation refused as `TRUNCATED`; FIFO refused as `NOT_REGULAR`; final symlink refused with macOS `O_NOFOLLOW`/`ELOOP`; wrong digest refused as `DIGEST_MISMATCH`. This was prototype evidence only, not verification of current `source_snapshot.py`, a concurrent-race proof, parent-symlink handling, or cross-platform behavior.

### 2.3 Candidate limits are not production policy

The previous report listed these synthetic test candidates:

- Source: **256 MiB**
- Total timing samples: **250,000**
- Probe/refinement JSON: **16 MiB each**
- ReviewBundle JSON: **8 MiB**
- Probe rows: **4,096**
- Process memory: **512 MiB**

**None is an approved production limit.** The 512 MiB value is not a proven upper bound for the combined configuration. The values were not all capacity-tested together. Source/probe/refinement/bundle production distributions, JSON depth behavior, target OS properties, and peak memory with immutable buffer freezing remain `NOT_OBSERVED`.

A synthetic count of 20,000 used only a 124–148 byte ISO-BMFF fixture; that is evidence of sample-driven amplification, not evidence that 250,000 is a safe or representative ceiling. Production values require workload evidence and synthetic capacity tests that combine source buffers, parser allocations, JSON object graphs, and immutable copies under the proposed process cap.

## 3. Proposed internal admission contract

The following is a contract shape, not an adopted API or implementation instruction:

```python
@dataclass(frozen=True)
class AdmittedSource:
    view: ReadOnlyBuffer
    sha256: str
    byte_length: int
    source_locator: str
    opened_identity: OpenFileIdentity  # operation-local; never serialized

@dataclass(frozen=True)
class AdmissionLimits:
    max_source_bytes: int
    max_timing_samples: int
    max_probe_bytes: int
    max_refinement_bytes: int
    max_bundle_bytes: int
    max_json_depth: int
    max_probe_rows: int
    max_operation_memory_bytes: int


def admit_source(
    *, source_path: Path, expected_sha256: str, limits: AdmissionLimits,
) -> AdmittedSource:
    """Return only after descriptor, type, size, complete read and same-buffer SHA checks."""


def revalidate_e01_with_admitted_source(
    *, artifact: Mapping[str, object], source: AdmittedSource,
    bounded_refinement: ReadOnlyBuffer | None,
) -> E01ValidationResult:
    """Apply the existing authoritative E01 rules to the admitted source bytes."""


def require_s5_identity_for_operation(
    *, source: AdmittedSource, bounded_probe: ReadOnlyBuffer | None,
    refinement: Mapping[str, object], limits: AdmissionLimits,
) -> S5AdmissionResult:
    """Apply only the A-12 structural identity rule; no timing-table parse."""
```

The exact types, error taxonomy, and call graph require implementation design after adoption. Required error classes should distinguish at least `MISSING`, `NOT_REGULAR`, `SYMLINK_OR_UNSUPPORTED_NOFOLLOW`, `OVERSIZE`, `TRUNCATED`, `CHANGED_DURING_READ`, `DIGEST_MISMATCH`, `MALFORMED_CONTAINER`, `MALFORMED_ARTIFACT`, `IDENTITY_UNPROVEN`, and `RESOURCE_BUDGET_EXCEEDED`. Any error returns no admitted view and grants no consumer permission.

### 3.1 Named-byte and persisted-artifact paths

- **Named-byte E01:** admit the declared source once; pass its exact immutable view to the existing byte-oriented timing parser and S5. Run the authoritative E01 predicate through the same evidence rules. Timing remeasurement occurs once.
- **Persisted measurement artifact:** bounded-read and validate the named refinement artifact; resolve only its declared source locator(s) under existing locator/digest semantics; admit the matching bytes once; remeasure and compare the persisted facts through the same E01 rules; give the same source view to S5. Do not let `_resolved_byte_source_path` perform an unbounded pre-read followed by a path-based remeasurement.
- **Snapshot validation:** the source read/hash in `verify_snapshot_evidence` is an independent legacy path. The implementation must either adapt it to verify the admitted bytes while still checking snapshot path/manifest/permissions, or explicitly retain a separate bounded read and report the additional I/O. The record must not claim one total source read if snapshot validation still opens the source separately.
- **ReviewBundle and other JSON:** envelope, refinement, probe, manifest, and bundle reads each require their own byte/depth/row policy. A source cap does not bound these artifacts.

## 4. Descriptor, immutability, and failure contract

The proposed portable policy is fail-closed:

1. Open path components descriptor-relatively where supported; reject parent and final symlinks. Verify the final opened object with `fstat` as a regular file. Use nonblocking open semantics where needed to avoid hanging on special files.
2. If the platform cannot reliably enforce the selected no-follow/reparse-point policy, refuse admission on that platform; do not silently fall back to ordinary path following.
3. Check the opened descriptor’s initial size against the applicable cap before buffer allocation or content read. Read only within the initial admitted size and fixed cap, in bounded chunks. Refuse short read, growth, size/identity change, or digest mismatch. Hash exactly the bytes in the returned view.
4. Do not expose any writable alias to the admitted bytes. If constructing immutable `bytes` duplicates a mutable read buffer, account for both allocations in the peak budget and release the mutable buffer before downstream work where feasible.
5. File replacement after open does not replace the already-open descriptor’s object. It also does not prove that the path still names that object later. Concurrent in-place writes cannot be prevented by ordinary descriptor reads; before/after metadata checks plus same-buffer expected digest reject inconsistent content but do not make the underlying filesystem immutable.
6. On any failure, discard the incomplete buffer. No unbounded `Path.read_bytes()` fallback, alternate locator substitution, guessed stream mapping, or evidence promotion is allowed.

These are required properties to implement and test, not claims that the current snapshot reader already provides them. Filesystem snapshot/locking guarantees beyond descriptor identity require a separate platform/storage assumption and are not adopted here.

## 5. Historical records and operation-scoped consumers

### 5.1 Validation and authority stages

The proposed loader separates:

1. **Structural record validation:** version, closed schema/field rules, canonical representation and record digest. Malformed or tampered records are rejected.
2. **External E01/snapshot revalidation:** current dependencies are re-read under bounded rules. Unavailable/mismatching dependencies result in an unverified state, not altered historical bytes.
3. **Operation-scoped S5 admission:** at each consumer operation, source/probe bytes are freshly admitted and the positional identity predicate rerun.
4. **Permission to consume:** binding/editorial/preview/real-plan operations require their existing E01 requirements plus successful fresh S5 admission where identity binding is relied on.

A structurally valid V1/V2/V3 record with unavailable external dependencies should remain readable as unverified if its structural digest/schema is valid. A malformed/tampered record remains rejected. This is a **proposal**: baseline V3 validation can raise during snapshot verification before the current `from_record` unverified handling, so changing that behavior requires explicit adoption and regression tests.

Historical sealed V1/V2/V3 bytes, schemas, and receipts remain untouched. `current_e01_validated` retains only its current E01 meaning; it must not become an S5 status bit. No serialized S5 result or reusable stale boolean is introduced.

### 5.2 Consumer enforcement

- HumanDecision create and resume must freshly validate the bundle’s E01 and S5 requirements before accepting binding/editorial authority.
- Local preview must repeat admission immediately before preview use; it must not inherit a stale success from a previously loaded bundle.
- Real-plan admission must require current operation-scoped S5 success in addition to the existing E01 authority predicate.
- Any missing source/probe, changed digest, malformed container, positional mismatch, or resource-limit refusal blocks the relevant consumer. Existing fail-closed refusal paths remain.
- Single-track compatibility remains limited to the existing accepted case and does not become independent source/probe pairing proof. `container_path=None`/artifact-only evidence cannot pass source admission for S5.
- `probe_source_binding=PRODUCER_SEALED` and `demuxer_build_state=NOT_OBSERVED` remain exactly at their existing evidence boundary.

## 6. Required, conditional, and forbidden ownership

| File/surface | Ownership in a later authorized implementation | Authority condition |
|---|---|---|
| `src/vip_fvs/review_bundle.py` | **Required:** staged validation/admission orchestration; ephemeral operation-scoped status only. | Historical load semantics require explicit adoption. |
| `src/vip_fvs/stream_identity_gate.py` | **Required:** accept admitted source/probe views instead of reopening paths; preserve S2 predicate and single-track refusal/compatibility. | No new persisted evidence fields. |
| `src/vip_fvs/human_decision.py` | **Required:** create/resume must not bypass fresh S5 admission. | Separate downstream admission decision required. |
| `src/vip_fvs/local_preview.py` | **Required:** fresh S5 revalidation at preview boundary. | Separate downstream admission decision required. |
| `src/vip_fvs/real_plan.py` | **Required:** fresh S5 revalidation at real-plan boundary. | Separate downstream admission decision required. |
| `tests/vip_fvs/test_review_bundle_stream_identity.py` | **Required:** focused synthetic admission and ReviewBundle tests. | No authentic media/native tool tests. |
| `src/gate3/container.py` | **Frozen/shared, separate authorization required:** `stts`/`ctts` pre-allocation sample cap and rejection result; any byte-parser API change. | Gate-3 contract owner must explicitly authorize exact function, behavior, and compatibility surface. |
| `src/gate3/refinement.py` | **Frozen/shared, separate authorization required:** internal byte-oriented E01 eligibility route while preserving public `is_binding_eligible`. | Gate-3/E01 contract owner must approve interface and unchanged predicate semantics. |
| `src/vip_fvs/source_snapshot.py` | **Conditional, separate authorization required:** adapt snapshot verification to admitted bytes or strengthen bounded descriptor semantics. | Snapshot contract owner must approve revalidation/load behavior and any I/O guarantee change. |
| Corresponding refinement, snapshot, container, HumanDecision, preview, and real-plan tests | **Required as applicable:** regression tests with exclusive ownership assigned before implementation. | Synthetic tests only within the later grant. |
| Schemas, receipts, sealed records, historical decisions, frozen specs, WBS, Atlas, source media | **Forbidden in this proposal’s implementation scope.** | No authority to change them. |
| FFmpeg/FFprobe, providers/models, exports, protected media, Gate status | **Forbidden.** | No authority granted. |

The exact later file list must be finalized after the frozen/shared contract decisions. This proposal does not authorize edits to any listed file.

## 7. Synthetic acceptance evidence required later

These criteria are proposed for a later TDD plan; no RED/GREEN run is claimed here:

- Oversized source is refused before allocation or content read; growth cannot exceed the admitted allocation/read cap; truncation, mutation and digest mismatch return no partial admission.
- Parent/final symlinks, FIFO/device/non-regular inputs, and unsupported no-follow platforms fail closed under the adopted OS policy.
- E01 and S5 receive the exact same immutable view and SHA. Named-byte and persisted-measurement paths preserve existing E01 outputs/refusals; the timing parser runs once per operation.
- Sample totals over the cap are rejected before `stts`/`ctts` expansion. At/below cap, source-native PTS/timebase outputs match pre-change synthetic oracles byte-for-byte/value-for-value.
- Probe/refinement/bundle limits are enforced before JSON parsing; maximum depth, row count, digest mismatch, malformed JSON, and malformed boxes refuse deterministically.
- Positional mismatch, duplicate IDs, unsupported `tkhd`, missing/corrupt probe, artifact-only source, and ambiguous structure fail closed; accepted single-track compatibility remains.
- Valid historical V1/V2/V3 sealed bytes are unchanged. Structurally valid but externally unverified records remain unverified and cannot reach HumanDecision, preview, or real-plan binding admission; malformed/tampered records remain rejected.
- Static/runtime guards show no FFmpeg/FFprobe call, no S5 timing-table parse, no new schema/receipt/sealed field, and no source-media mutation.
- Combined synthetic capacity tests measure `tracemalloc` and process RSS separately for source buffer, immutable freeze, timing arrays, probe/refinement/bundle JSON, and worst accepted sample/row/depth configuration. Test fixtures must remain under explicit per-run byte, memory, and time ceilings.

## 8. Contract-owner decisions required before an executable plan

1. **Frozen `gate3/container.py`:** approve the exact total sample cap and pre-allocation refusal semantics for `_parse_stts`/`_parse_ctts`, plus whether any parser API shape changes. Existing accepted source-native timing values must remain unchanged.
2. **Frozen `gate3/refinement.py`:** approve the minimal internal byte-oriented eligibility interface and require that public `is_binding_eligible` semantics/evidence checks remain authoritative.
3. **`source_snapshot.py`:** decide whether snapshot verification may consume the already-admitted bytes while separately validating manifest/path/permissions, or must make an additional bounded read. State the resulting read count and guarantees.
4. **Historical V3:** approve structural readability of a valid sealed record when external snapshot dependencies are unavailable, with `current_e01_validated=False` and no binding/editorial authority; malformed/tampered records still reject.
5. **Platform/path policy:** name supported operating systems and exact parent/final symlink, reparse-point, non-regular-file, and unavailable no-follow behavior.
6. **Consumer authority:** approve operation-scoped fresh S5 admission at HumanDecision create/resume, preview, and real-plan boundaries without serialized S5 booleans.
7. **Resource policy:** approve production source/sample/probe/refinement/bundle/JSON depth/rows/process-memory limits only after workload distribution evidence and combined synthetic capacity tests. The candidate values in §2.3 are not approved.

## 9. Adoption text proposed

> **A-7 S5 shared source admission architecture — proposed adoption:** S5 ReviewBundle consumption shall use a descriptor-admitted, bounded, digest-verified, genuinely immutable source byte view shared with the existing authoritative E01 remeasurement. The public `is_binding_eligible` predicate and its evidence semantics remain unchanged. `stts`/`ctts` sample totals shall be checked before per-sample allocation under an explicitly approved limit, while accepted source-native PTS/timebase results remain unchanged. S5 shall inspect only the A-12-permitted structural metadata and shall not parse timing tables, compute new PTS/timebase or edit boundaries, or invoke FFmpeg/FFprobe.
>
> Structural record validation, external E01/snapshot revalidation, operation-scoped S5 admission, and consumer permission are separate stages. Structurally valid historical V1/V2/V3 records whose external dependencies are unavailable may remain readable only as unverified; malformed/tampered records remain rejected. Historical sealed bytes, schemas, and receipts are unchanged. No reusable serialized S5 authorization boolean is added. HumanDecision create/resume, preview, and real-plan admission require fresh S5 success where stream identity binding is consumed. `PRODUCER_SEALED` remains a producer assertion and `demuxer_build_state=NOT_OBSERVED` remains unchanged.
>
> This architecture adoption does not itself authorize implementation. Separate contract-owner decisions are required for the frozen Gate-3 sample cap and rejection semantics, the byte-oriented internal E01 interface, snapshot verification behavior, historical V3 unverified loading, supported platform/path policy, downstream operation admission, and production resource limits. The numerical values in this proposal are synthetic-test candidates only, not production policy. No schema, receipt, sealed record, source media, provider/native execution, export, or Gate promotion change is authorized.

## 10. Reconsideration and implementation gate

This proposal is ready for Owner/contract-owner adoption review, not implementation. It becomes suitable input to a test-driven implementation plan only after the decisions in §8 are recorded, production resource limits have supporting workload/capacity evidence, and the accepted per-operation consumer contract is exact. Any narrower approval must name the affected frozen surface and its exact behavior; silence or A-12 adoption alone does not authorize those changes.
