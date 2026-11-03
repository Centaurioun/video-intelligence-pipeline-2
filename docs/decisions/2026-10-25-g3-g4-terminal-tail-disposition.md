# Gate-3 `IT-6 (G-4)` terminal-interval / stream-tail disposition — decision, alternatives and execution packet

| Field | Value |
| --- | --- |
| Status | `PROPOSED_DISPOSITION` — documentation only. This document grants nothing and changes no behaviour. |
| Base | `1cf13a3ff7ad4f9e5af5527fe8d19063a001cec0` (`origin/main`, verified at dispatch) |
| Scope owner | Repository Owner (tail policy, A′-7 erratum) + Gate-3 contract owner (claim label, code mapping, version pinning) |
| Supersedes | Nothing. Refines the tracking language in `docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md:247`, `docs/project/01_CURRENT_STATE_AND_HANDOFF.md:17,:25` and `docs/project/CHATGPT_CONTINUITY_START_HERE.md:139`, which call this question "A-12 / IT-6". |
| Evidence lanes | `docs/agent-runs/2026-10-25-g3-a12-tail-duration/lane-1-source-trace.md`, `lane-2-test-and-red-matrix.md`, `lane-3-authority-trace.md` |
| Independent review | Adversarial read-only review at this base (see §12). Two load-bearing defects in the first draft are corrected here: the plan pin **does** carry the full certified record (E10), and consumer re-measurement **exceeds** A-12's recorded bound (design R-8, matrix A-11). Both corrections *shrink* the recommended slice. |
| Prohibitions honoured | No real/protected media executed; no models/downloads; no render/export; no Gate promotion; no frozen-contract change; no destructive Git; no canonical-main write. |

---

## 1. The question, decomposed

The dispatch fuses two independent questions under one label. They have different owners, different
frozen constraints and different blast radii, and only one of them is the "A-12" the design defines.

| # | Question | Governing identifier | Current state |
| --- | --- | --- | --- |
| Q1 (`DC-BIND`) | Must **`SourceSnapshotStore.bind_temporal_authority` (V1)** refuse a source whose `duration_consistency` is `"MISMATCH"`? (the third `xfail(strict=True)`) | No §17 A-number; the tripwire is `tests/vip_fvs/adversarial/test_temporal_evidence_v1_matrix.py:376-400` | Bind is duration-blind by approved design; xfail deliberately RED |
| Q2 (`IT-6 (G-4)`) | May a **`DERIVED_NOT_OBSERVED` stream-tail extent** (`duration_ts`, last PTS + last sample delta) bound a **non-production preview endpoint in V1**, and under what claim label? | `IT-6 (G-4)` — design `:394`, authority matrix `:41` verdict (c) `PENDING` | FVS refuses every terminal interval; no product path can emit one |
| Q3 (`A-12`) | Consumption-time re-verification of **composed** evidence (IT-5) and the Dv-13 rule that composition never hands `refine()` a non-member end | `A-12` — design `:433`, authority matrix `:34` verdict (b) `AUTHORIZED_BY_OWNER_APPROVAL`, **bounded to "digest/verbatim-binding re-check only (design R-8: no new ffprobe, no second full parse)"** | Authorized direction; the additive receipt field still needs Gate-3 contract-owner acceptance |

**Identifier defect (MEASURED, documentation-level).** Commit `30a794013` introduced the alias
"A-12/IT-6" for the tail question. The alias then reached the owner-approved A′-7 record
(`docs/decisions/2026-10-25-g3-a3-aprime7-bounded-owner-decision.md:44,:46`), the WBS, the handoff, a
source comment (`src/vip_fvs/source_snapshot.py:762`) and tests. No crosswalk sentence exists anywhere
in the tree (`NOT_OBSERVED` after a tree-wide grep; the dispatch's "design `:399`" crosswalk is not
present). Semantics were never changed by the alias, but "A-12 PENDING" in the tracker is now
ambiguous between Q1, Q2 and Q3, and the tracker cannot be resolved without the crosswalk in §2.

---

## 2. Naming crosswalk (recommended, label-only)

| Question | Canonical id | Alias to retire | Never renumber |
| --- | --- | --- | --- |
| Consumption-time re-verification of composed evidence + Dv-13 | `A-12` | — | `A-12`, `IT-5` |
| Terminal-interval / stream-tail acceptance | `IT-6 (G-4)` | `A-12/IT-6` | — |
| V1 bind-level duration enforcement (third strict xfail) | `DC-BIND` | `A-12 tail/duration xfail` | — |
| Lane-C owner items | `LC-A-1…LC-A-5` | `A-1…` (collides with the C′ matrix numbering) | — |

`A-13` is `PROPOSED_UNASSIGNED` and must only be minted if the Owner requires a new §17 decision item
for the tail policy itself. Historical run/plan/wave artifacts keep their text and gain a pointer; they
are not rewritten.

---

## 3. Evidence ledger

Classes follow `AGENTS.md` item 6. `MEASURED` here means produced by executing a deterministic command
or by reading the cited line of source at the stated base; `NOT_OBSERVED` is an availability/status
condition, never an evidence class.

