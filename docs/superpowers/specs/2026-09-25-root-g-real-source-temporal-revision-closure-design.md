# Root G — Real-Source Temporal + Revision Closure Design (Frozen Spec)

- **Root:** `root-real-source-editorial-contract-closure`
- **Goal:** `goal-20260925-real-source-editorial-contract-closure`
- **Branch:** `execution/execution-portfolio-20260924-v1/real-source-editorial-contract-closure`
- **Base / ROOT_BASE_SHA:** `d3b477db97541d7cd2775e7c42381eb4875de519`
- **Frozen:** 2026-09-25
- **Status:** APPROVED (owner design approval); governing authority for the Root-G implementation plan
- **Implementation:** `IMPLEMENTATION_AUTHORIZED=false` — this spec grants no implementation authority

> This document is the frozen governing design authority for Root G. It is
> implementation-independent where possible and mechanically precise where a
> predicate is normative. An implementation plan references it; the plan does
> not extend or reinterpret it.

---

## 1. Authority

### 1.1 Authority this spec stands on

| Ref | Artifact | Role |
|---|---|---|
| A1 | Owner design-approval prompt, 2026-09-25 (Root G owner approval → spec + plan) | Explicit owner approval of the bounded Root-G design |
| A2 | `.orchestration/portfolios/execution-portfolio-20260924-v1/authority/root-expansion-authorization-20260925-v2.json` @ blob `ce93a736295da7154bb1052fe4a3d3fec3ea07cc` | Root-G existence, base SHA, reservations, prohibitions |
| A3 | `.orchestration/portfolios/execution-portfolio-20260924-v1/goals/goal-20260925-real-source-editorial-contract-closure/task-packet.json` @ blob `e8234c4117318a823c4e2651a8620b41539592d5` | Root-G scope, design questions, prohibited scope |
| A4 | `.orchestration/portfolios/execution-portfolio-20260924-v1/authority/source-presence-and-g-test-ownership-normalization-20260925-v1.json` @ blob `166667bb224b46a7f97c51304bb1723424b896dd`, introduced at bootstrap commit `5e638ae816293a49891810af8d49246c92a95545` | v1 normalization; two new test paths; current-write hard denial |
| A5 | `.orchestration/portfolios/execution-portfolio-20260924-v1/authority/root-g-test-path-scope-amendment-20260925-v1.json` @ blob `6e214c304d68eb1a6ce22a0907a3bfa62efbaee3`, on bootstrap @ `fc21dc587321ba73b82b3cfe3644ce4fcc7c68fe` | Additive five-path test scope; purpose-limited fixture exception |
| A6 | `docs/handoffs/2026-09-25-chatgpt-continuation-v2/root-g-h/phase-2/ROOT_G_V2_FINAL_ADJUDICATION.md` | Coordinator adjudication; freezes `prior_revision` type and load-then-extend rule |
| A7 | Root D frozen branch `execution/execution-portfolio-20260924-v1/editorial-pipeline` @ `332bce40bae94a636d32e02f82b8467d8ae41645`, `src/vip_fvs/editorial_plan.py` @ blob `b1bc211695d72aeeca1273fa9816cbde8a7f2e03` | Current strongest implementation precedent for exact revision binding + immediate-prior lineage |

### 1.2 Repository rules this spec obeys

- `AGENTS.md` rule 7: semantic/model, technical-window, matched-offset, source-PTS/frame, proxy, timeline and rendered-output coordinates are distinct typed domains; a semantic timestamp is not a frame-accurate cut.
- `AGENTS.md` rule 8: source media is immutable and is never automatically rewritten because of a match/duplicate result.
- `AGENTS.md` rule 10: source identity/revision, run/attempt identity, artifact provenance, evidence state and policy are recorded for every derived claim.
- `AGENTS.md` rule 43: path/contract ownership conflicts are checked before spending agent capacity.
- `docs/architecture/CANONICAL_CONTRACTS.md`: typed time domains; half-open `[start, end)`; source PTS/frame claims identify stream and time base; VFR media never derives frames from `seconds × FPS`; only a deterministic source-native attempt may emit `source_pts`/`source_frame` refinement; corrections supersede rather than overwrite.
- `docs/architecture/ASTRA_DECISION_REGISTER.md` D10/D11: typed intervals carry domain, source revision, stream, origin, endpoints, time base, mapping, precision, producer and refinement eligibility; semantic/model/match intervals cannot authorize source-frame or edit cuts.

### 1.3 What this spec is NOT authority for

This spec does **not** authorize, and must never be read as authorizing:

