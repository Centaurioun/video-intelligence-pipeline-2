# Gate-3 A-3 — Owner-approved A′-7 bounded schema decision (2026-10-25)

**Status:** `DESIGN_DECISION_APPROVED_BY_OWNER_IN_CHAT`; `SOURCE_IMPLEMENTATION_NOT_STARTED`; `INTEGRATION_NOT_AUTHORIZED_BY_THIS_RECORD`.

**Authority/provenance:** In the current ChatGPT collaboration on 2026-10-25, following independent GitHub review of `main@cb5468b320f554aa08cc767c5cfe45e63126416a`, the Owner replied **"verdiğin iki promptu başlattım. önerini de onaylıyorum."** This approves the **explicitly delimited A′-7 recommendation immediately preceding that reply**, not all of historical spec §17. This repository entry records the chat decision; it is not a fabricated GitHub approval comment. Source of previously restricted scope: PR #165 Owner clarification comment `6391392209`. Do not infer consent for operational work.

**Governing links:**
- `docs/superpowers/specs/2026-10-25-gate3-dual-temporal-authority-composition-design.md` — approved high-level C′ / strict-V1 direction;
- `docs/agent-runs/2026-10-25-g3-cprime-v1/authority-disposition-matrix.md` — A-1…A-12 disposition;
- `docs/agent-runs/2026-10-25-g3-temporal-binding-wave3/a3-decision-proposal.md` — earlier A′ six-field proposal; now superseded **only for A-3's bounded D-1…D-5 decision**;
- `docs/agent-runs/2026-10-25-g3-temporal-binding-wave3/v1-evidence-baseline.md` — measured V1 compatibility;
- `docs/agent-runs/2026-10-25-g3-temporal-binding-wave3/independent-review.md` — previously identified D-4 sketch defect.

## Exact accepted scope (D-1…D-5)

**D-1 — Additive schema v2.** Reuse existing snapshot binding identity, retained-byte verification and canonical SHA-256 evidence seal. New `schema_version: 2` has a separate creation entry point; existing v1 generation and v1 verification remain intact (subject to the already authorized A-9 strict origin-zero refusal). No separate composed-artifact implementation is approved by this decision.

**D-2 — Closed v2 payload, exactly seven *additional* keys.** Preserve the existing 13 v1 body key names/types and add:
1. `duration_ts`: exact nonnegative `int`, from ISO-BMFF `mdhd`;
2. `duration_consistency`: exact `"MATCH" | "MISMATCH"`; **derived comparison** from measured duration and measured presentation/tail, **not an independent observation**;
3. `tail_duration_ticks`: exact positive `int`, from last `stts` delta;
4. `presentation_origin_ticks`: exact `int` and must equal **0** for strict V1; any nonzero value refuses without normalizing;
5. `stream_handler`: exact `str`, from `hdlr`; for selected video track require `"vide"`;
6. `stream_identity_derivation`: exact nonempty `str` naming the parser's actual selection mode; this **does not prove** equality with an FFprobe global stream index;
7. `composition_offsets`: ordered list of exact signed `int` values from `ctts`, **aligned one-to-one with `dts_ticks` in decode/sample order**. Its length must equal `len(dts_ticks)`; check `sorted(dts_ticks[i] + composition_offsets[i]) == pts_ticks` (including duplicate ticks, without `set` or nominal frame-rate arithmetic).

Result: **20 body keys + `evidence_sha256` = 21 total evidence keys**, closed exact set. The digest covers `schema_version` and all 20 body keys with the existing canonical JSON domain. No caller-supplied temporal facts are accepted. The existing parser supplies the seven source facts; do not alter frozen `src/gate3/container.py`.

`nb_frames` is derivable as `len(pts_ticks)` and excluded. Do not add `has_b_frames`: the current binder's `sorted(pts) != dts` reordering predicate has measured false-positive/false-negative cases and is *not* a correct proof of underlying per-sample reordering. Adding offsets preserves data to support a **future separately dispositioned** composition/reordering decision; it does **not** authorize changing the current reordering acceptance predicate in this slice.

**D-3 — Two creation paths, version-pinned verification.**
- Existing `SourceSnapshotStore.bind_temporal_authority(snapshot, *, selected_stream_index, declared_vfr, declared_reordering)` keeps its exact public signature, historical 14-key v1 evidence shape (13 body + digest), DTS-deltas+tail VFR predicate and refusal expectations.
- New `SourceSnapshotStore.bind_temporal_authority_v2(snapshot, *, selected_stream_index, declared_vfr, declared_reordering)` creates v2 with the **presentation-delta-only VFR** predicate already supported by A-2, with no tail in the classification basis.
- Existing `verify_temporal_authority(snapshot,evidence)` discriminates versions before applying version-specific closed field sets, recomputes from retained source bytes using the matching version, and never upgrades/downgrades. Preserve pinned refusal code for a legacy v1 receipt whose `schema_version` is merely relabelled `2` (`SNAPSHOT_TEMPORAL_EVIDENCE_BINDING_MISMATCH`); a mixed/partial payload must refuse.
- No new `TEMPORAL_AUTHORITY_*` error code is introduced here.

