# Gate-0 D-2 Owner-Input Readiness and Contract Crosscheck (2026-10-25)

**Report ID:** `VIP-G0-D2-INPUT-READINESS-20261025`
**Baseline:** local `main` and local remote-tracking `origin/main` both read `813f1982416fda7cb5619c903a607df148df2140` on 2026-10-25. No fetch was performed (no network use), so live remote state is `NOT_OBSERVED`; this is local-ref evidence only.
**Owner packet:** PR #182, pinned commit `4a65bff0904c60163bf501014e07fbe5d4239cfc`, file `docs/gate0/OWNER_AUTHORIZATION_INPUT_PACKET_2026-10-25.md`. This report cites that pinned packet; it does not replace, rebase or amend it.
**Merged D-1 software:** PR #187 (`7ed1c2920`, P-09 config-freeze inspector), PR #188 (`e52468679`, P-05 reviewer envelope), PR #189 (`3bccc4ee2`, P-08 `authorized_local` declaration/preflight), reconciliation PR #190 (`053a1a562`).
**Status:** `D2_INTAKE_PARTIALLY_READY` · `D2_INPUTS_PENDING` · `D3_EXECUTION_NOT_AUTHORIZED` · `GATE0_EXPERIMENT_NOT_RUN` · `DOCUMENTATION_ONLY_NO_OPERATIONAL_GRANT`.
**Companion checklist/matrix:** `docs/gate0/D2_OWNER_INPUT_INTAKE_CHECKLIST_2026-10-25.md`.

This report grants no permission. Filling an input document, committing a synthetic fixture, or opening this PR cannot grant file-reading, probing, model-loading or execution rights. Only a separate, explicit D-3 operational authorization can do that.

---

## 1. Question and method

The question is not "is the Gate-0 software finished?" It is: **which genuine Owner inputs and operational permissions are still missing before the Gate-0 experiment can leave D-1 software preparation, and can the merged D-1 validators actually accept those inputs when supplied?**

Method:

1. Verified local `main` and the merged D-1 ancestry; read the canonical WBS, handoff, experiment contract, implementation spec v1.1, v1.1.1 erratum, canonical contracts, the D-1 decision record and the D-1 plan.
2. Read the P-08 declaration/refusal path, the P-05 reviewer envelope, the P-09 freeze inspector, the frozen config schema, the policy/egress gate and the preflight path.
3. Compared those interfaces against the experiment contract and PR #182's prerequisite ledger P-01…P-11.
4. Ran the targeted D-1 tests read-only against the clean baseline (no real media, model or network):

   ```text
   cd /tmp/vip-d2-base   # detached at 813f19824, clean
   PYTHONPATH=src:experiments:scripts \
     /Users/yusuf/Repos/video-intelligence-pipeline/.venv/bin/python -m pytest -p no:cacheprovider -q \
     tests/gate0/media/test_authorized_local_d1_declaration.py \
     tests/gate0/unit/test_authorized_local_d1_refusal.py \
     tests/gate0/unit/test_authorized_local_d1_label_seams.py \
     tests/gate0/unit/test_authorized_local_d1_model_seam.py \
     tests/gate0/unit/test_reviewer_envelope_d1.py \
     tests/gate0/unit/test_config_freeze_d1.py
   # 281 passed in 0.22s (Python 3.14.9, pytest 8.3.3)
   ```
5. Exercised only artificial metadata and existing synthetic fixtures. No archive path was opened, enumerated, stat-ed, hashed, probed or decoded; no authentic model was downloaded or loaded; no provider/network call was made.
6. Applied independent review and the six-cycle refinement record in §11.

Evidence classes are used as the repository requires: `MEASURED` only for commands actually run; `MATCHED` for source-to-claim correspondence; `NOT_OBSERVED` for absent real-world state. Absence of evidence is never reported as a pass.

---

## 2. Verdict

The approved D-1 software deliverables are merged and their targeted suite passes (G0.1.4 itself remains unchecked in the WBS), and the hard refusal behaviour is real: the D-3 gate is a literal `return False`, and a declaration file cannot grant access (`src/gate0/execution.py:1595-1603`, `src/gate0/execution.py:1711-1743`, `src/gate0/cli.py:241-248`).

D-2 is **not ready to be accepted as a complete input package**. Of the 30 required field rows in the companion matrix:

| State | Count | Meaning |
|---|---:|---|
| `VERIFIED` (genuine input present and validated) | 0 | No authentic corpus, query, reviewer, model or host input exists yet. |
| `PENDING` (Owner/editor action alone can close) | 7 | Text-only designation or decision; the repository can record/validate it without a code change. |
| `BLOCKED` (cannot be accepted even if supplied) | 21 | A schema field, format, validator, tool or contract-owner ruling is missing, or closure depends on a not-authorized operation. |
| `NOT_OBSERVED` (real observation absent) | 2 | Human-judgment and post-run audit evidence cannot exist before real review/execution. |

