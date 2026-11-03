# Python synthetic smoke CI and runtime scope (2026-10-24)

**Scope:** development-only, model-free / protected-media-free regression checks. This document does **not** authorize real archive execution, model downloads, provider calls, production editing, or Gate promotion.

GitHub Actions workflows:

- [`python-synthetic-smoke.yml`](../../.github/workflows/python-synthetic-smoke.yml) — the selected smoke subset summarized below.
- [`gate0-d1-integrated-regressions.yml`](../../.github/workflows/gate0-d1-integrated-regressions.yml) — targeted D-1 A/B/C and frozen Gate-0 synthetic contract regressions.
- [`gate0-broad-synthetic-regressions.yml`](../../.github/workflows/gate0-broad-synthetic-regressions.yml) — the complete `tests/gate0` selection (the broad Gate-0 regression surface). It installs only the already locked Gate-0 test prerequisites and pre-flights the frozen historical Git objects with `git cat-file -e`, so a checkout without preserved history fails loudly instead of surfacing as an opaque test error.

- **CI interpreter matrix:** CPython **3.11** and **3.14** (Ubuntu GitHub-hosted runner).
- **Dependency inputs:** all three workflows pin `requirements/gate0.lock` (`pytest==8.3.3`) and additionally install `jsonschema==4.26.0` and `numpy>=2.3,<3` / `pillow>=11.1,<13` (VIP-FVS and persistent-index import graph). None downloads models or archive media, and no workflow adds a dependency beyond this locked set.
- **Smoke coverage:** canonical JSON (Gate 0), synthetic three-arm compatibility (Gate 1), fault semantics (Gate 2), synthetic ISO-BMFF timing (Gate 3), source-snapshot single-read/PTS and preflight-overlay validation.
- **Git checkout:** full history to avoid false failures when deterministic provenance references Git objects.
- **Boundaries:** these are selected **smoke tests**, not the complete repository test suite, not a macOS runtime attestation, and not evidence of Python compatibility for all optional/pilot interfaces.
- **Current runtime packaging:** repository root has no `pyproject.toml` or `requires-python` declaration; the CI matrix is an executable test contract, not a claim that all production functions support either interpreter.

Do not declare the matrix green until both GitHub Actions jobs have completed successfully on the exact candidate commit. A blocked or unavailable Actions runner is `NOT_OBSERVED`, not PASS. The Owner decides whether to make these checks required for merging later; no GitHub ruleset changes are part of this work.
