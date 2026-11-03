# A-7 P2 Governance Reconciliation — Conditional Owner Decision

**Status:** Owner decision recorded; durable adoption is pending integration of PR #239. The Repository Owner explicitly assumes the bounded contract-owner responsibilities below. This record does not implement A-7, authorize real-media execution, or promote a Gate.

**Canonical base:** `f59657db3a52b09f3988b8144c11bc1a0ada4854` (2026-10-28). The draft was prepared on an isolated branch from this exact commit.

**Owner decision (2026-10-28):** The Repository Owner approved Option 2 in PR #239 and expressly assumes accountability, for this bounded A-7 P2 implementation only, for the A-7, Gate-3, fixture, A-5, A-12/IT-6, and A-1/Root-G contract-owner decisions identified in P-1, P-2, P-3, P-4, P-5, P-7, P-8, P-11, and P-12. The Owner adopts the exact P2 rule in the existing readiness packet §3 and approves the P-8 correction proposed in this PR. Technical constraints and the S1–S5 path set remain unchanged. P-11 and P-12 are accepted only to the extent supported by existing contracts and code; a contradiction blocks the affected slice. This direction is recorded here but must be durably adopted through PR #239 before implementation begins.

## Adopted P2 rule and scope

Adopt or reject, for A-7 only, the existing readiness packet §3 rule: for an unfragmented ISO-BMFF source with `N >= 2` direct `moov/trak` children and `N` FFprobe streams, establish correspondence only when every `streams[i].id` is canonical valid lowercase `0x` hexadecimal equal to the structurally valid `tkhd.track_ID` of `traks[i]`, all IDs are usable and unique, and the selected position is in range and is video on both sides. Re-derive the relation from digest-bound source bytes and the digest-verified persisted probe artifact under the packet's `PRODUCER_SEALED` source/probe pairing label. Refuse on any missing, malformed, mismatched, ambiguous, or unsupported fact. Ordinal equality, stream-count equality, handler heuristics, and box-order plausibility alone never prove identity.

The rule adds no timing authority. Source-native PTS/timebase evidence remains the only basis for source temporal bounds; VFR endpoints must not be derived from seconds times nominal FPS. Existing A-9 origin-zero edit-list behavior remains unchanged. No schema, sealed-evidence field, receipt field, probe argv, refusal namespace, verifier, local-preview behavior, or production trust state changes are proposed.

## Authority and role-identity findings

Before the Owner's explicit decision below, the current repository identified accountable roles but did not bind them to named people or record a delegation appointing the Repository Owner. The latest Owner decision resolves role identity for this bounded packet by expressly assuming those responsibilities; this is direct Owner authorization, not an inference from prior authorship:

- The A-7 readiness packet §6 assigns P-1 to “Owner + A-7 contract owner”; P-2 to “Owner + Gate-3 contract owner”; P-3 to “Owner + Gate-3 fixture owner”; P-4 to “Contract owner”; P-5 to “A-7/A-11 contract owner”; P-7 to “A-5 contract owner”; P-8 to “Gate-3 contract owner”; P-11 to “A-12/IT-6 contract owner”; P-12 to “A-1 contract owner”. These are role labels, not identity or delegation records.
- `docs/agent-runs/2026-10-25-g3-cprime-v1/authority-disposition-matrix.md` assigns decisions to Owner/contract-owner roles and records A-7 as pending. It does not name an A-7, Gate-3, fixture, A-12, A-1, or Root-G contract-owner delegate.
- `AGENTS.md`, `src/gate3/AGENTS.md`, `docs/architecture/CANONICAL_CONTRACTS.md`, and `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md` state repository and technical boundaries but do not appoint those contract owners.
- No repository `CODEOWNERS` file or current delegation record assigning these roles was found in the canonical tree.
- The Owner's 2026-10-28 direction explicitly states that the Repository Owner also assumes the listed contract-owner responsibilities for this bounded implementation. No concurrence is inferred from authorship of prior packets or the independent AI review.

### ADR-0003 reconciliation

ADR-0003 removes ordinary development branch/path source-authorization enforcement and prohibits replacement administrative grants, witnesses, or equivalent blockers. No branch/path grant is required here. The Owner's explicit bounded role assumption and decision resolves the earlier contract-owner identity/concurrence condition; ADR-0003 itself neither grants nor removes that A-7 decision. Technical evidence, parser-boundary, schema, and source-immutability protections remain in force. P2 is adopted at Owner/contract-owner decision level; implementation must wait for this decision and the P-8 correction to be durably integrated.

