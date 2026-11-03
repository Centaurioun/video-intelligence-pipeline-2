# Gate-0 D-2 Owner-Input Intake Checklist and Evidence-Completeness Matrix (2026-10-25)

**Checklist ID:** `VIP-G0-D2-OWNER-INTAKE-20261025`
**Baseline:** `main@813f1982416fda7cb5619c903a607df148df2140`.
**Owner packet:** PR #182 at pinned commit `4a65bff0904c60163bf501014e07fbe5d4239cfc` — `docs/gate0/OWNER_AUTHORIZATION_INPUT_PACKET_2026-10-25.md`. This checklist references that packet; it does not replace it, replace its P-01…P-11 ledger, or supersede its disposition.
**Companion report:** `docs/gate0/D2_OWNER_INPUT_READINESS_2026-10-25.md`.
**Status:** `D2_INTAKE_PARTIALLY_READY` · `D2_INPUTS_PENDING` · `D3_EXECUTION_NOT_AUTHORIZED`.
**This document grants nothing.** It is a text-only intake form and status matrix. It cannot authorize reading, probing, hashing, decoding or loading any real media, model or provider. A completed form never authorizes any operation it names, and every such operation still requires a separate D-3 grant; completion is assessed per Part C independently of D-3.

---

## How to use this checklist

1. Fill Part A (Owner/editorial decisions) and attach the named evidence. Text-only work can start immediately.
2. Run the same deterministic rules in Part C (or the future `scripts/verify_gate0_d2_inputs.py`, PKT-D2-1) against the D-2 package. Do not hand-set a state.
3. Part B is the field-by-field completeness matrix. A field may only be marked `VERIFIED` by the rule in Part C, never by assertion.
4. Part D is the separate D-3 authorization request. Do **not** fold a D-3 grant into Part A or Part B; keep the three grants distinct.
5. Part E records evidence links and the acceptance signature.

**Fill conventions**

- `DIGEST` = 64 lowercase hexadecimal characters, SHA-256 over the canonical serialization named by the governing schema; never a placeholder (`"0"*64` is `PLACEHOLDER`, not a value).
- `ID` = stable ASCII identifier; no spaces; unique within its artifact.
- `PATH` = repository-relative path for D-2 text; an absolute real root may appear only inside a D-3 grant, never in a D-2 form.
- `NONE` / `TBD` are not evidence. Missing values stay blank and keep the field non-`VERIFIED`.
- A `[x]` checkbox means "value supplied and evidence attached", not "authorized".

---

## Part A — Owner and editorial decisions to supply

### A.1 Owner decisions (text-only)

