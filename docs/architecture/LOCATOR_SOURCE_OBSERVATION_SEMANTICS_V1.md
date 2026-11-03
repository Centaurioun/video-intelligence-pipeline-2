# Locator source observation semantics v1

**Locator observations.** A stored locator/path is an occurrence observation at
`T_obs`, not content identity. A `source_locations`-style row records the
`source_sha256` of bytes read from that locator into the verified private
snapshot during the ingestion observation window, together with filesystem
metadata captured for that window. Pre/post stat or fingerprint guards may
detect observable change, but they do not prove a simultaneous or atomic
binding between the external path, those bytes, and a database commit. The row
is a last-observed locator projection, not a lease, lock, watcher, or proof of
the bytes currently at that path. `source_sha256` and verified snapshot bytes
remain content authority. A later use of external media must verify the exact
expected `source_sha256`. Any operation claiming `MEASURED` byte authority
must consume those same verified bytes through a private snapshot or stable
file handle whose consumed bytes remain bound to the verified digest; a stable
descriptor alone does not prevent in-place mutation. A separate path hash
followed by a tool reopening the mutable path does not prove which bytes the
tool consumed. Missing, unreadable, or
mismatching bytes fail closed. Locator observation metadata does not itself
establish a `MEASURED` media-content claim.