- product code in `src/vip_fvs/**`. The **only** contemplated product surfaces for this design are exactly:

  - `src/vip_fvs/real_source_service.py`
  - `src/vip_fvs/real_plan.py`

  Both are non-writable until a separate explicit implementation authorization exists. No other product path is contemplated, and no `src/**` wildcard is granted or implied.
- creation or editing of any `tests/vip_fvs/**` file **now** (the exact five-path scope is enumerated in §9.1);
- CLI changes (`src/vip_fvs/cli.py` is outside Root G);
- Gate-3 changes (`src/gate3/**`);
- `src/vip_fvs/human_decision.py`, `schemas/vip_fvs/human_decision.json`, `src/vip_fvs/editorial_plan.py`;
- canonical-`main` mutation, root-to-root merge, force push, destructive Git;
- Gate promotion or `export_eligible` production authority;
- provider/model activity, model downloads, protected/archive media access, real-media execution, render/export.

### 1.4 Current implementation-write authority (hard denial)

The governing authority records state `implementation_authorized=false` for Root G, and A4/A5 classify an explicit `false` as a **HARD_DENIAL**, not a reservation and not a deferral-with-default-allow:

- reservations confer no write authority;
- exact-path sibling allocation confers no write authority;
- historical source presence confers no write authority;
- `all_five_allocated_paths_write_authorized_now: false`;
- unblocking requires **a separate explicit Root-G implementation authorization**.

---

## 2. Problem statements

### 2.1 D-PROV-1 — real-source temporal authority

Recorded in frozen Root D (`handoff.json` `contract_deltas`/`open_problem_ids`; `state.json` `open_problems[0]` and `produced_contract_deltas[0]`), status `OPEN_CONTRACT_BOUNDARY` / `PROVISIONAL_NEEDS_CONVERGENCE`:

> `real_source_service` interval selector does not compare locator timebase with probe timebase and merges frame/packet PTS; outside Root-D write domain.

Three distinct seams, all in `src/vip_fvs/real_source_service.py`:

- **D-PROV-1.A — locator coordinate.** A retrieval locator `pts` is interpreted as an exact source tick with no validation of the locator's declared timebase against the measured probe timebase. `SearchHit` carries `pts` + `timebase_num` + `timebase_den`, and the index layer already models the timebase as a rational (`pts_instant`), yet the service never consults it.
- **D-PROV-1.B — endpoint evidence role.** Observed source ticks are assembled by unioning frame presentation aliases with packet `pts` into one accumulator and collapsing through `sorted({...})`. A packet-only tick can therefore serve as an exact interval endpoint, and the accumulated set carries no record of which evidence class produced each tick.
- **D-PROV-1.C — publication before cross-check.** The service publishes a probe-derived timebase into the ReviewBundle without first comparing it to the timebase that Gate-3 actually measured from the source bytes. A downstream comparison exists at plan-build time (`real_plan.py::_load_authoritative_refinement`), so this is not an absent check; it is a check that runs **after** an internally inconsistent bundle may already have been sealed to disk.

### 2.2 D-REALPLAN-1 — decision-to-plan revision binding

Recorded in frozen Root D (`state.json` `open_problems[1]`, `produced_contract_deltas[1]`), status `OPEN_CONTRACT_BOUNDARY` / `CONFIRMED_OUT_OF_SCOPE`:

> Human decision binds `target_plan_revision`, but the constructor can receive a different `plan_revision` and produces the plan from that argument.

Two distinct defects in `src/vip_fvs/real_plan.py`:

- **D-REALPLAN-1.A — no exact decision/revision predicate.** `to_gate3_editorial_decision` projects `target_plan_revision` into `decided_on_revision`, but `build_real_edit_plan` never asserts the projected revision equals its own `plan_revision`. Gate-3's own bound is a lower bound (`1 <= decided_on_revision <= plan_revision`) and is deliberately correct for inherited decisions; it cannot substitute for the missing exact predicate.
- **D-REALPLAN-1.B — orphan and non-round-trippable revisions.** A caller may request `plan_revision > 1` with no lineage at all, producing an unattributable orphan revision. Additionally, `EditPlanRevision.to_record()` emits `supersedes` and `derived_from_refs`, but the REAL constructor passes neither and `load_real_plan` restores neither, so a lineage-bearing revision cannot survive its own `plan.to_record() != record["plan"]` readback assertion.

Both defects are of one kind: an unqualified or stale input silently becomes authoritative output.

---

## 3. Approved temporal predicates

All temporal predicates operate on **integer source ticks** in a **validated timebase**. No predicate in this spec may compute or compare a time value using floating point, `r_frame_rate`, `avg_frame_rate`, `nb_frames`, container duration, a nominal frame rate, or a `seconds × FPS` reconstruction.

### 3.1 Locator coordinate admissibility (D-PROV-1.A)