| Id | Fact | Class | Basis |
| --- | --- | --- | --- |
| E1 | The GREEN pin and the strict xfail are satisfied **simultaneously**: `1 passed, 27 deselected, 1 xfailed`. | MEASURED | `PYTHONPATH=src:experiments .venv/bin/python -m pytest tests/vip_fvs/adversarial/test_temporal_evidence_v1_matrix.py -k duration_inconsistent -q` (reproduced twice: Lead and independent review) |
| E2 | Baseline trio (`test_temporal_evidence_v1_matrix.py`, `test_source_snapshot_temporal_v2.py`, `tests/gate3`) is stable: `92 passed, 1 xfailed`. | MEASURED | same invocation, full files (reproduced twice) |
| E3 | Frozen `gate3.refinement.refine()` **already implements the tail policy**: a MATCH source with requested end `== duration_ts` yields `end_ticks=160`, `end_is_stream_tail=True`, `extent_state="DERIVED_NOT_OBSERVED"`, `last_frame_extent=None`, `tail_measurement_ref="C2_tail_measurement_reference:…"`, two `uncertainty` records including `C2_tail_measurement_reference` with `derivation="duration_ts - last_pts"`. | MEASURED | probe calling `refine(PtsTable(TimeBase(1,1000),(0,40,80,120)), (0,160), …, container_path=…)` on `build_mp4(media_timescale=1000, sample_deltas=(40,40,40,40))`; writer `src/gate3/refinement.py:618-634` |
| E4 | The same path refuses a MISMATCH source: `blocked="TAIL_NOT_BINDING_ELIGIBLE"`, `extent_state="UNCERTAIN"`. | MEASURED | probe with `declared_duration=999`; predicate at `src/gate3/refinement.py:291-305` |
| E5 | V1 binding never reads `duration_ts`/`duration_consistency`; a MISMATCH source binds 14 fields and round-trips `verify_temporal_authority` (rebind). No MISMATCH refusal token exists in the module. | MEASURED | `src/vip_fvs/source_snapshot.py:679-684,:707-721,:915-940`; tested by `.../test_temporal_evidence_v1_matrix.py:330-373` |
| E6 | V2 binding recomputes `expected_consistency`, refuses only a **lying** label, and seals the genuine MISMATCH as a measured fact (`duration_ts 999`, `"MISMATCH"`); verification rebinds, so a MISMATCH re-seals rather than refusing. | MEASURED | `src/vip_fvs/source_snapshot.py:815-819,:837-858,:942-977`; `tests/vip_fvs/unit/test_source_snapshot_temporal_v2.py:273-290` |
| E7 | The FVS preview path has **two** unconditional terminal-interval refusals, both outside `src/gate3/**`, plus one lossy summary that is **not** the plan pin. | MEASURED | `src/vip_fvs/real_source_service.py:372-384` (`SOURCE_PTS_INTERVAL_NOT_OBSERVED`); `src/vip_fvs/real_preview_verifier.py:384-400` (`STREAM_TAIL_NOT_SUPPORTED`); compact bundle summary at `src/vip_fvs/real_source_service.py:626-650` while the **full record is persisted** at `:651-660` |
| E8 | The preview verifier never reads `end_is_stream_tail`/`extent_state`/`binding_eligible` although the full pinned refinement is in scope and returned by `_authority_from_plan`. | MEASURED | grep empty in `src/vip_fvs/real_preview_verifier.py`; `_authority_from_plan` returns the full mapping at `:53-92` |
| E9 | **Zero** product consumers read the sealed V2 `duration_ts`/`duration_consistency`/`tail_duration_ticks`/`presentation_origin_ticks`. The only readers are `source_snapshot`'s own verifier and tests. The verifier's `"v2"` branch is the sealed *multi-placement preview manifest*, not temporal evidence (`src/vip_fvs/real_preview_verifier.py:223-240`). | MEASURED | repo-wide grep over `src/` |
| E10 | The plan pin carries the **full** byte-bound refinement record, so a product plan **can** carry the tail certification. `_load_authoritative_refinement` re-reads the artifact at `evidence_artifact_ref`, re-verifies `assert_evidence_digest`, requires `is_binding_eligible(record) is True` and equality of refinement_id/source_revision/stream/start/end/timebase; `build_real_edit_plan` embeds `{**full_ref, …}`. `gate3.plan` hashes only `(refinement_id, evidence_digest)` per refinement but serialises the full `pinned_refinements`. | MEASURED | `src/vip_fvs/real_plan.py:252-282` (loader), `:307-317` (`**full_ref`), `:268` (`is_binding_eligible is True`); `src/gate3/plan.py:163,:166` |
| E11 | `tail_end`'s `last_delta_ticks`/`rate_regime` synthesis route has **zero** callers (latent public hazard, never exercised by the product), and an artifact dict that carries `nb_frames`+`duration_ts` but **omits** `duration_consistency` still returns `binding_eligible=True`. | MEASURED (first) / DERIVED from PROBE (second) | `src/gate3/temporal.py:37-50`; call sites only `src/gate3/refinement.py:128`, `src/gate3/verify.py:57`; no test calls `tail_end` |
| E12 | `ffprobe` recomputes duration from sample tables and **masks** an `mdhd` duration edit that the repo parser sees (45000→54000 edit: parser `MISMATCH`, ffprobe still `45000`). | MEASURED (inherited) | Lane-C memo `docs/agent-runs/2026-10-25-g3-dual-temporal-authority/04-stream-tail-and-audio-policy.md`; not re-executed in this packet |
| E13 | `DURATION_CONSISTENCY_NOT_MATCH` (`src/gate3/receipt.py:300`) is referenced by **no** test. | MEASURED | grep over `tests/` |
| E14 | `tail_end` is exercised by **no** direct unit test; the `TAIL_*` codes have zero test coverage. | MEASURED | grep over `tests/` |
| E15 | A plan artifact can carry a full gate3 refinement (fixture path pins `{rid: full}`; bundle path reloads the full record), so a terminal interval is constructible **without** real media for verifier-level testing. | MEASURED | `src/vip_fvs/real_plan.py:468`, `:307-317`; `tests/vip_fvs/adversarial/test_real_preview_verifier_qc.py:134-165` |
| E16 | Reordered/B-frame MATCH bytes are buildable: `build_mp4(sample_deltas=(40,40,80,80), ctts_offsets=(0,80,-40,-40), declared_duration=200)` → pts `(0,40,120,120)`, dts `(0,40,80,160)`, MATCH, tail 80, one duplicate presentation tick. | DERIVED from PROBE (Lane 2) | Lane 2 §2 R3 |
| E17 | The same reordered tables with `declared_duration=240` are a MISMATCH and are pinned GREEN as a single-read V1 bind: `_FROZEN_PARSE` records `duration_ts 240`, `tail_duration_ticks 80`, `pts_ticks (0,40,120,120)`, `duration_consistency "MISMATCH"`. | MEASURED | `tests/vip_fvs/unit/test_source_snapshot_temporal_single_read.py:40-61`, asserted at `:113-343` (unit, not `adversarial/`; `160` is not that fixture's declared duration) |
| E18 | The plan `digest` covers only `(refinement_id, evidence_digest)` per pinned refinement, **not** the record body, so a consume-time re-derivation of the record's own `evidence_digest` is load-bearing for any acceptance that relies on the pin. | MEASURED | `src/gate3/plan.py:163` (digest inputs) vs `:166` (full `pinned_refinements` serialised) |
| E19 | A-12's recorded bound is digest/verbatim-binding re-check only: design R-8 "No second full-source parse outside the snapshot store", and `authority-disposition-matrix.md:34` "Bound it to digest/verbatim-binding re-check only (design R-8: no new ffprobe, no second full parse)". Deriving facts from container bytes inside the verifier is A-11's derivation subset, verdict (c), contract owner (`matrix :33,:74`); IT-8 is `PARKED_BLOCKED` (`docs/decisions/2026-10-25-g3-a3-aprime7-bounded-owner-decision.md:45`). | MEASURED | design `docs/superpowers/specs/2026-10-25-gate3-dual-temporal-authority-composition-design.md:83`; authority matrix `:33,:34,:74` |
| — | No real, authentic or protected media was opened; no VFR or reordered tail was executed at FVS level; `verify_preview` was not executed end-to-end (code-read + existing pins); no Linux/3.14 run was performed for this packet. | NOT_OBSERVED | — |

**Editorial inference, flagged as such:** the recommendation in §6, the label choice in §7 and the
"enabling-only value" judgement in §8.6 are policy judgements, not measurements.

---

## 4. Decision matrix

`P0` = what exists and is enforced today. Every column is evaluated against the evidence above.
Policy labels `P2e`/`P2r` replace the earlier draft's `P2a`/`P2b`; `P2m` is new and is the recommended
target. The mapping is stated so the lane memos and their earlier wording stay traceable.

| | Policy | Admission basis | Safety property actually obtained | Frozen-decision compatibility | Authority needed | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| **P0** | Status quo | Every terminal interval refused (`SOURCE_PTS_INTERVAL_NOT_OBSERVED`, `STREAM_TAIL_NOT_SUPPORTED`, `TAIL_REQUIRES_MEASURED_CONTAINER`) | Ambiguity never reaches a claim; no tail extent can be asserted at all | Fully compatible; deliberate and test-pinned (`test_real_preview_verifier_qc.py:341-357`) | None | **In force now** |
| **P1** | Strict refusal at **binding** (make the xfail GREEN) | V1 `bind_temporal_authority` refuses MISMATCH (optionally V2 too) | Stronger at the storage boundary, but a refusal token makes MISMATCH **unrepresentable**, destroying a legitimate source a future consumer could safely handle | **Incompatible.** A′-7 D-1/D-3 preserve V1 generation *and* verification; A′-7 `:46` "A v2 `MISMATCH` status is sealed, not automatically refused"; `DURATION_CONSISTENCY_NOT_MATCH` already fails closed downstream (`refinement.py:291-305`, `receipt.py:300`, `verify.py:55-59`) | Owner amendment of A′-7 D-1/D-3 **plus** Gate-3 contract-owner versioned-evidence change | **Rejected** |
| **P2m** | **Pinned-certification acceptance** (digest / verbatim binding only) | The verifier accepts a terminal interval iff the plan-pinned refinement **already certifies** a byte-bound MATCH tail, the record body is digest-re-verified at consume time (E18), and every frozen §8.7 predicate is re-checked from the record; **no byte re-measurement** | Tail extent becomes assertable with `DERIVED_NOT_OBSERVED` and a permanently `UNCERTAIN` last-frame extent; the provenance chain is container measurement → `refine()` → digest-bound record → digest-pinned plan → consume-time digest re-check | **Exceeds nothing.** Sits exactly inside A-12's recorded bound (E19); consumes frozen modules without editing them; requires no A-11 derivation and no R-8 exception; A-1/Root-G §3.4 untouched (no parse at all); A-5 untouched (frozen codes reused) | IT-6 disposition (Owner + Gate-3 contract owner) **plus** the claim label (A.4) | **Recommended target — smallest honest slice (`S1`)** |
| **P2r** | **Consumption-time re-measurement** | The verifier itself re-measures the named source bytes via frozen `gate3.container`/`gate3.temporal` and admits iff the re-measured end equals the requested end and §8.7 holds | Strongest independence: no producer record and no `ffprobe` value can substitute for measured container facts (E12); detects a producer record that disagrees with the bytes | **Exceeds A-12's bound.** A-12 is bounded to digest/verbatim re-check *because* design R-8 forbids "a second full-source parse outside the snapshot store" (E19); the facts derived would fall to **A-11's derivation subset**, verdict (c) contract owner, while IT-8 is `PARKED_BLOCKED`. Consumes (does not edit) frozen modules, so design §13 and A-1 are clean — R-8/A-11 are the breaking constraints | IT-6 disposition **plus** an explicit R-8 exception **plus** the A-11 derivation subset (contract owner) | **Deferred: stronger, but not the first slice (`S1B`)** |
| **P2e** | **Sealed-V2-evidence acceptance** (earlier draft's `P2a`) | Admit iff sealed V2 temporal evidence satisfies the §8.7 predicates | Tail extent assertable; relies on a sealed producer measurement | Predicates are approved design text (§8.7); endpoint admission is not; A′-7 D-5 forces a V2-only consumer | IT-6 disposition **plus** a V2-evidence threading path that does not exist (E9) | **Fallback only** (strictly larger scope than `P2m`, weaker than `P2r`) |
| **P3** | Deferred / unsupported tail **as declared policy** | Continue refusing (P0 behaviour) while sealed facts remain available for audit | Same as P0, but the deferral becomes an explicit, dated contract statement instead of an implicit gap | Fully compatible; zero new authority | None (documentation record only) | **Adopt as the interim in-force policy while §6 disposition is pending** |
| **P4** | Seconds × nominal FPS, `last_delta_ticks` synthesis, or "next tick" fabrication | Derive the end from duration-in-seconds × FPS or from the last sample delta | **None.** Fabricates frame-accurate temporal evidence | Prohibited by `src/gate3/temporal.py` header, design §8.7 ("never synthesize a following tick, never use nominal FPS"), authority matrix A-9/IT-3, and dispatch step 8 | — | **Rejected unconditionally** |

**What the first draft got wrong (corrected, both defects shrink the recommendation).**
(1) It claimed the plan pin was the compact projection and therefore could not carry a certification —
false (E10); the pin carries the full record, so a **one-file, no-parse** slice exists (`P2m`/`S1`).
(2) It proposed consumer re-measurement (`P2r`) as the recommended target while describing it as
"realising the A-12/IT-5 duty" — false (E19); re-measurement **exceeds** A-12's bound and needs an R-8
exception plus A-11's derivation subset. Consequences: `P2r` is deferred behind two authority grants,
and the "P2-pre precondition" of the first draft (verifier has no container-duration source) is real but
no longer blocking — it only means `P2m` must rely on the pinned certification rather than on a fresh
measurement.

---

## 5. Source-and-test gap inventory

Gaps below are the delta between measured capability and the P2 target. Each names the exact site.
`P2m` = recommended slice; `P2r` = re-measurement variant.

| Id | Gap | Site | Class | `P2m` | `P2r` |
| --- | --- | --- | --- | --- | --- |
| G-1 | Producer cannot emit a terminal interval at all: the interval end may only be the next observed frame PTS. | `src/vip_fvs/real_source_service.py:372-384` | MEASURED | blocks product reachability (`S2`) | blocks product reachability (`S2`) |
| G-2 | The bundle summary is compact, but the **plan build reloads the full record** from `evidence_artifact_ref`; therefore no tail fact is lost and no summary-schema change is needed for the certification to travel. | `src/vip_fvs/real_source_service.py:626-660`; `src/vip_fvs/real_plan.py:252-282,:307-317` | MEASURED | **not a gap** (corrected from the first draft) | not a gap |
| G-3 | Verifier refuses every terminal interval unconditionally. | `src/vip_fvs/real_preview_verifier.py:384-400` | MEASURED | the branch to change | the branch to change |
| G-4 | Verifier never reads the certification it already holds. | `src/vip_fvs/real_preview_verifier.py:53-92` vs grep-empty use | MEASURED | required check | required check |
| G-5 | V1 evidence carries no duration facts, so no V1 consumer can detect a MISMATCH. | `src/vip_fvs/source_snapshot.py:707-721` | MEASURED (by design, A′-7 D-2) | not relevant (no evidence consumed) | not relevant |
| G-6 | No consume-time certification check exists in FVS. | absence | MEASURED | the slice's core (digest-bound, no parse) | the slice's core (adds a parse) |
| G-7 | The verifier has no measured container-duration source, and `ffprobe` is measurably unsafe as one. | `real_preview_verifier.py:147-163`; E12 | MEASURED | **not blocking** — the pinned record supplies the certification | requires the A-11 derivation + R-8 exception |
| G-8 | `tail_end` with `nb_frames`+`duration_ts` but **absent** `duration_consistency` still returns `binding_eligible=True` (predicate hole in a frozen module). | `src/gate3/temporal.py:37-50` | DERIVED from PROBE | consumer guard: require the certification's C2 entry to carry `container_facts.duration_consistency == "MATCH"` and `measured_source_digest == source_content_digest` | same guard (plus its own facts) |
| G-9 | `tail_end`'s `last_delta_ticks` route mints `binding_eligible=True` from a caller-asserted `"uniform"` regime with zero callers and zero tests. | `src/gate3/temporal.py:47-49` | MEASURED / untested | negative-control test required | same |
| G-10 | `TAIL_*`/`EVIDENCE_DIGEST_MISMATCH` paths have no dedicated coverage for the terminal branch; `tail_end` has no direct unit test. | grep over `tests/` | MEASURED | new tests | new tests |
| G-11 | `DURATION_CONSISTENCY_NOT_MATCH` (receipt non-claimability) is untested. | `src/gate3/receipt.py:300` | MEASURED | pin it | pin it |
| G-12 | The third strict xfail matches **any** `SourceSnapshotError` with no `match=`/code, so any refusal (digest, origin, parse, VFR) XPASSes it: under P1 the decision would be unfalsifiable. | `tests/vip_fvs/adversarial/test_temporal_evidence_v1_matrix.py:376-400` | MEASURED | must be repaired only inside any authorized `DC-BIND` change (`S3`) | same |
| G-13 | The design §8.7 predicate `nb_frames == len(pts)` cannot be restated inside `vip_fvs.source_snapshot`/`real_source_probe`/`refinement_adapter` (module-scoped ban), but `real_preview_verifier.py` is **not** covered by that ban. | `tests/vip_fvs/adversarial/test_source_snapshot_temporal_safety.py:595-608` | MEASURED | use the record's C2 facts + the independently probed PTS enumeration; no binder needed | use the parser's count directly |
| G-14 | Identifier collision between two decision questions, with no crosswalk. | §2 | MEASURED | documentation | documentation |
| G-15 | No test distinguishes "refused because duration is ambiguous" from "refused because the feature is unimplemented". | `real_preview_verifier.py:396-400` single code | MEASURED | code-mapped branch | code-mapped branch |
| G-16 | The plan digest does not cover the pinned record body, so an acceptance that trusts the pin without re-deriving the record digest is forgeable. | `src/gate3/plan.py:163,:166`; E18 | MEASURED | consume-time `assert_evidence_digest` required | same, plus byte re-measurement |
| G-17 | Any consumer re-measurement conflicts with design R-8 and lands in A-11's derivation subset; no disposition records this. | E19 | MEASURED | not applicable | requires two authority grants first |

---

## 6. Recommended disposition

1. **Adopt `P3` as the dated interim in-force policy** until the IT-6 disposition is recorded: terminal
   intervals stay refused, the sealed V2 facts stay available for audit and are never consumed to
   support a claim, and the inability is stated as *deferred by decision*, not as an accidental gap.
   Zero new authority; consistent with every frozen decision.
2. **Request `P2m` (pinned-certification acceptance) as the target** — the one-file slice in §8.1 —
   with `P2e` as the fallback if the Owner requires sealed-evidence predicates instead. Rationale, in
   priority order:
   - it is inside A-12's **recorded bound** (digest/verbatim re-check only, E19), so it adds no R-8
     exception, no A-11 derivation and no new measurement path;
   - it keeps the provenance chain intact and unfakeable at the decision point, because the plan pin's
     digest does **not** cover the record body (E18) and the slice therefore re-derives it;
   - it is version-agnostic: no V1/V2 evidence is consumed, so A′-7 D-5 is not silently widened;
   - it consumes `src/gate3/**` without editing it (design §13) and touches no service, schema or code
     namespace.
3. **Defer `P2r` (re-measurement), not reject it.** It is the only variant that is independent of the
   producer record, but `E19` shows it exceeds A-12's bound: it needs (i) an explicit R-8 exception and
   (ii) A-11's derivation subset from the Gate-3 contract owner, with IT-8 still `PARKED_BLOCKED`. If
   the Owner prefers it, it becomes `S1B` and the same write scope applies with a larger authority set.
4. **Keep `DC-BIND` (Q1) RED and unchanged.** A V1 bind refusal would make an ambiguity
   unrepresentable while the downstream layers already fail closed, and it contradicts A′-7 D-1/D-3 and
   `:46`. Its real defect is falsifiability (G-12), not policy.
5. **Correct labels only** (§2) across the WBS, handoff, the A′-7 addendum, the two test files and the
   `src/vip_fvs/source_snapshot.py:762` comment. Archive artifacts are pointer-annotated, not rewritten.
6. **Record the two frozen-module hazards (G-8, G-9) as a durable Problem** and guard them at the
   consumer. They are not silently reachable today (zero callers for the delta route; both live call
   sites always pass the consistency key) but a future `tail_end` caller could mint `binding_eligible`
   without a measured `MATCH`.
7. **Reconcile the earlier lane conclusion, explicitly.** Lane 2 concluded "P2 … consumers must refuse"
   and pinned today's verifier refusal (`lane-2-test-and-red-matrix.md:10,:127`). That conclusion was
   drawn for a predicate-only design and is **superseded** here: `P2m`/`P2r` necessarily make the
   preview verifier an *admitting* consumer for certified terminal intervals, which is precisely the
   IT-6 decision the Owner is asked to take. The pinned refusal must therefore be amended deliberately
   under A.6 — not silently. Lane 2's matrix has no admitting column; the reconciliation is this item
   plus §7's added `P2m`/`P2r` columns.

### 6.1 The third strict xfail — disposition statement

The tripwire stays `xfail(strict=True)` and stays RED. It is **not** satisfied, retired, weakened or
made green by this packet, and it must not be turned green by a tolerance change, a reduced assertion
or fabricated temporal evidence. Its assertion (`_bind(...)` must raise `SourceSnapshotError` on a
MISMATCH source) is preserved as the historical record of an undecided question, and it already carries
the precision defect G-12. Its **marker reason may be relabelled** under A.6 (from "A-12/IT-6 PENDING" to
"DC-BIND PENDING") because that is a label correction; the **assertion body may not change** without a
`DC-BIND` decision. Under any future `DC-BIND` decision the replacement must be a **code-pinned** test
(`match=` on a typed code) that also keeps the GREEN pin's evidence-shape assertions alive, and the
retirement must be recorded in the same decision document that authorizes it.

---

## 7. Synthetic RED acceptance matrix

Every row is constructible from synthetic bytes or fact-layer patching at this base; no media, model,
provider or render is involved. `Current` is the measured outcome at `1cf13a3`. Layers:
`v1`/`v2` = snapshot binding, `art` = `gate3.container.verified_measurement_artifact`,
`tail` = `gate3.temporal.tail_end`, `rt` = `gate3.refinement` tail path, `fvs` = `verify_preview`.

| R | Scenario | Fixture | Current | P1 | P2m (target) | P2r | P3 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | CFR MATCH control | `build_mp4(1000,(40,40,40,40))` | v1 binds 14 fields; v2 seals; `refine` admits end 160 (`DERIVED_NOT_OBSERVED`) | admit | **admit** + tail check recorded | admit + re-measured | admit, endpoint refused |
| R2 | VFR MATCH | `(30,50,40,40)`; `declared_vfr=True` | facts via PROBE; exact-byte test `NOT_OBSERVED` | admit | admit + tail | admit | admit, refused |
| R3 | Reordered PTS MATCH | `(40,40,80,80)+(0,80,-40,-40)`, `declared_duration=200` | MATCH sibling untested; MISMATCH sibling (240) binds as V1 pin (E17) | admit | admit only at 200, never at `dts[-1]=160` | same | admit, refused |
| R4 | Trailing-duration MISMATCH (load-bearing) | `(40,40,40,40)`, `declared_duration=999` | v1 binds; v2 seals 999/`MISMATCH`; `rt` → `TAIL_NOT_BINDING_ELIGIBLE` | **refuse bind** (incompatible) | endpoint refused + receipt `DURATION_CONSISTENCY_NOT_MATCH` pinned | refused by re-measurement | unchanged + pinned |
| R5 | `duration_ts <= last_pts` | `(40,40,80,80)` with `declared_duration` 160 then 120 | `MISMATCH`; `art` rejects; `tail_end` raises "does not extend beyond" | refuse bind | endpoint refused (`TAIL_FACTS_INCONSISTENT`) | endpoint refused | unchanged |
| R6 | Absent / unparsable `duration_ts` | fact-layer `pop("duration_ts")` (monkeypatch precedent) / truncated bytes | v2 `SNAPSHOT_TEMPORAL_FACTS_INVALID`; v1 **binds** (gap); parse refusal | v1 must refuse | endpoint refused (`TAIL_MEASUREMENT_MISSING_CONTAINER_FACTS`; no certification exists) | endpoint refused | unchanged |
| R7 | `nb_frames` absent or `!= len(pts)` | fact layer (not byte-expressible) | `tail_end` raises "nb_frames is inconsistent" / key error | refuse bind | certification cannot exist (class-level); consumer requires `measured_source_digest` + PTS enumeration equality | parser count compared | unchanged |
| R8 | Nonzero `elst` origin | `media_time_offset=100` | `EDIT_LIST_ORIGIN_NOT_APPLIED` at v1, v2 and `refine` (`refinement.py:116-119`) | same | no certified record can exist; inherited, never re-derived | same | same |
| R9 | Multi-stream ambiguity | `fixturegen.RECIPES` multi-trak (one MATCH, one MISMATCH) | per-stream refusal; binding behaviour `NOT_OBSERVED` | per-stream | per-stream; certification must match `expected_stream_index` | per-stream | per-stream |
| R10 | Malformed / truncated ISO-BMFF | `_truncate_leaf` / inflated `stts` count | measurement refusal | same | same | same | same |
| R11 | Tail end exactly `== duration_ts` | R1 bytes | `rt`/`refine` admit; `fvs` refuses | admit | **the admission row** — exact end only, artifact body digest re-verified | admission, re-measured | refused (documented split) |
| R12 | Requested end `!= duration_ts` | R1 bytes, end 120/140 | `rt` → `TAIL_RECOMPUTED_END_DIFFERS` | refuse | refuse (`TAIL_RECOMPUTED_END_DIFFERS`) | refuse | refuse |
| R13 | Tail request with no measured container | `refine(..., container_path=None)` | `TAIL_REQUIRES_MEASURED_CONTAINER`; `fvs` refuses | refuse | refuse (`TAIL_REQUIRES_MEASURED_CONTAINER`; no record) | refuse | refuse |
| R14 | Semantic timestamp as endpoint | semantic-candidate evidence shape; semantic tick 500 | `UNSUPPORTED_BINDING_DOMAIN`; candidate non-binding | never frame-accurate | same | same | same |
| R15 | Nominal-FPS / `last_delta_ticks` derivation | `PtsTable(TimeBase(1,1000),(0,40,80,120))` | synthesises `TailEnd(160,…,True)` today (G-9); missing-consistency hole (G-8) | **refuse** | **refuse** + consumer requires the C2 facts block | **refuse** | **refuse** |
| R16 | V1 evidence at the tail endpoint | R1 source with V1 (14-field) evidence | no consumer reads evidence version | n/a | n/a (no evidence consumed) | n/a | n/a |
| R17 | **Tampered pinned record body** (new) | plan artifact whose `pinned_refinements` body is edited while the plan digest is unchanged (E18) | plan digest does not cover the body; `fvs` never reads it | n/a | **refuse** (`EVIDENCE_DIGEST_MISMATCH` from the consume-time re-derivation) | refuse | n/a |
| R18 | **Producer record disagrees with bytes** (P2m vs P2r splitter) | pinned record claims `MATCH`/tail while the named bytes are MISMATCH (fact-layer synthesis) | no consumer exists | n/a | **not detectable** by `P2m`; detected only if the record's own digest/source binding is inconsistent | **refuse** (re-measurement disagrees) | n/a |

Minimum falsifiability set: **`P2m` requires R1/R2/R3 (admission controls), R4, R7, R11, R12, R13, R14,
R15, R17** (R18 is documented as a known `P2m` limitation, not a pass criterion). Without R4+R17 the
acceptance is unfalsifiable; without R1/R2/R3 a refusal could be over-broad and pass vacuously. Every
negative row asserts an **exact frozen code**, never a bare "raises": this is the lesson of G-12.

---

## 8. Smallest implementation slice, with exclusive writer ownership

### 8.0 `S0` — this packet (authorized now)

Documentation-only: this decision record, the three lane memos, the §2 label crosswalk, and a tracker
checkpoint. No behaviour, no test change, no xfail change.

### 8.1 `S1` — verifier-side acceptance of a **pinned tail certification** (`P2m`, recommended)

**Status: `BLOCKED_ON_IT6_DISPOSITION`.** This is the next authorized-after-disposition slice and the
smallest one that is independently testable: one production file, no container parse, no schema change,
no new refusal code, no service change.

- **Exclusive writer**: one agent, one lane memo; no concurrent writer on the same files.
- **Write scope (exactly)**: `src/vip_fvs/real_preview_verifier.py` (terminal branch and its private
  helpers only); `tests/vip_fvs/adversarial/test_real_preview_verifier_qc.py` (tail-refusal region
  only); new `tests/vip_fvs/adversarial/test_stream_tail_admission.py`. No other file.
- **Stop-and-report guard**: if any required fact is absent from the pinned record, or if threading it
  requires an edit to `src/vip_fvs/source_snapshot.py`, `real_source_service.py`, `real_plan.py`,
  `review_bundle.py`, `local_preview.py`, receipt/QC modules or `src/gate3/**`, stop and report — that
  is `S1B`/`S2`, not `S1`.
- **Exact functions touched**: `verify_preview(...)` (`src/vip_fvs/real_preview_verifier.py:200`) —
  replace the `else: raise ValueError("STREAM_TAIL_NOT_SUPPORTED")` branch at `:396-400`; add private
  helpers `_pinned_tail_certification(...)` (evaluate the certification from the record already
  returned by `_authority_from_plan`) and `_tail_refusal_reason(...)` (map to existing codes); append
  checks to the existing `checks` tuple (no `PreviewVerification` field change).
- **Required logic (fail-closed, in order)**:
  1. non-terminal interval → unchanged behaviour; no new code path;
  2. terminal interval → take the pinned refinement already in scope (`_authority_from_plan`);
  3. re-read the artifact at `evidence_artifact_ref`; recompute
     `assert_evidence_digest(RECORD_KIND_REFINEMENT, record)`; require equality with the pinned
     `evidence_digest` (**E18/G-16**: the plan digest does not cover the record body) →
     `EVIDENCE_DIGEST_MISMATCH` on failure;
  4. require `record["source_content_digest"] == auth_values["source_sha256"]`,
     `record["stream_index"] == expected_stream_index`, `record["time_base"] == expected_timebase`,
     `record["start_ticks"] == interval start` (→ existing `SOURCE_REVISION_MISMATCH`/
     `SOURCE_STREAM_OR_TIMEBASE_MISMATCH`);
  5. require `end_is_stream_tail is True`, `method.derivation ==
     "pts_start_tick->duration_ts_tail_end"`, `extent_state == "DERIVED_NOT_OBSERVED"`,
     `last_frame_extent is None`, `tail_measurement_ref == f"C2_tail_measurement_reference:{source_sha256}"`;
  6. require the C2 `uncertainty` entry to carry `measured_source_digest == source_content_digest`,
     `container_facts.duration_consistency == "MATCH"` (**guards G-8**), `container_facts.duration_ts >
     independent_pts[-1]` and `container_facts.duration_ts == end_ticks == requested end`, `start` a
     member of the independently probed PTS enumeration; otherwise
     `TAIL_MEASUREMENT_MISSING_CONTAINER_FACTS` / `TAIL_FACTS_INCONSISTENT` /
     `TAIL_NOT_BINDING_ELIGIBLE` / `TAIL_RECOMPUTED_END_DIFFERS` respectively;
  7. **origin zero is inherited, never re-derived**: the record can only exist if `refine()` refused a
     nonzero `presentation_origin_ticks` (`src/gate3/refinement.py:116-119`), and plan build required
     `is_binding_eligible(record) is True` (`src/vip_fvs/real_plan.py:268`); the helper must not read or
     relax origin;
  8. **do not** call `is_binding_eligible`/`_byte_authority_covers`/`recompute_tail` at consume time —
     those re-resolve the named bytes, i.e. a second full parse forbidden by design R-8 (§4 `P2r`);
  9. admit only then, appending a check entry such as `{"check": "terminal_interval_tail", "result":
     "PASS", "basis": "pinned_refinement_certification", "derivation": "duration_ts - last_pts",
     "tail_end_ticks": <duration_ts>, "extent_state": "DERIVED_NOT_OBSERVED"}`; `production_eligible`
     and `export_eligible` stay **unchanged (`False`)**; the claim label may use only the existing
     receipt `NOT_OBSERVED` tokens if A.4 is granted;
  10. never synthesise a following tick; never consult `last_delta_ticks`, a nominal FPS, a duration in
      seconds, or any float; never treat `ffprobe` duration as authority (E12).
- **Refusal mapping — existing names only** (A-5 stays `PENDING`, no new code, no new namespace):
  artifact-body digest → `EVIDENCE_DIGEST_MISMATCH`; missing/unusable certification →
  `REFINEMENT_AUTHORITY_MISSING`; source/stream/timebase identity → `SOURCE_REVISION_MISMATCH`,
  `SOURCE_STREAM_OR_TIMEBASE_MISMATCH`; tail predicate failures → `TAIL_MEASUREMENT_MISSING_CONTAINER_FACTS`,
  `TAIL_FACTS_INCONSISTENT`, `TAIL_NOT_BINDING_ELIGIBLE`, `TAIL_RECOMPUTED_END_DIFFERS`,
  `TAIL_REQUIRES_MEASURED_CONTAINER`.
- **Acceptance tests (RED first)**: R11 positive (synthetic MATCH bytes, terminal end admitted, tail
  check recorded, `production_eligible=False`, `export_eligible=False`); one negative per predicate
  (R4, R5, R7, R12, R13, R15, origin R8); **R17 artifact-body tamper refused**; an explicit R18 test
  documenting that `P2m` does **not** detect a record that disagrees with the bytes (the limitation is
  asserted, not hidden); a nominal-FPS regression test that patches `fps`/seconds inputs into the path
  and asserts they are never read.
- **Trust label, mandatory**: `S1` is **"pinned-certification acceptance (producer-trusted,
  digest-bound)"**. It must never be described as independent re-measurement; producer independence
  comes from plan build (`is_binding_eligible`) plus the consume-time digest re-derivation, not from a
  fresh byte measurement.
- **Explicit non-goal**: `S1` makes the verifier *capable*; it does not make the product path
  *produce* a terminal interval (`S2`). This must be stated in the run memo so `S1` is not misreported
  as feature completion.

### 8.2 `S1B` — verifier-side consumption-time **re-measurement** (`P2r`)

**Status: `BLOCKED`.** Same write scope as `S1`, but the helper would parse the named bytes. That is
forbidden by design R-8 ("No second full-source parse outside the snapshot store") and lands in A-11's
derivation subset (verdict (c), contract owner) with IT-8 `PARKED_BLOCKED` (E19). Requires **two**
explicit grants before any code: an R-8 exception, and A-11's derivation subset. Strictly stronger than
`S1` (R18 becomes testable) and strictly larger in authority.

### 8.3 `S2` — producer terminal interval

**Status: `BLOCKED`.** The plan pin already carries the full record (E10, G-2), so **no summary-schema
change is needed**; what blocks `S2` is *where* a container duration may be read to request
`end = duration_ts`: authority matrix A-1 verdict (c) `PENDING` (Root-G §3.4 bans container parsing
inside `real_source_service.py`) and A-11's derivation subset. One contract surface plus one placement
decision — not a bounded single-writer slice yet, and it is the only remaining blocker to product
reachability.

### 8.4 `S3` — `DC-BIND` xfail disposition

**Status: `BLOCKED_ON_OWNER`.** Requires an Owner decision amending A′-7 D-1/D-3 plus a typed code
(G-12) and a Gate-3 contract-owner versioned-evidence change. Recommended outcome: leave V1 binding
duration-blind; G-12's precision defect is repaired only as part of any such authorized change.

### 8.5 `S4` — frozen-module hazards G-8/G-9

**Status: `BLOCKED` (`src/gate3/**` = NO DELTA in V1).** Record as a durable Problem with the exact
predicate hole and the zero-caller argument; `S1` installs the consumer guard in the meantime.

### 8.6 Value statement (honest, `EDITORIAL_INFERENCE`)

`S1` closes a real hole — a consumer that holds a tail certification but never reads it — and converts
an unconditional "not supported" into a measured, testable decision with existing codes, entirely inside
A-12's recorded bound. It is **enabling-only**: without `S2` the product path still cannot construct a
terminal interval, so no user-visible capability changes. The alternative to `S1` (wait for `S2`) leaves
the verifier's certification-blindness unfixed and the product refusal indistinguishable from a
regression (G-15).

---

## 9. Rejected alternatives and reconsideration triggers

| Rejected | Why | Reconsider if |
| --- | --- | --- |
| `P1` strict bind refusal (make the xfail green) | Contradicts A′-7 D-1/D-3 and `:46`; destroys a sealable ambiguity for no safety gain (downstream already fails closed); unfalsifiable without a typed code | Owner amends A′-7 and a typed code + `match=` test is authorized; or a real consumer is found that cannot fail closed on MISMATCH |
| `P4` seconds × nominal FPS / next-tick / `last_delta_ticks` synthesis | Fabricates frame-accurate temporal evidence; prohibited by the frozen `temporal.py` header, design §8.7 and the dispatch | Never. A future source-native duration is the only acceptable substitute |
| Deriving the tail end from `ffprobe` duration | Measurably a different quantity (E12: masks `mdhd` edits) | If a measurement proves `ffprobe` reports the container-declared `duration_ts` for every admitted profile |
| Choosing `P2r` (consumer re-measurement) first | Exceeds A-12's recorded digest-only bound; needs an R-8 exception and A-11's derivation subset (E19) | The Owner grants both explicitly and accepts a second parse at the consumer |
| Trusting the pinned certification **without** re-deriving the record digest | The plan digest does not cover the record body (E18/G-16), so the acceptance would be forgeable | Never (no cheaper equivalence exists) |
| Widening `S1` to touch `source_snapshot.py`/plan/receipt schemas | Turns a bounded slice into a multi-contract change without disposition | A separate IT-6/contract-owner disposition explicitly authorizes the plumbing |
| Making the `nb_frames` predicate literal inside `source_snapshot`/`real_source_probe`/`refinement_adapter` | Those modules are covered by the module-scoped ban (G-13); `real_preview_verifier.py` is not | If the safety suite is re-authorized to permit a narrowed, non-inference use |
| Renumbering `A-12` to the tail question | Breaks design §17, the C′ matrix and the A-12 receipt-field work; A-12 is already authorized in the other sense | Owner explicitly re-mints identifiers (contrary to §2 recommendation) |

---

## 10. Exact authority requirements

Requested of the **Repository Owner** (tail policy + A′-7 erratum) and the **Gate-3 contract owner**
(claim label, frozen-code mapping, version pinning). Per ADR-0003 the development source-write
enforcement remains reported as `DISABLED_BY_OWNER`; this request creates no grants, task packets,
Owner Witnesses or `PASS` records, and must not be read as one.

**A. Requested authorizations (each numbered; anything not listed stays unauthorized):**

1. Record the §2 identifier crosswalk as a label-only erratum: `A-12` = consumption-time re-verification
   (IT-5) + Dv-13; the tail question is `IT-6 (G-4)`; the third strict xfail is `DC-BIND`; Lane-C owner
   items are `LC-A-*`. Correction targets: the A′-7 decision (addendum; approved text preserved), the
   WBS, the handoff, the continuity start-here, `tests/vip_fvs/adversarial/test_temporal_evidence_v1_matrix.py`,
   `tests/vip_fvs/unit/test_source_snapshot_temporal_v2.py`, and the comment at
   `src/vip_fvs/source_snapshot.py:762`. Historical artifacts are pointer-annotated, not rewritten.
2. Decide `IT-6`: may a `DERIVED_NOT_OBSERVED` tail extent (`duration_ts − last_pts`,
   `duration_consistency == "MATCH"`, `presentation_origin_ticks == 0`) bound a **non-production**
   preview endpoint in V1, under claim label `source_end_extent_state = "DERIVED_NOT_OBSERVED"` with
   the last frame's own display extent permanently `UNCERTAIN`? **Recommended: YES**, bounded to V1
   non-production preview, under the design §8.7 predicates only.
3. Authorize `S1` **only if** A.2 is YES, with the `P2m` decision basis: the verifier accepts a terminal
   interval only from the plan-pinned refinement that already certifies a byte-bound MATCH tail, and
   **re-derives the record's own `evidence_digest` at consume time** plus the identity/tail predicates
   in §8.1 — all inside `src/vip_fvs/real_preview_verifier.py`, with **no** container parse, **no**
   `src/gate3/**` edit, **no** new measurement path (therefore no R-8 exception is requested here).
   If the Owner instead prefers independent re-measurement, that is `S1B` and requires **two further
   grants**: (i) an explicit design-R-8 exception for a second full-source parse at the consumer, and
   (ii) A-11's derivation subset from the Gate-3 contract owner (`matrix :33,:74`), noting IT-8 stays
   `PARKED_BLOCKED` (`aprime7 :45`).
4. Authorize the claim label through the existing receipt `NOT_OBSERVED` list only (e.g. `"source tail
   extent (DERIVED_NOT_OBSERVED)"`, `"last frame display extent (UNCERTAIN)"`): no new receipt field, no
   schema version bump, closed field sets unchanged.
5. Authorize the frozen/existing-code mapping in §8.1 only (`EVIDENCE_DIGEST_MISMATCH`,
   `REFINEMENT_AUTHORITY_MISSING`, `SOURCE_REVISION_MISMATCH`, `SOURCE_STREAM_OR_TIMEBASE_MISMATCH`,
   `TAIL_*`). No new refusal code or namespace; A-5 stays `PENDING`.
6. Authorize test changes: amend the tail-refusal assertions in
   `tests/vip_fvs/adversarial/test_real_preview_verifier_qc.py` so refusal is asserted only for
   unmeasurable/inadmissible cases; add `tests/vip_fvs/adversarial/test_stream_tail_admission.py`. The
   `xfail(strict=True)` at `test_temporal_evidence_v1_matrix.py:376-400` may be **relabelled**
   (marker reason only), assertion body preserved, and stays RED.
7. Authorize recording the G-8/G-9 frozen-module hazards as a durable Problem (no code change).

**B. Explicitly NOT requested / NOT authorized (must not be inferred from A):**

1. Any change to V1 binding or verification, or turning `test_duration_inconsistent_source_must_not_bind`
   green.
2. Any change to V2 bind-and-seal semantics (a MISMATCH stays sealed, never auto-refused).
3. Any edit to `src/gate3/**`, `src/vip_fvs/source_snapshot.py` semantics, `local_preview.py`, `cli.py`,
   receipt/QC schema modules, or `schemas/**`.
4. Producer-side terminal interval selection (`S2`) or any container read inside
   `src/vip_fvs/real_source_service.py`.
5. Any new `TEMPORAL_AUTHORITY_*`/`STREAM_TAIL_*` code, or renaming/removing a frozen code.
6. Real/authentic/protected media, network, models/providers, render/export, Gate promotion, canonical
   main integration, or changing `production_eligible`/`export_eligible`.
7. Any synthesized terminal tick, nominal-FPS or seconds×FPS arithmetic, packet-PTS/floats/tolerance,
   or any weakening of `SOURCE_*`/`SNAPSHOT_*`/digest assertions.
8. Treating this request as a grant, or emitting a fabricated `PASS`/`AUTHORIZED_CURRENT`/
   Owner Witness record.

**C. Acceptance evidence required for `S1`:** (1) positive synthetic MATCH terminal admission from a
pinned certification with the tail check record and `production_eligible=False`; (2) one negative per
predicate with the exact existing code; (3) **R17** artifact-body tamper refused by consume-time digest
re-derivation; (4) **R18** limitation asserted honestly (a record disagreeing with the bytes is not
detected by `P2m`); (5) nominal-FPS/`last_delta_ticks` negative control; (6) full `tests/vip_fvs` plus
affected `tests/gate3` result, with the third strict xfail **still RED**; (7) `git diff --stat` confined
to the §8.1 scope; (8) workspace verifier and secret scan clean, reporting
`DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT=DISABLED_BY_OWNER` (never `PASS`); (9) no receipt schema change, no
`src/gate3/**` delta, no new codes, no container parse added to `src/vip_fvs/`.

---

## 11. Label and evidence discipline (binding on any implementation)

- The terminal interval end is `DERIVED_NOT_OBSERVED`, never `MEASURED`; the refinement record's
  top-level `evidence_class="MEASURED"` describes the *refinement measurement*, not the final frame's
  extent. Consumers must read `end_is_stream_tail`/`extent_state` and must never infer extent from
  `evidence_class` alone.
- `S1`'s acceptance is **"pinned-certification acceptance (producer-trusted, digest-bound)"**. It must
  never be described as independent re-measurement or as `VERIFIED`; only `S1B` could make that claim,
  and only after its two grants.
- Output duration measured by `ffprobe` on the rendered artifact (`real_preview_verifier.py:467-480`) and
  the source tail extent are different domains; they must not be compared or substituted.
- A semantic or model timestamp may only identify a candidate; it is never a frame-accurate cut or a
  tail endpoint (R14).
- `duration_consistency` is a **derived comparison**, not an independent observation; `tail_duration_ticks`
  is the definition of the tail term (last sample delta), so `MATCH` is a consistency check, not a
  measurement of the final frame's duration.

---

## 12. Provenance

- `docs/agent-runs/2026-10-25-g3-a12-tail-duration/lane-1-source-trace.md` — 30-row behaviour matrix,
  line-cited; V1 duration-blindness, V2 seal-not-refuse, tail predicate order, consumer count zero.
- `docs/agent-runs/2026-10-25-g3-a12-tail-duration/lane-2-test-and-red-matrix.md` — 28-site test
  inventory, mutual-exclusion proof, 15-row fixture-measured RED matrix, fixture capability proof.
  Its "consumers must refuse" conclusion is superseded for `P2m`/`P2r` per §6 item 7.
- `docs/agent-runs/2026-10-25-g3-a12-tail-duration/lane-3-authority-trace.md` — identifier collision
  provenance, per-policy authority verdicts, owner table, verbatim authority-request block.
- **Independent adversarial review** (read-only, fresh context, this base): verdict `DO_NOT_SHIP` on the
  first draft with 2 blockers, 2 major, 4 minor, 2 nits and 1 missing-smaller-slice finding; all are
  incorporated. Blockers corrected: (a) the plan pin carries the full certified record (E10/G-2 rewrite,
  which produced the smaller `P2m` slice), (b) `P2r` exceeds A-12's R-8 bound and needs A-11's
  derivation subset (E19, §4, §10 A.3). Majors corrected: §4-vs-§6 recommendation inversion (now one
  ordered recommendation) and the unreconciled lane-2 consumer-refusal conclusion (§6 item 7). Reviewer
  also reproduced E1/E2 exactly and independently confirmed E3/E4, G-8 and G-9.
- Governed by: design `docs/superpowers/specs/2026-10-25-gate3-dual-temporal-authority-composition-design.md`
  §8.7/§11/§13/§15/§17 and R-8; `docs/agent-runs/2026-10-25-g3-cprime-v1/authority-disposition-matrix.md`;
  `docs/decisions/2026-10-25-g3-a3-aprime7-bounded-owner-decision.md`;
  `docs/agent-runs/2026-10-25-g3-dual-temporal-authority/04-stream-tail-and-audio-policy.md`;
  `AGENTS.md` items 6, 22-27, 37-42.
- Base `1cf13a3ff7ad4f9e5af5527fe8d19063a001cec0`. Re-verify every line reference against live `main`
  before acting; this packet is a dated disposition, not mutable truth.
