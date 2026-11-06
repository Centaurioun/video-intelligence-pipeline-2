# CORE-02 — Trusted synthetic fixture provenance design proposal

**Status:** PROPOSED — OWNER APPROVAL PENDING
**Date:** 2026-11-06
**Run / lane:** VIP-CORE02-FOLLOWUP-20261106 / SYNTHETIC-FIXTURE-PROVENANCE-DESIGN
**Scope:** Architecture research and proposal only. No source, schema, policy, runtime, or Gate behavior is changed by this document.

## Decision requested

Decide whether analyze-local should gain a strict, repository-controlled synthetic-fixture admission path separate from its current self-declared JSON grant. If so, approve the bounded trust boundary and a later implementation scope. This proposal recommends a two-part design: a closed, repository-pinned fixture manifest (B) for stable fixtures, plus a constrained generator interface (A) for ephemeral fixtures. It does not recommend treating a locally supplied signature or digest as independent trust.

The initial strict path would accept only (1) exact fixture bytes whose digest is in the trusted manifest, or (2) output created during the same invocation by an allowlisted generator and bounded recipe, with a receipt bound to the captured output. The existing --source plus user-readable grant path must not become trusted-generated admission merely by adding another self-asserted field. Whether that legacy path remains available as clearly lower-assurance synthetic demonstration behavior, or refuses before probing/indexing, is an Owner decision.

The assurance claim is narrow: “this input matches a fixture artifact or generation operation accepted by the selected repository policy, under the stated repository and runner assumptions.” It cannot establish that a malicious user controlling the local account, checkout, executable, trust manifest, and process memory did not fabricate the whole chain.

## Evidence ledger

Evidence is pinned to immutable Git objects. Source links name the Canonical CORE-02 candidate at 520ab543c7eb765ce1cba989742dde3abd4bbf4e, tree 3ad25b7b00b03a14e6ed2cc068a027dc042f2a46.