A retrieval locator `pts` MUST NOT be interpreted as an exact source tick unless **all** of the following hold:

1. `pts` is an exact non-boolean integer;
2. locator `timebase_num` and `timebase_den` are present, are exact non-boolean integers, and are both strictly positive;
3. the locator timebase is **exactly rationally equivalent** to the measured probe timebase, evaluated with integer arithmetic only:

```
locator_num * probe_den == probe_num * locator_den
```

4. no rescaling is performed. When equivalence holds, the locator `pts` is used **unchanged** as a tick candidate. Rational-equivalent-but-unreduced declarations (e.g. `2/2000` vs `1/1000`) denote the same tick unit and MUST behave identically to reduced ones; any conversion to a common representation is forbidden.

If any of 1–3 fails, the locator `pts` MUST NOT be used for exact source-tick selection, and the preparation MUST refuse with the code in §7.

*Mechanical justification:* the question answered here is "do these two declarations denote the same instant for tick t?" Both sides are declarations from independently produced metadata, and the index layer already treats the timebase as a rational. Rational equivalence is exact, avoids false refusal on formatting differences, and introduces no inexactness.

### 3.2 Authoritative endpoint-candidate projection (D-PROV-1.B)

Exact half-open `[start, end)` source-PTS endpoint candidates MUST be derived only from **measured frame presentation evidence of the selected stream**.

1. **Frame records only.** The projection reads `ffprobe_json["frames"]` entries whose `stream_index` equals `probe.selected_stream_index`. Entries with a `None`/absent/unparseable `stream_index` are excluded, never guessed. Records for other streams are excluded.
2. **Presentation fields only.** Per frame, aliases are inspected in this exact order: `best_effort_timestamp` → `pts` → `pkt_pts`.
3. **First valid wins.** The first alias whose value is a valid lossless presentation tick is used: an exact non-boolean `int`, or a `str` matching an optional leading `-` followed by digits only. Exactly **one** tick is contributed per frame.
4. **Malformed earlier aliases do not mask later valid aliases.** If an earlier alias is present but invalid (float, fraction string, `None`, non-numeric, `bool`), the projection continues to the next alias. No coercion — no `float()`, no rounding, no truncation — is ever applied.
5. **No valid alias for a frame** ⇒ that frame contributes **no** authoritative tick. This is not by itself a refusal.
6. **No alias is read from packets, and no tick is read from a top-level `pts_ticks` key** under any payload shape, including payloads that carry neither `frames` nor `packets`.
7. **Duplicate presentation ticks are preserved** in the ordered measured evidence with their multiplicity. Multiplicity is evidence and MUST NOT be collapsed away. The interval coordinates still use the **least** authoritative tick strictly greater than `start`, which is well defined over a value set; duplicates therefore do not create coordinate ambiguity and do not trigger a refusal.

**Hit test and upper endpoint.** The hit's locator `pts` is admissible as `start` only if it is a member of the authoritative projection. The endpoint is the least member strictly greater than `start`. If no member is strictly greater, refuse.

**No fallback.** If the authoritative projection is empty — no selected-stream frame yields a presentation tick — the preparation MUST fail closed with the distinct code in §7. There is no fallback to packet `pts`, to a top-level `pts_ticks` key, to a semantic timestamp, or to a nominal rate.

### 3.3 Evidence-class discipline

- The authoritative endpoints are `MEASURED` source-native ticks.
- Packet `pts` is corroborative/diagnostic provenance only. A packet-only tick can never be a hit or an endpoint. When a tick is present in both frame and packet evidence, it is admissible **because of the frame observation**, not because packet evidence was promoted.
- A semantic timestamp (`timestamp_human`, `semantic_seconds`) is candidate context only; it is never exact cut authority and never reaches interval selection.
- The broad observed-timestamp inventory helper (`_observed_pts`) MAY remain for compatibility and diagnostics, unchanged. It is **not** endpoint authority under this spec. An implementation MAY keep it exactly as-is; it MUST NOT be the source of exact endpoints.

### 3.4 Pre-publication measured-timebase cross-check (D-PROV-1.C)

After the service receives the authoritative, binding-eligible Gate-3 refinement record, and **before** the ReviewBundle is written:

1. read the measured timebase from that record;
2. compare it to the probe timebase using **exact tuple equality** on both integer components;
3. on mismatch, refuse with the code in §7 — no bundle is written;
4. a missing/invalid measured timebase in the record MUST refuse (no silent degradation);
5. on success, **publish the authoritative measured representation** as the bundle's source/refinement timebase, so the bundle carries the measured authority rather than a re-assertion of the probe declaration.