More important than the counts, **three structural facts** make a naive "collect the documents" plan fail:

1. **The frozen config schema cannot carry values the code requires.** `schemas/gate0/config.json:10` permits nine model fields and `additionalProperties:false`; it has no `licence`, `runtime_precision`, `model_root`, `revision` or `preprocessing_digest`. `model_preconditions` blocks on `runtime_precision` and `licence` (`src/gate0/execution.py:1548-1592`), and `_sandbox_binding_present` requires `sandbox.sandbox_id` (`src/gate0/execution.py:1536-1546`), which the sandbox schema also does not permit (`schemas/gate0/config.json:15`). A genuine model/host binding therefore **cannot be represented today**.
2. **Several permission artifacts have no defined format at all.** Rights basis, egress manifest, Owner-authored discovery authorization, execution authorization, adjudication provenance, reviewer independence, promotion record and configuration-freeze approval are required by the contract/decision record but have no schema or accepted form. `config/gate0/default.json` carries placeholder values (all-zero digests, `NOT_OBSERVED` identities, `weights_digest: null`, `dimension: 0`, a fixture review root); a freeze inspector can compare equality but cannot authenticate (`src/gate0/config_freeze.py:257-286`, `:326-337`).
3. **There is no real-corpus execution path, and the CLI child-attestation path cannot succeed.** Both branches of `_preflight_binding` return exit `20` (`src/gate0/cli.py:52-91`); the only exit-0 preflight is the in-process synthetic/fixture stage path (`src/gate0/execution.py:808-839`), and the CLI dispatches only synthetic or fixture-media inputs (`src/gate0/cli.py:265-290`). Linux-only bwrap/interpreter requirements are hard-coded (`scripts/gate0-run.sh:11-17`), and this dev host has neither binary.

Consequently D-2 can start **now** only on the text-only workstream: corpus designation, rights/policy drafting, 40 editor queries, reviewer/adjudicator appointment, model identity/licence paperwork, host choice, and the contract-owner ruling queue. It cannot yet be closed, and it cannot be converted into real-media review or a scored run.

---

## 3. D-2 versus D-3: the boundary that must not leak

`D-1/D-2/D-3` is packet/WBS vocabulary. The words appear zero times in `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md`, `docs/implementation-spec-v1.1.md`, the v1.1.1 erratum and `docs/architecture/CANONICAL_CONTRACTS.md`; the governing documents instead speak of Owner corpus/policy approval before execution (`docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md:14-15`), discovery versus processing authorization (`docs/architecture/CANONICAL_CONTRACTS.md:127-133`), and explicit user approval (`docs/implementation-spec-v1.1.md:288-294`). The mapping below is therefore an interpretation, not a contract quotation.

| | D-2 (information and decisions) | D-3 (operational authorization) |
|---|---|---|
| Nature | Text, identifiers, digests, policy choices, appointments, signed declarations | Explicit permission to perform real operations |
| Examples | corpus session/revision list; rights basis; retention choices; 40 query texts; reviewer names; model identity/licence; host choice; no-egress statement; contract rulings | mount/read named real root; DISCOVER/HASH/PROBE inventory; reviewers inspect real media; load authentic weights; decode/embed/rank/evaluate; scored run |
| Media contact | **None** | The only layer that may contact real media/model |
| Can it be granted by an input document? | It is itself an input declaration | No — requires a separate explicit authorization record authored for that purpose |
| Current state | Partially ready; 7/30 rows closable | `NOT_AUTHORIZED`; no artifact format exists |

Two consequences follow, and they are load-bearing:

- **Reviewer access is not covered by D-2.** The D-1 decision record already says reviewer access to a real evaluation corpus requires explicit real-source access permission, and that PR #182 §6's critical-chain suggestion is not that grant (`docs/decisions/2026-10-25-gate0-d1-source-only-preparation-approved.md:25`). Text-only query/rubric templates require no media access. Real corpus inspection by the two reviewers needs its own explicit grant.
- **Discovery/inventory is itself an operation.** Contract-required inventory fields (occurrence/revision identity, selected stream, locator, byte/hash/probe evidence) cannot be produced by filling a form. They require a bounded `DISCOVER/HASH/PROBE` authorization over a named root, distinct from the later processing authorization (`docs/implementation-spec-v1.1.md:76`, `docs/architecture/CANONICAL_CONTRACTS.md:127-133`). D-2 can declare the intended scope; D-3 must authorize the act.

Recommended interpretation for Owner approval: **D-2 ends at a signed, text-only input package; every byte-level read, hash, probe, decode, weight load and scored evaluation is D-3.** If the Owner prefers a different line, that is itself a contract-owner ruling (R-15 below).

---

## 4. Field-by-field completeness matrix

The complete 30-row matrix, with accepted format, deterministic validation rule, closure evidence and current validator coverage, is the companion document `docs/gate0/D2_OWNER_INPUT_INTAKE_CHECKLIST_2026-10-25.md` Part B. Summary by domain:

