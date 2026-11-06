# VIP CORE-02 — Synthetic-fixture trusted provenance design task

> **Trigger:** Superpowers brainstorming; architecture/design investigation ONLY. No source edits, tests that consume real/archival media, implementation worktrees, migrations, policy changes or production enablement. Obtain explicit owner approval of a proposed design before writing implementation plans/source changes.

**Date:** 2026-11-06  
**Status:** OWNER APPROVED FOR READ-ONLY DESIGN RESEARCH — DESIGN DECISION PENDING  
**Owner receipt:** LAB `docs/decisions/2026-11-06_CORE02_DIGEST_REPAIR_AND_FIXTURE_PROVENANCE_DESIGN_AUTHORIZATION.md` on `planning/vip-core02-digest-repair-fixture-provenance-20261106`.

**Exact code source:** Canonical `Centaurioun/video-intelligence-pipeline@520ab543c7eb765ce1cba989742dde3abd4bbf4e`, tree `3ad25b7b00b03a14e6ed2cc068a027dc042f2a46`; canonical main `3bfcc2ba221b36df6773e630b44479ec961d630a`. Reference independent read-only GitHub audit LAB `review/vip-core02-independent-audit-20261106@63f410e5e48cd962efd3e28fe724bbf90f13f552`.

## Design problem — do not prematurely assume a solution

`src/vip_fvs/query_analysis_authorization.py` verifies the schema/digest/expiry of a user-readable `SYNTHETIC_FIXTURE_ONLY` grant with a self-declared `source_kind="synthetic"` and `generator`, plus exact source SHA/size/query/stream/timebase bindings. The digest is computed from the grant's own bytes; **it is not an independent attestation of who generated the actual media**.

`src/vip_fvs/cli.py::main` `analyze-local` branch checks the grant and bytes, then captures a snapshot, probes and indexes the admitted media using a deterministic fake embedder. `src/vip_fvs/core_analysis.py` rechecks the same synthetic grant and snapshot. REAL model mode is separately hard-disabled. The risk is a **provenance/synthetic-admission bypass** if authentic or protected bytes are falsely tagged as generated fixture bytes; none was observed.

The goal is a **local-first, testable trust mechanism** proving fixture generation/authority under a stated threat model before indexing/probing any source bytes. It must not be presented as a mathematically absolute proof that media is synthetic when the adversary controls both source bytes and every signing/generation tool.

## Mandatory read-only discovery / source inspection

- Refresh live Canonical and LAB Git refs; read `AGENTS.md`, `docs/INDEX.md`, four `docs/project/` handoffs, `docs/architecture/CANONICAL_CONTRACTS.md`, `docs/architecture/THROUGHPUT_FIRST_DEVELOPMENT_PROTOCOL.md`, current synthetic admission/corpus separation policies, and applicable exact task constraints.
- Read current `src/vip_fvs/query_analysis_authorization.py`, `core_analysis.py`, `core_generation_evidence.py`, `core_report.py`, `cli.py` (`analyze-local`, `_fixture_provenance`, `_fixture_grant_source`, `_probe_synthetic_analysis_source`), `source_snapshot.py`, `bounded_admission.py`, `_bounded_admission_fs.py`, `real_source_probe.py` and `pilot_authorization.py`. Discover actual paths by Git tree, not guesses.
- Inspect `tests/vip_fvs/integration/test_core_analyze_local_cli.py`, `tests/vip_fvs/unit/test_query_analysis_authorization.py`, generated fixture helpers, current source-kind/admission adversarial tests and any existing trusted/signed fixture receipt conventions. Record whether a generator is in-process, an external binary, Git-pinned, reproducible, or merely labeled.
- Keep verified source facts separate from threat-model assumptions, risks and recommendations. No false security guarantees.

## Required design questions