**No second container parser.** The measured timebase MUST come from the already-produced authoritative Gate-3 refinement output. Root G MUST NOT call `parse_iso_bmff_timing` (or any other container parser) inside `real_source_service.py` to recreate a measurement the authoritative refinement path already produced.

*Mechanical justification for tuple equality here (asymmetric with §3.1):* this predicate answers a different question — "did two independent measurements of the same bytes agree?" A divergence, even an unreduced-but-equivalent one, means the two measurement paths disagree about the source's tick unit, and the value is about to be published. Structural equality keeps publication deterministic and keeps every existing downstream structural comparison valid (`SourceTimelineMapping` exact `(num, den)` match; the plan-time summary/record comparison).

### 3.5 VFR rule

No predicate in this spec infers, reconstructs or validates a frame position from a nominal frame rate. Variable-frame-rate sources are handled solely by their measured presentation ticks and validated timebase. `seconds × nominal FPS` is forbidden everywhere in the Root-G closure. Reordering (B-frames) is handled by presentation-order fields only; decode-order values are never endpoint authority.

### 3.6 Source immutability and provenance

- The source media is never written, canonicalized, renamed or deleted by any Root-G behavior.
- The existing source-digest and source-revision assertions of the probe and preparation boundary remain in force and are not weakened.
- Every published interval remains attributable to a source revision, a selected stream, a timebase, and the measured evidence artifact that carries it.

---

## 4. Approved revision predicates

Let `N = plan_revision`, `D` = the newly supplied `HumanDecisionArtifact`, and `P` = the optional `prior_revision` (see §5).

### 4.1 Exact new-decision binding (always)

1. `D` must bind the selected refinement (existing pin/refinement checks remain in force and unchanged).
2. The projected `EditorialDecision.decided_on_revision` must equal `N` **exactly**.
   - Since `to_gate3_editorial_decision` maps `target_plan_revision` → `decided_on_revision`, this is equivalently the requirement `D.payload["target_plan_revision"] == N`.
   - This is an **exact** predicate, not the interval `1 <= decided_on_revision <= N`. Gate-3's interval bound is correct for inherited decisions and remains untouched; it does not satisfy this requirement.
3. A newly supplied decision targeting an **older** revision MUST NOT construct a higher revision, **including** when a valid prior revision is supplied. A decision with `target_plan_revision == 1` supplied with `N == 2` MUST be refused.
4. Older decisions may appear in revision `N` only as decisions **inherited through verified prior-plan lineage**. They are never the newly supplied authority for `N`.

### 4.2 Immediate-prior lineage (N > 1)

1. `N == 1`: `P` MUST be `None`. Supplying a prior revision is refused.
2. `N > 1`: `P` is REQUIRED and MUST satisfy:
   - `P.plan_revision == N - 1` (skipped revisions are refused);
   - `P.plan_id == plan_id` (a chain may not change plan identity);
   - `P.plan_scope` is compatible with the effective scope of the plan being built.
3. Construction for `N > 1` MUST route through the existing `gate3.plan.new_revision(P, ...)`. Consequently `supersedes == P.digest`, `derived_from_refs == [P.digest]`, `prior_revision is P`, and `plan_id`/`plan_revision` continuity are enforced by Gate-3's own constructor rather than re-implemented in `real_plan.py`.
4. `gate3.plan.new_revision` is not modified, wrapped with divergent semantics, or duplicated.

### 4.3 Load-then-extend rule

A sealed prior REAL plan may be used as the immediate predecessor directly:

```
prior = load_real_plan(path).plan
build_real_edit_plan(..., plan_revision=prior.plan_revision + 1, prior_revision=prior)
```

A loaded revision `N` is **sufficient** immediate-predecessor evidence for `N + 1`. A predecessor-of-predecessor object is NOT required, because `new_revision` consumes only `prev.plan_id`, `prev.plan_revision`, `prev.digest`, `prev.source_revision_ids`, `prev.plan_scope`, `prev.policy_decision_ref` and `prev.pinned_evidence_digests` — none of which requires `prev.prior_revision`. This holds only because §6 guarantees that `load_real_plan` restores the lineage fields that feed `digest`.

### 4.4 Unsupported caller surfaces

Any caller that requests `N > 1` without supplying the immediate prior revision MUST fail closed with the code in §7. Lineage is never fabricated and a revision is never emitted as an orphan. `src/vip_fvs/cli.py` has no prior-plan input and is outside Root G; a CLI request for `N > 1` therefore fails closed at the constructor. This is recorded as an intentional fail-closed limitation, not a defect and not a contract delta requiring CLI mutation.

### 4.5 No authority created

No plan produced under this spec becomes `export_eligible`. This spec creates no Gate promotion, no production export authority, and no policy authority. `policy_decision_ref` handling remains exactly as it is today.