| Label | Observed fact | Source |
|---|---|---|
| VERIFIED | The synthetic grant has an exact field set, requires grant_kind=SYNTHETIC_FIXTURE_ONLY, source_kind=synthetic, and a nonempty generator; it binds source digest/size and analysis scope. record_digest is computed over the supplied canonical grant bytes. The loader does not check a signer or trusted issuer. | [query_analysis_authorization.py L19–27, L46–68, L70–118](https://github.com/Centaurioun/video-intelligence-pipeline/blob/520ab543c7eb765ce1cba989742dde3abd4bbf4e/src/vip_fvs/query_analysis_authorization.py#L19-L27) |
| VERIFIED | The CLI checks --fake-embedder, rejects a symlink leaf, loads the grant, validates scope, hashes the selected source, snapshots it, probes the snapshot, and runs the analysis. | [cli.py L991–1044](https://github.com/Centaurioun/video-intelligence-pipeline/blob/520ab543c7eb765ce1cba989742dde3abd4bbf4e/src/vip_fvs/cli.py#L991-L1044) |
| VERIFIED | _fixture_grant_source hashes source.read_bytes() and compares digest/size. The separate preview sidecar has only source_kind, sha256, and generator, requires canonical JSON, and compares the digest with the source. Neither establishes an issuer. | [cli.py L173–206](https://github.com/Centaurioun/video-intelligence-pipeline/blob/520ab543c7eb765ce1cba989742dde3abd4bbf4e/src/vip_fvs/cli.py#L173-L206) |
| VERIFIED | Core analysis rechecks the grant and source around processing and binds probe/generation evidence to a captured snapshot. These checks support byte consistency and scope, not generator authentication. | [core_analysis.py L93–157, L161–208, L278–293](https://github.com/Centaurioun/video-intelligence-pipeline/blob/520ab543c7eb765ce1cba989742dde3abd4bbf4e/src/vip_fvs/core_analysis.py#L93-L157) |
| VERIFIED | Snapshot capture is documented to follow preliminary authorization; it uses bounded no-follow checks and binds staged bytes. Thus authorization must be sound before capture. | [source_snapshot.py L373–404, L431–475](https://github.com/Centaurioun/video-intelligence-pipeline/blob/520ab543c7eb765ce1cba989742dde3abd4bbf4e/src/vip_fvs/source_snapshot.py#L373-L404) |
| VERIFIED | The analyze-local orchestrator refuses REAL mode and requires the fake runtime. This does not prove that its input is synthetic. | [core_analysis.py L93–100](https://github.com/Centaurioun/video-intelligence-pipeline/blob/520ab543c7eb765ce1cba989742dde3abd4bbf4e/src/vip_fvs/core_analysis.py#L93-L100) |
| VERIFIED | Corpus preflight is explicitly test plumbing, not a real admission grant or trust anchor, and uses SYNTHETIC_TRUST_DOUBLE_ONLY. | [corpus_admission.py L1–5, L30–42](https://github.com/Centaurioun/video-intelligence-pipeline/blob/520ab543c7eb765ce1cba989742dde3abd4bbf4e/src/vip_fvs/corpus_admission.py#L1-L5) |
| VERIFIED | Adopted A-7 S5 source-admission policy requires bounded descriptor-based reads and fail-closed path/digest checks, but says this proves only the immutable bytes admitted/consumed in that operation. Production limits and supported OS list remain pending, and implementation authorization is separately scoped. This is a useful filesystem-integrity precedent, not synthetic-origin authorization. | [A-7 S5 Owner adoption at 520ab543](https://github.com/Centaurioun/video-intelligence-pipeline/blob/520ab543c7eb765ce1cba989742dde3abd4bbf4e/docs/decisions/2026-10-28-a7-s5-shared-admission-owner-adoption.md#L1-L25) |
| VERIFIED | The checked-in timing fixture materializer writes digest-bound JSON metadata, not media bytes. It is not proof of the origin of the CLI MP4 fixture. | [materialize.py L1–29](https://github.com/Centaurioun/video-intelligence-pipeline/blob/520ab543c7eb765ce1cba989742dde3abd4bbf4e/tests/vip_fvs/fixtures/materialize.py#L1-L29) |
| VERIFIED | Canonical contracts distinguish source occurrence/custody from byte digest identity, and require a derived artifact to resolve through source revision, producer attempt, and policy. | [CANONICAL_CONTRACTS.md L6–30, L171–196](https://github.com/Centaurioun/video-intelligence-pipeline/blob/520ab543c7eb765ce1cba989742dde3abd4bbf4e/docs/architecture/CANONICAL_CONTRACTS.md#L6-L30) |
| VERIFIED | The pinned Canonical candidate contains CODEX_NATIVE_THREAD_OPERATIONS_RUNBOOK.md; the observed shared Canonical working tree lacks that file. This proposal used the pinned candidate runbook and live Codex tool inventory for process facts, not as product authority. | [Canonical runbook at 520ab543](https://github.com/Centaurioun/video-intelligence-pipeline/blob/520ab543c7eb765ce1cba989742dde3abd4bbf4e/docs/architecture/CODEX_NATIVE_THREAD_OPERATIONS_RUNBOOK.md) |
| VERIFIED | The independent audit calls F2 a provenance/policy gap, not evidence that protected media was processed. It also retains CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT. | [Independent CORE-02 audit at LAB 63f410e5e48cd962efd3e28fe724bbf90f13f552](https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/63f410e5e48cd962efd3e28fe724bbf90f13f552/docs/reviews/2026-11-06_CHATGPT_INDEPENDENT_CORE02_GITHUB_SOURCE_AUDIT.md) |

**INFERENCE:** A caller who can choose arbitrary bytes and author the matching grant can satisfy the current grant integrity and scope checks if other exact bindings match. This follows from the loader and CLI flow; it is not evidence that such input was used. SHA-256 answers whether bytes equal a named digest. It does not identify who generated them, custody, or permission to read them.

## Threat model and trust boundary

### In scope

- Accidental or low-capability mislabeling: a caller marks a non-fixture file synthetic, edits a grant/sidecar, replays a stale receipt, supplies an unsupported recipe, modified fixture manifest, symlink, or changing path.
- A local caller can write arbitrary files and JSON but does not control the reviewed repository policy identity or trusted CI/release artifact selected for admission.
- Tool substitution, stale generator identity, unbounded input/output, wrong source occurrence, and unsafe path races.

The strict path should fail closed for these cases before FFprobe, decoding, indexing, or retaining derived artifacts.

### Out of scope for local-only assurance

A process running as the same user may edit the checkout, replace executables, alter environment variables, modify process memory, replace a local manifest, or bypass local code. A local administrator can do more. A signature, embedded public key, pinned file, or in-memory token stored in the same writable environment does not defend against those actors. This design does not claim defense against a compromised repository/reviewer, malicious CI, compromised release/signing key, OS/kernel compromise, or the owner intentionally running modified code.

To defend against a same-user attacker able to alter the checkout, trust must move to an independently protected anchor, such as a reviewed signed release or CI artifact whose key and verification path the attacker cannot replace. Such infrastructure is outside this bounded proposal and needs a separate decision.

### Four different claims

1. **Digest integrity:** measured bytes equal a named digest and byte count. The current SHA binding can establish this.
2. **Trusted issuer identity:** a configured authority issued or approved policy/receipt. Canonical JSON and a record self-hash do not establish this. A signature works only relative to a protected trusted key and verifier.
3. **Source occurrence and custody:** one generated output was created for one invocation in a controlled workspace. Identical bytes can exist at multiple occurrences; assign a fresh occurrence ID and bind it to a generation receipt.
4. **Actual generator provenance:** a named generator, exact source/runtime identity, recipe, and configuration produced those bytes. A generator string is only an assertion until emitted by a controlled execution boundary and bound to output.

## Alternatives

| Option | Assurance and tradeoffs | Disposition |
|---|---|---|
| **A. Controlled in-process generator** | A trusted process constructs an artifact from a constrained recipe and binds a receipt to captured output. Avoids accepting arbitrary caller-selected media. Generator code/runtime remain trusted. MP4 generation may use external FFmpeg, making executable bytes, version, arguments, environment, and output custody part of the boundary. A mutable local checkout cannot prove itself against its owner. | Retain as one part; begin with a pure in-process structured fixture or independently pinned generator/toolchain. |
| **B. Repository-pinned closed fixture manifest** | Reviewed manifest binds fixture ID, exact digest/size, type, purpose/operation, and policy version. Exact bytes can be admitted without trusting caller metadata. It approves bytes, not the history of copies; adding fixtures requires review. Modified manifest/checkout defeats local trust unless policy identity is anchored to a protected revision/release. | Retain for stable fixtures and use as the smallest first slice. |
| **C. Signed receipts** | Detached receipts can bind generator, recipe, output digest, occurrence, purpose, scope and issuer key. Requires key issuance/storage, rotation/revocation, offline verification, CI signing, algorithm policy, and verifier supply-chain review. A same-user local key is not independent trust. Signature authenticates a statement, not generator quality or semantic “syntheticness.” | Defer. Reconsider for cross-machine artifact distribution with protected key custody. |
| **D. Current self-declared JSON grant plus SHA-256** | Provides canonical syntax, integrity against the supplied digest, expiry/revocation fields and exact scope matching. Anyone who creates bytes can compute a matching digest and self-declare generator/source kind. | Reject as trusted generation evidence. Could remain a clearly lower-assurance declaration only if it cannot satisfy strict admission. |
| **E. Filename, codec, pixels, FFprobe, classifier heuristics** | Can detect malformed files and provide technical measurements, but authentic footage can share codecs/patterns and synthetic-looking media can be transformed. None proves origin or grants read permission. | Reject as trust mechanism; keep technical probing after admission. |

### Bounded A+B combination

**PROPOSAL:** one versioned policy supports two separately named modes:

- **Manifest fixture mode (B):** closed entries bind exact fixture ID, digest, byte count, artifact type, allowed purpose/operations, and policy identity. This is the minimum viable initial admission route.
- **Generated fixture mode (A+B):** a trusted entry point takes only a bounded declarative recipe, no arbitrary source paths/URLs/shell/user-selected executable, creates a new output in an invocation-owned private directory with no-clobber semantics, measures the output, and issues a receipt bound to the operation. The reviewed policy pins the generator identity and recipe schema.

If FFmpeg is permitted, generator identity must include resolved executable digest/version, exact argv recipe, relevant environment, and the restriction that no user-selected input media is accepted. A path string or FFprobe result is not executable identity. If the current CLI cannot enforce this boundary without weakening it, keep the route blocked rather than calling it trusted. The hybrid still does not authenticate provenance if checkout, generator, and policy are all controlled by the adversary.

## Proposed receipt and field origins

Create a new, strictly versioned SyntheticFixtureReceipt/manifest contract; do not overload SyntheticFixtureGrant or silently reinterpret record_digest. Require canonical JSON, duplicate-key rejection, exact fields, valid digests, and supported versions.

| Field group | Example fields | Origin / validation |
|---|---|---|
| Schema and policy | schema_id/version, policy_id/digest/revision | Verified only by comparing with the selected trusted manifest/release anchor. A digest supplied inside the receipt is not self-authenticating. |
| Issuer and assurance | issuer_id, assurance_profile, issuance_mode | Match to configured policy. Do not call a local self-declared issuer cryptographically authenticated. Prefer a label such as REPOSITORY_POLICY_ACCEPTED unless a protected signer is adopted. |
| Occurrence and operation | occurrence_id, revision_id, run_id, attempt_id, operation, purpose, issued_at, optional expiry/revocation ref | IDs bind one use. Clock and local revocation files are only as trustworthy as the host. |
| Generator | generator_id, generator_source_digest, repository_commit, runtime_id, optional executable_digest/version | Match to policy/release inputs; a version string alone is an assertion. |
| Recipe | recipe_id/digest, canonical parameters, seed, limits | Verified for the exact canonical input consumed by the generator; does not establish semantic truth. Bounded mode forbids arbitrary file/network inputs. |
| Output binding | relative locator under policy-owned root, output_sha256, byte_count, captured file identity, artifact_kind | Measure from the safely opened generated or allowlisted artifact. A locator is not content identity or occurrence identity. |
| Probe and downstream binding | stream index, timebase, snapshot ID/manifest digest, probe digest, generation/index/output roots | Stream/timebase/probe are measured from the captured bytes and exact invocation. Operation/root scope comes from policy; receipt fields cannot widen it. |
| Receipt integrity | canonical receipt digest; optional future signature | Digest detects changes only. Verify signatures only against a separately trusted key plus checked revocation policy. |

Keep assertion-level classes distinct. Digest, byte count, probe and file facts are MEASURED; equality to manifest/policy is MATCHED; EDITORIAL_INFERENCE is not generation trust. NOT_OBSERVED is an availability state, not an evidence class. A receipt never promotes synthetic results into production evidence.

## Authorization and safe read ordering

1. **Resolve policy before media access.** Select an immutable manifest/release identity through harness configuration, not an arbitrary path beside the candidate. Verify schema, policy identity, allowlisted fixture or generator, operation, purpose, quotas, expiry/revocation references, and permitted output roots. Missing, ambiguous, stale or unknown policy refuses.
2. **Bind occurrence before reading.** Manifest mode creates a fresh use ID bound to the entry and locator. Generator mode authorizes only a recipe/generator operation; it accepts no external source path. Do not depend on a digest learned from reading an otherwise unauthorized file.
3. **Open descriptor-relative and no-follow.** Reject symlink components, nonregular files, path escape, size overrun, and detectable file-identity changes between stat/open. Bind device/inode or platform identity to the descriptor. This mitigates mistakes/races, not a malicious same-user process.
4. **Manifest mode measures authorized bytes.** Hash through the opened descriptor with a hard limit and compare with the expected manifest digest/size, never the caller's grant digest. Unknown entry or mismatch refuses before FFprobe/decode/index.
5. **Generator mode creates then captures.** Run only an allowlisted generator with constrained recipe/argv into a fresh private no-clobber location. Issue the receipt in that invocation context, safely open the output, measure digest/size while retaining object identity, then copy to the private source snapshot. If FFmpeg is approved, check its policy identity before spawn; use explicit argv, no shell, and finite runtime/output.
6. **Seal one snapshot and process only it.** Atomically publish a bounded private snapshot and receipt. Verify snapshot evidence, then point FFprobe and index at that snapshot, never the mutable original. Bind probe, generation, and report to snapshot manifest digest and occurrence.
7. **Recheck before publication.** Revalidate policy identity, expiry/revocation, snapshot, and receipt binding. If anything changed, refuse and do not publish trusted-success evidence.

Keep separate: (a) permission to discover/read bytes; (b) whether already authorized bytes match a reviewed fixture or generation operation. Manifest mode authorizes reading exact known fixture bytes before measuring them. Generator mode authorizes creation from a bounded recipe and then measures output. Never hash an arbitrary candidate to retroactively grant permission to read it.

## Refusal conditions and adversarial test proposals

These are proposed contracts; no tests were run for this design.

| Case | Expected result | Limits |
|---|---|---|
| Arbitrary source plus forged self-consistent current grant/sidecar | Refuse strict admission before FFprobe/decode/index/report. | Does not defend against modified application code. |
| Exact manifest bytes, approved purpose, safe root | Accept; include policy identity and a new occurrence ID. | Proves exact byte allowlist match, not historic creation method. |
| Manifest changed, digest/size mismatch, unknown entry, stale policy, unsupported schema, duplicate JSON keys | Refuse before source probe/index. | Trust in manifest anchor remains an assumption. |
| Same bytes at a second occurrence; receipt replay for another run/purpose/query/operation/output root | Refuse scope/occurrence mismatch unless fixed manifest policy explicitly allows reuse with a new occurrence. | Identical bytes do not reveal physical custody history. |
| Recipe traversal, URL/input path, unbounded size/duration, unapproved executable, modified generator digest, ambient PATH substitution | Refuse before spawn/output read. | Does not prove generator correctness. |
| Output changed during capture, symlink/parent symlink, hard-link swap, rename race, quota overflow | Refuse by descriptor identity and limits; exercise race points with barriers/fault injection. | Tested behavior applies only to tested OS/filesystems. |
| Copied/expired/revoked/unknown-key signature or changed signed bytes in a future signed profile | Refuse. | Does not prove private-key security or issuer integrity. |
| Receipt signed by a key in the same writable checkout | Do not claim same-user attacker resistance. | Demonstrates why local signatures alone add no independent trust. |
| Synthetic-looking filename/codec/pixels absent from policy | Refuse. | Heuristics never override policy. |
| REAL mode, real weights/provider, or fixture receipt used as real/pilot authority | Continue refusing. | Synthetic-only success does not prove real-source authorization. |
| Policy changes after admission but before publication | Refuse trusted-success report and retain truthful failure state. | Crash atomicity needs separate testing. |

All unknown policy/issuer, malformed receipt, digest mismatch, missing occurrence, changed source/snapshot, unsafe path/type, quota breach, unsupported generator/tool, expiry/revocation, replay outside scope, probe not bound to admitted bytes, or attempted escalation to real/pilot/production/edit/export/Gate authority fails closed.

## Compatibility and migration

- Add a new receipt/policy version; do not rewrite historical receipts/reports.
- Historical SyntheticFixtureGrant.record_digest continues to mean a digest of its supplied canonical record. Historical generator/source_kind fields remain assertions, not signatures.
- Future implementation must choose whether old grants remain explicitly untrusted developer declarations or are refused by analyze-local before source access. They cannot satisfy strict admission by default.
- Existing recipe descriptors retain their current declared meaning. The current materializer writes JSON metadata, not MP4; it is not retroactive media-generation proof.
- New reports may add fixture_admission_profile, fixture_policy_digest, fixture_receipt_digest, occurrence_id, and snapshot binding only after separate schema approval.
- Corpus separation remains distinct: membership/exclusion attestations do not prove a media generator produced a file.
- No proposal here activates REAL mode, model loading, cloud/provider access, protected/archive reads, production processing, or Gate promotion.

## Rejected routes and reconsideration triggers

| Route / claim | Reason not adopted |
|---|---|
| “SHA proves synthetic” | SHA proves digest equality, not origin or authority. |
| Treat current grant as trusted issuer | The record is self-authored; its digest only checks its own bytes. |
| Sign every receipt with a local key | Same-user modification can replace key, signer, and verifier; lifecycle cost without independent trust. |
| Trust generator name/version string | Caller-controlled and not bound to code or invocation. |
| Classify from codec, pixels, filename, duration, or FFprobe | Properties are shared by real and synthetic media; none authorizes a read. |
| Add remote PKI, daemon, cloud notarization, or provider dependency | Outside local fixture scope unless stronger assurance/artifact distribution is required. |
| Claim absolute synthetic truth on user-controlled host | A local mechanism cannot prove itself against an actor controlling every local trust anchor. |

Reconsider a protected signer/CI release profile if fixtures move across machines, are produced outside reviewed repository workflow, authorize consequential processing, or the threat model includes checkout replacement. Reconsider dynamic generation if fixed manifest fixtures cannot cover required tests or FFmpeg identity cannot be pinned. Reconsider A+B if an adversarial review finds arbitrary inputs or ambient executable substitution cannot be excluded. Each trigger needs a new explicit Owner decision.

## Owner decisions needed before implementation planning

1. Is the intended guarantee protection against accidental/misconfigured local use, or against a same-user actor able to alter checkout and executables? This proposal supports the former; the latter requires a protected independent anchor.
2. Should the first strict slice admit only exact B-manifest fixtures, or include A-generated fixtures? If A is included, is external FFmpeg acceptable under digest/version pinning, or must generation stay in-process?
3. Which reviewed ref/release/CI identity supplies the trusted manifest in an editable local checkout? If none exists, should strict admission be CI-only or locally unavailable?
4. Should the current arbitrary-source + JSON grant route be denied in analyze-local, or remain a lower-assurance developer-only path that cannot yield trusted synthetic status?
5. Which operations may a fixture authorize? Proposal limits this to local synthetic probe/index/query/report with fake runtime and finite quotas; no arbitrary-source discovery rights, REAL/pilot rights, protected media, edit/export, production, or Gate permission.
6. What local revocation and clock assumptions are acceptable? A mutable local revoked flag is not protected.
7. Does the Owner approve a versioned receipt and proposed evidence state, or require different representation?

## Non-claims and terminal disposition

- No authentic/protected media read or processing was performed or observed for this design. No claim about historical use is made.
- **REAL mode stays disabled.** Synthetic-only results do not prove production readiness, authentic model behavior, real-media provenance, retrieval quality, or archive suitability.
- **CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT remains open.** This proposal grants no interval, edit-boundary, Gate-3, or canonical-main authority.
- This is not an implementation plan, code/schema/policy approval, security certification, PR, merge, or Gate promotion.

**Terminal:** SYNTHETIC_FIXTURE_PROVENANCE_DESIGN_PROPOSED — OWNER_APPROVAL_PENDING

## Related pinned records

- Task packet: LAB docs/superpowers/tasks/2026-11-06-vip-core02-synthetic-fixture-provenance-design-task.md at planning commit cc0f3b26d081e0312a05bc80a85bfe326885694b.
- Owner authority: LAB docs/decisions/2026-11-06_CORE02_DIGEST_REPAIR_AND_FIXTURE_PROVENANCE_DESIGN_AUTHORIZATION.md at that planning commit.
- Independent audit: LAB docs/reviews/2026-11-06_CHATGPT_INDEPENDENT_CORE02_GITHUB_SOURCE_AUDIT.md at 63f410e5e48cd962efd3e28fe724bbf90f13f552.
- Canonical source: Centaurioun/video-intelligence-pipeline@520ab543c7eb765ce1cba989742dde3abd4bbf4e; source predecessor/current main at research start: 3bfcc2ba221b36df6773e630b44479ec961d630a.
