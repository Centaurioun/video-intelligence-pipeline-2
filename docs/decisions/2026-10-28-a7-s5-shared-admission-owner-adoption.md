# A-7 S5 Shared Source Admission — Owner Adoption Decision

**Decision status: ARCHITECTURAL CONTRACT ADOPTED — IMPLEMENTATION NOT AUTHORIZED — PRODUCTION ADMISSION BLOCKED PENDING EVIDENCE.**

**Decision date:** 2026-10-28
**Decision authority:** Repository Owner’s explicit D1–D7 disposition in the Goal that requested this record; bounded to A-7 S5.
**Decision base:** `main@a31c9e79e851515a8c74e67301b27bc4bee56fa3`
**Architecture proposal:** PR #252, signed proposal commit `ae421720e689211306b7112fe54e506b98fc1341`, integrated by merge commit `fffec44e709ae485fb7eac52b1e322546c992b5d`.
**Contract-owner proposal:** PR #253, signed proposal commit `8561a6c7a26f4a41906d32bda1bab37b83c17463`, integrated by merge commit `a31c9e79e851515a8c74e67301b27bc4bee56fa3`.

This record adopts the bounded architectural dispositions below. It does not rewrite either integrated proposal, which remains historically marked `PROPOSED`. It authorizes no source implementation, executable implementation plan, production resource limit, real-media or native-tool operation, rendering/export, provider/model activity, or Gate promotion.

## Adopted D1–D7 dispositions

| Decision | Owner disposition | Adopted boundary |
|---|---|---|
| **D1 — Shared E01/S5 source admission** | **ADOPT** | Within one admission operation, E01 authoritative source-native timing remeasurement and S5 structural stream-identity verification use the same complete, bounded, expected-SHA-256-verified, genuinely immutable source byte view. No partial admission, unbounded read fallback, alternate locator substitution, or mutable-buffer alias is permitted. Named-byte and persisted-measurement-artifact paths retain existing evidence requirements. |
| **D2 — Timing-parser pre-allocation safety** | **ADOPT NARROW PARSER-SAFETY PRINCIPLE AND EXPLICIT FROZEN EXCEPTION IN PRINCIPLE ONLY** | The minimum exception to the integrated P-2 `container.py`/timing prohibition and T1–T11 freeze covers only `_parse_stts`, `_parse_ctts`, `parse_iso_bmff_timing_bytes`, and directly required sample-budget argument plumbing. Count preflight precedes all per-sample allocation; one source-wide cumulative budget applies; `ctts` is not double-counted against `stts`; malformed, inconsistent, unsupported, or over-budget inputs fail closed; accepted source-native PTS/timebase values and public result shape remain compatible; S5 adds no timing parse. This does not authorize code writes or adopt a numeric production ceiling. |
| **D3 — Authoritative E01 compatibility** | **ADOPT** | An internal byte-oriented E01 route may be designed only if it preserves every authoritative requirement and refusal of `is_binding_eligible`. The public predicate remains authoritative and unchanged. Structural-only eligibility, caller timing arrays, self-declared digests, unresolved persisted artifacts, and guessed or substituted locators never grant binding authority. |
| **D4 — Historical ReviewBundle behavior** | **ADOPT** | Separate structural record validation, external snapshot/E01 revalidation, fresh operation-scoped S5 admission, and consumer permission. Structurally valid historical V1/V2/V3 records with unavailable external dependencies may load as unverified; malformed or tampered records remain rejected. V3 external snapshot failure ordering is explicitly within this intended compatibility change. Sealed bytes, schemas, digests, and receipts remain unchanged. `current_e01_validated` remains E01-only. No serialized S5 state is allowed. |
| **D5 — Descriptor-based bounded admission** | **ADOPT FAIL-CLOSED PRINCIPLE; DEFER PLATFORM SUPPORT LIST** | Source/artifact admission must use bounded descriptor-based reads, regular-file checks, pre-read size checks, adopted parent/final path-component no-follow policy, and same-buffer digest verification. Unsupported symlink/reparse semantics, non-regular files, oversize, mutation, truncation, and digest mismatch fail closed; no weaker fallback is permitted. The result proves only the immutable bytes admitted and consumed in that operation, not filesystem immutability or later pathname identity. No operating system is yet approved for production admission. |
| **D6 — Operation-scoped consumer enforcement** | **ADOPT** | Fresh S5 admission is required wherever stream identity is consumed for a binding decision: HumanDecision creation and resume; real-plan single-selection and multi-selection admission; each selection’s lineage revalidation; and local-preview admission. Every independently bound selection is checked independently. No stale, cached, serialized, or inherited S5-success boolean grants permission. A later renderer/FFmpeg/native pathname reopen is a separate identity boundary and is not proven or authorized here. |
| **D7 — Production resource limits** | **DEFER PRODUCTION LIMITS** | `PRODUCTION_RESOURCE_BUDGET = PENDING_EVIDENCE`. No unlimited source admission is allowed while finite supported limits are pending. Candidate values below are synthetic diagnostic/test parameters only, not production maxima or defaults. |

