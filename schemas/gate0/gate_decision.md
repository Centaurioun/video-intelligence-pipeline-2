# Gate decision schema

The report payload is UTF-8 LF Markdown with trailing whitespace removed. Its
logical record is closed to exactly these fields:

`run_id`, `benchmark_status`, `gate_decision`, `stop_reason`, `metrics_digest`,
`threshold_digest`, `authority`, `reviewers`, and `decided_at`.

`benchmark_status` ∈ `PLANNED`, `VALID`, `INVALID_PROTOCOL`, `PASS`, `FAIL`,
`NOT_RUN`; `gate_decision` ∈ `PASS`, `FAIL`, `INVALID_PROTOCOL`, `NOT_RUN`.
Digest fields are lowercase SHA-256 (64 hexadecimal characters), IDs are
lowercase opaque IDs (`^[a-z0-9][a-z0-9_-]{0,127}$`), and `decided_at` is an
RFC-3339 timestamp with an explicit offset. Unknown fields and non-finite
numbers are rejected by the artifact validator. The digest covers the exact
normalized UTF-8 LF bytes, excluding no logical record fields.
