# VIP B-first B2 — failed tool-identity preflight: independent evidence and debugging gate

**Date:** 2026-11-07 Europe/Istanbul
**Scope:** Verified GitHub run/job/log/source inspection and documentation only. No rerun, new workflow push, tooling execution, repository settings update or real/synthetic media operation.
**Status:** `BFIRST_B2_TOOL_PREFLIGHT_EXECUTED_ONCE_FAILED`; `A2_BLOCKED_TOOL_IDENTITY`; `A3_NOT_RUN`; `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`; `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.

## Verified exact source and run evidence

Canonical repository: `Centaurioun/video-intelligence-pipeline`.

- Remote preflight branch `refs/heads/design/bfirst-a2-tool-identity-preflight-20261107` **exists**, HEAD **`54b8f945a51b634e2d3c2d955a9e1f1de9e7777b`**; source tree `0c4db75cc70afcc5e33bf008c466fa1a326fd397`. Source workflow path `.github/workflows/bfirst-tool-identity-preflight.yml`; blob `aca16c1004a7823b17770f405c6cca740ca02ae2`. No claim of source changes or new publication beyond that ref.
- Run [`42339608944`](https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/42339608944), GitHub REST verified `event=push`, `head_branch=design/bfirst-a2-tool-identity-preflight-20261107`, `head_sha=54b8f945...`, path matches, `run_attempt=1`, `status=completed`, `conclusion=failure`, `actor=Centaurioun`. Run created 2026-11-07T04:42:29Z and last updated 04:42:36Z. The GitHub list endpoint returned exactly one workflow run for this branch.
- Job ID **`128304150939`** verified by GitHub workflow-run jobs API. Four steps: `Set up job=success`, `Refuse unauthorized workflow context=success`, `Hash local tool executable bytes without executing tools=failure`, `Complete job=success`.
- Independent job log download yielded 278 lines. Runner `2.338.2`, Ubuntu `24.04.5 LTS`, runner image `ubuntu-24.04`, `ImageVersion=20261101.360.1` in setup, runner image provisioner `20261028.624`. First gate log exposes exactly matching repository/event/ref/workflow ref, `github.sha`, `github.workflow_sha`, expected source variable and attempt 1; guard prints accepted.
- Next step returns **`REFUSED: local metadata validation failed`** followed by process exit code 1. It never emits the expected per-tool report nor persisted summary. Consequently the exact exception, progress through FFmpeg and FFprobe hash loops, paths, sizes, byte SHA-256 and package versions are **NOT_OBSERVED**. The available log cannot establish whether either hash was calculated transiently in memory.
- Canonical `main@3bfcc2ba221b36df6773e630b44479ec961d630a`, LAB `main@5eab58ea2a5424424cb95f2690654b91395425df` unchanged at inspection. Existing issuance branch was NOT_FOUND. Current targeted preflight ruleset `26744266` independently verified active, exact branch target with create/update rules, single bypass User `86323645`; don't extrapolate this to all actors or runtime enforcement. Two backup GitHub release records returned `immutable=true`.
- A1 producer `413d032e5635e4d8670e5565856f7fcfcfaca3ff` is not thereby published or exercised. No new video or artifact observed, no Stage A3.

## Source-code diagnosis without execution

The exact published Python body handles:
```python
try:
    main()
except SystemExit:
    raise
except Exception:
    raise SystemExit("REFUSED: local metadata validation failed")
```

Therefore the **observed generic refusal is evidence that an ordinary Python Exception (not the intentionally named SystemExit cases) escaped main()**, or other equivalently generic handler execution. It is NOT evidence identifying which underlying exception or operation produced it. The broad handler destroys phase and exception-class information. Bash appends and prints the summary only **after** Python exits 0, so even its earlier runner/OS preamble is unavailable in the Actions summary on failure.

Potential **hypotheses requiring controlled offline reproduction**, not verified root causes:

1. `check_directory_chain(entry)` is called for **every PATH directory before looking for tool candidates**. It calls `os.stat(prefix)` on every prefix; a missing/inaccessible/atypical PATH entry may raise `FileNotFoundError` or `PermissionError`, which becomes the generic refusal. A PATH directory that doesn't contain either tool should not automatically be mistaken for evidence that an actual tool executable is unsafe.
2. `resolve_with_links` and `Path(...).resolve(strict=True)` rely on existing symlink chains and may raise ordinary `OSError`/resolution errors; logs contain no phase.
3. `bounded_command` subprocess helper runs only `dpkg-query` on local package metadata; subprocess/selector errors could be masked. The source uses `process.kill(); process.wait()` without a second bounded wait in timeout/overflow handlers, a separate boundedness review point; not evidence that this caused the observed near-immediate refusal.
4. Package owner parsing assumes at least one output line; incomplete or malformed metadata may cause an `IndexError` masked by generic refusal.
5. Summary/stat/file operations or runner environment may raise ordinary exceptions that likewise lose provenance. Exact environment PATH was **not captured**, and neither specific failure location nor measurements can be retroactively inferred from timestamp alone.

**No one hypothesis is established as the actual cause.** Reproduce failure classes using an offline deterministic fake PATH/mocked regular executable metadata and mock subprocess in a sandbox; no FFmpeg/FFprobe process, network or protected media. Consider a phase-enumerated bounded diagnostic status emitted on refusal (constant code, no secrets/paths/stack trace) under a later separately authorized source change.

## Next safe dependency sequence

**D0 — no-execution, no source writing (current authority):**
- Preserve run/job/log URL, immutable source SHA/tree/blob and failure receipt.
- Use systematic-debugging: inspect the source and construct falsifiable hypotheses; reproduce under an isolated local fake runner/PATH with surrogate executable files that are not FFmpeg/FFprobe. Verify that prospective negative tests fail for the current underlying behavior; never claim exact root cause if unavailable.
- Review source for failure observability and process-wait bounds. Do not print token values, live PATH entries, secret paths, absolute host paths or unbounded exception text in any proposed hosted log.
- Return a minimal proposed workflow-only diagnostic repair, prospective RED/GREEN and exact changed-file authority, with independent reviewer requirement. If a repair is not reproducibly justified, return `ROOT_CAUSE_NOT_OBSERVED` rather than an unjustified patch.
- Freeze existing published preflight SHA and branch; **no push/rerun and no changes to A1 producer**.

**D1 — separate Owner authorization required for ANY future operation**: after bounded source-only debugging, a new reviewed immutable SHA and one newly authorized branch/trigger plus its enforced actor/ref protection and externally set/read-back expected SHA may be approved. The former one-run preflight grant was **consumed**, even though the measurement failed. Do not push a changed workflow to the current preflight branch using that exhausted authority, silently reuse the old expected SHA, or rerun the failed job. If new workflow code/trigger is proposed, show its updated identity guard and no-main trigger feasibility. A published branch cannot be 'updated only for inspection' when its workflow `push` trigger would automatically run.
- New authorized work would still be *media-free executable-byte identity only*, no FFmpeg/FFprobe process invocation, package installs/downloads, artifact upload, protected media, production A2, A3, Stage B/C or Gate promotion. The owner must expressly set the new run/attempt allowance and risk model before action.
- The issuer A1 `413d032e...` remains untouched; output hashes, if later produced, require independent review and separate Owner tool-hash approval before A2 production.

**Terminal:** `BFIRST_B2_A2_PREFLIGHT_FAILURE_SOURCE_AND_RUN_RECONCILED` with `ROOT_CAUSE_NOT_OBSERVED`; `A2_BLOCKED_TOOL_IDENTITY`; `A3_NOT_RUN`; `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`; `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.
