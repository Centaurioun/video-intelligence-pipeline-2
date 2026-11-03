# ADR-0001: Reference-Pack Copy Boundary

## Status

Accepted for Phase 0.

## Context

The repository needs compact, inspectable architecture evidence from external
projects, but public GitHub visibility does not establish unrestricted copying.
Several selected references have no GitHub-recognized license metadata; Video
Duplicate Finder is AGPLv3. The Phase-0 goal is research provenance, not
vendoring or code reuse.

## Decision

- Keep full pinned sparse checkouts in Git-ignored `external/`.
- Commit raw, selected source snapshots only when the inspected source has a
  declared permissive license and no source-specific credential restriction.
- For unknown-license or strong-copyleft sources, commit `NOTES.md` plus the
  per-file, SHA-pinned source map and rationale in
  `reference-pack/selection-manifest.json`; do not commit raw code.
- Treat this as a conservative engineering boundary, not legal advice. Any
  future distribution or code reuse requires a source-specific license review.

## Consequences

The Astra reviewer gets compact architectural findings, exact paths, revisions,
and safe access to full source when necessary. It must open the ignored sparse
checkout for source-level detail in these cases. VDF remains an external-tool
candidate rather than source to merge into this repository.