---

## 5. Exact prior input type (frozen)

The public extension is frozen as:

```python
def build_real_edit_plan(
    bundle: ReviewBundle,
    decision: HumanDecisionArtifact,
    *,
    plan_id: str,
    plan_revision: int,
    pinned_evidence_digests: Mapping[str, str] | None = None,
    policy_decision_ref: str | None = None,
    prior_revision: EditPlanRevision | None = None,
) -> RealPlanArtifacts:
    ...
```

Rules:

- `prior_revision` is keyword-only, optional, and defaulted to `None`. Existing revision-1 callers are source-compatible.
- The accepted type is `EditPlanRevision | None`. `RealPlanArtifacts` is **not** a second accepted type; a union input would add no authority or capability.
- A caller holding `RealPlanArtifacts` passes `artifacts.plan`.
- A caller loading a sealed prior REAL plan passes `load_real_plan(path).plan`.
- No path parameter is added, and the CLI is not widened.
- `gate3.plan.new_revision` receives an `EditPlanRevision`, matching its existing contract.

### 5.1 Accepted public interface delta

```
id=G-REALPLAN-LINEAGE-INPUT-1
type=BACKWARD_COMPATIBLE_PUBLIC_INTERFACE_EXTENSION
surface=vip_fvs.real_plan.build_real_edit_plan
change=optional keyword-only prior_revision: EditPlanRevision | None plus N>1 lineage semantics
existing_revision1_callers=SOURCE_COMPATIBLE
cli=UNCHANGED_AND_FAILS_CLOSED_FOR_N_GT_1
```

This delta is entirely inside the Root-G reserved `real_plan.py` surface. It MUST be recorded as an interface change and MUST NOT be reported as "no interface change". It confers no authority to edit any consumer of `build_real_edit_plan`.

---

## 6. Serialization / readback invariants

The REAL plan envelope is unchanged; lineage lives **inside** the existing `plan` sub-object.

### 6.1 Envelope

The top-level record keys remain exactly:

```
{schema_version, plan, placement, mapping, projected_decision,
 plan_digest, placement_digest, mapping_digest, record_digest}
```

No new top-level key is added. No field is removed.

### 6.2 Construction

1. The REAL plan constructor MUST forward `supersedes`, `derived_from_refs` and `prior_revision` when they are present.
2. For `N > 1`, the constructed object IS the `new_revision` result; it is not re-constructed and its lineage is not re-derived.
3. For `N == 1`, `supersedes` is absent, `derived_from_refs` is empty and `prior_revision` is `None`.

### 6.3 Load / readback

`load_real_plan` MUST:

1. **restore** `supersedes` and `derived_from_refs` from the sealed `record["plan"]`;
2. not invent a `prior_revision` object (it is intentionally not serialized);
3. continue to verify `plan.to_record() == record["plan"]` and `plan_digest == plan.digest`;
4. **verify lineage coherence exactly** rather than trusting the record. The invariant is *exact equality with what construction can produce* (see §4.2), not mere membership:
   - `plan_revision == 1` ⇒ `supersedes` is absent or `None` **and** `derived_from_refs == []`;
   - `plan_revision > 1` ⇒ `supersedes` is present and is a valid lowercase-hex digest, **and** `derived_from_refs == [supersedes]` exactly — no additional unrelated derived reference, and no missing supersedes link;
   - any violation refuses with the code in §7.

   *Mechanical justification:* `gate3.plan.new_revision` always sets `derived_from_refs=[prev.digest]` and `supersedes=prev.digest`, so Root-G construction can never emit a record with an extra derived ref or a `supersedes` absent from the list. A membership-only rule would therefore accept a hand-forged sealed record that the producer cannot create; requiring exact list equality makes readback as strict as construction. This is a consistency clarification of already-approved `new_revision` semantics, not a new capability.

### 6.4 Chain extension after load

Because §6.3 restores the fields that feed `digest` and `supersedes`, the loaded `EditPlanRevision` is itself the immediate predecessor required to build `N + 1` (§4.3). No additional predecessor object and no additional envelope field are required.

### 6.5 Bounded honesty

`prior_revision` (the object) is intentionally not serialized. A loaded revision therefore carries lineage **references** and its own identity, which is exactly what `new_revision` consumes. This is sufficient by §4.3 and is not a limitation.

---

## 7. Refusal taxonomy

New codes are distinct so a cause is never hidden behind an unrelated failure. Existing codes are not repurposed or removed.

### 7.1 Temporal (`src/vip_fvs/real_source_service.py`)