**D-4 — Narrow safety-test amendment, not the earlier illustrative AST sketch.** Replace the single overbroad `duration_ts` token ban in `tests/vip_fvs/adversarial/test_source_snapshot_temporal_safety.py` only as needed for v2. Static/AST tests must distinguish authenticated parser-result field access, permitted closed evidence dictionary-key serialization, and forbidden nominal-rate field reads or nominal-FPS arithmetic. Add *behavioral/mutation negative controls* for aliased/untrusted values, bad types (including bool), fabricated duration/offsets, and altered digest/bytes. AST field-position inspection alone **cannot prove full dataflow provenance**: retained-byte remeasurement, exact mapping checks and tamper refusals are the actual safety proof. Do not weaken the untouched modules' nominal-rate bans.

**D-5 — Consumer version sufficiency.** Any future v2-only consumer must explicitly refuse v1 evidence, never infer version sufficiency by presence of fields, and must re-verify at consumption. Exact stable consumer refusal-code naming remains **PENDING A-5**; this decision does not introduce a consumer nor its error code.

## Boundaries / residual dependencies

- **Strict V1 origin-zero** always; nonzero `elst.media_time` is unsupported and must refuse `EDIT_LIST_ORIGIN_NOT_APPLIED`, never offset-normalized.
- **A-1 composition placement, A-5 stable names, A-6 dedicated composition module, A-7 FFprobe-global↔ISO-BMFF track correspondence, A-11 provenance derivation, and A-12/IT-6 terminal-tail policy remain PENDING** where not already narrowly authorized.
- **IT-8 remains PARKED_BLOCKED**. A′-7 does not invent a snapshot in the fixture chain or establish stream mapping.
- The existing third `xfail(strict=True)` tied to duration-consistency enforcement remains deliberately RED/PENDING A-12. A v2 `"MISMATCH"` status is sealed, not automatically refused.
- No edits under `src/gate3/**`, Gate-0, shared preview/verifier, and no change to v1 historical evidence contracts in this scope.
- No protected/real archive operations, local/authentic model load/download, MPS/provider calls, real edits/renders/exports, production/Gate promotion or modification to the frozen Owner backup.
- **Development-source authorization enforcement remains `DISABLED_BY_OWNER`** under ADR-0003; do not reintroduce grant bureaucracy.

## Delivery / evidence requirement

Follow `docs/superpowers/plans/2026-10-25-g3-a3-aprime7-snapshot-v2-implementation.md` **after plan review** in a distinct exclusive-writer worktree. TDD RED→GREEN against generated disposable ISO-BMFF fixtures; verified compatibility, negative mutations, relevant full suites and PR CI. Commit to an isolated source branch and open a PR; do **not** auto-merge into canonical main. Keep the two independently running Owner-launched Gate-3 A-7 and Gate-0 preparation lanes untouched.

**Six-cycle disposition:** live source/contract evidence → owner authority delta → three alternatives (A′-7 selected; six-field A′ narrower; separate-artifact B deferred) → bounded plan → adversarial v1/PTS/AST tests → independently verified PR before any integration claim.

## Addendum 2026-10-25 (label-only clarification; approved text above unchanged)

This addendum corrects an identifier alias introduced after this decision was recorded. It changes no
authorization, no schema and no behaviour.

- The decision item labelled `A-12/IT-6` above is the **terminal-duration / stream-tail policy question**, whose canonical governing identifier is **`IT-6 (G-4)`** (design `:394`; authority matrix verdict (c), `PENDING`).
- **`A-12`** in the design §17 / authority-matrix numbering is a *different* item: consumption-time re-verification of composed evidence (IT-5) plus the Dv-13 rule that composition never hands `refine()` a non-member end. `A-12` is **not** renumbered and is **not** the tail policy.
- The third `xfail(strict=True)` referenced above is the **`DC-BIND`** tripwire (`tests/vip_fvs/adversarial/test_temporal_evidence_v1_matrix.py:376-400`); it remains deliberately RED.
- Lane-C owner items are referenced as `LC-A-*` to avoid collision with the C′ matrix `A-1…A-12` numbering.
- The disposition packet for `IT-6` is `docs/decisions/2026-10-25-g3-g4-terminal-tail-disposition.md`. Nothing above is relaxed by it: strict V1 origin-zero stays in force, the v2 `"MISMATCH"` status remains **sealed and not automatically refused**, and no tail acceptance is authorized here.
