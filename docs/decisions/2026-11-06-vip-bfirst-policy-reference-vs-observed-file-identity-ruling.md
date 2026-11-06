# VIP B-first — policy fixture reference versus observed physical file identity

**Date:** 2026-11-06  
**Status:** BOUNDED SYNTHETIC FOLLOW-UP ADOPTED FOR TASK PLANNING / PROSPECTIVE TDD; no production, authentic-media or mainline authority.  
**Source of scope:** Explicit owner approval of continuing the initial B-first synthetic lane, followed by "kaldığın yerden devam et" after an independent source audit. This ruling is strictly limited to the identified occurrence/provenance semantics of the already authorized new component. It is not a global future-action waiver.

## Verified immutable evidence

- Canonical `Centaurioun/video-intelligence-pipeline`, B-first component candidate `c474b8702d610462c455f8598052c06fe7dd9dd9`, tree `67f62da71954f7afa081467b2f9ff6f6f01517bd`, direct parent `215ec88270a2437a746fbab1f4842b83ee11c512`.
- Canonical `main@3bfcc2ba221b36df6773e630b44479ec961d630a` remained unchanged in GitHub checks.
- Audit: LAB `review/vip-bfirst-manifest-source-identity-audit-20261106@0691e332b757b464fcc4f9622ca4531814b4d8c7`, `docs/reviews/2026-11-06-vip-bfirst-manifest-source-identity-and-tdd-audit.md`.
- LAB main `5eab58ea2a5424424cb95f2690654b91395425df` remained unchanged.
- Verified Git blob: `cfr_4s_shape.json` at `ed7780041be153138273848359c8e368493d3057` = 1834 bytes, SHA-256 `b1fdef7c7232e1e96f2bc3faff062ffdaa5755af5492c0b351f745cb32e1b975`.
- Verified Git blob: `vfr_nonuniform.json` at `bbb8374548bb2021f9fd62c9c8e2cc6cfeb6c68b` = 1294 bytes, SHA-256 `0c966865b3b881319658a30a6dfb062dc00b467fc71cc2a0f41499969d72261e`. Both digests were independently recomputed from fetched exact Git blob content and match committed code constants.
- GitHub workflow `42282239478` was `success` on exact candidate SHA; 308 synthetic-smoke PASS per Python 3.11/3.14. New focused test was **not** included in this smoke selection. Reported local 105 PASS per interpreter and native source reviewer `NO_FINDING` are not independently reproduced here.
- The original feature's TDD pre-implementation behavioral RED was **NOT_OBSERVED**; a later prospective TDD cycle must not be represented as retroactive proof.

## Technical defect/ambiguity to resolve, not to overstate

`src/vip_fvs/trusted_fixture_manifest.py` uses code-pinned `SOURCE_COMMIT`, `SOURCE_TREE`, fixture path/blob/SHA/length, and gives the `FixturePolicyEntry.occurrence_id` and admitted `AdmittedTimingRecipe.occurrence_id` values of the form `git:<SOURCE_COMMIT>:<fixture path>`. However actual bytes are read from the *current imported worktree* via `_repository_root() / tests/vip_fvs/fixtures` and `bounded_admission.admit_relative_file_bytes`. The returned `device`, `inode` and hash represent that file, not the historical Git object location. Identical bytes from two different checkout roots can match the same policy even with distinct observed physical file identities.

The policy binding is useful and intentionally low-assurance against local accidental misuse; the **Git ref is an expected POLICY FIXTURE REFERENCE, not a measured physical source occurrence**. No protected source, changed archive, security compromise or read bypass was observed. The separate descriptor-based admission does not prove an immutable historical file origin after checkout/copy.

## Adopted disposition

**D1 — Keep closed allowlist and bounded admission.** No broad rewrite, no new trusted-video claims, no dynamic generator or model.

**D2 — Distinguish proof domains.** Represent code-pinned Git commit/blob/path as `policy_fixture_ref` / `pinned_policy_reference` (MATCHED to reviewed policy) and observed `device/inode` or explicit file identity as local MEASURED evidence. If no unique source occurrence can be established from the current descriptor/operation, mark it `NOT_OBSERVED` as an availability state, NOT an evidence class or fabricated historical occurrence. Do not conflate expected policy reference with observed occurrence.

**D3 — Preserve compatibility where justified.** The component is new and has no other modified caller in the original B-first candidate diff. Before changing fields, inspect the exact current consumer graph. Prefer narrowly versioned field-level semantics. If an existing consumer or governing canonical contract demands `occurrence_id` with a historical meaning, stop and propose a separate contract ruling rather than silently breaking a shared API. No downgrade to hash-only custody claims.

**D4 — Prospective test-first proof required.** On a new isolated clean Canonical successor branch from exact `c474b870...`, add a same-exact-reviewed-bytes/two-roots test that demonstrates the current ambiguity as behavioral RED *against original code*, then implement the smallest GREEN fix. Preserve the original feature's missing RED as an historical gap. A missing pytest/collection error is NOT behavioral RED.

**D5 — Distinct source identities remain strictly bounded.** Assert correct identity separation for current synthetic fixtures, avoid unauthorized input reads, and preserve allowed-operation/purpose check before descriptor reads, path/symlink/race refusals and `O_NOFOLLOW`. The runtime observation may identify a device/inode for a single admission operation; it must not imply permanent custody or stable cross-machine identity. Avoid claiming same-user attacker resistance.

**D6 — Prior main-ref process deviation preserved.** Codex previously reported moving local `main` with `git update-ref refs/heads/main refs/remotes/origin/main`. No repair/reset is authorized. Future work starts from exact immutable candidate in an isolated worktree and does not move local or remote main.

## Non-authority and next gate

Only `src/vip_fvs/trusted_fixture_manifest.py` and `tests/vip_fvs/unit/test_trusted_fixture_manifest.py` are admissible for the next narrow code candidate; no other source/test/schema/CLI changes without a new owner-specified path and scope. A new clean independent reviewer worktree is required for candidate review, with test execution where installed, or exact `NOT_OBSERVED` receipts.

Maintain `BFIRST_MANIFEST_PRIMITIVE_PARTIAL` until the new successor has credible prospective RED/GREEN, matched unit/relevant Python3.11/3.14 regression, GitHub CI exact SHA, and independent reviewer evidence. A narrower `OCCURRENCE_SEMANTICS_REPAIR_VERIFIED` may be reported only if all direct evidence supports it. An older feature's RED chronology remains `NOT_OBSERVED` forever.

`STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED` and `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT` persist. No protected/real media, model downloads/inference, provider/cloud egress, video generation, Gate promotion, production edit/render/export, source migration, deletion/clean/reset/force push, Canonical/LAB main edit or PR/main merge.

**Terminal:** `BFIRST_POLICY_REFERENCE_OBSERVED_OCCURRENCE_SEPARATION_APPROVED_FOR_BOUNDED_TDD` — NO MAIN MERGE.
