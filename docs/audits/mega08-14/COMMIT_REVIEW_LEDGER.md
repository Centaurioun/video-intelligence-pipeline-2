# MEGA-08–14 commit review ledger

| Reviewed LAB SHA | Parent | Changed paths / scope | CI evidence | Disposition |
|---|---|---|---|---|
| `22f1ffa7064f697d4049e39587945b1decabec4e` | See `git show` | Stable starting baseline; MEGA-03…07 and previous product synthetic suites | Actions `41756569162`: Python 3.11 + 3.14 successful; 307 per version per `docs/ai-studio-tasks/MEGA_03_07_PROGRESS.md:19-23` | `VERIFIED_GITHUB` for baseline only; not MEGA-08…14 |
| `b55b14884dc5d62f8784c60af2a8e14fea107b36` | `41f043e2067ed419aaa56dd53c9da61f66162eca` | Workflow + audit/task documents only; no MEGA-08…14 implementation/test paths | Actions not queried for this exact docs/workflow head; baseline run is not transferable | `NOT_YET_SUBMITTED` for implementation; `SOURCE_INSPECTED` current CI gap |

## Fixed checks for every future candidate

1. Fetch and record immutable SHA, parent(s), exact diff paths, `git diff --check`, additions/deletions, and relevant tree state (especially `.github/**` and all six `src/gate0/media/**` files).
2. Read all candidate code and tests. Verify actual source imports, dataclass fields, runner/serializer constructors and exact canonical model space identities. Check no new retrieval/recovery/temporal/authority subsystem duplicates.
3. Search source/tests for source media open/stat/hash/probe/decode, model/network/provider, FFmpeg/subprocess, fake human/Owner signatures, `MEASURED`/QC status upgrades, path traversal, duplicate-key parser weakening, unbound occurrence identity, and false CI skips.
4. Inspect Actions by exact SHA. Both Python 3.11 and 3.14 must actually select submitted new tests and previous baseline tests. Record test counts from logs; presence checks and green old-suite-only runs are insufficient.
5. Keep dispositions per SHA. Any new `origin/main` SHA makes earlier candidate review historical until diff/tests/CI relationships are reconciled.

## Current open issues

- `A-01` (`P1`): workflow currently has no MEGA-08…14 selectors/completeness checks.
- No implementation commit has been submitted; all new wave behavior remains `NOT_OBSERVED`.
