# VIP B-first fixture manifest — independent exact-source audit

**Date:** 2026-11-06  
**Auditor:** ChatGPT, independent read-only GitHub source/blob/CI inspection.  
**Disposition:** `BFIRST_MANIFEST_PRIMITIVE_PARTIAL` — code exists and verified GitHub synthetic CI passes; missing historical behavioral RED and a substantive policy-identity versus observed-occurrence ambiguity should be resolved before promotion.  
**No execution:** Local Python/pytest, native reviewer worktree and dirty local checkout were NOT accessed. No source code or Canonical/LAB main changed.

## Frozen verified GitHub anchors

- Canonical `main=3bfcc2ba221b36df6773e630b44479ec961d630a`.
- Canonical B-first branch `feature/vip-core02-bfirst-fixture-manifest-20261106` at `c474b8702d610462c455f8598052c06fe7dd9dd9`, tree `67f62da71954f7afa081467b2f9ff6f6f01517bd`. Direct parent `215ec88270a2437a746fbab1f4842b83ee11c512`.
- Diff `215ec882...c474b870`: exactly two added paths: `src/vip_fvs/trusted_fixture_manifest.py` (184 lines) and `tests/vip_fvs/unit/test_trusted_fixture_manifest.py` (212 lines). No SQLite, CLI, legacy interval or shared contract source changes.
- LAB `main=5eab58ea2a5424424cb95f2690654b91395425df`. DO_NOT_DELETE backup GitHub releases both fetched `immutable=true`.
- Workflow run `42282239478` exact final candidate SHA, `workflow_dispatch`, both Python smoke jobs successful; individual fetched logs report **308 passed (Python 3.11)** and **308 passed (Python 3.14)**. These smoke selections DO NOT include the new manifest unit test.
- Codex reports **105 passed** in selected local Python 3.11 and 3.14 test suites and reviewer `NO_FINDING`. Those are **REPORTED**, not independently rerun. The reported reviewer used the shared checkout and did not run tests; it does not meet the stronger clean independent review-worktree expectation. Behavioral pre-implementation TDD RED: `NOT_OBSERVED`; pytest absence/collection failure does not count.

## Independent fixture evidence

Read exact GitHub blob contents and independently recomputed SHA-256 with a verified SHA-256 implementation (known vector `abc=ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`):

| Policy fixture | Git blob identity | Length | Independently computed SHA-256 |
|---|---|---:|---|
| `cfr_4s_shape.json` | `ed7780041be153138273848359c8e368493d3057` | 1,834 B | `b1fdef7c7232e1e96f2bc3faff062ffdaa5755af5492c0b351f745cb32e1b975` |
| `vfr_nonuniform.json` | `bbb8374548bb2021f9fd62c9c8e2cc6cfeb6c68b` | 1,294 B | `0c966865b3b881319658a30a6dfb062dc00b467fc71cc2a0f41499969d72261e` |

Both constants in `trusted_fixture_manifest.py` match. These are JSON timing recipes, NOT video media or generator provenance. Historic Git references are selected by the implementation's frozen code/policy, not authenticated by a protected signing root or a separate CI trust service.

## Source behavior review

**Positive / VERIFIED FROM CODE:**
- `admit_fixture` checks allowlisted ID, purpose, operation, kind and explicitly supplied occurrence value before invoking `open_trusted_root` or reading fixture bytes.
- Uses `bounded_admission.admit_relative_file_bytes` for descriptor-based bounded reads, expected SHA-256 and file identity verification. Extra post-read `os.stat(..., follow_symlinks=False)` checks regular file and device/inode; `st_nlink != 1` refuses hardlink alias. The lower layer itself verifies file/parent identities around the read.
- Unknown IDs and disallowed VIDEO/REAL operation refuse; caller cannot pass arbitrary `root`, `source_path` or grant to `admit_fixture`. Code does not enable REAL and does not modify `analyze-local`.
- Source-code evidence classes explicitly keep `policy_evidence=MATCHED` and `byte_evidence=MEASURED`; code docstring disclaims protections against same-user modification of trust roots.