| Domain | IDs | State at baseline | Key obstacle |
|---|---|---|---|
| Corpus, rights, policy | G0-D2-01…09 | 1 PENDING, 8 BLOCKED | Rights basis, retention binding, egress and Owner-authored ALLOW records have no format; declaration accepts optional digests and cannot bind retention |
| 40 editor queries and freeze | G0-D2-10…13 | 3 PENDING, 1 BLOCKED | Editor texts absent (readiest real work); freeze/approval artifact and approved config-digest anchor absent |
| Reviewers, labels, audit | G0-D2-14…19 | 2 PENDING, 2 BLOCKED, 2 NOT_OBSERVED | Independence criteria and adjudication provenance undefined; real review access ungranted; top-ten audit needs a run |
| Model, runtime, host, deps | G0-D2-20…23 | 4 BLOCKED | Config schema cannot carry licence/precision/root/revision/preprocessing or `sandbox_id`; torch/transformers unlocked; real preflight cannot succeed |
| Freeze, authorization, acceptance | G0-D2-24…30 | 1 PENDING, 6 BLOCKED | No execution-authorization, discovery-authorization or promotion-record format; D-3 prohibited |

`VERIFIED` on any owner-input row requires an authentic artifact plus a passing validator. None exists. `NOT_OBSERVED` here is an availability condition, not an evidence class.

---

## 5. Exact missing Owner inputs (decision-ready)

These asks are text-only unless marked otherwise. D-3 asks are deliberately separate in §5.3.

### 5.1 D-2 corpus, policy and model decisions

