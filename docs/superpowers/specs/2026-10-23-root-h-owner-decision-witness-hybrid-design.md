# Root-H Owner Decision Witness — Hybrid Trust-Anchor Design

**Date:** 2026-10-23  
**Design status:** OWNER-APPROVED ARCHITECTURE; deployment-specific anchor controls and exact runtime grants must be independently verified before implementation or activation.  
**Source of approval:** Explicit Owner message "Onaylıyorum" in response to the proposed independent local trust root, signed distribution, and non-circular Consumer Intent model.  
**Current code:** draft PR #131 at `9715d57fc898ef5ad35c17d2f14e99904c5b8be4`; `_validate_v2_owner_decision_witness` unconditionally fails closed.  
**Fixed trust observed:** `ae048af1898aadd30088eaf984d665b40cb8614b`. Verify again before any governed operation.

## 1. Objective and non-goals

Authenticate a real Owner's narrowly scoped `ACCEPTED_AS_MUTATION_BASE` decision independently from a Portfolio Admin, then validate candidate/consumer/base/exact-source-path bindings offline when the freshest trusted metadata policy permits. Source-presence, current-write authority and mutation-base acceptance remain **three distinct predicates**.

This design **does not** approve issuing a real dependency acceptance, generating private keys, changing runtime verifier behavior, changing canonical `main`, modifying Gate evidence, importing PR #128/#130, or relaxing PR #131's unconditional fail-closed denial today.

## 2. Approved architecture

- **Signer:** Owner-held Ed25519 private signing key, unavailable to Portfolio Admin, ordinary coding agents, mutable worktrees, provider tools and CI jobs by default.
- **Local trust root:** independently Owner-approved public verification key identity and key-management policy, provisioned outside Portfolio Admin's write scope. An ordinary JSON file inside the bootstrap trust branch, or an agent-writable path in the same OS user session, **is not** an independent trust anchor.
- **Portable distribution:** signed decision records and checkpoint/revocation records can be carried by Git or offline copies; the transport is untrusted.
- **Non-circular Consumer Intent:** first freeze a task-scoped identity and exact domain/base/paths record; the Owner's signed decision references its content identity. Only *afterward* may a final task packet refer to both the intent and signed decision, with no cycle.
- **Conditional enabling:** unprovisioned/untrusted anchor, stale checkpoint, unverifiable Owner decision, unsupported crypto backend or unchecked code integrity means **DENY**. The current PR #131 dependency branch remains unconditionally denied until independently authorized integration.

### Security principals and boundary

The Portfolio Admin may stage manifest, task packets, registry, observation records and signed-object delivery bytes. Admin cannot:
1. sign as Owner;
2. change the trusted Owner key identity/policy or the trusted checkpoint floor/freshness mechanism;
3. change the trusted code that performs verification and still claim the original assurance.

Separate GitHub repositories alone do **not** establish (2) or (3). Require independent evidence of principal/ACL separation and operator control. For local-first work, use Owner/operator provisioning under a genuinely separate OS/hardware/management principal; if not achievable, classify `TRUST_ANCHOR_INDEPENDENCE_BLOCKED`. Document the actual machine, deployment trust path, principals and integrity controls before claiming protection. A path supplied via mutable environment variable or by Admin-controlled configuration is not authoritative.

## 3. Signing format — implementation proposal under approved architecture

Use **raw Ed25519 detached signatures** (RFC 8032) over exact bytes, not OpenSSH `SSHSIG`, unless a separate interoperable wire-format decision is documented. The approved architecture fixes Ed25519, not a pre-existing production private-key format.

```text
signed_bytes = b"VIP-ROOT-H\x00ACCEPTED-AS-MUTATION-BASE\x00v1\x00"
             + RFC8785_JCS(decision)
signature = Ed25519.sign(owner_private_key, signed_bytes)
```

The displayed `\x00` denotes **single NUL bytes** on wire (not four printable characters). Parse JSON using a strict UTF-8/I-JSON decoder: reject duplicate property names, invalid numbers, improper Unicode, extra schema fields and unknown signing algorithms. Use RFC 8785 JCS exactly (including UTF-16 property-key ordering); never substitute Python `sort_keys=True` as equivalent. Reject any object whose required canonical byte representation cannot be established deterministically.

Decision envelope: closed `{"format":"vip-owner-ed25519-v1","key_id":"<trusted fingerprint identifier>","decision":{...},"signature_b64":"..."}` with a canonical Base64 encoding and explicit no-extra-field rule. The `key_id` is only a selector of an already trusted, active, separately provisioned key; an envelope-supplied key is not trusted.

## 4. Non-circular immutable Consumer Intent