| Ref | Decision to supply | Fill | Evidence to attach | Contributes to field(s) |
|---|---|---|---|---|
| D2-A1 | Authorized corpus designation: sessions, revisions, durations, selected stream, family coverage (≥3 sessions, ≥6 revisions, 60–120 min total) | `sessions =`<br>`revisions =`<br>`total_minutes =`<br>`families =` | D-2 decision record; table of identities only | G0-D2-01, 09 |
| D2-A2 | Rights/ownership basis and attesting authority | `basis =`<br>`attestor =`<br>`scope/constraints =` | Signed statement (format awaiting R-03) | G0-D2-02 |
| D2-A3 | Source-use and retention policy: per-class values and the revision→class mapping | `classes =`<br>`mapping =`<br>`expiry =`<br>`readers =`<br>`deletion =` | Policy text + mapping table (binding field awaits R-04) | G0-D2-03, 29 |
| D2-A4 | Sensitivity/consent state | `sensitivity =`<br>`consent/ethics =` | Policy text | G0-D2-04 |
| D2-A5 | Inclusion/exclusion decisions per revision, with reasons | `included =`<br>`excluded + reason =` | Per-revision table | G0-D2-07 |
| D2-A6 | Relation groups (exact-byte / transformed / partial-copy / same-session) and one source-disjoint development revision set | `groups =`<br>`development_revision =`<br>`disjointness_basis =` | Relation/split table | G0-D2-08, 09 |
| D2-A7 | Local-only/no-egress statement and egress-manifest content | `egress = none`<br>`manifest_rows =`<br>`manifest_digest =` | Policy text + manifest (format awaits R-05) | G0-D2-06, 30 |
| D2-A8 | Model identity/licence: exact model, revision, weights SHA-256, licence file, processor digest, preprocessing, runtime precision, dimension, space ID | `model =`<br>`revision =`<br>`weights_sha256 =`<br>`licence =`<br>`processor_digest =`<br>`preprocessing =`<br>`runtime_precision =`<br>`dimension =`<br>`space_id =` | Vendor/model-card evidence + digest table | G0-D2-20, 21 |
| D2-A9 | Host choice: Linux bwrap host (PR #182 recommended) or macOS Stage-B design | `host_choice = LINUX / MACOS_STAGE_B`<br>`rationale =` | Decision note | G0-D2-22 |
| D2-A10 | Gate-0 owner identity (`gate_owner_id`), equal in config and manifest | `gate_owner_id =` | Decision note | G0-D2-26 |
| D2-A11 | Configuration-freeze approval intent + approved `config_digest` once complete | `approve_when_complete =`<br>`config_digest =` | Signed decision (anchor awaits R-11) | G0-D2-13, 24 |

### A.2 Editorial and human-review decisions

| Ref | Decision to supply | Fill | Evidence to attach | Contributes to field(s) |
|---|---|---|---|---|
| D2-B1 | 24 positive queries, exactly 6 per family, in the editor's own language (no translation/rewrite/model derivation) | 24 rows | `queries.jsonl`-compatible rows + family tags + language | G0-D2-10 |
| D2-B2 | 8 plausible-absent queries, same editorial language rules | 8 rows | rows | G0-D2-11 |
| D2-B3 | 8 development queries | 8 rows | rows | G0-D2-12 |
| D2-B4 | Two independent reviewer identities and one adjudicator | `reviewer_1 =`<br>`reviewer_2 =`<br>`adjudicator =` | Signed appointment list | G0-D2-14, 16 |
| D2-B5 | Reviewer independence declaration and editor-as-reviewer status | per-person declaration | Signed declaration (criteria await R-01) | G0-D2-15 |
| D2-B6 | Adjudication procedure and record format | `procedure =`<br>`record =` | Procedure + template (format awaits R-02) | G0-D2-16, 18 |
| D2-B7 | Blinding values: reviewer-visible/hidden fields, token map, access scope | `visible =`<br>`hidden =`<br>`token_map =` | Table matching config blind fields | G0-D2-17 |

> Human work may start on **text-only** items now. Two-reviewer inspection of real media is **not** covered by D-2; it needs the separate grant in Part D.2 (see report §3).

---

## Part B — Field-by-field completeness matrix

States are computed per Part C, not chosen. Baseline counts: `VERIFIED 0 · PENDING 7 · BLOCKED 21 · NOT_OBSERVED 2`.

### B.1 Corpus, rights and policy (G0-D2-01…09)

| ID | Requirement | State | Owner | Accepted format | Deterministic validation rule / existing coverage | Closure evidence |
|---|---|---|---|---|---|---|
| G0-D2-01 | Authorized corpus: 60–120 min, ≥3 sessions, ≥6 revisions, family coverage | `PENDING` | Owner | Text table of session/revision identities + durations + families | Counts and totals computed from text; no media contact. Declaration accepts per-revision identities only (`src/gate0/media_experiment.py:91-106`) | A1 + validator exit 0 |
| G0-D2-02 | Rights/ownership basis and attesting authority | `BLOCKED` | Owner + contract-owner | Signed statement; **format undefined** | No schema/field; declaration policy permits only `local_only`; blocker identity exists (`src/gate0/media_experiment.py:306-312`). Needs R-03 | Ruling + statement + digest |
| G0-D2-03 | Source-use + retention policy binding | `BLOCKED` | Owner + contract-owner | Per-class config values + per-revision mapping | Config schema requires five classes × nine fields, but no per-revision binding field; declaration cannot express it. Needs R-04 | Ruling + policy record + config |
| G0-D2-04 | Sensitivity/consent state | `BLOCKED` | Owner | Enum value + note in policy text | Enum exists in runtime schema; no D-2 artifact. Rule awaits R-16 | Policy record |
| G0-D2-05 | Purpose-scoped ALLOW separating discovery and processing | `BLOCKED` | Owner + contract-owner | **No Owner-authored artifact format**; runtime PDP emits decisions (`src/gate0/execution.py:702-710`) | `PolicyDecision` 12 required fields validated at runtime only (`src/gate0/policy.py:18-31`); no D-2 record. Needs R-09/R-10 | Ruling + authorization format |
| G0-D2-06 | Egress-manifest content + digest / no-egress policy | `BLOCKED` | Owner + contract-owner | Policy text + manifest rows + digest; **manifest format undefined** | Only a 64-hex digest is carried/echoed (`src/gate0/execution.py:709,816`); no manifest schema. Needs R-05 | Ruling + manifest |
| G0-D2-07 | Inclusion/exclusion decisions per revision | `BLOCKED` | Owner + contract-owner | Per-revision reason table (prose) | No declaration field; the contract requires the reason at `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md:26-27`, but the source-manifest surface has no reason field, so a prose-only value cannot be machine-bound (`docs/implementation-spec-v1.1.md:75`). Needs R-14 | Ruling + schema field + validator |
| G0-D2-08 | Relation grouping (exact-byte/transformed/partial-copy/same-session) | `BLOCKED` | Owner + contract-owner | Relation pairs + kind labels | Declaration checks pairs are declared, same-split, no self, but `relation_kind` enum is undefined (R-16), so kind labels cannot be validated | Ruling + enum + validator |
| G0-D2-09 | Source-disjoint dev/eval partition (dev 10–15 min) | `BLOCKED` | Owner + contract-owner | Split table; exactly one development revision | Structural declaration checks only; measured duration/disjointness proof needs an authorized inventory read (D-3) and measurement ruling (R-14) | Ruling + D-3 measurement + validator |

### B.2 Queries and freeze (G0-D2-10…13)

| ID | Requirement | State | Owner | Accepted format | Deterministic validation rule / existing coverage | Closure evidence |
|---|---|---|---|---|---|---|
| G0-D2-10 | 24 positive editor queries, 6 per family | `PENDING` | Editor | `queries.jsonl`-compatible rows + family tags + language | Count = 24 and 6/6/6/6; exact editor text; no rewrite/AI derivative; loaders exist but are unwired (`src/gate0/execution.py:1189-1497`) | B1 + validator |
| G0-D2-11 | 8 plausible-absent editor queries | `PENDING` | Editor | rows | Count = 8; absent semantics declared; no label leakage | B2 + validator |
| G0-D2-12 | 8 development queries | `PENDING` | Editor | rows | Count = 8; distinct from evaluation set | B3 + validator |
| G0-D2-13 | Frozen query/split/gold/rubric/reviewer/config/threshold digests before preflight | `BLOCKED` | Owner + contract-owner | Signed freeze record with digests; **approval format + config anchor absent** | Inspector validates placeholders/equality but cannot authenticate; no approved `config_digest` anchor (`src/gate0/config_freeze.py:257-286`). Needs R-11 | Ruling + freeze record |

### B.3 Reviewers, labels and audit (G0-D2-14…19)

| ID | Requirement | State | Owner | Accepted format | Deterministic validation rule / existing coverage | Closure evidence |
|---|---|---|---|---|---|---|
| G0-D2-14 | Two named reviewers | `PENDING` | Owner | Two identities | Exactly 2 distinct reviewer ids; config `reviewer_ids`; envelope enforces 2 identities but evaluate does not pass expected ids (`src/gate0/execution.py:954-957`; binding defect tracked separately as PKT-D2-2) | B4 + validator |
| G0-D2-15 | Reviewer independence criteria/declaration | `BLOCKED` | Owner + contract-owner | Per-reviewer declaration; **criteria undefined** | No field/criteria; editor-as-reviewer indistinguishable. Needs R-01 | Ruling + declarations |
| G0-D2-16 | Adjudicator appointment + procedure | `BLOCKED` | Owner + contract-owner | Appointment + procedure + record; **no schema field** | Envelope accepts an optional `adjudication_ref`; when present both reviewers must record the same value and both may omit it; equal final grades are required, and adjudication provenance is otherwise discarded. Needs R-02 | Ruling + procedure |
| G0-D2-17 | Blinding values (visible/hidden/token map/access scope) | `PENDING` | Owner | Table | Exactly 2 tokens, frozen arm tokens, 2 distinct arm ids; the mapping digest is checked at execution against a hard-coded zero config digest (`src/gate0/execution.py:954`), so it does not bind the real run config; real access scope unmodeled | B7 + validator |
| G0-D2-18 | Two-reviewer full-corpus event catalog, grades 0/1/2, interval uncertainty, label version | `NOT_OBSERVED` | Reviewers | Human-gold schema rows after corpus freeze | Catalog format exists (`src/gate0/execution.py:1192-1194`), but no genuine judgment exists and real-media access is ungranted; interval uncertainty is currently unusable in the envelope (`UNCERTAIN` refused) | Real review + freeze |
| G0-D2-19 | Post-ranking blinded top-ten-union audit | `NOT_OBSERVED` | Reviewers + contract-owner | **Format undefined**; requires a scored run | No artifact format; cannot exist before a scored run. Needs R-18 | Run + audit record |

### B.4 Model, runtime, host and dependencies (G0-D2-20…23)

| ID | Requirement | State | Owner | Accepted format | Deterministic validation rule / existing coverage | Closure evidence |
|---|---|---|---|---|---|---|
| G0-D2-20 | Offline model identity/weights/processor/dimension + public licence | `BLOCKED` | Owner + contract-owner | Identity table + digest + licence evidence | `model_preconditions` blocks on licence and precision (`src/gate0/execution.py:1548-1592`), but the frozen model schema has no `licence` attribute and `additionalProperties:false` (`schemas/gate0/config.json:10`). Needs R-06 | Ruling + schema + licence evidence |
| G0-D2-21 | Runtime precision, preprocessing, pooling, space ID, tie rule frozen | `BLOCKED` | Owner + contract-owner | Definitions + digests | `runtime_precision`, `preprocessing_digest`, `model_root`, `revision` are unrepresentable in the frozen schema; run manifest expects preprocessing. Needs R-06 | Ruling + config |
| G0-D2-22 | Host + sandbox/child-boundary attestation inputs | `BLOCKED` | Owner + contract-owner | Host choice + paths/versions/digests | Linux-only scripts (`scripts/gate0-run.sh:11-17`); `_sandbox_binding_present` requires `sandbox.sandbox_id` (`src/gate0/execution.py:1536-1546`) which the schema forbids (`schemas/gate0/config.json:15`); `_preflight_binding` exits 20 on both branches (`src/gate0/cli.py:52-91`), and no real host binding is representable. Needs R-07/R-08 | Ruling + host evidence |
| G0-D2-23 | Dependency lock, no-install, BLAS/cache discipline | `BLOCKED` | Owner + contract-owner | Pinned lock with hashes/transitive closure | `requirements/gate0.lock` is `pytest==8.3.3` only; torch/transformers undeclared; D-1 forbids installs/downloads | Separate dependency authorization |

### B.5 Freeze, authorization, acceptance, discovery (G0-D2-24…30)

| ID | Requirement | State | Owner | Accepted format | Deterministic validation rule / existing coverage | Closure evidence |
|---|---|---|---|---|---|---|
| G0-D2-24 | Configuration freeze approval | `BLOCKED` | Owner + contract-owner | Signed freeze decision + approved digest; **no format** | Inspector cannot authenticate; config incomplete; no approval artifact. Needs R-11 | Ruling + freeze record |
| G0-D2-25 | Explicit execution authorization | `BLOCKED` | Owner | **No artifact format**; D-3 remains `NOT_AUTHORIZED` | Gate is literal `return False` (`src/gate0/execution.py:1595-1603`); `execution_authorized=True` is inert in the inspector | Ruling + D-3 authorization |
| G0-D2-26 | `gate_owner_id` bound and equal across config + manifest | `PENDING` | Owner | Exact identity string | Config placeholder `gate0-owner`; equality check exists (`docs/implementation-spec-v1.1.1-erratum.md:111-124`) | A10 + config |
| G0-D2-27 | Post-run Owner acceptance + signed promotion record | `BLOCKED` | Owner + contract-owner | **No signature/record format** | Cannot exist before a run; format undefined. Needs R-15 | Ruling + acceptance record |
| G0-D2-28 | Real `review_input.authorized_root` + file digest | `BLOCKED` | Owner + contract-owner | Absolute root + file digest (D-3 scope) | Current root is a test fixture (`config/gate0/default.json`); real root access unauthorized; format erratum-only | Ruling + D-3 grant |
| G0-D2-29 | Retention/cleanup/tombstone execution authority | `BLOCKED` | Owner | Policy authority + cleanup record | Spec defines retention/tombstone content (`docs/implementation-spec-v1.1.md:237-251`), but no execution authority exists | Ruling + D-3 grant |
| G0-D2-30 | Discovery authorization scope (`DISCOVER/HASH/PROBE` only) | `BLOCKED` | Owner + contract-owner | Authorization record with authority, occurrence/locator scope, custody, purpose, expiry, decision | Runtime schema exists and is enforced (`schemas/gate0/discovery_authorizations.json`; `src/gate0/contracts/validator.py:129,189,226`), but the record is PDP-emitted and needs runtime `policy_decision_id`/`decision_digest`; there is no Owner-authored intake/loader, and the contract still requires it (`docs/implementation-spec-v1.1.md:76`; `docs/architecture/CANONICAL_CONTRACTS.md:127-133`) | Ruling + intake/loader + D-3-AUTH-1 |

---

## Part C — Deterministic state rules

A field's state is a function of artifact presence, format availability, validator result and evidence digest. The same input package must always produce the same output.

```text
state(field):
  if field is an observation-only requirement (human judgment or post-run outcome)
       and source access/run is not authorized:              -> NOT_OBSERVED
  if required schema/format/validator/ruling is missing:      -> BLOCKED
  if no artifact present:                                     -> PENDING   (PENDING = the only missing step is the Owner's text-only action)
  if artifact present but incomplete, placeholder, or validator fails: -> PENDING
  if validator passes and evidence digest is recorded:        -> VERIFIED
  otherwise:                                                  -> PENDING
```

Precedence and invariants:

1. `BLOCKED` outranks `PENDING`: a value cannot be counted as pending when the repository cannot accept it.
2. `NOT_OBSERVED` is an availability condition, never an evidence class and never a pass.
3. A field may be `VERIFIED` only with authentic evidence plus a passing deterministic check; no authentic Owner input exists at baseline, so the count is 0.
4. No output state may be `AUTHORIZED`, `GRANTED`, `FROZEN` or `PASS`. D-2 completeness is not D-3 authorization and not a Gate verdict.
5. A placeholder digest (`"0"*64`), `null` where a value is required, `TBD`, empty relation list, or zero byte count is not evidence.
6. Duplicate IDs, missing required IDs, or a field ID not in the 30-row set are invalid input, not partial completion.
7. Recompute the counts by state after every submission; do not hand-edit the summary.

`validator` in these rules means the field-level acceptance check available at baseline (loader, schema validation, or declared equality rule); the aggregate `scripts/verify_gate0_d2_inputs.py` (PKT-D2-1) is not a prerequisite for classifying fields. A field whose acceptance requires a code/schema change or an unratified ruling is `BLOCKED`.

Suggested machine entrypoint once PKT-D2-1 exists:

```bash
python scripts/verify_gate0_d2_inputs.py --package <d2-package-dir> --format json
# exit 0 = all rows VERIFIED (never happens before D-3 evidence exists)
# exit 1 = incomplete; prints per-ID state and missing evidence
# exit 2 = invalid/refused input (duplicate ID, placeholder, media path in D-2 package, authorization claim)
```

---

## Part D — Separate D-3 authorization requests (not part of D-2 acceptance)

Fill nothing here as part of Part A/B. Each is a separate explicit grant with its own named scope. Any D-2 package that claims to grant these is invalid (exit 2).

### D.1 Discovery/inventory — `D3-AUTH-1`

- Named real root: `________________`
- Authorized operations: `DISCOVER`, `HASH`, `PROBE` only — no decode, no embed, no export
- Authority/custody: `________________`
- Purpose: Gate-0 source inventory, occurrence/revision identity, stream/locator evidence
- Expiry: `________________` · Revocation: `________________`
- Decision record + digest: `________________`

### D.2 Reviewer real-media access — `D3-AUTH-2`

- Named corpus root: `________________`
- Authorized persons: reviewer 1, reviewer 2, adjudicator (named in Part A)
- Allowed: read-only inspection for event catalog and top-ten-union audit
- Conditions: blinding preserved; no ranking access; no egress; no copies beyond permitted artifacts; expiry
- Decision record + digest: `________________`

### D.3 Processing/execution — `D3-AUTH-3`

- Named model root + weights digest (from A8): `________________`
- Allowed: authentic weight load; extract/embed/rank/evaluate; one bounded run set with named run IDs
- Prohibitions: no network/provider/cloud, no production export, no Gate promotion, no destructive Git, no frozen-backup modification
- Budgets: indexing ≤4 h; warm p95 ≤5 s; peak RSS ≤80% installed RAM (declared, not measured)
- Expiry/revocation: `________________` · Decision record + digest: `________________`

---

## Part E — Evidence index and acceptance

| Evidence item | Artifact ref / path (D-2 text only) | Digest | Date | Attestor |
|---|---|---|---|---|
| D-2 decision record |  |  |  |  |
| Rights/ownership statement |  |  |  |  |
| Source-use/retention policy |  |  |  |  |
| Corpus designation + relation/split tables |  |  |  |  |
| 40 editor queries |  |  |  |  |
| Reviewer/adjudicator appointments + independence declarations |  |  |  |  |
| Model licence/model-card + identity table |  |  |  |  |
| Host decision + egress statement |  |  |  |  |
| Contract-owner rulings R-01…R-18 |  |  |  |  |
| D-2 completeness validator output (PKT-D2-1) |  |  |  |  |

**Acceptance statement (to be signed only after all non-BLOCKED rows are `VERIFIED` and all BLOCKED rulings are recorded):**

> I confirm the D-2 package above is complete for the fields marked `VERIFIED`, that missing fields are listed, and that this package does **not** authorize any real-media, model, network or execution operation. Operational authorization is requested separately in Part D. Completing or signing this page creates no authority by itself.

`Owner signature/identity:` ________________ `Date:` ____________ `Package digest:` ________________

---

## Appendix — Required contract-owner rulings

R-01 reviewer independence; R-02 adjudication provenance/format; R-03 rights-basis format; R-04 retention binding point; R-05 egress-manifest contents; R-06 model licence/precision/root/revision/preprocessing representation; R-07 `sandbox_id` representation; R-08 host choice; R-09 discovery authorization format/ownership; R-10 execution authorization format/authority; R-11 freeze approval format + `config_digest` anchor; R-12 reviewer-access boundary; R-13 query-family certification/absent semantics; R-14 coverage/dev-duration measurement; R-15 promotion/acceptance record; R-16 `sensitivity_consent`/`relation_kind`; R-17 discovery `purpose` spelling; R-18 post-ranking top-ten-union audit format. See report §7 for why each blocks acceptance.
