# CORE-02 — Owner authorization: digest repair and provenance design

**Date:** 2026-11-06  
**Status:** OWNER APPROVED — two separate, bounded lanes  
**Authority:** explicit owner response "Onaylıyorum." to ChatGPT's independent CORE-02 review findings and proposal for (A) narrow Report V1 digest repair, publication failure-path tests, and (B) separate **design-only** trusted synthetic fixture provenance research.

## Verified anchors

- Canonical `main@3bfcc2ba221b36df6773e630b44479ec961d630a` (unchanged at approval-time GitHub check).
- CORE-02 code candidate `feature/vip-core02-single-video-semantic-report-20261106@520ab543c7eb765ce1cba989742dde3abd4bbf4e`; tree `3ad25b7b00b03a14e6ed2cc068a027dc042f2a46`.
- CORE-01 source predecessor `261319d4ac7f3c2ac80b67a59baea13bba73bfed`.
- Independent GitHub-only audit: `Centaurioun/video-intelligence-pipeline-2` branch `review/vip-core02-independent-audit-20261106@63f410e5e48cd962efd3e28fe724bbf90f13f552`, document `docs/reviews/2026-11-06_CHATGPT_INDEPENDENT_CORE02_GITHUB_SOURCE_AUDIT.md`.
- LAB main `5eab58ea2a5424424cb95f2690654b91395425df`. Both DO_NOT_DELETE backup releases were verified immutable at the authorization-time query.

## Lane A — permitted code remediation

**Implementable now** only on a fresh, clean, isolated Canonical **successor candidate branch** based on exact `520ab543...`, with independent review and TDD.

- Repair `src/vip_fvs/core_report.py` so the report digest is **excluded when hashing** but **included in the final persisted JSON**.
- Add generated/synthetic report unit and CLI integration tests that reopen published bytes, verify the digest, detect tampering, maintain deterministic serialization, prevent clobber, and exercise publication error states including a fault **after target link but during directory fsync**.
- Investigate failure atomicity and crash/sync ambiguity by tests/reasoning. If changing the publication protocol beyond this minimal fix is necessary, stop and request bounded owner design approval; don't perform destructive recovery or silently delete output after an uncertain commit.
- Preserve Report V1 field and evidence meanings, POINT, PTS/timebase, CORE-01 strict stream, all prior CLI commands and frozen Gate-3 contracts. Keep REAL disabled.
- Normal GitHub feature-branch push plus applicable synthetic CI permitted; no PR/main merge.

## Lane B — permitted architecture/design only

**Research and propose** independently trustworthy synthetic fixture provenance: define attacker/trust model; inventory current `SyntheticFixtureGrant`, `_fixture_grant_source`, `_fixture_provenance`, `_probe_synthetic_analysis_source`, source snapshot/admission boundaries and related governing policies; compare candidate approaches, their authorization assumptions and residual risks; recommend a bounded approach with rejected alternatives and reconsideration triggers. Publish the design as a **documentation-only proposal on a distinct LAB design branch**, not Canonical source code. Obtain separate owner architecture approval before writing any provenance-policy enforcement code.

## Required independence and safety

- Lane A is the **only source writer**; Lane B is read-only against Canonical and LAB source plus documentation-only owner of its **distinct** LAB design branch/path. Concurrency only when native separate verified workers, leases, and ownership permit; no agent-count optimization.
- Never edit shared dirty worktrees, current existing CORE-02 worker, Canonical/LAB main, immutable backup releases, legacy `review_bundle.py`, legacy `+1s` semantic interval or Gate-3 temporal contract.
- No genuine/archival/protected media, REAL runtime, model downloads/loads, provider calls, network inference, whole archive, edit/render/QC, Gate promotion, destructive Git or integration PR.
- `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT` remains open. Prior CLI Report V1 synthetic candidate is **NEEDS_WORK** until Lane A code/test/reviewer correction; Lane B must not be smuggled into Lane A.
- If native thread/create/worktree binding/lease or contract scope cannot be independently verified, stop write lane with explicit `BLOCKED` evidence.

## Handoff and exit criteria

- Lane A: exact reviewed SHA, source and test diff, RED/GREEN evidence, on-disk digest proof, fault-injection and CI receipts; `CORE02_DIGEST_REPAIR_VERIFIED` only with independently supported successful evidence, otherwise `CORE02_DIGEST_REPAIR_PARTIAL`.
- Lane B: source-grounded threat model and options, approval-required unresolved architecture decisions and rejected paths; terminal `SYNTHETIC_FIXTURE_PROVENANCE_DESIGN_PROPOSED — OWNER_APPROVAL_PENDING`.
- No implication that overall CORE-02 is product/real-source ready, no legacy CORE-01 completion, no Canonical main integration.

**Terminal authorization:** CORE02_OWNER_APPROVED_DIGEST_REPAIR_AND_PROVENANCE_DESIGN_ONLY.