1. **Trust anchor:** Who/what can attest generation? Repository-pinned source/generator commit, controlled native fixture creation, synthetic bytes generated *inside* trusted test process, signer keys, owner-issued issuance policy, attestation store, CI-controlled environment — distinguish each possibility and its actual trust assumptions.
2. **Adversary model:** Can an adversary edit a JSON grant, source path, file bytes, generator, current Git checkout, signer key, registry or local filesystem? Do they merely mislabel media accidentally? What is the defensible boundary on a locally controlled Mac?
3. **Authorized read order:** How can the gate verify a source's generation provenance without reading unauthorized source bytes? Distinguish a generated-media receipt from discovery authorization; never use a hash computed during an unauthorized read to grant itself permission retroactively.
4. **Provenance format:** Minimal fields for issuer/trust root, generator identity/version/code digest, input recipe/config/seed, source occurrence/revision/digest/size, stream/timebase, issuance/grant expiry/revocation, purpose, allowed operations, output/index/snapshot roots, artifact retention, and canonical serialization. Identify which claims can actually be verified.
5. **Tampering/replay:** Same SHA different source occurrence, symlink/path swap, mutable output root, revoked/expired grant, stale generator identity, copied receipt, time-of-check/time-of-use source changes, symlink under trusted root, environmental mutation, user-supplied FFmpeg binary and executable trust.
6. **Supply-chain and local-first tradeoffs:** Absolute trust is not possible if user can change all local state. What limited assurance can be achieved without cloud PKI, private key distribution or privileged daemons?
7. **Compatibility:** Existing `SYNTHETIC_FIXTURE_ONLY` grant and generated-media sidecar, source snapshot, Gate-0 experimental policy, corpus admission separation, existing CI fixtures; migration/versioning of new provenance without erasing historical fixture reports; real mode remains disabled.
8. **Verification:** Concrete RED/GREEN test ideas: self-consistent forged grant+authentic bytes denied, signed/registry fixture accepted only under valid trusted policy, source identity mismatch denied, stale/edited generator/receipt rejected, canonical digest match != trust, concurrent replacement and TOCTOU checks, no protected reads before grant, no fake-to-real promotion.
9. **Deployment gates:** Provide exact actions requiring separate owner grant; no real media/model/provider/Gate promotion based on fixture provenance.

## Alternatives to study and criticize

| Approach | Advantages | Costs, limitations / likely risks |
|---|---|---|
| A. **Trusted in-process fixture generator** creates media in an owned sealed temporary workspace from a constrained recipe and emits a linked provenance receipt; external arbitrary files cannot claim the same eligibility | Small local-only trusted path and clear custody for tests; no key infrastructure | Generator binary/toolchain still trusted; external use/long-lived fixtures require an explicit trust boundary; wrong path ownership or mutation remains possible |
| B. **Repository-pinned verified fixture manifest** with exact blessed content hashes and generator fingerprints, enforced as a closed allowlist | Auditable and reproducible, low ongoing complexity | Cannot prove a listed file was generated after manifest adoption; adding new fixtures requires reviewed manifest updates; a compromised manifest can bless arbitrary bytes |
| C. **Cryptographically signed generation receipts** with explicitly trusted issuer public keys and reproducible source digest, chain and scope | Supports detached proof for external generated artifacts | Key custody, enrollment/revocation, local trust-anchor bypass, issuance workflow, signature algorithm choices and correctness/security review are substantial |
| D. **User-supplied canonical JSON grant plus SHA-256** (current) | Low friction, useful integrity and scope binding | **REJECT AS TRUSTED GENERATION EVIDENCE**. Anyone who can create source bytes can create a matching grant; content hash does not prove origin. |
| E. **Infer synthetic status from video pixels, filenames, codec or FFprobe output** | No issuance integration | **REJECT**: classifier heuristics are neither provenance nor permission |

Explicitly evaluate a minimal **A+B hybrid**, but do not privilege it without comparing the actual repository constraints. Preserve rejected options and reconsideration triggers. A costly key service is not automatically justified for purely local unit fixtures.

## Deliverable / decision gate

Write a **proposed design** as a new file under LAB `docs/superpowers/specs/`, on a **fresh separate LAB documentation-only design branch**, not the code-fix branch. Suggested branch `design/vip-core02-trusted-synthetic-fixture-provenance-20261106` based on checked LAB main. Keep original audit/design/handoff files unchanged.

Include:
- Evidence ledger with pinned GitHub source SHAs and exact files.
- Threat model and trust boundaries with realistic non-goals.
- Current existing contracts/paths and exact gaps.
- A/B/C/D/E alternatives, rejected routes, costs and explicit decision triggers.
- Recommended bounded initial approach (or clear BLOCKED if lack of credible trust anchor).
- Proposed versioned receipt/schema/validation and atomic or immutable artifact lifecycle, plus safe no-clobber output and source read ordering.
- Precise field provenance: measured vs matched vs asserted/signed, never upgrade class.
- Backward compatibility/migration; current untrusted grants fail closed for trusted admission while legacy generated synthetic tests can still be labeled as lower-assurance if policy allows.
- Concrete adversarial acceptance tests and what they would NOT prove.
- Required owner architecture decisions before implementation planning.
- No software changes, PR, merge, unapproved data operations, or claims of implementation.

Use independent critique where available; final disposition:
`SYNTHETIC_FIXTURE_PROVENANCE_DESIGN_PROPOSED — OWNER_APPROVAL_PENDING`,
or `SYNTHETIC_FIXTURE_PROVENANCE_DESIGN_BLOCKED` with concrete evidence.

**Do not implement or enable a new provenance policy without separate explicit Owner approval.**