## Consolidated prerequisite dispositions

| ID | Accountable authority in existing records | Evidence at canonical base | Disposition | Exact scope / boundary |
|---|---|---|---|---|
| P-1 | Repository Owner acting as A-7 contract owner for this packet | Owner's explicit 2026-10-28 role assumption; readiness packet §3; historical matrix A-7 `(c) PENDING` | **APPROVED and adopted at decision level; durable integration PENDING.** | Exact P2 predicate above only; no guessed mapping. |
| P-2 / B-9 | Repository Owner acting as Gate-3 contract owner for this packet | Owner's explicit decision; readiness packet §6 | **APPROVED; durable integration PENDING.** | Exactly one new pure module `src/gate3/stream_identity.py` for structural `tkhd.track_ID` validation and cross-namespace predicate. No edits to `container.py`, timing code, schemas, or unrelated Gate-3 modules. |
| P-3 / B-7 | Repository Owner acting as Gate-3 fixture owner for this packet | Owner's explicit decision; readiness packet C-10 and plan S1 stop guards | **APPROVED; durable integration PENDING.** | `src/gate3/fixturegen.py` plus only the two fixture digest constants named in readiness packet C-10 / plan S1. Stop if any additional byte pin changes or any other fixture delta is required. |
| P-4 / B-3 | Repository Owner acting as A-7 contract owner for this packet | Owner's explicit decision; readiness packet §3 and §6 | **APPROVED; durable integration PENDING.** | Re-derive only. No sealed evidence, schemas, persisted record formats, receipts, or plan fields may change. |
| P-5 / B-5 | Repository Owner acting as A-7/A-11 contract owner for this packet | Owner's explicit decision; readiness packet §5 and §6 | **APPROVED; durable integration PENDING.** | Bind-time adapter and ReviewBundle validation only, subject to P-11. No shared verifier or `local_preview.py` changes. |
| P-7 / B-4 | Repository Owner acting as A-5 contract owner for this packet | Owner's explicit decision; readiness packet §6 | **APPROVED; durable integration PENDING.** | Reuse existing refusal interfaces; no new public refusal namespace or diagnostic prose treated as contract. |
| P-8 | Repository Owner acting as Gate-3 contract owner for this packet | Exact missing path verified absent; current general evidence/PTS/scope controls survive elsewhere; Owner explicitly approves the proposed AGENTS correction | **APPROVED; durable integration PENDING.** | Proposed AGENTS-only wording change in this PR. Do not invent missing contract content; retain a stop if a task depends on absent Candidate B directives. No branch/path grant or Owner Witness is introduced. |
| P-9 | Implementing Lead | At this revision, local main and origin/main were synchronized to `f59657db3a52b09f3988b8144c11bc1a0ada4854`; exact relevant source/contract anchors were rechecked | **SATISFIED for this revision; repeat before implementation dispatch.** | Reconfirm exact source anchors and base before implementation. |
| P-11 | Repository Owner acting as A-12/IT-6 contract owner, subject to existing contract | Authority matrix A-12 authorizes consumption-time digest/verbatim re-check only and says no second full parse; A-7 plan S5 adds a metadata-only `moov/trak`/`tkhd` source scan in ReviewBundle; current `review_bundle.py` does not perform that scan | **LIMITED ACCEPTANCE DOES NOT AUTHORIZE S5. S5 BLOCKED pending resolution of the scope contradiction.** | S5 may proceed only if a current contract supports this extra metadata scan or a separate explicit contract amendment resolves the “digest/verbatim-binding re-check only” bound. Do not implement S5 or an alternate consumer path while unresolved. |
| P-12 | Repository Owner acting as A-1/Root-G contract owner for this packet | Root-G boundary prohibits adding a container parse inside `real_source_service.py`; current service calls `refine_retrieval_candidate`, and the existing adapter calls `parse_iso_bmff_timing` in `refinement_adapter.py`; planned S4 passes probe artifact metadata but adds no parser call to the service | **APPROVED NARROWLY; durable integration PENDING.** | S4 may pass the authorized probe artifact path/digest through the existing adapter call. Keep parsing in `refinement_adapter.py`; any new `parse_iso_bmff_timing` or other container-parser call in `real_source_service.py` is outside approval and blocks S4. |