| Condition | Code |
|---|---|
| Locator timebase missing, non-integer, `bool`, `None`, or ≤ 0 | `SOURCE_LOCATOR_TIMEBASE_INVALID` |
| Locator timebase not rationally equivalent to probe timebase | `SOURCE_LOCATOR_TIMEBASE_MISMATCH` |
| No selected-stream frame yields an authoritative presentation tick | `SOURCE_FRAME_PRESENTATION_PTS_NOT_OBSERVED` |
| Authoritative refinement record carries no valid measured timebase | `AUTHORITATIVE_REFINEMENT_TIMEBASE_NOT_MEASURED` |
| Authoritative measured timebase ≠ probe timebase (tuple) | `AUTHORITATIVE_REFINEMENT_TIMEBASE_MISMATCH` |
| Hit locator `pts` is not a member of the authoritative projection, or no greater member exists | existing `SOURCE_PTS_NOT_OBSERVED` / `SOURCE_PTS_INTERVAL_NOT_OBSERVED` (unchanged) |

### 7.2 Revision (`src/vip_fvs/real_plan.py`)

| Condition | Code |
|---|---|
| Projected `decided_on_revision != plan_revision` | `PLAN_REVISION_MUST_MATCH_DECISION_REVISION` |
| `N == 1` with a prior revision supplied | `PLAN_REVISION_1_CANNOT_HAVE_PRIOR_REVISION` |
| `N > 1` with no prior revision | `PLAN_REVISION_AFTER_1_REQUIRES_IMMEDIATE_PRIOR_REVISION` |
| `prior_revision.plan_revision != N - 1` | `PRIOR_REVISION_MUST_IMMEDIATELY_PRECEDE_THIS_REVISION` |
| `prior_revision.plan_id != plan_id` | `PRIOR_REVISION_MUST_SHARE_PLAN_ID` |
| `prior_revision.plan_scope` incompatible with effective scope | `PRIOR_REVISION_MUST_HAVE_COMPATIBLE_PLAN_SCOPE` |
| Invalid `prior_revision` argument type | `PRIOR_REVISION_MUST_BE_AN_EDIT_PLAN_REVISION` |
| Sealed-record lineage/readback incoherence (§6.3) | `REAL_PLAN_LINEAGE_READBACK_MISMATCH` |

---

## 8. Public interface delta summary

Only one public/shared-interface delta is produced by this design: `G-REALPLAN-LINEAGE-INPUT-1` (§5.1).

Everything else is explicitly **no delta**:

| Surface | Verdict | Reason |
|---|---|---|
| `src/gate3/**` | NO DELTA | Uses the existing, unmodified `gate3.plan.new_revision`; no predicate, bound or record shape changes |
| `src/vip_fvs/human_decision.py`, `schemas/vip_fvs/human_decision.json` | NO DELTA | `target_plan_revision` already exists and suffices; the closed payload/schema stay closed |
| `src/vip_fvs/editorial_plan.py` (Root D) | NO DELTA | Root D's accepted bridge already carries the mirrored semantics; not writable by Root G |
| `src/vip_fvs/cli.py` | NO DELTA | Intentional fail-closed limitation; not writable by Root G |
| REAL plan envelope | NO DELTA | `_RECORD_FIELDS` unchanged (§6.1) |
| Non-ISO-BMFF containers | NO DELTA / OUT OF SCOPE | Pre-existing fail-closed boundary; not widened by Root G |
| Existing test files outside the five-path scope | NO DELTA | Explicitly outside Root-G authority |

---

## 9. Test scope

### 9.1 The closed five-path set

```
NEW (Root-G owned):
1. tests/vip_fvs/unit/test_real_source_temporal_authority.py
2. tests/vip_fvs/unit/test_real_plan_revision_binding.py

EXISTING (purpose-limited fixture edit exception only):
3. tests/vip_fvs/integration/test_real_source_prepare.py
4. tests/vip_fvs/adversarial/test_real_prepare_plan_authority_v3.py
5. tests/vip_fvs/integration/test_real_preview_cli.py
```

No other `tests/vip_fvs/**` path is part of the approved design. Explicitly **outside** Root-G authority and receiving no allocation: `tests/vip_fvs/unit/test_real_plan.py`, `tests/vip_fvs/unit/test_real_source_service.py`.

### 9.2 Fixture-contract alignment (paths 3–5)

These three fixtures currently monkeypatch retrieval with hit-shaped `SimpleNamespace` objects that carry `pts` but omit `timebase_num`/`timebase_den`, so they cannot satisfy the real retrieval temporal contract:

