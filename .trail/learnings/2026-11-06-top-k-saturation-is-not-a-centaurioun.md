---
title: Top-K saturation is not a total match count
author: Centaurioun
date: 2026-11-06
branch: codex/mega-core-02-verification-20261106
id: l-c7d9477f
scope: repo
status: active
src: agent
touches:
  - src/vip_fvs/core_analysis.py
  - src/vip_fvs/core_report.py
---

## Decided
Sort retrieved candidates using their unrounded backend score and preserve enough score precision in Report V1 so deterministic order remains auditable. When the retrieval request fills top_k, the returned hits are only a lower bound; report total_eligible_matches as NOT_OBSERVED unless an API actually observed the total.

## Tried and ruled out
Rounding raw scores to 12 decimals makes near-equal but distinct scores tie and lets PTS override the backend rank. Using indexed sample count as the eligible-match total confuses storage size with query relevance.

## Watch out
If a future search API supplies a separately measured total, validate its provenance and distinguish it from source_sample_count. Keep zero-hit semantics at exactly zero.

In the code: src/vip_fvs/core_analysis.py candidate sorting and Top-K report assembly; src/vip_fvs/core_report.py score ordering and NOT_OBSERVED count validation.
