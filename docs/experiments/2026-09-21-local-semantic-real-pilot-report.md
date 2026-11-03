# Exact Developer-Local Real Semantic Pilot v1

## Terminal result

`PASS`: the authorized local index/query/refinement chain completed with source and provenance invariants intact, and the frozen anchor-retrieval proceed signal was met (`7 STRONG`, `0 USEFUL`, `0 WEAK`, `0 MISS`).

This is an anchor-retrieval reproduction pilot. It is not exact-boundary accuracy, frame-accurate edit authority, a Gate-1 benchmark, or archive generalization.

## Fresh measured facts

The only processed source was `/Users/yusuf/Movies/kolaj-1-uzun.mp4`. Its SHA-256 was `3834a376ecdb0358377fbc62f914f651a21e8486f9a23c179b22a1b889fae139` before and after processing; observed size was 841,521,389 bytes and mtime remained `1789495404`. No source bytes were changed.

The frozen local model was `google/siglip-base-patch16-224`, revision `7fd15f0689c79d79e38b1c2e2e2370a7bf2761ed`, weights SHA-256 `2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8`, with processor digest `4806b21bbf8b71362f21a021f2be993f6339e67c212f776f73b03b8f12ea7980`. Runtime device was freshly verified MPS. Offline environment controls were set; OS-level egress denial was not observed.

Exactly one real index build used the current persistent-local-index CLI, the exact source path, and the fixed 4.5-second sampling policy. It produced 59 rows in generation `648dd7391ec2a92e51aacdd20d11c4bd5c1a5c3ce88755066c819e0faa852508`, semantic space `3840a0f423fa3ef6c273e61160131dd8c698c83873e9db99ee1917750e5cfe5a`, in 52.55 seconds wall time.

The exact seven frozen queries were run twice in equivalent seven-query batches. The JSON outputs were byte-identical: rankings, row IDs, source SHA, integer PTS, timebase, thumbnail paths, and scores all matched.

## Anchor rubric results

| Query | Label | Top-1 source time | Anchor delta | Best anchor-near rank |
|---|---|---:|---:|---:|
| Q1 mall selfie | STRONG | 4.500 s | 1.500 s | 1 |
| Q2 ballet students | STRONG | 58.517 s | 1.517 s | 1 |
| Q3 mirrors rehearsal | STRONG | 139.550 s | 1.050 s | 2 |
| Q4 male instructor | STRONG | 162.050 s | 0.550 s | 2 |
| Q5 castle selfie | STRONG | 175.550 s | 1.550 s | 1 |
| Q6 Gothic cathedral | STRONG | 202.550 s | 1.450 s | 1 |
| Q7 ballet poster | STRONG | 220.550 s | 0.550 s | 1 |

The raw normalized query and Top-5 evidence is in [normalized-results.json](../agent-runs/run-20260921-local-semantic-real-pilot/normalized-results.json). Historical comparisons are preserved in the A7 lane memo and the per-query Q1/Q2/Q5 memos; no query was rewritten after results were seen. Direct visual inspection was not used, so no `VISUALLY_OBSERVED` claim is made.

## Source-native refinement

Each Top-1 candidate carried integer source PTS in timebase `1/600`. The measured source-native PTS table was used, and each endpoint was selected as the first actual measured PTS strictly after the hit PTS. All seven refinements were binding-eligible, with source digest equality before and after. Semantic timestamps remain candidate evidence and were not upgraded to edit boundaries.

The real source initially exposed a parser defect: the MP4 begins with a 64-bit large-size `mdat`, which the parser rejected, and its B-frame presentation PTS are reordered relative to decode DTS. A bounded fix added large-size/zero-size BMFF handling and exposed sorted presentation PTS while retaining DTS evidence. Targeted post-fix tests passed (`26 passed`).

## Claims and non-claims

The local technical chain is reproducible for this one authorized file and model contract. The result does not establish general semantic retrieval quality, exact scene boundaries, frame-accurate cuts, provider comparisons, Gate promotion, or archive-scale behavior. No provider/cloud activity, model download, production export, or unauthorized-media access was observed.

Terminal disposition: `PASS`.
