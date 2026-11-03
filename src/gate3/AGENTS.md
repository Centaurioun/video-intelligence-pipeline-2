# Gate-3 Production-Code Instructions

Scope: `src/gate3/**`.

Read repository root `AGENTS.md`, the current Owner-approved task scope/authority, and applicable governing contracts before changing this subtree. This means the user's/Owner's task direction; ADR-0003 requires no branch/path administrative grant or Owner Witness for ordinary development. The previously referenced `docs/gates/gate3/SELECTED_CANDIDATE_EXECUTION_CONTRACT.md` is absent from canonical `main`; do not infer or recreate its contents. If a task depends on its missing directives, stop until the responsible contract owner supplies the contract or approves an amendment to this pre-read requirement.

- T1–T11 are frozen. Do not redesign them.
- Exact temporal truth comes from source-native PTS/timebase evidence. Never derive exact VFR frames via seconds × nominal FPS.
- Preserve source identity/revision/stream, run/attempt identity, provenance and evidence state.
- Do not silently upgrade evidence.
- Source media is immutable.
- Synthetic/local scope only; no protected media, provider/cloud calls, production export, or model downloads.
- Every behavior change requires observed RED → minimal GREEN → refactor/regression.
- Unexpected failures require systematic root-cause debugging before fixes.
- Obey the repair/task's exact writable ownership. Do not widen your own scope.
- The referenced Candidate B DIRECT/ADAPT/TEST_ONLY/REJECT map is not present in the current repository. Do not infer or apply a Candidate B disposition; if a task requires it, stop for a contract-owner decision.
- A child completion claim is not acceptance; persist a compact durable handoff and let the root independently verify/integrate.