| Path | Observed condition |
|---|---|
| `tests/vip_fvs/integration/test_real_source_prepare.py` | Hit lacks locator timebase; probe injects top-level `pts_ticks` and no frames |
| `tests/vip_fvs/adversarial/test_real_prepare_plan_authority_v3.py` | Hit lacks locator timebase; probe injects top-level `pts_ticks` and no frames; asserts `requested_pts == (40, 80)` and therefore depends on the injected `pts_ticks` |
| `tests/vip_fvs/integration/test_real_preview_cli.py` | Hit lacks locator timebase; probe already uses explicit `frames`, so no `pts_ticks` migration is needed |

Permitted edit purposes (authorization A5), and nothing else:

- add or use locator `timebase_num`/`timebase_den` on fake semantic hits so they satisfy the actual `SearchHit` temporal contract (`pts` + `timebase_num` + `timebase_den`);
- preferably construct actual `SearchHit` fixture objects instead of hit-shaped stand-ins, where appropriate;
- replace successful exact-boundary dependence on an injected top-level `pts_ticks` probe value with explicit frame presentation evidence (`frames[].best_effort_timestamp` / `pts` / `pkt_pts`) where needed;
- update assertions only insofar as they verify Root-G D-PROV-1 / D-REALPLAN-1 behavior.

Prohibited: unrelated refactor; cleanup/reorganization/formatting; new product behavior or assertions unrelated to D-PROV-1/D-REALPLAN-1; weakening production validation to tolerate a missing locator timebase; retaining top-level `pts_ticks` as REAL exact-boundary authority for a successful path; deleting/renaming/splitting the file; editing before separate explicit implementation authorization.

**Contract-integrity rule:** where a fixture and the real contract disagree, the fixture is corrected and the contract is not relaxed.

### 9.3 The real retrieval temporal contract

`persistent_local_index.search.SearchHit` is the contract the fixtures must model. Its fields are:

```
query, rank, score, row_id, source_path, source_sha256,
pts, timebase_num, timebase_den,
timestamp_human, thumbnail_path, thumbnail_status
```

### 9.4 Required coverage

**Path 1 — temporal authority.** Endpoint selection must cover at minimum: locator timebase exactly equal to probe; rationally equivalent but unreduced; mismatch with the same numeric `pts`; missing/malformed locator timebase; packet-only tick; same tick present in frame and packet; top-level `pts_ticks` with no frames; frame presentation records present; alias fallback with a malformed earlier alias; no authoritative frame evidence; an absence-of-rate-inference structural assertion.

Preservation of duplicate evidence must be pinned **observably**, not inferred from interval coordinates: the authoritative frame-presentation projection itself must be asserted to map input selected-stream frame ticks `(40, 40, 80)` to `(40, 40, 80)` — not `(40, 80)`. Because a set-collapsing implementation would still yield the interval `40 → 80`, an interval-only assertion cannot discharge §3.2(7). The projection is a module-internal implementation detail, not a public interface, so naming it is a plan-level decision rather than a spec-level one.

The pre-publication measured-timebase gate (§3.4) must be covered by RED tests for: missing measured `time_base`; structurally invalid measured timebase; measured/probe tuple mismatch; no `review-bundle.json` published on any of those refusals; and, on an exact match, publication proceeding with both the bundle source timebase and the refinement summary timebase equal to the authoritative measured tuple.

**Path 2 — revision binding.** Must cover at minimum: `N=1` exact match with no prior; `N=1` with prior refuses; `N=2` with no prior refuses; `N=2` with immediate prior and target 2 succeeds with correct lineage; `N=2` with target 1 and valid prior refuses; skipped revision refuses; different `plan_id` refuses; **incompatible prior `plan_scope` refuses** (using a real valid `EditPlanRevision` predecessor, since the accepted input type is frozen); save→load lineage preserved; load then build `N+1`; **hand-forged incoherent sealed lineage refuses**, covering at least (a) `derived_from_refs` missing the `supersedes` link and (b) `derived_from_refs` carrying an additional unrelated derived reference — in both cases without weakening the canonical envelope/digest checks in order to reach the lineage predicate; and no produced plan is `export_eligible`.

---

## 10. Execution preconditions

1. **Administrative test-path scope — SATISFIED.** The five-path scope is remotely durable (A4 + A5 on bootstrap @ `fc21dc587321ba73b82b3cfe3644ce4fcc7c68fe`).
2. **Explicit implementation authorization — NOT SATISFIED.** No path in §9.1 may be created or edited, and no product path may change, until a separate explicit Root-G implementation authorization exists. An allocation, a reservation, a spec, and a plan are all explicitly *not* write authority.

Hard precondition, to appear verbatim in the implementation plan:

```
PLAN_APPROVAL_DOES_NOT_AUTHORIZE_IMPLEMENTATION.
A separate explicit owner implementation authorization is mandatory.
The five-path test authority must be remotely durable before any test write.
```

---

## 11. Evidence classification

