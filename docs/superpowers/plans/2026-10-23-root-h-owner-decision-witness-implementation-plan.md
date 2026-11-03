# Root-H Owner Decision Witness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended where independently authorized) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a testable, Owner-authenticated Ed25519 decision-witness validator for Root-H accepted-dependency mutation bases without enabling real admission until an independent trust anchor and operational Owner authorization are verified.

**Architecture:** Freeze task-scoped Consumer Intent independently of the final packet; verify raw Ed25519 signatures over domain-separated JCS decision bytes; require an independently provisioned Owner key and signed, freshness-bounded checkpoint. Integrate the witness validator as a new candidate on an explicitly chosen fresh base: PR #131 (`9715d57`) and PR #132 (`0edb12a`) are **sibling** branches from `17edacbe`, and #132 does not descend from #131, so no integration base is inherited automatically. Preserve canonical and v1 behavior.

**Tech Stack:** Python 3, existing Bash/embedded Python Root-H verifier, `pytest`, Git immutable commit/blob/tree checks, RFC 8785 JCS, RFC 8032 Ed25519; approved and **locally installed** crypto/canonicalization library or separately reviewed vendored implementation required before any code/backend decision.

**Spec:** `docs/superpowers/specs/2026-10-23-root-h-owner-decision-witness-hybrid-design.md` and `docs/research/2026-10-23/boost-convergence/OWNER_ROOT_H_WITNESS_HYBRID_DESIGN_APPROVAL.md`.

## Global Constraints