| Ask | Exact question to the Owner | Accepted form | Blocking issue |
|---|---|---|---|
| D2-A1 Corpus designation | Name the already-local sessions/revisions (>=3 sessions, >=6 revisions, 60–120 min) and the intended family coverage | Text table: session, revision ID, duration, selected stream, family coverage | Inventory digests need D-3 discovery; declaration only records identities |
| D2-A2 Rights basis | What right/ownership basis permits this evaluation, and who attests it? | Signed statement naming authority, scope, constraints | No format/schema; declaration policy only permits `{"local_only": true}` |
| D2-A3 Source-use and retention | For each revision, which retention class applies, expiry, readers, deletion action? | Table mapped to `config/gate0/default.json` retention classes | No per-revision retention field in declaration; no D-2 artifact schema |
| D2-A4 Sensitivity/consent | Is the material sensitive, and what consent/ethics constraint applies? | Enum choice + note | Enum exists only in runtime schema; no D-2 record |
| D2-A5 Inclusion/exclusion | Which revisions/windows are excluded, and why? | Per-revision reason list | No declaration field for reasons; source manifest requires it later |
| D2-A6 Relations and split | Which revisions are exact-byte/transformed/partial-copy/same-session groups, and which single development revision/window set is source-disjoint? | Relation pairs + split table | `relation_kind` enum undefined; declaration checks only structural split |
| D2-A7 Egress/no-network | What is the local-only/no-egress statement and the egress-manifest content? | Policy text + digest + manifest rows | Egress-manifest format is `NOT_OBSERVED`; only a 64-hex digest is echoed |
| D2-A8 Model identity | Which offline model revision, weights SHA-256, public licence, processor digest, preprocessing definition, runtime precision, dimension and space ID? | Identity table + vendor licence evidence | `licence`, `runtime_precision`, `model_root`, `revision`, `preprocessing_digest` are not representable in the frozen model schema |
| D2-A9 Host choice | Linux bwrap host (recommended by PR #182) or macOS Stage-B design? | Explicit choice + rationale | macOS Stage-B is `NEEDS_WORK`; Linux host provisioning/attestation is operational (D-3-adjacent) |
| D2-A10 `gate_owner_id` | Which identity is the Gate-0 owner/authority? | Exact string | Config placeholder `gate0-owner`; equality check exists |
| D2-A11 Freeze approval | Does the Owner approve the exact frozen configuration once complete? | Signed decision with `config_digest` | No approved config-digest anchor; config incomplete |

### 5.2 Editorial and human-review decisions

| Ask | Exact question | Accepted form | Blocking issue |
|---|---|---|---|
| D2-B1 24 positive queries | Supply 24 positive queries, exactly 6 per family, in the editor's own language, no translation/rewrite/model derivation | `queries.jsonl`-compatible rows + family tags + language | None in principle — readiest real work; loaders exist but are unwired |
| D2-B2 8 plausible-absent queries | Supply 8 plausible-absent queries under the same editorial-language rules | Rows + absent semantics | Absent-query rubric awaited (R-13) |
| D2-B3 8 development queries | Supply 8 development queries, distinct from the evaluation set | Rows | None beyond loader wiring |
| D2-B4 Reviewers and adjudicator | Names/identities of the two independent reviewers and the adjudicator | Signed appointment list | Reviewer-independence criteria absent (R-01); adjudication format absent (R-02) |
| D2-B5 Independence | What makes the two reviewers independent of each other and of the model/ranker build? | Declaration per reviewer (role, conflicts, no prior access to rankings) | No field/criteria; editor-as-reviewer not distinguishable |
| D2-B6 Adjudication | Who adjudicates disagreements, by what procedure, and what record proves it? | Procedure + record template | No field; envelope requires equal final grades but discards adjudication provenance |
| D2-B7 Blinding values | Real reviewer-visible/hidden fields and token map (values need not be secret now) | Table matching config blind fields | Config supports token map; real access scope unmodeled |
| D2-B8 Review access boundary | Do reviewers inspect real media under D-2, or only after a separate real-source access grant? | Owner ruling | Most consequential boundary ambiguity; decision record implies a separate grant (R-12) |

### 5.3 D-3 operational authorization (not granted by any D-2 document)

| Ask | Scope that must be explicit |
|---|---|
| D3-AUTH-1 Discovery/inventory | Named real root; operations limited to `DISCOVER/HASH/PROBE`; authority, custody, purpose, expiry, decision record; no processing |
| D3-AUTH-2 Reviewer real-media access | Named corpus root; which reviewers/adjudicator; read-only inspection only; no egress; expiry; blinding and independence conditions |
| D3-AUTH-3 Processing/execution | Authentic model root + weight load; extract/embed/rank/evaluate; run IDs and budgets; no network/provider/cloud; no production export; no Gate promotion; one bounded attempt set |

Each is a separate permission. A single "go ahead" that blurs discovery, reviewer access and scored execution should be treated as incomplete and sent back for clarification.

---

## 6. Existing-code validation coverage

Test evidence: the six targeted D-1 files pass (`281 passed`). That means the code does what its tests say; it does **not** mean the code enforces the full contract.

### 6.1 P-08 `authorized_local` declaration and refusal (merged #189)

| Aspect | Evidence | Assessment |
|---|---|---|
| Declaration recognised only by fixed filename `authorized-corpus.json` in a synthetic path | `src/gate0/media_experiment.py:91-106` | Enforced |
| Locator lexical safety, no resolution, no backslash/absolute/`..`, one development revision, evaluation coverage, relation pairs, provenance placeholder ban, policy only `local_only` | `src/gate0/media_experiment.py` declaration validator | Enforced |
| Declared sources are never opened/stat-ed/hashed/probed; only the declaration file itself is read (2 MiB cap) | `src/gate0/media_experiment.py`; `src/gate0/execution.py:1703-1708` | Enforced; `MEASURED` by tests |
| Hard refusal before input load; exit 20; gate literal `False` | `src/gate0/execution.py:1595-1603`, `:1711-1743`, `:1754-1759`; `src/gate0/cli.py:241-248` | Enforced and fail-closed |
| Rights attestation, content SHA-256, retention policy, model licence, sandbox binding | `src/gate0/media_experiment.py:306-312` | Declared blockers only — no acceptance record exists |
| Over-permissive declaration surface | `declared_byte_count` may be 0, digests may be null, relations may be empty, provenance has no required keys | **Fix candidate** |
| P-08 execution wiring (manifest projection, editor/gold loaders, LocalSiglip adapter, decode_pixels, lock) | loaders exist but no stage calls them; `measure_corpus` has no `decode_pixels`; `_representations` hardcodes the fake embedding adapter; `requirements/gate0.lock` is `pytest==8.3.3` only | **Absent / unwired**; D-3-adjacent |

### 6.2 P-05 reviewer envelope (merged #188)

| Aspect | Evidence | Assessment |
|---|---|---|
| Closed envelope/row schema; two reviewers per query/window/token; exactly two identities; one token map; grades 0/1/2; blinding scan; atomic root-contained write | `src/gate0/reviewer_envelope.py:76-92`, `:283-344`, `:511-580` | Enforced |
| Consumer un-blinds into `window_judgments.jsonl` | `src/gate0/execution.py:927-990` | Wired for evaluation only |
| Query/window coverage cardinality | `validate_reviewer_envelope` accepts a 4-row/1-query envelope; `known_query_ids` is subset-only (`src/gate0/reviewer_envelope.py:347-376`); `evaluate` checks only a 24-query count | **Absent / over-permissive**; under-coverage can yield silent 0-hit metrics instead of `INVALID_PROTOCOL` |
| Digest pinning of the review input before ranking | `expected_input_digest` exists in `load_reviewer_input` (`src/gate0/evaluation.py:99-113`) but is never passed; digest is recorded after the fact | **Absent**; needs freeze-artifact ruling |
| Assertion digest semantics | shape-only 64-hex, never recomputed or cross-checked (`src/gate0/reviewer_envelope.py:132-135`, `:283`) | **Over-permissive** |
| Inclusion/exclusion reason binding | contract requires a per-revision reason (`docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md:26-27`), but the declaration has no reason field and `source_manifest.json` carries only `source_status` | **Contract surface gap**; row G0-D2-07 is `BLOCKED` |
| Independence / editor-as-reviewer / adjudicator provenance | expected reviewer identity is not passed at `src/gate0/execution.py:954-957`; adjudication provenance discarded | **Absent** |
| Real authorized root | `config/gate0/default.json` review root is `tests/gate0/fixtures/review-input` | **Fixture-bound** |

### 6.3 P-09 freeze inspector (merged #187)

| Aspect | Evidence | Assessment |
|---|---|---|
| Canonical config digest, frozen schema load, placeholder/zero rejection, observation equality, no media/model/source I/O (the inspector reads the frozen config schema file) | `src/gate0/config_freeze.py:172-177`, `:257-286`, `:326-337` | Implemented and tested |
| Authenticity | constants `authentic=False`, `freeze_state=NOT_FROZEN`, `approval=NOT_GRANTED`, `gate_verdict=NOT_RUN`; the canonical config digest and schema digest are derived locally, as are the policy-root path hash and launcher argv/mount digests; observed entity digests remain caller-supplied equality checks | Correctly refuses to claim authenticity |
| Owner-supplied digests | equality is not authenticity: fabricated equal digests yield `READY_FOR_FREEZE_REVIEW` with `authentic=False` | **Over-permissive if read as acceptance**; envelope wording must stay `READY_FOR_FREEZE_REVIEW`, never `FROZEN` |
| Blind-mapping digest | runtime recomputes the mapping digest with a hard-coded zero config digest (`src/gate0/execution.py:639`, `:954`; `src/gate0/evaluation.py:96`) rather than the run's real config digest | **Contract-incompatible**: a digest that binds the real config digest cannot match the runtime value |
| Source-manifest digest | accepted but never consumed by run/manifest paths | **Dead field** |
| Real preflight success | `_preflight_binding` returns exit 20 on both branches (`src/gate0/cli.py:52-91`); the in-process synthetic/fixture stage path can return 0 with `host_sandbox_observation=NOT_OBSERVED` (`src/gate0/execution.py:808-839`) | **Absent for real mode**; D-3 cannot start |
| Config schema completeness | no `licence`, `runtime_precision`, `model_root`, `revision`, `preprocessing_digest`, `sandbox_id`; `additionalProperties:false` | **Contract-incompatible**; values cannot be supplied |
| Dependency lock | `requirements/gate0.lock` only `pytest==8.3.3`; torch/transformers undeclared and installs prohibited in D-1 | **Blocked** |

### 6.4 Duplicated, absent, permissive and incompatible checks

- **Duplicated:** coverage arithmetic exists in both the declaration path and evaluation path; two model-precondition views report different blocker sets (6 blocker constants vs 8 missing fields); mapping-digest construction is duplicated between `evaluation.py` and `execution.py` with a hard-coded zero config digest; freeze/digest knowledge is repeated across modules.
- **Absent:** D-2 completeness validator; rights/retention binding; egress-manifest schema; Owner-authored discovery/execution intake (the runtime discovery schema exists); reviewer independence and adjudication provenance; coverage cardinality; top-ten-union audit format; promotion record; real preflight success; approved config-digest anchor.
- **Overly permissive:** declaration optional digests/zero byte count/empty relations; envelope minimum 4 rows and subset ids; shape-only assertion digest; loader length-checks only two digest fields (`src/gate0/config.py:131-132`); inspector equality vs authenticity; `execution_authorized` argument is inert.
- **Contract-incompatible:** unrepresentable model licence/precision/root/revision/preprocessing and `sandbox_id`; blind-digest formula mismatch; dead `source_manifest_digest`; `_preflight_binding` always returns 20 (fixture/media stage dispatch can still return 0 with sandbox observation `NOT_OBSERVED`); pytest-only lock against a frozen Python 3.11.9 runtime and a semantic model arm.

---

## 7. Contract-owner rulings required before D-2 can close

These are design/contract decisions, not code tasks. Each should be recorded as an explicit ruling with an owner and date; several change frozen surfaces and therefore need the same governing-decision discipline the D-1 decision used.

| ID | Ruling needed | Why it blocks |
|---|---|---|
| R-01 | Reviewer independence criteria (and whether the editor may review) | No enforceable rule; self-review would invalidate the label claim |
| R-02 | Adjudication record format and provenance fields | Envelope proves equal final grade, not adjudication |
| R-03 | Rights-basis format and who may attest it | No schema/field; cannot be accepted as evidence |
| R-04 | Where a revision's retention class is bound (declaration vs policy record vs config) | Declaration cannot express it; config retention classes are global |
| R-05 | Egress-manifest contents and authority | Only a 64-hex digest exists; impossible to validate |
| R-06 | Model `licence` and `runtime_precision` representation (and `model_root`/`revision`/`preprocessing_digest`) | Code blocks on them; frozen schema forbids them |
| R-07 | `sandbox.sandbox_id` representation | Code blocks on it; schema forbids it |
| R-08 | Host choice: Linux bwrap vs macOS Stage-B | Determines feasibility, code and authorization path |
| R-09 | Discovery authorization ownership and its relation to D-3 | Runtime schema exists and is enforced (`schemas/gate0/discovery_authorizations.json`), but it is PDP-emitted; no Owner-authored intake/loader, and the contract requires this authorization separately |
| R-10 | Execution authorization artifact format and authority | Gate is hard-coded closed; no way to open it legitimately |
| R-11 | Configuration-freeze approval format and approved `config_digest` anchor | Inspector cannot authenticate; freeze has no acceptance record |
| R-12 | Reviewer real-media access: D-2 or a D-3-scoped grant? | Determines when human work can start |
| R-13 | Query-family certification and absent-query semantics | Editors need a rubric; metrics treat absent queries separately |
| R-14 | Corpus coverage and dev-duration measurement rules | Contract states intents; exact validation is undefined |
| R-15 | Promotion/acceptance record format | No signed artifact exists; Gate cannot be promoted legitimately |
| R-18 | Post-ranking blinded top-ten-union audit artifact format | Contract requires the audit but no record format exists; cannot be produced before a scored run |
| R-16 | `sensitivity_consent` rule and `relation_kind` enum | Schema/enum gaps |
| R-17 | Discovery `purpose` spelling (erratum vs schema enum) | Contract-internal inconsistency |

Until these are ruled, the matrix rows marked `BLOCKED` cannot honestly move to `VERIFIED`, even if an Owner supplies a value.

---

## 8. Critical-path dependency order

```text
[now, text-only]
  Owner D-2 decisions (rights, corpus designation, retention, egress statement, host choice, model licence/identity)
  Editor workstream (40 queries)          Reviewer appointment + independence declaration
  Contract-owner rulings R-01…R-18
        │
        ▼
  D-2 intake package + D-2 completeness validator (PKT-D2-1)
        │
        ├── schema/format fixes after rulings (PKT-D2-4) ── config with real values ── freeze approval (R-11)
        │
  D-3-AUTH-1 discovery/inventory over named root (separate grant)
        │
        ▼
  source inventory + source_manifest_digest + relations + split freeze
        │
  D-3-AUTH-2 reviewer real-media access (separate grant)
        │
        ▼
  two-reviewer full-corpus catalog + adjudication ── freeze query/gold/config/threshold digests
        │
  D-3-AUTH-3 processing/execution authorization (separate grant)
        │
        ▼
  preflight (must be made capable of success) → extract/embed/rank → evaluate → blinded top-ten-union audit
        │
        ▼
  gate_decision + Owner acceptance/promotion record (R-15)
```

Hard edges: labels come only after corpus freeze; model/config/threshold digests freeze before label access; no scored run before D-3-AUTH-3; no Gate promotion without the separate acceptance record. The bold dependency that is easy to miss: **PKT-D2-4 (schema/format fixes after rulings) sits on the critical path before a real config can even be written.**

---

## 9. Minimal next READY code/test packets

Only packets that need no fresh governing design decision are marked READY. All are local-only, synthetic/artificial, and cannot open the D-3 gate.

### PKT-D2-1 — D-2 completeness validator (READY)

**Goal:** one deterministic, read-only evaluator for the companion matrix, so "the package is complete" becomes a command result rather than an opinion.
**Owned paths (proposed):** new `scripts/verify_gate0_d2_inputs.py`; new `tests/gate0/unit/test_verify_gate0_d2_inputs.py`; no edits to existing src/schemas.
**Design:** consumes a D-2 package directory of abstract JSON/Markdown records (ids only, no media paths), reuses the existing fail-closed loaders where available (`src/vip_fvs/pilot_authorization.py`, `scripts/remaining_work_authority.py`) and `inspect_freeze_readiness` for config metadata; exit `0` complete, `1` incomplete with field IDs, `2` refused/invalid. It must never resolve or read a declared corpus path.
**TDD plan:** (1) RED — tests for the 30 stable IDs, state vocabulary, duplicate/missing-ID rejection, placeholder rejection, and "a declaration cannot grant access" (no output state may be `AUTHORIZED`); run and record failure because the module is absent. (2) GREEN — minimal table-driven evaluator. (3) Negative tests: rights text absent, digests all-zero, reviewer count ≠ 2, query counts ≠ 24/8/8, `licence` unrepresentable, D-3 ask present in a D-2 package → refuse. (4) Determinism: identical input directory yields byte-identical output.
**Acceptance:** `pytest tests/gate0/unit/test_verify_gate0_d2_inputs.py` green; run on an artificial complete package never prints `FROZEN`/`AUTHORIZED`.

### PKT-D2-2 — Reviewer-input binding fixes that the contract already implies (READY, narrow)

**Goal:** stop the evaluate stage from accepting an envelope whose blinding binding is not the run's config, and bind the two declared reviewer identities.
**Owned paths (proposed):** `src/gate0/execution.py` (prepare/evaluate mapping-digest construction and evaluate call), `src/gate0/evaluation.py` (add an optional `expected_reviewer_ids` parameter to `load_reviewer_input`; no schema change), and a new focused test file `tests/gate0/unit/test_reviewer_input_binding_d1.py`; no edits to `reviewer_envelope.py`, schemas or config. This is an ownership proposal only — a fresh task assigns it.
**Design:** thread the run's real `config_digest` into the two hard-coded mapping-digest sites (`src/gate0/execution.py:639` prepare and `:954` evaluate) and into `load_reviewer_input(config_digest=...)`; pass `expected_input_digest` only once a frozen anchor exists (R-11); add an optional `expected_reviewer_ids` parameter to `load_reviewer_input` that compares the envelope's reviewer-identity set to `config["policy"]["reviewer_ids"]` (reusing the identity rule already enforced by `reviewer_envelope.validate_reviewer_envelope(expected_reviewer_ids=...)` at `src/gate0/reviewer_envelope.py:386-398`). This is contract-implied: the envelope must stay blind, bound to one frozen configuration, and limited to the two declared reviewers.
**TDD plan:** (1) RED — tests that (a) an envelope whose mapping digest was built with the real config digest is currently refused, (b) an envelope built with the zero config digest is currently accepted when the run config digest is non-zero, and (c) a mismatched reviewer identity is currently accepted. Run and record the failures. (2) GREEN — minimal parameter plumbing only. (3) Regression: existing 89 envelope tests and the 281-test targeted set (six files) stay green. (4) Verify no real media/model access and no D-3 gate change.
**Acceptance:** zero-config/mismatched envelopes return `INVALID_PROTOCOL`; correctly bound envelope accepted; no D-3 gate change.

### PKT-D2-3 — Query/human-gold loader conformance tests (READY, characterization first)

**Goal:** prove the unwired editors/gold loaders enforce the contract's 24+8+8 and family/two-reviewer rules, without wiring them into a real execution path.
**Owned paths (proposed):** new `tests/gate0/unit/test_editor_and_gold_loader_conformance_d1.py`; if a gap is proven, a minimal additive guard in the loader module only (not the stage pipeline). File ownership to be assigned in a fresh task, not by this report.
**TDD plan:** (1) RED — tests that reject 23/25 positives, missing family, AI-rewritten/duplicate text, synthetic-label fallback, editor-as-reviewer leakage. (2) GREEN minimal guard if needed. (3) No stage wiring; no real media.
**Acceptance:** tests green; the production `_load_inputs` synthetic path is untouched.

### PKT-D2-4 — Schema/format widening and real preflight success (NOT READY — needs governing decision)

After rulings R-06/R-07/R-11 and a new explicit authorization: extend the frozen model/sandbox schema (or define an approved external binding record), add the approved freeze/acceptance artifact, and make preflight capable of a successful exit under attestation. Touches `schemas/gate0/*`, `src/gate0/config.py` (contract-frozen), `src/gate0/config_freeze.py`, `src/gate0/cli.py`, `src/gate0/stages/preflight.py`. It must not be attempted as a routine fix; it changes frozen surfaces.

### PKT-D2-5 — Real execution mode and dependency lock (NOT READY — D-3/no-install)

Wiring `decode_pixels` into `measure_corpus`, replacing the fake embedding adapter with a licensed local adapter, and adding pinned torch/transformers lock entries. Requires explicit installation/model-load authorization and a dependency decision; outside D-1/D-2 authority. Envelope producer CLI and top-ten-union audit tooling are likewise deferred until R-02/R-15.

---

## 10. WBS recommendations

No WBS edit is made in this documentation-only PR; these are recommendations for the WBS owner.

1. **Keep the merged D-1 checkmarks and add a D-2 sub-ledger.** The WBS already records D-1 P-08/P-05/P-09 as bounded partial checkmarks; add the 30-row matrix (or a stable link to it) and its per-state counts so D-2 progress is observable per field instead of one summary line. Do not re-check G0.1.4.
2. **Add a contract-owner ruling queue (R-01…R-18) as a first-class blocking dependency** of G0.1.4, with a single owner and a decision-record path. Several rulings change frozen surfaces; they need the same discipline as the D-1 decision.
3. **Record the packet-staleness note without amending PR #182:** PR #182's "P-08 missing / reviewer-envelope tool does not exist / no freeze tooling" claims are only **partially** superseded: the named artifacts now exist (#189/#188/#187), but P-08's real-corpus path, an envelope-producer CLI and an authenticating freeze remain absent (see §6). Cite PR #182 at its pinned SHA, note the stale rows, and keep the packet open. Separately, describe P-08 as "declaration/refusal merged plus unwired seams" and P-09 as a non-authenticating readiness inspector — never as a freeze.
4. **Add the schema-gap and preflight-success items** (`licence`/`runtime_precision`/`model_root`/`revision`/`preprocessing_digest`/`sandbox_id`; `_preflight_binding` always returns 20 (fixture/media stage dispatch can still return 0 with sandbox observation `NOT_OBSERVED`)) as explicit D-2-blocking engineering risks, not hidden D-3 work.
5. **Record the reviewer-access boundary** (§3): D-2 text-only preparation is allowed; real-media review requires a separate explicit grant. Do not let the WBS critical chain imply that D-2 completion enables reviewer corpus access.
6. **Keep P-08.7 dependency-lock work blocked** under the D-1 no-install/no-download rule and label it as requiring a separate dependency/authorization decision; do not schedule it as ordinary D-2 work.
7. **Add PKT-D2-1 (D-2 validator) as a READY packet** and PKT-D2-2/PKT-D2-3 as narrow READY hardening candidates; keep PKT-D2-4/PKT-D2-5 off the READY frontier until rulings/authorization.
8. **Retain PR #182 open and pinned.** It is cited at `4a65bff…` by merged authority documents; rebasing or amending it would break that provenance. This PR references it and does not replace it.

---

## 11. Six-cycle refinement record, independent review and verification

| Cycle | Work | Change produced |
|---|---|---|
| 1. Governing facts | Verified main/WBS/contract/spec/erratum/handoff/PR #182 pinned packet and D-1 merge ancestry | Confirmed the packet is OPEN, 115 commits behind main and 1 commit ahead of its base, digest-pinned; established contract-native vocabulary |
| 2. Authority audit | Read D-1 decision record and plan; separated D-1/D-2/D-3; confirmed D-3 `NOT_AUTHORIZED` and reviewer access needing separate permission | Added the D-2/D-3 boundary table and reviewer-access warning |
| 3. Interface inspection | Read P-08 declaration/refusal, P-05 envelope, P-09 inspector, config schema, policy/egress, preflight; ran 281 targeted tests | Found schema gaps, dead field, blind-digest mismatch, preflight false-success, envelope over-permissiveness |
| 4. Input classification | Built the 30-field matrix, formats, validation rules, closure evidence; classified states | 0 VERIFIED / 7 PENDING / 21 BLOCKED / 2 NOT_OBSERVED; identified readings that a packet-only view misses |
| 5. Adversarial review | Independent reviewer lane checked claims against source and limits; no real media/model/network touched | Corrections recorded in the final text; no claim promoted beyond evidence |
| 6. Verification and reconciliation | Re-ran targeted tests read-only; re-read local `origin/main` ref (no fetch); secret/limit audit; verified documentation-only diff | Report and checklist consistent with baseline; D-3 remains `NOT_AUTHORIZED` |

**Independent review:** a separate read-only reviewer (fresh context) audited this report and the companion checklist against the sources and the absolute limits, with instructions to flag over-claims, fabricated inputs, D-2/D-3 leakage and any implication of real access. It reviewed commit `7b80db520` and its findings (memo `.orchestration/gate0-d2-readiness-20261025/lanes/L7-review.md`) are applied in the follow-up commit on this PR; remaining open questions are named in §7 rather than silently resolved.

**Verification performed:**

- The local `origin/main` ref remained `813f1982416fda7cb5619c903a607df148df2140`; this PR's base is that commit. No fetch was performed, so the live remote is `NOT_OBSERVED`.
- Targeted D-1 suite: `281 passed` (read-only worktree, Python 3.14.9, pytest 8.3.3).
- No real/protected media was opened, enumerated, stat-ed, hashed, probed or decoded; no authentic model was downloaded/loaded; no provider/network call was made.
- This PR is documentation-only and does not modify code, schemas, config, fixtures, the freeze state or any authorization.

**Limitations:**

- Test counts and host observations describe this analysis environment; they are not a Linux-host attestation.
- PR #182's workload arithmetic and stale-status claims were reviewed only as packet text; the packet is not rebased.
- The D-2/D-3 boundary interpretation in §3 is a recommendation for Owner/contract-owner confirmation (R-12/R-18), not a contract quotation.

---

## 12. References

- `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md`
- `docs/implementation-spec-v1.1.md`
- `docs/implementation-spec-v1.1.1-erratum.md`
- `docs/architecture/CANONICAL_CONTRACTS.md`
- `docs/project/12_2026-10-25_FOUR_GATE_PRODUCT_COMPLETION_WBS.md`
- `docs/project/01_CURRENT_STATE_AND_HANDOFF.md`
- `docs/decisions/2026-10-25-gate0-d1-source-only-preparation-approved.md`
- `docs/superpowers/plans/2026-10-25-gate0-d1-source-only-preparation.md`
- PR #182 pinned packet: `docs/gate0/OWNER_AUTHORIZATION_INPUT_PACKET_2026-10-25.md` at `4a65bff0904c60163bf501014e07fbe5d4239cfc`
- `config/gate0/default.json`; `schemas/gate0/config.json`
- `src/gate0/{media_experiment.py,execution.py,cli.py,reviewer_envelope.py,config_freeze.py,evaluation.py,config.py}`
- `scripts/gate0-run.sh`; `requirements/gate0.lock`