**F1 — Distinguish pinned policy occurrence from observed worktree occurrence (contract review required):**
- `SOURCE_COMMIT`, `SOURCE_TREE`, `FixturePolicyEntry.occurrence_id="git:<frozen-commit>:tests/vip_fvs/fixtures/<file>"` and returned `AdmittedTimingRecipe.policy_commit/policy_tree/blob_oid/occurrence_id` are fixed values from the reviewed **policy**.
- Actual bytes are opened via `_repository_root() -> Path(__file__).absolute().parents[2]`, i.e. under whichever *current checkout/worktree* imported this Python module. There is no runtime check that the worktree HEAD/tree is the frozen source commit or that the opened file is itself a historical Git object from that commit.
- SHA-256 establishes byte equality with the frozen recipe, but matching bytes do **not** establish that the **observed physical file occurrence** is the source occurrence at the historic Git revision. The code correctly returns observed `device`/`inode`, but mixes a policy occurrence ref into the `occurrence_id` field of the admitted result without distinguishing provenance roles.
- The negative test `test_foreign_occurrence_replay_refuses_before_source_read` supplies a caller-asserted wrong occurrence string and tests pre-read rejection; it does **not** demonstrate that a same-byte fixture copied into another checkout/root is detected as an unauthorized physical occurrence. This is a **source-level evidence/semantic concern**, not a reported exploit of protected media or a demonstrated remote attack.
- Suggested bounded adversarial TDD: in a new isolated candidate, first write a test that injects/arranges two **different controlled synthetic roots with identical reviewed fixture bytes** and checks that neither produces an unqualified `observed_occurrence` claim tied to frozen Git commit; distinguish `expected_policy_occurrence_ref` from independently observed file identity and purpose. If the source component cannot fix semantics without changing shared downstream contracts, STOP for a narrow versioned decision rather than invent custody.
- Even if unchanged physically, label `policy_commit` and `blob_oid` as `PINNED_POLICY_REFERENCE` or equivalent *source-of-policy metadata*; never silently upgrade those to proof that the opened file was read from that historical commit.

**F2 — Historical test-first RED cannot be reconstructed after the fact:**
- The original candidate was implemented with missing pre-implementation behavioral RED because pytest was unavailable; Codex acknowledged and correctly retained `PARTIAL`.
- No post-hoc test run can transform a previous collection error into an actual historical behavioral RED. A new **prospective** test-first amendment may provide RED against immutable `c474...`, then GREEN on a successor (for any confirmed F1 correction). Preserve prior `NOT_OBSERVED` in the historical receipt and do not rewrite history or classify process exception as completed TDD.
- Reviewer source pass alone is not independent test execution. Obtain a fresh reviewer in a verified **separate clean read-only worktree** at the final successor SHA if repository protocol requires it.

**F3 — Post-read absolute-path check and races are not full adversarial certification:**
- `os.stat(_repository_fixture_root() / entry.relative_path, follow_symlinks=False)` occurs after `TrustedRoot` scope closes, distinct from descriptor-relative lower-layer checks. This may produce a false refusal under concurrent ancestor replacement, and a following swap after this check is outside its scope. Do not call this proof of complete filesystem race resistance. Test actual approved local threat model, not universal POSIX guarantees.
- `st_nlink != 1` is a bounded defense-in-depth rule; a uniquely linked same-byte copied file can still match SHA, so it is not independent source-occurrence provenance.

## Recommended next bounded action

1. Treat current `c474b870...` as a **useful unmerged component candidate**, not a verified trusted-video pipeline.
2. Request independent confirmation of F1 on a fresh isolated read-only worktree and an exact two-root same-bytes test demonstration; avoid redefining a historical policy reference as measured origin.
3. If confirmed and within authority, create **new isolated Canonical successor branch based at exact `c474...`** and authorize only `src/vip_fvs/trusted_fixture_manifest.py` and `tests/vip_fvs/unit/test_trusted_fixture_manifest.py` for a prospective RED/GREEN correction. Capture TDD chronology and new reviewer on final immutable SHA. If schema or shared contracts must change, STOP with owner-facing decision.
4. Continue to keep `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED` and `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`. No new media, models, cloud/provider execution, Gate, PR, main merge, backup change or destructive Git.

**Terminal:** `VIP_BFIRST_SOURCE_AUDIT_NEEDS_EVIDENCE_AND_POSSIBLE_OCCURRENCE_CONTRACT_REPAIR`.