- Authoritative endpoints are `MEASURED` source-native ticks.
- Endpoint candidates are `MATCHED` (semantic retrieval locator) before refinement; they never become exact authority merely by being carried forward.
- Editorial decisions remain `EDITORIAL_INFERENCE`.
- `NOT_OBSERVED` remains an availability/status condition, never an evidence class and never promoted by review or by a schema evolution.
- No predicate in this spec promotes an assertion's class.

---

## 12. Explicitly rejected alternatives

| Rejected | Reason |
|---|---|
| Equality-only revision fix (`decided_on_revision == N` without lineage) | Leaves orphan `N>1` constructible; cannot satisfy §4.2 |
| Lineage-only revision fix (no exact new-decision predicate) | Allows an older-target decision as new authority; violates §4.1 |
| Restricting REAL planning to `N == 1` | Amputates the existing `new_revision` capability and makes `plan_revision` dead; scope distortion, not closure |
| Re-implementing the revision chain inside `real_plan.py` | A second chain implementation that can drift from `gate3/plan.py`; violates one-authority-per-predicate |
| Adding plan identity to the human-decision payload/schema | Requires closed-schema and `_PAYLOAD_FIELDS` changes in unauthorized surfaces |
| Accepting `RealPlanArtifacts` as `prior_revision` | A union input adds no authority or capability; §5 freezes a single type |
| Wrapping or modifying `gate3.plan.new_revision` | Gate-3 is read-only for Root G |
| A second `parse_iso_bmff_timing` call in Root G | Duplicates a measurement the authoritative refinement path already produced and digests |
| Locator-only temporal closure | Leaves packet-derived endpoints admissible (§3.2) |
| Frame-only temporal closure without the measured-timebase cross-check | Leaves the publication gate open (§3.4) |
| Cross-check-only temporal closure | Leaves both endpoint seams open |
| `float`/`math.isclose` timebase comparison | Inexact; forbidden by §3 |
| Tuple equality for the locator comparison | False refusal on unreduced-but-equivalent declarations; the index layer models the timebase rationally |
| Rational equivalence for the measured-refinement comparison | Admits cross-measurement disagreement and breaks deterministic publication/downstream structural comparison |
| Rescaling locator ticks to a canonical timebase | Reintroduces silent tick-domain equivalence |
| Snap-to-`first_at_or_after` as the endpoint mechanism | Silent resolution instead of fail-closed refusal |
| Top-level `pts_ticks` as REAL exact-boundary authority (including a shape-based fixture seam) | No production ffprobe payload emits it; a synthetic payload must not gain REAL authority by omitting frame records |
| Rejecting a frame whose earlier alias is malformed | Lets an optional bad alias mask a valid later alias; §3.2(4) |
| Coercing a malformed/float alias | Inexact conversion |
| Weakening the locator rule to tolerate duck-typed hits | Converts a fixture omission into a production authority bypass |
| `set()`-collapsing duplicate presentation evidence | Destroys evidence multiplicity |
| Adding a `--prior-plan` CLI surface | Outside Root-G authority; §4.4 |
| Non-ISO-BMFF support expansion | Out of scope |
| Opening a new Problem record for `editorial_plan` structural symmetry | No concrete violation of its own frozen contract demonstrated; recorded only as a deferred convergence observation |

---

## 13. Reconsideration triggers

- Owner decides a newly supplied decision may target an older revision.
- Owner decides revision numbers may skip rather than being strictly consecutive.
- Owner decides a REAL plan may be chained onto a synthetic/fixture ancestor.
- Owner requires an on-disk predecessor reference or a plan-path parameter.
- Owner requires the locator and measured timebases to be structurally identical rather than rationally equivalent.
- Owner requires the measured-refinement comparison to use rational equivalence.
- Owner requires human decisions to carry plan identity (schema + `human_decision.py` delta; unauthorized here).
- `gate3.plan.new_revision` semantics change, or a higher authority narrows REAL planning to revision 1.
- The five-path authority scope changes, or a broader `tests/vip_fvs/**` allocation is later granted.
- Root-G target product blobs change from `real_source_service.py` `7840268a5cd7775aeb7c64d09cbdd9a1cfe66058` / `real_plan.py` `02a5798d97b4133f82b69183137fd052f9717bc6`.
- Non-ISO-BMFF admission becomes a goal.
- A real multi-revision producer appears that cannot supply a sealed immediate predecessor.

---

## 14. Non-authority statement

This spec grants no product implementation authority, no test creation or edit authority, no CLI/Gate-3/schema authority, no Gate promotion, no export authority, no `main` mutation authority, and no media or provider execution authority. Implementation of anything described here requires separate explicit owner authorization. Where this spec and a current repository authority record disagree, the authority record governs.