## Frozen authority and evidence boundaries

The adopted D2 exception is deliberately narrow and in principle only. Before any implementation, a separate exact scope must identify the finite sample budget, API/signature, refusal mapping, every directly affected parser caller, and exclusive source/test paths. No unrelated Gate-3 timing behavior is opened. The existing `is_binding_eligible` contract remains authoritative; this decision does not approve changes to `refinement.py` until an exact implementation scope is granted.

A-12/P-11 amendment PR #251 remains in force: S5 may inspect only the permitted ISO-BMFF structural identity metadata (`moov/trak/tkhd`, and video-handler `trak/mdia/hdlr`) from the digest-verified source bytes. No additional FFmpeg/FFprobe call, timing-table parse in S5, new PTS/timebase calculation, edit-boundary derivation, schema/evidence/receipt/sealed-record field, or evidence-strength promotion is adopted. `PRODUCER_SEALED` is not independent probe/source-pairing proof; `demuxer_build_state=NOT_OBSERVED` remains unchanged. Source-native PTS/timebase remains authoritative.

The Owner has not adopted a supported OS list. Reported macOS final-component `O_NOFOLLOW` prototype evidence does not establish parent-component safety, cross-platform equivalence, or production filesystem guarantees. A platform remains unavailable for production admission until its path, descriptor, race, and resource guarantees are independently validated.

## Resource evidence and pending limits

The reported synthetic diagnostics from `/tmp/vip_s5_diag/` are limited apparatus evidence and were not independently rerun for this adoption. They demonstrated sample-count-driven allocation amplification on small synthetic ISO-BMFF fixtures; they do not establish workload distributions, safe maxima, or production capacity.

The following values remain test candidates only:

| Parameter | Synthetic candidate only | Adopted production limit |
|---|---:|---|
| Source bytes | 256 MiB | None — pending evidence |
| Total timing samples | 250,000 | None — pending evidence |
| Probe JSON | 16 MiB | None — pending evidence |
| Refinement JSON | 16 MiB | None — pending evidence |
| ReviewBundle JSON | 8 MiB | None — pending evidence |
| Probe stream rows | 4,096 | None — pending evidence |
| JSON nesting depth | 64 | None — pending evidence |
| Process peak memory | 512 MiB | None — pending evidence; not a proven combined upper bound |

In particular, a 256 MiB mutable source buffer plus a full immutable copy could transiently consume 512 MiB before parser allocations, interpreter overhead, and JSON object graphs. These candidates have not been shown jointly compatible. Production use remains blocked until workload evidence and combined synthetic peak-memory tests support finite settings.

## Implementation remains blocked

This adoption does not authorize S5 code or tests. Before a later, separately authorized TDD implementation, the following remain required:

1. Evidence-backed finite source, sample, probe, refinement, bundle, row/depth, and process-memory budgets, plus combined peak-memory validation.
2. Supported-platform/path-component policy and synthetic tests for parent/final symlinks, non-regular files, growth, truncation, mutation, replacement, and immutable-buffer behavior.
3. Complete bounded source-read-path inventory covering named-byte and persisted-artifact E01, snapshot verification, ReviewBundle/refinement/probe artifacts, and downstream revalidation.
4. Exact E01 byte-oriented internal interface and caller inventory that preserve public `is_binding_eligible` semantics.
5. Exact parser-call plumbing and compatible refusal mapping for the narrow D2 exception.
6. Explicit V1/V2/V3 synthetic regression design, including V3 unavailable-snapshot loading as unverified and rejection of malformed/tampered records.
7. Fresh per-consumer S5 tests for HumanDecision create/resume, preview, real-plan single/multi-selection, and lineage, without any serialized S5 authorization state.
8. A separate implementation authorization naming the exact source/test paths, scope, stop conditions, and review requirements.

No source, tests, schemas, receipts, sealed records, historical decisions, frozen specifications beyond the D2 exception-in-principle disposition above, WBS, Atlas, source media, or production tooling are changed or authorized by this record. S5 implementation remains blocked; production admission remains blocked pending evidence.