- This is **an implementation plan, not an active current-write grant**. Work on new, isolated, current-authorized non-main branch/worktree with exact root/goal/implementation base, writer and all actual file paths. If the needed grant is missing, **STOP before file writes**, report exact request.
- Owner approval covers hybrid root+Consumer Intent **architecture**, not generating a real private key, provisioning production trust, issuing any real accepted dependency decision, activating dependency admission, modifying canonical main, merging PRs or granting wildcard permissions.
- Root-H current canonical-only source candidate is PR #131 at `9715d57fc898ef5ad35c17d2f14e99904c5b8be4` (sibling of PR #132 at `0edb12adac3fdeabc67bcba53112287ee4542b5c`; both branch from `17edacbe`); fixed administrative trust observed at `ae048af1898aadd30088eaf984d665b40cb8614b` (later advanced to `621385b4`), main at `17edacbe64983ae284f09a8386377200bf538ec3`. These are observations, **re-fetch before action**.
- Preserve all 141 previously reported Root-H tests (reported count only; static enumeration observed 155 `def test_*` at PR #131 and 147 in the verifier test file at PR #132 plus 22 unittest methods in the new witness test file — no pytest collection/execution count observed), v1 behavior, `dependency_authorized`, dynamic ordinal behavior, historical source-presence and canonical v2 validation. Do not merge or trust PR #128/#130 implicitly.
- The exact code filenames below are a **proposed new scope** for authorization, not previously granted paths; code writer cannot write administrative `.orchestration/` records. Admin controls are handled separately by serialized Worktree Admin with independently approved exact paths.
- Never make Portfolio Admin's write access to its own JSON, Git/CI metadata or environment equivalent to Owner issuer authority. No implicit bypass on missing anchor, crypto dependency, checkpoint/freshness, verifier integrity or clock.
- **No provider/cloud calls, network package downloads, protected media, model downloads, Gate promotion, forced Git operations or destructive cleanup.**
- Every implementation task: prove behavioral RED, narrow GREEN, inspect outputs and independent review. Full `bash scripts/verify-workspace.sh` failures remain FAIL, even if scoped Root-H suite is green.

## Normalization note (2026-10-24)

- **Lineage (R2 F4):** PR #130 (`a7f7236`), PR #131 (`9715d57`), and PR #132 (`0edb12a`) are sibling branches from `17edacbe`. This plan now treats the integration base as an explicit choice rather than an inherited PR #131 ancestry.
- **Selectors (R2 F6):** the four focused `-k` selectors in Tasks 1–4 were statically checked at PR #132 head `0edb12a`: each resolves to at least one test node (`intent`/`jcs`/`duplicate`; `checkpoint`/`anchor`/`rotation` — `rotation` alone has no match but the compounded selector resolves; `owner_signature`/`owner_ref`/`decision_replay`/`tampered_tree`/`revoked`; and `v2_real_dependency`/`v2_signed_dependency`). No selector change was required.
- **Admin surface (R2 F5):** the witness registry schema and registry record are already published in the trust tree (`root-h-owner-decision-witness-registry.v1.schema.json`; registry record `{"records": [], "no_owner_dependency_acceptance_issued": true}`). Task 6 verifies/adopts these; it does not create them.

## File responsibility map (proposed, pending exact grant)

- Create: `scripts/root_h_owner_witness.py` — pure strict JSON/JCS, Ed25519 owner decision verification, trusted checkpoint/intent validation. No private-key operations or network.
- Create: `tests/scripts/test_root_h_owner_witness.py` — synthetic cryptographic vectors and adversarial cases only, no real Owner keys.
- Modify: `scripts/verify-workspace.sh` — narrowly integrate trusted witness predicate at `_validate_v2_owner_decision_witness`, retain fail-closed default in absence of trusted anchor, and existing Root-H authority.
- Modify: `tests/scripts/test_verify_workspace_source_authorization.py` — end-to-end synthetic fixture tests and v1/canonical regressions.
- Admin lane ONLY, later (see Task 6): proposed new closed schemas for Consumer Intent, signed decision envelope, protected-anchor/checkpoint policy and index pinning under **Owner-authorized exact paths**, to be assigned by Portfolio Admin; no assumed writable paths or real acceptance.
- Separate Owner/operator provisioning: selected machine-scoped public-key anchor and protected checkpoint-floor state, plus a verified verifier-code provenance channel. **NOT performed by this implementation task.**

## Review Focus — Five highest-risk negative classes

1. **Admin changes local key/anchor location** through an environment variable, mutable config or symlink: reject unless independently provisioned trust policy authorizes the identity (Tasks 0, 2).
2. **Packet / signed decision content-hash cycle or mismatched Consumer Intent**: reject an unfrozen intent and any mismatch of exact identity/path/base from the signed hash (Tasks 1, 3).
3. **Stale checkpoint / rollback / clock spoofing**: reject expired or retrograde/offline-uncertain state; synthetic valid signature alone is insufficient (Tasks 2, 3).
4. **Unsigned or Admin-authored pseudo-Owner acceptance**: reject even with `issuer_id=portfolio-owner`, free-text `issuer_decision_ref` and a well-formed registry (Tasks 3, 4).
5. **Actual code/crypto-provider tampering**: do not claim Owner independence if executable integrity or the crypto library provenance is not verifiable; deny deployment (Tasks 0, 4).

---

### Task 0 — Trust boundary, environment and current-write authority (READ-ONLY)

**Files:** inspect `AGENTS.md`, four project handoffs, Root-H approved design/plan, current `scripts/verify-workspace.sh`, existing test files, trust manifests/schemas and local packaging/dependencies. No persistent code changes.

**Interfaces:**
- Consumes: current main/PR131/bootstrap SHAs, writer ownership, local crypto/JCS availability and Owner-controlled anchor operational environment.
- Produces: `AUTHORITY_AND_TRUST_BOUNDARY_RECEIPT` with exact proposed code/test/admin paths, approved candidate base, test-only crypto backend and independent protection observations.

- [ ] Read all governing refs and verify clean isolated worktree, exact task grant and protected Owner-operator trust anchor capabilities; classify `NOT_OBSERVED` if no owner provisioning evidence.
- [ ] Inspect available local Ed25519 and RFC8785 implementations, supported Python versions, license/packaging and test runner; propose a **specific** audited backend consistent with offline/no-download policy. Do not write private signing tooling or fetch new packages.
- [ ] Verify independent code integrity/provenance and trust-anchor/monotonic-state write separation from Admin. An Owner-root key fingerprint in an Admin-controlled file is not sufficient.
- [ ] If no positive source-write grant exists: STOP at `BLOCKED_BY_AUTHORITY`; hand back exact requested Root-H task authorization. If no independent Owner anchor exists, **synthetic development may still be separately authorized**, but real activation remains `OWNER_ANCHOR_NOT_PROVISIONED`.
- [ ] Resolve candidate implementation lineage without silently combining PR #128/#130 or disturbing PR #131.

### Task 1 — Canonical intent + decision serialization (TDD)

**Files:** create `scripts/root_h_owner_witness.py`; create `tests/scripts/test_root_h_owner_witness.py`.

**Interfaces:**
- Produces: `parse_strict_json(raw: bytes) -> Mapping[str, Any]`, `canonical_jcs(value: Mapping[str, Any]) -> bytes`, `consumer_intent_digest(intent: Mapping[str, Any]) -> str`, `signed_decision_bytes(decision: Mapping[str, Any]) -> bytes`.
- Consumes: exact closed intent/decision schema and domain `b"VIP-ROOT-H\x00ACCEPTED-AS-MUTATION-BASE\x00v1\x00"`.

- [ ] Write RED tests `test_intent_digest_canonical_and_acyclic`, `test_owner_decision_jcs_interop_vectors`, `test_duplicate_json_and_noncanonical_paths_denied`. Assert known RFC8785 interoperability vectors; intent excludes final packet/decision refs, decision digest is independent of packet.
- [ ] Run `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/scripts/test_root_h_owner_witness.py -k 'intent or jcs or duplicate'`; capture initial meaningful RED.
- [ ] Implement strict JSON/JCS wrappers using the verified, locally available backend, domain-separated message, SHA256 of JCS Consumer Intent and exact closed schema/length limits. Reject extraneous fields, invalid Unicode/number/ambiguous encodings and wildcard/noncanonical paths.
- [ ] Run focused GREEN; add tests for explicit Git blob SHA vs SHA256 separation and content-hash-cycle nonexistence; commit only under exact fresh grant.

### Task 2 — Trusted anchor and checkpoint-policy verifier (TDD)

**Files:** same helper/test paths; any trust-state machine storage interface remains protected out-of-band, not an Admin-owned new runtime file.

**Interfaces:**
- Consumes: independently provisioned `trusted_anchor` (read-only Owner commitment), signed checkpoint bytes, protected `highest_seen_version`/digest and a trusted `now`/freshness policy.
- Produces: `validate_checkpoint(anchor: TrustedAnchor, checkpoint: Mapping[str, Any], rollback_state: CheckpointFloor, now: datetime) -> ActiveKeysAndRevocations` or a fail-closed validation error.

- [ ] Write RED tests `test_admin_replaced_anchor_denied`, `test_checkpoint_signature_and_chain_denial`, `test_checkpoint_rollback_expiry_or_clock_uncertainty_denied`, `test_key_rotation_requires_trusted_continuity`.
- [ ] Run `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/scripts/test_root_h_owner_witness.py -k 'checkpoint or anchor or rotation'`; record RED.
- [ ] Implement verification only; pinned public key identity, immutable anchor source, signed sequential checkpoints, validity/expiry/revocation and protected monotonic high-water floor. When trust anchor, trusted time or protected floor is unproven, deny real dependency use.
- [ ] Run focused GREEN and review trust-source injection surfaces. Test-only synthetic keys/anchors are **not** real Owner authorization.

### Task 3 — Ed25519 signed decision bound to Consumer Intent (TDD)

**Files:** helper/test paths.

**Interfaces:**
- Consumes: `VerifiedTrustState`, strict `consumer_intent`, signed `decision_envelope`, requested candidate/consumer exact identity/path/base.
- Produces: `verify_owner_decision(...) -> VerifiedOwnerAcceptance` only upon cryptographic and scope validation.

- [ ] Write RED tests `test_owner_signature_correct_scope_positive_synthetic`, `test_free_text_owner_ref_without_signature_denied`, `test_decision_replay_wrong_consumer_denied`, `test_tampered_tree_paths_or_intent_denied`, `test_revoked_or_expired_owner_decision_denied`.
- [ ] Run `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/scripts/test_root_h_owner_witness.py -k 'owner_signature or owner_ref or decision_replay or tampered_tree or revoked'`; record RED.
- [ ] Implement verified key lookup and raw Ed25519 signature check over exact domain+JCS(decision); bind decision id/sequence, consumer intent digest, candidate commit+tree, root/goal/branch/base/writer and exact paths; check current checkpoint and revocation.
- [ ] Run focused GREEN, no fallback to admin-only trust/witness; commit only authorized exact paths.

### Task 4 — Fail-closed Root-H v2 wiring (TDD)

**Files:** modify `scripts/verify-workspace.sh` and `tests/scripts/test_verify_workspace_source_authorization.py`; use approved helper only via a verified import/code path.

**Interfaces:**
- Consumes: `verify_owner_decision` result and existing `_validate_v2_owner_decision_witness`, Root-H trust ledger/manifest and current-write/domain/transfer checks.
- Produces: unchanged v1 and canonical v2 outcomes; positive accepted dependency **only when the independent anchor/signature/checkpoint and full scope checks are actually verified**.

- [ ] RED `test_v2_real_dependency_denies_admin_only_claims`: existing mocked Admin-authored registry/Owner text must fail. RED `test_v2_signed_dependency_acceptance_synthetic`: only complete synthetic trusted anchor+signed decision+intent may pass, with no production Owner issuance.
- [ ] Run `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/scripts/test_verify_workspace_source_authorization.py -k 'v2_real_dependency or v2_signed_dependency'`; record RED. Do not fake RED with missing import or invalid fixture.
- [ ] In authorized isolated branch, connect helper to current hard-deny placeholder with strict protected anchor loading and mandatory signer/checkpoint state; fail closed if any independent trust boundary is missing. Preserve all `dependency_authorized`, dynamic ordinal, current SOURCE-AUTH and non-`src/` path enforcement.
- [ ] Run focused GREEN, full existing Root-H v1/v2 suites and adversarial exercises; do not accept an ordinary PR or any actual dependency without an independently signed Owner record.
- [ ] If protected verifier integrity/anchor bootstrap remains unverified, report `CRYPTO_WITNESS_CODE_CANDIDATE_ONLY` and **do not activate real dependency acceptance**, even if synthetic positive fixtures pass.

### Task 5 — Independent review, certification and non-main delivery

**Files:** only exact authorized code/test paths. Owner root provisioning, signer/private key creation, actual acceptance records and admin trust write lane stay out of scope.

**Interfaces:**
- Consumes: authorized patch candidate, synthetic test receipts, trusted anchor policy and independent reviewer findings.
- Produces: immutable candidate SHAs, changed blobs, validation matrix, and review-only PR if publication separately authorized.

- [ ] Run `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q -p no:cacheprovider tests/scripts/test_root_h_owner_witness.py tests/scripts/test_verify_workspace_source_authorization.py`, `bash -n scripts/verify-workspace.sh`, Python compile and `git diff --check`. Record full output/count/exits.
- [ ] Run `bash scripts/verify-workspace.sh` and preserve actual global exit status and unrelated environment failures. Scoped tests do not imply overall workspace PASS.
- [ ] Inspect diff against frozen base: no v1 behavior drift, no real Owner signing/private key, no wildcard writes, no unauthorized schema/trust files, no implicit acceptance to PRs.
- [ ] Obtain independent security/code review of exact SHA/diff, including compromised Admin, source substitution, checkpoint rollback, consumer-intent cycle and crypto backend attack scenarios.
- [ ] With current exact grant and passing scoped evidence, publish only via non-force branch push; verify remote commit/tree/blobs and separate reviewer acknowledgement. Never merge `main`.
- [ ] Report one of: `SYNTHETIC_OWNER_WITNESS_CANDIDATE_PUBLISHED_REAL_ACCEPTANCE_DISABLED`, `BLOCKED_BY_AUTHORITY`, `BLOCKED_BY_TRUST_BOOTSTRAP`, or `NEEDS_SCOPED_REPAIR`. Do not claim real-issuer readiness from a synthetic public key.

### Task 6 — Administrative schema/registry lane (separate serialized admin, not this writer)

**Files:** separate serialized Portfolio Admin exact-path grant only. This task's writer must not write `.orchestration/` records; no trust path is assumed writable.

**Interfaces:**
- Consumes: published witness-registry schema/record, the v2-generation schema set, and the intent/decision/checkpoint field models from Tasks 1–3.
- Produces: a proposed exact-path admin packet requesting (a) closed Consumer Intent schema, (b) closed signed-decision-envelope schema, (c) protected-anchor/checkpoint-policy schema, and (d) index-pinning update tasks, plus witness-registry update instructions — for separate admin approval, not execution here.

- [ ] Preflight and verify the already-published `root-h-owner-decision-witness-registry.v1.schema.json` and its registry record in the current trust tree; record the observed commit/tree. Do not re-create them.
- [ ] Propose exact closed schema paths for Consumer Intent, signed decision envelope, and protected-anchor/checkpoint policy under `.orchestration/portfolios/execution-portfolio-20260924-v1/authority/schemas/`, each with field-level constraints and error classes; submit to Portfolio Admin for a separate exact grant.
- [ ] Propose the witness-registry update procedure (append-only records, `no_owner_dependency_acceptance_issued` remains `true`, no real acceptance) and index-pinning tasks; mark all of it `ADMIN_ONLY_NOT_EXECUTED_BY_THIS_PLAN` until a separate grant exists.
- [ ] If no separate admin exact-path grant is present, report `BLOCKED_BY_ADMIN_GRANT`; do not write any `.orchestration/` path.

## Six-Cycle Iterative Refinement

1. Factual/current Git identity and crypto-library/deployment capabilities are verified.
2. Closed schemas, Consumer Intent, signed decision, checkpoint and error classes covered.
3. Source-presence/current-write/dependency-acceptance separation and PR #131 fail-closed guarantee preserved.
4. No pointless repeated research or automatic 19-root migration; serialized Admin and exclusive code writer.
5. Negative tests for hostile/admin-forged trust, clock/state and wrong-code configurations.
6. Exact execution grants, useful stop states, immutable receipts and Owner provisioning handoff.

**No command in this plan itself authorizes persistent changes.**
