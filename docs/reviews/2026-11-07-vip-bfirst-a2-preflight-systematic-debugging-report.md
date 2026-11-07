# VIP B-first B2 — failed tool-identity preflight: systematic debugging report

**Date:** 2026-11-07 (Europe/Istanbul)
**Scope:** Read-only inspection of one immutable Canonical workflow/run, bounded local synthetic reproductions, and a proposed diagnostic repair.
**Status:** `ROOT_CAUSE_NOT_OBSERVED`; `A2_BLOCKED_TOOL_IDENTITY`; `A3_NOT_RUN`; `STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`; `CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`.

No hosted workflow was rerun, no workflow source was changed, and no tool identity was approved. No FFmpeg or FFprobe process was launched; no video/media was created or read.

The pinned LAB audit was retrieved read-only from [commit `377fe6f4778c4c9cc69197404f9d5c9e965c5001`](https://github.com/Centaurioun/video-intelligence-pipeline-2/blob/377fe6f4778c4c9cc69197404f9d5c9e965c5001/docs/reviews/2026-11-07-vip-bfirst-a2-failed-preflight-independent-evidence-and-debug-gate.md). LAB documentation branch base for this report: `main@5eab58ea2a5424424cb95f2690654b91395425df` (tree `dae72052bbdbc1962713f302b50f8fa2fd78ed7f`).

Canonical source: [commit `54b8f945a51b634e2d3c2d955a9e1f1de9e7777b`](https://github.com/Centaurioun/video-intelligence-pipeline/commit/54b8f945a51b634e2d3c2d955a9e1f1de9e7777b), [workflow file](https://github.com/Centaurioun/video-intelligence-pipeline/blob/54b8f945a51b634e2d3c2d955a9e1f1de9e7777b/.github/workflows/bfirst-tool-identity-preflight.yml) (blob `aca16c1004a7823b17770f405c6cca740ca02ae2`); [Actions run `42339608944`](https://github.com/Centaurioun/video-intelligence-pipeline/actions/runs/42339608944).

## 1. Evidence ledger

| Claim | Evidence | Classification |
| --- | --- | --- |
| Canonical preflight source is commit `54b8f945a51b634e2d3c2d955a9e1f1de9e7777b`, tree `0c4db75cc70afcc5e33bf008c466fa1a326fd397`. | GitHub branch/commit API, local isolated source worktree at the exact commit, and `git rev-parse`. | VERIFIED |
| Workflow path and blob are `.github/workflows/bfirst-tool-identity-preflight.yml`, blob `aca16c1004a7823b17770f405c6cca740ca02ae2`. | Exact commit tree and local `git hash-object` of the file contents. | VERIFIED |
| Run `42339608944` was a `push` event on `design/bfirst-a2-tool-identity-preflight-20261107`, head/workflow SHA `54b8f945…`, attempt 1, completed with `failure`. | Current GitHub Actions run API and branch-filtered run list. | VERIFIED |
| Job `128304150939` failed in `Hash local tool executable bytes without executing tools`; context authorization passed. | Workflow-run jobs API and downloaded job log. | VERIFIED |
| Runner image was `ubuntu-24.04`, `ImageVersion=20261101.360.1`, Ubuntu `24.04.5 LTS`, runner version `2.338.2`; provisioner version `20261028.624`. | Job setup log. | VERIFIED |
| The measurement step ended with `REFUSED: local metadata validation failed` and exit code 1; it did not emit its per-tool result or summary. | Job log. | VERIFIED |
| FFmpeg/FFprobe paths, byte counts, hashes, package metadata, and which tool-loop iteration completed. | No measurement result was emitted; the generic handler hides the operation and exception. | NOT_OBSERVED |
| A1 producer SHA `413d032e5635e4d8670e5565856f7fcfcfaca3ff` was changed or pushed by this investigation. | No access/write was made to its worktree or branch. | NOT_CHANGED_BY_THIS_INVESTIGATION; predecessor state not re-audited here |

The run log shows the failed Python step began around `04:42:33.593Z` and emitted the generic refusal around `04:42:33.627Z` (about 34 ms later). This makes the explicit two-second timeout message an unobserved path in this run; it does not identify the actual exception.

## 2. Exact source failure boundary

The published workflow re-raises intentional `SystemExit` refusals, but masks every ordinary Python `Exception` escaping `main()` as the same message:

```python
try:
    main()
except SystemExit:
    raise
except Exception:
    raise SystemExit("REFUSED: local metadata validation failed")
```

This is at workflow lines 254–259. Therefore the hosted message establishes that an unexpected exception escaped `main()` and reached the broad handler. It does not identify the exception type or phase. Bash writes the summary only after Python exits successfully, so a failed Python measurement leaves no partial summary in the Actions step summary.

The following operations inside that boundary can raise ordinary exceptions which would be converted into the same refusal:

| Phase/source lines | Operations | Examples of masked failures |
| --- | --- | --- |
| startup, 75–95 | `sys.argv`, `os.getuid`, PATH parsing/encoding, `summary.stat()` | `IndexError`, `OSError`, `UnicodeEncodeError`, path/stat errors |
| package process helper, 97–137 | `Popen`, selector construction/register/select, `os.set_blocking`/`os.read`, `poll`, `kill`, `wait`, stream close | launch/permission errors other than specially handled `FileNotFoundError`, selector/descriptor errors, process API errors |
| directory/symlink traversal, 139–174 | chained `os.stat`, `Path.resolve(strict=True)`, `os.lstat`, `os.readlink` | missing/inaccessible components, resolution errors, symlink races |
| candidate validation/hash, 176–230 | `os.stat`, `os.access`, `os.open`, `os.fstat`, `os.read`, `os.close`, digest construction | file permission/race/I/O errors, descriptor failures, unexpected filesystem errors |
| package evidence, 231–247 | package subprocess output parsing, string encoding, report construction | process errors or malformed/oversized metadata failures; some are explicit `SystemExit` refusals |
| report materialization, 248–253 | bytes encoding, summary stat/open/write | encoding or filesystem/write errors |

Intentional validation refusals (`SystemExit`) bypass the generic handler and retain their explicit message. The hosted log does not show which row, if any, caused this incident.

## 3. Bounded local synthetic reproductions

I extracted the Python heredoc from the exact local workflow file at the immutable source SHA. Tests used temporary synthetic files named `ffmpeg` and `ffprobe` containing inert text, fake PATH entries, and a mocked `subprocess.Popen` boundary that accepted only `/usr/bin/dpkg-query` package-query calls. Those calls were simulated with pipe-backed test doubles; no real package query, FFmpeg or FFprobe process was invoked. Temporary harness artifacts were removed after each case. Runtime: Python `3.14.9`.

| Synthetic case | Observed result | Interpretation |
| --- | --- | --- |
| Both inert executable-shaped files; mocked owner/version replies | Exit 0; two fake digests emitted in temporary summary | Positive control: workflow body can finish with controlled local inputs. Digests were only for inert surrogate bytes. |
| Valid synthetic PATH entry followed by a missing directory | Generic `local metadata validation failed`; no package subprocess call | `check_directory_chain(entry)` can raise `FileNotFoundError` before the tool candidate loop completes; the broad handler masks it. This proves a reproducible failure mode, not that the hosted runner had this PATH. |
| Broken `ffmpeg` symlink | Same generic refusal | Strict symlink resolution can raise an ordinary filesystem exception masked by the handler. |
| Injected `PermissionError` from candidate `os.stat` | Same generic refusal | A file-stat error is reproducibly masked. |
| Mocked package-query `Popen` raises `PermissionError` | Same generic refusal; one package-process attempt | An unexpected metadata subprocess launch error is reproducibly masked. Hosted package-process state is unknown. |
| Owner metadata is newline-only (`b"\\n"`) and version query is empty | Exit 0; both surrogate hashes emitted | This malformed non-empty metadata is accepted: parsing yields an empty package name and the report can contain a blank package value. It did not reproduce the hosted generic exception. This is a robustness concern, not a demonstrated incident cause. |
| Package-query output exceeds 8,192 bytes | Explicit `REFUSED: ffmpeg package-owner query output exceeded 8192 bytes`; no generic masking | The existing output ceiling fails closed for this case. |

The one-shot local Python harness exited 0 after recording the expected result for each case. These are controller-observed local behavior reproductions against the exact published workflow body, not a hosted reproduction and not evidence of actual runner environment values. The ephemeral inline harness was not retained as a file, digest, or executable test artifact; the exact case results below are therefore **REPORTED_BY_CONTROLLER, not independently reproducible from this report**. This does not affect the independent source/log evidence or change the hosted root-cause status.

### Hypotheses not established as the hosted root cause

- A missing or inaccessible PATH entry could produce the generic error, but the run did not log `PATH` or a phase code.
- Symlink resolution, file metadata access, package-query launch/IO, summary handling, and other filesystem races can produce the same message, but the run does not distinguish them.
- Package ownership/version output may be malformed, but the synthetic newline-only case passed rather than reproducing the error.
- The timeout cleanup path is separately under-bounded (below); the hosted log contains no timeout-specific refusal and failed within tens of milliseconds, so this is not evidence that a timeout caused this incident.

No hypothesis is promoted to root cause. Preserve `ROOT_CAUSE_NOT_OBSERVED`.

## 4. Minimal proposed repair — not implemented

The smallest justified replacement is a **workflow-only diagnostic improvement**: keep all fail-closed validations and limits, but track an internal fixed phase identifier and map errors to a small fixed category. On an unexpected exception, emit only a bounded diagnostic such as:

`REFUSED: local metadata validation failed [phase=path_entry_stat; kind=filesystem_missing]`

Use an enumerated phase set, for example `startup_metadata`, `path_entry_stat`, `path_resolution`, `candidate_stat`, `tool_byte_open_read`, `package_owner_query`, `package_version_query`, `summary_materialization`, and `unexpected`. Map exception types into a closed set such as `filesystem_missing`, `filesystem_permission`, `filesystem_io`, `subprocess`, and `unexpected`. Do not print raw exception strings, paths, environment values, stack traces, tokens, or unbounded data. Keep explicit `SystemExit` safety refusals unchanged. This provides phase evidence on a later approved run without weakening admission or retry behavior.

A separate boundedness hardening is justified by static inspection: lines 112–113, 121–123, 128–130, and 133–135 call `process.wait()` with no timeout after `kill()`. The initial wait at lines 124–126 has a deadline, but cleanup can wait without a bound. Treat this as a distinct repair item, not the cause of run `42339608944`. A future replacement should use one shared cleanup deadline and bounded waits; if the child cannot be reaped within that bound, emit a fixed cleanup failure code and exit without an unbounded wait. Do not claim a particular signal/reaping behavior without a synthetic test.

No workflow patch has been created or applied in this task. The published workflow and its expected SHA remain unchanged.

## 5. Prospective behavioral RED/GREEN specification

A future authorized replacement should add local test-first checks around an extracted/pure Python helper or isolated workflow-body harness. The harness must use inert surrogate files and mocked process/selector boundaries; it must not execute `ffmpeg`, `ffprobe`, or system package tooling.

**RED on the current implementation:** demonstrate that the cases below collapse to the generic error or lack a testable phase code. Do not call missing-dependency/collection errors behavioral RED.

**GREEN on a proposed replacement:** require all of the following:

1. Missing/inaccessible PATH directory, bad path component, symlink loop/dangling link, candidate stat/open/read denial, and file replacement during measurement each fail closed with the correct fixed phase/category.
2. Package-query launch failure, nonzero exit, timeout, output overflow, malformed owner output, malformed version output, and summary write failure fail closed with bounded codes.
3. Valid inert surrogate executables produce their exact local SHA-256/byte length; results are emitted only after complete validation, and no real tool is executed.
4. Rerun, wrong-SHA, wrong-ref, wrong-workflow-ref and unauthorized repository/event test inputs stop before sentinel executable files are opened/read.
5. Error output contains no exception message, absolute path, PATH value, secret, stack trace, or uncontrolled-size string; diagnostic output has a tested maximum length.
6. Timeout/overflow cleanup mocks prove kill/reap calls remain deadline-bounded and no unbounded `wait()` occurs.
7. Existing package metadata size ceilings and all deliberate `SystemExit` refusal messages remain intact.

Expected result sequence: tests first fail against the old generic boundary (`RED`), then pass with the minimal diagnostic/cleanup change (`GREEN`). No chronological RED/GREEN is claimed in this investigation because no production change was authorized or made.

## 6. Controls and explicit Owner authorization required before another hosted attempt

The original one-run preflight allowance was consumed by run `42339608944`, even though it failed. A future hosted execution requires a new explicit Owner decision; no implication from the original approval should be used.

The next authorization packet should require:

1. **New immutable source candidate:** a fresh unique branch and exact source SHA/tree. Keep `54b8f945…` and its existing branch immutable. Do not push a changed workflow to the old branch: its `push` trigger would execute it.
2. **Narrow source scope:** only `.github/workflows/bfirst-tool-identity-preflight.yml` on the new candidate, unless the Owner explicitly approves another exact path. No changes to the production issuance workflow or A1 producer.
3. **Actor/ref restriction:** a narrowly scoped active ruleset for the new exact ref, with the one authorized actor explicitly identified. The earlier push transcript reported `Bypassed rule violations` for branch creation; before a future push, independently verify the actual ruleset/ref match and that only the intended actor is in the bypass set. Do not infer exclusivity from a successful push or stale ruleset ID.
4. **External expected-SHA binding:** set and independently read back `BFIRST_B2_TOOL_PREFLIGHT_EXPECTED_SHA` equal to the exact new reviewed 40-character commit. A source-authored value is not an authorization gate.
5. **Pre-push review and trigger audit:** independently review that exact SHA; verify new branch/workflow identity guards, one `push` event only, narrow path filters, no other workflow auto-trigger, minimum permissions, and attempt-1 refusal before any executable-byte read.
6. **Fresh finite run allowance:** Owner approval for exactly one first-attempt hosted run on that new source SHA, explicit prohibition of rerun/retry/second push, and acknowledgement of the accepted hosted-runner networking residual risk. Any failed attempt consumes the allowance.
7. **No tool-hash promotion from measurement alone:** the new digests must be independently reviewed and separately approved before configuring production issuer allowlist variables or pushing/running A1.

Until all those predicates pass, do not push a replacement workflow and do not run the issuer.

## 7. Unchanged boundaries and terminal state

- Canonical `main` and LAB `main` were read-only. Canonical source stayed at the published preflight SHA; no new Canonical commit/ref or Actions run was created by this investigation.
- LAB design work is confined to this new documentation-only local branch. It has not been pushed, so no hosted workflow was triggered by this report.
- No A1 source modification, production issuance run, media generation, artifact upload/download, model/provider operation, Stage A3, Stage B/C, or Gate promotion occurred.
- The exact failed hosted run remains a failure; no digest pair was obtained; no root cause is established.

`BFIRST_B2_A2_PREFLIGHT_FAILURE_SOURCE_AND_RUN_RECONCILED` is **not** asserted. This report's investigative disposition is `ROOT_CAUSE_NOT_OBSERVED`; required operational statuses remain:

`A2_BLOCKED_TOOL_IDENTITY`

`A3_NOT_RUN`

`STRICT_ANALYZE_LOCAL_VIDEO_NOT_OBSERVED`

`CORE01_LEGACY_INTERVAL_BLOCKED_BY_CONTRACT`
