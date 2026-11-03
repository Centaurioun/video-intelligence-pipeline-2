# Gate-3 A-7 Cross-Contract Integration Readiness — Decision Packet (rev. 2)

- Date: 2026-10-25. Base: `813f1982416fda7cb5619c903a607df148df2140` (= `origin/main`, PR #204).
- Predecessor: `docs/decisions/2026-10-25-g3-a7-stream-namespace-positive-mapping-disposition.md` (PR #203, merged at `13e3c96d5be8a22564a52dd34cdaad7085b86291`; that packet's own base was `7b72e2b3`).
- Lane memos (this packet's evidence): `docs/agent-runs/2026-10-25-g3-a7-cross-contract-readiness/lanes/{a-spec-anchor,b-code-interface,c-review-ledger,d-demux-verify,e-contract-adversarial,f-code-adversarial}.md`.
- Implementation plan: `docs/superpowers/plans/2026-10-25-g3-a7-stream-identity-mapping-implementation-plan.md`.

> **STATUS — `PROPOSED_DISPOSITION`. This document grants no authority.**
> It proposes contract-owner decisions. It does **not** adopt A-7, does **not** change `src/**`, `tests/**` or `schemas/**`, does **not** edit the canonical WBS, and does **not** unbundle `IT-8`. `A-7` remains `(c) PENDING` and `IT-8` remains `PARKED_BLOCKED` until a separate owner/contract-owner record adopts something. Every "PROPOSED" row is a request, not a fact.
> `DEVELOPMENT_SOURCE_AUTH_ENFORCEMENT` is `DISABLED_BY_OWNER` (ADR-0003); this document invents no grant, witness, or `PASS` marker, and adds no administrative layer.
> **Revision 2** folds two independent adversarial lanes (`e-`, `f-`); every finding and its disposition is in §12.

## 0. What this packet is for

PR #203 proved a candidate rule (`P2`) and deliberately stopped before adoption. Two things were missing for an implementation-ready decision:

1. **Cross-contract ownership** — *where* the correspondence is computed, *who* owns each of its two sides, and *which* files may change (PR #203 asked this as `B-1 … B-10` but did not answer it).
2. **A smallest coherent architecture** — a design in which the rule can be implemented without opening schema, container, probe-argv, plan, receipt or preview-artifact surfaces.

This packet answers both, corrects PR #203 where live `813f1982` disagrees with it, and states one thing PR #203 asserted too strongly: **the probe-artifact ↔ source-bytes pairing is a producer-sealed assertion today, not an independently re-measurable one** (§4.5). That single correction is what makes the proposal honest.

It does **not** re-run the 14-case synthetic study, the 24 RED rows, or the evidence inventory; it re-verifies only the facts the decisions rest on.

## 1. Corrections to the PR #203 packet at `813f1982`

Citation/state corrections only. PR #203's policy verdicts survive all of them.

| # | PR #203 claim | State at `813f1982` | Effect |
|---|---|---|---|
| C-1 | WBS anchors `:252`, `:253`, `:7`, `:13` | **`:255`**, **`:258`**, **`:9`**, **`:15`**; authoritative adoption-pending row is **`WBS:257`**; docs-only row is `WBS:256` | Use `:255–:258` |
| C-2 | `PA-5`: "`src/gate3/**` and `tests/**` take no delta" | **`tests/**` has no freeze of any kind.** `a3:47` names `src/gate3/**`, Gate-0, shared preview/verifier — not `tests/**`. `S1:340` (`NO DELTA`) is a Root-G **interface-delta row with a reason**, not a subtree freeze | Tests are ordinary writable surfaces under task ownership |
| C-3 | P0 "Lead-verified coextensive" | `review_bundle.py:360` is a **live cross-namespace comparison**; `E-15` supersedes the "coextensive" wording but `DP:145` was never rescoped and no §4 row covers it | It is a **bundle-validation detection gap** |
| C-4 | `review_bundle.py:360` compares same-probe values | Compares a **Gate-3 all-trak ordinal** with a **libavformat stream index** | The consumption surface is real |
| C-5 | §7.1(3)/§7.2 refute non-canonical `tkhd` headers | `size == 0` was not enumerated; `_boxes` (`container.py:60-74`) silently converts `size==0` to `end-pos`, so the condition is **invisible unless the raw size word at the yielded `box_start` is re-read** | Added as an explicit check + RED row |
| C-6 | §2 anchor for "FFprobe global index" = `real_source_probe.py:163-167,198-206` | Those are the argv and the canonical-JSON/digest publication. Correct: **`:98-117`** (`_select_stream`, `stream["index"]` at `:110,:114`), **`:191`**, **`:217`** | Citation repair |
| C-7 | Design premise: selector = "N-th timing-bearing `vide` trak" | Only `design:158`/`:439` assert it. Code: `container.py:165` enumerates **all** direct `moov/trak`; `:167-169` assigns `traks_index` before the timing filter; `:171` selects on it; `:199` publishes `stream_count = len(traks)` | Residual risk is **track-ID usability + payload attribution**, not ordinal displacement |
| C-8 | `ORDINAL_DISPLACEMENT` as design vocabulary | Packet-coined. Design's named code is `TEMPORAL_AUTHORITY_STREAM_IDENTITY_DIVERGENCE` (`design:280,:306`); that namespace is unadopted (`matrix:27`) | No `TEMPORAL_AUTHORITY_*` name is used here |
| C-9 | `src/gate3/AGENTS.md:5` compliance assumed | Mandated pre-read `docs/gates/gate3/SELECTED_CANDIDATE_EXECUTION_CONTRACT.md` **does not exist** (matrix `M8`) | Prerequisite P-8 |
| C-10 | `fixturegen._tkhd` fix "changes four pinned fixtures"; *no* committed fixture byte-pins | WRONG in rev. 1. Every generated MP4 carries `track_ID == 0` (`fixturegen.py:21` writes the ordinal into *modification_time*), **and** the fix changes fixture bytes: `tests/vip_fvs/unit/test_source_snapshot_temporal_single_read.py:55,:70` pin `f0911b54…`, the digest of `build_mp4(_REORDER_BYTES)`. Measured full-suite effect of the fix: **2 failed, 1221 passed** | The fixture repair is a named two-constant re-baseline with a stop guard |
| C-11 | `mock` path `prototypes/…/functional_prototype.py` | Real path is **`src/gate3/functional_prototype.py:129-133`** | Citation repair |
| C-12 | A-6/B-9 "matrix names only `composed_temporal.py`" | Accurate as a *decision-row* reading; the module itself is proposed at `design:427` (§17 A-6). No record authorizes any other new Gate-3 module | B-9 is a new grant either way |

`MEASURED` re-verifications at `813f1982` (ffprobe 9.0.2, synthetic fixtures only): positional `streams[i].id` = lowercase hex of that trak's `tkhd.track_ID`; reversed ids `[2,1] → ["0x2","0x1"]` (position, **not** sort order); large-size `tkhd` (`size==1`) is readable only via header-aware payload start (`payload+12`; `box+20` reads `creation_time`); one stream per direct `moov/trak` in box order for four shapes; fMP4 keeps `moov/tkhd` but the repo timing parser refuses it.

## 2. Decision matrix — approved vs proposed

"APPROVED" = in force at `813f1982` under an existing record. "PROPOSED" = this packet asks; nothing is decided. No PROPOSED item may be implemented before its own disposition lands.

| ID | Question | State | Governing text |
|---|---|---|---|
| P0 | Refusal-only A-7 safety (single-trak / sole-video derivations; no guessed mapping) | **APPROVED — IN FORCE, do not weaken** | `WBS:255`; `matrix:29`; `CHATGPT:137` |
| P1 | Universal refusal as the fail-closed branch of any future mapping rule | **APPROVED as that branch only** | `matrix:29`; `CHATGPT:137` |
| A′-7 | Snapshot temporal evidence v2 (closed 21-key evidence projection = 20 body keys + `evidence_sha256`; strict origin-zero) | **APPROVED and implemented** | `a3:24,:27`; `src/vip_fvs/source_snapshot.py:800-859` |
| A-9 | Edit lists: strict origin-zero admitted; a nonzero `elst.media_time` refuses `EDIT_LIST_ORIGIN_NOT_APPLIED` | **APPROVED — unchanged by this packet** | `matrix:31`; `src/gate3/container.py:124-131`; `src/gate3/refinement.py:116-118` |
| IT-8 | Preview/verifier provenance repair | **PARKED_BLOCKED** — refusal subset only; deriving byte/stream/timescale facts in the verifier is not authorized | `matrix:43`; `WBS:255,:257` |
| **B-1** | Adopt the positional identity rule as the accepted A-7 mapping rule | **PROPOSED — new Owner + contract-owner disposition** | `matrix:29,:73`; `design:439`; `WBS:257`; `a3:44` |
| **B-2** | Placement of the `tkhd` fact + predicate | **PROPOSED** — `src/gate3/stream_identity.py`; binding authorization is **B-9** | `matrix:28`; `design:427` |
| **B-3** | Store the mapping proof vs re-derive it | **PROPOSED — re-derive** (no schema, no evidence-key delta) | `a3:24`; `a3:27` |
| **B-4** | Granular `R-ID-REFUSE-*` codes vs existing refusal faces | **PROPOSED — reuse existing faces; never pin diagnostic strings in tests** | `matrix:27` (A-5 `(c)`) |
| **B-5** | Preview/verifier refusal scope before A-7 resolves | **PROPOSED — bind + bundle validation; verifier and `local_preview` untouched** | `matrix:33,:43,:62`; `a3:47` |
| **B-6** | Admit the `P2u` two-sided video-uniqueness subset | **NOT PROPOSED NOW** — needs a new fact for no extra truth | PR #203 §6 |
| **B-7** | Grant a `src/gate3/fixturegen.py` delta | **PROPOSED — narrow grant + named two-constant re-baseline** | `src/gate3/AGENTS.md:5,:13,:15`; C-10 |
| **B-8** | Gate-0 `id` suppression | **OUT OF SCOPE** | — |
| **B-9** | May a **second** Gate-3 module exist and enumerate `moov/trak` | **PROPOSED — yes, exactly one: `src/gate3/stream_identity.py`** | `matrix:28`; `design:427` |
| **B-10** | Demuxer-build identity | **PROPOSED — a claim label, not a gate** (§4.8) | `AGENTS.md:58,:90` |
| **B-11** *(new)* | Probe-artifact self-binding (artifact carries the source digest it measured) | **PROPOSED as a prerequisite, not as part of the smallest slice** — needs a grant on `src/vip_fvs/real_source_probe.py` | §4.5; finding W2C-2 |
| P4 | Ordinal/count/order heuristic (`id == k`) | **REJECTED UNCONDITIONALLY** | PR #203 §6 |
| P3 | Corroboration-only facts | **CORROBORATION ONLY** | PR #203 §6 |

## 3. B-1 — exact proposed adoption text

Proposed for a **new** contract-owner record; quoted as the literal text to adopt or reject.

> **A-7 STREAM IDENTITY — PROPOSED ADOPTION (verified positional identity; fail-closed; scope: multi-`trak` containers).**
>
> **Scope.** Let the container be an unfragmented ISO-BMFF source whose `moov` box has `N >= 2` direct `trak` children `T0 … T(N-1)` in box order, and let the FFprobe stream list have `N` entries `S0 … S(N-1)` in JSON-array order. The FFprobe global stream index of a track is admitted as corresponding to that track **only** when all of (1)–(8) hold and the caller also satisfies (9)–(11). A container with exactly one direct `trak` is **outside this rule**: with one stream, the FFprobe index of that stream is fixed by cardinality, so no namespace ambiguity exists and the existing behaviour stands unchanged, neither strengthened nor weakened.
>
> 1. **Bound inputs, and the exact strength of that binding.**
>    (a) The container-side facts are re-derived from bytes whose SHA-256 the caller recomputed and compared to the declared `source_sha256` of the same named source.
>    (b) The probe-side rows are read from the persisted probe artifact whose **file bytes** hash to the declared `probe_digest` (the producer digests the canonical JSON **including its trailing newline**, `src/vip_fvs/real_source_probe.py:198-199`; a digest of the un-newlined form does not match).
>    (c) The pairing *"this probe JSON was measured on those source bytes"* is **`PRODUCER_SEALED`**: it exists because the probe binding records the source digest and the probe digest together in one process, under a before/after source-digest equality check, and the refinement record then seals both under its own evidence digest (`src/vip_fvs/real_source_service.py:609-611`). It is **not** an independent re-measurement at consume time, the persisted probe artifact carries no source digest of its own (`real_source_probe.py:185-224`), and no artifact field exists today that would make it self-proving. Every statement relying on this rule must carry `probe_source_binding = PRODUCER_SEALED`.
>
> 2. **Cardinality.** `len(S) == N`.
> 3. **Structural `tkhd` validity, per position.** Each `Ti` has exactly one direct `tkhd` child; the raw size word at that box's start is not `0` and not `1`; box length is `>= 92` (version 0) or `>= 104` (version 1); version ∈ {0,1}; the `track_ID` field at that version's offset lies inside the box. Boxes are read only through the header-aware reader at `src/gate3/container.py:60-74`, and the `size == 0` check re-reads the size word at the yielded `box_start` because that reader converts `size==0` to `end-pos` and would otherwise hide it.
> 4. **Track-ID validity.** `0 < track_ID(Ti) < 0xFFFFFFFF` for every position.
> 5. **Probe-ID validity.** Every `Si` carries `id`, canonical lowercase `0x` hex, `0 < int(id,16) < 0xFFFFFFFF`, and `index(Si) == i`.
> 6. **Positional identity.** `int(Si.id, 16) == track_ID(Ti)` for **every** `i`. This is equality of values **at the same position**; it is explicitly not `int(Si.id,16) == i`, which reversed ids falsify.
> 7. **Uniqueness.** The `track_ID` values are pairwise distinct, so the correspondence is a bijection.
> 8. **Guarded selection.** For selected position `k`: `0 <= k < N`, `handler(Tk) == "vide"`, `codec_type(Sk) == "video"`, `index(Sk) == k`. `k` must be an exact integer — never `bool`, never `float`.
> 9. **Timing is unchanged.** Every published timing fact remains the container re-measurement of `Tk` through the existing byte-authority path. This rule adds evidence about *which track `k` is*; it never adds, replaces, normalizes or truncates a timing fact, and never introduces `seconds × nominal FPS` arithmetic.
> 10. **Edit lists are untouched.** This rule makes **no** claim about `edts`/`elst` and introduces no edit-list refusal. Edit-list admission stays exactly as A-9 approved it: origin-zero admitted, nonzero `elst.media_time` refuses `EDIT_LIST_ORIGIN_NOT_APPLIED`.
> 11. **Provenance label.** The correspondence is asserted **for the demuxer that produced the probe artifact**. No demuxer/tool identity is recorded for it today, so every use carries `demuxer_build_state = NOT_OBSERVED`, and must never be reported as `VERIFIED` nor used to argue an `IT-8` unblock.
>
> **Fail-closed branch.** If any of (1)–(8) cannot be established, the correspondence is **refused**, never guessed, never downgraded to a heuristic, and never replaced by a count/order/handler argument. Refusal classes, in evaluation order: `BOUND-EVIDENCE-UNAVAILABLE`, `NO-TKHD`, `TKHD-HEADER-UNSUPPORTED`, `TRACK-ID-UNUSABLE`, `TRACK-ID-DUPLICATE`, `COUNT-MISMATCH`, `PROBE-ID-UNUSABLE`, `POSITIONAL-MISMATCH`, `SELECTED-NOT-VIDEO`, `SELECTION-AMBIGUOUS`. These strings are **implementation diagnostics**: they are defined once in the owning module, they are not contract vocabulary, and no test may pin them as literals (A-5 `(c)` PENDING).
>
> **Residual assumptions, stated not hidden.** (i) Condition (6) asserts an implementation property of the `mov` demuxer — that libavformat assigns `streams[i].id` from the same-position `trak`'s `tkhd.track_ID`. That is `MEASURED` on exactly one build (ffprobe 9.0.2, synthetic fixtures) and `NOT_OBSERVED` for other builds, for real media, and for v1/large-size `tkhd` beyond fixtures. (ii) The repo's own parser never reads `tkhd.track_ID`, so it is **not** an independent witness; independence comes only from two different code paths over the same bytes. (iii) The probe↔source pairing is `PRODUCER_SEALED`, not independently re-measured (condition 1c).
>
> **Does not decide.** This rule does not adopt: the `TEMPORAL_AUTHORITY_*` code namespace or any failure-code name (A-5); a composed-authority module or object (A-6); composition placement inside `prepare_real_source` (A-1); any `IT-8` verifier derivation or provenance repair; any schema or evidence-key delta; any probe-argv change; any Gate promotion. It also does not itself authorize implementation — that needs the prerequisites in §6.
>
> **Reconsideration triggers (exact).** Reopen if: a second demuxer build or a real-media corpus contradicts condition (6) for an admitted case; a real container has direct `moov/trak` children FFprobe does not emit as streams (cardinality then fails closed — a coverage loss, and the trigger to reconsider `P2u`/`B-6`); a v1 or large-size `tkhd` must be admitted; the probe artifact gains a source digest (then condition (1c) upgrades from `PRODUCER_SEALED` to self-proving and this text must be rewritten, not merely relabelled); or A-5/A-6/A-9 adopt names this text refers to only descriptively.

## 4. Preferred architecture for the smallest `P2` implementation

### 4.1 One sentence

**One Gate-3 module owns the `tkhd` fact and the cross-namespace comparison; one tiny FVS gate owns the shared invocation policy; two existing surfaces invoke it — at bind and at bundle validation — and nothing new is serialized.**

The correspondence is a **checked** fact, not a **stored** one: it is recomputed from digest-verified inputs wherever it is needed.

### 4.2 Components, owners, exclusive write paths

| Component | Path | Contract owner | Writer | Change |
|---|---|---|---|---|
| Fact + predicate | `src/gate3/stream_identity.py` **(new)** | Gate-3 / A-7 contract owner | `W-FACT` | New, pure, stdlib-only, no file I/O |
| Predicate tests | `tests/gate3/test_stream_identity_mapping.py` **(new)** | Gate-3 | `W-FACT` | New |
| Fixture conformance | `src/gate3/fixturegen.py` | Gate-3 fixture owner | `W-FIXTURE` | `_tkhd` field order + optional `track_id`; builders; one `RECIPES` consumer |
| Fixture byte-pin re-baseline | `tests/vip_fvs/unit/test_source_snapshot_temporal_single_read.py` (`:55`, `:70`) | FVS snapshot owner | `W-FIXTURE` | **Exactly two constants**, nothing else |
| Fixture tests | `tests/gate3/test_fixturegen_tkhd_conformance.py` **(new)** | Gate-3 | `W-FIXTURE` | New |
| Shared invocation policy | `src/vip_fvs/stream_identity_gate.py` **(new)** | FVS / A-7 contract owner | `W-GATE` | One function: verify artifact **file** digest, derive `len(traks)` from bytes, single-trak rule, else require `PROVEN` |
| Gate tests | `tests/vip_fvs/test_stream_identity_gate.py` **(new)** | FVS | `W-GATE` | New |
| Bind-time enforcement | `src/vip_fvs/refinement_adapter.py` (`refine_requested_candidate:144`, forwarded from `refine_retrieval_candidate:281`) + `src/vip_fvs/real_source_service.py:540-552` | FVS / A-7 contract owner | `W-BIND` | New keywords; guard replaced by the gate |
| Bind tests | `tests/gate3/test_stream_namespace_safety.py`, `tests/vip_fvs/test_stream_identity_bind.py` **(new)** | FVS | `W-BIND` | Amended only if a pin legitimately changes |
| Consumption-time enforcement | `src/vip_fvs/review_bundle.py` (the cross-namespace gate at `:356-364`) | FVS / A-7 contract owner | `W-BUNDLE` | Re-derive before accepting selector equality |
| Consumption tests | `tests/vip_fvs/test_review_bundle_stream_identity.py` **(new)** | FVS | `W-BUNDLE` | New |

**Dependency direction preserved:** `vip_fvs → gate3` only. `stream_identity.py` imports `gate3.container._boxes` (an **intra-package** private use of the only permitted reader) and nothing from `vip_fvs`. The gate module imports `gate3.stream_identity`; it holds the only file I/O.

### 4.3 Proof ownership

| Fact | Owner | Checked by | Carried how |
|---|---|---|---|
| positions and box order of direct `moov/trak` | Gate-3 container | `container.py:165` | in-process measurement |
| `tkhd` presence/header/version/length/`track_ID` | Gate-3 `stream_identity` | this rule | re-derived |
| FFprobe stream rows | FVS probe artifact | **artifact file digest** | persisted canonical JSON |
| **the correspondence** | Gate-3 `stream_identity` | every consumer | **recomputed, never carried** |
| probe↔source pairing | FVS producer (`real_source_service.py:609-611`) | `PRODUCER_SEALED` label | sealed refinement record |
| timing facts | Gate-3 byte authority | existing byte binding | existing sealed evidence |
| demuxer identity | FVS | — (`NOT_OBSERVED`) | transient evidence object only |

Consumers own **invocation and refusal**, never the predicate. That is what stops three files from making three different assumptions about the same integer.

### 4.4 Serialization — decision and rationale (B-3)

**Serialize nothing new.** Inputs already exist and are digest-bound at both consumers: bundle payload carries `source.source_sha256`, `source.probe_artifact_ref`, `source.probe_digest` (`review_bundle.py:125`); the byte-authority binding carries `container_path` **or** `measurement_artifact_path` (`refinement.py:590-593`); `is_binding_eligible` already re-validates it.

Storing the proof would need an A′-7 `D-2` successor (closed 21-key projection), a schema version bump in frozen `src/vip_fvs/source_snapshot.py`, and a `review_bundle` schema change (`schemas/vip_fvs/review_bundle.v3.json` has `additionalProperties: false`) — a large authority surface for a re-derivable fact. Storing buys portability, not truth.

**Bundle-path caveat (finding W2C-4).** When `byte_authority.container_path` is `None` the container bytes are not resolvable from a bundle; the gate must then refuse rather than degrade. This is a *coverage* rule, stated in the plan, not a silent fallback.

Trigger to revisit: a consumer appears that holds a sealed record but can reach neither container bytes nor the probe artifact. None exists at `813f1982`.

### 4.5 Digest binding — and its honest limit

1. **container bytes ↔ `source_sha256`**: recomputed by the caller; mismatch refuses.
2. **probe artifact file ↔ `probe_digest`**: `sha256(file bytes)`; the producer's digest covers canonical JSON **plus its trailing newline**, so the gate hashes bytes as written and, like `review_bundle.py:340-341`, accepts only the canonical form(s) the producer actually emits.
3. **probe ↔ source**: **`PRODUCER_SEALED`**, as specified in §3 condition (1c). The gate cannot prove it and must not imply it can. Consequence: the proof is *as strong as the producer*, which is exactly why `B-11` (probe self-binding) is the recommended follow-up, and why every claim carries the label.
4. **rows ↔ artifact**: the gate reads rows from the digest-verified file itself, so no separate "caller says these rows came from there" argument exists — the pure module receives rows plus a `probe_provenance` string describing that artifact, and records it in its evidence object.

### 4.6 Refusal semantics (B-4, B-5)

- **Adapter (bind).** The guard at `src/vip_fvs/refinement_adapter.py:194-217` is **replaced**, never merely relaxed. The replacement must refuse every input the old guard refused *when no evidence is supplied*, and may accept a multi-`trak` container only when the gate returns `PROVEN`. That is the only sense in which it is stronger; the packet does not claim more. Deletion and replacement are one commit; a commit that only deletes is a fail-open window and must be reverted.
- **Bundle validation.** The existing comparison at `review_bundle.py:356-364` gains a gate call and keeps raising the same `ValueError` family. No new token namespace, no new field.
- **Verifier.** `src/vip_fvs/real_preview_verifier.py` is **not touched**: `matrix:43` bars deriving byte/stream/timescale facts there, and `a3:47` names the shared preview/verifier. Its existing `artifact.selected_stream_index != measured_stream` check (`:385-386`) compares a quantity that upstream gates now make meaningful.
- **No pinned diagnostics.** Tests assert `state`/refusal *identity through constants*, never literal diagnostic strings; if A-5 later names codes, renaming stays a one-module change.
- **Seal tightening deferred.** Restricting the accepted `stream_identity_derivation` vocabulary at `source_snapshot.py:811` refuses nothing that binds today; it costs a frozen-file delta for no safety gain now.
- **Edit lists untouched** (§3 condition 10): no new refusal, A-9 unchanged.

### 4.7 Source-native timing protection (must-not-weaken list)

(a) The FFprobe integer remains the API selector and is never reinterpreted as an ordinal; (b) timing stays bound to the same physical `trak` the probe row named; (c) no `seconds × nominal FPS`; (d) no renormalization/re-render/re-timestamp (`refinement_adapter.py:268-270` stays read-only); (e) no truncation of `pts_ticks`; (f) `-map 0:{stream_index}` (`local_preview.py:739-745`) keeps FFprobe semantics and becomes safe precisely because the mapping is proven; (g) `media_timescale` stays the `mdhd` timescale of the selected trak.

### 4.8 Demuxer-build identity (B-10)

Facts: ffprobe JSON has **no** program/build/version field; the probe artifact is canonical payload + digest only, so two builds with identical JSON are indistinguishable; a tool-identity mechanism exists only in the local-preview lane (`local_preview.py:177-184`).

**Proposed: a claim label, not a gate, and with no new carrier.** `demuxer_build_state ∈ {OBSERVED, NOT_OBSERVED}` is a **language requirement** on claims (this packet, PR bodies, review notes) and a field on the *transient* evidence object returned by the gate — never a persisted artifact field, because no permitted carrier exists. `NOT_OBSERVED` blocks the word `VERIFIED` and blocks any `IT-8` unblocking argument. Refusing all binds without a build record is explicitly **rejected**: it would refuse every working bind today, prevent no wrong mapping, and turn a provenance limitation into an outage. `B-11`/`P-6` (probe self-binding incl. executable digest) is the path to `OBSERVED`.

### 4.9 Alternatives deliberately not taken

| Alternative | Why not now | Reconsider when |
|---|---|---|
| Store the proof in sealed temporal evidence | Needs a D-2 successor, new schema version, closed-key-set edit, bundle-schema change | A consumer exists with neither probe artifact nor container bytes |
| Predicate inside `src/vip_fvs/**` | FVS would own a container fact (`design` §7) and would duplicate a box reader or make a private cross-package import | Owner denies B-9 and prefers a frozen `container.py` addition |
| Add `parse_tkhd_track_ids()` to frozen `container.py` | `matrix:84`/`a3:27` deny edits there; the parser dict is contract-shaped | Owner authorizes a container delta and the contract-shape review |
| Harden the verifier first | `matrix:43` + `a3:47`; bind+bundle already cover both routes | A-11 scope explicitly admits derive-and-refuse |
| Admit `P2u` (`B-6`) | Needs a new fact for no extra truth on the admitted path | A real corpus shows a case `P2` refuses but `P2u` admits safely |
| Keep `fixturegen` unmodified | The corpus could not express distinct ids; every RED row would need a private builder | Owner prefers NO DELTA; then a private builder module is the alternative |
| Ignore the probe↔source gap and call the proof "independent" | It is not; the artifact carries no source digest | `B-11` lands |

## 5. Cross-contract conflicts, resolved at design level

| Conflict | Resolution |
|---|---|
| **A-1** (`S1:155`: `prepare_real_source` must not call a container parser) | The predicate is invoked inside `refinement_adapter.refine_requested_candidate`, which **already** calls `parse_iso_bmff_timing`; `real_source_service.py:540-552` only passes the probe path and digest. The boundary crossing is therefore *the existing one*, not a new one — but because the call chain is reached from `prepare_real_source`, **A-1 placement is a stated residual** (P-12): if A-1 later relocates composition, the adapter path is unaffected; if A-1 instead forbids any container read reached from `prepare_real_source`, this design is void and must be re-scoped. |
| **A-5** (`(c)` PENDING codes) | No new namespace; diagnostics live in one module constant; tests never pin literals. |
| **A-6/B-9** (only `composed_temporal.py` proposed) | B-9 asks for exactly one other module and explicitly **not** `composed_temporal.py`, so `P2` does not couple to the blocked A-6/IT-3 workstream. |
| **A-7** | This packet *is* the A-7 decision request; it decides nothing. |
| **A-9** (origin-zero admitted) | §3 condition (10) removes every edit-list refusal from the rule. Rev. 1's `EDIT-LIST-UNSUPPORTED` was wrong and is withdrawn. |
| **A-11 / IT-8** | Scope cut to bind + bundle; the verifier is untouched, so IT-8 gains no derivation. |
| **A-12** (consumption-time re-verification bounded to digest/verbatim re-check; no second full parse, design R-8) | The bundle gate performs a **metadata-only box scan** (box headers + 24 bytes per `trak`); it never parses `stts`/`ctts`/`mdhd` and produces no timing fact. The plan pins that with a static guard test and with P-11, an explicit A-12 confirmation that a `tkhd`-only enumeration is not "a second full parse". If P-11 is refused, `S5` is dropped and the residual is recorded instead. |
| `a3:47` vs `matrix:33/:43` on the shared verifier | `a3:47` is scope-bound to the A′-7 record. This packet avoids the collision by not editing the verifier or `source_snapshot.py` at all. |
| `S1:340` promoted into a subtree freeze | Read as scope-bound (C-2). No general freeze exists; the delta still needs a grant because none exists and `src/gate3/AGENTS.md:15` forbids widening a task's own scope. |

## 6. Implementation prerequisites

| # | Prerequisite | Owner | Blocks | Exact requirement |
|---|---|---|---|---|
| P-1 | Adopt §3 as a contract-owner record (or reject and stop) | Owner + A-7 contract owner | all | A new record; do not edit PR #203's packet |
| P-2 | `B-9` grant: one new Gate-3 module `src/gate3/stream_identity.py` | Owner + Gate-3 contract owner | `S2`–`S5` | Names the file and its single purpose |
| P-3 | `B-7` grant: `fixturegen.py` delta **plus** the two named constant re-baselines | Owner + Gate-3 fixture owner | `S1` | Names both files; accepts the stop guard |
| P-4 | `B-3` confirmation: re-derive, no store, no schema change | Contract owner | `S4`,`S5` | States that no evidence body grows |
| P-5 | `B-5` confirmation: bind + bundle only; verifier/`local_preview` untouched | A-7/A-11 contract owner | `S4`,`S5` | Resolves `a3:47` vs `matrix:33/:43` in favour of "untouched" |
| P-6 | `B-11` probe self-binding (source digest + executable digest in the artifact) | FVS | `S7` (optional) | Not required for `S1`–`S5`; upgrades the label from `PRODUCER_SEALED` |
| P-7 | `B-4` confirmation: reuse existing faces; no new namespace; no literal diagnostics in tests | A-5 contract owner | `S4`,`S5` | May be given as "deferred to A-5" |
| P-8 | Resolve `src/gate3/AGENTS.md:5`'s missing pre-read | Gate-3 contract owner | `S1`,`S2` | Supply the contract or amend the pre-read (matrix `M8`) |
| P-9 | Re-synchronize `origin/main` and re-confirm anchors before dispatch | implementing Lead | all | Anchors are `813f1982`-relative |
| P-11 | A-12 confirmation: a `tkhd`-only box enumeration at bundle validation is not the forbidden "second full parse" | A-12/IT-6 contract owner | `S5` | If refused, drop `S5` and record the residual |
| P-12 | A-1 confirmation: invoking the predicate from the adapter, reached via `prepare_real_source`, is within the existing parser boundary | A-1 contract owner | `S4` | Since the adapter already calls the parser, this is a confirmation, not a new grant |

## 7. What this packet does not decide

Any `src/**` acceptance; schema or evidence-key changes; a probe-argv change or `-select_streams`; plan/review-bundle/receipt shape changes; Gate-0 probe allowlists; real or protected media; any provider/model/render work; Gate promotion; any WBS checkbox; the merge of this branch; and any statement that `IT-8` is unblocked, that composed authority exists, or that A-5/A-6 progress has occurred.

## 8. Label discipline

- Never compare typed domains: container `traks_index` and FFprobe `index` are different namespaces even when integers coincide.
- Never describe a re-derivable proof as "stored", a receipt digest as identity evidence, or a second read of the same bytes as an independent demuxer.
- The positional equality is `MEASURED` on synthetic fixtures on one ffprobe build; `NOT_OBSERVED` for real media and other builds. The probe↔source pairing is `PRODUCER_SEALED`.
- Never report this packet's acceptance as `IT-8` progress, composed-authority progress, or A-5/A-6 progress.
- Refusal strings are diagnostics, not contract codes.

## 9. Six-cycle refinement record (this packet's own cycles)

| Cycle | Question | What changed |
|---|---|---|
| 1 | Re-derive evidence? | Only the facts the six decisions rest on (lane D). Nothing failed to reproduce |
| 2 | Is "store the proof" cheaper? | No — closed-key-set successor + schema version + frozen edit + bundle schema change, for a re-derivable fact. Reversed |
| 3 | Can the verifier be hardened cheaply under IT-8? | No — `matrix:43`, `a3:47`. Cut to bind + bundle |
| 4 | Is a second Gate-3 module necessary? | Yes, for the fact *and* the comparison, or FVS owns a container fact. Exactly one module |
| 5 | Do the build-identity facts force refusal? | No — refusing unrecorded builds refuses every working bind. Converted to a claim label |
| 6 | Does any slice touch a frozen surface? | `container.py` no; `source_snapshot.py` no; `schemas/**` no; probe argv no; preview/verifier no. Writes are two new modules, `fixturegen.py`, the adapter, the bundle, and tests |
| 7 | Independent adversarial wave 2 | Two lanes, both `DO_NOT_SHIP`; 30 findings; §12 |
| 8 | Lead adjudication | Every BLOCKER and MAJOR accepted and folded; two findings partially rejected with reasons (§12) |

## 10. Provenance and citation verification

- Base `813f1982` verified as `origin/main` after `git fetch --prune`; worktree tree clean at base.
- WBS anchors re-read at `:1`, `:9`, `:15`, `:255`, `:256`, `:257`, `:258`. Matrix at `:23`, `:27`, `:28`, `:29`, `:31`, `:33`, `:38`, `:43`, `:55`, `:62`, `:73`, `:84`. A′-7 record at `:3`, `:5`, `:24`, `:27`, `:44`, `:45`, `:47`.
- Code re-read at this base: `src/gate3/container.py:30-45,60-74,124-131,140-153,155-201,205-283`; `src/gate3/fixturegen.py:21,60-80,85-105`; `src/gate3/refinement.py:40-99,500-600,605-640`; `src/vip_fvs/refinement_adapter.py:144-230,281`; `src/vip_fvs/review_bundle.py:125,326-364`; `src/vip_fvs/real_preview_verifier.py:95-147,363-404`; `src/vip_fvs/real_source_probe.py:98-117,185-224`; `src/vip_fvs/real_source_service.py:540-552,600-611`; `src/vip_fvs/local_preview.py:177-184,739-745`; `src/vip_fvs/source_snapshot.py:795-859`; `tests/vip_fvs/unit/test_source_snapshot_temporal_single_read.py:43-72`; `tests/gate3/test_stream_namespace_safety.py` (all 158 lines).
- Runtime: `tests/gate3 tests/vip_fvs` → **1223 passed, 1 xfailed**; namespace pins 5 passed (CPython 3.14.9). No environment-caused failures.
- Not verified here: real-media equality; any second demuxer build; the `src/gate3/**` execution contract (missing, P-8).

## 11. Status summary

| Item | Status |
|---|---|
| A-7 mapping rule | **PENDING** — §3 is a proposal, adoption **NOT** claimed |
| A-7 refusal-only protection | In force, unchanged |
| This packet | Documentation-only; grants nothing |
| Implementation slices | **BLOCKED_ON_§6_PREREQUISITES** |
| `IT-8` | **PARKED_BLOCKED**, unchanged |
| Canonical WBS | Not edited by design |

## 12. Independent adversarial review (wave 2) — findings and dispositions

Two fresh-context, read-only lanes attacked this packet and its plan. Both returned **DO_NOT_SHIP**. Findings are recorded in `lanes/e-contract-adversarial.md` (17, contract/authority) and `lanes/f-code-adversarial.md` (20, code/feasibility). All BLOCKERs and MAJORs were accepted and folded into this revision.

| # | Lane | Finding | Disposition |
|---|---|---|---|
| W2C-1 | contract | Fail-closed branch refused `EDIT-LIST-UNSUPPORTED` that no condition stated | **Accepted** — refusal withdrawn; §3 condition (10) now says edit lists are untouched; A-9 preserved |
| W2C-2 | contract | "Bound probe evidence for the same named source" is unestablishable: the artifact carries no source digest and no record cross-checks probe↔source | **Accepted** — the strongest finding. §3 (1c) now names the pairing `PRODUCER_SEALED` with its exact basis and limits; `B-11`/P-6 added; §4.5 rewritten |
| W2C-3 | contract | A-9 papered over (no §5 row; plan refused any `edts`) | **Accepted** — see W2C-1; new `A-9` rows in §2 and §5 |
| W2C-4 | contract | A-12 "satisfied by construction" is false: bundle validation re-parses container bytes | **Partially accepted** — scope is a metadata-only box scan, not a full parse; §5 rewritten; P-11 added so the contract owner decides; if refused, `S5` drops |
| W2C-5 | contract | A-1 row misdescribes the call graph ("not a prerequisite" unsupported) | **Accepted** — §5 rewritten; A-1 stated as a residual and P-12 added |
| W2C-6 | contract | Single-trak branch contradicts "only when all of (1)–(7) hold" | **Accepted** — §3 now scopes the rule to `N >= 2`, so single-`trak` is outside the rule rather than an exception to it |
| W2C-7 | contract | `size!=0` undetectable through `_boxes`; no RED row | **Accepted** — §3(3) specifies re-reading the raw size word at the yielded `box_start`; plan adds R-21 |
| W2C-8 | contract | `demuxer_build_state` has no permitted carrier | **Accepted** — §4.8: transient evidence object + language rule only, never a persisted field |
| W2C-9 | contract | Test-pinned diagnostics are a de facto A-5 namespace | **Accepted** — §4.6: tests assert through module constants, never literal strings |
| W2C-10 | contract | S1 write scope omits the consumer test modules; "no committed byte pins" false | **Accepted** — C-10 corrected; write scope and stop guard name the exact two constants |
| W2C-11 | contract | "21-key" vs "20 body keys + digest" misquote | **Accepted** — both spellings used explicitly, quoted from `a3:27` |
| W2C-12 | contract | Evaluation-order drift between §3 and the plan | **Accepted** — one order, stated once, mirrored in the plan |
| W2C-13 | contract | `size==0` spec premise uncited | **Accepted** — phrased structurally (a `size==0` box extends to its container's end; `tkhd` is not the last child) rather than by spec quotation |
| W2C-14 | contract | Wrong path for `functional_prototype.py` | **Accepted** — C-11 |
| W2C-15 | contract | `design:427` over-read for B-9 | **Partially accepted** — §2/B-9 now says "the only module any record *proposes*", and `matrix:28` remains the decision row |
| W2F-1 | code | S1 breaks two committed fixture-digest pins and cannot land GREEN as scoped | **Accepted** — the two constants are now named in the write scope and the stop guard |
| W2F-2 | code | S3 hashed `canonical_json(payload)` while the producer digests JSON **+ newline** → would refuse all genuine artifacts | **Accepted** — the gate hashes the artifact **file bytes**, §4.5(2) states the newline, plan R-G2 pins it |
| W2F-3 | code | `stream_count` was caller-asserted and chose the legacy branch before counting | **Accepted** — the gate derives `len(traks)` from the bytes; `stream_count` is no longer an argument |
| W2F-4 | code | S2 lacked the `provenance` argument §4.5(3) requires; "strictly stronger" not established | **Accepted** — `probe_provenance` is a required argument; §4.6 now claims only "never weaker without evidence, stronger only with evidence" |
| W2F-5 | code | R-G5 impossible under S3's own step order | **Accepted** — the gate counts `traks` first, then takes the single-`trak` branch |
| W2F-6 | code | R-G2…R-G6 share one `ImportError` RED; a blanket-refusal stub satisfies five of six | **Accepted** — each row now asserts a distinct returned state/constant, and R-G7 (valid three-`trak` → `PROVEN`) defeats a blanket refuser |
| W2F-7 | code | R-B2 already passes at base (old guard emits the same prefix) | **Accepted** — R-B2 now requires a *distinguishable* refusal, not merely a refusal |
| W2F-8 | code | R-B4's premise ("binds today") is false | **Accepted** — rewritten as a distinct-reason row |
| W2F-9 | code | S4 patched the wrong function (guard is in `refine_requested_candidate`) | **Accepted** — §4.2 and the plan name `refine_requested_candidate:144` and the `:281` forwarder |
| W2F-10 | code | Rule (3) `CONTAINER-UNSUPPORTED` and `build_timingless_trak_mp4` had no consumers | **Accepted** — `CONTAINER-UNSUPPORTED` dropped (timing parser owns fragmentation); the timing-less builder becomes a **positive** row proving the predicate does not require timing |
| W2F-11 | code | R-U1 is genuinely RED; write sets disjoint; no import cycle | **Confirmed** — the reproduction (`465f60ab…`) is cited in the plan |
| W2F-12 | both | Rev. 1 did not require a "does not prove" statement per slice | **Accepted** — every task packet carries one |

Not accepted, with reasons: the suggestion to *drop* bundle validation entirely (it leaves a measured live gap, `E-B1`); and the suggestion to label the proof "independent" once `B-11` lands (still producer-sealed until the artifact self-binds, and even then the demuxer property remains build-specific).

If a later reader finds a finding marked accepted but not visible in the text, the text wins; treat that as a defect, not as authority.
