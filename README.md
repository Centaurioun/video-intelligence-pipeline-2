# Video Intelligence Pipeline

> **Architecture audit complete — GATE-0 IMPLEMENTATION SPECIFICATION and implementation planning are ready for execution review; production implementation is not approved.**

This project is preparing an evidence-rich, provider-independent foundation for
finding usable moments in a large video archive. The first approved architecture
question is deliberately narrower than the full product vision: determine whether
one local sampled-visual semantic retrieval method can reliably surface useful
visual moments on a small, authorized local corpus.

The architecture remains local-first and evidence-preserving. Deterministic
FFmpeg/ffprobe inspection, source identity/provenance, local retrieval, later VDF
relation evidence, and optional DeepSeek/Gemini/TwelveLabs benchmark roles are
separated by explicit gates rather than treated as one immediate pipeline.

Semantic retrieval and frame-accurate editing remain separate. A model may
identify a useful semantic candidate window; final cuts require deterministic
source-native frame/PTS refinement and a later human/editorial decision.

## Current status

Phase 0 assembled the reproducible research corpus. Phase 0.5 produced twelve
focused evidence memos and six cross-critiques. The architecture audit resolved
the major identity, evidence, status, timing, egress, provider, dedupe, and gate-
boundary contradictions. Gate-0 Implementation Specification v1.1 was then
normalized through six cumulative review cycles plus fresh red-team review and
has received explicit user approval for implementation planning only.

The current architecture/specification handoff is:

- `docs/audits/ASTRA_ARCHITECTURE_DECISION_PACKAGE.md`
- `docs/architecture/ASTRA_DECISION_REGISTER.md`
- `docs/architecture/CANONICAL_CONTRACTS.md`
- `docs/architecture/GATE_0_EXPERIMENT_CONTRACT.md`
- `docs/audits/POST_ASTRA_SIX_CYCLE_REFINEMENT.md`
- `docs/implementation-spec-v1.1.md`
- `docs/audits/GATE0_SPEC_NORMALIZATION_REVIEW.md`
- `docs/architecture/MAIN_AGENT_SYNC_PROTOCOL.md`
- `docs/architecture/SUBAGENT_LANE_PROTOCOL.md`

The repository still does **not** contain an approved production pipeline,
provider stack, database, scheduler, search UI, editor, or archive-scale runtime.

Read [docs/INDEX.md](docs/INDEX.md) before exploring the workspace. The committed
[reference-pack/](reference-pack/) is the high-signal evidence surface; ignored
[external/](external/) holds full reference checkouts only for targeted follow-up
questions.

## Repository boundaries

- `prototypes/google-video-analyzer/` remains a preserved Google/Gemini prototype
  snapshot, not the future provider architecture.
- `reference-pack/` contains selected source evidence and provenance notes, not
  vendored production dependencies.
- `src/` remains intentionally empty of production implementation until a
  separately reviewed implementation plan is completed and later execution is
  explicitly authorized.
- Gate 0 is local-only and read-only with respect to source media. Cloud
  providers, VDF execution, vector services, Drive materialization, editing,
  rendering, and UI work are later-gate questions.
- Codex/subagent process orchestration is governed by
  `docs/architecture/SUBAGENT_LANE_PROTOCOL.md`; it is repository workflow, not
  product/runtime orchestration.
- Every repo-working main-agent turn begins and ends with the safe canonical
  local-`main`/`origin/main` synchronization defined in
  `docs/architecture/MAIN_AGENT_SYNC_PROTOCOL.md`. Subagent lane branches remain
  local by default and become remotely durable through verified main integration.

## Next gate

The current planning artifact is **GATE-0 IMPLEMENTATION PLANNING** using the approved
`docs/implementation-spec-v1.1.md` and the Superpowers `writing-plans` workflow.
The planning task may produce an executable task breakdown, dependencies, test-
first sequence, file/module ownership, verification checkpoints, and bounded
handoff for a later implementation review.

This approval does **not** authorize production code, real archive processing,
model downloads, provider requests, cloud egress, or later-gate infrastructure.
A separate explicit user authorization is required before any implementation
execution begins.
