# MEGA-08–14 commit review ledger

| Reviewed LAB SHA | Parent | Changed paths / scope | CI evidence | Disposition |
|---|---|---|---|---|
| `22f1ffa7064f697d4049e39587945b1decabec4e` | See `git show` | Stable starting baseline; MEGA-03…07 and previous product synthetic suites | Actions `41756569162`: Python 3.11 + 3.14 successful; 307 per version per `docs/ai-studio-tasks/MEGA_03_07_PROGRESS.md:19-23` | `VERIFIED_GITHUB` for baseline only; not MEGA-08…14 |
| `b55b14884dc5d62f8784c60af2a8e14fea107b36` | `41f043e2067ed419aaa56dd53c9da61f66162eca` | Workflow + audit/task documents only; no MEGA-08…14 implementation/test paths. Workflow adds completeness checks and conditional wave selectors. | Actions `41760125750`: Python 3.11 + 3.14 successful; all seven new test steps skipped because files are absent; completeness and aggregate steps succeeded. | `NOT_YET_SUBMITTED`; CI coverage is present, but new-wave behavior remains unexecuted. |

## Fixed checks for every future candidate

1. Fetch and record immutable SHA, parent(s), exact diff paths, `git diff --check`, additions/deletions, and relevant tree state (especially `.github/**` and all six `src/gate0/media/**` files).
2. Read all candidate code and tests. Verify actual source imports, dataclass fields, runner/serializer constructors and exact canonical model space identities. Check no new retrieval/recovery/temporal/authority subsystem duplicates.
3. Search source/tests for source media open/stat/hash/probe/decode, model/network/provider, FFmpeg/subprocess, fake human/Owner signatures, `MEASURED`/QC status upgrades, path traversal, duplicate-key parser weakening, unbound occurrence identity, and false CI skips.
4. Inspect Actions by exact SHA. Both Python 3.11 and 3.14 must actually select submitted new tests and previous baseline tests. Record test counts from logs; presence checks and green old-suite-only runs are insufficient.
5. Keep dispositions per SHA. Any new `origin/main` SHA makes earlier candidate review historical until diff/tests/CI relationships are reconciled.

## Current open issues

- Prior `A-01` (`P1`) is withdrawn as `AUDIT_REVIEWER_ERROR`; see [PHASE_A_CORRECTION_2026-11-04.md](PHASE_A_CORRECTION_2026-11-04.md). The workflow has selectors, completeness checks, and aggregate enforcement at `b55b148…`.
- No implementation commit has been submitted; all new wave behavior remains `NOT_OBSERVED`. Actions run `41760125750` skipped all seven MEGA test steps on both Python versions; that run does not verify new-wave behavior.