Before any Owner signing operation, separately freeze the `consumer_intent` record, containing at least:

- `intent_schema`, globally unique `intent_id`, `portfolio_id`, `root_id`, `goal_id`, exact `branch` and immutable implementation/mutation-base SHAs;
- assigned writer identity and exact worktree/branch binding consistent with the approved task context;
- proposed dependency candidate root/goal/branch, commit SHA and its exact verified tree SHA;
- approved exact canonical source-write paths (sorted, unique, no wildcards or `src/**`), plus task scope;
- parent design/authority IDs and intent creation metadata; non-security timestamps are audit evidence only.

Use `consumer_intent_sha256 = SHA256(RFC8785_JCS(consumer_intent))`. Store its exact independently verified Git blob locator too if represented as a Git record; **do not confuse Git blob SHA-1 identity with SHA-256 of JCS bytes**. A frozen intent is not a grant. No circular reference to the final task packet or signed decision is allowed inside this intent.

The signed `decision` is a closed schema with:
`decision_schema`, `decision_id`, `decision_sequence`, `action=ACCEPT`, `purpose=ACCEPTED_AS_MUTATION_BASE`, `consumer_intent_sha256`, exact candidate SHA/tree and consumer root/goal/branch identity, immutable exact path list, `issued_at`, `not_before`, `expires_at`, `key_id` (or derive only from envelope with exact equality check), and optional `supersedes_decision_id` with authenticated lineage. Every field is covered by the signature. `decision_id` cannot be reused for a different intent/payload.

**Safe order:** Owner/authorized task drafts and freezes intent → Owner inspects immutable SHA/fields and signs exact decision → Admin transports signed bytes without altering them → separately authorized task packet references frozen intent and decision blobs → verifier recomputes all identities and exact matches. Owner signing does not itself grant source-write paths; task-specific current-write authority remains independently mandatory.

Do not pin the *final* task-packet blob inside the signed decision if that packet will pin the signed decision blob: this forms a content-hash cycle. The verifier must compare every grant-relevant packet/slot field to the signed intent, rejecting additions or substitutions.

## 5. Independent trust bootstrap and immutable checkpoints

A trusted verifier has an independently provisioned local root `root_key_id` and initial public-key commitment. Provisioning must record: responsible human/Owner, OS/security principal, concrete location or trusted service, immutability/write ACL result, verifier binary/script integrity verification, and independent Owner fingerprint confirmation. If this proof is absent, **DENY**.

Define closed, Owner-authenticated checkpoint data:
- `checkpoint_version` strictly increasing and `previous_checkpoint_hash` linking the chain;
- active/revoked keys and validity windows; permitted role `ACCEPTED_AS_MUTATION_BASE`;
- ordered decision/revocation sets with exact IDs/hashes, valid-from and expiry;
- `checkpoint_issued_at`, `checkpoint_expires_at` and max-offline age from independently protected policy.

Persist a highest-accepted version/digest outside Admin-writable state; reject rollback, equivocation, unknown key, invalid dual-signature rotation, revoked keys, expired or superseded decisions. For key rotation, require authenticated continuity from the previous trusted root and proof of possession/authorization of the successor key, with an explicit, separately reviewed recovery policy; no Admin self-declared new root.

**Offline freshness limit:** cryptographic verification proves authenticity of the cached checkpoint, not absence of newer remote revocations. Reject stale or expired checkpoints; freshness requires a trustworthy clock/update-start time and trusted monotonic floor. If the verifier lacks a reliable clock or protected checkpoint state, use a stricter read-only or online-attestation policy and **DENY dependency acceptance** rather than pretending offline freshness. “Always latest offline” is an impossible guarantee.

## 6. Verification acceptance algorithm (required order)

1. Verify trusted verifier code/release identity and independently provisioned root key commitment; reject anchor/config supplied solely by Admin.
2. Parse and authenticate checkpoint chain, root-key rotation and revocations; enforce freshness/expiry/monotonic anti-rollback.
3. Strictly parse exact intent and decision envelope; reject duplicate/unknown fields, ambiguous encodings, wrong signature domain, unknown algorithms/key IDs.
4. Verify Ed25519 signature using the separately trusted active Owner key.
5. Check intent hash, signing purpose, decision uniqueness, consumer scope, path equality, writer/root/goal/branch/base and live task-packet/slot values.
6. Verify dependency candidate Git commit **object**, exact tree, relation to consuming HEAD and accepted observation; no inferred PR or `dependency_authorized` promotion.
7. Check explicit status/sequence/revocation/supersession against trusted checkpoint and live trust ledger without relying on Admin-only claims.
8. Pass the cryptographic predicate **only together with** current-write/path/transfer/mutation checks. Record the immutable evidence IDs in the result.