## P-8 correction and integration gate

The Owner approves changing only the stale pre-read reference and its dependent Candidate B sentence in `src/gate3/AGENTS.md`. The exact patch appears in this PR. “Task authorization and scope” means user/Owner task direction, not a branch/path administrative grant or Owner Witness removed for ordinary development by ADR-0003. The patch does not introduce a replacement grant gate or claim that the missing Candidate B map has been recovered. It preserves T1–T11 freeze, source-native PTS/VFR, provenance, immutability, synthetic/local scope, TDD, and task ownership. The P-8 correction is not effective until PR #239 is accepted through the required integration process.

No S1–S5 implementation may start until this Owner decision and the P-8 AGENTS correction are durably adopted through integration of PR #239. Independent review and CI are still required; the prior GitHub Actions infrastructure failure is not a passing test result. Even after integration, P-11 continues to block S5 unless the A-12 scope contradiction is resolved. P-12 authorizes only the existing adapter parse path and no parser call added to `real_source_service.py`.

## Exact implementation-plan path set if prerequisites are later completed

This is the existing plan's source/test boundary, recorded to prevent scope drift. It is not a write authorization while the dispositions above remain pending.

| Slice | Planned files | Boundaries |
|---|---|---|
| S1 fixture conformance | `src/gate3/fixturegen.py`; `tests/gate3/test_fixturegen_tkhd_conformance.py`; `tests/vip_fvs/unit/test_source_snapshot_temporal_single_read.py` | Only the two named digest constants in the existing test file may be rebased; stop on any additional pin change. |
| S2 fact/predicate | `src/gate3/stream_identity.py`; `tests/gate3/test_stream_identity_mapping.py` | Exactly one new pure, stdlib-only Gate-3 module; no I/O. |
| S3 shared gate | `src/vip_fvs/stream_identity_gate.py`; `tests/vip_fvs/test_stream_identity_gate.py` | Sole file-I/O gate; verify probe artifact file digest and derive track count from source bytes. |
| S4 bind | `src/vip_fvs/refinement_adapter.py`; `src/vip_fvs/real_source_service.py`; `tests/gate3/test_stream_namespace_safety.py`; `tests/vip_fvs/test_stream_identity_bind.py` | Adapter call path only. Retain current multi-track refusal when proof is absent. |
| S5 ReviewBundle | `src/vip_fvs/review_bundle.py`; `tests/vip_fvs/test_review_bundle_stream_identity.py` | Metadata-only `tkhd` scan if and only if P-11 is accepted; never parse timing tables here. |

No other source, test, schema, fixture pin, verifier, preview, probe argv, receipt, plan, or evidence files are in this proposed slice. The plan's named new tests are required for TDD but do not authorize changes to unrelated existing expectations.

## Implementation boundary after genuine dispositions

Only after PR #239 is durably integrated may S1–S4 proceed, and only under their listed path scopes and RED→GREEN stop guards. S5 remains blocked by P-11 unless its metadata-only scan is explicitly supported by an applicable current contract or the A-12 scope is amended. No alternate consumer path is authorized. S6 verifier hardening, S7/B-11 probe self-binding, A-5/A-6 composition, IT-8, preview/render/export, real media, model/provider activity, reindexing, snapshots, and Gate promotion remain excluded. Preserve the two-pin fixture stop guard, source immutability, and independent review requirements.

## Remaining disposition and stop rules

The earlier separate-role condition for P-1, P-2, P-3, P-4, P-5, P-7, P-8, P-11, and P-12 is resolved by the Repository Owner's explicit bounded role assumption and decision. The remaining technical scope issue is P-11: A-12 is documented as digest/verbatim-binding re-check only, while S5 proposes an additional metadata-only source scan. The Owner has accepted P-11 only to the extent current contracts support it; they do not clearly authorize the added scan, so S5 stays blocked. Resolving that boundary requires a separate authoritative A-12 contract amendment or explicit narrowing of the S5 implementation plan, not inference from this Owner decision. No real-media rerun, model/provider activity, new snapshot, reindexing, render/export, Gate promotion, or merge is authorized here.