Fail closed on any source unavailable, mismatch, stale trust, wrong interpretation or Git validation failure. Unknown version or fallback logic must not downgrade to a weaker acceptance mode.

## 7. Single-use, replay, and threat model

The exact consumer identity and intent hash make re-use in other tasks invalid, while repeated validation of the *same* tuple is idempotent. Offline signature verification alone cannot enforce globally “exactly once” execution; requiring that property entails independently trusted signed consumption history and transactional semantics, **out of scope** absent explicit Owner decision.

Attacker capabilities to test:
- Admin authors JSON, Git commits, registries and PR claims, but not independent Owner signature or root integrity;
- mutable process environment and alternate path injection;
- stale/malicious checkpoint replay, branch/commit/tree swapping and hostile path encodings;
- task packet/decision circular hashes or path additions;
- a compromised verifier code path: **no independence claim** without trusted verifier distribution/measurement.

## 8. Explicit compatibility and adoption bounds

- Preserve v1 exact behavior and historical SOURCE-AUTH classes.
- Preserve current PR #131 canonical v2 candidate and its unconditional accepted-dependency denial until full independently verified mechanism is integrated under new scope authorization.
- Never import PR #128 schema/runtime issues or implicitly accept PR #130 as dependency; `dependency_authorized` is for source provenance, not Owner base acceptance.
- Real Owner private-key generation, first anchor provisioning, any actual signed acceptance, and production policy activation require **separate positive Owner/operational authorization** and proof that Admin lacks control.
- A separate planning or synthetic-test commit is not a real trust-chain source of authority.
- Scope is deterministic Root-H governance only: no protected video/media, provider calls, model downloads, Gate promotion or canonical main merge.

## 9. Rejected alternatives and reconsideration triggers

| Alternative | Disposition | Reconsider when |
| --- | --- | --- |
| Put public key only in Admin-writable bootstrap manifest | REJECT | Admin loses write control under an independently verified deployment policy |
| Use a second GitHub repo without independent ACL evidence | REJECT | Proven Owner-only root/admin separation and protected release verification |
| Treat Git commit hash, PR review or free-text Owner reference as Owner identity | REJECT | Never alone; may carry signed evidence |
| Sign final packet SHA while packet includes decision SHA | REJECT | Refactor to frozen consumer intent, no hash dependency cycle |
| Full TUF deployment immediately | DEFER | Multi-party repository-scale update needs justify full framework |
| Locally trusted root + portable Ed25519/JCS attestations | SELECTED | Reconsider only on independently justified crypto/tooling constraints |

## 10. Acceptance tests

- Signed exact intent/decision/checkpoint accepted **in a synthetic fixture** under a test anchor with isolated protected state.
- Missing/tampered signature, wrong key, unknown algorithm, duplicate JSON keys, wrong domain/canonicalization and nonexact paths denied.
- Mismatched candidate commit/tree, writer/branch/base/goal, extra source path or different task packet denied.
- Admin writes fake Owner witness/registry but cannot change trusted anchor: denied.
- Stale/rollback/equivocal checkpoint, forged rotation, revoked/expired decision and clock uncertainty: denied.
- No cyclic content hash; intent and decision blob revisions are verified separately.
- Preserved PR #131 canonical path and v1 tests remain successful; full workspace verifier exit reported literally.
- No real dependency acceptance or production signature is created during implementation testing.

## 11. References and independent evidence

- RFC 8785 (JCS): https://www.rfc-editor.org/rfc/rfc8785.html
- RFC 8032 (Ed25519): https://www.rfc-editor.org/rfc/rfc8032
- TUF metadata update design (inspiration, not claimed full implementation): https://theupdateframework.github.io/specification/latest/
- Verified code starting point: https://github.com/Centaurioun/video-intelligence-pipeline/pull/131
- Current approved v2 architecture: `docs/research/2026-10-23/boost-convergence/OWNER_ROOT_H_V2_DESIGN_APPROVAL.md`

## 12. Decision and next stage

**OWNER-APPROVED**: hybrid independently provisioned trust root, Ed25519-signed Owner decisions and non-circular Consumer Intent.  
**IMPLEMENTATION DESIGN CHOICES FOR REVIEW**: raw Ed25519/JCS wire format, exact data schema fields, deployment anchor binding and offline checkpoint operational policy. These details do not broaden the approval or permit key provisioning.

Prepare Superpowers `writing-plans` and a read-only deployment/security preflight. The next authorized development task can build synthetic fixtures with a test-only key only after a new exact Root-H writer grant; real acceptance remains disabled until a separately authenticated Owner action and operational rollout decision.
